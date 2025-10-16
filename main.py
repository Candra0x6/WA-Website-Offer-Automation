"""
Main Script - WhatsApp Message Campaign Runner

Entry point for running WhatsApp message campaigns.
Supports dry-run mode, resume capability, and configurable rate limiting.

Usage:
    python main.py                    # Run campaign with default settings
    python main.py --dry-run          # Preview without sending
    python main.py --headless         # Run in headless mode
    python main.py --resume           # Resume previous campaign
    python main.py --validate         # Validate configuration
    python main.py --interactive      # Interactive setup wizard
    python main.py --version          # Show version information
    python main.py --info             # Show system information

Author: WhatsApp Automation System
Date: 2025-10-16
Version: 1.0.0
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.campaign_manager import CampaignManager
from src.core.delay_manager import create_default_delay_manager, create_test_delay_manager
from src.utils.logger import setup_logger

# Version information
__version__ = "1.0.0"
__author__ = "WhatsApp Automation System"
__last_updated__ = "2025-10-16"


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='WhatsApp Message Campaign Runner - Automated business outreach system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python main.py                          # Run campaign with default settings
  python main.py --dry-run                # Preview messages without sending
  
  # Configuration
  python main.py --validate               # Validate configuration and data
  python main.py --interactive            # Interactive setup wizard
  python main.py --config campaign.json   # Load settings from config file
  
  # Execution modes
  python main.py --headless               # Run without browser UI
  python main.py --resume                 # Resume from last position
  python main.py --test                   # Use test mode (fast delays)
  
  # Data files
  python main.py --excel data/test.xlsx   # Use different Excel file
  python main.py --profile my_profile     # Use custom Chrome profile
  
  # Information
  python main.py --version                # Show version information
  python main.py --info                   # Show system information
  python main.py --help                   # Show this help message

Features:
  ✓ Intelligent message selection (creation vs enhancement)
  ✓ Session persistence (scan QR code once)
  ✓ Anti-ban protection with rate limiting
  ✓ Comprehensive logging and analytics
  ✓ CSV reports and real-time metrics
  ✓ Dry-run mode for testing
  ✓ Campaign resume capability
        """
    )
    
    # Action commands
    action_group = parser.add_argument_group('Action Commands')
    action_group.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration and data without running campaign'
    )
    
    action_group.add_argument(
        '--interactive',
        action='store_true',
        help='Run interactive setup wizard'
    )
    
    action_group.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )
    
    action_group.add_argument(
        '--info',
        action='store_true',
        help='Show detailed system information and exit'
    )
    
    # File inputs
    file_group = parser.add_argument_group('File Inputs')
    file_group.add_argument(
        '--excel',
        default='data/data.xlsx',
        help='Path to Excel file with business data (default: data/data.xlsx)'
    )
    
    file_group.add_argument(
        '--profile',
        default='chrome_profile_whatsapp',
        help='Chrome profile directory for WhatsApp session (default: chrome_profile_whatsapp)'
    )
    
    file_group.add_argument(
        '--config',
        help='Path to JSON configuration file for campaign settings'
    )
    
    # Execution modes
    mode_group = parser.add_argument_group('Execution Modes')
    mode_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview messages without actually sending them'
    )
    
    mode_group.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no UI)'
    )
    
    mode_group.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last saved progress'
    )
    
    mode_group.add_argument(
        '--test',
        action='store_true',
        help='Use test mode with faster delays and no rate limits'
    )
    
    # Logging options
    log_group = parser.add_argument_group('Logging Options')
    log_group.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    log_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output (only errors)'
    )
    
    log_group.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored console output'
    )
    
    return parser.parse_args()


def validate_inputs(args):
    """Validate command line arguments."""
    excel_file = Path(args.excel)
    
    if not excel_file.exists():
        print(f"❌ Error: Excel file not found: {excel_file}")
        print(f"   Please create {excel_file} or specify a different file with --excel")
        return False
    
    if not excel_file.suffix in ['.xlsx', '.xls']:
        print(f"❌ Error: Invalid file type: {excel_file.suffix}")
        print(f"   Expected .xlsx or .xls file")
        return False
    
    return True


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("🤖 WHATSAPP MESSAGE CAMPAIGN SYSTEM")
    print("=" * 60)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print("=" * 60 + "\n")


