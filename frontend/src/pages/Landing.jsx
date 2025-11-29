import { Link } from 'react-router-dom'

const Landing = () => {
  return (
    <div className="app-shell" style={{ minHeight: '100vh', padding: '4rem 2rem' }}>
      <section className="card" style={{ maxWidth: '720px', margin: '0 auto' }}>
        <p style={{ letterSpacing: '0.2em', color: '#94a3b8', fontSize: '0.8rem' }}>
          MVP ROADMAP
        </p>
        <h1 style={{ fontSize: '2.5rem', margin: '0.5rem 0 1rem' }}>
          From chat transcripts to Obsidian-ready reflections.
        </h1>
        <p style={{ color: '#cbd5f5', lineHeight: 1.6 }}>
          Import your exported LLM conversations, chat with Bedrock-powered reflective models, and publish
          Markdown entries that sync with your vault.
        </p>
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
          <Link className="button primary" to="/app">
            Enter Workspace
          </Link>
          <a className="button" href="docs/PRODUCT_REQUIREMENTS.md" target="_blank" rel="noreferrer">
            View PRD
          </a>
        </div>
      </section>
    </div>
  )
}

export default Landing
