'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/src/contexts/AuthContext';
import ClientNotificationCenter from './ClientNotificationCenter';
import { 
  UserIcon, 
  LogOutIcon, 
  SettingsIcon, 
  HomeIcon, 
  FolderIcon,
  MenuIcon,
  XIcon
} from 'lucide-react';

export function Navigation() {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  if (isLoading) {
    return (
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600"></div>
              <h1 className="text-xl font-bold text-slate-900">ArchMesh</h1>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="border-b bg-white/80 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600"></div>
            <h1 className="text-xl font-bold text-slate-900">ArchMesh</h1>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              href="/"
              className="text-slate-600 hover:text-slate-900 transition-colors flex items-center space-x-1"
            >
              <HomeIcon className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            {/* Demo Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2">
                  <span>Demos</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-56">
                <DropdownMenuItem asChild>
                  <Link href="/demo-upload">Document Upload Demo</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/demo-requirements">Requirements Analysis Demo</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/demo-architecture">Architecture Design Demo</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/demo-brownfield">Brownfield Analysis Demo</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/demo-vibe">Vibe Coding Demo</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {isAuthenticated && (
              <Link
                href="/projects"
                className="text-slate-600 hover:text-slate-900 transition-colors flex items-center space-x-1"
              >
                <FolderIcon className="h-4 w-4" />
                <span>Projects</span>
              </Link>
            )}

            <ClientNotificationCenter />

            {/* User Menu */}
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center space-x-2">
                    <UserIcon className="h-4 w-4" />
                    <span className="hidden sm:inline">{user?.name || user?.email}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium">{user?.name}</p>
                      <p className="w-[200px] truncate text-sm text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/my-account" className="flex items-center">
                      <SettingsIcon className="mr-2 h-4 w-4" />
                      <span>My Account</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                    <LogOutIcon className="mr-2 h-4 w-4" />
                    <span>Sign out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-2">
                <Link href="/login">
                  <Button variant="ghost">Sign in</Button>
                </Link>
                <Link href="/register">
                  <Button>Sign up</Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleMobileMenu}
              className="flex items-center space-x-2"
            >
              {isMobileMenuOpen ? (
                <XIcon className="h-4 w-4" />
              ) : (
                <MenuIcon className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t pt-4">
            <div className="flex flex-col space-y-4">
              <Link
                href="/"
                className="text-slate-600 hover:text-slate-900 transition-colors flex items-center space-x-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <HomeIcon className="h-4 w-4" />
                <span>Home</span>
              </Link>
              
              {isAuthenticated && (
                <Link
                  href="/projects"
                  className="text-slate-600 hover:text-slate-900 transition-colors flex items-center space-x-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <FolderIcon className="h-4 w-4" />
                  <span>Projects</span>
                </Link>
              )}

              {isAuthenticated ? (
                <div className="space-y-2">
                  <div className="px-2 py-1 text-sm text-slate-500">
                    {user?.name} ({user?.email})
                  </div>
                  <Link
                    href="/my-account"
                    className="text-slate-600 hover:text-slate-900 transition-colors flex items-center space-x-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <SettingsIcon className="h-4 w-4" />
                    <span>My Account</span>
                  </Link>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      handleLogout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full justify-start text-red-600"
                  >
                    <LogOutIcon className="mr-2 h-4 w-4" />
                    <span>Sign out</span>
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col space-y-2">
                  <Link href="/login" onClick={() => setIsMobileMenuOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start">
                      Sign in
                    </Button>
                  </Link>
                  <Link href="/register" onClick={() => setIsMobileMenuOpen(false)}>
                    <Button className="w-full">
                      Sign up
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
