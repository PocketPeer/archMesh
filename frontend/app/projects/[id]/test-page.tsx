'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function TestProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          <h1 className="text-3xl font-bold text-slate-900">Project Detail Page - REDESIGNED</h1>
          <p className="text-slate-600">Project ID: {projectId}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Project Header</h3>
              <p className="text-slate-600">Project information, stats, and quick actions</p>
            </div>
            
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Workflow Dashboard</h3>
              <p className="text-slate-600">Current workflow, history, and analytics</p>
            </div>
            
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Results & Outputs</h3>
              <p className="text-slate-600">Requirements, architecture, and documents</p>
            </div>
            
            <div className="p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Collaboration</h3>
              <p className="text-slate-600">Team, AI chat, and notifications</p>
            </div>
          </div>
          
          <div className="text-center">
            <button 
              onClick={() => router.push('/projects')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Back to Projects
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
