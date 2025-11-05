import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { Search } from 'lucide-react'
import './Devices.css'
import './shared.css'

const Devices: React.FC = () => {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [deviceType, setDeviceType] = useState('')
  const [os, setOs] = useState('')

  const { data: devices = [], isLoading, error } = useQuery({
    queryKey: ['devices', search, deviceType, os],
    queryFn: async () => {
      try {
        const params: any = { limit: 100 }
        if (search) params.search = search
        if (deviceType) params.device_type = deviceType
        if (os) params.os = os
        const res = await api.get('/devices/', { params })
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load devices:', error)
        return []
      }
    },
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="devices-page">
        <div className="page-header">
          <h1>Device Inventory</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="devices-page">
      <div className="page-header">
        <h1>Device Inventory</h1>
      </div>

      {error && (
        <div className="error-message">
          Failed to load devices: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      <div className="filters">
        <div className="filter-group">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search devices..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select value={deviceType} onChange={(e) => setDeviceType(e.target.value)}>
          <option value="">All Types</option>
          <option value="server">Server</option>
          <option value="workstation">Workstation</option>
          <option value="router">Router</option>
          <option value="switch">Switch</option>
          <option value="printer">Printer</option>
          <option value="iot">IoT Device</option>
        </select>
        <input
          type="text"
          placeholder="OS Filter"
          value={os}
          onChange={(e) => setOs(e.target.value)}
        />
      </div>

      {devices.length === 0 ? (
        <div className="empty-state">No devices found. Run a scan to discover devices.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Device Type</th>
                <th>OS</th>
                <th>Hostname</th>
                <th>MAC Address</th>
                <th>First Seen</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device: any) => (
                <tr
                  key={device.ip_address}
                  onClick={() => navigate(`/devices/${device.ip_address}`)}
                  className="clickable-row"
                >
                  <td>{device.ip_address || 'N/A'}</td>
                  <td>{device.device_type || 'Unknown'}</td>
                  <td>{device.os || 'Unknown'}</td>
                  <td>{device.hostname || 'N/A'}</td>
                  <td>{device.mac_address || 'N/A'}</td>
                  <td>{device.first_seen ? new Date(device.first_seen).toLocaleDateString() : 'N/A'}</td>
                  <td>{device.last_seen ? new Date(device.last_seen).toLocaleDateString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Devices
