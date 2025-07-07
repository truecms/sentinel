function TestMinimal() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">
          Tailwind CSS Test
        </h1>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-4">
          <h2 className="text-2xl font-semibold mb-2">Card Component</h2>
          <p className="text-gray-600">
            This is a test card with Tailwind styles.
          </p>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-red-500 text-white p-4 rounded">Red Box</div>
          <div className="bg-green-500 text-white p-4 rounded">Green Box</div>
          <div className="bg-blue-500 text-white p-4 rounded">Blue Box</div>
        </div>
        
        <button className="mt-4 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
          Click Me
        </button>
      </div>
    </div>
  );
}

export default TestMinimal;