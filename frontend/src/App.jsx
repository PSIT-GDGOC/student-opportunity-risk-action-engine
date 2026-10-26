import { useState } from 'react'
import './App.css'

// Risk levels are sample values; this component displays them rather than calculating risk.
const opportunities = [
  { title: 'Google Summer Internship', company: 'Google', type: 'Internship', deadline: '2026-10-24', status: 'In progress', risk: 'High', reason: 'Application is still in progress and needs immediate attention.', icon: 'G' },
  { title: 'Software Engineer Intern', company: 'Microsoft', type: 'Internship', deadline: '2026-10-29', status: 'Not started', risk: 'Medium', reason: 'Application has not been started and the deadline is approaching.', icon: 'M' },
  { title: 'Amazon ML Summer School', company: 'Amazon', type: 'Program', deadline: '2026-11-08', status: 'In progress', risk: 'Low', reason: 'Application is underway with time remaining before the deadline.', icon: 'a' },
]

function deadlineDetails(dateString, now = new Date()) {
  const [year, month, day] = dateString.split('-').map(Number)
  const deadlineUTC = Date.UTC(year, month - 1, day)
  const todayUTC = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())
  const days = Math.round((deadlineUTC - todayUTC) / 86400000)
  if (days < 0) return { text: `${Math.abs(days)} day${days === -1 ? '' : 's'} overdue`, overdue: true }
  if (days === 0) return { text: 'Due today', overdue: false }
  return { text: `${days} day${days === 1 ? '' : 's'} left`, overdue: false }
}

