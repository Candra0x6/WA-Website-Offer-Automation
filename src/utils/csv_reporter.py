"""
CSV Reporting System

Exports campaign results and analytics to CSV format:
- Campaign summary reports
- Detailed message logs
- Performance metrics
- Error reports
- Statistics export

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


logger = logging.getLogger(__name__)


@dataclass
class CampaignReportRow:
    """Single row in campaign report."""
    
    timestamp: str
    business_name: str
    phone: str
    message_type: str  # 'creation' or 'enhancement'
    status: str  # 'success', 'failed', 'skipped'
    error_message: str = ""
    message_preview: str = ""
    retry_count: int = 0
    duration_seconds: float = 0.0


class CSVReporter:
    """
    CSV reporting system for campaign results and analytics.
    
    Features:
    - Export campaign results to CSV
    - Export performance metrics
    - Export error logs
    - Export statistics summaries
    """
    
    def __init__(self, reports_dir: str = "data/reports"):
        """
        Initialize CSV reporter.
        
        Args:
            reports_dir: Directory for CSV reports
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CSV Reporter initialized: {self.reports_dir}")
    
    def export_campaign_results(
        self,
        results: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Export campaign results to CSV.
        
        Args:
            results: List of campaign result dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"campaign_results_{timestamp}.csv"
        
        output_path = self.reports_dir / filename
        
        # CSV headers
        headers = [
            'Timestamp',
            'Business Name',
            'Phone',
            'Message Type',
            'Status',
            'Error Message',
            'Message Preview',
            'Retry Count',
            'Duration (seconds)',
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for result in results:
                row = {
                    'Timestamp': result.get('timestamp', ''),
                    'Business Name': result.get('business_name', ''),
                    'Phone': result.get('phone', ''),
                    'Message Type': result.get('message_type', ''),
                    'Status': result.get('status', ''),
                    'Error Message': result.get('error', ''),
                    'Message Preview': result.get('message_preview', '')[:100],
                    'Retry Count': result.get('retry_count', 0),
                    'Duration (seconds)': result.get('duration', 0.0),
                }
                writer.writerow(row)
        
        logger.info(f"Campaign results exported: {output_path}")
        logger.info(f"Total rows: {len(results)}")
        
        return str(output_path)
    
    def export_performance_metrics(
        self,
        metrics: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Export performance metrics to CSV.
        
        Args:
            metrics: Performance metrics dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.csv"
        
        output_path = self.reports_dir / filename
        
        headers = [
            'Operation',
            'Total Operations',
            'Successful',
            'Failed',
            'Success Rate',
            'Average Duration',
            'Total Duration',
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for operation_name, operation_metrics in metrics.items():
                row = {
                    'Operation': operation_name,
                    'Total Operations': operation_metrics.get('total_operations', 0),
                    'Successful': operation_metrics.get('successful', 0),
                    'Failed': operation_metrics.get('failed', 0),
                    'Success Rate': operation_metrics.get('success_rate', '0%'),
                    'Average Duration': operation_metrics.get('average_duration', '0s'),
                    'Total Duration': operation_metrics.get('total_duration', '0s'),
                }
                writer.writerow(row)
        
        logger.info(f"Performance metrics exported: {output_path}")
        return str(output_path)
    
    def export_error_log(
        self,
        errors: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Export error log to CSV.
        
        Args:
            errors: List of error dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_log_{timestamp}.csv"
        
        output_path = self.reports_dir / filename
        
        headers = [
            'Timestamp',
            'Error Type',
            'Error Message',
            'Context',
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for error in errors:
                # Flatten context for CSV
                context_str = str(error.get('context', {}))
                
                row = {
                    'Timestamp': error.get('timestamp', ''),
                    'Error Type': error.get('error_type', ''),
                    'Error Message': error.get('error_message', ''),
                    'Context': context_str,
                }
                writer.writerow(row)
        
        logger.info(f"Error log exported: {output_path}")
        logger.info(f"Total errors: {len(errors)}")
        
        return str(output_path)
    
    def export_campaign_summary(
        self,
        campaign_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Export campaign summary to CSV.
        
        Args:
            campaign_data: Campaign summary dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"campaign_summary_{timestamp}.csv"
        
        output_path = self.reports_dir / filename
        
        # Extract campaign info
        info = campaign_data.get('campaign_info', {})
        summary = campaign_data.get('summary', {})
        rate_limiting = campaign_data.get('rate_limiting', {})
        
        # Create summary rows
        rows = [
            {'Metric': 'Campaign Details', 'Value': ''},
            {'Metric': 'Excel File', 'Value': info.get('excel_file', '')},
            {'Metric': 'Dry Run', 'Value': str(info.get('dry_run', False))},
            {'Metric': 'Start Time', 'Value': info.get('start_time', '')},
            {'Metric': 'End Time', 'Value': info.get('end_time', '')},
            {'Metric': '', 'Value': ''},
            {'Metric': 'Results Summary', 'Value': ''},
            {'Metric': 'Total Businesses', 'Value': summary.get('total_businesses', 0)},
            {'Metric': 'Processed', 'Value': summary.get('processed', 0)},
            {'Metric': 'Sent Successfully', 'Value': summary.get('sent', 0)},
            {'Metric': 'Failed', 'Value': summary.get('failed', 0)},
            {'Metric': 'Skipped', 'Value': summary.get('skipped', 0)},
            {'Metric': '', 'Value': ''},
            {'Metric': 'Rate Limiting', 'Value': ''},
            {'Metric': 'Total Sent', 'Value': rate_limiting.get('total_sent', 0)},
            {'Metric': 'Sent Today', 'Value': rate_limiting.get('sent_today', 0)},
            {'Metric': 'Sent This Hour', 'Value': rate_limiting.get('sent_this_hour', 0)},
            {'Metric': 'Daily Limit', 'Value': rate_limiting.get('daily_limit', 0)},
            {'Metric': 'Hourly Limit', 'Value': rate_limiting.get('hourly_limit', 0)},
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Metric', 'Value'])
            writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Campaign summary exported: {output_path}")
        return str(output_path)
    
    def export_statistics(
        self,
        stats: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Export general statistics to CSV.
        
        Args:
            stats: Statistics dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"statistics_{timestamp}.csv"
        
        output_path = self.reports_dir / filename
        
        # Flatten nested dictionary
        rows = []
        
        def flatten_dict(d: Dict, prefix: str = ''):
            """Recursively flatten dictionary."""
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    flatten_dict(value, full_key)
                elif isinstance(value, list):
                    rows.append({'Metric': full_key, 'Value': f"[{len(value)} items]"})
                else:
                    rows.append({'Metric': full_key, 'Value': str(value)})
        
        flatten_dict(stats)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Metric', 'Value'])
            writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Statistics exported: {output_path}")
        return str(output_path)
    
    def create_combined_report(
        self,
        campaign_data: Dict[str, Any],
        results: List[Dict[str, Any]],
        performance_metrics: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        report_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a complete report with multiple CSV files.
        
        Args:
            campaign_data: Campaign summary data
            results: Campaign results list
            performance_metrics: Performance metrics (optional)
            errors: Error log (optional)
            report_name: Base name for report files (auto-generated if None)
            
        Returns:
            Dict mapping report types to file paths
        """
        if report_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"report_{timestamp}"
        
        report_files = {}
        
        # Campaign summary
        summary_file = f"{report_name}_summary.csv"
        report_files['summary'] = self.export_campaign_summary(
            campaign_data,
            filename=summary_file
        )
        
        # Campaign results
        results_file = f"{report_name}_results.csv"
        report_files['results'] = self.export_campaign_results(
            results,
            filename=results_file
        )
        
        # Performance metrics (if provided)
        if performance_metrics:
            metrics_file = f"{report_name}_metrics.csv"
            report_files['metrics'] = self.export_performance_metrics(
                performance_metrics,
                filename=metrics_file
            )
        
        # Error log (if provided)
        if errors:
            errors_file = f"{report_name}_errors.csv"
            report_files['errors'] = self.export_error_log(
                errors,
                filename=errors_file
            )
        
        logger.info(f"Combined report created: {report_name}")
        logger.info(f"Files: {', '.join(report_files.keys())}")
        
        return report_files
