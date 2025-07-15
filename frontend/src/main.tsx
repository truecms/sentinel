import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './app/store'
import { AuthProvider } from './components/auth/AuthProvider'
import { setupInterceptors } from './app/api/interceptors'
import { apiClient } from './utils/api'
import './index.css'
import App from './App.tsx'

// Setup auth interceptors
setupInterceptors(apiClient);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Provider>
  </StrictMode>,
)
