# Computer Investigations Framework

<div align="center">

![CIF Logo](https://via.placeholder.com/150x150?text=CIF)

**An open-source digital forensics platform for remote file system investigation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)

[Quick Start](#quick-start) • [Documentation](#documentation) • [Features](#features) • [Installation](#installation) • [Contributing](#contributing)

</div>

---

<div align="center">

⚠️ **WORK IN PROGRESS** ⚠️

**This project is currently under active development.** The codebase is functional but not yet ready for production installations. An update will be added to this README when the project is ready for general use.

</div>

---

## Overview

Computer Investigations Framework (CIF) is an open-source digital forensics platform designed for remote file system investigation. CIF provides features that you might find in commercial products, but is fully open-source:

- 🌐 **Web-based investigation dashboard** - Modern, intuitive interface for investigations
- 🔌 **Lightweight endpoint agents** - Easy deployment on Windows, Linux, and macOS
- 🔍 **Classic forensic interface** - Hex view, metadata, and search capabilities
- ⚡ **Real-time file system browsing** - WebSocket-based live data access
- 🏢 **Enterprise-ready** - Domain-aware agent tagging and management

## Features

### 🎯 Core Capabilities

- **Agent Management**: View all registered agents with domain, computer name, and IP address tagging
- **File System Browser**: Navigate remote file systems with breadcrumb navigation
- **Hex Viewer**: Classic forensic interface with hexadecimal file viewer featuring:
  - Offset display (hex addresses)
  - Hex and ASCII columns side-by-side
  - Search functionality within hex content
  - Chunked reading for large files
- **Metadata Display**: Comprehensive file metadata including:
  - File size, timestamps (created, modified, accessed)
  - File permissions and ownership
  - MD5 hash (for files < 100MB)
  - MIME type, inode, user/group IDs
  - Windows-specific attributes (owner, file attributes)

### 🚀 Advanced Features

- **Windows Binary Support**: Standalone `.exe` for Windows endpoints (no Python required)
- **Kernel-Level Access**: Windows agent with kernel API integration for enhanced performance
- **Multi-IP Support**: Detect and display all network interfaces
- **Domain Integration**: Automatic domain detection and tagging
- **Real-time Updates**: WebSocket-based communication for live data

## Architecture

```
┌─────────────┐
│   Web UI    │ (React Frontend)
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼──────────────────┐
│   Backend Server        │ (Python/Flask)
│   - API Endpoints       │
│   - WebSocket Server    │
│   - SQLite Database     │
└──────┬──────────────────┘
       │
       │ Registration & Commands
       │
┌──────▼──────┐  ┌──────────┐  ┌──────────┐
│   Agent 1   │  │ Agent 2  │  │ Agent N  │
│  (Endpoint) │  │(Endpoint)│  │(Endpoint)│
└─────────────┘  └──────────┘  └──────────┘
```

## Quick Start

### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **npm or yarn** - Comes with Node.js

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/malsiftcyber/ComputerInvestigationsFramework.git
cd ComputerInvestigationsFramework
```

#### 2. Start Backend Server

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python backend/server.py
```

The backend will start on `http://localhost:5000`

#### 3. Start Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

#### 4. Deploy Agent

**Python Agent (Cross-platform):**
```bash
cd agent
pip install -e .
cif-agent --server-url http://your-server-ip:5000
```

**Windows Binary:**
```cmd
# Download cif-agent.exe from Releases
cif-agent.exe --server-url http://your-server-ip:5000
```

### First Investigation

1. Open `http://localhost:3000` in your browser
2. You should see your registered agent(s) in the dashboard
3. Click on an agent to browse its file system
4. Click on files to view them in forensic mode (hex view + metadata)

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

## Installation

### Backend Server

See [Backend Installation Guide](docs/BACKEND.md)

### Frontend

See [Frontend Installation Guide](docs/FRONTEND.md)

### Agents

#### Standard Agent (Python)

```bash
cd agent
pip install -e .
```

#### Windows Binary

Download pre-built binaries from [Releases](https://github.com/yourusername/ComputerInvestigationsFramework/releases) or build your own:

```cmd
cd agent
build_windows.bat
```

See [agent/BUILD_WINDOWS.md](agent/BUILD_WINDOWS.md) for detailed build instructions.

#### Windows Kernel Agent

For enhanced performance and access to protected files:

```cmd
cd agent
build_kernel_agent.bat
```

See [agent/KERNEL_AGENT.md](agent/KERNEL_AGENT.md) for more information.

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Agent Documentation](agent/README.md)
- [Windows Build Guide](agent/BUILD_WINDOWS.md)
- [Kernel Agent Guide](agent/KERNEL_AGENT.md)
- [API Documentation](docs/API.md) (Coming soon)

## Project Structure

```
ComputerInvestigationsFramework/
├── backend/              # Backend server (Flask)
│   ├── server.py        # Main server application
│   └── __init__.py
├── agent/                # Endpoint agent software
│   ├── agent.py         # Standard agent
│   ├── windows_kernel_agent.py  # Windows kernel agent
│   ├── setup.py         # Package setup
│   ├── build_windows.bat # Windows build script
│   └── ...
├── frontend/             # React web interface
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.js       # Main app component
│   │   └── index.js     # Entry point
│   └── package.json
├── .github/
│   └── workflows/       # GitHub Actions workflows
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── QUICKSTART.md       # Quick start guide
```

## Usage Examples

### Basic File System Investigation

```python
# Agent automatically registers on startup
cif-agent --server-url http://192.168.1.100:5000

# In web interface:
# 1. Select agent from dashboard
# 2. Browse file system
# 3. Click files to view hex content
# 4. Review metadata panel
```

### Windows Domain Environment

```cmd
# Agents automatically detect domain
cif-agent.exe --server-url http://investigation-server:5000

# Dashboard shows: DOMAIN\COMPUTERNAME
# All IP addresses are displayed
```

## Security Considerations

⚠️ **Important**: This tool is designed for authorized investigations only.

### Production Deployment Checklist

- [ ] Add authentication/authorization
- [ ] Use HTTPS/TLS encryption
- [ ] Implement proper access controls
- [ ] Add audit logging
- [ ] Secure agent-server communication
- [ ] Code sign Windows binaries
- [ ] Review firewall rules
- [ ] Enable rate limiting

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ComputerInvestigationsFramework.git
cd ComputerInvestigationsFramework

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install

# Run development servers
# Terminal 1:
python backend/server.py

# Terminal 2:
cd frontend && npm start
```

## Troubleshooting

### Common Issues

**Agent not appearing in dashboard:**
- Verify agent is running and can reach server URL
- Check firewall settings
- Verify WebSocket connection in browser console

**Files not loading:**
- Ensure agent has proper permissions to read files
- Check agent logs for errors
- Verify file path is correct

**WebSocket connection issues:**
- Check firewall settings (port 5000)
- Verify server is running
- Check network connectivity

For more troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Roadmap

- [ ] Authentication and authorization
- [ ] HTTPS/TLS support
- [ ] File carving capabilities
- [ ] Timeline analysis
- [ ] Registry viewer (Windows)
- [ ] Event log viewer
- [ ] Reporting and export features
- [ ] Multi-user support
- [ ] Case management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by classic forensic investigation tools and commercial digital forensics platforms
- Built with Flask, React, and Material-UI
- Uses Socket.IO for real-time communication

## Support

- 📧 Email: security@malsiftcyber.com
- 🐛 Issues: [GitHub Issues](https://github.com/malsiftcyber/ComputerInvestigationsFramework/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/malsiftcyber/ComputerInvestigationsFramework/discussions)

---

<div align="center">

Made with ❤️ for the digital forensics community

[⬆ Back to Top](#computer-investigations-framework)

</div>
