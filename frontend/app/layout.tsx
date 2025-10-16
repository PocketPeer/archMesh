import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ArchMesh PoC - AI-Powered Architecture Design",
  description: "Transform business requirements into system architectures using AI agents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
          <nav className="border-b bg-white/80 backdrop-blur-sm">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600"></div>
                  <h1 className="text-xl font-bold text-slate-900">ArchMesh</h1>
                </div>
                <div className="flex items-center space-x-4">
                  <a
                    href="/projects"
                    className="text-slate-600 hover:text-slate-900 transition-colors"
                  >
                    Projects
                  </a>
                  <a
                    href="/"
                    className="text-slate-600 hover:text-slate-900 transition-colors"
                  >
                    Home
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
        <Toaster />
      </body>
    </html>
  );
}