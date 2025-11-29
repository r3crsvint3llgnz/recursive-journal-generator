import { useEffect, useState } from 'react'
import UploadPanel from '../components/UploadPanel.jsx'
import { listRecentImports } from '../lib/api.js'

const Dashboard = () => {
  const [recentImports, setRecentImports] = useState([])
  const [importStatus, setImportStatus] = useState('Ready to accept uploads.')

  const nextActions = [
    {
      title: 'Connect Amplify Backend',
      detail: 'Run `amplify init` and `amplify add auth` to provision Cognito + hosting environments.'
    },
    {
      title: 'Design Chat Surfaces',
      detail: 'Implement chat tabs for Imports, Live Journaling, and Insight summaries.'
    },
    {
      title: 'Hook Bedrock Models',
      detail: 'Call the journal-generation Lambda and mirror template contract for previews.'
    }
  ]

  const status = [
    { label: 'Auth', state: 'Not configured', description: 'Awaiting Amplify CLI push' },
    { label: 'Imports', state: 'S3 pipeline wired', description: 'Upload endpoint live' },
    { label: 'Templates', state: 'v1 available', description: 'Obsidian MD scaffold shipped' }
  ]

  useEffect(() => {
    refreshImports()
  }, [])

  const refreshImports = async () => {
    try {
      const data = await listRecentImports()
      setRecentImports(data)
      setImportStatus(data.length ? 'Showing most recent uploads.' : 'No uploads yet.')
    } catch (error) {
      setImportStatus(error.message)
    }
  }

  const handleUploadComplete = async () => {
    setImportStatus('Upload finished. Fetching status…')
    await refreshImports()
  }

  return (
    <div className="grid">
      <UploadPanel onUploadComplete={handleUploadComplete} />
      <section className="card">
        <h2>Recent Imports</h2>
        <p style={{ color: '#94a3b8' }}>{importStatus}</p>
        <ul>
          {recentImports.length === 0 && <li>No imports recorded yet.</li>}
          {recentImports.map((item) => (
            <li key={item.import_id} style={{ marginBottom: '0.75rem' }}>
              <strong>{item.title || 'Pending conversations'}</strong>
              <div style={{ color: '#94a3b8' }}>
                {item.import_id} • {item.status || 'processing'}
              </div>
            </li>
          ))}
        </ul>
      </section>
      <section className="card">
        <h2>Environment Checklist</h2>
        <ul>
          {status.map((item) => (
            <li key={item.label} style={{ marginBottom: '1rem' }}>
              <strong>{item.label}</strong>
              <div style={{ color: '#94a3b8' }}>{item.state}</div>
              <small style={{ color: '#94a3b8' }}>{item.description}</small>
            </li>
          ))}
        </ul>
      </section>
      <section className="card">
        <h2>Next Build Targets</h2>
        {nextActions.map((action) => (
          <article key={action.title} style={{ marginBottom: '1rem' }}>
            <strong>{action.title}</strong>
            <p style={{ color: '#cbd5f5' }}>{action.detail}</p>
          </article>
        ))}
      </section>
      <section className="card" style={{ gridColumn: '1 / -1' }}>
        <h2>Preview Pane</h2>
        <p style={{ color: '#94a3b8' }}>
          This area will soon render Markdown previews powered by the template engine. Use it to verify tag
          placement, YAML front matter, and transcript details before exporting to Obsidian.
        </p>
      </section>
    </div>
  )
}

export default Dashboard
