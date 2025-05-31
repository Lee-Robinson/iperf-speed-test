#!/usr/bin/env python3
"""
IPERF Speed Test Monitor (iperf_test.py)
A Python script to perform periodic IPERF speed tests and log results.
"""

import subprocess
import json
import time
import datetime
import sys
import signal
import os
from pathlib import Path

class IperfSpeedTester:
    def __init__(self, server="speedtest.serverius.net", port=5201, interval=300, duration=None):
        """
        Initialize the IPERF speed tester.
        
        Args:
            server (str): IPERF server to test against
            port (int): Server port (default 5201)
            interval (int): Time between tests in seconds (default 5 minutes)
            duration (int): Total test duration in seconds (None for continuous)
        """
        self.server = server
        self.port = port
        self.interval = interval
        self.duration = duration
        self.start_time = None
        
        # Create desktop folder for results
        self.setup_results_folder()
        
        self.running = True
        self.test_results = []
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def setup_results_folder(self):
        """Create a results folder on the desktop"""
        # Get desktop path (works on macOS, Linux, Windows)
        if sys.platform == "darwin":  # macOS
            desktop_path = os.path.expanduser("~/Desktop")
        elif sys.platform == "win32":  # Windows
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        else:  # Linux
            desktop_path = os.path.expanduser("~/Desktop")
            
        # Create timestamped folder
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.results_folder = os.path.join(desktop_path, f"IPERF_Results_{timestamp}")
        
        try:
            os.makedirs(self.results_folder, exist_ok=True)
            self.log_file = os.path.join(self.results_folder, "iperf_speed_test.log")
            self.report_file = os.path.join(self.results_folder, "iperf_speed_report.html")
        except Exception as e:
            # Fallback to current directory if desktop not accessible
            print(f"⚠️  Could not create desktop folder: {e}")
            print("📁 Using current directory instead...")
            self.results_folder = os.getcwd()
            self.log_file = "iperf_speed_test.log"
            self.report_file = "iperf_speed_report.html"
    
    def show_progress_bar(self, current, total, description="Progress"):
        """Show a progress bar"""
        bar_length = 40
        progress = current / total
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        percent = progress * 100
        print(f"\r{description}: [{bar}] {percent:.1f}%", end='', flush=True)
        
    def format_duration(self, seconds):
        """Format duration in seconds to human readable format"""
        if seconds is None:
            return "Continuous"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        else:
            return f"{minutes}m"
    
    def get_remaining_time(self):
        """Get remaining test time"""
        if self.duration is None or self.start_time is None:
            return None
            
        elapsed = time.time() - self.start_time
        remaining = self.duration - elapsed
        return max(0, remaining)
    
    def should_continue_testing(self):
        """Check if testing should continue based on duration"""
        if self.duration is None:
            return True  # Run continuously
            
        if self.start_time is None:
            return True  # First run
            
        elapsed = time.time() - self.start_time
        return elapsed < self.duration
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping speed tests...")
        self.running = False
        
    def check_iperf3_installed(self):
        """Check if iperf3 is installed on the system"""
        try:
            subprocess.run(["iperf3", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def install_iperf3_instructions(self):
        """Print installation instructions for iperf3"""
        print("📦 iperf3 is not installed. Please install it first:")
        print("\n🍎 macOS:")
        print("   brew install iperf3")
        print("\n🐧 Ubuntu/Debian:")
        print("   sudo apt update && sudo apt install iperf3")
        print("\n🎩 Red Hat/CentOS/Fedora:")
        print("   sudo yum install iperf3  # or dnf install iperf3")
        print("\n🪟 Windows:")
        print("   Download from: https://iperf.fr/iperf-download.php")
        
    def run_speed_test(self):
        """Run a single IPERF speed test"""
        try:
            # Run iperf3 client test
            cmd = [
                "iperf3",
                "-c", self.server,
                "-p", str(self.port),
                "-J",  # JSON output
                "-t", "10"  # 10 second test
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse JSON output
                data = json.loads(result.stdout)
                return self.parse_iperf_result(data)
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip(),
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test timed out after 30 seconds",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON output: {e}",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
    def parse_iperf_result(self, data):
        """Parse IPERF JSON result into our format"""
        try:
            end_data = data.get("end", {})
            sum_sent = end_data.get("sum_sent", {})
            sum_received = end_data.get("sum_received", {})
            
            # Convert bits per second to Mbps
            upload_bps = sum_sent.get("bits_per_second", 0)
            download_bps = sum_received.get("bits_per_second", 0)
            
            upload_mbps = upload_bps / 1_000_000 if upload_bps else 0
            download_mbps = download_bps / 1_000_000 if download_bps else 0
            
            return {
                "success": True,
                "timestamp": datetime.datetime.now().isoformat(),
                "server": self.server,
                "upload_mbps": round(upload_mbps, 2),
                "download_mbps": round(download_mbps, 2),
                "upload_bytes": sum_sent.get("bytes", 0),
                "download_bytes": sum_received.get("bytes", 0),
                "duration": end_data.get("sum_sent", {}).get("seconds", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse result: {e}",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
    def log_result(self, result):
        """Log result to file"""
        timestamp = result["timestamp"]
        
        if result["success"]:
            log_entry = (
                f"{timestamp} | SUCCESS | "
                f"↑{result['upload_mbps']:6.2f} Mbps | "
                f"↓{result['download_mbps']:6.2f} Mbps | "
                f"Server: {result['server']}\n"
            )
        else:
            log_entry = f"{timestamp} | FAILED | Error: {result['error']}\n"
            
        with open(self.log_file, "a") as f:
            f.write(log_entry)
            
    def print_result(self, result):
        """Print result to console"""
        timestamp = datetime.datetime.fromisoformat(result["timestamp"]).strftime("%H:%M:%S")
        
        if result["success"]:
            print(f"⚡ {timestamp} | "
                  f"Upload: {result['upload_mbps']:6.2f} Mbps | "
                  f"Download: {result['download_mbps']:6.2f} Mbps")
        else:
            print(f"❌ {timestamp} | Test failed: {result['error']}")
            
    def generate_html_report(self):
        """Generate HTML report from test results"""
        if not self.test_results:
            return
            
        print(f"\n📊 Generating HTML report...")
        
        # Show progress for report generation
        for i in range(0, 101, 10):
            self.show_progress_bar(i, 100, "Creating report")
            time.sleep(0.1)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        if successful_tests:
            avg_upload = sum(r["upload_mbps"] for r in successful_tests) / len(successful_tests)
            avg_download = sum(r["download_mbps"] for r in successful_tests) / len(successful_tests)
            max_upload = max(r["upload_mbps"] for r in successful_tests)
            max_download = max(r["download_mbps"] for r in successful_tests)
            min_upload = min(r["upload_mbps"] for r in successful_tests)
            min_download = min(r["download_mbps"] for r in successful_tests)
        else:
            avg_upload = avg_download = max_upload = max_download = min_upload = min_download = 0
            
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>IPERF Speed Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 5px; }}
        .author {{ text-align: center; margin: 10px 0; font-size: 14px; color: #666; }}
        .author a {{ color: #2196F3; text-decoration: none; }}
        .author a:hover {{ text-decoration: underline; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #f5f5f5; padding: 15px; border-radius: 5px; flex: 1; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .results {{ margin-top: 20px; }}
        .success {{ color: #4CAF50; }}
        .failure {{ color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 IPERF Speed Test Report</h1>
        <p>Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Server: {self.server}:{self.port}</p>
    </div>
    
    <div class="author">
        <p>Written by Lee Robinson to test ISP speeds | <a href="https://github.com/Lee-Robinson" target="_blank">GitHub: https://github.com/Lee-Robinson</a></p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-value">{len(self.test_results)}</div>
            <div>Total Tests</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{len(successful_tests)}</div>
            <div>Successful</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{len(failed_tests)}</div>
            <div>Failed</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{avg_download:.1f}</div>
            <div>Avg Download (Mbps)</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{avg_upload:.1f}</div>
            <div>Avg Upload (Mbps)</div>
        </div>
    </div>
    
    <h2>Speed Statistics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Download (Mbps)</th>
            <th>Upload (Mbps)</th>
        </tr>
        <tr>
            <td>Average</td>
            <td>{avg_download:.2f}</td>
            <td>{avg_upload:.2f}</td>
        </tr>
        <tr>
            <td>Maximum</td>
            <td>{max_download:.2f}</td>
            <td>{max_upload:.2f}</td>
        </tr>
        <tr>
            <td>Minimum</td>
            <td>{min_download:.2f}</td>
            <td>{min_upload:.2f}</td>
        </tr>
    </table>
    
    <h2>Recent Test Results</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Status</th>
            <th>Download (Mbps)</th>
            <th>Upload (Mbps)</th>
            <th>Details</th>
        </tr>
"""
        
        # Add last 50 results
        for result in self.test_results[-50:]:
            timestamp = datetime.datetime.fromisoformat(result["timestamp"]).strftime("%H:%M:%S")
            if result["success"]:
                html_content += f"""
        <tr class="success">
            <td>{timestamp}</td>
            <td>✅ Success</td>
            <td>{result['download_mbps']:.2f}</td>
            <td>{result['upload_mbps']:.2f}</td>
            <td>Duration: {result.get('duration', 'N/A')}s</td>
        </tr>"""
            else:
                html_content += f"""
        <tr class="failure">
            <td>{timestamp}</td>
            <td>❌ Failed</td>
            <td>-</td>
            <td>-</td>
            <td>{result['error']}</td>
        </tr>"""
                
        html_content += """
    </table>
</body>
</html>"""
        
        with open(self.report_file, "w") as f:
            f.write(html_content)
        
        print("\n✅ Report generation complete!")
            
    def run(self):
        """Main run loop"""
        print("🚀 IPERF Speed Test Monitor")
        print("=" * 50)
        print("Written by Lee Robinson to test ISP speeds")
        print("GitHub: https://github.com/Lee-Robinson")
        print("=" * 50)
        
        # Check if iperf3 is installed
        if not self.check_iperf3_installed():
            self.install_iperf3_instructions()
            return
            
        print(f"📊 Testing against: {self.server}:{self.port}")
        print(f"⏱️  Test interval: {self.interval} seconds")
        print(f"⏰ Test duration: {self.format_duration(self.duration)}")
        print(f"📁 Results folder: {self.results_folder}")
        print(f"📝 Logging to: {os.path.basename(self.log_file)}")
        print(f"📄 Report will be saved to: {os.path.basename(self.report_file)}")
        print("\nPress Ctrl+C to stop\n")
        
        # Set start time
        self.start_time = time.time()
        
        while self.running and self.should_continue_testing():
            try:
                # Show remaining time if duration is set
                remaining = self.get_remaining_time()
                if remaining is not None:
                    remaining_formatted = self.format_duration(int(remaining))
                    print(f"🔄 Running speed test... (Time remaining: {remaining_formatted})", end=" ", flush=True)
                else:
                    print("🔄 Running speed test...", end=" ", flush=True)
                    
                result = self.run_speed_test()
                
                self.test_results.append(result)
                self.log_result(result)
                self.print_result(result)
                
                # Generate report every 10 tests or on failure
                if len(self.test_results) % 10 == 0 or not result["success"]:
                    self.generate_html_report()
                
                # Check if we should continue and sleep
                if self.running and self.should_continue_testing():
                    time.sleep(self.interval)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(10)  # Wait before retrying
        
        # Check if we finished due to time limit
        if not self.should_continue_testing() and self.running:
            print(f"\n⏰ Test duration completed! Ran for {self.format_duration(self.duration)}")
                
        # Generate final report
        self.generate_html_report()
        
        # Show final file locations
        print(f"\n📁 All results saved to:")
        print(f"   Folder: {self.results_folder}")
        print(f"   Log:    {self.log_file}")
        print(f"   Report: {self.report_file}")
        print(f"\n💡 To open the folder: open '{self.results_folder}'")
        print(f"💡 To view the report: open '{self.report_file}'")
        print("👋 Speed testing stopped.")

def get_user_server_choice():
    """Get server choice from user"""
    print("🌐 IPERF Server Selection")
    print("=" * 40)
    print("🇬🇧 UK Servers (Recommended for UK users):")
    print("1. iperf.as42831.net (London) - UK Servers, Reliable")
    print("2. speedtest.lon1.uk.leaseweb.net (London) - LeaseWeb")
    print("3. speedtest.lon12.uk.leaseweb.net (London) - LeaseWeb Alt")
    print("4. lon.speedtest.clouvider.net (London) - Clouvider")
    print("5. 185.59.221.51 (London) - DATAPACKET")
    print()
    print("🌍 International Servers:")
    print("6. ams.speedtest.clouvider.net (Amsterdam) - Very Reliable")
    print("7. speedtest.wtnet.de (Germany) - High Speed")
    print("8. speedtest.init7.net (Switzerland) - Stable")
    print("9. nyc.speedtest.clouvider.net (New York) - US")
    print("10. Enter custom server")
    print()
    
    while True:
        choice = input("Choose option (1-10): ").strip()
        
        if choice == "1":
            return "iperf.as42831.net", 5300
        elif choice == "2":
            return "speedtest.lon1.uk.leaseweb.net", 5201
        elif choice == "3":
            return "speedtest.lon12.uk.leaseweb.net", 5201
        elif choice == "4":
            return "lon.speedtest.clouvider.net", 5200
        elif choice == "5":
            return "185.59.221.51", 5201
        elif choice == "6":
            return "ams.speedtest.clouvider.net", 5200
        elif choice == "7":
            return "speedtest.wtnet.de", 5200
        elif choice == "8":
            return "speedtest.init7.net", 5201
        elif choice == "9":
            return "nyc.speedtest.clouvider.net", 5200
        elif choice == "10":
            while True:
                server = input("Enter IPERF server address: ").strip()
                if server:
                    break
                print("❌ Server address cannot be empty")
            
            while True:
                try:
                    port_input = input("Enter port (default 5201): ").strip()
                    port = int(port_input) if port_input else 5201
                    if 1 <= port <= 65535:
                        break
                    else:
                        print("❌ Port must be between 1 and 65535")
                except ValueError:
                    print("❌ Please enter a valid port number")
            
            return server, port
        else:
            print("❌ Please enter 1-10")

def get_test_interval():
    """Get test interval from user"""
    print("\n⏱️  Test Interval Selection")
    print("=" * 25)
    print("1. Every 30 seconds (for short duration tests)")
    print("2. Every 1 minute")
    print("3. Every 5 minutes (recommended)")
    print("4. Every 10 minutes")
    print("5. Every 30 minutes")
    print("6. Custom interval")
    print()
    
    while True:
        choice = input("Choose option (1-6): ").strip()
        
        if choice == "1":
            return 30
        elif choice == "2":
            return 60
        elif choice == "3":
            return 300
        elif choice == "4":
            return 600
        elif choice == "5":
            return 1800
        elif choice == "6":
            while True:
                try:
                    minutes = float(input("Enter interval in minutes: ").strip())
                    if minutes > 0:
                        return int(minutes * 60)
                    else:
                        print("❌ Interval must be greater than 0")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            print("❌ Please enter 1-6")

def get_test_duration():
    """Get test duration from user"""
    print("\n⏰ Test Duration Selection")
    print("=" * 25)
    print("1. Run for 1 hour")
    print("2. Run for 2 hours")
    print("3. Run for 4 hours")
    print("4. Run for 8 hours")
    print("5. Run for 24 hours")
    print("6. Run continuously (until stopped manually)")
    print("7. Custom duration")
    print()
    
    while True:
        choice = input("Choose option (1-7): ").strip()
        
        if choice == "1":
            return 3600  # 1 hour in seconds
        elif choice == "2":
            return 7200  # 2 hours
        elif choice == "3":
            return 14400  # 4 hours
        elif choice == "4":
            return 28800  # 8 hours
        elif choice == "5":
            return 86400  # 24 hours
        elif choice == "6":
            return None  # Run continuously
        elif choice == "7":
            while True:
                try:
                    hours = float(input("Enter duration in hours (0.1 to 24): ").strip())
                    if 0.1 <= hours <= 24:
                        return int(hours * 3600)  # Convert to seconds
                    else:
                        print("❌ Duration must be between 0.1 and 24 hours")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            print("❌ Please enter 1-7")

def main():
    """Main function"""
    print("🚀 IPERF Speed Test Monitor")
    print("=" * 50)
    print("Written by Lee Robinson to test ISP speeds")
    print("GitHub: https://github.com/Lee-Robinson")
    print("=" * 50)
    print()
    
    # Get server choice from user
    server, port = get_user_server_choice()
    
    # Get test interval from user
    interval = get_test_interval()
    
    # Get test duration from user
    duration = get_test_duration()
    
    print(f"\n✅ Configuration:")
    print(f"   Server: {server}:{port}")
    print(f"   Interval: {interval//60} minute(s)")
    if duration:
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        if hours > 0:
            duration_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        else:
            duration_str = f"{minutes}m"
        print(f"   Duration: {duration_str}")
    else:
        print(f"   Duration: Continuous (until stopped)")
    print()
    
    # Confirm before starting
    confirm = input("Start testing? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Cancelled.")
        return
    
    print()
    
    # Create and run the speed tester
    tester = IperfSpeedTester(server=server, port=port, interval=interval, duration=duration)
    tester.run()

if __name__ == "__main__":
    main()
