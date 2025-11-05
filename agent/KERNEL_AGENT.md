# Windows Kernel-Level Agent

This agent uses Windows kernel APIs for lower-level file system access, providing better performance and access to system-protected files.

## Architecture

### Kernel-Level APIs Used

The agent interfaces directly with Windows kernel32.dll using ctypes:

1. **FindFirstFile/FindNextFile** - Direct directory enumeration
2. **CreateFile/ReadFile** - Kernel-level file I/O
3. **GetFileAttributesEx** - Fast metadata retrieval
4. **GetFileSecurity** - Security descriptor access (with admin privileges)

### Benefits

- **Better Performance**: Direct kernel calls bypass Python's file system abstraction
- **Access Protected Files**: Can access system-protected files when run as administrator
- **More Accurate Timestamps**: Uses Windows FILETIME structures directly
- **Lower Overhead**: Fewer system calls and better caching

### Important Note

**Windows Defender Firewall** is a **user-mode component**, not a kernel component. This agent:
- Uses **kernel APIs** from user-mode (via ctypes)
- Requires **administrator privileges** for full functionality
- Does **NOT** require a kernel driver (which would be complex and require signing)

For true kernel-mode access, you would need a Windows kernel driver, which requires:
- Code signing certificate
- Driver development kit (WDK)
- Kernel debugging setup
- Much more complexity

This implementation provides the practical middle ground: kernel-level APIs from user-mode.

## Usage

### Building the Kernel Agent

```cmd
cd agent
pip install pyinstaller
pip install python-socketio psutil pywin32
pyinstaller --clean cif-kernel-agent.spec
```

### Running

**As Administrator (recommended):**
```cmd
# Right-click and "Run as Administrator"
cif-kernel-agent.exe --server-url http://your-server:5000
```

**Without Admin (limited functionality):**
```cmd
cif-kernel-agent.exe --server-url http://your-server:5000
```

## Features

### Kernel-Level Directory Listing

Uses `FindFirstFile`/`FindNextFile` APIs for:
- Faster directory enumeration
- Direct access to file attributes
- Accurate FILETIME structures
- Better handling of long paths

### Kernel-Level File Reading

Uses `CreateFile`/`ReadFile` APIs for:
- Direct file handle access
- Better performance on large files
- Access to locked files (with proper permissions)
- Lower-level file I/O control

### Enhanced Metadata

When running as administrator:
- Full security descriptor access
- File owner information
- Extended attributes
- System-protected file access

## Security Considerations

⚠️ **Important**: Running with administrator privileges:

- Grants access to system-protected files
- May trigger antivirus warnings
- Should only be used in controlled environments
- Consider code signing for production use

## Comparison with Standard Agent

| Feature | Standard Agent | Kernel Agent |
|---------|---------------|--------------|
| File Access | Python I/O | Kernel APIs |
| Performance | Standard | Enhanced |
| Protected Files | Limited | Full (as admin) |
| Timestamps | Python conversion | Direct FILETIME |
| Overhead | Higher | Lower |
| Complexity | Low | Medium |

## Fallback Behavior

The kernel agent includes fallback mechanisms:
- If kernel APIs fail, falls back to Python standard I/O
- Gracefully handles permission errors
- Works without admin privileges (with limitations)

## Requirements

- Windows 7+ (64-bit)
- Administrator privileges (recommended)
- pywin32 (for enhanced metadata)

## Troubleshooting

### "Access Denied" Errors

- Run as Administrator
- Check file permissions
- Some system files may require SYSTEM account

### Kernel API Failures

- Agent automatically falls back to standard Python I/O
- Check Windows API error codes in logs
- Verify administrator privileges

### Antivirus Warnings

- Kernel-level access may trigger false positives
- Consider code signing the executable
- Whitelist the executable in antivirus software

