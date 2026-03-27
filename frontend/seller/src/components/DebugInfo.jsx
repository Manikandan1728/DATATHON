import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useLocation } from 'react-router-dom'

const DebugInfo = () => {
  const { user, isAuthenticated, loading } = useAuth()
  const location = useLocation()

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs max-w-xs z-50">
      <div><strong>Current Path:</strong> {location.pathname}</div>
      <div><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</div>
      <div><strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</div>
      <div><strong>User:</strong> {user ? user.email : 'None'}</div>
    </div>
  )
}

export default DebugInfo
