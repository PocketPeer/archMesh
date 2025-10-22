import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/src/contexts/AuthContext';
import SimplifiedNavigation from '@/components/SimplifiedNavigation';
import HydrationFix from '@/components/HydrationFix';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ArchMesh - AI-Powered Architecture Guidance',
  description: 'Get intelligent architecture guidance, generate diagrams, and create implementation plans in minutes.',
  keywords: ['architecture', 'software design', 'microservices', 'system design', 'AI guidance'],
  authors: [{ name: 'ArchMesh Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning={true}>
        <HydrationFix />
        <AuthProvider>
          <div className="min-h-screen bg-slate-50">
            <SimplifiedNavigation />
            <main className="flex-1">
              {children}
            </main>
          </div>
          <Toaster 
            position="top-right"
            expand={true}
            richColors={true}
            closeButton={true}
          />
        </AuthProvider>
      </body>
    </html>
  );
}