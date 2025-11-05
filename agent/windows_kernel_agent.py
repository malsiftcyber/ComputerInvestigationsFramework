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

class WindowsKernelAgent:
    """Windows agent with kernel-level access using native Windows APIs"""
    
    def __init__(self, server_url):
        if platform.system() != 'Windows':
            raise RuntimeError("WindowsKernelAgent is Windows-only")
        
        self.server_url = server_url
        self.agent_id = self.get_or_create_agent_id()
        self.hostname = platform.node()
        self.platform = platform.system()
        self.computer_name = self.get_computer_name()
        self.domain_name = self.get_domain_name()
        self.ip_addresses = self.get_ip_addresses()
        self.sio = socketio.Client()
        self.setup_handlers()
        
        # Check for admin privileges
        self.is_admin = self.check_admin_privileges()
        if not self.is_admin:
            print("Warning: Not running with administrator privileges. Some features may be limited.")
    
    def get_computer_name(self):
        """Get computer name"""
        try:
            import win32api
            return win32api.GetComputerName()
        except:
            return platform.node()
    
    def get_domain_name(self):
        """Get domain name"""
        try:
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
        
    def check_admin_privileges(self):
        """Check if running with administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def get_or_create_agent_id(self):
        """Get or create a unique agent ID"""
        agent_id_file = os.path.join(os.getenv('PROGRAMDATA', os.getenv('APPDATA', os.path.expanduser('~'))), 'cif_agent_id')
        
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
            self.sio.emit('agent_register', {
                'agent_id': self.agent_id,
                'hostname': self.hostname,
                'computer_name': self.computer_name,
                'domain_name': self.domain_name,
                'ip_addresses': self.ip_addresses,
                'platform': self.platform,
                'is_admin': self.is_admin,
                'kernel_mode': True
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
            print(f'Admin privileges: {self.is_admin}')
            print(f'Kernel-level access: Enabled')
        
        @self.sio.on('list_directory')
        def on_list_directory(data):
            path = data.get('path', 'C:\\')
            try:
                entries = self.list_directory_kernel(path)
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
                chunk_size = 1024 * 64
                chunk_number = data.get('chunk_number', 0)
                
                # Use native Windows file I/O
                file_data = self.read_file_kernel(file_path, chunk_number, chunk_size)
                
                self.sio.emit('file_content', {
                    'agent_id': self.agent_id,
                    'path': file_path,
                    'chunk_number': chunk_number,
                    'hex_data': file_data['hex'],
                    'size': file_data['size'],
                    'file_size': file_data['file_size'],
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
                metadata = self.get_file_metadata_kernel(file_path)
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
    
    def list_directory_kernel(self, path):
        """List directory using Windows kernel APIs"""
        entries = []
        
        try:
            import ctypes
            from ctypes import wintypes
            
            # Normalize path
            path = os.path.normpath(path)
            if not os.path.exists(path):
                return entries
            
            if not os.path.isdir(path):
                return entries
            
            # Use FindFirstFile/FindNextFile for better performance
            INVALID_HANDLE_VALUE = -1
            FILE_ATTRIBUTE_DIRECTORY = 0x10
            
            class WIN32_FIND_DATA(ctypes.Structure):
                _fields_ = [
                    ('dwFileAttributes', wintypes.DWORD),
                    ('ftCreationTime', wintypes.FILETIME),
                    ('ftLastAccessTime', wintypes.FILETIME),
                    ('ftLastWriteTime', wintypes.FILETIME),
                    ('nFileSizeHigh', wintypes.DWORD),
                    ('nFileSizeLow', wintypes.DWORD),
                    ('dwReserved0', wintypes.DWORD),
                    ('dwReserved1', wintypes.DWORD),
                    ('cFileName', wintypes.CHAR * 260),
                    ('cAlternateFileName', wintypes.CHAR * 14),
                ]
            
            kernel32 = ctypes.windll.kernel32
            search_path = os.path.join(path, '*')
            
            find_data = WIN32_FIND_DATA()
            handle = kernel32.FindFirstFileA(
                search_path.encode('utf-8'),
                ctypes.byref(find_data)
            )
            
            if handle == INVALID_HANDLE_VALUE:
                # Fallback to standard Python approach
                return self.list_directory_fallback(path)
            
            try:
                while True:
                    name = find_data.cFileName.decode('utf-8', errors='ignore')
                    
                    # Skip . and ..
                    if name in ('.', '..'):
                        if kernel32.FindNextFileA(handle, ctypes.byref(find_data)) == 0:
                            break
                        continue
                    
                    item_path = os.path.join(path, name)
                    is_dir = bool(find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
                    
                    # Get file size
                    size = (find_data.nFileSizeHigh << 32) | find_data.nFileSizeLow
                    
                    # Convert FILETIME to datetime
                    def filetime_to_datetime(ft):
                        """Convert Windows FILETIME to Python datetime"""
                        import time
                        EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970
                        HUNDREDS_OF_NANOSECONDS = 10000000
                        
                        total = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
                        total -= EPOCH_AS_FILETIME
                        seconds = total // HUNDREDS_OF_NANOSECONDS
                        nanoseconds = (total % HUNDREDS_OF_NANOSECONDS) * 100
                        
                        return datetime.fromtimestamp(seconds + nanoseconds / 1e9)
                    
                    entry = {
                        'name': name,
                        'path': item_path,
                        'is_directory': is_dir,
                        'size': size if not is_dir else 0,
                        'created': filetime_to_datetime(find_data.ftCreationTime).isoformat(),
                        'modified': filetime_to_datetime(find_data.ftLastWriteTime).isoformat(),
                        'accessed': filetime_to_datetime(find_data.ftLastAccessTime).isoformat(),
                        'attributes': hex(find_data.dwFileAttributes),
                        'kernel_mode': True
                    }
                    
                    entries.append(entry)
                    
                    if kernel32.FindNextFileA(handle, ctypes.byref(find_data)) == 0:
                        break
            finally:
                kernel32.FindClose(handle)
                
        except Exception as e:
            print(f'Kernel API error, falling back: {e}')
            return self.list_directory_fallback(path)
        
        return sorted(entries, key=lambda x: (not x.get('is_directory', False), x['name'].lower()))
    
    def list_directory_fallback(self, path):
        """Fallback directory listing using standard Python"""
        entries = []
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
        return sorted(entries, key=lambda x: (not x.get('is_directory', False), x['name'].lower()))
    
    def read_file_kernel(self, file_path, chunk_number, chunk_size):
        """Read file using Windows kernel APIs"""
        import ctypes
        from ctypes import wintypes
        
        GENERIC_READ = 0x80000000
        OPEN_EXISTING = 3
        FILE_SHARE_READ = 0x1
        FILE_SHARE_WRITE = 0x2
        
        kernel32 = ctypes.windll.kernel32
        
        # Open file with kernel-level access
        handle = kernel32.CreateFileA(
            file_path.encode('utf-8'),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None
        )
        
        if handle == -1:  # INVALID_HANDLE_VALUE
            raise IOError(f"Could not open file: {file_path}")
        
        try:
            # Get file size
            file_size_high = wintypes.DWORD()
            file_size = kernel32.GetFileSize(handle, ctypes.byref(file_size_high))
            file_size |= (file_size_high.value << 32)
            
            # Seek to chunk position
            offset = chunk_number * chunk_size
            kernel32.SetFilePointer(handle, offset, None, 0)
            
            # Read chunk
            buffer = ctypes.create_string_buffer(chunk_size)
            bytes_read = wintypes.DWORD()
            
            if not kernel32.ReadFile(handle, buffer, chunk_size, ctypes.byref(bytes_read), None):
                raise IOError("Failed to read file")
            
            chunk = buffer.raw[:bytes_read.value]
            
            return {
                'hex': chunk.hex(),
                'size': len(chunk),
                'file_size': file_size
            }
        finally:
            kernel32.CloseHandle(handle)
    
    def get_file_metadata_kernel(self, file_path):
        """Get comprehensive file metadata using Windows kernel APIs"""
        import ctypes
        from ctypes import wintypes
        
        metadata = {}
        
        try:
            # Use GetFileAttributesEx for faster metadata retrieval
            class WIN32_FILE_ATTRIBUTE_DATA(ctypes.Structure):
                _fields_ = [
                    ('dwFileAttributes', wintypes.DWORD),
                    ('ftCreationTime', wintypes.FILETIME),
                    ('ftLastAccessTime', wintypes.FILETIME),
                    ('ftLastWriteTime', wintypes.FILETIME),
                    ('nFileSizeHigh', wintypes.DWORD),
                    ('nFileSizeLow', wintypes.DWORD),
                ]
            
            kernel32 = ctypes.windll.kernel32
            file_data = WIN32_FILE_ATTRIBUTE_DATA()
            
            if kernel32.GetFileAttributesExA(
                file_path.encode('utf-8'),
                0,  # GetFileExInfoStandard
                ctypes.byref(file_data)
            ):
                # Convert FILETIME to datetime
                def filetime_to_datetime(ft):
                    import time
                    EPOCH_AS_FILETIME = 116444736000000000
                    HUNDREDS_OF_NANOSECONDS = 10000000
                    
                    total = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
                    total -= EPOCH_AS_FILETIME
                    seconds = total // HUNDREDS_OF_NANOSECONDS
                    nanoseconds = (total % HUNDREDS_OF_NANOSECONDS) * 100
                    
                    return datetime.fromtimestamp(seconds + nanoseconds / 1e9)
                
                size = (file_data.nFileSizeHigh << 32) | file_data.nFileSizeLow
                
                metadata.update({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': size,
                    'is_directory': bool(file_data.dwFileAttributes & 0x10),
                    'created': filetime_to_datetime(file_data.ftCreationTime).isoformat(),
                    'modified': filetime_to_datetime(file_data.ftLastWriteTime).isoformat(),
                    'accessed': filetime_to_datetime(file_data.ftLastAccessTime).isoformat(),
                    'attributes': hex(file_data.dwFileAttributes),
                    'kernel_mode': True
                })
        except Exception as e:
            print(f'Kernel metadata error: {e}')
            # Fallback to standard method
            metadata = self.get_file_metadata_fallback(file_path)
        
        # Get additional Windows-specific metadata
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
            metadata['file_attributes'] = hex(attrs)
            
            # Get extended attributes if available
            if self.is_admin:
                try:
                    # Get security descriptor
                    sd = win32security.GetFileSecurity(file_path, win32security.DACL_SECURITY_INFORMATION)
                    metadata['security_descriptor'] = str(sd)
                except:
                    pass
        except ImportError:
            pass
        except Exception as e:
            metadata['windows_metadata_error'] = str(e)
        
        # Calculate MD5 hash for files
        if not metadata.get('is_directory', False) and metadata.get('size', 0) < 100 * 1024 * 1024:
            try:
                md5_hash = hashlib.md5()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                metadata['md5'] = md5_hash.hexdigest()
            except Exception as e:
                metadata['hash_error'] = str(e)
        
        # Get MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        metadata['mime_type'] = mime_type or 'unknown'
        
        return metadata
    
    def get_file_metadata_fallback(self, file_path):
        """Fallback metadata retrieval"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'is_directory': os.path.isdir(file_path),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
        }
    
    def connect(self):
        """Connect to the server"""
        try:
            print(f'Connecting to server: {self.server_url}')
            print(f'Agent ID: {self.agent_id}')
            print(f'Running with admin privileges: {self.is_admin}')
            print(f'Kernel-level access: Enabled')
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
    parser = argparse.ArgumentParser(description='CIF Kernel Agent - Windows kernel-level agent')
    parser.add_argument('--server-url', required=True, help='Server URL (e.g., http://localhost:5000)')
    
    args = parser.parse_args()
    
    if platform.system() != 'Windows':
        print("Error: WindowsKernelAgent requires Windows")
        sys.exit(1)
    
    agent = WindowsKernelAgent(args.server_url)
    agent.connect()

if __name__ == '__main__':
    main()

