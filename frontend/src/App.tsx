import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from './api'

function App() {
  const health = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  return (
    <main>
      <h1>Cooking Hub</h1>
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
