import { BrowserRouter, Routes, Route } from 'react-router-dom'

function TestApp() {
  console.log('TestApp is rendering');
  
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1>Test App is Working!</h1>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <div>
              <h2>Home Page</h2>
              <p>If you can see this, routing is working!</p>
              <nav>
                <a href="/features" style={{ marginRight: '10px' }}>Features</a>
                <a href="/pricing">Pricing</a>
              </nav>
            </div>
          } />
          <Route path="/features" element={<div><h2>Features Page</h2></div>} />
          <Route path="/pricing" element={<div><h2>Pricing Page</h2></div>} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default TestApp