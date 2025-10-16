"""
Campaign Manager - Orchestrates WhatsApp Message Campaigns

Coordinates the complete message sending workflow:
- Load businesses from Excel
- Initialize WhatsApp controller
- Apply rate limiting and delays
- Track progress and results
- Support resume from interruption
- Generate campaign reports

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.models.business import Business
from src.core.excel_handler import ExcelDataHandler
from src.core.message_composer import MessageComposer
from src.core.whatsapp_controller import WhatsAppController
from src.core.delay_manager import DelayManager, create_default_delay_manager
from src.utils.csv_reporter import CSVReporter
from src.utils.analytics_tracker import AnalyticsTracker

logger = logging.getLogger(__name__)


@dataclass
class MessageResult:
    """Result of sending a single message."""
    
    business_name: str
    phone: str
    message_type: str
    status: str  # 'success', 'failed', 'skipped'
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message_preview: Optional[str] = None


@dataclass
class CampaignProgress:
    """Track campaign progress."""
    
    total_businesses: int = 0
    processed: int = 0
    sent: int = 0
    failed: int = 0
    skipped: int = 0
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    last_processed_index: int = -1
    results: List[MessageResult] = field(default_factory=list)


class CampaignManager:
    """
    Manages complete WhatsApp message campaigns.
    
    Features:
    - Load businesses from Excel
    - Send messages with rate limiting
    - Track progress and results
    - Support resume from interruption
    - Generate reports
    """
    
    def __init__(self,
                 excel_file: str,
                 chrome_profile: str = "chrome_profile_whatsapp",
                 delay_manager: Optional[DelayManager] = None,
                 progress_file: Optional[str] = None,
                 dry_run: bool = False):
        """
        Initialize campaign manager.
        
        Args:
            excel_file: Path to Excel file with business data
            chrome_profile: Chrome profile path for WhatsApp session
            delay_manager: Delay manager instance (creates default if None)
            progress_file: Path to progress file for resume capability
            dry_run: If True, don't actually send messages
        """
        self.excel_file = Path(excel_file)
        self.chrome_profile = chrome_profile
        self.dry_run = dry_run
        
        # Initialize components
        self.delay_manager = delay_manager or create_default_delay_manager()
        self.excel_handler = ExcelDataHandler(str(self.excel_file))
        self.message_composer = MessageComposer()
        self.whatsapp_controller: Optional[WhatsAppController] = None
        
        # New Phase 6 components
        self.csv_reporter = CSVReporter()
        self.analytics_tracker = AnalyticsTracker()
        
        # Progress tracking
        self.progress = CampaignProgress()
        self.progress_file = Path(progress_file) if progress_file else None
        
        # Load existing progress if available
        if self.progress_file and self.progress_file.exists():
            self._load_progress()
        
        logger.info(
            f"CampaignManager initialized: "
            f"Excel={self.excel_file}, Profile={self.chrome_profile}, "
            f"DryRun={self.dry_run}"
        )
    
    def run_campaign(self, headless: bool = False) -> bool:
        """
        Run complete message campaign.
        
        Args:
            headless: Run browser in headless mode
            
        Returns:
            bool: True if campaign completed successfully
        """
        try:
            logger.info("=" * 60)
            logger.info("🚀 STARTING WHATSAPP CAMPAIGN")
            logger.info("=" * 60)
            
            # Step 1: Load businesses
            businesses = self._load_businesses()
            if not businesses:
                logger.error("No valid businesses to process")
                return False
            
            # Start analytics tracking
            self.analytics_tracker.start_campaign(len(businesses))
            
            # Step 2: Initialize WhatsApp (unless dry run)
            if not self.dry_run:
                if not self._initialize_whatsapp(headless):
                    logger.error("Failed to initialize WhatsApp")
                    return False
            
            # Step 3: Send messages
            self._send_messages(businesses)
            
            # End analytics tracking
            self.analytics_tracker.end_campaign()
            
            # Step 4: Generate report
            self._generate_report()
            
            logger.info("=" * 60)
            logger.info("✅ CAMPAIGN COMPLETED")
            logger.info("=" * 60)
            
            return True
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Campaign interrupted by user")
            self._save_progress()
            return False
            
        except Exception as e:
            logger.error(f"Campaign failed: {str(e)}", exc_info=True)
            return False
            
        finally:
            # Cleanup
            if self.whatsapp_controller:
                self.whatsapp_controller.close()
    
    def _load_businesses(self) -> List[Business]:
        """Load and validate businesses from Excel."""
        logger.info(f"📂 Loading businesses from {self.excel_file}")
        
        try:
            businesses = self.excel_handler.get_businesses()
            
            # Filter out already processed (if resuming)
            if self.progress.last_processed_index >= 0:
                businesses = businesses[self.progress.last_processed_index + 1:]
                logger.info(
                    f"📥 Resuming from index {self.progress.last_processed_index + 1}"
                )
            
            self.progress.total_businesses = len(businesses)
            
            logger.info(f"✅ Loaded {len(businesses)} businesses")
            
            # Show summary
            validation_summary = self.excel_handler.get_validation_summary()
            logger.info(f"📊 Validation Summary:")
            logger.info(f"   Total Rows: {validation_summary['total_rows']}")
            logger.info(f"   Valid: {validation_summary['valid_rows']}")
            logger.info(f"   Invalid: {validation_summary['invalid_rows']}")
            logger.info(f"   Success Rate: {validation_summary['success_rate']:.1f}%")
            
            return businesses
            
        except Exception as e:
            logger.error(f"Failed to load businesses: {str(e)}")
            raise
    
    def _initialize_whatsapp(self, headless: bool) -> bool:
        """Initialize WhatsApp controller."""
        logger.info("🌐 Initializing WhatsApp Web...")
        
        try:
            self.whatsapp_controller = WhatsAppController(
                profile_path=self.chrome_profile,
                headless=headless
            )
            
            success = self.whatsapp_controller.initialize_driver()
            
            if success:
                logger.info("✅ WhatsApp Web initialized successfully")
            else:
                logger.error("❌ Failed to initialize WhatsApp Web")
            
            return success
            
        except Exception as e:
            logger.error(f"WhatsApp initialization failed: {str(e)}")
            return False
    
    def _send_messages(self, businesses: List[Business]):
        """Send messages to all businesses with rate limiting."""
        logger.info(f"\n📨 Sending messages to {len(businesses)} businesses...")
        
        self.progress.start_time = datetime.now()
        
        for i, business in enumerate(businesses):
            try:
                # Check rate limits
                can_send, reason = self.delay_manager.can_send_message()
                if not can_send:
                    logger.warning(f"🛑 Rate limit reached: {reason}")
                    self._record_result(business, 'skipped', reason)
                    break
                
                # Send message
                logger.info(f"\n[{i+1}/{len(businesses)}] Processing: {business.business_name}")
                result = self._send_single_message(business)
                
                # Record result
                self._record_result(
                    business,
                    result['status'],
                    result.get('error'),
                    result.get('message')
                )
                
                # Update progress
                self.progress.processed += 1
                self.progress.last_processed_index = i
                
                # Save progress periodically
                if self.progress.processed % 5 == 0:
                    self._save_progress()
                
                # Wait before next message (if not last message)
                if i < len(businesses) - 1 and result['status'] == 'success':
                    self.delay_manager.wait_between_messages()
                
            except KeyboardInterrupt:
                logger.warning("\n⚠️ Sending interrupted by user")
                raise
                
            except Exception as e:
                logger.error(f"Error processing {business.business_name}: {str(e)}")
                self._record_result(business, 'failed', str(e))
        
        self.progress.end_time = datetime.now()
        self._save_progress()
    
    def _send_single_message(self, business: Business) -> Dict[str, Any]:
        """
        Send message to a single business.
        
        Args:
            business: Business to send message to
            
        Returns:
            dict: Result with status, error, message
        """
        try:
            # Compose message
            message = self.message_composer.compose_message(business)
            message_type = self.message_composer.detect_message_type(business)
            
            logger.info(f"📝 Message type: {message_type.upper()}")
            logger.info(f"📝 Message preview: {message[:80]}...")
            
            # Dry run mode
            if self.dry_run:
                logger.info("✅ DRY RUN - Message not actually sent")
                return {
                    'status': 'success',
                    'message': message,
                    'dry_run': True
                }
            
            # Actually send via WhatsApp
            success = self.whatsapp_controller.send_message(business.phone, message)
            
            if success:
                logger.info(f"✅ Message sent successfully to {business.phone}")
                self.delay_manager.record_message_sent()
                return {
                    'status': 'success',
                    'message': message
                }
            else:
                logger.error(f"❌ Failed to send message to {business.phone}")
                return {
                    'status': 'failed',
                    'error': 'Send operation failed',
                    'message': message
                }
                
        except Exception as e:
            logger.error(f"Error sending to {business.business_name}: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _record_result(self,
                       business: Business,
                       status: str,
                       error: Optional[str] = None,
                       message: Optional[str] = None,
                       duration: float = 0.0,
                       retry_count: int = 0):
        """Record message sending result."""
        message_type = self.message_composer.detect_message_type(business)
        
        result = MessageResult(
            business_name=business.business_name,
            phone=business.phone,
            message_type=message_type,
            status=status,
            error=error,
            message_preview=message[:80] if message else None
        )
        
        self.progress.results.append(result)
        
        # Update counters
        if status == 'success':
            self.progress.sent += 1
            # Track in analytics
            self.analytics_tracker.track_message_sent(
                business.business_name,
                business.phone,
                message_type,
                business.has_website(),
                duration,
                retry_count
            )
        elif status == 'failed':
            self.progress.failed += 1
            # Track in analytics
            self.analytics_tracker.track_message_failed(
                business.business_name,
                business.phone,
                message_type,
                business.has_website(),
                error or 'Unknown error',
                duration,
                retry_count
            )
        elif status == 'skipped':
            self.progress.skipped += 1
            # Track in analytics
            self.analytics_tracker.track_message_skipped(
                business.business_name,
                business.phone,
                error or 'Unknown reason'
            )
    
    def _generate_report(self):
        """Generate campaign report."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 CAMPAIGN REPORT")
        logger.info("=" * 60)
        
        # Summary statistics
        logger.info(f"Total Businesses: {self.progress.total_businesses}")
        logger.info(f"Processed: {self.progress.processed}")
        logger.info(f"✅ Sent: {self.progress.sent}")
        logger.info(f"❌ Failed: {self.progress.failed}")
        logger.info(f"⏭️  Skipped: {self.progress.skipped}")
        
        # Success rate
        if self.progress.processed > 0:
            success_rate = (self.progress.sent / self.progress.processed) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Duration
        if self.progress.start_time and self.progress.end_time:
            duration = self.progress.end_time - self.progress.start_time
            logger.info(f"Duration: {duration}")
        
        # Delay manager stats
        logger.info("\n📊 Rate Limiting Statistics:")
        self.delay_manager.print_statistics()
        
        # Analytics summary
        logger.info("\n📊 Analytics Summary:")
        self.analytics_tracker.print_summary()
        
        # Save detailed report (JSON)
        self._save_detailed_report()
        
        # Export CSV reports
        self._export_csv_reports()
        
        # Export analytics
        self._export_analytics()
        
        logger.info("=" * 60)
    
    def _save_detailed_report(self):
        """Save detailed campaign report to JSON file."""
        try:
            report_file = Path("data") / "campaign_reports" / f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            report_data = {
                'campaign_info': {
                    'excel_file': str(self.excel_file),
                    'dry_run': self.dry_run,
                    'start_time': self.progress.start_time.isoformat() if self.progress.start_time else None,
                    'end_time': self.progress.end_time.isoformat() if self.progress.end_time else None,
                },
                'summary': {
                    'total_businesses': self.progress.total_businesses,
                    'processed': self.progress.processed,
                    'sent': self.progress.sent,
                    'failed': self.progress.failed,
                    'skipped': self.progress.skipped,
                },
                'rate_limiting': self.delay_manager.get_statistics(),
                'results': [
                    {
                        'business_name': r.business_name,
                        'phone': r.phone,
                        'message_type': r.message_type,
                        'status': r.status,
                        'error': r.error,
                        'timestamp': r.timestamp,
                    }
                    for r in self.progress.results
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Detailed report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
    
    def _save_progress(self):
        """Save campaign progress for resume capability."""
        if not self.progress_file:
            return
        
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            progress_data = {
                'last_processed_index': self.progress.last_processed_index,
                'processed': self.progress.processed,
                'sent': self.progress.sent,
                'failed': self.progress.failed,
                'skipped': self.progress.skipped,
                'start_time': self.progress.start_time.isoformat() if self.progress.start_time else None,
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
            
            logger.debug(f"Progress saved to {self.progress_file}")
            
        except Exception as e:
            logger.error(f"Failed to save progress: {str(e)}")
    
    def _load_progress(self):
        """Load campaign progress for resume."""
        if not self.progress_file or not self.progress_file.exists():
            return
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            self.progress.last_processed_index = progress_data.get('last_processed_index', -1)
            self.progress.processed = progress_data.get('processed', 0)
            self.progress.sent = progress_data.get('sent', 0)
            self.progress.failed = progress_data.get('failed', 0)
            self.progress.skipped = progress_data.get('skipped', 0)
            
            if progress_data.get('start_time'):
                self.progress.start_time = datetime.fromisoformat(progress_data['start_time'])
            
            logger.info(f"✅ Progress loaded: Resuming from index {self.progress.last_processed_index}")
            
        except Exception as e:
            logger.error(f"Failed to load progress: {str(e)}")
    
    def _export_csv_reports(self):
        """Export CSV reports for campaign results."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Prepare results data
            results_data = []
            for result in self.progress.results:
                results_data.append({
                    'timestamp': result.timestamp,
                    'business_name': result.business_name,
                    'phone': result.phone,
                    'message_type': result.message_type,
                    'status': result.status,
                    'error': result.error or '',
                    'message_preview': result.message_preview or '',
                })
            
            # Export campaign results
            results_file = self.csv_reporter.export_campaign_results(
                results_data,
                filename=f"campaign_results_{timestamp}.csv"
            )
            logger.info(f"📄 Results exported: {results_file}")
            
            # Prepare campaign data for summary
            campaign_data = {
                'campaign_info': {
                    'excel_file': str(self.excel_file),
                    'dry_run': self.dry_run,
                    'start_time': self.progress.start_time.isoformat() if self.progress.start_time else None,
                    'end_time': self.progress.end_time.isoformat() if self.progress.end_time else None,
                },
                'summary': {
                    'total_businesses': self.progress.total_businesses,
                    'processed': self.progress.processed,
                    'sent': self.progress.sent,
                    'failed': self.progress.failed,
                    'skipped': self.progress.skipped,
                },
                'rate_limiting': self.delay_manager.get_statistics(),
            }
            
            # Export campaign summary
            summary_file = self.csv_reporter.export_campaign_summary(
                campaign_data,
                filename=f"campaign_summary_{timestamp}.csv"
            )
            logger.info(f"📄 Summary exported: {summary_file}")
            
        except Exception as e:
            logger.error(f"Failed to export CSV reports: {str(e)}")
    
    def _export_analytics(self):
        """Export analytics data to JSON."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analytics_file = self.analytics_tracker.export_analytics(
                filename=f"analytics_{timestamp}.json"
            )
            logger.info(f"📊 Analytics exported: {analytics_file}")
            
        except Exception as e:
            logger.error(f"Failed to export analytics: {str(e)}")
