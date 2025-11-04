import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './Agents.css'

const Agents: React.FC = () => {
  const { data: agents = [] } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await api.get('/agents/')
      return res.data
    },
  })

  return (
    <div className="agents-page">
      <div className="page-header">
        <h1>Discovery Agents</h1>
      </div>

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
                <td>{agent.id.substring(0, 8)}...</td>
                <td>{agent.hostname || 'N/A'}</td>
                <td>{agent.platform || 'Unknown'}</td>
                <td>{agent.version || 'N/A'}</td>
                <td>
                  <span className={`status-badge status-${agent.status}`}>
                    {agent.status}
                  </span>
                </td>
                <td>{agent.last_seen ? new Date(agent.last_seen).toLocaleString() : 'Never'}</td>
                <td>{agent.scan_count || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Agents
