import React from 'react'

export default function App() {
  return (
    <div className="container">
      <header className="header">
        <h1>HaaS Proof-of-Concept</h1>
        <p className="subtitle">Static prototype (React + TypeScript)</p>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Sign Up / Login</h2>
          <p>Mock forms to illustrate auth flow.</p>
          <div className="row">
            <input placeholder="Email" />
            <input placeholder="Password" type="password" />
            <button>Login</button>
          </div>
          <div className="row">
            <input placeholder="New Email" />
            <input placeholder="New Password" type="password" />
            <button>Sign Up</button>
          </div>
        </section>

        <section className="card">
          <h2>Projects</h2>
          <p>Create and view projects</p>
          <div className="row">
            <input placeholder="Project Name" />
            <input placeholder="Description" />
            <button>Create Project</button>
          </div>
          <ul className="list">
            <li>Project A — ID: P-001 — Example project</li>
            <li>Project B — ID: P-002 — Example project</li>
          </ul>
        </section>

        <section className="card">
          <h2>Hardware Sets</h2>
          <p>Capacity and availability</p>
          <div className="hwsets">
            <div className="hw card">
              <h3>HWSet1</h3>
              <p>Total: 10</p>
              <p>Available: 7</p>
              <div className="row">
                <input type="number" min="0" max="10" placeholder="Units" />
                <button>Check Out</button>
                <button className="secondary">Check In</button>
              </div>
            </div>
            <div className="hw card">
              <h3>HWSet2</h3>
              <p>Total: 20</p>
              <p>Available: 15</p>
              <div className="row">
                <input type="number" min="0" max="20" placeholder="Units" />
                <button>Check Out</button>
                <button className="secondary">Check In</button>
              </div>
            </div>
          </div>
          <div className="note">Global capacity shared across projects (read-only here).</div>
        </section>
      </main>

      <footer className="footer">
        <span>© {new Date().getFullYear()} HaaS PoC</span>
      </footer>
    </div>
  )
}
