'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BellIcon, 
  CheckCircleIcon, 
  AlertCircleIcon, 
  ClockIcon, 
  XIcon,
  EyeIcon,
  RefreshCwIcon
} from 'lucide-react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  timestamp: string;
  workflowId?: string;
  projectId?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  read: boolean;
}

interface NotificationCenterProps {
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
  onClearAll: () => void;
  onViewWorkflow: (workflowId: string, projectId: string) => void;
}

export default function NotificationCenter({ 
  notifications, 
  onMarkAsRead, 
  onClearAll, 
  onViewWorkflow 
}: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'error':
        return <AlertCircleIcon className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertCircleIcon className="h-5 w-5 text-yellow-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-blue-600" />;
    }
  };

  const getNotificationBadge = (type: Notification['type']) => {
    const variants = {
      success: 'default',
      error: 'destructive',
      warning: 'secondary',
      info: 'outline'
    } as const;

    return (
      <Badge variant={variants[type]}>
        {type.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        <BellIcon className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
          >
            {unreadCount}
          </Badge>
        )}
      </Button>

      {/* Notification Panel */}
      {isOpen && (
        <Card className="absolute right-0 top-12 w-96 z-50 border-0 shadow-xl">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Notifications</CardTitle>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onClearAll}
                    className="text-xs"
                  >
                    Clear All
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                >
                  <XIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <CardDescription>
              {notifications.length} notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-slate-500">
                <BellIcon className="h-8 w-8 mx-auto mb-2 text-slate-400" />
                <p>No notifications yet</p>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                      !notification.read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-slate-900">
                            {notification.title}
                          </h4>
                          <div className="flex items-center space-x-2">
                            {getNotificationBadge(notification.type)}
                            {!notification.read && (
                              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-slate-600 mt-1">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-slate-500">
                            {new Date(notification.timestamp).toLocaleString()}
                          </span>
                          <div className="flex items-center space-x-2">
                            {notification.workflowId && notification.projectId && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  onViewWorkflow(notification.workflowId!, notification.projectId!);
                                  onMarkAsRead(notification.id);
                                }}
                                className="text-xs"
                              >
                                <EyeIcon className="h-3 w-3 mr-1" />
                                View
                              </Button>
                            )}
                            {notification.action && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  notification.action!.onClick();
                                  onMarkAsRead(notification.id);
                                }}
                                className="text-xs"
                              >
                                {notification.action.label}
                              </Button>
                            )}
                            {!notification.read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onMarkAsRead(notification.id)}
                                className="text-xs"
                              >
                                Mark Read
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
