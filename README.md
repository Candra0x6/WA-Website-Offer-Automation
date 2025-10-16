# WhatsApp Offer Automation 🚀

A Python-based Selenium automation system that sends personalized cold messages via WhatsApp Web to businesses, offering either website creation or enhancement services based on their current online presence.

## 📋 Features

- ✅ **Intelligent Message Selection**: Automatically detects if a business has a website and sends appropriate messages
- ✅ **Persistent Session**: Scan QR code once, reuse session for subsequent runs
- ✅ **Anti-Ban Protection**: Random delays, rate limiting, and message variations
- ✅ **Excel Integration**: Easy data management with Excel spreadsheets
- ✅ **Enhanced Logging**: Multi-handler logging system with rotation and JSON output
- ✅ **CSV Reporting**: Comprehensive campaign reports and message logs
- ✅ **Real-time Analytics**: Performance tracking and distribution analysis
- ✅ **Dry-Run Mode**: Test your messages without actually sending them
- ✅ **Retry Mechanism**: Automatic retries with exponential backoff
- ✅ **Configurable**: Extensive configuration via environment variables

## 🏗️ Project Structure

```
whatsapp-offer/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   ├── prd.md                       # Product Requirements Document
│   ├── implementation-plan.md       # Implementation Plan
│   ├── PHASE6_COMPLETION.md        # Phase 6 Completion Report
│   └── usage-guide.md              # Detailed Usage Guide
│
├── src/
│   ├── main.py                      # Entry point
│   ├── config/
│   │   ├── settings.py              # Configuration management
│   │   └── templates.py             # Message templates
│   ├── core/
│   │   ├── excel_handler.py         # Excel data processing
│   │   ├── message_composer.py      # Message generation
│   │   ├── whatsapp_controller.py   # WhatsApp automation
│   │   └── session_manager.py       # Session management
│   ├── utils/
│   │   ├── validators.py            # Data validation
│   │   ├── delay_manager.py         # Anti-ban delays
│   │   ├── enhanced_logging.py      # Enhanced logging system
│   │   ├── csv_reporter.py          # CSV export functionality
│   │   ├── analytics_tracker.py     # Real-time analytics
│   │   └── logger.py                # Basic logging
│   └── models/
│       ├── business.py              # Business model
│       └── message_log.py           # Log entry model
│
├── data/
│   ├── data.xlsx                    # Input Excel file
│   ├── reports/                     # CSV campaign reports
│   └── analytics/                   # Analytics JSON files
│
├── logs/
│   ├── delivery_log.csv             # Message delivery logs
│   ├── whatsapp_automation.log      # Main application log
│   ├── errors.log                   # Error log
│   └── json_logs.json               # Structured JSON logs
│
└── tests/
    └── ...                          # Test files
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Google Chrome** (latest version)
- **WhatsApp Account**
- **Excel file** with business data

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-offer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` file with your settings (optional, defaults work fine)

6. **Prepare your data**
   - Create `data/data.xlsx` with these columns:
     - `Business Name` (required)
     - `Description` (optional)
     - `Website` (optional - determines message type)
     - `Phone` (required - international format)
     - `Google Maps Link` (optional)

### First Run

1. **Test with dry-run mode** (recommended)
   ```bash
   python src/main.py --dry-run
   ```

2. **Run for real** (scans QR code on first run)
   ```bash
   python src/main.py
   ```

3. **Scan the QR code** when prompted (only needed once!)

4. **Watch the magic happen** ✨

## 📊 Excel File Format

Your `data/data.xlsx` should look like this:

| Business Name | Description | Website | Phone | Google Maps Link |
|---------------|-------------|---------|-------|------------------|
| Coffee Shop | Local cafe | | +1234567890 | https://maps... |
| Tech Startup | Software dev | https://example.com | +0987654321 | https://maps... |

