'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/src/contexts/AuthContext';
import { AIChatWidget } from '@/src/components/ai-chat/AIChatWidget';
import Link from 'next/link';

export default function DemoVibePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-slate-900">Vibe Coding Demo</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Try the AI assistant for code generation and guidance. For full project-integrated vibe coding, please sign in and open a project.
        </p>
      </div>

      <Card className="max-w-3xl mx-auto border-0 shadow-lg">
        <CardHeader>
          <CardTitle>AI Assistant</CardTitle>
          <CardDescription>Ask questions about architecture, code, or best practices</CardDescription>
        </CardHeader>
        <CardContent>
          {!isAuthenticated ? (
            <div className="text-center space-y-4">
              <p className="text-slate-600">
                You are exploring the AI assistant in demo mode. Sign in for a persistent chat and project-aware assistance.
              </p>
              <div className="flex gap-3 justify-center">
                <Link href="/login"><Button variant="outline">Sign in</Button></Link>
                <Link href="/register"><Button>Sign up</Button></Link>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-500 mb-4">You are signed in. Feel free to ask the assistant anything.</p>
          )}

          {/* The widget floats; include it so users can interact immediately */}
          <div className="mt-6">
            <AIChatWidget />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


