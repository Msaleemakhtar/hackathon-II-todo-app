"use client";

import { useState, useEffect } from 'react';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Lock, Save } from 'lucide-react';
import apiClient from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';
import { Skeleton } from '@/components/ui/skeleton';

function SettingsPage() {
  const { user } = useAuth();
  const [accountInfo, setAccountInfo] = useState({
    name: '',
    email: ''
  });
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch user profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user?.id) return;

      try {
        const response = await apiClient.get(`/v1/${user.id}/profile`);
        setAccountInfo({
          name: response.data.name || '',
          email: response.data.email || ''
        });
      } catch (error) {
        console.error('Failed to fetch profile:', error);
        setMessage({ type: 'error', text: 'Failed to load profile data.' });
      } finally {
        setIsLoadingProfile(false);
      }
    };

    fetchProfile();
  }, [user?.id]);

  const handleUpdateAccountInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setIsLoading(true);

    if (!user?.id) {
      setMessage({ type: 'error', text: 'User not authenticated.' });
      setIsLoading(false);
      return;
    }

    try {
      await apiClient.patch(`/v1/${user.id}/profile`, {
        name: accountInfo.name
      });

      setMessage({ type: 'success', text: 'Account information updated successfully!' });
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: 'Failed to update account information.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match!' });
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters long!' });
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement actual API call when backend endpoint is ready
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to change password.' });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoadingProfile) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header Skeleton */}
        <div className="mb-6 space-y-3">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-96" />
        </div>

        {/* Tabs Skeleton */}
        <div className="space-y-6">
          {/* Tab Buttons Skeleton */}
          <div className="flex gap-4">
            <Skeleton className="h-10 flex-1" />
            <Skeleton className="h-10 flex-1" />
          </div>

          {/* Tab Content Skeleton */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            {/* Title */}
            <Skeleton className="h-6 w-56 mb-6" />

            {/* Form Fields Skeleton */}
            <div className="space-y-6">
              {/* Name Field */}
              <div className="space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-11 w-full" />
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-11 w-full" />
                <Skeleton className="h-3 w-48" />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <Skeleton className="h-11 flex-1" />
                <Skeleton className="h-11 flex-1" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-sm md:text-base text-gray-600">Manage your account settings and preferences</p>
      </div>

      {/* Message Alert */}
      {message && (
        <div
          className={`mb-6 p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="account" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-4 md:mb-6">
          <TabsTrigger value="account" className="gap-1 md:gap-2 text-xs md:text-sm">
            <User className="h-3 w-3 md:h-4 md:w-4" />
            <span className="hidden sm:inline">Account Information</span>
            <span className="sm:hidden">Account</span>
          </TabsTrigger>
          <TabsTrigger value="password" className="gap-1 md:gap-2 text-xs md:text-sm">
            <Lock className="h-3 w-3 md:h-4 md:w-4" />
            <span className="hidden sm:inline">Change Password</span>
            <span className="sm:hidden">Password</span>
          </TabsTrigger>
        </TabsList>

        {/* Account Information Tab */}
        <TabsContent value="account">
          <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
            <h2 className="text-base md:text-lg font-semibold mb-4 md:mb-6 text-gray-900">Account Information</h2>

            <form onSubmit={handleUpdateAccountInfo} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  type="text"
                  value={accountInfo.name}
                  onChange={(e) =>
                    setAccountInfo({ ...accountInfo, name: e.target.value })
                  }
                  placeholder="Enter your name"
                  className="h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={accountInfo.email}
                  disabled
                  className="h-11 bg-gray-100 cursor-not-allowed"
                  title="Email cannot be changed"
                />
                <p className="text-xs text-gray-500">Email address cannot be changed</p>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 bg-coral hover:bg-coral-600 gap-2"
                >
                  <Save className="h-4 w-4" />
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button type="button" variant="outline" className="flex-1">
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        </TabsContent>

        {/* Change Password Tab */}
        <TabsContent value="password">
          <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
            <h2 className="text-base md:text-lg font-semibold mb-4 md:mb-6 text-gray-900">Change Password</h2>
            <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-lg mb-4">
              <p className="text-sm">Password management is handled through our authentication system. To change your password, please log out and use the &quot;Forgot Password&quot; feature on the login page.</p>
            </div>

            <form onSubmit={handleChangePassword} className="space-y-4" style={{ opacity: 0.6, pointerEvents: 'none' }}>
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input
                  id="currentPassword"
                  type="password"
                  placeholder="Enter current password"
                  value={passwordData.currentPassword}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, currentPassword: e.target.value })
                  }
                  required
                  className="h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  id="newPassword"
                  type="password"
                  placeholder="Enter new password"
                  value={passwordData.newPassword}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, newPassword: e.target.value })
                  }
                  required
                  className="h-11"
                />
                <p className="text-xs text-gray-500">Password must be at least 8 characters long</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm new password"
                  value={passwordData.confirmPassword}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, confirmPassword: e.target.value })
                  }
                  required
                  className="h-11"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 bg-coral hover:bg-coral-600"
                >
                  {isLoading ? 'Updating...' : 'Update Password'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() =>
                    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
                  }
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default withAuth(SettingsPage);