function App() {
  const [active, setActive] = useState('Overview')
  const [search, setSearch] = useState('')
  const [tasks, setTasks] = useState([
    { id: 1, text: 'Update resume with latest projects', done: true },
    { id: 2, text: 'Practice 2 DSA problems', done: false },
    { id: 3, text: 'Prepare internship application', done: false },
  ])

  const filtered = opportunities.filter(item =>
    `${item.title} ${item.company}`.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview">
          <span className="brand-mark">S</span>
          <span>PathPilot<small>STUDENT SUCCESS ENGINE</small></span>
        </a>

        <p className="nav-label">WORKSPACE</p>
        {[
          ['Overview', '▦'],
          ['Opportunities', '◇'],
          ['My Applications', '▤'],
          ['Action Planner', '✓'],
        ].map(([name, icon]) => (
          <button key={name} className={`nav-item ${active === name ? 'active' : ''}`}
            onClick={() => setActive(name)}>
            <span>{icon}</span>{name}
          </button>
        ))}

        <div className="sidebar-bottom">
          <div className="help-card">
            <span className="help-icon">✦</span>
            <strong>Stay one step ahead</strong>
            <p>Small actions today lead to bigger opportunities tomorrow.</p>
          </div>
          <div className="profile">
            <div className="avatar">S</div>
            <div><strong>Student Workspace</strong><small>Career explorer</small></div>
            <span className="profile-dots">···</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {active}</div>
          <div className="top-actions">
            <span className="today-label">✦ Your next step starts here</span>
            <button className="icon-button" aria-label="Notifications">♧<i /></button>
          </div>
        </header>

        <div className="content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">YOUR PERSONAL CAREER COMPASS</p>
              <h1>{active === 'Overview' ? 'Make your next move count.' : active}</h1>
              <p className="subtitle">Turn your goals into a plan, and your plan into progress.</p>
            </div>
            <button className="primary-button" onClick={() => setActive('Opportunities')}>＋ Explore opportunities</button>
          </section>

          <section className="hero-banner">
            <div className="hero-copy">
              <span className="banner-tag">✦ YOUR WEEKLY CHECK-IN</span>
              <h2>Your future is built<br />one action at a time.</h2>
              <p>Keep track of deadlines, spot risks early, and focus on what matters next.</p>
              <button onClick={() => setActive('Action Planner')}>View my action plan <span>→</span></button>
            </div>
            <div className="hero-art" aria-hidden="true">
              <div className="orbit orbit-one" />
              <div className="orbit orbit-two" />
              <div className="art-card card-back">↗<small>YOUR GROWTH</small></div>
              <div className="art-card card-front"><span>✦</span><strong>Progress</strong><div className="progress-track"><i /></div><small>Keep going!</small></div>
              <div className="art-star">✳</div>
            </div>
          </section>

          <section className="stats-grid">
            <article className="stat-card"><div className="stat-top"><span>Tracked opportunities</span><span className="stat-icon lavender">◇</span></div><strong>12</strong><p><span className="positive">+3</span> added this month</p></article>
            <article className="stat-card"><div className="stat-top"><span>Applications in progress</span><span className="stat-icon mint">↗</span></div><strong>05</strong><p>Keep your momentum going</p></article>
            <article className="stat-card"><div className="stat-top"><span>Upcoming deadlines</span><span className="stat-icon peach">◷</span></div><strong>03</strong><p><span className="warning-text">1 needs attention</span></p></article>
            <article className="stat-card"><div className="stat-top"><span>Tasks completed</span><span className="stat-icon blue">✓</span></div><strong>{tasks.filter(t => t.done).length}/3</strong><p>Your consistency is building</p></article>
          </section>

          <section className="dashboard-grid">
            <article className="panel opportunity-panel">
              <div className="panel-heading"><div><h3>Priority opportunities</h3><p>Keep the best-fit opportunities on your radar.</p></div><button className="text-button" onClick={() => setActive('Opportunities')}>View all →</button></div>
              <div className="search-box"><span>⌕</span><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search opportunities..." aria-label="Search opportunities" /></div>
              <div className="opportunity-list">
                {filtered.map(item => {
                  const deadline = deadlineDetails(item.deadline)
                  return (
                    <div className="opportunity" key={item.title}>
                      <div className={`company-icon company-${item.icon.toLowerCase()}`}>{item.icon}</div>
                      <div className="opportunity-info">
                        <strong>{item.title}</strong>
                        <p>{item.company} <span>·</span> {item.type}</p>
                        <small>Deadline: {new Date(`${item.deadline}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</small>
                        <p className="application-status"><b>Application:</b> {item.status}</p>
                        <p className="risk-reason"><b>Why {item.risk.toLowerCase()} risk:</b> {item.reason}</p>
                      </div>
                      <div className="opportunity-meta">
                        <span className={`risk risk-${item.risk.toLowerCase()}`}>{item.risk} risk</span>
                        <small className={deadline.overdue ? 'deadline-overdue' : ''}>{deadline.text}</small>
                      </div>
                    </div>
                  )
                })}
                {filtered.length === 0 && <p className="empty-state">No matching opportunities found.</p>}
              </div>
            </article>

            <article className="panel action-panel">
              <div className="panel-heading"><div><h3>Your action plan</h3><p>A few focused steps go a long way.</p></div><span className="action-count">{tasks.filter(t => t.done).length}/3</span></div>
              <div className="task-list">
                {tasks.map(task => (
                  <label className={`task ${task.done ? 'task-done' : ''}`} key={task.id}>
                    <input type="checkbox" checked={task.done} onChange={() => setTasks(old => old.map(t => t.id === task.id ? { ...t, done: !t.done } : t))} />
                    <span className="custom-check">{task.done ? '✓' : ''}</span>
                    <span>{task.text}</span>
                  </label>
                ))}
              </div>
              <div className="risk-alert"><span>✦</span><div><strong>One thing to focus on</strong><p>Start early on applications with approaching deadlines to reduce last-minute stress.</p></div></div>
              <button className="outline-button" onClick={() => setActive('Action Planner')}>Open action planner →</button>
            </article>
          </section>

          <footer className="footer"><span>PathPilot <b>·</b> Built for student growth</span><span>Plan smarter. Move forward. <b>✦</b></span></footer>
        </div>
      </main>
    </div>
  )
}

export default App
