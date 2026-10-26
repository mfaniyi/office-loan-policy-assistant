import { useState } from 'react'
import { loginEmployee } from '../services/api'

interface EmployeeLoginProps {
  onLoginSuccess: (accessToken: string) => void
}

function EmployeeLogin({ onLoginSuccess }: EmployeeLoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!email.trim() || !password) {
      setError('Please enter your email and password.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await loginEmployee({
        email: email.trim(),
        password,
      })

      onLoginSuccess(response.access_token)
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Unable to sign in. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="login-container">
      <h2>Employee Login</h2>

      <p>
        Sign in to access your personalized loan assessment.
      </p>

      <form onSubmit={handleSubmit} className="login-form">
        <label htmlFor="employee-email">Email Address</label>

        <input
          id="employee-email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Enter your email"
          required
        />

        <label htmlFor="employee-password">Password</label>

        <input
          id="employee-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
          required
        />

        {error && (
          <p role="alert" className="error-message">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </section>
  )
}

export default EmployeeLogin