import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { Plus, Trash2 } from 'lucide-react'
import './Scheduling.css'
import './shared.css'

const Scheduling: React.FC = () => {
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    targets: '',
    scan_type: 'port_scan',
    scanner: 'nmap',
    frequency: 'daily',
    enabled: true,
  })

  const { data: schedules = [], isLoading, error } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      try {
        const res = await api.get('/scheduling/')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load schedules:', error)
        return []
      }
    },
    retry: 1,
  })

  const createSchedule = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/scheduling/', {
        name: data.name,
        targets: data.targets.split(/[,\n]/).map((t: string) => t.trim()).filter(Boolean),
        scan_type: data.scan_type,
        scanner: data.scanner,
        frequency: data.frequency,
        enabled: data.enabled,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      setShowCreateModal(false)
      setFormData({ name: '', targets: '', scan_type: 'port_scan', scanner: 'nmap', frequency: 'daily', enabled: true })
    },
    onError: (error: any) => {
      console.error('Failed to create schedule:', error)
      alert(`Failed to create schedule: ${error.response?.data?.detail || error.message}`)
    },
  })

  const deleteSchedule = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/scheduling/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
    },
    onError: (error: any) => {
      console.error('Failed to delete schedule:', error)
      alert(`Failed to delete schedule: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createSchedule.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="scheduling-page">
        <div className="page-header">
          <h1>Scan Scheduling</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="scheduling-page">
      <div className="page-header">
        <h1>Scan Scheduling</h1>
        <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          New Schedule
        </button>
      </div>

      {error && (
        <div className="error-message">
          Failed to load schedules: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create Scheduled Scan</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Schedule Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Targets</label>
                <textarea
                  value={formData.targets}
                  onChange={(e) => setFormData({ ...formData, targets: e.target.value })}
                  placeholder="192.168.1.0/24"
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
                </select>
              </div>
              <div className="form-group">
                <label>Frequency</label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={createSchedule.isPending}>
                  {createSchedule.isPending ? 'Creating...' : 'Create Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {schedules.length === 0 ? (
        <div className="empty-state">No scheduled scans configured. Create a schedule to get started.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Targets</th>
                <th>Type</th>
                <th>Frequency</th>
                <th>Status</th>
                <th>Next Run</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {schedules.map((schedule: any) => (
                <tr key={schedule.id}>
                  <td>{schedule.name || 'Unnamed'}</td>
                  <td>{schedule.targets?.length || 0} targets</td>
                  <td>{schedule.scan_type || 'N/A'}</td>
                  <td>{schedule.frequency || 'N/A'}</td>
                  <td>
                    <span className={`status-badge status-${schedule.enabled ? 'enabled' : 'disabled'}`}>
                      {schedule.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td>{schedule.next_run ? new Date(schedule.next_run).toLocaleString() : 'N/A'}</td>
                  <td>
                    <button
                      className="btn-icon"
                      onClick={() => deleteSchedule.mutate(schedule.id)}
                      disabled={deleteSchedule.isPending}
                    >
                      <Trash2 size={16} />
                    </button>
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

export default Scheduling
