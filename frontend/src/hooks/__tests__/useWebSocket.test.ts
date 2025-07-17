/**
 * Tests for WebSocket hooks
 */

import React from 'react'
import { renderHook, act } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { toast } from 'react-hot-toast'
import { useWebSocketConnection, useWebSocketSubscription, useDashboardMetrics } from '../useWebSocket'
import { websocketService } from '@services/websocket'
import authSlice from '@features/auth/authSlice'

// Mock the websocket service
jest.mock('@services/websocket')
jest.mock('react-hot-toast')

const mockWebSocketService = websocketService as jest.Mocked<typeof websocketService>

// Mock store setup
const createMockStore = (isAuthenticated = true) => {
  return configureStore({
    reducer: {
      auth: authSlice,
    },
    preloadedState: {
      auth: {
        user: isAuthenticated ? { id: 1, email: 'test@example.com' } : null,
        token: isAuthenticated ? 'mock-token' : null,
        refreshToken: null,
        isAuthenticated,
        loading: false,
        error: null,
      },
    },
  })
}

const createWrapper = (isAuthenticated = true) => {
  const store = createMockStore(isAuthenticated)
  return ({ children }: { children: React.ReactNode }) => React.createElement(
    Provider,
    { store },
    children
  )
}

describe('useWebSocketConnection', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should connect to WebSocket when authenticated', async () => {
    mockWebSocketService.connect.mockResolvedValue(undefined)
    mockWebSocketService.onConnectionChange.mockReturnValue(jest.fn())
    mockWebSocketService.onError.mockReturnValue(jest.fn())
    mockWebSocketService.getConnectionStatus.mockReturnValue('connected')

    const { result } = renderHook(() => useWebSocketConnection(), {
      wrapper: createWrapper(true),
    })

    await act(async () => {
      // Wait for the useEffect to run
      await new Promise(resolve => setTimeout(resolve, 0))
    })

    expect(mockWebSocketService.connect).toHaveBeenCalled()
    expect(mockWebSocketService.onConnectionChange).toHaveBeenCalled()
    expect(mockWebSocketService.onError).toHaveBeenCalled()
  })

  it('should disconnect when not authenticated', () => {
    mockWebSocketService.disconnect.mockImplementation(() => {})

    renderHook(() => useWebSocketConnection(), {
      wrapper: createWrapper(false),
    })

    expect(mockWebSocketService.disconnect).toHaveBeenCalled()
  })

  it('should handle connection errors', async () => {
    const errorMessage = 'Connection failed'
    mockWebSocketService.connect.mockRejectedValue(new Error(errorMessage))
    mockWebSocketService.onConnectionChange.mockReturnValue(jest.fn())
    mockWebSocketService.onError.mockReturnValue(jest.fn())

    const { result } = renderHook(() => useWebSocketConnection(), {
      wrapper: createWrapper(true),
    })

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0))
    })

    expect(result.current.error).toBe(errorMessage)
    expect(result.current.connectionStatus).toBe('disconnected')
  })

  it('should provide reconnect function', async () => {
    mockWebSocketService.connect.mockResolvedValue(undefined)
    mockWebSocketService.onConnectionChange.mockReturnValue(jest.fn())
    mockWebSocketService.onError.mockReturnValue(jest.fn())

    const { result } = renderHook(() => useWebSocketConnection(), {
      wrapper: createWrapper(true),
    })

    await act(async () => {
      await result.current.reconnect()
    })

    expect(mockWebSocketService.connect).toHaveBeenCalledTimes(2) // Once in useEffect, once in reconnect
  })
})

