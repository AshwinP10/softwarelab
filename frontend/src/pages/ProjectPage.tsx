import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:5000'

const ProjectPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const location = useLocation()
  const navigate = useNavigate()

  // Try to get project metadata from navigation state if available
  const state = location.state as { name?: string; description?: string } | null
  const [name, setName] = useState<string | null>(state?.name ?? null)
  const [description, setDescription] = useState<string | null>(state?.description ?? null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resources, setResources] = useState<Array<any>>([])
  const [resLoading, setResLoading] = useState(false)
  const [resError, setResError] = useState<string | null>(null)
  const [quantities, setQuantities] = useState<{[key: string]: number}>({})
  const [actionLoading, setActionLoading] = useState<{[key: string]: boolean}>({})
  const [actionMessage, setActionMessage] = useState<string>('')
  const [members, setMembers] = useState<string[]>([])
  const [inviteUser, setInviteUser] = useState('')
  const [inviteMessage, setInviteMessage] = useState('')

  useEffect(() => {
    // if we have name/description from navigation state, no need to fetch
    if (name !== null && description !== null) return
    if (!projectId) return
    setLoading(true)
    const userId = localStorage.getItem('userId')
    if (!userId) {
      setError('Please log in first')
      setLoading(false)
      return
    }
    
    fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}?userId=${encodeURIComponent(userId)}`)
      .then(async res => {
        if (res.status === 404) throw new Error('Project not found')
        if (res.status === 403) throw new Error('Access denied - you are not a member of this project')
        if (!res.ok) throw new Error('Failed to fetch project')
        return res.json()
      })
      .then(data => {
        setName(data.name)
        setDescription(data.description)
      })
      .catch(err => setError(String(err)))
      .finally(() => setLoading(false))
  }, [projectId])

  useEffect(() => {
    if (!projectId) return
    const userId = localStorage.getItem('userId')
    if (!userId) {
      setResError('Please log in first')
      return
    }
    
    setResLoading(true)
    setResError(null)
    fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}/resources?userId=${encodeURIComponent(userId)}`)
      .then(async res => {
        if (res.status === 403) throw new Error('Access denied - you are not a member of this project')
        if (!res.ok) throw new Error('Failed to fetch resources')
        return res.json()
      })
      .then(data => setResources(data))
      .catch(err => setResError(String(err)))
      .finally(() => setResLoading(false))
  }, [projectId])

  const handleHardwareAction = async (hwsetId: string, action: 'checkout' | 'checkin') => {
    const quantity = quantities[hwsetId] || 1
    const userId = localStorage.getItem('userId')
    
    if (!userId) {
      setActionMessage('Please log in first')
      return
    }
    
    if (quantity <= 0) {
      setActionMessage('Quantity must be greater than 0')
      return
    }
    
    setActionLoading(prev => ({...prev, [hwsetId]: true}))
    setActionMessage('')
    
    try {
      const res = await fetch(`${API_BASE}/api/projects/${projectId}/resources/${hwsetId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity, userId })
      })
      
      const data = await res.json()
      if (!res.ok) {
        setActionMessage(data.error || `${action} failed`)
        return
      }
      
      setActionMessage(data.message)
      // Refresh resources to show updated quantities
      setResLoading(true)
      const refreshRes = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId!)}/resources?userId=${encodeURIComponent(userId)}`)
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json()
        setResources(refreshData)
      }
      setResLoading(false)
      
      // Clear the quantity input
      setQuantities(prev => ({...prev, [hwsetId]: 1}))
      
    } catch (err) {
      setActionMessage(`Network error during ${action}`)
    } finally {
      setActionLoading(prev => ({...prev, [hwsetId]: false}))
    }
  }

  const refreshResources = async () => {
    if (!projectId) return
    setResLoading(true)
    setResError(null)
    try {
      const userId = localStorage.getItem('userId')
      if (userId) {
        const res = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId!)}/resources?userId=${encodeURIComponent(userId)}`)
        if (res.ok) {
          const data = await res.json()
          setResources(data)
        }
      }
    } catch (err) {
      setResError('Failed to refresh resources')
    } finally {
      setResLoading(false)
    }
  }

  const fetchMembers = async () => {
    if (!projectId) return
    const userId = localStorage.getItem('userId')
    if (!userId) return
    
    try {
      const res = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}/members?userId=${encodeURIComponent(userId)}`)
      if (res.ok) {
        const data = await res.json()
        setMembers(data.members || [])
      }
    } catch (err) {
      console.error('Failed to fetch members:', err)
    }
  }

  const handleInviteUser = async () => {
    if (!inviteUser.trim() || !projectId) return
    
    const userId = localStorage.getItem('userId')
    if (!userId) {
      setInviteMessage('Please log in first')
      return
    }
    
    try {
      const res = await fetch(`${API_BASE}/api/projects/${encodeURIComponent(projectId)}/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requestingUser: userId,
          inviteUser: inviteUser.trim()
        })
      })
      
      const data = await res.json()
      if (res.ok) {
        setInviteMessage(data.message)
        setInviteUser('')
        fetchMembers() // Refresh members list
      } else {
        setInviteMessage(data.error || 'Failed to invite user')
      }
    } catch (err) {
      setInviteMessage('Network error during invite')
    }
  }

  // Fetch members when component loads
  useEffect(() => {
    fetchMembers()
  }, [projectId])

  return (
    <div style={{display: 'grid', gap: 20}}>
      <section className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <h2>{name ?? `Project ${projectId}`}</h2>
            <div className="subtitle">ID: {projectId}</div>
            {loading ? <p>Loading...</p> : <p style={{color: 'var(--muted)'}}>{description ?? 'No description provided.'}</p>}
            {error && <div style={{color: 'salmon'}}>Error: {error}</div>}
          </div>
          <div>
            <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
          </div>
        </div>
      </section>

      <section className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <h2>Project Resources (Hardware Sets)</h2>
          <button onClick={refreshResources} disabled={resLoading}>
            {resLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        
        {actionMessage && (
          <div style={{
            padding: '8px 12px', 
            marginBottom: '12px',
            backgroundColor: actionMessage.includes('error') || actionMessage.includes('failed') ? '#ffebee' : '#e8f5e8',
            color: actionMessage.includes('error') || actionMessage.includes('failed') ? '#c62828' : '#2e7d32',
            borderRadius: '4px'
          }}>
            {actionMessage}
          </div>
        )}
        
        {resLoading && <div>Loading resources...</div>}
        {resError && <div style={{color: 'salmon'}}>Error: {resError}</div>}
        {!resLoading && !resError && (
          <div className="hwsets">
            {resources.map((r: any) => (
              <div className="hw card" key={r.hwsetId}>
                <h3>{r.name} ({r.hwsetId})</h3>
                <p><strong>Total:</strong> {r.total}</p>
                <p><strong>Allocated to project:</strong> {r.allocatedToProject}</p>
                <p><strong>Available:</strong> {r.available}</p>
                <div className="row">
                  <input 
                    type="number" 
                    min="1" 
                    max={Math.max(r.available, r.allocatedToProject)} 
                    placeholder="Quantity"
                    value={quantities[r.hwsetId] || 1}
                    onChange={e => setQuantities(prev => ({
                      ...prev, 
                      [r.hwsetId]: parseInt(e.target.value) || 1
                    }))}
                  />
                  <button 
                    onClick={() => handleHardwareAction(r.hwsetId, 'checkout')}
                    disabled={actionLoading[r.hwsetId] || r.available === 0}
                  >
                    {actionLoading[r.hwsetId] ? 'Processing...' : 'Checkout'}
                  </button>
                  <button 
                    className="secondary"
                    onClick={() => handleHardwareAction(r.hwsetId, 'checkin')}
                    disabled={actionLoading[r.hwsetId] || r.allocatedToProject === 0}
                  >
                    {actionLoading[r.hwsetId] ? 'Processing...' : 'Check In'}
                  </button>
                </div>
                {r.notes && <div className="note" style={{marginTop: '8px', fontSize: '0.9em', color: 'var(--muted)'}}>{r.notes}</div>}
              </div>
            ))}
            {resources.length === 0 && <div>No resources found for this project.</div>}
          </div>
        )}
      </section>

      <section className="card">
        <h2>Project Members</h2>
        <div style={{marginBottom: '16px'}}>
          <h4>Current Members ({members.length})</h4>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px'}}>
            {members.map(member => (
              <span key={member} style={{
                padding: '4px 8px',
                backgroundColor: 'var(--accent-bg)',
                borderRadius: '4px',
                fontSize: '0.9em'
              }}>
                {member}
              </span>
            ))}
            {members.length === 0 && <span style={{color: 'var(--muted)'}}>No members found</span>}
          </div>
        </div>
        
        <div>
          <h4>Invite User to Project</h4>
          <div className="row" style={{marginBottom: '8px'}}>
            <input 
              placeholder="Enter userId to invite"
              value={inviteUser}
              onChange={e => setInviteUser(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleInviteUser()}
            />
            <button onClick={handleInviteUser} disabled={!inviteUser.trim()}>
              Invite User
            </button>
          </div>
          {inviteMessage && (
            <div style={{
              padding: '8px 12px',
              backgroundColor: inviteMessage.includes('error') || inviteMessage.includes('Failed') ? '#ffebee' : '#e8f5e8',
              color: inviteMessage.includes('error') || inviteMessage.includes('Failed') ? '#c62828' : '#2e7d32',
              borderRadius: '4px',
              fontSize: '0.9em'
            }}>
              {inviteMessage}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default ProjectPage
