import socketio
import os
import platform
import uuid
import json
import hashlib
from datetime import datetime
import argparse
import sys
import psutil
import socket

class CIFAgent:
    def __init__(self, server_url):
        self.server_url = server_url
        self.agent_id = self.get_or_create_agent_id()
        self.hostname = platform.node()
        self.platform = platform.system()
        self.computer_name = self.get_computer_name()
        self.domain_name = self.get_domain_name()
        self.ip_addresses = self.get_ip_addresses()
        self.sio = socketio.Client()
        self.setup_handlers()
    
    def get_computer_name(self):
        """Get computer name"""
        try:
            if platform.system() == 'Windows':
                import win32api
                return win32api.GetComputerName()
            else:
                return platform.node()
        except:
            return platform.node()
    
    def get_domain_name(self):
        """Get domain name"""
        try:
            if platform.system() == 'Windows':
                import win32api
                try:
                    domain = win32api.GetDomainName()
                    if domain:
                        return domain
                except:
                    pass
                
                # Try alternative method
                try:
                    import win32net
                    domain_info = win32net.NetGetAnyDCName(None, None)
                    if domain_info:
                        return domain_info.replace('\\\\', '').split('.')[0] if '.' in domain_info else domain_info.replace('\\\\', '')
                except:
                    pass
                
                # Try environment variable
                domain = os.getenv('USERDOMAIN')
                if domain:
                    return domain
                
                # Try getting from fully qualified domain name
                hostname = socket.getfqdn()
                if '.' in hostname:
                    parts = hostname.split('.')
                    if len(parts) > 1:
                        return '.'.join(parts[1:])
            
            # For Linux/Mac, try to get from hostname
            hostname = socket.getfqdn()
            if '.' in hostname:
                parts = hostname.split('.')
                if len(parts) > 1:
                    return '.'.join(parts[1:])
            
            return None
        except Exception as e:
            print(f'Warning: Could not determine domain name: {e}')
            return None
    
    def get_ip_addresses(self):
        """Get all IP addresses of the machine"""
        ip_addresses = []
        try:
            # Get hostname
            hostname = socket.gethostname()
            
            # Get primary IP
            try:
                primary_ip = socket.gethostbyname(hostname)
                if primary_ip and primary_ip not in ip_addresses:
                    ip_addresses.append(primary_ip)
            except:
                pass
            
            # Get all network interfaces
            try:
                import psutil
                net_if_addrs = psutil.net_if_addrs()
                for interface_name, interface_addresses in net_if_addrs.items():
                    for addr in interface_addresses:
                        if addr.family == socket.AF_INET:  # IPv4
                            ip = addr.address
                            if ip and ip not in ip_addresses and not ip.startswith('127.'):
                                ip_addresses.append(ip)
                        elif addr.family == socket.AF_INET6:  # IPv6
                            ip = addr.address.split('%')[0]  # Remove scope ID
                            if ip and ip not in ip_addresses and not ip.startswith('::1'):
                                ip_addresses.append(ip)
            except Exception as e:
                print(f'Warning: Could not enumerate all IP addresses: {e}')
            
            # Fallback: try connecting to external server to determine public IP
            if not ip_addresses:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    if local_ip:
                        ip_addresses.append(local_ip)
                except:
                    pass
            
            return ip_addresses if ip_addresses else ['Unknown']
        except Exception as e:
            print(f'Warning: Could not determine IP addresses: {e}')
            return ['Unknown']
        
    def get_or_create_agent_id(self):
        """Get or create a unique agent ID"""
        # On Windows, use AppData folder if available
        if platform.system() == 'Windows':
            agent_id_file = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'cif_agent_id')
        else:
            agent_id_file = os.path.expanduser('~/.cif_agent_id')
        
        if os.path.exists(agent_id_file):
            try:
                with open(agent_id_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        agent_id = str(uuid.uuid4())
        try:
            os.makedirs(os.path.dirname(agent_id_file), exist_ok=True)
            with open(agent_id_file, 'w') as f:
                f.write(agent_id)
        except Exception as e:
            print(f'Warning: Could not save agent ID: {e}')
        return agent_id
    
    def setup_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print(f'Connected to server: {self.server_url}')
            # Register with server
            self.sio.emit('agent_register', {
                'agent_id': self.agent_id,
                'hostname': self.hostname,
                'computer_name': self.computer_name,
                'domain_name': self.domain_name,
                'ip_addresses': self.ip_addresses,
                'platform': self.platform
            })
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print('Disconnected from server')
        
        @self.sio.on('registration_success')
        def on_registration_success(data):
            print(f'Successfully registered as agent: {self.agent_id}')
            print(f'Hostname: {self.hostname}')
            print(f'Computer Name: {self.computer_name}')
            print(f'Domain: {self.domain_name or "N/A"}')
            print(f'Platform: {self.platform}')
            print(f'IP Addresses: {", ".join(self.ip_addresses)}')
        
        @self.sio.on('list_directory')
        def on_list_directory(data):
            path = data.get('path', '/')
            try:
                entries = self.list_directory(path)
                self.sio.emit('filesystem_list', {
                    'agent_id': self.agent_id,
                    'path': path,
                    'entries': entries
                })
            except Exception as e:
                self.sio.emit('filesystem_list', {
                    'agent_id': self.agent_id,
                    'path': path,
                    'error': str(e),
                    'entries': []
                })
        
        @self.sio.on('read_file')
        def on_read_file(data):
            file_path = data.get('path')
            try:
                # Read file in chunks for large files
                chunk_size = 1024 * 64  # 64KB chunks
                chunk_number = data.get('chunk_number', 0)
                
                with open(file_path, 'rb') as f:
                    f.seek(chunk_number * chunk_size)
                    chunk = f.read(chunk_size)
                    hex_data = chunk.hex()
                    
                    self.sio.emit('file_content', {
                        'agent_id': self.agent_id,
                        'path': file_path,
                        'chunk_number': chunk_number,
                        'hex_data': hex_data,
                        'size': len(chunk),
                        'file_size': os.path.getsize(file_path),
                        'offset': chunk_number * chunk_size
                    })
            except Exception as e:
                self.sio.emit('file_content', {
                    'agent_id': self.agent_id,
                    'path': file_path,
                    'error': str(e)
                })
        
        @self.sio.on('get_metadata')
        def on_get_metadata(data):
            file_path = data.get('path')
            try:
                metadata = self.get_file_metadata(file_path)
                self.sio.emit('file_metadata', {
                    'agent_id': self.agent_id,
                    'path': file_path,
                    'metadata': metadata
                })
            except Exception as e:
                self.sio.emit('file_metadata', {
                    'agent_id': self.agent_id,
                    'path': file_path,
                    'error': str(e)
                })
    
    def list_directory(self, path):
        """List directory contents"""
        entries = []
        
        try:
            # Normalize path for Windows
            if platform.system() == 'Windows':
                path = os.path.normpath(path)
                if path == '.':
                    path = os.getcwd()
            
            if not os.path.exists(path):
                return entries
            
            if not os.path.isdir(path):
                return entries
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    entry = {
                        'name': item,
                        'path': item_path,
                        'is_directory': os.path.isdir(item_path),
                        'size': stat.st_size if os.path.isfile(item_path) else 0,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                        'mode': oct(stat.st_mode)[-3:] if hasattr(stat, 'st_mode') else 'N/A',
                        'uid': stat.st_uid if hasattr(stat, 'st_uid') else None,
                        'gid': stat.st_gid if hasattr(stat, 'st_gid') else None
                    }
                    entries.append(entry)
                except PermissionError:
                    entry = {
                        'name': item,
                        'path': item_path,
                        'is_directory': False,
                        'error': 'Permission denied'
                    }
                    entries.append(entry)
                except Exception as e:
                    entry = {
                        'name': item,
                        'path': item_path,
                        'is_directory': False,
                        'error': str(e)
                    }
                    entries.append(entry)
        except Exception as e:
            print(f'Error listing directory {path}: {e}')
            raise
        
        return sorted(entries, key=lambda x: (not x.get('is_directory', False), x['name'].lower()))
    
    def get_file_metadata(self, file_path):
        """Get comprehensive file metadata"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = os.stat(file_path)
        
        metadata = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'is_directory': os.path.isdir(file_path),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'mode': oct(stat.st_mode) if hasattr(stat, 'st_mode') else 'N/A',
            'uid': stat.st_uid if hasattr(stat, 'st_uid') else None,
            'gid': stat.st_gid if hasattr(stat, 'st_gid') else None,
            'inode': stat.st_ino if hasattr(stat, 'st_ino') else None,
            'device': stat.st_dev if hasattr(stat, 'st_dev') else None
        }
        
        # Calculate MD5 hash for files
        if os.path.isfile(file_path) and stat.st_size < 100 * 1024 * 1024:  # Only for files < 100MB
            try:
                md5_hash = hashlib.md5()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                metadata['md5'] = md5_hash.hexdigest()
            except Exception as e:
                metadata['hash_error'] = str(e)
        
        # Get file type
        if os.path.isfile(file_path):
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            metadata['mime_type'] = mime_type or 'unknown'
        
        # Windows-specific attributes
        if platform.system() == 'Windows':
            try:
                import win32security
                import win32api
                
                # Get file owner
                sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
                owner_sid = sd.GetSecurityDescriptorOwner()
                owner_name, domain_name, _ = win32security.LookupAccountSid(None, owner_sid)
                metadata['owner'] = f'{domain_name}\\{owner_name}' if domain_name else owner_name
                
                # Get file attributes
                attrs = win32api.GetFileAttributes(file_path)
                metadata['attributes'] = hex(attrs)
            except ImportError:
                # pywin32 not available, skip Windows-specific metadata
                pass
            except Exception as e:
                metadata['windows_metadata_error'] = str(e)
        
        return metadata
    
    def connect(self):
        """Connect to the server"""
        try:
            print(f'Connecting to server: {self.server_url}')
            print(f'Agent ID: {self.agent_id}')
            self.sio.connect(self.server_url)
            print(f'Agent started. Waiting for commands...')
            self.sio.wait()
        except KeyboardInterrupt:
            print('\nShutting down agent...')
            self.sio.disconnect()
            sys.exit(0)
        except Exception as e:
            print(f'Failed to connect to server: {e}')
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='CIF Agent - Endpoint agent for Computer Investigations Framework')
    parser.add_argument('--server-url', required=True, help='Server URL (e.g., http://localhost:5000)')
    parser.add_argument('--register', action='store_true', help='Register with server (default behavior)')
    
    args = parser.parse_args()
    
    agent = CIFAgent(args.server_url)
    agent.connect()

if __name__ == '__main__':
    main()