**Important Notes:**
- `Phone` must be in international format (e.g., `+1234567890`, `6281234567890`)
- If `Website` is **empty**, system sends **"website creation"** message
- If `Website` has a **URL**, system sends **"website enhancement"** message

## ⚙️ Configuration

Edit `.env` file to customize settings:

```env
# Rate Limiting (IMPORTANT for anti-ban!)
MIN_MESSAGE_DELAY=20          # Minimum seconds between messages
MAX_MESSAGE_DELAY=90          # Maximum seconds between messages
BATCH_SIZE=15                 # Messages before long break
MAX_DAILY_MESSAGES=50         # Maximum messages per day

# Delays
MIN_BATCH_DELAY=300           # 5 minutes
MAX_BATCH_DELAY=900           # 15 minutes

# Mode
DRY_RUN=False                 # Set to True for testing
HEADLESS=False                # Set to True to hide browser
```

## 🎯 Usage Examples

### Basic Usage
```bash
# Send messages with default settings
python src/main.py
```

### Dry-Run Mode (Test First!)
```bash
# Preview messages without sending
python src/main.py --dry-run
```

### Custom Excel File
```bash
# Use a different Excel file
python src/main.py --excel path/to/your/file.xlsx
```

### Headless Mode
```bash
# Run without showing browser
python src/main.py --headless
```

### Custom Rate Limiting
```bash
# Override delay settings
python src/main.py --min-delay 30 --max-delay 120
```

## 📝 Message Templates

The system includes **5 creation templates** and **5 enhancement templates** that are randomly selected to add variation.

**Creation Template Example:**
> Hi {business_name}, your business sounds amazing! I help local brands like yours create professional websites that attract more customers online. Would you like me to send a free mockup idea?

**Enhancement Template Example:**
> Hey {business_name}, I checked out your website ({website}) — it's great! I specialize in modern redesigns that improve speed, mobile look, and Google ranking. Would you like a free concept preview?

Templates are in `src/config/templates.py` - feel free to customize!

## 📊 Logs & Monitoring

### Enhanced Logging System (Phase 6)
The system now includes a comprehensive logging infrastructure:

**Log Files** (`logs/` directory):
- `whatsapp_automation.log` - All application logs
- `errors.log` - Error logs only
- `json_logs.json` - Structured JSON logs for analytics
- `delivery_log.csv` - Message delivery logs

**Log Rotation**: Automatic rotation at 10MB with 5 backup files

### CSV Reports
Campaign reports are automatically generated in `data/reports/`:

**Campaign Results** (`campaign_results_YYYYMMDD_HHMMSS.csv`):
```csv
business_name,phone,website,message_type,status,error,timestamp
Coffee Shop,+1234567890,,creation,success,,2025-10-16T10:30:00
Tech Startup,+0987654321,https://example.com,enhancement,success,,2025-10-16T10:32:15
```

**Campaign Summary** (`campaign_summary_YYYYMMDD_HHMMSS.csv`):
- Total messages, sent, failed, skipped
- Success rate and duration
- Rate limiting statistics

### Real-Time Analytics
Analytics data is saved to `data/analytics/analytics_YYYYMMDD_HHMMSS.json`:

```json
{
  "campaign_id": "campaign_20251016_133355",
  "metrics": {
    "total_businesses": 11,
    "messages_sent": 11,
    "messages_failed": 0,
    "success_rate": 100.0
  },
  "message_distribution": {
    "creation": 6,
    "enhancement": 5
  },
  "hourly_distribution": {...}
}
```

### Legacy CSV Logs
All message delivery attempts are also logged to `logs/delivery_log.csv`:

```csv
timestamp,business_name,phone,website,message_type,status,error_message,retry_count
2025-10-16T10:30:00,Coffee Shop,+1234567890,,creation,success,,0
2025-10-16T10:32:15,Tech Startup,+0987654321,https://example.com,enhancement,success,,0
```

