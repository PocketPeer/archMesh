"use client";

import React from 'react';

export interface ModeOption {
  value: 'greenfield' | 'brownfield';
  label: string;
  description: string;
  icon: string;
}

interface ModeSelectorProps {
  value: 'greenfield' | 'brownfield';
  onChange: (mode: 'greenfield' | 'brownfield') => void;
  options?: ModeOption[];
  disabled?: boolean;
  className?: string;
}

const defaultOptions: ModeOption[] = [
  {
    value: 'greenfield',
    label: 'New Project (Greenfield)',
    description: 'Start fresh with a new system architecture',
    icon: '🌱'
  },
  {
    value: 'brownfield',
    label: 'Existing System (Brownfield)',
    description: 'Integrate new features with existing architecture',
    icon: '🏗️'
  }
];

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  value,
  onChange,
  options = defaultOptions,
  disabled = false,
  className = ''
}) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Project Type
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Choose whether you're building a new system or integrating with an existing one.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {options.map((option) => (
          <div
            key={option.value}
            className={`
              relative p-4 border-2 rounded-lg cursor-pointer transition-all duration-200
              ${value === option.value
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400'
                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            onClick={() => !disabled && onChange(option.value)}
          >
            {/* Selection indicator */}
            {value === option.value && (
              <div className="absolute top-3 right-3">
                <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}

            {/* Option content */}
            <div className="flex items-start space-x-3">
              <div className="text-2xl">{option.icon}</div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                  {option.label}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {option.description}
                </p>
              </div>
            </div>

            {/* Mode-specific features */}
            {option.value === 'greenfield' && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center space-x-1 mb-1">
                    <span className="w-1 h-1 bg-green-500 rounded-full"></span>
                    <span>Clean slate design</span>
                  </div>
                  <div className="flex items-center space-x-1 mb-1">
                    <span className="w-1 h-1 bg-green-500 rounded-full"></span>
                    <span>Latest technologies</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-1 h-1 bg-green-500 rounded-full"></span>
                    <span>No legacy constraints</span>
                  </div>
                </div>
              </div>
            )}

            {option.value === 'brownfield' && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center space-x-1 mb-1">
                    <span className="w-1 h-1 bg-orange-500 rounded-full"></span>
                    <span>GitHub integration</span>
                  </div>
                  <div className="flex items-center space-x-1 mb-1">
                    <span className="w-1 h-1 bg-orange-500 rounded-full"></span>
                    <span>Existing architecture analysis</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="w-1 h-1 bg-orange-500 rounded-full"></span>
                    <span>Integration planning</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Help text */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
        <div className="flex items-start space-x-2">
          <svg className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            <p className="font-medium mb-1">Need help choosing?</p>
            <p>
              <strong>Greenfield:</strong> Perfect for new applications, startups, or when you want to use the latest technologies without constraints.
            </p>
            <p className="mt-1">
              <strong>Brownfield:</strong> Ideal when you need to add features to existing systems, modernize legacy applications, or integrate with current infrastructure.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModeSelector;
