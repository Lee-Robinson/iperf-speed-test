# IPERF Speed Test Monitor
![Screenshot 2025-05-31 at 08 32 27](https://github.com/user-attachments/assets/564f3695-f6a4-497d-b898-83b6c43fe88f)

🚀 A Python script to perform automated IPERF speed tests and generate comprehensive reports for ISP speed monitoring.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🌐 **Multiple Public Servers**: Choose from reliable IPERF3 servers worldwide
- ⏱️ **Automated Testing**: Run tests at custom intervals (1 min to hours)
- 📊 **HTML Reports**: Beautiful, responsive reports with statistics
- 📝 **Detailed Logging**: Track all test results with timestamps
- 🎯 **Cross-Platform**: Works on Windows, macOS, and Linux
- ⚡ **Real-time Display**: See results as tests complete
- 🛡️ **Error Handling**: Graceful handling of network issues and timeouts

## Screenshots

### Terminal Output
```
🚀 IPERF Speed Test Monitor
==================================================
Written by Lee Robinson to test ISP speeds
GitHub: https://github.com/Lee-Robinson
==================================================

🌐 IPERF Server Selection
==============================
1. ams.speedtest.clouvider.net (Amsterdam) - Reliable
2. speedtest.wtnet.de (Germany) - High speed
3. speedtest.init7.net (Switzerland) - Stable
...

⚡ 14:23:15 | Upload:  25.43 Mbps | Download:  89.21 Mbps
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

### Download and Run
#### Quick Start (One Command)
```bash
# Download and run immediately
curl -O https://raw.githubusercontent.com/Lee-Robinson/iperf-speed-test/main/iperf_test.py && python3 iperf_test.py
```

#### Alternative Methods
**Option 1: Manual Download**
1. Download `iperf_test.py`
2. Make it executable (Linux/macOS): `chmod +x iperf_test.py`
3. Run: `python3 iperf_test.py`

**Option 2: Git Clone**
```bash
git clone https://github.com/Lee-Robinson/iperf-speed-test.git
cd iperf-speed-test
python3 iperf_test.py
```

**Option 3: wget (Linux/macOS)**
```bash
wget https://raw.githubusercontent.com/Lee-Robinson/iperf-speed-test/main/iperf_test.py
python3 iperf_test.py
```

## Usage

1. **Run the script:**
   ```bash
   python3 iperf_test.py
   ```

2. **Choose a server:**
   - Select from 5 reliable public servers worldwide
   - Or enter your own custom server

3. **Set test interval:**
   - 1 minute, 5 minutes, 10 minutes, or custom

4. **Monitor results:**
   - Real-time terminal output
   - Automatic logging to `iperf_speed_test.log`
   - HTML report generation at `iperf_speed_report.html`

5. **Stop testing:**
   - Press `Ctrl+C` to stop gracefully

## Output Files

- **`iperf_speed_test.log`**: Detailed text log of all tests
- **`iperf_speed_report.html`**: Interactive HTML report with statistics and graphs

## Server Options

The script includes several reliable public IPERF3 servers:

| Location | Server | Speed | Description |
|----------|--------|-------|-------------|
| Amsterdam | ams.speedtest.clouvider.net | 10 Gbps | Very reliable |
| Germany | speedtest.wtnet.de | 40 Gbps | High speed |
| Switzerland | speedtest.init7.net | 20 Gbps | Very stable |
| London | lon.speedtest.clouvider.net | 10 Gbps | UK users |
| New York | nyc.speedtest.clouvider.net | 10 Gbps | US East Coast |

## Configuration

You can customize the script by modifying:
- Test duration (default: 10 seconds per test)
- Timeout settings (default: 30 seconds)
- Report generation frequency
- Log file names and locations

## Troubleshooting

### "iperf3 command not found"
Install iperf3 using the installation instructions above.

### "Test timed out"
- Try a different server from the list
- Check your internet connection
- Some servers may be temporarily busy

### "Server is busy"
IPERF3 servers only allow one connection at a time. Try:
- Waiting a few seconds and trying again
- Choosing a different server
- Using a custom server with multiple ports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Lee Robinson**
- GitHub: [@Lee-Robinson](https://github.com/Lee-Robinson)

## Acknowledgments

- Built using the excellent [iperf3](https://iperf.fr/) network testing tool
- Public server list from [iperf3serverlist.net](https://iperf3serverlist.net/)
- Inspired by the need for reliable ISP speed monitoring

---

⭐ **Star this repository if you find it useful!**
