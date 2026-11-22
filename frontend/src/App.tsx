import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchHealth, fetchMe, logout } from './api'
import Login from './Login'

function App() {
  const queryClient = useQueryClient()
  const me = useQuery({ queryKey: ['me'], queryFn: fetchMe })
  const health = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    enabled: me.data?.authenticated === true,
  })
  const logoutMutation = useMutation({
    mutationFn: logout,
    // Drop all cached data and refetch, so nothing from the session lingers.
    onSuccess: () => queryClient.resetQueries(),
  })

  if (me.isPending) return <main>Loading…</main>
  if (me.isError) {
    return (
      <main>
        <p role="alert">Can't reach the server: {me.error.message}</p>
      </main>
    )
  }
  if (!me.data.authenticated) return <Login />

  return (
    <main>
      <h1>Cooking Hub</h1>
      {me.data.auth_enabled && (
        <button type="button" onClick={() => logoutMutation.mutate()}>
          Log out
        </button>
      )}
      {health.isPending && <p>Checking API…</p>}
      {health.isError && <p role="alert">API unreachable: {health.error.message}</p>}
      {health.isSuccess && (
        <p>
          API: {health.data.status} / DB: {health.data.database}
        </p>
      )}
    </main>
  )
}

export default App
