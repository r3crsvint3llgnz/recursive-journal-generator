import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

const AppShell = ({ children, user, onSignOut }) => {
  return (
    <div className="app-shell">
      <header>
        <div>
          <strong>Recursive Journal Generator</strong>
          <div style={{ fontSize: '0.9rem', color: '#cbd5f5' }}>
            Signed in as {user?.username || user?.attributes?.email}
          </div>
        </div>
        <nav>
          <NavLink to="/app">Workspace</NavLink>
          <NavLink to="/settings">Settings</NavLink>
          <button className="button" onClick={onSignOut} type="button">
            Sign out
          </button>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  )
}

AppShell.propTypes = {
  children: PropTypes.node.isRequired,
  user: PropTypes.shape({
    username: PropTypes.string,
    attributes: PropTypes.object
  }),
  onSignOut: PropTypes.func.isRequired
}

export default AppShell
