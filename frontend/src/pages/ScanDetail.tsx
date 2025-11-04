import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './ScanDetail.css'

const ScanDetail: React.FC = () => {
  const { scanId } = useParams<{ scanId: string }>()

  const { data: scan } = useQuery({
    queryKey: ['scan', scanId],
    queryFn: async () => {
      const res = await api.get(`/scans/${scanId}`)
      return res.data
    },
  })

  const { data: results = [] } = useQuery({
    queryKey: ['scan-results', scanId],
    queryFn: async () => {
      const res = await api.get(`/scans/${scanId}/results`)
      return res.data
    },
  })

  if (!scan) return <div>Loading...</div>

  return (
    <div className="scan-detail">
      <h1>Scan Details</h1>
      
      <div className="scan-info">
        <div className="info-card">
          <h3>Scan Information</h3>
          <div className="info-row">
            <span className="info-label">Status:</span>
            <span className={`status-badge status-${scan.status}`}>{scan.status}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Scanner:</span>
            <span>{scan.scanner}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Type:</span>
            <span>{scan.scan_type}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Targets:</span>
            <span>{scan.targets?.join(', ') || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Created:</span>
            <span>{new Date(scan.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="results-section">
        <h2>Scan Results ({results.length})</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>IP Address</th>
                <th>Port</th>
                <th>Service</th>
                <th>State</th>
                <th>Product</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result: any, idx: number) => (
                <tr key={idx}>
                  <td>{result.ip_address}</td>
                  <td>{result.port}</td>
                  <td>{result.service || 'N/A'}</td>
                  <td>{result.state}</td>
                  <td>{result.product || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default ScanDetail
