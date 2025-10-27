import React from 'react'
import { useNavigate } from 'react-router-dom'

const AuthPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <section className="card full-height">
      <h2>Sign Up / Login</h2>
      <p>Mock forms to illustrate auth flow.</p>
      <div className="row">
        <input placeholder="Email" />
        <input placeholder="Password" type="password" />
        <button onClick={() => navigate('/dashboard')}>Login</button>
      </div>
      <div className="row">
        <input placeholder="New Email" />
        <input placeholder="New Password" type="password" />
        <button onClick={() => navigate('/dashboard')}>Sign Up</button>
      </div>
    </section>
  )
}

export default AuthPage
