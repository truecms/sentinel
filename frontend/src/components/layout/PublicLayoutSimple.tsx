import { Outlet } from 'react-router-dom';

const PublicLayoutSimple = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Sentinel</h1>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default PublicLayoutSimple;