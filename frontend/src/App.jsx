import { Amplify } from 'aws-amplify'
import { Navigate, Route, Routes } from 'react-router-dom'
import awsExports from './aws-exports.js'
import Landing from './pages/Landing.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Settings from './pages/Settings.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

Amplify.configure(awsExports)

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