### Console Output
Real-time progress with colored output:
```
2025-10-16 10:30:00 | INFO     | [1/10] (10.0%) Processing: Coffee Shop
2025-10-16 10:30:05 | INFO     | ✅ Coffee Shop (+1234567890) - SUCCESS
```

### Session Summary
After completion, you'll see enhanced analytics:
```
============================================================
📊 CAMPAIGN ANALYTICS
============================================================

📈 Overall Performance:
   Total Businesses: 50
   Messages Sent: 48
   Messages Failed: 1
   Messages Skipped: 1
   Success Rate: 96.00%
   Average Time: 1.23s

📝 Message Types:
   Creation: 30 (62.5%)
   Enhancement: 18 (37.5%)

⚡ Rate Limiting:
   Rate Limit Hits: 2
   Batch Delays: 3
============================================================

📄 Reports generated:
   - data/reports/campaign_results_20251016_103000.csv
   - data/reports/campaign_summary_20251016_103000.csv
   - data/analytics/analytics_20251016_103000.json
```

## 🛡️ Safety & Best Practices

### Anti-Ban Measures
✅ Random delays (20-90 seconds)
✅ Batch processing with long breaks
✅ Daily message limits (default: 50)
✅ Message template variations
✅ Session persistence (no repeated logins)

### Recommendations
- **Start small**: Test with 5-10 contacts first
- **Use dry-run**: Always test before sending
- **Monitor closely**: Watch for WhatsApp warnings
- **Respect limits**: Don't exceed 50 messages/day
- **Add value**: Only message relevant businesses
- **Include opt-out**: Add unsubscribe option

### ⚠️ Legal Considerations
- Comply with local anti-spam laws
- Follow GDPR/privacy regulations
- Respect WhatsApp Terms of Service
- Obtain consent where required
- Provide opt-out mechanism

## 🧪 Testing

