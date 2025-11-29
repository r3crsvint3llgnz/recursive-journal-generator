import PropTypes from 'prop-types'
import { Authenticator, View } from '@aws-amplify/ui-react'
import '@aws-amplify/ui-react/styles.css'
import AppShell from '../layout/AppShell.jsx'

const ProtectedRoute = ({ children }) => {
  return (
    <Authenticator socialProviders={['google']} hideSignUp={false} variation="modal">
      {({ signOut, user }) => (
        <AppShell user={user} onSignOut={signOut}>
          <View as="main">{children}</View>
        </AppShell>
      )}
    </Authenticator>
  )
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired
}

export default ProtectedRoute