def print_version():
    """Print version information."""
    print(f"\nWhatsApp Campaign System v{__version__}")
    print(f"Last Updated: {__last_updated__}")
    print(f"Author: {__author__}")
    print("\nFeatures:")
    print("  ✓ Intelligent message selection")
    print("  ✓ Session persistence")
    print("  ✓ Anti-ban protection")
    print("  ✓ Comprehensive logging")
    print("  ✓ CSV reports & analytics")
    print("  ✓ Dry-run testing")
    print("  ✓ Campaign resume")
    print()


def print_system_info():
    """Print detailed system information."""
    import platform
    import selenium
    import pandas as pd
    
    print("\n" + "=" * 60)
    print("📊 SYSTEM INFORMATION")
    print("=" * 60)
    
    # Application info
    print("\n📦 Application:")
    print(f"   Version: {__version__}")
    print(f"   Last Updated: {__last_updated__}")
    
    # Python info
    print("\n🐍 Python:")
    print(f"   Version: {platform.python_version()}")
    print(f"   Implementation: {platform.python_implementation()}")
    
    # System info
    print("\n💻 System:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Dependencies
    print("\n📚 Dependencies:")
    print(f"   Selenium: {selenium.__version__}")
    print(f"   Pandas: {pd.__version__}")
    
    try:
        import phonenumbers
        print(f"   PhoneNumbers: {phonenumbers.__version__}")
    except:
        pass
    
    try:
        import openpyxl
        print(f"   OpenPyXL: {openpyxl.__version__}")
    except:
        pass
    
    # File locations
    print("\n📁 Directories:")
    print(f"   Working Dir: {Path.cwd()}")
    print(f"   Script Dir: {Path(__file__).parent}")
    
    data_dir = Path('data')
    print(f"   Data Dir: {data_dir.absolute()} {'✓' if data_dir.exists() else '✗'}")
    
    logs_dir = Path('logs')
    print(f"   Logs Dir: {logs_dir.absolute()} {'✓' if logs_dir.exists() else '✗'}")
    
    reports_dir = Path('data/reports')
    print(f"   Reports Dir: {reports_dir.absolute()} {'✓' if reports_dir.exists() else '✗'}")
    
    analytics_dir = Path('data/analytics')
    print(f"   Analytics Dir: {analytics_dir.absolute()} {'✓' if analytics_dir.exists() else '✗'}")
    
    print("\n" + "=" * 60 + "\n")


def validate_configuration(args):
    """
    Validate all configuration and data files.
    
    Returns:
        tuple: (success: bool, errors: list, warnings: list)
    """
    errors = []
    warnings = []
    
    print("\n" + "=" * 60)
    print("🔍 CONFIGURATION VALIDATION")
    print("=" * 60 + "\n")
    
    # Check Excel file
    print("📋 Checking Excel file...")
    excel_file = Path(args.excel)
    if not excel_file.exists():
        errors.append(f"Excel file not found: {excel_file}")
        print(f"   ✗ File not found: {excel_file}")
    elif not excel_file.suffix in ['.xlsx', '.xls']:
        errors.append(f"Invalid Excel file type: {excel_file.suffix}")
        print(f"   ✗ Invalid file type: {excel_file.suffix}")
    else:
        print(f"   ✓ Excel file found: {excel_file}")
        
        # Try to load and validate Excel data
        try:
            import pandas as pd
            df = pd.read_excel(excel_file)
            
            print(f"   ✓ Total rows: {len(df)}")
            
            # Check required columns
            required_cols = ['Business Name', 'Phone']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                errors.append(f"Missing required columns: {', '.join(missing_cols)}")
                print(f"   ✗ Missing columns: {', '.join(missing_cols)}")
            else:
                print(f"   ✓ All required columns present")
                
                # Count non-empty phone numbers as proxy for valid businesses
                valid_count = df['Phone'].notna().sum()
                print(f"   ✓ Rows with phone numbers: {valid_count}")
                
                if valid_count == 0:
                    errors.append("No valid businesses found (all phone numbers empty)")
                    print(f"   ✗ No valid businesses found!")
            
        except Exception as e:
            errors.append(f"Failed to load Excel file: {str(e)}")
            print(f"   ✗ Error loading file: {str(e)}")
    
    # Check directories
    print("\n📁 Checking directories...")
    data_dir = Path('data')
    if not data_dir.exists():
        warnings.append(f"Data directory not found: {data_dir}")
        print(f"   ⚠ Data directory will be created: {data_dir}")
    else:
        print(f"   ✓ Data directory exists: {data_dir}")
    
    logs_dir = Path('logs')
    if not logs_dir.exists():
        warnings.append(f"Logs directory not found: {logs_dir}")
        print(f"   ⚠ Logs directory will be created: {logs_dir}")
    else:
        print(f"   ✓ Logs directory exists: {logs_dir}")
    
    reports_dir = Path('data/reports')
    if not reports_dir.exists():
        print(f"   ⚠ Reports directory will be created: {reports_dir}")
    else:
        print(f"   ✓ Reports directory exists: {reports_dir}")
    
    analytics_dir = Path('data/analytics')
    if not analytics_dir.exists():
        print(f"   ⚠ Analytics directory will be created: {analytics_dir}")
    else:
        print(f"   ✓ Analytics directory exists: {analytics_dir}")
    
    # Check Chrome profile
    print("\n🌐 Checking Chrome profile...")
    profile_dir = Path(args.profile)
    if profile_dir.exists():
        print(f"   ✓ Chrome profile exists: {profile_dir}")
        print(f"   ℹ  QR scan not required (session exists)")
    else:
        print(f"   ℹ  Chrome profile will be created: {profile_dir}")
        print(f"   ℹ  QR scan will be required on first run")
    
    # Check config file if specified
    if args.config:
        print("\n⚙️  Checking config file...")
        config_file = Path(args.config)
        if not config_file.exists():
            errors.append(f"Config file not found: {config_file}")
            print(f"   ✗ File not found: {config_file}")
        else:
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                print(f"   ✓ Config file loaded: {config_file}")
                print(f"   ✓ Settings: {len(config_data)} options")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in config file: {str(e)}")
                print(f"   ✗ Invalid JSON: {str(e)}")
            except Exception as e:
                errors.append(f"Error reading config file: {str(e)}")
                print(f"   ✗ Error: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ Errors: {len(errors)}")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print("\n✅ No errors found")
    
    if warnings:
        print(f"\n⚠️  Warnings: {len(warnings)}")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("\n✅ No warnings")
    
    success = len(errors) == 0
    status_msg = "VALIDATION PASSED ✅" if success else "VALIDATION FAILED ❌"
    print(f"\n{status_msg}")
    print("=" * 60 + "\n")
    
    return success, errors, warnings


def interactive_setup():
    """Interactive campaign setup wizard."""
    print("\n" + "=" * 60)
    print("🧙 INTERACTIVE CAMPAIGN SETUP WIZARD")
    print("=" * 60 + "\n")
    
    print("This wizard will guide you through setting up your campaign.")
    print("Press Ctrl+C at any time to cancel.\n")
    
    config = {}
    
    try:
        # Excel file
        print("📋 Step 1: Excel File")
        default_excel = "data/data.xlsx"
        excel_input = input(f"   Excel file path [{default_excel}]: ").strip()
        config['excel'] = excel_input if excel_input else default_excel
        
        # Validate Excel file
        if not Path(config['excel']).exists():
            print(f"   ⚠️  Warning: File not found: {config['excel']}")
            create = input("   Create a sample Excel file? (yes/no): ").lower()
            if create in ['yes', 'y']:
                print("   ℹ  Please use the sample template in docs/")
        
        # Chrome profile
        print("\n🌐 Step 2: Chrome Profile")
        default_profile = "chrome_profile_whatsapp"
        profile_input = input(f"   Profile directory [{default_profile}]: ").strip()
        config['profile'] = profile_input if profile_input else default_profile
        
        # Execution mode
        print("\n🚀 Step 3: Execution Mode")
        print("   1. Live (send real messages)")
        print("   2. Dry-run (preview only)")
        mode_input = input("   Select mode [1/2]: ").strip()
        config['dry_run'] = (mode_input == '2')
        
        # Headless mode
        print("\n🖥️  Step 4: Browser Mode")
        headless_input = input("   Run in headless mode? (yes/no) [no]: ").lower()
        config['headless'] = headless_input in ['yes', 'y']
        
        # Test mode
        print("\n⚡ Step 5: Rate Limiting")
        test_input = input("   Use test mode (fast delays)? (yes/no) [no]: ").lower()
        config['test'] = test_input in ['yes', 'y']
        
        # Resume
        print("\n🔄 Step 6: Resume")
        resume_input = input("   Resume from previous campaign? (yes/no) [no]: ").lower()
        config['resume'] = resume_input in ['yes', 'y']
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"   Excel File: {config['excel']}")
        print(f"   Chrome Profile: {config['profile']}")
        print(f"   Mode: {'DRY RUN' if config['dry_run'] else 'LIVE'}")
        print(f"   Browser: {'Headless' if config['headless'] else 'Headed'}")
        print(f"   Test Mode: {'Yes' if config['test'] else 'No'}")
        print(f"   Resume: {'Yes' if config['resume'] else 'No'}")
        print("=" * 60 + "\n")
        
        # Confirm
        confirm = input("Start campaign with these settings? (yes/no): ").lower()
        if confirm not in ['yes', 'y']:
            print("\n❌ Campaign cancelled")
            return None
        
        return config
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return None


