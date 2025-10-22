'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BuildingIcon,
  SearchIcon,
  LinkIcon,
  BookOpenIcon,
  UserIcon,
  LogOutIcon,
  MenuIcon,
  XIcon,
  HomeIcon,
  SparklesIcon,
  SettingsIcon
} from 'lucide-react';
import { useAuth } from '@/src/contexts/AuthContext';

export default function SimplifiedNavigation() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const navigationItems = [
    {
      name: 'Home',
      href: '/',
      icon: <HomeIcon className="h-4 w-4" />,
      description: 'Get started with architecture guidance'
    },
    {
      name: 'Patterns',
      href: '/patterns',
      icon: <BookOpenIcon className="h-4 w-4" />,
      description: 'Browse architecture patterns and best practices'
    }
  ];

  const architectOptions = [
    {
      name: 'Design New Architecture',
      href: '/architecture/new',
      icon: <BuildingIcon className="h-5 w-5" />,
      color: 'text-blue-600',
      description: 'Create complete system architecture from requirements'
    },
    {
      name: 'Evaluate Existing',
      href: '/architecture/evaluate',
      icon: <SearchIcon className="h-5 w-5" />,
      color: 'text-purple-600',
      description: 'Analyze and improve your current system design'
    },
    {
      name: 'Plan Integration',
      href: '/architecture/integrate',
      icon: <LinkIcon className="h-5 w-5" />,
      color: 'text-green-600',
      description: 'Design integration strategies for existing systems'
    }
  ];

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <SparklesIcon className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-slate-900">ArchMesh</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-slate-600">
                  <UserIcon className="h-4 w-4" />
                  <span className="text-sm">{user?.name || 'User'}</span>
                </div>
                <Link href="/admin">
                  <Button variant="outline" size="sm">
                    <SettingsIcon className="h-4 w-4 mr-2" />
                    Admin
                  </Button>
                </Link>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOutIcon className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link href="/login">
                  <Button variant="outline" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="outline"
            size="sm"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <XIcon className="h-4 w-4" /> : <MenuIcon className="h-4 w-4" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 py-4">
            <div className="space-y-4">
              {navigationItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.icon}
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-sm text-slate-600">{item.description}</div>
                  </div>
                </Link>
              ))}

              <div className="pt-4 border-t border-slate-200">
                {isAuthenticated ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-slate-600 p-2">
                      <UserIcon className="h-4 w-4" />
                      <span>{user?.name || 'User'}</span>
                    </div>
                    <Link href="/admin" className="block">
                      <Button variant="outline" size="sm" className="w-full">
                        <SettingsIcon className="h-4 w-4 mr-2" />
                        Admin Panel
                      </Button>
                    </Link>
                    <Button variant="outline" size="sm" onClick={handleLogout} className="w-full">
                      <LogOutIcon className="h-4 w-4 mr-2" />
                      Sign Out
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Link href="/login" className="block">
                      <Button variant="outline" size="sm" className="w-full">
                        Sign In
                      </Button>
                    </Link>
                    <Link href="/register" className="block">
                      <Button size="sm" className="w-full">
                        Get Started
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions Bar */}
      {isAuthenticated && (
        <div className="bg-slate-50 border-t border-slate-200">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="text-sm text-slate-600">
                Quick Actions - Choose your architecture task:
              </div>
              <div className="flex space-x-2">
                {architectOptions.map((option) => (
                  <Link key={option.name} href={option.href}>
                    <Button variant="outline" size="sm" className="flex items-center space-x-2">
                      <div className={option.color}>{option.icon}</div>
                      <span className="hidden sm:inline">{option.name}</span>
                    </Button>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
