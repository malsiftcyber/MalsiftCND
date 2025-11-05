import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Activity, Server, Search, Shield } from 'lucide-react'
import './Dashboard.css'
import './shared.css'

const Dashboard: React.FC = () => {
  const { data: scans = [], isLoading: scansLoading, error: scansError } = useQuery({
    queryKey: ['scans'],
    queryFn: async () => {
      try {
        const res = await api.get('/scans/', { params: { limit: 10 } })
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load scans:', error)
        return []
      }
    },
    retry: 1,
  })

  const { data: devices = [], isLoading: devicesLoading, error: devicesError } = useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      try {
        const res = await api.get('/devices/', { params: { limit: 100 } })
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load devices:', error)
        return []
      }
    },
    retry: 1,
  })

  const isLoading = scansLoading || devicesLoading

  const scanStatusCounts = scans?.reduce((acc: any, scan: any) => {
    acc[scan.status] = (acc[scan.status] || 0) + 1
    return acc
  }, {}) || {}

  const deviceTypeCounts = devices?.reduce((acc: any, device: any) => {
    const type = device.device_type || 'Unknown'
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {}) || {}

  const chartData = Object.entries(scanStatusCounts).map(([name, value]) => ({
    name,
    value,
  }))

  const pieData = Object.entries(deviceTypeCounts).map(([name, value]) => ({
    name,
    value,
  }))

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

  if (isLoading) {
    return (
      <div className="dashboard">
        <h1>Dashboard</h1>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      {(scansError || devicesError) && (
        <div className="error-message">
          {scansError && <div>Failed to load scans: {scansError instanceof Error ? scansError.message : 'Unknown error'}</div>}
          {devicesError && <div>Failed to load devices: {devicesError instanceof Error ? devicesError.message : 'Unknown error'}</div>}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#667eea20', color: '#667eea' }}>
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{scans?.length || 0}</div>
            <div className="stat-label">Total Scans</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#28a74520', color: '#28a745' }}>
            <Server size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{devices?.length || 0}</div>
            <div className="stat-label">Discovered Devices</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#17a2b820', color: '#17a2b8' }}>
            <Search size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{scans?.filter((s: any) => s.status === 'running').length || 0}</div>
            <div className="stat-label">Active Scans</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#ffc10720', color: '#ffc107' }}>
            <Shield size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{scans?.filter((s: any) => s.status === 'completed').length || 0}</div>
            <div className="stat-label">Completed Scans</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>Scan Status Distribution</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No scan data available</div>
          )}
        </div>

        <div className="chart-card">
          <h2>Device Types</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No device data available</div>
          )}
        </div>
      </div>

      <div className="recent-scans">
        <h2>Recent Scans</h2>
        {scans.length === 0 ? (
          <div className="empty-state">No scans found. Create your first scan to get started.</div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Scan ID</th>
                  <th>Targets</th>
                  <th>Status</th>
                  <th>Scanner</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {scans.slice(0, 10).map((scan: any) => (
                  <tr key={scan.scan_id}>
                    <td>{scan.scan_id?.substring(0, 8) || 'N/A'}...</td>
                    <td>{scan.targets?.length || 0} targets</td>
                    <td>
                      <span className={`status-badge status-${scan.status || 'unknown'}`}>
                        {scan.status || 'unknown'}
                      </span>
                    </td>
                    <td>{scan.scanner || 'N/A'}</td>
                    <td>{scan.created_at ? new Date(scan.created_at).toLocaleDateString() : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
