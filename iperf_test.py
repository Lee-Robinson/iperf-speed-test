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
        
        # Save files directly in the current directory (no subfolder creation)
        self.log_file = "iperf_speed_test.log"
        self.report_file = "iperf_speed_report.html"
        
        self.running = True
        self.test_results = []
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping speed tests...")
        self.running = False
        
    def should_continue_testing(self):
        """Check if testing should continue based on duration"""
        if self.duration is None:
            return True
            
        if self.start_time is None:
            return True
            
        elapsed = time.time() - self.start_time
        return elapsed < self.duration
        
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
        
    def check_iperf3_installed(self):
        """Check if iperf3 is installed on the system"""
        try:
            subprocess.run(["iperf3", "--version"], capture_output=True, check=True)
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
            cmd = [
                "iperf3",
                "-c", self.server,
                "-p", str(self.port),
                "-J",
                "-t", "10"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
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
        
        # Configuration summary
        print("✅ CONFIGURATION SUMMARY")
        print("=" * 50)
        print(f"📊 Server: {self.server} ({self.port})")
        print(f"⏰ Duration: {self.format_duration(self.duration)}")
        
        # Format interval properly
        interval_minutes = self.interval // 60
        interval_seconds = self.interval % 60
        if interval_minutes > 0:
            if interval_seconds > 0:
                interval_display = f"{interval_minutes} minute(s) {interval_seconds} second(s)"
            else:
                interval_display = f"{interval_minutes} minute(s)"
        else:
            interval_display = f"{interval_seconds} second(s)"
        print(f"⏱️  Interval: {interval_display} (continuous monitoring)")
        
        print(f"📝 Log file: {os.path.basename(self.log_file)}")
        print(f"📄 Report file: {os.path.basename(self.report_file)}")
        print("=" * 50)
        print()
        
        confirm = input("Proceed with this configuration? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("👋 Cancelled.")
            return
        
        print("\nPress Ctrl+C to stop\n")
        
        # Set start time
        self.start_time = time.time()
        
        while self.running and self.should_continue_testing():
            try:
                # Progress bar for timed tests
                if self.duration:
                    elapsed = time.time() - self.start_time
                    progress = min(elapsed / self.duration, 1.0)
                    filled = int(progress * 20)
                    bar = "█" * filled + "░" * (20 - filled)
                    percent = int(progress * 100)
                    print(f"🔄 [{bar}] {percent}%")
                
                result = self.run_speed_test()
                
                self.test_results.append(result)
                self.log_result(result)
                self.print_result(result)
                
                # Status display
                successful_tests = [r for r in self.test_results if r["success"]]
                failed_tests = [r for r in self.test_results if not r["success"]]
                success_rate = (len(successful_tests) / len(self.test_results)) * 100 if self.test_results else 0
                
                elapsed = time.time() - self.start_time
                elapsed_min = int(elapsed // 60)
                elapsed_sec = int(elapsed % 60)
                
                # Calculate remaining time
                if self.duration:
                    remaining = max(0, self.duration - elapsed)
                    remaining_min = int(remaining // 60)
                    if remaining_min > 60:
                        remaining_hours = remaining_min // 60
                        remaining_min = remaining_min % 60
                        remaining_str = f"{remaining_hours}h {remaining_min}m"
                    else:
                        remaining_str = f"{remaining_min}m"
                    
                    print(f"📊 Status: {len(self.test_results)} tests, {len(failed_tests)} failures ({success_rate:.1f}% success)")
                    print(f"⏱️  Elapsed: {elapsed_min}:{elapsed_sec:02d} | Remaining: {remaining_str}")
                else:
                    print(f"📊 Status: {len(self.test_results)} tests, {len(failed_tests)} failures ({success_rate:.1f}% success)")
                    print(f"⏱️  Elapsed: {elapsed_min}:{elapsed_sec:02d} | Remaining: ∞")
                
                print("-" * 50)
                
                # Generate report every 10 tests
                if len(self.test_results) % 10 == 0 or not result["success"]:
                    self.generate_html_report()
                    
                if self.running and self.should_continue_testing():
                    time.sleep(self.interval)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(10)
        
        # Generate final report
        self.generate_html_report()
        
        # Show final results
        print(f"\n" + "=" * 50)
        print("📁 FILES GENERATED:")
        print(f"📝 Log file: {os.path.abspath(self.log_file)}")
        print(f"📄 HTML report: {os.path.abspath(self.report_file)}")
        print("=" * 50)
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
    print("1. Run for 30 minutes")
    print("2. Run for 1 hour")
    print("3. Run for 2 hours")
    print("4. Run for 4 hours")
    print("5. Run for 8 hours")
    print("6. Run for 24 hours")
    print("7. Run continuously (until stopped manually)")
    print("8. Custom duration")
    print()
    
    while True:
        choice = input("Choose option (1-8): ").strip()
        
        if choice == "1":
            return 1800
        elif choice == "2":
            return 3600
        elif choice == "3":
            return 7200
        elif choice == "4":
            return 14400
        elif choice == "5":
            return 28800
        elif choice == "6":
            return 86400
        elif choice == "7":
            return None
        elif choice == "8":
            while True:
                try:
                    hours = float(input("Enter duration in hours (0.1 to 24): ").strip())
                    if 0.1 <= hours <= 24:
                        return int(hours * 3600)
                    else:
                        print("❌ Duration must be between 0.1 and 24 hours")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            print("❌ Please enter 1-8")

def main():
    """Main function"""
    print("🚀 IPERF Speed Test Monitor")
    print("=" * 50)
    print("Written by Lee Robinson to test ISP speeds")
    print("GitHub: https://github.com/Lee-Robinson")
    print("=" * 50)
    print()
    
    # Get user choices
    server, port = get_user_server_choice()
    interval = get_test_interval()
    duration = get_test_duration()
    
    # Create and run the speed tester
    tester = IperfSpeedTester(server=server, port=port, interval=interval, duration=duration)
    tester.run()

if __name__ == "__main__":
    main()
