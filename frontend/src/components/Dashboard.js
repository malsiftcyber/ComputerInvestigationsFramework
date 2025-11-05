import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  AppBar,
  Toolbar,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Computer as ComputerIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/agents`);
      setAgents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'offline':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatAgentName = (agent) => {
    if (agent.domain_name && agent.computer_name) {
      return `${agent.domain_name}\\${agent.computer_name}`;
    }
    return agent.computer_name || agent.hostname || 'Unknown';
  };

  const formatIPAddresses = (ip_addresses) => {
    if (!ip_addresses || ip_addresses.length === 0) {
      return 'N/A';
    }
    if (ip_addresses.length === 1) {
      return ip_addresses[0];
    }
    return `${ip_addresses[0]} (+${ip_addresses.length - 1} more)`;
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <ComputerIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Computer Investigations Framework
          </Typography>
          <IconButton color="inherit" onClick={fetchAgents}>
            <RefreshIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Typography variant="h4" gutterBottom>
          Registered Agents
        </Typography>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Computer Name</TableCell>
                  <TableCell>Domain</TableCell>
                  <TableCell>Platform</TableCell>
                  <TableCell>IP Address(es)</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Registered</TableCell>
                  <TableCell>Last Seen</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {agents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      No agents registered. Install an agent on an endpoint to begin.
                    </TableCell>
                  </TableRow>
                ) : (
                  agents.map((agent) => (
                    <TableRow
                      key={agent.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/agent/${agent.id}`)}
                    >
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {formatAgentName(agent)}
                          </Typography>
                          {agent.hostname && agent.hostname !== agent.computer_name && (
                            <Typography variant="caption" color="text.secondary">
                              {agent.hostname}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {agent.domain_name ? (
                          <Chip label={agent.domain_name} size="small" color="primary" />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>{agent.platform}</TableCell>
                      <TableCell>
                        <Tooltip
                          title={
                            agent.ip_addresses && agent.ip_addresses.length > 1
                              ? agent.ip_addresses.join(', ')
                              : ''
                          }
                        >
                          <Typography variant="body2">
                            {formatIPAddresses(agent.ip_addresses)}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={agent.status}
                          color={getStatusColor(agent.status)}
                          size="small"
                          icon={
                            agent.status === 'active' ? (
                              <CheckCircleIcon />
                            ) : (
                              <CancelIcon />
                            )
                          }
                        />
                      </TableCell>
                      <TableCell>{formatDate(agent.registered_at)}</TableCell>
                      <TableCell>{formatDate(agent.last_seen)}</TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/agent/${agent.id}`);
                          }}
                        >
                          <ComputerIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
    </Box>
  );
}

export default Dashboard;

