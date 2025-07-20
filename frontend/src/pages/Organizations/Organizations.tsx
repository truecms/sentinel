import React, { useState, useEffect } from 'react';
import { Plus, Building2, Users, Settings, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { EmptyState } from '../../components/common/EmptyState';
import { Spinner } from '../../components/common/Spinner';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { toast } from 'react-hot-toast';
import { apiClient } from '../../utils/api';

interface Organization {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  users?: any[];
  sites_count?: number;
  is_default?: boolean;
}

export const Organizations: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/organizations/');
      setOrganizations(response.data);
    } catch (error: any) {
      if (error.response?.status === 403) {
        toast.error('You do not have permission to view organizations');
      } else if (error.response?.status === 401) {
        toast.error('Your session has expired. Please login again.');
      } else {
        toast.error('Failed to load organizations');
      }
      console.error('Error fetching organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async () => {
    try {
      setCreateError(null);
      setCreateLoading(true);
      await apiClient.post('/organizations/', formData);
      toast.success('Organization created successfully');
      setShowCreateModal(false);
      setFormData({ name: '', description: '' });
      fetchOrganizations();
    } catch (error: any) {
      let errorMessage = 'Failed to create organization';
      
      if (error.response?.status === 403) {
        errorMessage = 'Only administrators can create new organizations';
      } else if (error.response?.status === 409 || error.response?.status === 400) {
        errorMessage = error.response?.data?.detail || errorMessage;
      } else if (error.message === 'Network Error') {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setCreateError(errorMessage);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleSetDefault = async (orgUuid: string) => {
    try {
      await apiClient.post(`/organizations/by-uuid/${orgUuid}/set-default`);
      toast.success('Default organization updated');
      fetchOrganizations();
    } catch (error) {
      toast.error('Failed to update default organization');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            Organizations
          </h1>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Manage your organizations and their settings
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Organization
        </Button>
      </div>

      {/* Organizations Grid */}
      {organizations.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Building2 className="w-12 h-12 text-neutral-400 dark:text-neutral-600" />}
            title="No organizations found"
            description="You don't have access to any organizations. Contact your administrator if you believe this is an error."
            action={
              // Only show create button if there's a chance the user can create orgs
              !loading ? {
                label: "Create Organization",
                onClick: () => setShowCreateModal(true),
              } : undefined
            }
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {organizations.map((org) => (
            <Card
              key={org.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/app/organizations/${org.uuid}`)}
            >
              <div className="p-6 space-y-4">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                      <Building2 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">
                        {org.name}
                      </h3>
                      {org.is_default && (
                        <Badge variant="info" size="sm" className="mt-1">
                          Default
                        </Badge>
                      )}
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-neutral-400" />
                </div>

                {org.description && (
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 line-clamp-2">
                    {org.description}
                  </p>
                )}

                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4 text-neutral-400" />
                    <span className="text-neutral-600 dark:text-neutral-400">
                      {org.users?.length || 0} users
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Building2 className="w-4 h-4 text-neutral-400" />
                    <span className="text-neutral-600 dark:text-neutral-400">
                      {org.sites_count || 0} sites
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-neutral-200 dark:border-neutral-800">
                  <Badge
                    variant={org.is_active ? 'success' : 'danger'}
                    size="sm"
                  >
                    {org.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  
                  {!org.is_default && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSetDefault(org.uuid);
                      }}
                    >
                      Set as Default
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Organization Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setCreateError(null);
          setFormData({ name: '', description: '' });
        }}
        title="Create New Organization"
      >
        <div className="space-y-4">
          {createError && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    {createError}
                  </h3>
                </div>
              </div>
            </div>
          )}
          <Input
            label="Organization Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter organization name"
            required
          />
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter organization description"
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-700 rounded-lg 
                       bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="ghost"
              onClick={() => setShowCreateModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateOrganization}
              disabled={!formData.name.trim() || createLoading}
              isLoading={createLoading}
            >
              Create Organization
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};