# Computer Investigations Framework - Quick Start Guide

## Overview

This is an open-source digital forensics platform similar to Magnet Axiom, featuring:
- Web-based investigation interface
- Endpoint agents for remote file system access
- EnCase-style forensic file viewer with hex view
- Real-time file system browsing

## Quick Start

### 1. Start the Backend Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python backend/server.py
```

Server runs on `http://localhost:5000`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

### 3. Install Agent on Target Endpoint

```bash
cd agent
pip install -e .
cif-agent --server-url http://your-server-ip:5000
```

### 4. Use the Web Interface

1. Open `http://localhost:3000` in your browser
2. You should see your registered agent(s) in the dashboard
3. Click on an agent to browse its file system
4. Click on files to view them in forensic mode (hex view + metadata)

## Architecture

- **Backend**: Flask server with WebSocket support (SocketIO)
- **Frontend**: React application with Material-UI
- **Agent**: Python script that connects to server and responds to file system queries
- **Database**: SQLite for storing agent registration info

## Key Features

1. **Agent Management Dashboard**: View all registered agents and their status
2. **File System Browser**: Navigate remote file systems with breadcrumb navigation
3. **Hex Viewer**: EnCase-style hexadecimal file viewer with:
   - Offset display
   - Hex and ASCII columns
   - Search functionality
   - Chunked reading for large files
4. **Metadata Panel**: Shows file metadata including:
   - Size, timestamps, permissions
   - MD5 hash (for files < 100MB)
   - MIME type, inode, user/group IDs

## Security Notes

⚠️ **Important**: This is a development tool. For production use, you should:
- Add authentication/authorization
- Use HTTPS/TLS encryption
- Implement proper access controls
- Add audit logging
- Secure the agent-server communication

## Troubleshooting

- **Agent not showing in dashboard**: Check that the agent is running and can reach the server URL
- **Files not loading**: Ensure the agent has proper permissions to read files
- **WebSocket connection issues**: Check firewall settings and ensure ports are open

