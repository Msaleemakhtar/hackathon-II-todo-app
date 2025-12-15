"use client";

import { memo, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { LayoutDashboard, Star, CheckSquare, FolderOpen, Settings, HelpCircle, LogOut, X } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { authClient } from '@/lib/auth';
import { useUIStore } from '@/store/ui-store';

const SidebarComponent = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user } = useAuth();
  const { isSidebarOpen, setIsSidebarOpen } = useUIStore();

  // Generate initials from user name or email
  const getInitials = (name: string | null, email: string) => {
    if (name && name.trim().length >= 2) {
      // Get first two characters of name
      return name.trim().substring(0, 2).toUpperCase();
    }
    // Fallback to first two characters of email
    return email.substring(0, 2).toUpperCase();
  };

  const initials = user ? getInitials(user.name, user.email) : "??";
  const displayName = user?.name || user?.email || "User";
  const displayEmail = user?.email || "";

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Vital Task", href: "/vital-tasks", icon: Star },
    { label: "My Task", href: "/my-tasks", icon: CheckSquare },
    { label: "Task Categories", href: "/categories", icon: FolderOpen },
    { label: "Settings", href: "/settings", icon: Settings },
    { label: "Help", href: "/help", icon: HelpCircle },
  ];

  const handleLogout = async () => {
    try {
      await authClient.signOut();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Force redirect even if logout fails
      router.push('/login');
    }
  };

  // Close sidebar on route change for mobile
  useEffect(() => {
    setIsSidebarOpen(false);
  }, [pathname, setIsSidebarOpen]);

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const sidebar = document.getElementById('mobile-sidebar');
      const menuButton = document.getElementById('mobile-menu-button');
      if (isSidebarOpen && sidebar && !sidebar.contains(e.target as Node) && !menuButton?.contains(e.target as Node)) {
        setIsSidebarOpen(false);
      }
    };

    if (isSidebarOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isSidebarOpen, setIsSidebarOpen]);

  return (
    <>
      {/* Backdrop for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        id="mobile-sidebar"
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 h-screen bg-coral flex flex-col text-white
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Close button for mobile */}
        <div className="lg:hidden flex justify-end p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(false)}
            className="text-white hover:bg-coral-600"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* User Profile Section */}
        <div className="p-6 border-b border-coral-600">
          <div className="flex items-center space-x-3 mb-2">
            <Avatar className="h-12 w-12 border-2 border-white">
              <AvatarImage src="" alt={displayName} />
              <AvatarFallback className="bg-coral-700 text-white font-semibold">{initials}</AvatarFallback>
            </Avatar>
            <div className="flex-1 overflow-hidden">
              <h3 className="font-semibold text-sm truncate">{displayName}</h3>
              <p className="text-xs text-coral-100 truncate">{displayEmail}</p>
            </div>
          </div>
        </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-white text-coral font-medium'
                    : 'text-white hover:bg-coral-600'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Logout Button */}
      <div className="p-4 border-t border-coral-600">
        <Button
          onClick={handleLogout}
          variant="ghost"
          className="w-full text-white hover:bg-coral-600 hover:text-white flex items-center justify-center space-x-2"
        >
          <LogOut className="h-4 w-4" />
          <span className="text-sm font-medium">Logout</span>
        </Button>
      </div>
      </div>
    </>
  );
};

// Memoize Sidebar to prevent unnecessary re-renders on navigation
const Sidebar = memo(SidebarComponent);
Sidebar.displayName = 'Sidebar';

export default Sidebar;
