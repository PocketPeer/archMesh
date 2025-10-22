'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  UserPlusIcon, 
  UsersIcon, 
  MailIcon, 
  ShieldIcon, 
  MoreHorizontalIcon,
  TrashIcon,
  EditIcon
} from 'lucide-react';

export interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: 'owner' | 'collaborator' | 'viewer';
  status: 'active' | 'pending' | 'inactive';
  joinedAt: string;
  lastActive?: string;
}

interface TeamCollaborationProps {
  projectId: string;
  members: TeamMember[];
  onAddMember: (email: string, role: TeamMember['role']) => Promise<void>;
  onRemoveMember: (memberId: string) => Promise<void>;
  onUpdateRole: (memberId: string, role: TeamMember['role']) => Promise<void>;
}

export default function TeamCollaboration({ 
  projectId, 
  members, 
  onAddMember, 
  onRemoveMember, 
  onUpdateRole 
}: TeamCollaborationProps) {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState<TeamMember['role']>('collaborator');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddMember = async () => {
    if (!newMemberEmail.trim()) return;
    
    try {
      setIsAdding(true);
      await onAddMember(newMemberEmail.trim(), newMemberRole);
      setNewMemberEmail('');
      setIsAddDialogOpen(false);
    } catch (error) {
      console.error('Failed to add member:', error);
    } finally {
      setIsAdding(false);
    }
  };

  const getRoleBadge = (role: TeamMember['role']) => {
    const variants = {
      owner: 'default',
      collaborator: 'secondary',
      viewer: 'outline'
    } as const;

    const colors = {
      owner: 'bg-blue-100 text-blue-800',
      collaborator: 'bg-green-100 text-green-800',
      viewer: 'bg-gray-100 text-gray-800'
    };

    return (
      <Badge className={colors[role]}>
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </Badge>
    );
  };

  const getStatusBadge = (status: TeamMember['status']) => {
    const variants = {
      active: 'default',
      pending: 'secondary',
      inactive: 'outline'
    } as const;

    return (
      <Badge variant={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getRoleDescription = (role: TeamMember['role']) => {
    switch (role) {
      case 'owner':
        return 'Full access to project, can manage team and settings';
      case 'collaborator':
        return 'Can edit project, start workflows, and view results';
      case 'viewer':
        return 'Can view project and results, but cannot make changes';
      default:
        return '';
    }
  };

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <UsersIcon className="h-5 w-5 text-slate-600" />
            <CardTitle>Team Members</CardTitle>
            <Badge variant="secondary" className="ml-2">
              {members.length} members
            </Badge>
          </div>
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                <UserPlusIcon className="h-4 w-4 mr-2" />
                Add Member
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Add Team Member</DialogTitle>
                <DialogDescription>
                  Invite a new member to collaborate on this project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Email Address *
                  </label>
                  <Input
                    type="email"
                    placeholder="Enter email address"
                    value={newMemberEmail}
                    onChange={(e) => setNewMemberEmail(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Role *
                  </label>
                  <Select value={newMemberRole} onValueChange={(value: TeamMember['role']) => setNewMemberRole(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="collaborator">
                        <div className="flex flex-col">
                          <span className="font-medium">Collaborator</span>
                          <span className="text-sm text-slate-600">Can edit and start workflows</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="viewer">
                        <div className="flex flex-col">
                          <span className="font-medium">Viewer</span>
                          <span className="text-sm text-slate-600">Can view project and results</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-slate-500 mt-1">
                    {getRoleDescription(newMemberRole)}
                  </p>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setIsAddDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleAddMember}
                    disabled={!newMemberEmail.trim() || isAdding}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isAdding ? 'Adding...' : 'Add Member'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        <CardDescription>
          Manage team members and their permissions for this project
        </CardDescription>
      </CardHeader>
      <CardContent>
        {members.length === 0 ? (
          <div className="text-center py-8">
            <UsersIcon className="h-12 w-12 mx-auto text-slate-400 mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No team members yet</h3>
            <p className="text-slate-600 mb-4">
              Invite team members to collaborate on this project
            </p>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <UserPlusIcon className="h-4 w-4 mr-2" />
              Add First Member
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:border-slate-300 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-slate-600">
                        {member.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-slate-900">{member.name}</h4>
                      {getStatusBadge(member.status)}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <MailIcon className="h-3 w-3 text-slate-400" />
                      <span className="text-sm text-slate-600">{member.email}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <ShieldIcon className="h-3 w-3 text-slate-400" />
                      {getRoleBadge(member.role)}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Joined {new Date(member.joinedAt).toLocaleDateString()}
                      {member.lastActive && (
                        <span> • Last active {new Date(member.lastActive).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Select
                    value={member.role}
                    onValueChange={(value: TeamMember['role']) => onUpdateRole(member.id, value)}
                    disabled={member.role === 'owner'}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="owner" disabled>
                        Owner
                      </SelectItem>
                      <SelectItem value="collaborator">
                        Collaborator
                      </SelectItem>
                      <SelectItem value="viewer">
                        Viewer
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  {member.role !== 'owner' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onRemoveMember(member.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
