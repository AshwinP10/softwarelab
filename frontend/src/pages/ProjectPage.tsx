import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'

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

  useEffect(() => {
    // if we have name/description from navigation state, no need to fetch
    if (name !== null && description !== null) return
    if (!projectId) return
    setLoading(true)
    fetch(`/api/projects/${encodeURIComponent(projectId)}`)
      .then(async res => {
        if (res.status === 404) throw new Error('Project not found')
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
    setResLoading(true)
    setResError(null)
    fetch(`/api/projects/${encodeURIComponent(projectId)}/resources`)
      .then(async res => {
        if (!res.ok) throw new Error('Failed to fetch resources')
        return res.json()
      })
      .then(data => setResources(data))
      .catch(err => setResError(String(err)))
      .finally(() => setResLoading(false))
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
        <h2>Project Resources (Hardware Sets)</h2>
        {resLoading && <div>Loading resources...</div>}
        {resError && <div style={{color: 'salmon'}}>Error: {resError}</div>}
        {!resLoading && !resError && (
          <div className="hwsets">
            {resources.map((r: any) => (
              <div className="hw card" key={r.hwsetId}>
                <h3>{r.name} ({r.hwsetId})</h3>
                <p>Total: {r.total}</p>
                <p>Allocated to project: {r.allocatedToProject}</p>
                <p>Available: {r.available}</p>
                <div className="row">
                  <input type="number" min="0" max={r.total} placeholder="Units" />
                  <button>Request</button>
                  <button className="secondary">Release</button>
                </div>
                {r.notes && <div className="note">{r.notes}</div>}
              </div>
            ))}
            {resources.length === 0 && <div>No resources found for this project.</div>}
          </div>
        )}
      </section>
    </div>
  )
}

export default ProjectPage
