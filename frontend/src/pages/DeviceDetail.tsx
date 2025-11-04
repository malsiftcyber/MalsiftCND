import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './DeviceDetail.css'

const DeviceDetail: React.FC = () => {
  const { ip } = useParams<{ ip: string }>()

  const { data: device, isLoading } = useQuery({
    queryKey: ['device', ip],
    queryFn: async () => {
      const res = await api.get(`/devices/${ip}`)
      return res.data
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (!device) return <div>Device not found</div>

  return (
    <div className="device-detail">
      <h1>Device Details: {device.ip_address}</h1>

      <div className="device-info-grid">
        <div className="info-card">
          <h3>Basic Information</h3>
          <div className="info-row">
            <span className="info-label">IP Address:</span>
            <span>{device.ip_address}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Device Type:</span>
            <span>{device.device_type || 'Unknown'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Hostname:</span>
            <span>{device.hostname || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">MAC Address:</span>
            <span>{device.mac_address || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">OS:</span>
            <span>{device.os || 'Unknown'}</span>
          </div>
        </div>

        <div className="info-card">
          <h3>Discovery Information</h3>
          <div className="info-row">
            <span className="info-label">First Seen:</span>
            <span>{device.first_seen ? new Date(device.first_seen).toLocaleString() : 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Last Seen:</span>
            <span>{device.last_seen ? new Date(device.last_seen).toLocaleString() : 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Scan Count:</span>
            <span>{device.scan_count || 0}</span>
          </div>
        </div>
      </div>

      {device.ai_analysis && (
        <div className="info-card">
          <h3>AI Analysis</h3>
          <pre>{JSON.stringify(device.ai_analysis, null, 2)}</pre>
        </div>
      )}

      {device.ports && device.ports.length > 0 && (
        <div className="info-card">
          <h3>Open Ports</h3>
          <div className="ports-list">
            {device.ports.map((port: any, idx: number) => (
              <div key={idx} className="port-item">
                <span className="port-number">{port.port}</span>
                <span className="port-service">{port.service || 'Unknown'}</span>
                <span className="port-state">{port.state}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DeviceDetail
