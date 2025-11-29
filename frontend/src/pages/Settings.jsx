const Settings = () => {
  return (
    <div className="grid">
      <section className="card">
        <h2>Data Controls</h2>
        <p>Expose toggles for retaining raw transcripts vs. summary-only storage.</p>
        <button className="button" type="button">
          Request Data Export
        </button>
      </section>
      <section className="card">
        <h2>Connected Services</h2>
        <ul>
          <li>Obsidian Sync – pending</li>
          <li>Pocket / PKM Webhooks – backlog</li>
        </ul>
      </section>
    </div>
  )
}

export default Settings
