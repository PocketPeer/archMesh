"use client";

/**
 * Success Toast Component
 * 
 * Displays success messages with auto-dismiss functionality.
 * Provides clear feedback for successful operations like file uploads.
 */

import React, { useEffect, useState } from 'react';
import { CheckCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface SuccessToastProps {
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  autoDismiss?: boolean;
  duration?: number;
  onDismiss?: () => void;
  className?: string;
}

const SuccessToast: React.FC<SuccessToastProps> = ({
  title,
  message,
  action,
  autoDismiss = true,
  duration = 5000,
  onDismiss,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (!autoDismiss) return;

    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev - (100 / (duration / 100));
        if (newProgress <= 0) {
          setIsVisible(false);
          return 0;
        }
        return newProgress;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [autoDismiss, duration]);

  // Separate effect to handle dismissal when progress reaches 0
  useEffect(() => {
    if (progress <= 0 && !isVisible && onDismiss) {
      onDismiss();
    }
  }, [progress, isVisible, onDismiss]);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible) return null;

  return (
    <div className={`fixed top-4 right-4 z-50 ${className}`}>
      <Card className="p-4 shadow-lg border-l-4 border-l-green-500 bg-white min-w-80">
        <div className="flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
          
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm text-gray-900">{title}</h4>
            <p className="text-sm text-gray-600 mt-1">{message}</p>
            
            {action && (
              <div className="mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={action.onClick}
                  className="text-xs"
                >
                  {action.label}
                </Button>
              </div>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="p-1 h-auto"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        {autoDismiss && (
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div
                className="bg-green-500 h-1 rounded-full transition-all duration-100"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default SuccessToast;
