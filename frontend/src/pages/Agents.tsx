import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './Agents.css'
import './shared.css'

const Agents: React.FC = () => {
  const { data: agents = [], isLoading, error } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      try {
        const res = await api.get('/agents/')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load agents:', error)
        return []
      }
    },
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="agents-page">
        <div className="page-header">
          <h1>Discovery Agents</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="agents-page">
      <div className="page-header">
        <h1>Discovery Agents</h1>
      </div>

      {error && (
        <div className="error-message">
          Failed to load agents: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {agents.length === 0 ? (
        <div className="empty-state">No discovery agents registered. Install an agent to get started.</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Agent ID</th>
                <th>Hostname</th>
                <th>Platform</th>
                <th>Version</th>
                <th>Status</th>
                <th>Last Seen</th>
                <th>Scans Run</th>
              </tr>
            </thead>
            <tbody>
              {agents.map((agent: any) => (
                <tr key={agent.id}>
                  <td>{agent.id?.substring(0, 8) || 'N/A'}...</td>
                  <td>{agent.hostname || 'N/A'}</td>
                  <td>{agent.platform || 'Unknown'}</td>
                  <td>{agent.version || 'N/A'}</td>
                  <td>
                    <span className={`status-badge status-${agent.status || 'unknown'}`}>
                      {agent.status || 'unknown'}
                    </span>
                  </td>
                  <td>{agent.last_seen ? new Date(agent.last_seen).toLocaleString() : 'Never'}</td>
                  <td>{agent.scan_count || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Agents
