import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './Accuracy.css'

const Accuracy: React.FC = () => {
  const { data: rankings = [] } = useQuery({
    queryKey: ['accuracy-rankings'],
    queryFn: async () => {
      const res = await api.get('/accuracy/rankings')
      return res.data
    },
  })

  const chartData = rankings.map((ranking: any) => ({
    name: ranking.source_name,
    accuracy: ranking.accuracy_score,
    reliability: ranking.reliability_score,
  }))

  return (
    <div className="accuracy-page">
      <div className="page-header">
        <h1>Accuracy Rankings</h1>
      </div>

      <div className="chart-card">
        <h2>Data Source Accuracy</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="accuracy" fill="#667eea" name="Accuracy" />
            <Bar dataKey="reliability" fill="#764ba2" name="Reliability" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Accuracy Score</th>
              <th>Reliability Score</th>
              <th>Total Evaluations</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((ranking: any) => (
              <tr key={ranking.source_name}>
                <td>{ranking.source_name}</td>
                <td>{(ranking.accuracy_score * 100).toFixed(2)}%</td>
                <td>{(ranking.reliability_score * 100).toFixed(2)}%</td>
                <td>{ranking.total_evaluations || 0}</td>
                <td>{ranking.last_updated ? new Date(ranking.last_updated).toLocaleString() : 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Accuracy

