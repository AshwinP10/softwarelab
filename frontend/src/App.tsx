import React, { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8001'

interface User {
  id: string
  email: string
}

interface Project {
  id: string
  name: string
  description: string
  user_id: string
  created_at: string
}

interface HardwareSet {
  id: string
  name: string
  total_capacity: number
  available_capacity: number
}

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [hardware, setHardware] = useState<HardwareSet[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  
  // Auth form states
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  
  // Project form states
  const [projectName, setProjectName] = useState('')
  const [projectDescription, setProjectDescription] = useState('')
  
  // Hardware form states
  const [checkoutQuantities, setCheckoutQuantities] = useState<{[key: string]: number}>({})
  const [checkinQuantities, setCheckinQuantities] = useState<{[key: string]: number}>({})
  
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || 'Request failed')
    }
    
    return response.json()
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      })
      
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
      setMessage('Logged in successfully!')
      setError('')
      setLoginEmail('')
      setLoginPassword('')
    } catch (err: any) {
      setError(err.message)
      setMessage('')
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await apiCall('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email: signupEmail, password: signupPassword })
      })
      
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
      setMessage('Account created successfully!')
      setError('')
      setSignupEmail('')
      setSignupPassword('')
    } catch (err: any) {
      setError(err.message)
      setMessage('')
    }
  }

  const handleGuestLogin = async () => {
    const guestEmail = 'demo@haas.com'
    const guestPassword = 'demo123'
    
    try {
      // Try to login first
      const data = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: guestEmail, password: guestPassword })
      })
      
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
      setMessage('Logged in as guest! Try checking out hardware below.')
      setError('')
    } catch (err: any) {
      // If login fails, create the guest account
      try {
        const signupData = await apiCall('/auth/signup', {
          method: 'POST',
          body: JSON.stringify({ email: guestEmail, password: guestPassword })
        })
        
        setToken(signupData.access_token)
        localStorage.setItem('token', signupData.access_token)
        
        // Create demo projects for the guest user
        setTimeout(async () => {
          try {
            const demoProject1 = await apiCall('/projects', {
              method: 'POST',
              body: JSON.stringify({ 
                name: 'Demo Project Alpha', 
                description: 'Sample project for testing hardware checkout' 
              })
            })
            
            await apiCall('/projects', {
              method: 'POST',
              body: JSON.stringify({ 
                name: 'Demo Project Beta', 
                description: 'Another sample project for demonstrations' 
              })
            })
            
            // Auto-select the first demo project
            setSelectedProject(demoProject1.id)
            loadProjects()
            setMessage('Guest account ready! Demo projects created. Try checking out hardware!')
          } catch (projectErr) {
            console.log('Could not create demo projects:', projectErr)
          }
        }, 500)
        
        setMessage('Created guest account with demo data!')
        setError('')
      } catch (signupErr: any) {
        setError('Failed to create guest account: ' + signupErr.message)
        setMessage('')
      }
    }
  }

  const handleLogout = () => {
    setToken(null)
    setUser(null)
    setProjects([])
    setHardware([])
    localStorage.removeItem('token')
    setMessage('Logged out successfully!')
  }

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const newProject = await apiCall('/projects', {
        method: 'POST',
        body: JSON.stringify({ name: projectName, description: projectDescription })
      })
      
      setMessage('Project created successfully!')
      setError('')
      setProjectName('')
      setProjectDescription('')
      
      // Auto-select the newly created project
      setSelectedProject(newProject.id)
      
      loadProjects()
    } catch (err: any) {
      setError(err.message)
      setMessage('')
    }
  }

  const handleCheckout = async (hardwareId: string) => {
    if (!selectedProject) {
      setError('Please select a project first')
      return
    }
    
    const quantity = checkoutQuantities[hardwareId] || 0
    if (quantity <= 0) {
      setError('Please enter a valid quantity')
      return
    }
    
    try {
      await apiCall('/hardware/checkout', {
        method: 'POST',
        body: JSON.stringify({
          hardware_set_id: hardwareId,
          project_id: selectedProject,
          quantity
        })
      })
      
      setMessage(`Checked out ${quantity} units successfully!`)
      setError('')
      setCheckoutQuantities({ ...checkoutQuantities, [hardwareId]: 0 })
      loadHardware()
    } catch (err: any) {
      setError(err.message)
      setMessage('')
    }
  }

  const handleCheckin = async (hardwareId: string) => {
    if (!selectedProject) {
      setError('Please select a project first')
      return
    }
    
    const quantity = checkinQuantities[hardwareId] || 0
    if (quantity <= 0) {
      setError('Please enter a valid quantity')
      return
    }
    
    try {
      await apiCall('/hardware/checkin', {
        method: 'POST',
        body: JSON.stringify({
          hardware_set_id: hardwareId,
          project_id: selectedProject,
          quantity
        })
      })
      
      setMessage(`Checked in ${quantity} units successfully!`)
      setError('')
      setCheckinQuantities({ ...checkinQuantities, [hardwareId]: 0 })
      loadHardware()
    } catch (err: any) {
      setError(err.message)
      setMessage('')
    }
  }

  const loadProjects = async () => {
    try {
      const data = await apiCall('/projects')
      setProjects(data)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const loadHardware = async () => {
    try {
      const data = await apiCall('/hardware')
      setHardware(data)
    } catch (err: any) {
      setError(err.message)
    }
  }

  useEffect(() => {
    if (token) {
      loadProjects()
      loadHardware()
    }
  }, [token])

  return (
    <div className="container">
      <header className="header">
        <h1>HaaS Proof-of-Concept</h1>
        <p className="subtitle">Hardware-as-a-Service System</p>
        {token && (
          <div className="auth-info">
            <span>Logged in</span>
            <button onClick={handleLogout} className="secondary">Logout</button>
          </div>
        )}
      </header>

      {message && <div className="message success">{message}</div>}
      {error && <div className="message error">{error}</div>}

      <main className="grid">
        {!token ? (
          <section className="card auth-section">
            <h2>Authentication Required</h2>
            
            <div className="guest-login">
              <button onClick={handleGuestLogin} className="guest-btn">
                🚀 Quick Demo Login (Guest)
              </button>
              <p className="guest-note">Skip signup and try the app instantly with demo data</p>
            </div>

            <div className="divider">
              <span>OR</span>
            </div>

            <div className="auth-forms">
              <form onSubmit={handleLogin} className="auth-form">
                <h3>Login</h3>
                <input 
                  type="email" 
                  placeholder="Email" 
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                />
                <input 
                  type="password" 
                  placeholder="Password" 
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                />
                <button type="submit">Login</button>
              </form>

              <form onSubmit={handleSignup} className="auth-form">
                <h3>Sign Up</h3>
                <input 
                  type="email" 
                  placeholder="Email" 
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  required
                />
                <input 
                  type="password" 
                  placeholder="Password" 
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  required
                />
                <button type="submit">Sign Up</button>
              </form>
            </div>
          </section>
        ) : (
          <>
            <section className="card">
              <h2>Projects</h2>
              <form onSubmit={handleCreateProject} className="project-form">
                <div className="row">
                  <input 
                    placeholder="Project Name" 
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    required
                  />
                  <input 
                    placeholder="Description" 
                    value={projectDescription}
                    onChange={(e) => setProjectDescription(e.target.value)}
                    required
                  />
                  <button type="submit">Create Project</button>
                </div>
              </form>
              
              <div className="project-selector">
                <label>Select Project for Hardware Operations:</label>
                <select 
                  value={selectedProject} 
                  onChange={(e) => setSelectedProject(e.target.value)}
                >
                  <option value="">-- Select Project --</option>
                  {projects.map(project => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <ul className="list">
                {projects.length === 0 ? (
                  <li>No projects yet. Create one above!</li>
                ) : (
                  projects.map(project => (
                    <li key={project.id}>
                      <strong>{project.name}</strong> — {project.description}
                      <br />
                      <small>ID: {project.id}</small>
                    </li>
                  ))
                )}
              </ul>
            </section>

            <section className="card hardware-section">
              <h2>🔧 Hardware Checkout System</h2>
              <p>Global capacity shared across all projects</p>
              
              {selectedProject ? (
                <div className="selected-project-info">
                  <strong>Active Project:</strong> {projects.find(p => p.id === selectedProject)?.name || 'Unknown'}
                </div>
              ) : (
                <div className="warning">
                  ⚠️ Select a project above to enable hardware checkout/checkin
                </div>
              )}
              
              <div className="hwsets">
                {hardware.map(hw => (
                  <div key={hw.id} className={`hw card ${!selectedProject ? 'disabled' : ''}`}>
                    <h3>{hw.name}</h3>
                    <div className="capacity-info">
                      <div className="capacity-bar">
                        <div 
                          className="capacity-used" 
                          style={{width: `${((hw.total_capacity - hw.available_capacity) / hw.total_capacity) * 100}%`}}
                        ></div>
                      </div>
                      <p>Available: <strong>{hw.available_capacity}</strong> / {hw.total_capacity} units</p>
                    </div>
                    
                    <div className="hw-actions">
                      <div className="action-group">
                        <label>Check Out Hardware:</label>
                        <div className="row">
                          <input 
                            type="number" 
                            min="1" 
                            max={hw.available_capacity}
                            placeholder="Qty"
                            value={checkoutQuantities[hw.id] || ''}
                            onChange={(e) => setCheckoutQuantities({
                              ...checkoutQuantities,
                              [hw.id]: parseInt(e.target.value) || 0
                            })}
                            disabled={!selectedProject}
                          />
                          <button 
                            onClick={() => handleCheckout(hw.id)}
                            disabled={!selectedProject || !checkoutQuantities[hw.id] || checkoutQuantities[hw.id] <= 0}
                            className="checkout-btn"
                          >
                            📤 Check Out
                          </button>
                        </div>
                      </div>
                      
                      <div className="action-group">
                        <label>Check In Hardware:</label>
                        <div className="row">
                          <input 
                            type="number" 
                            min="1"
                            placeholder="Qty"
                            value={checkinQuantities[hw.id] || ''}
                            onChange={(e) => setCheckinQuantities({
                              ...checkinQuantities,
                              [hw.id]: parseInt(e.target.value) || 0
                            })}
                            disabled={!selectedProject}
                          />
                          <button 
                            className="checkin-btn"
                            onClick={() => handleCheckin(hw.id)}
                            disabled={!selectedProject || !checkinQuantities[hw.id] || checkinQuantities[hw.id] <= 0}
                          >
                            📥 Check In
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <span>© {new Date().getFullYear()} HaaS PoC</span>
      </footer>
    </div>
  )
}
