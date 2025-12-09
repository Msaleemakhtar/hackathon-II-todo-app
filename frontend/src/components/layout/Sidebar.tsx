"use client";

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { LayoutDashboard, Star, CheckSquare, FolderOpen, Settings, HelpCircle, LogOut } from 'lucide-react';

const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();

  // Mock user data - will be replaced with actual auth
  const user = {
    name: "John Doe",
    email: "john.doe@example.com",
    avatar: "",
    initials: "JD"
  };

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Vital Task", href: "/vital-tasks", icon: Star },
    { label: "My Task", href: "/my-tasks", icon: CheckSquare },
    { label: "Task Categories", href: "/categories", icon: FolderOpen },
    { label: "Settings", href: "/settings", icon: Settings },
    { label: "Help", href: "/help", icon: HelpCircle },
  ];

  const handleLogout = () => {
    // TODO: Implement logout logic
    router.push('/login');
  };

  return (
    <div className="w-64 h-screen bg-coral flex flex-col text-white">
      {/* User Profile Section */}
      <div className="p-6 border-b border-coral-600">
        <div className="flex items-center space-x-3 mb-2">
          <Avatar className="h-12 w-12 border-2 border-white">
            <AvatarImage src={user.avatar} alt={user.name} />
            <AvatarFallback className="bg-coral-700 text-white">{user.initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 overflow-hidden">
            <h3 className="font-semibold text-sm truncate">{user.name}</h3>
            <p className="text-xs text-coral-100 truncate">{user.email}</p>
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
          className="w-full justify-start text-white hover:bg-coral-600 hover:text-white"
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;
