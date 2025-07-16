import { ToasterProps } from 'react-hot-toast';

export const toastConfig: ToasterProps = {
  position: 'top-right',
  toastOptions: {
    duration: 4000,
    style: {
      background: '#fff',
      color: '#363636',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    },
    className: 'dark:bg-gray-800 dark:text-white',
    success: {
      duration: 3000,
      iconTheme: {
        primary: '#10b981',
        secondary: '#fff',
      },
    },
    error: {
      duration: 5000,
      iconTheme: {
        primary: '#ef4444',
        secondary: '#fff',
      },
    },
    loading: {
      iconTheme: {
        primary: '#3b82f6',
        secondary: '#fff',
      },
    },
  },
};