"use client";

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useUIStore } from '@/store/ui-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, Bell, Settings } from 'lucide-react';

const Header = () => {
  const router = useRouter();
  const { searchTerm, setSearchTerm } = useUIStore();
  const [currentDate, setCurrentDate] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const notificationRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Format: Tuesday 20/06/2023
    const formatDate = () => {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const now = new Date();
      const dayName = days[now.getDay()];
      const day = String(now.getDate()).padStart(2, '0');
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const year = now.getFullYear();
      return `${dayName} ${day}/${month}/${year}`;
    };
    setCurrentDate(formatDate());
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showNotifications]);

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
  };

  const handleSettingsClick = () => {
    router.push('/settings');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex items-center space-x-2 flex-1 max-w-xl">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder="Search your task here..."
              className="pr-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button
              size="sm"
              variant="ghost"
              className="absolute right-0 top-0 h-full px-3"
            >
              <Search className="h-4 w-4 text-gray-500" />
            </Button>
          </div>
        </div>

        {/* Right Side Icons and Date */}
        <div className="flex items-center space-x-6">
          {/* Notification Icon */}
          <div className="relative" ref={notificationRef}>
            <Button
              size="sm"
              variant="ghost"
              className="relative p-2"
              onClick={handleNotificationClick}
            >
              <Bell className="h-5 w-5 text-gray-600" />
              {/* Notification badge */}
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </Button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  <div className="p-4 hover:bg-gray-50 border-b border-gray-100 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 bg-coral rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">New task assigned</p>
                        <p className="text-xs text-gray-500 mt-1">You have been assigned a new task "Complete project documentation"</p>
                        <p className="text-xs text-gray-400 mt-1">2 hours ago</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 hover:bg-gray-50 border-b border-gray-100 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 bg-gray-300 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Task deadline approaching</p>
                        <p className="text-xs text-gray-500 mt-1">Task "Review code changes" is due tomorrow</p>
                        <p className="text-xs text-gray-400 mt-1">5 hours ago</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 hover:bg-gray-50 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 bg-gray-300 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Task completed</p>
                        <p className="text-xs text-gray-500 mt-1">You completed "Update user interface"</p>
                        <p className="text-xs text-gray-400 mt-1">1 day ago</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 border-t border-gray-200 text-center">
                  <button className="text-sm text-coral hover:text-coral-600 font-medium">
                    View all notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Settings Icon */}
          <Button
            size="sm"
            variant="ghost"
            className="p-2"
            onClick={handleSettingsClick}
          >
            <Settings className="h-5 w-5 text-gray-600" />
          </Button>

          {/* Current Date */}
          <div className="text-sm font-medium text-gray-700">
            {currentDate}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
