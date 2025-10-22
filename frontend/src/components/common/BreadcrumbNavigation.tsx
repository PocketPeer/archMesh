/**
 * Breadcrumb Navigation Component
 * 
 * Provides contextual navigation breadcrumbs for the application.
 * Shows the current location and allows easy navigation back to parent pages.
 */

import React from 'react';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[];
  className?: string;
}

const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({ 
  items, 
  className = '' 
}) => {
  // Always start with home
  const allItems = [
    {
      label: 'Home',
      href: '/',
      icon: <Home className="h-4 w-4" />
    },
    ...items
  ];

  return (
    <nav className={`flex items-center space-x-1 text-sm ${className}`} aria-label="Breadcrumb">
      {allItems.map((item, index) => {
        const isLast = index === allItems.length - 1;
        const isFirst = index === 0;

        return (
          <React.Fragment key={index}>
            {!isFirst && (
              <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
            )}
            
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
              >
                {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                <span className="truncate">{item.label}</span>
              </Link>
            ) : (
              <span 
                className={`flex items-center gap-1 ${
                  isLast 
                    ? 'text-gray-900 font-medium' 
                    : 'text-gray-600'
                }`}
              >
                {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                <span className="truncate">{item.label}</span>
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

// Helper function to generate breadcrumbs for common pages
export const generateBreadcrumbs = {
  home: (): BreadcrumbItem[] => [],
  
  projects: (): BreadcrumbItem[] => [
    { label: 'Projects', href: '/projects' }
  ],
  
  project: (projectId: string, projectName?: string): BreadcrumbItem[] => [
    { label: 'Projects', href: '/projects' },
    { 
      label: projectName || `Project ${projectId}`, 
      href: `/projects/${projectId}` 
    }
  ],
  
  projectUpload: (projectId: string, projectName?: string): BreadcrumbItem[] => [
    { label: 'Projects', href: '/projects' },
    { 
      label: projectName || `Project ${projectId}`, 
      href: `/projects/${projectId}` 
    },
    { label: 'Upload Requirements' }
  ],
  
  workflow: (projectId: string, sessionId: string, projectName?: string): BreadcrumbItem[] => [
    { label: 'Projects', href: '/projects' },
    { 
      label: projectName || `Project ${projectId}`, 
      href: `/projects/${projectId}` 
    },
    { label: 'Workflow', href: `/projects/${projectId}/workflows/${sessionId}` }
  ],
  
  demo: (demoType: string): BreadcrumbItem[] => [
    { label: 'Demos', href: '/demos' },
    { label: demoType.charAt(0).toUpperCase() + demoType.slice(1) }
  ]
};

export default BreadcrumbNavigation;

