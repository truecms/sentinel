import React from 'react'
import { Settings as SettingsIcon } from 'lucide-react'
import { Button } from '../../components/common'

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
            Settings
          </h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Configure your monitoring preferences and integrations
          </p>
        </div>
        <Button variant="primary" size="md">
          Save Changes
        </Button>
      </div>

      {/* Placeholder Content */}
      <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm p-12">
        <div className="text-center">
          <SettingsIcon className="w-16 h-16 text-neutral-400 dark:text-neutral-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
            Settings Coming Soon
          </h2>
          <p className="text-neutral-600 dark:text-neutral-400 max-w-md mx-auto">
            Configure notification preferences, API integrations, security policies, 
            and other platform settings.
          </p>
        </div>
      </div>
    </div>
  )
}