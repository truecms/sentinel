import React from 'react'
import { motion } from 'framer-motion'
import { Globe, Shield, Clock, AlertCircle } from 'lucide-react'
import { Card, Badge, Button } from '../../components/common'

interface Site {
  id: string
  name: string
  url: string
  status: 'healthy' | 'warning' | 'critical'
  lastChecked: Date
  drupalVersion: string
  securityUpdates: number
  modules: number
}

const mockSites: Site[] = [
  {
    id: '1',
    name: 'Corporate Website',
    url: 'https://corporate.example.com',
    status: 'healthy',
    lastChecked: new Date('2024-01-20T10:30:00'),
    drupalVersion: '10.1.8',
    securityUpdates: 0,
    modules: 45,
  },
  {
    id: '2',
    name: 'E-commerce Platform',
    url: 'https://shop.example.com',
    status: 'warning',
    lastChecked: new Date('2024-01-20T09:15:00'),
    drupalVersion: '9.5.11',
    securityUpdates: 3,
    modules: 62,
  },
  {
    id: '3',
    name: 'Blog Network',
    url: 'https://blog.example.com',
    status: 'critical',
    lastChecked: new Date('2024-01-20T08:45:00'),
    drupalVersion: '9.4.8',
    securityUpdates: 8,
    modules: 38,
  },
]

export const Sites: React.FC = () => {
  const getStatusColor = (status: Site['status']) => {
    switch (status) {
      case 'healthy':
        return 'success'
      case 'warning':
        return 'warning'
      case 'critical':
        return 'danger'
    }
  }

  const getStatusIcon = (status: Site['status']) => {
    switch (status) {
      case 'healthy':
        return <Shield className="w-5 h-5" />
      case 'warning':
        return <AlertCircle className="w-5 h-5" />
      case 'critical':
        return <AlertCircle className="w-5 h-5" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
            Sites
          </h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Manage and monitor your Drupal sites
          </p>
        </div>
        <Button variant="primary" size="md">
          Add New Site
        </Button>
      </div>

      {/* Sites Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockSites.map((site, index) => (
          <motion.div
            key={site.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="h-full">
              <div className="p-6 space-y-4">
                {/* Site Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                      {site.name}
                    </h3>
                    <a
                      href={site.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1 mt-1"
                    >
                      <Globe className="w-3 h-3" />
                      {site.url}
                    </a>
                  </div>
                  <Badge variant={getStatusColor(site.status)}>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(site.status)}
                      {site.status}
                    </div>
                  </Badge>
                </div>

                {/* Site Details */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-neutral-600 dark:text-neutral-400">
                      Drupal Version
                    </span>
                    <span className="font-medium text-neutral-900 dark:text-neutral-100">
                      {site.drupalVersion}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-neutral-600 dark:text-neutral-400">
                      Modules
                    </span>
                    <span className="font-medium text-neutral-900 dark:text-neutral-100">
                      {site.modules}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-neutral-600 dark:text-neutral-400">
                      Security Updates
                    </span>
                    <span className={`font-medium ${
                      site.securityUpdates > 0 
                        ? 'text-danger-600 dark:text-danger-400' 
                        : 'text-success-600 dark:text-success-400'
                    }`}>
                      {site.securityUpdates}
                    </span>
                  </div>
                </div>

                {/* Last Checked */}
                <div className="pt-3 border-t border-neutral-200 dark:border-neutral-700">
                  <div className="flex items-center gap-2 text-sm text-neutral-500 dark:text-neutral-400">
                    <Clock className="w-4 h-4" />
                    Last checked {site.lastChecked.toLocaleTimeString()}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-3">
                  <Button variant="outline" size="sm" className="flex-1">
                    View Details
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Run Check
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}