def load_config_file(config_path):
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Loaded configuration from: {config_path}")
        return config
    except Exception as e:
        print(f"❌ Error loading config file: {str(e)}")
        sys.exit(1)


def print_configuration(args):
    """Print campaign configuration."""
    print("📋 Configuration:")
    print(f"   Excel File: {args.excel}")
    print(f"   Chrome Profile: {args.profile}")
    print(f"   Mode: {'DRY RUN 🧪' if args.dry_run else 'LIVE 🚀'}")
    print(f"   Browser: {'Headless' if args.headless else 'Headed'}")
    print(f"   Resume: {'Yes' if args.resume else 'No'}")
    print(f"   Test Mode: {'Yes ⚡' if args.test else 'No'}")
    print(f"   Logging: {'Quiet' if hasattr(args, 'quiet') and args.quiet else ('Verbose' if args.verbose else 'Normal')}")
    if hasattr(args, 'config') and args.config:
        print(f"   Config File: {args.config}")
    print()


def confirm_start(args):
    """Ask user to confirm before starting campaign."""
    if args.dry_run:
        print("ℹ️  Running in DRY RUN mode - no messages will be sent")
        return True
    
    print("⚠️  WARNING: This will send real WhatsApp messages!")
    print("⚠️  Make sure you have reviewed the message templates.")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    return response.lower() in ['yes', 'y']


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Handle version command
    if args.version:
        print_version()
        sys.exit(0)
    
    # Handle info command
    if args.info:
        print_system_info()
        sys.exit(0)
    
    # Handle validate command
    if args.validate:
        success, errors, warnings = validate_configuration(args)
        sys.exit(0 if success else 1)
    
    # Handle interactive mode
    if args.interactive:
        config = interactive_setup()
        if config is None:
            sys.exit(0)
        # Override args with interactive config
        args.excel = config['excel']
        args.profile = config['profile']
        args.dry_run = config['dry_run']
        args.headless = config['headless']
        args.test = config['test']
        args.resume = config['resume']
    
    # Load config file if specified
    if args.config:
        file_config = load_config_file(args.config)
        # Merge file config with args (args take precedence)
        for key, value in file_config.items():
            if not hasattr(args, key) or getattr(args, key) is None:
                setattr(args, key, value)
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logger = setup_logger(__name__, level=log_level)
    
    # Print banner
    print_banner()
    
    # Validate inputs
    if not validate_inputs(args):
        sys.exit(1)
    
    # Print configuration
    print_configuration(args)
    
    # Confirm start (unless in interactive mode - already confirmed)
    if not args.interactive and not confirm_start(args):
        print("\n❌ Campaign cancelled by user")
        sys.exit(0)
    
    try:
        # Create delay manager
        if args.test:
            logger.info("Using TEST mode delay manager")
            delay_manager = create_test_delay_manager(
                stats_file='data/delay_stats_test.json'
            )
        else:
            delay_manager = create_default_delay_manager(
                stats_file='data/delay_stats.json'
            )
        
        # Create campaign manager
        progress_file = 'data/campaign_progress.json' if args.resume else None
        
        campaign = CampaignManager(
            excel_file=args.excel,
            chrome_profile=args.profile,
            delay_manager=delay_manager,
            progress_file=progress_file,
            dry_run=args.dry_run
        )
        
        # Run campaign
        success = campaign.run_campaign(headless=args.headless)
        
        if success:
            print("\n✅ Campaign completed successfully!")
            print(f"\n📊 Results saved to:")
            print(f"   - data/reports/")
            print(f"   - data/analytics/")
            print(f"   - logs/")
            sys.exit(0)
        else:
            print("\n⚠️ Campaign completed with errors")
            print(f"   Check logs/ directory for details")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Campaign interrupted by user")
        print("   Progress has been saved. Use --resume to continue.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
