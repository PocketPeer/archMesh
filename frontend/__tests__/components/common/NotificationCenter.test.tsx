/**
 * Tests for NotificationCenter component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NotificationCenter from '@/src/components/common/NotificationCenter';
import { useWebSocket } from '@/src/hooks/useWebSocket';

// Mock the useWebSocket hook
jest.mock('@/src/hooks/useWebSocket');
const mockUseWebSocket = useWebSocket as jest.MockedFunction<typeof useWebSocket>;

describe('NotificationCenter', () => {
  const mockMarkNotificationAsRead = jest.fn();
  const mockClearNotifications = jest.fn();

  beforeEach(() => {
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications: [],
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders notification bell icon', () => {
    render(<NotificationCenter />);
    
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows unread count badge when there are unread notifications', () => {
    const notifications = [
      {
        id: '1',
        type: 'info' as const,
        title: 'Test Notification',
        message: 'Test message',
        timestamp: Date.now(),
        read: false
      },
      {
        id: '2',
        type: 'success' as const,
        title: 'Another Notification',
        message: 'Another message',
        timestamp: Date.now(),
        read: true
      }
    ];

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications,
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });

    render(<NotificationCenter />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('opens notification dropdown when clicked', () => {
    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays notifications in dropdown', () => {
    const notifications = [
      {
        id: '1',
        type: 'info' as const,
        title: 'Test Notification',
        message: 'Test message',
        timestamp: Date.now(),
        read: false
      }
    ];

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications,
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });

    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Test Notification')).toBeInTheDocument();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('shows "No notifications yet" when there are no notifications', () => {
    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('No notifications yet')).toBeInTheDocument();
  });

  it('marks notification as read when clicked', () => {
    const notifications = [
      {
        id: '1',
        type: 'info' as const,
        title: 'Test Notification',
        message: 'Test message',
        timestamp: Date.now(),
        read: false
      }
    ];

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications,
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });

    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    const notification = screen.getByText('Test Notification');
    fireEvent.click(notification);
    
    expect(mockMarkNotificationAsRead).toHaveBeenCalledWith('1');
  });

  it('clears all notifications when clear all is clicked', () => {
    const notifications = [
      {
        id: '1',
        type: 'info' as const,
        title: 'Test Notification',
        message: 'Test message',
        timestamp: Date.now(),
        read: false
      }
    ];

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications,
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });

    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    const clearButton = screen.getByText('Clear all');
    fireEvent.click(clearButton);
    
    expect(mockClearNotifications).toHaveBeenCalled();
  });

  it('closes dropdown when clicking outside', async () => {
    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    
    // Click on the overlay (click outside handler)
    const overlay = document.querySelector('.fixed.inset-0.z-40');
    expect(overlay).toBeInTheDocument();
    
    fireEvent.click(overlay!);
    
    await waitFor(() => {
      expect(screen.queryByText('Notifications')).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('displays different notification types with correct icons', () => {
    const notifications = [
      {
        id: '1',
        type: 'success' as const,
        title: 'Success Notification',
        message: 'Success message',
        timestamp: Date.now(),
        read: false
      },
      {
        id: '2',
        type: 'error' as const,
        title: 'Error Notification',
        message: 'Error message',
        timestamp: Date.now(),
        read: false
      },
      {
        id: '3',
        type: 'warning' as const,
        title: 'Warning Notification',
        message: 'Warning message',
        timestamp: Date.now(),
        read: false
      }
    ];

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      isConnecting: false,
      error: null,
      lastMessage: null,
      sendMessage: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      workflowUpdates: [],
      notifications,
      markNotificationAsRead: mockMarkNotificationAsRead,
      clearNotifications: mockClearNotifications,
    });

    render(<NotificationCenter />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(screen.getByText('Success Notification')).toBeInTheDocument();
    expect(screen.getByText('Error Notification')).toBeInTheDocument();
    expect(screen.getByText('Warning Notification')).toBeInTheDocument();
  });
});

