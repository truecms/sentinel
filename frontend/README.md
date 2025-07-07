# Sentinel Monitoring Platform - Frontend

A modern React-based frontend for the Sentinel Monitoring Platform, built with TypeScript, Vite, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites

- Node.js 20+ 
- npm 10+
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # App-wide setup and configuration
│   │   ├── store.ts           # Redux store configuration
│   │   ├── api.ts             # RTK Query API setup
│   │   └── hooks.ts           # Typed Redux hooks
│   │
│   ├── features/              # Feature-based modules
│   │   ├── auth/             # Authentication feature
│   │   ├── dashboard/        # Dashboard feature
│   │   ├── organizations/    # Organization management
│   │   ├── sites/           # Site management
│   │   ├── modules/         # Module monitoring
│   │   └── reports/         # Reporting feature
│   │
│   ├── components/           # Shared components
│   │   ├── common/          # Generic UI components
│   │   ├── charts/          # Chart components
│   │   ├── layout/          # Layout components
│   │   └── widgets/         # Dashboard widgets
│   │
│   ├── pages/               # Page components
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript type definitions
│   ├── styles/              # Global styles
│   └── assets/              # Static assets
│
├── public/                   # Public assets
├── tests/                    # Test files
└── .storybook/              # Storybook configuration (coming soon)
```

## 🛠️ Available Scripts

```bash
# Development
npm run dev           # Start development server
npm run build         # Build for production
npm run preview       # Preview production build locally

# Testing
npm run test          # Run tests in watch mode
npm run test:ui       # Run tests with UI
npm run test:coverage # Run tests with coverage report

# Code Quality
npm run lint          # Run ESLint
npm run type-check    # Run TypeScript type checking

# Git Hooks (run automatically)
pre-commit            # Runs lint-staged on changed files
```

## 🔧 Technology Stack

### Core
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite 7** - Build tool and dev server
- **React Router 7** - Client-side routing

### State Management
- **Redux Toolkit** - State management
- **RTK Query** - Data fetching and caching
- **React Query** - Server state management

### UI & Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled UI components
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### Data Visualization
- **Recharts** - Chart library
- **React Grid Layout** - Dashboard grid system

### Forms & Validation
- **React Hook Form** - Form management
- **Zod** - Schema validation

### Real-time
- **Socket.io Client** - WebSocket connections

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Husky** - Git hooks
- **Vitest** - Testing framework
- **Testing Library** - Testing utilities

## 🔐 Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000

# Application
VITE_APP_NAME=Sentinel Monitoring Platform
VITE_APP_VERSION=1.0.0
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test src/components/Button/Button.test.tsx
```

### Writing Tests

Tests are co-located with components:
```
components/
  Button/
    Button.tsx
    Button.test.tsx
    index.ts
```

## 🎨 Code Style

This project uses:
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** strict mode

### Path Aliases

The following path aliases are configured:
- `@/*` → `src/*`
- `@components/*` → `src/components/*`
- `@features/*` → `src/features/*`
- `@utils/*` → `src/utils/*`
- `@hooks/*` → `src/hooks/*`
- `@types/*` → `src/types/*`
- `@assets/*` → `src/assets/*`

Example usage:
```typescript
import { Button } from '@components/common';
import { useAuth } from '@features/auth';
import { formatDate } from '@utils/format';
```

## 🚢 Deployment

### Production Build

```bash
# Build the application
npm run build

# Preview the build locally
npm run preview
```

The build output will be in the `dist/` directory.

### Docker

```bash
# Build and run with Docker Compose (from root directory)
docker-compose up -d frontend

# View logs
docker-compose logs -f frontend
```

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass (`npm run test`)
4. Ensure no linting errors (`npm run lint`)
5. Commit your changes (Husky will run pre-commit checks)
6. Push your branch and create a Pull Request

## 🐛 Troubleshooting

### Common Issues

1. **Port 3000 already in use**
   ```bash
   # Kill the process using port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **TypeScript errors in VS Code**
   - Restart TypeScript server: `Cmd+Shift+P` → "TypeScript: Restart TS Server"

3. **Dependencies issues**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **API connection issues**
   - Ensure backend is running on http://localhost:8000
   - Check proxy configuration in `vite.config.ts`

## 📚 Documentation

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vite.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org)

## 📄 License

This project is part of the Sentinel Monitoring Platform.