describe('useWebSocketSubscription', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should subscribe to channel when connected', () => {
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockReturnValue(mockUnsubscribe)
    
    // Mock the connection hook to return connected state
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const callback = jest.fn()
    const channel = 'test.channel'

    const { unmount } = renderHook(() => useWebSocketSubscription(channel, callback), {
      wrapper: createWrapper(true),
    })

    expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(channel, expect.any(Function))

    // Unmount should unsubscribe
    unmount()
    expect(mockUnsubscribe).toHaveBeenCalled()
  })

  it('should not subscribe when disconnected', () => {
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: false }),
    }))

    const callback = jest.fn()
    const channel = 'test.channel'

    renderHook(() => useWebSocketSubscription(channel, callback), {
      wrapper: createWrapper(true),
    })

    expect(mockWebSocketService.subscribe).not.toHaveBeenCalled()
  })

  it('should handle callback updates', () => {
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockReturnValue(mockUnsubscribe)
    
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const callback1 = jest.fn()
    const callback2 = jest.fn()
    const channel = 'test.channel'

    const { rerender } = renderHook(
      ({ callback }) => useWebSocketSubscription(channel, callback),
      {
        wrapper: createWrapper(true),
        initialProps: { callback: callback1 },
      }
    )

    // Get the wrapped callback that was passed to subscribe
    const wrappedCallback = mockWebSocketService.subscribe.mock.calls[0][1]

    // Test the original callback
    wrappedCallback({ test: 'data' })
    expect(callback1).toHaveBeenCalledWith({ test: 'data' })

    // Update the callback
    rerender({ callback: callback2 })

    // Test the new callback
    wrappedCallback({ test: 'data2' })
    expect(callback2).toHaveBeenCalledWith({ test: 'data2' })
    expect(callback1).toHaveBeenCalledTimes(1) // Should not be called again
  })
})

describe('useDashboardMetrics', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should subscribe to metrics updates', () => {
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockReturnValue(mockUnsubscribe)
    
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const { result } = renderHook(() => useDashboardMetrics(), {
      wrapper: createWrapper(true),
    })

    expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(
      'metrics.updates',
      expect.any(Function)
    )

    expect(result.current.loading).toBe(true)
    expect(result.current.metrics).toBe(null)
  })

  it('should subscribe to organization metrics when orgId provided', () => {
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockReturnValue(mockUnsubscribe)
    
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const orgId = 123

    renderHook(() => useDashboardMetrics(orgId), {
      wrapper: createWrapper(true),
    })

    expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(
      'org.123.metrics',
      expect.any(Function)
    )
  })

  it('should handle metrics updates', () => {
    let capturedCallback: any
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockImplementation((channel, callback) => {
      capturedCallback = callback
      return mockUnsubscribe
    })
    
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const { result } = renderHook(() => useDashboardMetrics(), {
      wrapper: createWrapper(true),
    })

    expect(result.current.loading).toBe(true)
    expect(result.current.metrics).toBe(null)

    // Simulate receiving metrics data
    const mockMetrics = {
      totalSites: 10,
      securityScore: 85,
      criticalUpdates: 3,
    }

    act(() => {
      capturedCallback(mockMetrics)
    })

    expect(result.current.loading).toBe(false)
    expect(result.current.metrics).toEqual(mockMetrics)
    expect(result.current.error).toBe(null)
  })

  it('should update metrics incrementally', () => {
    let capturedCallback: any
    const mockUnsubscribe = jest.fn()
    mockWebSocketService.subscribe.mockImplementation((channel, callback) => {
      capturedCallback = callback
      return mockUnsubscribe
    })
    
    jest.doMock('../useWebSocket', () => ({
      ...jest.requireActual('../useWebSocket'),
      useWebSocketConnection: () => ({ isConnected: true }),
    }))

    const { result } = renderHook(() => useDashboardMetrics(), {
      wrapper: createWrapper(true),
    })

    // First update
    act(() => {
      capturedCallback({ totalSites: 10, securityScore: 85 })
    })

    expect(result.current.metrics).toEqual({ totalSites: 10, securityScore: 85 })

    // Second update - should merge with existing
    act(() => {
      capturedCallback({ criticalUpdates: 3 })
    })

    expect(result.current.metrics).toEqual({
      totalSites: 10,
      securityScore: 85,
      criticalUpdates: 3,
    })
  })
})