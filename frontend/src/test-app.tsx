import React from 'react'

function TestApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test App</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ marginTop: '20px' }}>
        <h2>Test Tailwind Classes:</h2>
        <p className="text-blue-500">This should be blue</p>
        <p className="bg-red-100 p-4 rounded">This should have red background</p>
        <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
          Test Button
        </button>
      </div>
    </div>
  )
}

export default TestApp