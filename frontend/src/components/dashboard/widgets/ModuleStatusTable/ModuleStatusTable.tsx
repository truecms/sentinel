import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Shield,
  Info
} from 'lucide-react'
import { clsx } from 'clsx'
import type { ModuleStatusTableProps, ModuleStatus } from '../../../../types/dashboard'
import { Skeleton } from '../../../common'

export const ModuleStatusTable: React.FC<ModuleStatusTableProps> = ({
  modules,
  pagination,
  sorting,
  filters,
  onRowClick,
  loading = false,
  error,
}) => {
  const [localSearchTerm, setLocalSearchTerm] = useState(filters?.searchTerm || '')
  
  // Filter modules
  const filteredModules = useMemo(() => {
    let filtered = [...modules]
    
    if (filters?.searchTerm) {
      filtered = filtered.filter(module =>
        module.name.toLowerCase().includes(filters.searchTerm!.toLowerCase())
      )
    }
    
    if (filters?.securityOnly) {
      filtered = filtered.filter(module => module.securityUpdate)
    }
    
    return filtered
  }, [modules, filters])
  
  // Sort modules
  const sortedModules = useMemo(() => {
    if (!sorting) return filteredModules
    
    return [...filteredModules].sort((a, b) => {
      const aValue = a[sorting.field]
      const bValue = b[sorting.field]
      
      if (aValue < bValue) return sorting.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sorting.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [filteredModules, sorting])
  
  // Paginate modules
  const paginatedModules = useMemo(() => {
    if (!pagination) return sortedModules
    
    const start = (pagination.page - 1) * pagination.pageSize
    const end = start + pagination.pageSize
    
    return sortedModules.slice(start, end)
  }, [sortedModules, pagination])
  
  const totalPages = pagination 
    ? Math.ceil(filteredModules.length / pagination.pageSize)
    : 1
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalSearchTerm(e.target.value)
    filters?.onFilterChange({ searchTerm: e.target.value })
  }
  
  const handleSecurityFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    filters?.onFilterChange({ securityOnly: e.target.checked })
  }
  
  const getSortIcon = (field: keyof ModuleStatus) => {
    if (!sorting || sorting.field !== field) return null
    
    return sorting.direction === 'asc' 
      ? <ChevronUp className="w-4 h-4" />
      : <ChevronDown className="w-4 h-4" />
  }
  
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }
  
  if (error) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg border border-danger-200 dark:border-danger-800 p-6">
        <div className="flex items-center gap-2 text-danger-600 dark:text-danger-400">
          <AlertTriangle className="w-5 h-5" />
          <p className="font-medium">Error loading modules</p>
        </div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">{error.message}</p>
      </div>
    )
  }
  
  return (
    <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm">
      {/* Header with filters */}
      {filters && (
        <div className="p-4 border-b border-neutral-200 dark:border-neutral-700">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 dark:text-neutral-500" />
              <input
                type="text"
                value={localSearchTerm}
                onChange={handleSearchChange}
                placeholder="Search modules..."
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 placeholder-neutral-500 dark:placeholder-neutral-400"
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.securityOnly || false}
                onChange={handleSecurityFilterChange}
                className="rounded border-neutral-300 dark:border-neutral-600 text-primary-600 dark:text-primary-400 focus:ring-primary-500 dark:focus:ring-primary-400"
              />
              <span className="text-sm text-neutral-700 dark:text-neutral-300">Security updates only</span>
            </label>
          </div>
        </div>
      )}
      
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900">
              <th
                className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => sorting?.onSort('name')}
              >
                <div className="flex items-center gap-1">
                  Module Name
                  {getSortIcon('name')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => sorting?.onSort('currentVersion')}
              >
                <div className="flex items-center gap-1">
                  Current Version
                  <div className="relative group">
                    <Info className="w-3 h-3 text-neutral-400" />
                    <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-neutral-900 text-white rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                      Most commonly used version across your sites
                      <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900"></div>
                    </div>
                  </div>
                  {getSortIcon('currentVersion')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => sorting?.onSort('latestVersion')}
              >
                <div className="flex items-center gap-1">
                  Latest Version
                  <div className="relative group">
                    <Info className="w-3 h-3 text-neutral-400" />
                    <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-neutral-900 text-white rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                      Newest available version of this module
                      <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900"></div>
                    </div>
                  </div>
                  {getSortIcon('latestVersion')}
                </div>
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Status
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => sorting?.onSort('sites')}
              >
                <div className="flex items-center gap-1">
                  Sites
                  <div className="relative group">
                    <Info className="w-3 h-3 text-neutral-400" />
                    <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-neutral-900 text-white rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                      Number of sites with updates available
                      <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900"></div>
                    </div>
                  </div>
                  {getSortIcon('sites')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                onClick={() => sorting?.onSort('lastUpdated')}
              >
                <div className="flex items-center gap-1">
                  Last Updated
                  {getSortIcon('lastUpdated')}
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, index) => (
                <tr key={index}>
                  <td className="px-6 py-4">
                    <Skeleton width="8rem" height="1rem" />
                  </td>
                  <td className="px-6 py-4">
                    <Skeleton width="5rem" height="1rem" />
                  </td>
                  <td className="px-6 py-4">
                    <Skeleton width="5rem" height="1rem" />
                  </td>
                  <td className="px-6 py-4">
                    <Skeleton width="6rem" height="1.5rem" className="rounded-full" />
                  </td>
                  <td className="px-6 py-4">
                    <Skeleton width="3rem" height="1rem" />
                  </td>
                  <td className="px-6 py-4">
                    <Skeleton width="6rem" height="1rem" />
                  </td>
                </tr>
              ))
            ) : paginatedModules.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-neutral-500 dark:text-neutral-400">
                  No modules found
                </td>
              </tr>
            ) : (
              paginatedModules.map((module, index) => (
                <motion.tr
                  key={module.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onRowClick?.(module)}
                  className={clsx(
                    'hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors',
                    onRowClick && 'cursor-pointer'
                  )}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                      {module.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      {module.currentVersion}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      {module.latestVersion || module.currentVersion}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {module.securityUpdate ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800 dark:bg-danger-900/20 dark:text-danger-400 border border-danger-200 dark:border-danger-800">
                        <Shield className="w-3 h-3" />
                        Security Update
                      </span>
                    ) : module.latestVersion && module.latestVersion !== module.currentVersion ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800 dark:bg-warning-900/20 dark:text-warning-400 border border-warning-200 dark:border-warning-800">
                        Update Available
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800 dark:bg-success-900/20 dark:text-success-400 border border-success-200 dark:border-success-800">
                        Up to Date
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      {module.sites}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      {formatDate(module.lastUpdated)}
                    </div>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="px-6 py-3 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900">
          <div className="flex items-center justify-between">
            <div className="text-sm text-neutral-700 dark:text-neutral-300">
              Showing {((pagination.page - 1) * pagination.pageSize) + 1} to{' '}
              {Math.min(pagination.page * pagination.pageSize, filteredModules.length)} of{' '}
              {filteredModules.length} results
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => pagination.onPageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  pagination.page === 1
                    ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
                    : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
                )}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm text-neutral-700 dark:text-neutral-300">
                Page {pagination.page} of {totalPages}
              </span>
              <button
                onClick={() => pagination.onPageChange(pagination.page + 1)}
                disabled={pagination.page === totalPages}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  pagination.page === totalPages
                    ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-400 dark:text-neutral-600 cursor-not-allowed'
                    : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
                )}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}