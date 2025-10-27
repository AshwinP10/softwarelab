import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const DashboardPage: React.FC = () => {
  const navigate = useNavigate()

  // Create project form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [projectId, setProjectId] = useState('')

  // Get project by id state
  const [lookupId, setLookupId] = useState('')
  const [projects, setProjects] = useState<Array<any>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const handleCreate = async () => {
    setError(null)
    const idToUse = projectId || `proj-${Date.now()}`
    setCreating(true)
    try {
      const res = await fetch(`/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectId: idToUse, name, description }),
      })
      if (res.status === 409) {
        setError('Project ID already exists')
        return
      }
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.error || 'Failed to create project')
      }
      // navigate to the project page and pass the metadata
      navigate(`/project/${idToUse}`, { state: { name, description } })
    } catch (err: any) {
      console.error(err)
      setError(String(err.message || err))
    } finally {
      setCreating(false)
    }
  }

  const handleLookup = async () => {
    setError(null)
    if (!lookupId) {
      setError('Please enter a project ID')
      return
    }
    try {
      const res = await fetch(`/api/projects/${encodeURIComponent(lookupId)}`)
      if (res.status === 404) {
        setError('Project not found')
        return
      }
      if (!res.ok) throw new Error('Failed to load project')
      const data = await res.json()
      navigate(`/project/${lookupId}`, { state: { name: data.name, description: data.description } })
    } catch (err: any) {
      console.error(err)
      setError(String(err.message || err))
    }
  }

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetch('/api/projects')
      .then(async res => {
        if (!res.ok) throw new Error('Failed to fetch projects')
        return res.json()
      })
      .then(data => {
        if (!cancelled) setProjects(data)
      })
      .catch(err => {
        if (!cancelled) setError(String(err))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  return (
    <>
      <section className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <h2>Projects</h2>
          <button onClick={() => navigate('/')}>Log out</button>
        </div>
        <p>Create a new project or load by ID</p>

        <div style={{display: 'grid', gap: 12}}>
          <div className="card">
            <h3>Create Project</h3>
            <div className="row">
              <input placeholder="Project Name" value={name} onChange={e => setName(e.target.value)} />
              <input placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
              <input placeholder="Project ID" value={projectId} onChange={e => setProjectId(e.target.value)} />
              <button onClick={handleCreate}>Create Project</button>
            </div>
          </div>

          <div className="card">
            <h3>Get Project by ID</h3>
            <div className="row">
              <input placeholder="Project ID" value={lookupId} onChange={e => setLookupId(e.target.value)} />
              <button onClick={handleLookup}>Load Project</button>
            </div>
          </div>
        </div>

        {/* <div style={{marginTop: 12}}>
          <h4>Existing Projects</h4>
          {loading && <div>Loading projects...</div>}
          {error && <div style={{color: 'salmon'}}>Error: {error}</div>}
          <ul className="list">
            {projects.map((p: any) => (
              <li key={p.projectId} style={{cursor: 'pointer'}} onClick={() => navigate(`/project/${p.projectId}`)}>
                {p.name} — ID: {p.projectId} {p.description ? `— ${p.description}` : ''}
              </li>
            ))}
            {projects.length === 0 && !loading && <li>No projects found.</li>}
          </ul>
        </div> */}
      </section>

      {/* Hardware sets are shown on the project page. */}
    </>
  )
}

export default DashboardPage
