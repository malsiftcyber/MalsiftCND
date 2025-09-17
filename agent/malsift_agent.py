#!/usr/bin/env python3
"""
MalsiftCND Discovery Agent
Cross-platform network discovery agent with SSL-encrypted communication
"""
import asyncio
import aiohttp
import ssl
import json
import logging
import platform
import psutil
import subprocess
import time
import uuid
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import signal
import threading


class MalsiftAgent:
    """MalsiftCND Discovery Agent"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "agent_config.json"
        self.config = self._load_config()
        self.agent_id = self._get_or_generate_agent_id()
        self.session = None
        self.running = False
        self.heartbeat_task = None
        self.scan_task = None
        self.logger = self._setup_logging()
        
        # SSL context for secure communication
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE  # For development
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        default_config = {
            "server_url": "https://localhost:8000",
            "ssl_enabled": True,
            "heartbeat_interval": 60,
            "scan_enabled": True,
            "scan_interval_minutes": 60,
            "max_concurrent_scans": 5,
            "scan_timeout_seconds": 300,
            "target_networks": ["192.168.0.0/16", "10.0.0.0/8"],
            "excluded_networks": ["127.0.0.0/8"],
            "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389],
            "excluded_ports": [],
            "log_level": "INFO",
            "log_file": "malsift_agent.log"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")
        
        return default_config
    
    def _get_or_generate_agent_id(self) -> str:
        """Get or generate unique agent ID"""
        agent_id_file = "agent_id.txt"
        
        if os.path.exists(agent_id_file):
            try:
                with open(agent_id_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        # Generate new agent ID
        agent_id = str(uuid.uuid4())
        try:
            with open(agent_id_file, 'w') as f:
                f.write(agent_id)
        except Exception:
            pass
        
        return agent_id
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('malsift_agent')
        logger.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        
        # File handler
        file_handler = logging.FileHandler(self.config.get('log_file', 'malsift_agent.log'))
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def start(self):
        """Start the agent"""
        self.logger.info("Starting MalsiftCND Discovery Agent")
        self.logger.info(f"Agent ID: {self.agent_id}")
        self.logger.info(f"Platform: {platform.system()} {platform.machine()}")
        self.logger.info(f"Server URL: {self.config['server_url']}")
        
        self.running = True
        
        try:
            # Register agent
            await self._register_agent()
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Start scan task if enabled
            if self.config.get('scan_enabled', True):
                self.scan_task = asyncio.create_task(self._scan_loop())
            
            # Wait for tasks to complete
            await asyncio.gather(self.heartbeat_task, self.scan_task, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Agent error: {e}")
        finally:
            await self._cleanup()
    
    async def _register_agent(self):
        """Register agent with server"""
        try:
            async with aiohttp.ClientSession() as session:
                registration_data = {
                    "name": f"MalsiftAgent-{platform.node()}",
                    "description": f"MalsiftCND Discovery Agent on {platform.node()}",
                    "platform": self._get_platform(),
                    "architecture": platform.machine(),
                    "os_version": f"{platform.system()} {platform.release()}",
                    "agent_version": "1.0.0",
                    "ip_address": self._get_local_ip(),
                    "hostname": platform.node(),
                    "server_url": self.config['server_url'],
                    "ssl_enabled": self.config.get('ssl_enabled', True),
                    "target_networks": self.config.get('target_networks', []),
                    "excluded_networks": self.config.get('excluded_networks', []),
                    "target_ports": self.config.get('target_ports', []),
                    "excluded_ports": self.config.get('excluded_ports', [])
                }
                
                url = f"{self.config['server_url']}/api/v1/agents/register"
                async with session.post(url, json=registration_data, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Agent registered successfully: {result}")
                    else:
                        self.logger.error(f"Failed to register agent: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.config.get('heartbeat_interval', 60))
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(30)  # Retry in 30 seconds on error
    
    async def _send_heartbeat(self):
        """Send heartbeat to server"""
        try:
            async with aiohttp.ClientSession() as session:
                heartbeat_data = {
                    "status": "active",
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "network_usage": self._get_network_usage(),
                    "agent_version": "1.0.0",
                    "os_version": f"{platform.system()} {platform.release()}",
                    "uptime_seconds": int(time.time() - psutil.boot_time()),
                    "active_scans": 0,  # Will be updated when scans are running
                    "queued_scans": 0,
                    "error_count": 0,
                    "heartbeat_data": {
                        "python_version": platform.python_version(),
                        "process_count": len(psutil.pids()),
                        "boot_time": psutil.boot_time()
                    }
                }
                
                url = f"{self.config['server_url']}/api/v1/agents/{self.agent_id}/heartbeat"
                async with session.post(url, json=heartbeat_data, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        self.logger.debug("Heartbeat sent successfully")
                    else:
                        self.logger.error(f"Heartbeat failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
    
    async def _scan_loop(self):
        """Perform periodic network scans"""
        while self.running:
            try:
                await self._perform_network_scan()
                await asyncio.sleep(self.config.get('scan_interval_minutes', 60) * 60)
            except Exception as e:
                self.logger.error(f"Scan error: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes on error
    
    async def _perform_network_scan(self):
        """Perform network discovery scan"""
        self.logger.info("Starting network discovery scan")
        
        start_time = time.time()
        targets = self.config.get('target_networks', [])
        ports = self.config.get('target_ports', [])
        
        try:
            # Perform ping sweep first
            alive_hosts = await self._ping_sweep(targets)
            self.logger.info(f"Found {len(alive_hosts)} alive hosts")
            
            # Perform port scan on alive hosts
            scan_results = await self._port_scan(alive_hosts, ports)
            
            # Submit results
            await self._submit_scan_results(scan_results, start_time)
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            await self._submit_scan_error(str(e), start_time)
    
    async def _ping_sweep(self, targets: List[str]) -> List[str]:
        """Perform ping sweep to find alive hosts"""
        alive_hosts = []
        
        for target in targets:
            try:
                # Use nmap for ping sweep if available
                if self._is_command_available('nmap'):
                    result = await self._run_command([
                        'nmap', '-sn', target
                    ])
                    alive_hosts.extend(self._parse_nmap_ping(result))
                else:
                    # Fallback to simple ping
                    hosts = self._expand_network(target)
                    for host in hosts:
                        if await self._ping_host(host):
                            alive_hosts.append(host)
            except Exception as e:
                self.logger.error(f"Ping sweep error for {target}: {e}")
        
        return alive_hosts
    
    async def _port_scan(self, hosts: List[str], ports: List[int]) -> Dict[str, Any]:
        """Perform port scan on hosts"""
        scan_results = {
            "devices": [],
            "ports_found": 0,
            "services_found": 0
        }
        
        for host in hosts:
            try:
                if self._is_command_available('nmap'):
                    # Use nmap for detailed scanning
                    port_list = ','.join(map(str, ports))
                    result = await self._run_command([
                        'nmap', '-sV', '-p', port_list, host
                    ])
                    device_info = self._parse_nmap_result(result, host)
                else:
                    # Fallback to simple port check
                    device_info = await self._simple_port_check(host, ports)
                
                if device_info:
                    scan_results["devices"].append(device_info)
                    scan_results["ports_found"] += len(device_info.get('open_ports', []))
                    scan_results["services_found"] += len(device_info.get('services', []))
                    
            except Exception as e:
                self.logger.error(f"Port scan error for {host}: {e}")
        
        return scan_results
    
    async def _run_command(self, command: List[str]) -> str:
        """Run system command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Command failed: {stderr.decode()}")
        
        return stdout.decode()
    
    def _is_command_available(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def _ping_host(self, host: str) -> bool:
        """Ping a single host"""
        try:
            if platform.system().lower() == 'windows':
                command = ['ping', '-n', '1', '-w', '1000', host]
            else:
                command = ['ping', '-c', '1', '-W', '1', host]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return process.returncode == 0
            
        except Exception:
            return False
    
    def _expand_network(self, network: str) -> List[str]:
        """Expand network CIDR to list of IPs (simplified)"""
        # This is a simplified implementation
        # In production, use ipaddress module for proper CIDR expansion
        if '/' in network:
            base_ip = network.split('/')[0]
            if base_ip.startswith('192.168.'):
                return [f"192.168.{i}.{j}" for i in range(1, 255) for j in range(1, 255)]
            elif base_ip.startswith('10.'):
                return [f"10.{i}.{j}.{k}" for i in range(1, 255) for j in range(1, 255) for k in range(1, 255)]
        else:
            return [network]
    
    def _parse_nmap_ping(self, output: str) -> List[str]:
        """Parse nmap ping sweep output"""
        hosts = []
        for line in output.split('\n'):
            if 'Nmap scan report for' in line:
                # Extract IP address
                parts = line.split()
                if len(parts) >= 5:
                    ip = parts[4]
                    hosts.append(ip)
        return hosts
    
    def _parse_nmap_result(self, output: str, host: str) -> Dict[str, Any]:
        """Parse nmap scan result"""
        device_info = {
            "ip": host,
            "hostname": None,
            "open_ports": [],
            "services": [],
            "os_info": None
        }
        
        lines = output.split('\n')
        for line in lines:
            if 'Nmap scan report for' in line:
                parts = line.split()
                if len(parts) >= 5:
                    device_info["hostname"] = parts[4]
            elif '/tcp' in line and 'open' in line:
                # Parse open port
                parts = line.split()
                if len(parts) >= 3:
                    port_info = parts[0].split('/')
                    if len(port_info) == 2:
                        port = int(port_info[0])
                        protocol = port_info[1]
                        service = parts[2] if len(parts) > 2 else 'unknown'
                        
                        device_info["open_ports"].append({
                            "port": port,
                            "protocol": protocol,
                            "state": "open"
                        })
                        
                        device_info["services"].append({
                            "port": port,
                            "protocol": protocol,
                            "service": service
                        })
        
        return device_info if device_info["open_ports"] else None
    
    async def _simple_port_check(self, host: str, ports: List[int]) -> Dict[str, Any]:
        """Simple port check without nmap"""
        device_info = {
            "ip": host,
            "hostname": None,
            "open_ports": [],
            "services": []
        }
        
        for port in ports:
            try:
                # Simple socket connection test
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    device_info["open_ports"].append({
                        "port": port,
                        "protocol": "tcp",
                        "state": "open"
                    })
                    
            except Exception:
                continue
        
        return device_info if device_info["open_ports"] else None
    
    async def _submit_scan_results(self, results: Dict[str, Any], start_time: float):
        """Submit scan results to server"""
        try:
            async with aiohttp.ClientSession() as session:
                scan_data = {
                    "scan_type": "network_discovery",
                    "targets": self.config.get('target_networks', []),
                    "ports": self.config.get('target_ports', []),
                    "scanner": "nmap" if self._is_command_available('nmap') else "custom",
                    "status": "completed",
                    "started_at": datetime.fromtimestamp(start_time).isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration_seconds": time.time() - start_time,
                    "devices_found": len(results["devices"]),
                    "ports_found": results["ports_found"],
                    "services_found": results["services_found"],
                    "scan_results": results
                }
                
                url = f"{self.config['server_url']}/api/v1/agents/{self.agent_id}/scan-results"
                async with session.post(url, json=scan_data, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Scan results submitted: {result}")
                    else:
                        self.logger.error(f"Failed to submit scan results: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Submit scan results error: {e}")
    
    async def _submit_scan_error(self, error_message: str, start_time: float):
        """Submit scan error to server"""
        try:
            async with aiohttp.ClientSession() as session:
                scan_data = {
                    "scan_type": "network_discovery",
                    "targets": self.config.get('target_networks', []),
                    "ports": self.config.get('target_ports', []),
                    "scanner": "nmap" if self._is_command_available('nmap') else "custom",
                    "status": "failed",
                    "started_at": datetime.fromtimestamp(start_time).isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration_seconds": time.time() - start_time,
                    "devices_found": 0,
                    "ports_found": 0,
                    "services_found": 0,
                    "error_message": error_message
                }
                
                url = f"{self.config['server_url']}/api/v1/agents/{self.agent_id}/scan-results"
                async with session.post(url, json=scan_data, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        self.logger.info("Scan error submitted")
                    else:
                        self.logger.error(f"Failed to submit scan error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Submit scan error failed: {e}")
    
    def _get_platform(self) -> str:
        """Get platform identifier"""
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'unknown'
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _get_network_usage(self) -> float:
        """Get network usage in bytes per second"""
        try:
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent + net_io.bytes_recv
        except Exception:
            return 0.0
    
    async def _cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up agent resources")
        
        if self.session:
            await self.session.close()
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        if self.scan_task:
            self.scan_task.cancel()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MalsiftCND Discovery Agent')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--version', '-v', action='version', version='MalsiftCND Agent 1.0.0')
    
    args = parser.parse_args()
    
    agent = MalsiftAgent(args.config)
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Agent error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
