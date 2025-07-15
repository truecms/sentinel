import { configureStore } from '@reduxjs/toolkit';
import { api } from './api';
import authReducer from '@features/auth/authSlice';

export const store = configureStore({
  reducer: {
    // Add the RTK Query reducer
    [api.reducerPath]: api.reducer,
    // Feature reducers
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(api.middleware),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;