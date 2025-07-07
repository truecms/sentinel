// Application constants
export const APP_NAME = 'Sentinel Monitoring Platform';
export const APP_VERSION = '1.0.0';

// API endpoints
export const API_BASE_URL = '/api/v1';

// WebSocket configuration
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// Module types
export const MODULE_TYPES = {
  CORE: 'core',
  CONTRIB: 'contrib',
  CUSTOM: 'custom',
} as const;

// Module status
export const MODULE_STATUS = {
  UP_TO_DATE: 'up_to_date',
  UPDATE_AVAILABLE: 'update_available',
  SECURITY_UPDATE: 'security_update',
  UNKNOWN: 'unknown',
} as const;

// Risk levels
export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];