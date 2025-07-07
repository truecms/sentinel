import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<div>Landing Page Works!</div>} />
        <Route path="/features" element={<div>Features Page Works!</div>} />
        <Route path="/pricing" element={<div>Pricing Page Works!</div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App