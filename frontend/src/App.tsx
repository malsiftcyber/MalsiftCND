import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Scans from './pages/Scans'
import ScanDetail from './pages/ScanDetail'
import Devices from './pages/Devices'
import DeviceDetail from './pages/DeviceDetail'
import Integrations from './pages/Integrations'
import EDR from './pages/EDR'
import Scheduling from './pages/Scheduling'
import Tagging from './pages/Tagging'
import Exports from './pages/Exports'
import Agents from './pages/Agents'
import Accuracy from './pages/Accuracy'
import Admin from './pages/Admin'
import Layout from './components/Layout'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="scans" element={<Scans />} />
        <Route path="scans/:scanId" element={<ScanDetail />} />
        <Route path="devices" element={<Devices />} />
        <Route path="devices/:ip" element={<DeviceDetail />} />
        <Route path="integrations" element={<Integrations />} />
        <Route path="edr" element={<EDR />} />
        <Route path="scheduling" element={<Scheduling />} />
        <Route path="tagging" element={<Tagging />} />
        <Route path="exports" element={<Exports />} />
        <Route path="agents" element={<Agents />} />
        <Route path="accuracy" element={<Accuracy />} />
        <Route path="admin" element={<Admin />} />
      </Route>
    </Routes>
  )
}

export default App