Run tests with pytest:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_excel_handler.py
```

## 🐛 Troubleshooting

### QR Code Not Appearing
- Make sure WhatsApp Web is accessible
- Try running without `--headless` flag
- Check your internet connection

### Messages Not Sending
- Verify phone numbers are in international format
- Check if WhatsApp Web session is active
- Look for errors in console output
- Check `logs/delivery_log.csv` for details

### Session Expired
- Delete `chrome_profile_whatsapp/` folder
- Run the script again to re-scan QR code

### Rate Limit / Ban Warning
- **STOP immediately**
- Wait 24 hours
- Reduce `MAX_DAILY_MESSAGES`
- Increase delay ranges

## 🔧 Development

### Project Status
✅ **Phase 1**: Project Setup & Core Infrastructure (COMPLETED)
✅ **Phase 2**: Data Processing Layer (COMPLETED)
✅ **Phase 3**: Message Composition Engine (COMPLETED)
✅ **Phase 4**: WhatsApp Automation Core (COMPLETED)
✅ **Phase 5**: Rate Limiting & Campaign Management (COMPLETED)
✅ **Phase 6**: Logging, CSV Reporting & Analytics (COMPLETED)
✅ **Phase 7**: Main Application & CLI Enhancement (COMPLETED)
✅ **Phase 8**: Testing & Quality Assurance (COMPLETED)
⏳ **Phase 9**: Documentation & Deployment (Final Phase)

### Phase 2 Highlights
- ✅ Phone number validation (international support)
- ✅ URL validation
- ✅ Business name sanitization
- ✅ Excel data handler with error tracking
- ✅ 56 unit tests (70% coverage)
- ✅ Sample data for testing

### Phase 3 Highlights
- ✅ Intelligent message type detection
- ✅ Template-based personalization
- ✅ URL encoding for WhatsApp Web
- ✅ WhatsApp URL generation
- ✅ 31 unit tests (70% coverage)
- ✅ Complete integration with Phases 1-2

### Phase 4 Highlights
- ✅ Selenium-based WhatsApp Web automation
- ✅ Chrome session persistence (QR scan once)
- ✅ Human-like typing with random delays
- ✅ Message sending with retry logic
- ✅ Session management and validation
- ✅ Anti-automation detection measures

### Phase 5 Highlights
- ✅ Intelligent rate limiting (50/day, 15/hour)
- ✅ Random delays (20-90s between messages)
- ✅ Batch delays (5-15min after 10-20 messages)
- ✅ Complete campaign orchestration
- ✅ Progress tracking with resume capability
- ✅ Command-line interface (main.py)
- ✅ 25 tests passing (100% success rate)

### Phase 6 Highlights
- ✅ Multi-handler logging system (console, file, rotating, JSON)
- ✅ CSV reporting (8 comprehensive reports)
- ✅ Real-time analytics tracking
- ✅ Performance monitoring and metrics
- ✅ Campaign data exports

### Phase 7 Highlights
- ✅ Professional CLI with 14 command-line options
- ✅ Configuration validation (--validate)
- ✅ Interactive setup wizard (--interactive)
- ✅ System information tools (--version, --info)
- ✅ JSON configuration file support
- ✅ Enhanced UX (colors, verbose modes, quiet operation)

### Phase 8 Highlights
- ✅ Comprehensive testing suite (22 tests across 3 files)
- ✅ 100% campaign success validation
- ✅ File generation testing (CSV reports, analytics)
- ✅ CLI feature validation
- ✅ Production readiness confirmed
- ✅ Quality metrics documented
- ✅ CSV export for campaign results and summaries
- ✅ Real-time analytics tracking (metrics, distributions, timing)
- ✅ Seamless integration into campaign manager
- ✅ Log rotation (10MB max, 5 backups)
- ✅ Hourly message distribution tracking
- ✅ 4 integration tests passing (100% success rate)

### Phase 7 Highlights
- ✅ Enhanced CLI with 14 command-line options
- ✅ Configuration validation system (--validate)
- ✅ Interactive setup wizard (--interactive)
- ✅ Version and system info commands (--version, --info)
- ✅ JSON config file support (--config)
- ✅ Organized argument groups (Actions, Files, Modes, Logging)
- ✅ Comprehensive help documentation with examples
- ✅ All CLI features tested and working

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📚 Documentation

- **[PRD](docs/prd.md)**: Product Requirements Document
- **[Implementation Plan](docs/implementation-plan.md)**: Detailed development roadmap
- **[Phase 1 Completion](docs/phase1-completion.md)**: Phase 1 Summary
- **[Phase 2 Completion](docs/phase2-completion.md)**: Phase 2 Summary
- **[Phase 3 Completion](docs/phase3-completion.md)**: Phase 3 Summary
- **[Phase 5 Completion](docs/PHASE5_COMPLETION.md)**: Phase 5 Summary
- **[Phase 6 Completion](docs/PHASE6_COMPLETION.md)**: Phase 6 Summary
- **[Phase 7 Completion](docs/PHASE7_COMPLETION.md)**: Phase 7 Summary
- **[Usage Guide](docs/usage-guide.md)**: Comprehensive user guide (coming soon)

## 🔮 Future Enhancements

- 🔄 Multi-account support
- 📊 Advanced analytics dashboard
- 🤖 AI-powered message generation
- ⏰ Smart scheduling
- 📱 Response monitoring
- 🌐 Web UI for management

## 📄 License

This project is for educational purposes. Use responsibly and ethically.

## 🤝 Support

For issues, questions, or suggestions:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review logs in `logs/delivery_log.csv`
3. Open an issue on GitHub

## ⚠️ Disclaimer

This tool is for legitimate business outreach only. Users are responsible for:
- Complying with local laws and regulations
- Following WhatsApp Terms of Service
- Obtaining necessary consent
- Not spamming or harassing recipients
- Using ethical business practices

**Use at your own risk. The authors are not responsible for any misuse or consequences.**

---

**Made with ❤️ for ethical business growth**

**Version**: 1.0.0  
**Last Updated**: October 16, 2025  
**Status**: Phase 7 Complete ✅
