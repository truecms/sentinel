import { BrowserRouter, Routes, Route } from 'react-router-dom'

function SimpleApp() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
        <header style={{ backgroundColor: 'white', padding: '1rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h1>Sentinel - Drupal Security Monitoring</h1>
        </header>
        <Routes>
          <Route path="/" element={
            <main style={{ padding: '2rem' }}>
              <h2>Welcome to Sentinel</h2>
              <p>Monitor your Drupal sites' security with confidence.</p>
              <button style={{ backgroundColor: '#3b82f6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>
                Get Started
              </button>
            </main>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default SimpleApp