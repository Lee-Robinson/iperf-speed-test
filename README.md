# IPERF Speed Test Monitor
![Screenshot 2025-05-31 at 08 32 27](https://github.com/user-attachments/assets/564f3695-f6a4-497d-b898-83b6c43fe88f)
![Screenshot 2025-05-31 at 11 12 56](https://github.com/user-attachments/assets/2561074a-9172-4d87-a183-05873d7837a7)

# IPERF Speed Test Monitor

🚀 A Python script to perform automated IPERF speed tests and generate comprehensive reports for ISP speed monitoring.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🌐 **Multiple UK & International Servers**: Choose from 9 reliable IPERF3 servers worldwide, with 5 UK-specific options
- ⏰ **Flexible Duration Control**: Run tests for 1-24 hours or continuously until stopped
- ⏱️ **Customizable Intervals**: Test every 30 seconds to 30 minutes with preset and custom options
- 📊 **Real-time Progress Tracking**: Live progress bars, elapsed time, and remaining time display
- 📝 **Detailed Logging**: Track all test results with timestamps in structured log files
- 📄 **Professional HTML Reports**: Beautiful, responsive reports with statistics and performance graphs
- 🎯 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- ⚡ **Real-time Display**: See upload/download speeds as tests complete with success rate tracking
- 🛡️ **Error Handling**: Graceful handling of network issues, timeouts, and server failures

## Screenshots

### Interactive Server Selection
```
🌐 IPERF Server Selection
========================================
🇬🇧 UK Servers (Recommended for UK users):
1. iperf.as42831.net (London) - UK Servers, Reliable
2. speedtest.lon1.uk.leaseweb.net (London) - LeaseWeb
3. speedtest.lon12.uk.leaseweb.net (London) - LeaseWeb Alt
4. lon.speedtest.clouvider.net (London) - Clouvider
5. 185.59.221.51 (London) - DATAPACKET

🌍 International Servers:
6. ams.speedtest.clouvider.net (Amsterdam) - Very Reliable
7. speedtest.wtnet.de (Germany) - High Speed
8. speedtest.init7.net (Switzerland) - Stable
9. nyc.speedtest.clouvider.net (New York) - US
10. Enter custom server
```

### Real-time Progress Monitoring
```
🔄 [████████░░░░░░░░░░░░] 40%
⚡ 14:23:15 | Upload: 25.43 Mbps | Download: 89.21 Mbps
📊 Status: 12 tests, 0 failures (100.0% success)
⏱️  Elapsed: 01:01 | Remaining: 28m
--------------------------------------------------
```

### Professional File Output
```
==================================================
📁 FILES GENERATED:
📝 Log file: /Users/leerobinson/iperf_speed_test.log
📄 HTML report: /Users/leerobinson/iperf_speed_report.html
==================================================
```

## Installation

### Prerequisites
You need `iperf3` installed on your system:

#### macOS
```bash
brew install iperf3
```

#### Windows
```bash
# Using Chocolatey
choco install iperf3

# Using Scoop
scoop install iperf3

# Or download from: https://iperf.fr/iperf-download.php
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install iperf3
```

#### Linux (Red Hat/CentOS/Fedora)
```bash
sudo yum install iperf3  # or dnf install iperf3
```

### Quick Start - One Command Download & Run
```bash
# Download and run immediately
curl -O https://raw.githubusercontent.com/Lee-Robinson/iperf-speed-test/main/iperf_test.py && python3 iperf_test.py
```

### Alternative Installation Methods

**Option 1: Git Clone**
```bash
git clone https://github.com/Lee-Robinson/iperf-speed-test.git
cd iperf-speed-test
python3 iperf_test.py
```

**Option 2: wget (Linux/macOS)**
```bash
wget https://raw.githubusercontent.com/Lee-Robinson/iperf-speed-test/main/iperf_test.py
python3 iperf_test.py
```

**Option 3: Manual Download**
1. Download `iperf_test.py` from the repository
2. Run: `python3 iperf_test.py`

## Usage

### 1. Run the Script
```bash
python3 iperf_test.py
```

### 2. Interactive Configuration
The script will guide you through three simple configuration steps:

**Server Selection:**
- Choose from 5 UK servers (recommended for UK users)
- Select from 4 reliable international servers
- Or enter your own custom server details

**Test Interval:**
- 30 seconds (ideal for short tests)
- 1, 5, 10, or 30 minutes
- Custom interval in minutes

**Test Duration:**
- Quick presets: 1h, 2h, 4h, 8h, 24h
- Continuous mode (until manually stopped)
- Custom duration (0.1 to 24 hours)

### 3. Monitor Results
- **Real-time progress bar** showing completion percentage
- **Live speed results** for each test with timestamps
- **Status updates** showing success rate and timing
- **Automatic report generation** every 10 tests

### 4. Review Results
- **Text log**: `iperf_speed_test.log` with detailed test data
- **HTML report**: `iperf_speed_report.html` with interactive charts and statistics

## Server Options

The script includes carefully selected servers for optimal performance:

### UK Servers (Recommended for UK Users)
| Server | Location | Provider | Speed | Description |
|--------|----------|----------|-------|-------------|
| iperf.as42831.net | London | UK Servers | 10 Gbps | Most reliable for UK |
| speedtest.lon1.uk.leaseweb.net | London | LeaseWeb | 10 Gbps | Primary LeaseWeb |
| speedtest.lon12.uk.leaseweb.net | London | LeaseWeb | 10 Gbps | Alternative LeaseWeb |
| lon.speedtest.clouvider.net | London | Clouvider | 10 Gbps | Clouvider London |
| 185.59.221.51 | London | DATAPACKET | 10 Gbps | DATAPACKET London |

### International Servers
| Server | Location | Provider | Speed | Description |
|--------|----------|----------|-------|-------------|
| ams.speedtest.clouvider.net | Amsterdam | Clouvider | 10 Gbps | Very reliable |
| speedtest.wtnet.de | Germany | wilhelm.tel | 40 Gbps | High speed testing |
| speedtest.init7.net | Switzerland | Init7 | 20 Gbps | Very stable |
| nyc.speedtest.clouvider.net | New York | Clouvider | 10 Gbps | US East Coast |

## Output Files

### Log File (`iperf_speed_test.log`)
```
2025-05-31T14:23:15.123456 | SUCCESS | ↑ 25.43 Mbps | ↓ 89.21 Mbps | Server: iperf.as42831.net
2025-05-31T14:28:15.789012 | SUCCESS | ↑ 24.87 Mbps | ↓ 91.05 Mbps | Server: iperf.as42831.net
```

### HTML Report Features
- **Executive Summary**: Total tests, success rate, average speeds
- **Performance Statistics**: Min/max/average upload and download speeds
- **Detailed Results Table**: Individual test results with timestamps
- **Professional Styling**: Clean, printable format with charts
- **Author Attribution**: Links to GitHub repository

## Configuration Examples

### Short Diagnostic Test
- **Server**: UK server (option 1-5)
- **Interval**: 30 seconds
- **Duration**: 30 minutes
- **Use Case**: Quick ISP performance check

### Long-term Monitoring
- **Server**: Most reliable option for your location
- **Interval**: 5 minutes
- **Duration**: 24 hours
- **Use Case**: ISP performance monitoring over time

### Continuous Monitoring
- **Server**: Local server for best results
- **Interval**: 10 minutes
- **Duration**: Continuous
- **Use Case**: Ongoing network performance tracking

## Troubleshooting

### "iperf3 command not found"
Install iperf3 using the installation instructions above for your platform.

### "Test timed out"
- Try a different server from the list
- Check your internet connection
- Some servers may be temporarily busy (try again later)

### "Server is busy"
IPERF3 servers only allow one connection at a time:
- Wait a few seconds and the script will retry automatically
- Choose a different server from the list
- Use a custom server with multiple ports

### Inconsistent Results
- Try multiple UK servers to find the most stable option
- London servers provide best results for UK users
- Consider testing at different times of day

## Advanced Usage

### Custom Server Configuration
When selecting "Enter custom server":
1. Enter server hostname or IP address
2. Specify port (default 5201)
3. Ensure the server supports IPERF3 protocol

### Automated Runs
For automated/scheduled runs, you can modify the script to skip interactive prompts by hardcoding your preferred settings in the `main()` function.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Lee Robinson**
- GitHub: [@Lee-Robinson](https://github.com/Lee-Robinson)

## Acknowledgments

- Built using the excellent [iperf3](https://iperf.fr/) network testing tool
- Public server list curated from [iperf3serverlist.net](https://iperf3serverlist.net/)
- UK server selection optimised for Birmingham and Midlands users
- Inspired by professional network monitoring tools

---

⭐ **Star this repository if you find it useful!**
