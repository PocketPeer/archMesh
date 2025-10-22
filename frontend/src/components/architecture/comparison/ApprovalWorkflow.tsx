"use client";

/**
 * Approval Workflow Component.
 * 
 * Handles the approval process for architecture changes with
 * approval history, comments, and decision tracking.
 */

import React, { useState, useCallback } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  MessageSquare, 
  Clock, 
  User, 
  Calendar,
  Send,
  AlertTriangle,
  FileText,
  ThumbsUp,
  ThumbsDown,
  Edit
} from 'lucide-react';
import { 
  ApprovalWorkflowProps, 
  ApprovalDecision, 
  ApprovalHistory 
} from '../../../types/architecture-comparison';

export const ApprovalWorkflow: React.FC<ApprovalWorkflowProps> = ({
  onApprove,
  onReject,
  onRequestChanges,
  currentApprover,
  approvalHistory,
  className = '',
}) => {
  const [decision, setDecision] = useState<'approve' | 'reject' | 'changes_requested' | null>(null);
  const [comments, setComments] = useState('');
  const [conditions, setConditions] = useState<string[]>(['']);
  const [timeline, setTimeline] = useState({
    startDate: '',
    endDate: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle decision submission
  const handleSubmit = useCallback(async () => {
    if (!decision || !comments.trim()) return;

    setIsSubmitting(true);

    try {
      const approvalDecision: ApprovalDecision = {
        approved: decision === 'approve',
        approver: currentApprover || 'Current User',
        comments: comments.trim(),
        conditions: conditions.filter(c => c.trim()),
        timeline: timeline.startDate && timeline.endDate ? timeline : undefined,
      };

      if (decision === 'approve') {
        onApprove(approvalDecision);
      } else if (decision === 'reject') {
        onReject(comments.trim());
      } else if (decision === 'changes_requested') {
        onRequestChanges(comments.trim());
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [decision, comments, conditions, timeline, currentApprover, onApprove, onReject, onRequestChanges]);

  // Add condition
  const addCondition = useCallback(() => {
    setConditions(prev => [...prev, '']);
  }, []);

  // Update condition
  const updateCondition = useCallback((index: number, value: string) => {
    setConditions(prev => prev.map((c, i) => i === index ? value : c));
  }, []);

  // Remove condition
  const removeCondition = useCallback((index: number) => {
    setConditions(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'changes_requested': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'changes_requested': return <Edit className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Approval Workflow</h2>
        <p className="text-sm text-gray-600 mt-1">
          Review and approve architecture changes
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Current Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Current Status</h3>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-700">Pending Review</span>
            </div>
            {currentApprover && (
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">Assigned to: {currentApprover}</span>
              </div>
            )}
          </div>
        </div>

        {/* Decision Actions */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Make Decision</h3>
          
          {/* Decision Buttons */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <button
              onClick={() => setDecision('approve')}
              className={`flex items-center justify-center space-x-2 p-3 rounded-lg border-2 transition-colors ${
                decision === 'approve'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-green-300 text-gray-600'
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              <span className="text-sm font-medium">Approve</span>
            </button>

            <button
              onClick={() => setDecision('changes_requested')}
              className={`flex items-center justify-center space-x-2 p-3 rounded-lg border-2 transition-colors ${
                decision === 'changes_requested'
                  ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                  : 'border-gray-200 hover:border-yellow-300 text-gray-600'
              }`}
            >
              <Edit className="w-4 h-4" />
              <span className="text-sm font-medium">Request Changes</span>
            </button>

            <button
              onClick={() => setDecision('reject')}
              className={`flex items-center justify-center space-x-2 p-3 rounded-lg border-2 transition-colors ${
                decision === 'reject'
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-gray-200 hover:border-red-300 text-gray-600'
              }`}
            >
              <ThumbsDown className="w-4 h-4" />
              <span className="text-sm font-medium">Reject</span>
            </button>
          </div>

          {/* Comments */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comments *
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Provide detailed feedback on the proposed changes..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
          </div>

          {/* Conditions (for approval) */}
          {decision === 'approve' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Conditions (Optional)
              </label>
              <div className="space-y-2">
                {conditions.map((condition, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={condition}
                      onChange={(e) => updateCondition(index, e.target.value)}
                      placeholder="Enter condition..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {conditions.length > 1 && (
                      <button
                        onClick={() => removeCondition(index)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={addCondition}
                  className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  <span>+ Add Condition</span>
                </button>
              </div>
            </div>
          )}

          {/* Timeline (for approval) */}
          {decision === 'approve' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Implementation Timeline (Optional)
              </label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={timeline.startDate}
                    onChange={(e) => setTimeline(prev => ({ ...prev, startDate: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">End Date</label>
                  <input
                    type="date"
                    value={timeline.endDate}
                    onChange={(e) => setTimeline(prev => ({ ...prev, endDate: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!decision || !comments.trim() || isSubmitting}
            className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-colors ${
              decision === 'approve'
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : decision === 'reject'
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-yellow-600 hover:bg-yellow-700 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isSubmitting ? (
              <Clock className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>
              {isSubmitting
                ? 'Submitting...'
                : decision === 'approve'
                ? 'Approve Changes'
                : decision === 'reject'
                ? 'Reject Changes'
                : 'Request Changes'}
            </span>
          </button>
        </div>

        {/* Approval History */}
        {approvalHistory.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="font-medium text-gray-900 mb-3">Approval History</h3>
            <div className="space-y-3">
              {approvalHistory.map((history) => (
                <div key={history.id} className="border-l-4 border-gray-200 pl-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div className={`p-1 rounded-full ${getStatusColor(history.decision)}`}>
                        {getStatusIcon(history.decision)}
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {history.approver}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(history.timestamp).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">{history.comments}</p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Version: {history.version}</span>
                    <span className="capitalize">{history.decision.replace('_', ' ')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Guidelines */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
          <h3 className="font-medium text-blue-900 mb-2 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4" />
            <span>Review Guidelines</span>
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Review all changes and their impact on existing systems</li>
            <li>• Consider breaking changes and migration requirements</li>
            <li>• Ensure adequate testing and rollback plans are in place</li>
            <li>• Verify compliance with architectural standards</li>
            <li>• Check for security and performance implications</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ApprovalWorkflow;
