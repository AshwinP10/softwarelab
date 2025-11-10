import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:5000'

const AuthPage: React.FC = () => {
  const navigate = useNavigate()

  const [loginUserId, setLoginUserId] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [signupUserId, setSignupUserId] = useState('')
  const [signupPassword, setSignupPassword] = useState('')

  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // If already logged in, go straight to dashboard (helps with "state persists" later)
  useEffect(() => {
    const existing = localStorage.getItem('userId')
    if (existing) {
      navigate('/dashboard')
    }
  }, [navigate])

  const handleSignup = async () => {
    setError('')
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/api/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: signupUserId.trim(),
          password: signupPassword,
        }),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Sign up failed')
        return
      }

      setMessage('Sign up successful. You can now log in.')
      setSignupUserId('')
      setSignupPassword('')
    } catch (err) {
      setError('Network error during sign up')
    }
  }

  const handleLogin = async () => {
    setError('')
    setMessage('')
    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: loginUserId.trim(),
          password: loginPassword,
        }),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Login failed')
        return
      }

      // Persist simple auth state
      localStorage.setItem('userId', data.userId)
      navigate('/dashboard')
    } catch (err) {
      setError('Network error during login')
    }
  }

  return (
    <section className="card full-height">
      <h2>Sign Up / Login</h2>

      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      <div className="row">
        <h3>Login</h3>
        <input
          placeholder="User ID"
          value={loginUserId}
          onChange={(e) => setLoginUserId(e.target.value)}
        />
        <input
          placeholder="Password"
          type="password"
          value={loginPassword}
          onChange={(e) => setLoginPassword(e.target.value)}
        />
        <button onClick={handleLogin}>Login</button>
      </div>

      <div className="row">
        <h3>Sign Up</h3>
        <input
          placeholder="New User ID"
          value={signupUserId}
          onChange={(e) => setSignupUserId(e.target.value)}
        />
        <input
          placeholder="New Password"
          type="password"
          value={signupPassword}
          onChange={(e) => setSignupPassword(e.target.value)}
        />
        <button onClick={handleSignup}>Sign Up</button>
      </div>
    </section>
  )
}

export default AuthPage
