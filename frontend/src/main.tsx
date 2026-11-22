import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { UnauthorizedError, type AuthStatus } from './api'

// Any 401 (e.g. the session expired) marks the user as logged out, which makes
// App show the login screen instead of a broken page.
function handleError(error: Error) {
  if (error instanceof UnauthorizedError) {
    queryClient.setQueryData<AuthStatus>(['me'], { authenticated: false, auth_enabled: true })
  }
}

// One shared cache for all server data. Components ask for data by key, and
// TanStack Query handles fetching, caching, retries and loading/error state.
const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: handleError }),
  mutationCache: new MutationCache({ onError: handleError }),
  defaultOptions: {
    // Retrying won't fix a 401, so only retry other failures.
    queries: { retry: (count, error) => !(error instanceof UnauthorizedError) && count < 3 },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
