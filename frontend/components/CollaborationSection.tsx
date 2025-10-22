'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  UsersIcon, 
  MessageCircleIcon, 
  BellIcon, 
  PlusIcon,
  UserPlusIcon,
  SettingsIcon,
  MoreHorizontalIcon,
  CheckCircleIcon,
  ClockIcon,
  AlertCircleIcon,
  FileTextIcon,
  BuildingIcon,
  EyeIcon
} from 'lucide-react';
import { TeamMember, Notification } from '@/types';

interface CollaborationSectionProps {
  teamMembers: TeamMember[];
  notifications: Notification[];
  onTeamAction: (action: string, memberId?: string) => void;
  onNotificationAction: (action: string, notificationId: string) => void;
}

export default function CollaborationSection({ 
  teamMembers, 
  notifications, 
  onTeamAction, 
  onNotificationAction 
}: CollaborationSectionProps) {
  const [activeTab, setActiveTab] = useState('team');

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
      case 'warning': return <AlertCircleIcon className="h-4 w-4 text-orange-600" />;
      case 'info': return <ClockIcon className="h-4 w-4 text-blue-600" />;
      default: return <BellIcon className="h-4 w-4 text-slate-600" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-50 border-green-200';
      case 'warning': return 'bg-orange-50 border-orange-200';
      case 'info': return 'bg-blue-50 border-blue-200';
      default: return 'bg-slate-50 border-slate-200';
    }
  };

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <UsersIcon className="h-5 w-5 text-slate-600" />
          <span>Collaboration & Tools</span>
        </CardTitle>
        <CardDescription>
          Team collaboration, AI assistant, and notifications
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="team" className="flex items-center space-x-2">
              <UsersIcon className="h-4 w-4" />
              <span>Team</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center space-x-2">
              <MessageCircleIcon className="h-4 w-4" />
              <span>AI Assistant</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center space-x-2">
              <BellIcon className="h-4 w-4" />
              <span>Notifications</span>
              {notifications.length > 0 && (
                <Badge variant="destructive" className="ml-1">
                  {notifications.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Team Tab */}
          <TabsContent value="team" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Team Members</h3>
                <Button size="sm" onClick={() => onTeamAction('invite')}>
                  <UserPlusIcon className="h-4 w-4 mr-2" />
                  Invite Member
                </Button>
              </div>

              {teamMembers.length > 0 ? (
                <div className="space-y-3">
                  {teamMembers.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-medium">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-900">{member.name}</h4>
                          <p className="text-sm text-slate-600">{member.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={member.role === 'owner' ? 'default' : 'outline'}>
                          {member.role}
                        </Badge>
                        <Button variant="ghost" size="sm" onClick={() => onTeamAction('settings', member.id)}>
                          <SettingsIcon className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <UsersIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No Team Members</h3>
                  <p className="text-slate-600 mb-4">Invite team members to collaborate on this project</p>
                  <Button onClick={() => onTeamAction('invite')}>
                    <UserPlusIcon className="h-4 w-4 mr-2" />
                    Invite First Member
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>

          {/* AI Assistant Tab */}
          <TabsContent value="ai" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">AI Assistant</h3>
                <Badge variant="outline" className="text-green-600 border-green-300">
                  <CheckCircleIcon className="h-3 w-3 mr-1" />
                  Online
                </Badge>
              </div>

              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <h4 className="font-medium text-slate-900 mb-2">ArchMesh AI Assistant</h4>
                <p className="text-sm text-slate-600 mb-3">
                  Get help with architecture decisions, requirements analysis, and project guidance
                </p>
                <div className="flex items-center space-x-2">
                  <Button size="sm" onClick={() => onTeamAction('open-chat')}>
                    <MessageCircleIcon className="h-4 w-4 mr-2" />
                    Start Chat
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => onTeamAction('ai-settings')}>
                    <SettingsIcon className="h-4 w-4 mr-2" />
                    Settings
                  </Button>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border border-slate-200 rounded-lg">
                  <h4 className="font-medium text-slate-900 mb-2">Quick Actions</h4>
                  <div className="space-y-2">
                    <Button variant="outline" size="sm" className="w-full justify-start" onClick={() => onTeamAction('ai-help', 'requirements')}>
                      <FileTextIcon className="h-4 w-4 mr-2" />
                      Help with Requirements
                    </Button>
                    <Button variant="outline" size="sm" className="w-full justify-start" onClick={() => onTeamAction('ai-help', 'architecture')}>
                      <BuildingIcon className="h-4 w-4 mr-2" />
                      Architecture Guidance
                    </Button>
                    <Button variant="outline" size="sm" className="w-full justify-start" onClick={() => onTeamAction('ai-help', 'review')}>
                      <EyeIcon className="h-4 w-4 mr-2" />
                      Review Project
                    </Button>
                  </div>
                </div>

                <div className="p-4 border border-slate-200 rounded-lg">
                  <h4 className="font-medium text-slate-900 mb-2">Recent Activity</h4>
                  <div className="space-y-2 text-sm text-slate-600">
                    <p>• Analyzed requirements complexity</p>
                    <p>• Suggested architecture improvements</p>
                    <p>• Reviewed technology stack</p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Notifications</h3>
                <Button variant="outline" size="sm" onClick={() => onNotificationAction('mark-all-read')}>
                  Mark All Read
                </Button>
              </div>

              {notifications.length > 0 ? (
                <div className="space-y-3">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 border rounded-lg ${getNotificationColor(notification.type)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          {getNotificationIcon(notification.type)}
                          <div>
                            <h4 className="font-medium text-slate-900">{notification.title}</h4>
                            <p className="text-sm text-slate-600 mt-1">{notification.message}</p>
                            <p className="text-xs text-slate-500 mt-1">
                              {new Date(notification.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {!notification.read && (
                            <Badge variant="destructive" className="text-xs">
                              New
                            </Badge>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => onNotificationAction('dismiss', notification.id)}>
                            <MoreHorizontalIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BellIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No Notifications</h3>
                  <p className="text-slate-600">You're all caught up! New notifications will appear here</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
