# Frontend Setup Guide

This guide will help you set up the frontend development environment for the Monitoring Platform.

## Prerequisites

- Node.js 18+ and npm 9+
- Git
- Docker (for running the backend API locally)
- A code editor (VS Code recommended)

## Quick Start

### 1. Create Frontend Directory Structure

```bash
# From the project root
mkdir frontend
cd frontend
```

### 2. Initialize Vite Project

```bash
npm create vite@latest . -- --template react-ts
```

### 3. Install Core Dependencies

```bash
# Core dependencies
npm install react-router-dom@6 @reduxjs/toolkit react-redux axios
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install socket.io-client

# UI and styling
npm install tailwindcss@3 @headlessui/react @heroicons/react
npm install framer-motion react-grid-layout
npm install clsx tailwind-merge

# Charts and visualization
npm install recharts d3 @types/d3

# Form handling
npm install react-hook-form zod @hookform/resolvers

# Utilities
npm install date-fns lodash-es @types/lodash-es
npm install react-hot-toast

# Development dependencies
npm install -D @types/react @types/react-dom @types/node
npm install -D @vitejs/plugin-react vite-tsconfig-paths
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D vitest jsdom @vitest/ui
npm install -D postcss autoprefixer
npm install -D @types/react-grid-layout
```

### 4. Configure Tailwind CSS

Create `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

Create `postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Update `src/index.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
}
```

### 5. Configure Vite

Update `vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'redux-vendor': ['@reduxjs/toolkit', 'react-redux'],
          'ui-vendor': ['@headlessui/react', 'framer-motion', 'react-grid-layout'],
          'chart-vendor': ['recharts', 'd3'],
        },
      },
    },
  },
})
```

### 6. Update TypeScript Configuration

Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@features/*": ["./src/features/*"],
      "@utils/*": ["./src/utils/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@types/*": ["./src/types/*"],
      "@assets/*": ["./src/assets/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 7. Create Project Structure

```bash
# Create directory structure
mkdir -p src/{app,features,components,utils,hooks,types,assets,styles}
mkdir -p src/features/{auth,dashboard,organizations,sites,modules,reports}
mkdir -p src/components/{common,charts,layout,widgets}

# Create initial files
touch src/app/{store.ts,api.ts,hooks.ts}
touch src/utils/{constants.ts,helpers.ts,validators.ts}
touch src/types/{index.ts,api.ts,models.ts}
```

### 8. Set Up Redux Store

Create `src/app/store.ts`:
```typescript
import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { api } from './api'
import authReducer from '@/features/auth/authSlice'
import dashboardReducer from '@/features/dashboard/dashboardSlice'
import uiReducer from '@/features/ui/uiSlice'

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    auth: authReducer,
    dashboard: dashboardReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }).concat(api.middleware),
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

Create `src/app/hooks.ts`:
```typescript
import { useDispatch, useSelector } from 'react-redux'
import type { TypedUseSelectorHook } from 'react-redux'
import type { RootState, AppDispatch } from './store'

export const useAppDispatch: () => AppDispatch = useDispatch
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
```

### 9. Set Up API Client

Create `src/app/api.ts`:
```typescript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from './store'

const baseQuery = fetchBaseQuery({
  baseUrl: '/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token
    if (token) {
      headers.set('authorization', `Bearer ${token}`)
    }
    headers.set('X-API-Version', '1')
    return headers
  },
})

export const api = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['User', 'Organization', 'Site', 'Module', 'Dashboard', 'Report'],
  endpoints: (builder) => ({
    // Auth endpoints
    login: builder.mutation({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    
    // Add more endpoints as needed
  }),
})

export const {
  useLoginMutation,
  // Export more hooks as endpoints are added
} = api
```

### 10. Create Environment Configuration

Create `.env.development`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Monitoring Platform
VITE_APP_VERSION=1.0.0
```

Create `.env.production`:
```env
VITE_API_URL=/api/v1
VITE_WS_URL=/ws
VITE_APP_NAME=Monitoring Platform
VITE_APP_VERSION=1.0.0
```

### 11. Set Up ESLint

Create `.eslintrc.cjs`:
```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
    'prettier',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
}
```

### 12. Set Up Prettier

Create `.prettierrc`:
```json
{
  "semi": false,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

### 13. Update package.json Scripts

Update `package.json`:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "type-check": "tsc --noEmit"
  }
}
```

### 14. Create Initial App Component

Update `src/App.tsx`:
```typescript
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'
import { store } from '@/app/store'
import { AppRoutes } from '@/routes'
import '@/styles/globals.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppRoutes />
          <Toaster position="top-right" />
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </Provider>
  )
}

export default App
```

### 15. Run the Development Server

```bash
# Start the backend API (in a separate terminal)
cd .. # Go to project root
docker-compose up -d

# Start the frontend dev server
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Next Steps

1. **Implement Authentication**
   - Create login/register pages
   - Set up JWT token management
   - Implement protected routes

2. **Build Core Layout**
   - Create header, sidebar, and main layout components
   - Implement responsive navigation
   - Add theme switching

3. **Create Dashboard Components**
   - Implement widget system
   - Add real-time WebSocket connection
   - Build data visualization components

4. **Set Up Testing**
   - Configure Vitest for unit tests
   - Add React Testing Library tests
   - Set up E2E tests with Playwright

5. **Configure CI/CD**
   - Add GitHub Actions workflow
   - Set up automated testing
   - Configure deployment pipeline

## Development Tips

1. **Use TypeScript Strictly** - Enable all strict checks
2. **Component Organization** - One component per file
3. **State Management** - Use RTK Query for server state
4. **Performance** - Lazy load routes and heavy components
5. **Accessibility** - Test with keyboard and screen readers
6. **Documentation** - Use Storybook for component docs

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure the backend allows frontend origin
   - Check proxy configuration in vite.config.ts

2. **Type Errors**
   - Run `npm run type-check` to identify issues
   - Ensure all API responses have proper types

3. **Build Failures**
   - Clear node_modules and reinstall
   - Check for circular dependencies

4. **WebSocket Connection Issues**
   - Verify backend WebSocket endpoint
   - Check authentication token is being sent

## Resources

- [React Documentation](https://react.dev)
- [Redux Toolkit](https://redux-toolkit.js.org)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Guide](https://vitejs.dev/guide)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)