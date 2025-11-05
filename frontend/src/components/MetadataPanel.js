import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';

function MetadataPanel({ metadata }) {
  if (!metadata) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="text.secondary">No metadata available</Typography>
      </Box>
    );
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        File Metadata
      </Typography>

      <Paper sx={{ p: 2, mt: 2 }}>
        <List dense>
          <ListItem>
            <ListItemText
              primary="Name"
              secondary={metadata.name || 'N/A'}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Path"
              secondary={metadata.path || 'N/A'}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Size"
              secondary={metadata.size ? formatBytes(metadata.size) : 'N/A'}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Type"
              secondary={
                <Chip
                  label={metadata.is_directory ? 'Directory' : 'File'}
                  size="small"
                  color={metadata.is_directory ? 'primary' : 'default'}
                />
              }
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Created"
              secondary={formatDate(metadata.created)}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Modified"
              secondary={formatDate(metadata.modified)}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Accessed"
              secondary={formatDate(metadata.accessed)}
            />
          </ListItem>
          <Divider />

          {metadata.mode && (
            <>
              <ListItem>
                <ListItemText
                  primary="Permissions"
                  secondary={
                    <Typography variant="body2" fontFamily="monospace">
                      {metadata.mode}
                    </Typography>
                  }
                />
              </ListItem>
              <Divider />
            </>
          )}

          {metadata.inode && (
            <>
              <ListItem>
                <ListItemText
                  primary="Inode"
                  secondary={metadata.inode}
                />
              </ListItem>
              <Divider />
            </>
          )}

          {metadata.md5 && (
            <>
              <ListItem>
                <ListItemText
                  primary="MD5 Hash"
                  secondary={
                    <Typography variant="body2" fontFamily="monospace">
                      {metadata.md5}
                    </Typography>
                  }
                />
              </ListItem>
              <Divider />
            </>
          )}

          {metadata.mime_type && (
            <>
              <ListItem>
                <ListItemText
                  primary="MIME Type"
                  secondary={metadata.mime_type}
                />
              </ListItem>
              <Divider />
            </>
          )}

          {metadata.uid !== undefined && (
            <>
              <ListItem>
                <ListItemText
                  primary="User ID"
                  secondary={metadata.uid}
                />
              </ListItem>
              <Divider />
            </>
          )}

          {metadata.gid !== undefined && (
            <>
              <ListItem>
                <ListItemText
                  primary="Group ID"
                  secondary={metadata.gid}
                />
              </ListItem>
            </>
          )}
        </List>
      </Paper>
    </Box>
  );
}

export default MetadataPanel;

