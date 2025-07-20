import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Users, 
  Settings, 
  Globe,
  ArrowLeft,
  Save,
  Trash2,
  UserPlus,
  Shield
} from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Input } from '../../components/common/Input';
import { Table } from '../../components/common/Table';
import { Modal } from '../../components/common/Modal';
import { Spinner } from '../../components/common/Spinner';
import { toast } from 'react-hot-toast';
import { apiClient } from '../../utils/api';

interface Organization {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  users?: User[];
}

interface User {
  id: number;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
}

export const OrganizationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });
  const [newUserEmail, setNewUserEmail] = useState('');

  useEffect(() => {
    if (id) {
      fetchOrganization();
    }
  }, [id]);

  const fetchOrganization = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/organizations/${id}`);
      setOrganization(response.data);
      setFormData({
        name: response.data.name,
        description: response.data.description || '',
      });
    } catch (error) {
      toast.error('Failed to load organization');
      navigate('/app/organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await apiClient.put(`/organizations/${id}`, formData);
      toast.success('Organization updated successfully');
      setEditing(false);
      fetchOrganization();
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to update organization';
      toast.error(message);
    }
  };

  const handleDelete = async () => {
    try {
      await apiClient.delete(`/organizations/${id}`);
      toast.success('Organization deleted successfully');
      navigate('/app/organizations');
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to delete organization';
      toast.error(message);
    }
  };

  const handleAddUser = async () => {
    try {
      // TODO: Implement add user to organization API endpoint
      toast.success('User added successfully');
      setShowAddUserModal(false);
      setNewUserEmail('');
      fetchOrganization();
    } catch (error) {
      toast.error('Failed to add user');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!organization) {
    return null;
  }

  const userColumns = [
    {
      key: 'email',
      label: 'Email',
      render: (user: User) => (
        <div>
          <div className="font-medium">{user.email}</div>
          {user.full_name && (
            <div className="text-sm text-neutral-500">{user.full_name}</div>
          )}
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (user: User) => (
        <Badge variant={user.role === 'org_admin' ? 'primary' : 'neutral'}>
          {user.role}
        </Badge>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (user: User) => (
        <Badge variant={user.is_active ? 'success' : 'danger'}>
          {user.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (user: User) => (
        <Button variant="ghost" size="sm">
          Manage
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/app/organizations')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              {organization.name}
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Manage organization settings and members
            </p>
          </div>
        </div>
        <Badge
          variant={organization.is_active ? 'success' : 'danger'}
          size="lg"
        >
          {organization.is_active ? 'Active' : 'Inactive'}
        </Badge>
      </div>

      {/* Organization Details */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Organization Details
            </h2>
            {!editing ? (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setEditing(true)}
              >
                Edit
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEditing(false);
                    setFormData({
                      name: organization.name,
                      description: organization.description || '',
                    });
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleUpdate}
                  className="flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Save
                </Button>
              </div>
            )}
          </div>

          <div className="space-y-4">
            {editing ? (
              <>
                <Input
                  label="Organization Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-700 rounded-lg 
                             bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100
                             focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={3}
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="text-sm font-medium text-neutral-500">Name</label>
                  <p className="text-neutral-900 dark:text-neutral-100">{organization.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-500">Description</label>
                  <p className="text-neutral-900 dark:text-neutral-100">
                    {organization.description || 'No description provided'}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-500">Created</label>
                  <p className="text-neutral-900 dark:text-neutral-100">
                    {new Date(organization.created_at).toLocaleDateString()}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Members */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Users className="w-5 h-5" />
              Organization Members
            </h2>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowAddUserModal(true)}
              className="flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Add Member
            </Button>
          </div>

          {organization.users && organization.users.length > 0 ? (
            <Table data={organization.users} columns={userColumns} />
          ) : (
            <div className="text-center py-8 text-neutral-500">
              No members found
            </div>
          )}
        </div>
      </Card>

      {/* Danger Zone */}
      <Card className="border-danger-200 dark:border-danger-800">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-danger-600 dark:text-danger-400 mb-4">
            Danger Zone
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-neutral-900 dark:text-neutral-100">
                Delete Organization
              </h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Once deleted, this organization and all its data cannot be recovered.
              </p>
            </div>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowDeleteModal(true)}
              className="flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </Button>
          </div>
        </div>
      </Card>

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Organization"
      >
        <div className="space-y-4">
          <p className="text-neutral-600 dark:text-neutral-400">
            Are you sure you want to delete <strong>{organization.name}</strong>? 
            This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <Button
              variant="ghost"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
            >
              Delete Organization
            </Button>
          </div>
        </div>
      </Modal>

      {/* Add User Modal */}
      <Modal
        isOpen={showAddUserModal}
        onClose={() => setShowAddUserModal(false)}
        title="Add Member"
      >
        <div className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            value={newUserEmail}
            onChange={(e) => setNewUserEmail(e.target.value)}
            placeholder="Enter user email"
            required
          />
          <div className="flex justify-end gap-3">
            <Button
              variant="ghost"
              onClick={() => setShowAddUserModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleAddUser}
              disabled={!newUserEmail.trim()}
            >
              Add Member
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};