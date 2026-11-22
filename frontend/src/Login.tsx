import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { UnauthorizedError, login } from './api'

function Login() {
  const queryClient = useQueryClient()
  const [password, setPassword] = useState('')
  const loginMutation = useMutation({
    mutationFn: login,
    // Re-check the session; App then swaps this screen for the real one.
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    loginMutation.mutate(password)
  }

  return (
    <main>
      <h1>Cooking Hub</h1>
      <form onSubmit={handleSubmit}>
        {/* A username field (hidden) plus current-password lets password managers save it. */}
        <input type="text" name="username" autoComplete="username" value="cooking-hub" hidden readOnly />
        <label htmlFor="password">Password</label>{' '}
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          autoFocus
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />{' '}
        <button type="submit" disabled={loginMutation.isPending}>
          {loginMutation.isPending ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      {loginMutation.isError && (
        <p role="alert">
          {loginMutation.error instanceof UnauthorizedError
            ? 'Wrong password.'
            : `Couldn't log in: ${loginMutation.error.message}`}
        </p>
      )}
    </main>
  )
}

export default Login
