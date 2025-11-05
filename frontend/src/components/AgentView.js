import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Breadcrumbs,
  Link,
  Divider,
  Grid,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import FileViewer from './FileViewer';
import MetadataPanel from './MetadataPanel';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

function AgentView() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const [socket, setSocket] = useState(null);
  const [agentInfo, setAgentInfo] = useState(null);
  const [currentPath, setCurrentPath] = useState('/');
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileMetadata, setFileMetadata] = useState(null);

  useEffect(() => {
    // Fetch agent information
    const fetchAgentInfo = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/agents`);
        const agent = response.data.find(a => a.id === agentId);
        if (agent) {
          setAgentInfo(agent);
        }
      } catch (error) {
        console.error('Failed to fetch agent info:', error);
      }
    };
    
    fetchAgentInfo();
    
    const newSocket = io(API_BASE);
    setSocket(newSocket);

    newSocket.on('filesystem_list_response', (data) => {
      if (data.agent_id === agentId) {
        setEntries(data.entries || []);
        setLoading(false);
      }
    });

    newSocket.on('file_content_response', (data) => {
      if (data.agent_id === agentId) {
        setFileContent(data);
      }
    });

    newSocket.on('file_metadata_response', (data) => {
      if (data.agent_id === agentId) {
        setFileMetadata(data.metadata);
      }
    });

    return () => {
      newSocket.close();
    };
  }, [agentId]);

  useEffect(() => {
    if (socket && socket.connected) {
      loadDirectory(currentPath);
    }
  }, [socket, currentPath]);

  const loadDirectory = (path) => {
    setLoading(true);
    setEntries([]);
    socket.emit('list_directory', { path });
  };

  const handleItemClick = (entry) => {
    if (entry.is_directory) {
      setCurrentPath(entry.path);
      setSelectedFile(null);
      setFileContent(null);
      setFileMetadata(null);
    } else {
      setSelectedFile(entry);
      loadFile(entry.path);
    }
  };

  const loadFile = (filePath, chunkNumber = 0) => {
    socket.emit('read_file', { path: filePath, chunk_number: chunkNumber });
    socket.emit('get_metadata', { path: filePath });
  };

  const handleBreadcrumbClick = (path) => {
    setCurrentPath(path);
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatAgentName = () => {
    if (!agentInfo) return agentId;
    if (agentInfo.domain_name && agentInfo.computer_name) {
      return `${agentInfo.domain_name}\\${agentInfo.computer_name}`;
    }
    return agentInfo.computer_name || agentInfo.hostname || agentId;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const pathParts = currentPath.split('/').filter(p => p);
  const breadcrumbs = ['/'].concat(pathParts);

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {formatAgentName()}
            {agentInfo && agentInfo.domain_name && (
              <Chip 
                label={agentInfo.domain_name} 
                size="small" 
                color="primary" 
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
          {agentInfo && agentInfo.ip_addresses && agentInfo.ip_addresses.length > 0 && (
            <Typography variant="body2" sx={{ mr: 2 }}>
              {agentInfo.ip_addresses.join(', ')}
            </Typography>
          )}
          <IconButton color="inherit" onClick={() => loadDirectory(currentPath)}>
            <RefreshIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* File System Browser */}
        <Box sx={{ width: '400px', display: 'flex', flexDirection: 'column', borderRight: 1, borderColor: 'divider' }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Breadcrumbs aria-label="breadcrumb">
              {breadcrumbs.map((part, index) => {
                const path = index === 0 ? '/' : '/' + breadcrumbs.slice(1, index + 1).join('/');
                return (
                  <Link
                    key={index}
                    component="button"
                    variant="body2"
                    onClick={() => handleBreadcrumbClick(path)}
                    sx={{ textDecoration: 'none', cursor: 'pointer' }}
                  >
                    {part === '' ? '/' : part}
                  </Link>
                );
              })}
            </Breadcrumbs>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List sx={{ flex: 1, overflow: 'auto' }}>
              {entries.map((entry, index) => (
                <React.Fragment key={index}>
                  <ListItem
                    button
                    onClick={() => handleItemClick(entry)}
                    selected={selectedFile && selectedFile.path === entry.path}
                  >
                    <ListItemIcon>
                      {entry.is_directory ? <FolderIcon /> : <FileIcon />}
                    </ListItemIcon>
                    <ListItemText
                      primary={entry.name}
                      secondary={
                        <Box>
                          {!entry.is_directory && (
                            <Typography variant="caption" display="block">
                              {formatSize(entry.size)} • {formatDate(entry.modified)}
                            </Typography>
                          )}
                          {entry.error && (
                            <Chip label={entry.error} color="error" size="small" sx={{ mt: 0.5 }} />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Main Content Area */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {selectedFile ? (
            <Grid container sx={{ height: '100%' }}>
              <Grid item xs={12} md={fileMetadata ? 8 : 12} sx={{ height: '100%', overflow: 'hidden' }}>
                <FileViewer file={selectedFile} fileContent={fileContent} onLoadChunk={loadFile} />
              </Grid>
              {fileMetadata && (
                <Grid item xs={12} md={4} sx={{ height: '100%', overflow: 'auto', borderLeft: 1, borderColor: 'divider' }}>
                  <MetadataPanel metadata={fileMetadata} />
                </Grid>
              )}
            </Grid>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
              <Typography variant="h6">Select a file to view</Typography>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Browse the file system on the left and click on a file to view its contents in forensic mode.
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default AgentView;

