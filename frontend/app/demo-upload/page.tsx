'use client';

import { useState } from 'react';
import { DocumentUploader } from '@/components/DocumentUploader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export default function DemoUploadPage() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const handleUploadComplete = (file: File) => {
    setUploadedFiles(prev => [...prev, file]);
    toast.success(`File ${file.name} uploaded successfully!`);
  };

  const clearFiles = () => {
    setUploadedFiles([]);
    toast.info('Uploaded files cleared');
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-slate-900">Document Uploader Demo</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Test the drag-and-drop document uploader component with file validation, 
          progress tracking, and beautiful UI.
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        <DocumentUploader 
          onUploadComplete={handleUploadComplete}
          projectId="demo-project-123"
        />
      </div>

      {/* Upload Results */}
      {uploadedFiles.length > 0 && (
        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Upload Results</CardTitle>
                <CardDescription>
                  {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} successfully uploaded
                </CardDescription>
              </div>
              <Button variant="outline" onClick={clearFiles}>
                Clear All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">
                      {file.name.split('.').pop()?.toLowerCase() === 'pdf' ? '📄' :
                       file.name.split('.').pop()?.toLowerCase() === 'docx' ? '📝' :
                       file.name.split('.').pop()?.toLowerCase() === 'pptx' ? '📊' :
                       file.name.split('.').pop()?.toLowerCase() === 'txt' ? '📃' : '📁'}
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">{file.name}</p>
                      <p className="text-sm text-slate-600">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Badge variant="default">Uploaded</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Component Features */}
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Component Features</CardTitle>
          <CardDescription>
            The DocumentUploader component includes the following features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="font-semibold text-slate-900">Core Functionality</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Drag and drop file upload</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>File type validation</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>File size validation (50MB max)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Upload progress tracking</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Multiple file support</span>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-slate-900">UI/UX Features</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Beautiful drag-and-drop zone</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>File type icons and badges</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Progress bars and status indicators</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Toast notifications</span>
                </li>
                <li className="flex items-center space-x-2">
                  <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Responsive design</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Supported File Types */}
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Supported File Types</CardTitle>
          <CardDescription>
            The component accepts the following file formats
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-medium text-slate-900">Text Files</h4>
              <div className="space-y-1">
                <Badge variant="secondary">.txt</Badge>
                <Badge variant="secondary">.md</Badge>
                <Badge variant="secondary">.rst</Badge>
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-slate-900">Documents</h4>
              <div className="space-y-1">
                <Badge variant="secondary">.pdf</Badge>
                <Badge variant="secondary">.docx</Badge>
                <Badge variant="secondary">.doc</Badge>
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-slate-900">Presentations</h4>
              <div className="space-y-1">
                <Badge variant="secondary">.pptx</Badge>
                <Badge variant="secondary">.ppt</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
