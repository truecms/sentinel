import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Shield
} from 'lucide-react'
import { clsx } from 'clsx'
import type { ModuleStatusTableProps, ModuleStatus } from '../../../../types/dashboard'

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
      <div className="bg-white rounded-lg border border-red-200 p-6">
        <div className="flex items-center gap-2 text-red-600">
          <AlertTriangle className="w-5 h-5" />
          <p className="font-medium">Error loading modules</p>
        </div>
        <p className="text-sm text-gray-600 mt-1">{error.message}</p>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-lg border shadow-sm">
      {/* Header with filters */}
      {filters && (
        <div className="p-4 border-b">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={localSearchTerm}
                onChange={handleSearchChange}
                placeholder="Search modules..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.securityOnly || false}
                onChange={handleSecurityFilterChange}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Security updates only</span>
            </label>
          </div>
        </div>
      )}
      
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              <th
                className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => sorting?.onSort('name')}
              >
                <div className="flex items-center gap-1">
                  Module Name
                  {getSortIcon('name')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => sorting?.onSort('currentVersion')}
              >
                <div className="flex items-center gap-1">
                  Current Version
                  {getSortIcon('currentVersion')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => sorting?.onSort('latestVersion')}
              >
                <div className="flex items-center gap-1">
                  Latest Version
                  {getSortIcon('latestVersion')}
                </div>
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => sorting?.onSort('sites')}
              >
                <div className="flex items-center gap-1">
                  Sites
                  {getSortIcon('sites')}
                </div>
              </th>
              <th
                className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => sorting?.onSort('lastUpdated')}
              >
                <div className="flex items-center gap-1">
                  Last Updated
                  {getSortIcon('lastUpdated')}
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, index) => (
                <tr key={index}>
                  <td className="px-6 py-4">
                    <div className="h-4 w-32 bg-gray-200 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-6 w-24 bg-gray-200 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : paginatedModules.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
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
                    'hover:bg-gray-50 transition-colors',
                    onRowClick && 'cursor-pointer'
                  )}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {module.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">
                      {module.currentVersion}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">
                      {module.latestVersion || module.currentVersion}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {module.securityUpdate ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <Shield className="w-3 h-3" />
                        Security Update
                      </span>
                    ) : module.latestVersion && module.latestVersion !== module.currentVersion ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        Update Available
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Up to Date
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">
                      {module.sites}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">
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
        <div className="px-6 py-3 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
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
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                )}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm text-gray-700">
                Page {pagination.page} of {totalPages}
              </span>
              <button
                onClick={() => pagination.onPageChange(pagination.page + 1)}
                disabled={pagination.page === totalPages}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  pagination.page === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
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