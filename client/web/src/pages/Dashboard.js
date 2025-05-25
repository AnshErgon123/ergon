import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

// Mock data - replace with real data from your backend
const mockData = {
  status: {
    connected: true,
    messagesPerSecond: 1250,
    errorRate: 0.5,
    uptime: '2h 45m',
  },
  recentMessages: [
    { id: '0x123', data: '0x1A2B3C4D', timestamp: '2024-03-20 14:30:45' },
    { id: '0x456', data: '0x5E6F7A8B', timestamp: '2024-03-20 14:30:44' },
    { id: '0x789', data: '0x9C0D1E2F', timestamp: '2024-03-20 14:30:43' },
  ],
  statistics: {
    totalMessages: 125000,
    activeNodes: 8,
    busLoad: 45,
  },
};

const StatCard = ({ title, value, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box
          sx={{
            backgroundColor: `${color}15`,
            borderRadius: '50%',
            p: 1,
            mr: 2,
          }}
        >
          {icon}
        </Box>
        <Typography variant="h6" component="div">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" component="div" sx={{ mb: 1 }}>
        {value}
      </Typography>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <IconButton color="primary" size="large">
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Status Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Connection Status"
            value={mockData.status.connected ? 'Connected' : 'Disconnected'}
            icon={<CheckCircleIcon sx={{ color: '#4caf50' }} />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Messages/sec"
            value={mockData.status.messagesPerSecond.toLocaleString()}
            icon={<SpeedIcon sx={{ color: '#2196f3' }} />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Error Rate"
            value={`${mockData.status.errorRate}%`}
            icon={<WarningIcon sx={{ color: '#ff9800' }} />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Uptime"
            value={mockData.status.uptime}
            icon={<CheckCircleIcon sx={{ color: '#4caf50' }} />}
            color="#4caf50"
          />
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Recent Messages */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Recent Messages"
              action={
                <IconButton aria-label="refresh">
                  <RefreshIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      <th style={{ textAlign: 'left', padding: '8px' }}>ID</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Data</th>
                      <th style={{ textAlign: 'left', padding: '8px' }}>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockData.recentMessages.map((msg, index) => (
                      <tr key={index}>
                        <td style={{ padding: '8px' }}>{msg.id}</td>
                        <td style={{ padding: '8px' }}>{msg.data}</td>
                        <td style={{ padding: '8px' }}>{msg.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Statistics" />
            <Divider />
            <CardContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Total Messages
                </Typography>
                <Typography variant="h6" gutterBottom>
                  {mockData.statistics.totalMessages.toLocaleString()}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={75}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Active Nodes
                </Typography>
                <Typography variant="h6" gutterBottom>
                  {mockData.statistics.activeNodes}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={80}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Bus Load
                </Typography>
                <Typography variant="h6" gutterBottom>
                  {mockData.statistics.busLoad}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={mockData.statistics.busLoad}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 