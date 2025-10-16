'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';

interface DocumentUploaderProps {
  onUploadComplete: (file: File) => void;
  projectId: string;
}

interface FileWithProgress extends File {
  progress?: number;
  status?: 'uploading' | 'completed' | 'error';
  error?: string;
}

const ACCEPTED_FILE_TYPES = {
  'text/plain': ['.txt'],
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'text/markdown': ['.md'],
  'text/x-rst': ['.rst'],
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export function DocumentUploader({ onUploadComplete, projectId }: DocumentUploaderProps) {
  const [uploadedFiles, setUploadedFiles] = useState<FileWithProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(({ file, errors }) => {
        errors.forEach((error: any) => {
          if (error.code === 'file-too-large') {
            toast.error(`${file.name} is too large. Maximum size is 50MB.`);
          } else if (error.code === 'file-invalid-type') {
            toast.error(`${file.name} is not a supported file type.`);
          } else {
            toast.error(`${file.name}: ${error.message}`);
          }
        });
      });
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      const newFiles: FileWithProgress[] = acceptedFiles.map(file => ({
        ...file,
        progress: 0,
        status: 'uploading' as const,
      }));

      setUploadedFiles(prev => [...prev, ...newFiles]);
      setIsUploading(true);

      // Simulate upload progress for each file
      newFiles.forEach((file, index) => {
        simulateUpload(file, index);
      });
    }
  }, []);

  const simulateUpload = (file: FileWithProgress, index: number) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        setUploadedFiles(prev => 
          prev.map(f => 
            f === file 
              ? { ...f, progress: 100, status: 'completed' as const }
              : f
          )
        );

        // Call the completion callback
        onUploadComplete(file);
        toast.success(`${file.name} uploaded successfully!`);
        
        // Check if all uploads are complete
        setTimeout(() => {
          setUploadedFiles(prev => {
            const allComplete = prev.every(f => f.status === 'completed');
            if (allComplete) {
              setIsUploading(false);
            }
            return prev;
          });
        }, 500);
      } else {
        setUploadedFiles(prev => 
          prev.map(f => 
            f === file 
              ? { ...f, progress }
              : f
          )
        );
      }
    }, 200);
  };

  const removeFile = (fileToRemove: FileWithProgress) => {
    setUploadedFiles(prev => prev.filter(f => f !== fileToRemove));
    toast.info(`${fileToRemove.name} removed`);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'pptx':
      case 'ppt':
        return '📊';
      case 'txt':
        return '📃';
      case 'md':
        return '📋';
      case 'rst':
        return '📖';
      default:
        return '📁';
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
    disabled: isUploading,
  });

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Requirements Document</CardTitle>
          <CardDescription>
            Drag and drop your requirements document or click to browse files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
              ${isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
              }
              ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            <div className="space-y-4">
              <div className="mx-auto h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center">
                {isDragActive ? (
                  <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                ) : (
                  <svg className="h-8 w-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                )}
              </div>
              <div>
                <p className="text-lg font-medium text-slate-900">
                  {isDragActive ? 'Drop files here' : 'Upload your document'}
                </p>
                <p className="text-sm text-slate-600 mt-1">
                  {isUploading ? 'Upload in progress...' : 'Click to browse or drag and drop'}
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {Object.keys(ACCEPTED_FILE_TYPES).map(type => (
                  <Badge key={type} variant="secondary" className="text-xs">
                    {ACCEPTED_FILE_TYPES[type as keyof typeof ACCEPTED_FILE_TYPES].join(', ')}
                  </Badge>
                ))}
              </div>
              <p className="text-xs text-slate-500">
                Maximum file size: 50MB
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Files</CardTitle>
            <CardDescription>
              {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} uploaded
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadedFiles.map((file, index) => (
                <div key={`${file.name}-${index}`} className="flex items-center space-x-4 p-4 border border-slate-200 rounded-lg">
                  <div className="text-2xl">
                    {getFileIcon(file)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        {file.name}
                      </p>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={
                            file.status === 'completed' ? 'default' :
                            file.status === 'error' ? 'destructive' : 'secondary'
                          }
                          className="text-xs"
                        >
                          {file.status === 'completed' ? 'Completed' :
                           file.status === 'error' ? 'Error' : 'Uploading'}
                        </Badge>
                        {file.status === 'completed' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(file)}
                            className="h-6 w-6 p-0 text-slate-400 hover:text-red-600"
                          >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs text-slate-500">
                        {formatFileSize(file.size)}
                      </p>
                      {file.status === 'uploading' && (
                        <p className="text-xs text-slate-500">
                          {Math.round(file.progress || 0)}%
                        </p>
                      )}
                    </div>
                    {file.status === 'uploading' && (
                      <div className="mt-2">
                        <Progress value={file.progress || 0} className="h-2" />
                      </div>
                    )}
                    {file.status === 'error' && file.error && (
                      <p className="text-xs text-red-600 mt-1">
                        {file.error}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* File Type Information */}
      <Card>
        <CardHeader>
          <CardTitle>Supported File Types</CardTitle>
          <CardDescription>
            We support the following document formats for requirements analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <h4 className="font-medium text-slate-900">Text Documents</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📃</span>
                  <span className="text-sm text-slate-600">TXT - Plain text files</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📋</span>
                  <span className="text-sm text-slate-600">MD - Markdown documents</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📖</span>
                  <span className="text-sm text-slate-600">RST - reStructuredText</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium text-slate-900">Office Documents</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📄</span>
                  <span className="text-sm text-slate-600">PDF - PDF documents</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📝</span>
                  <span className="text-sm text-slate-600">DOCX - Word documents</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">📊</span>
                  <span className="text-sm text-slate-600">PPTX - PowerPoint presentations</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-start space-x-2">
              <svg className="h-5 w-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-800">Tips for best results</p>
                <ul className="text-xs text-blue-700 mt-1 space-y-1">
                  <li>• Use clear, well-structured documents</li>
                  <li>• Include business goals, functional requirements, and constraints</li>
                  <li>• Maximum file size: 50MB</li>
                  <li>• Multiple files can be uploaded simultaneously</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
