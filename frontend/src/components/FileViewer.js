import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  TextField,
  Button,
  IconButton,
  Toolbar,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Search as SearchIcon,
} from '@mui/icons-material';

function FileViewer({ file, fileContent, onLoadChunk }) {
  const [activeTab, setActiveTab] = useState(0);
  const [hexOffset, setHexOffset] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    if (fileContent && fileContent.chunk_number === 0) {
      setHexOffset(0);
    }
  }, [fileContent]);

  const formatHex = (hexString, offset = 0) => {
    if (!hexString) return [];
    const bytes = hexString.match(/.{1,2}/g) || [];
    const rows = [];
    const bytesPerRow = 16;

    for (let i = 0; i < bytes.length; i += bytesPerRow) {
      const rowBytes = bytes.slice(i, i + bytesPerRow);
      const rowOffset = offset + i;
      const hex = rowBytes.map((byte, idx) => {
        const byteIndex = i + idx;
        const isHighlighted = searchResults.includes(byteIndex);
        return { value: byte, highlighted: isHighlighted };
      }).join(' ');
      const ascii = rowBytes.map(byte => {
        const charCode = parseInt(byte, 16);
        return charCode >= 32 && charCode <= 126 ? String.fromCharCode(charCode) : '.';
      }).join('');

      rows.push({
        offset: rowOffset,
        hex,
        ascii,
        bytes: rowBytes,
      });
    }

    return rows;
  };

  const handleSearch = () => {
    if (!fileContent || !searchTerm) {
      setSearchResults([]);
      return;
    }

    const hexString = fileContent.hex_data || '';
    const searchBytes = searchTerm
      .split('')
      .map(c => c.charCodeAt(0).toString(16).padStart(2, '0'))
      .join('');

    const results = [];
    let index = hexString.indexOf(searchBytes);
    while (index !== -1) {
      results.push(Math.floor(index / 2));
      index = hexString.indexOf(searchBytes, index + 1);
    }

    setSearchResults(results);
  };

  const handlePrevChunk = () => {
    if (fileContent && fileContent.chunk_number > 0) {
      const newChunk = fileContent.chunk_number - 1;
      onLoadChunk(file.path, newChunk);
    }
  };

  const handleNextChunk = () => {
    if (fileContent && fileContent.offset + fileContent.size < fileContent.file_size) {
      const newChunk = fileContent.chunk_number + 1;
      onLoadChunk(file.path, newChunk);
    }
  };

  const hexRows = fileContent ? formatHex(fileContent.hex_data, fileContent.offset || 0) : [];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{file.name}</Typography>
          <Box>
            <TextField
              size="small"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              sx={{ mr: 1, width: 200 }}
            />
            <Button variant="outlined" size="small" onClick={handleSearch} startIcon={<SearchIcon />}>
              Search
            </Button>
          </Box>
        </Box>

        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Hex View" />
          <Tab label="Text View" />
        </Tabs>
      </Paper>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {activeTab === 0 ? (
          <Box>
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Offset: {fileContent ? `0x${(fileContent.offset || 0).toString(16).toUpperCase().padStart(8, '0')}` : 'N/A'}
                  {' / '}
                  Size: {fileContent ? `${fileContent.file_size} bytes (0x${fileContent.file_size.toString(16).toUpperCase()})` : 'N/A'}
                </Typography>
              </Box>
              <Box>
                <IconButton
                  size="small"
                  onClick={handlePrevChunk}
                  disabled={!fileContent || (fileContent.offset || 0) === 0}
                >
                  <ArrowUpwardIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={handleNextChunk}
                  disabled={!fileContent || fileContent.offset + fileContent.size >= fileContent.file_size}
                >
                  <ArrowDownwardIcon />
                </IconButton>
              </Box>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ width: 120 }}>Offset</TableCell>
                    <TableCell sx={{ width: 400 }}>Hex</TableCell>
                    <TableCell>ASCII</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {hexRows.map((row, index) => (
                    <TableRow key={index} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          0x{row.offset.toString(16).toUpperCase().padStart(8, '0')}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace" component="span">
                          {row.hex.split(' ').map((byte, idx) => {
                            const byteIndex = row.offset + idx;
                            const isHighlighted = searchResults.includes(byteIndex);
                            return (
                              <span
                                key={idx}
                                style={{
                                  backgroundColor: isHighlighted ? '#ffeb3b' : 'transparent',
                                  padding: '2px 4px',
                                  marginRight: '4px',
                                }}
                              >
                                {byte}
                              </span>
                            );
                          })}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {row.ascii}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {hexRows.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary">No data available</Typography>
              </Box>
            )}
          </Box>
        ) : (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Text View
            </Typography>
            <Paper sx={{ p: 2, fontFamily: 'monospace', whiteSpace: 'pre-wrap', backgroundColor: '#1e1e1e', color: '#d4d4d4' }}>
              {fileContent ? (
                (() => {
                  try {
                    const bytes = fileContent.hex_data.match(/.{1,2}/g) || [];
                    return bytes.map(byte => {
                      const charCode = parseInt(byte, 16);
                      return charCode >= 32 && charCode <= 126 ? String.fromCharCode(charCode) : '.';
                    }).join('');
                  } catch (e) {
                    return 'Unable to decode text content';
                  }
                })()
              ) : (
                'No content loaded'
              )}
            </Paper>
          </Box>
        )}
      </Box>
    </Box>
  );
}

export default FileViewer;

