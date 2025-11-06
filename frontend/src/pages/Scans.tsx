import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { Plus, Play, Trash2 } from 'lucide-react'
import './Scans.css'
import './shared.css'

const Scans: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    targets: '',
    scan_type: 'port_scan',
    scanner: 'nmap',
    ports: '',
    timeout: 300,
  })

  const { data: scans = [], isLoading, error } = useQuery({
    queryKey: ['scans'],
    queryFn: async () => {
      try {
        const res = await api.get('/scans/')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load scans:', error)
        return []
      }
    },
    retry: 1,
  })

  const createScan = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/scans/', {
        targets: data.targets.split(/[,\n]/).map((t: string) => t.trim()).filter(Boolean),
        scan_type: data.scan_type,
        scanner: data.scanner,
        ports: data.ports ? data.ports.split(',').map((p: string) => parseInt(p.trim())).filter(Boolean) : null,
        timeout: parseInt(data.timeout),
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scans'] })
      setShowCreateModal(false)
      setFormData({ targets: '', scan_type: 'port_scan', scanner: 'nmap', ports: '', timeout: 300 })
    },
    onError: (error: any) => {
      console.error('Failed to create scan:', error)
      let errorMessage = 'Unknown error occurred'
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail)
      } else if (error.message) {
        errorMessage = error.message
      } else if (typeof error === 'string') {
        errorMessage = error
      }
      alert(`Failed to create scan: ${errorMessage}`)
    },
  })

  const cancelScan = useMutation({
    mutationFn: async (scanId: string) => {
      await api.delete(`/scans/${scanId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scans'] })
    },
    onError: (error: any) => {
      console.error('Failed to cancel scan:', error)
      alert(`Failed to cancel scan: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createScan.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="scans-page">
        <div className="page-header">
          <h1>Network Scans</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="scans-page">
      <div className="page-header">
        <h1>Network Scans</h1>
        <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          New Scan
        </button>
      </div>

      {error && (
        <div className="error-message">
          Failed to load scans: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Scan</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Targets (IP addresses or CIDR blocks, one per line)</label>
                <textarea
                  value={formData.targets}
                  onChange={(e) => setFormData({ ...formData, targets: e.target.value })}
                  placeholder="192.168.1.0/24&#10;10.0.0.1"
                  rows={4}
                  required
                />
              </div>
              <div className="form-group">
                <label>Scan Type</label>
                <select
                  value={formData.scan_type}
                  onChange={(e) => setFormData({ ...formData, scan_type: e.target.value })}
                >
                  <option value="port_scan">Port Scan</option>
                  <option value="ping_sweep">Ping Sweep</option>
                  <option value="service_detection">Service Detection</option>
                  <option value="os_detection">OS Detection</option>
                </select>
              </div>
              <div className="form-group">
                <label>Scanner</label>
                <select
                  value={formData.scanner}
                  onChange={(e) => setFormData({ ...formData, scanner: e.target.value })}
                >
                  <option value="nmap">Nmap</option>
                  <option value="masscan">Masscan</option>
                </select>
              </div>
              <div className="form-group">
                <label>Ports (comma-separated, optional)</label>
                <input
                  type="text"
                  value={formData.ports}
                  onChange={(e) => setFormData({ ...formData, ports: e.target.value })}
                  placeholder="80,443,22,3389"
                />
              </div>
              <div className="form-group">
                <label>Timeout (seconds)</label>
                <input
                  type="number"
                  value={formData.timeout}
                  onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
                  min="60"
                  max="3600"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={createScan.isPending}>
                  {createScan.isPending ? 'Creating...' : 'Start Scan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {scans.length === 0 ? (
        <div className="empty-state">No scans found. Create your first scan to get started.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Scan ID</th>
                <th>Targets</th>
                <th>Type</th>
                <th>Scanner</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan: any) => (
                <tr key={scan.scan_id}>
                  <td>
                    <button
                      className="link-button"
                      onClick={() => navigate(`/scans/${scan.scan_id}`)}
                    >
                      {scan.scan_id?.substring(0, 8) || 'N/A'}...
                    </button>
                  </td>
                  <td>{scan.targets?.length || 0} targets</td>
                  <td>{scan.scan_type || 'N/A'}</td>
                  <td>{scan.scanner || 'N/A'}</td>
                  <td>
                    <span className={`status-badge status-${scan.status || 'unknown'}`}>
                      {scan.status || 'unknown'}
                    </span>
                  </td>
                  <td>{scan.created_at ? new Date(scan.created_at).toLocaleString() : 'N/A'}</td>
                  <td>
                    <div className="action-buttons">
                      {scan.status === 'running' && (
                        <button
                          onClick={() => cancelScan.mutate(scan.scan_id)}
                          className="btn-icon"
                          title="Cancel"
                          disabled={cancelScan.isPending}
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Scans
