"use client";

import { useState } from 'react';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Lock, Save } from 'lucide-react';
import apiClient from '@/lib/api-client';

function SettingsPage() {
  const [accountInfo, setAccountInfo] = useState({
    firstName: 'Sundar',
    lastName: 'Gurung',
    email: 'sundargurung360@gmail.com',
    contactNumber: '',
    position: ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpdateAccountInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setIsLoading(true);

    try {
      // TODO: Implement actual API call when backend endpoint is ready
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      setMessage({ type: 'success', text: 'Account information updated successfully!' });
    } catch (error) {
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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
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
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="account" className="gap-2">
            <User className="h-4 w-4" />
            Account Information
          </TabsTrigger>
          <TabsTrigger value="password" className="gap-2">
            <Lock className="h-4 w-4" />
            Change Password
          </TabsTrigger>
        </TabsList>

        {/* Account Information Tab */}
        <TabsContent value="account">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-6 text-gray-900">Account Information</h2>

            <form onSubmit={handleUpdateAccountInfo} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    type="text"
                    value={accountInfo.firstName}
                    onChange={(e) =>
                      setAccountInfo({ ...accountInfo, firstName: e.target.value })
                    }
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    type="text"
                    value={accountInfo.lastName}
                    onChange={(e) =>
                      setAccountInfo({ ...accountInfo, lastName: e.target.value })
                    }
                    className="h-11"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={accountInfo.email}
                  onChange={(e) => setAccountInfo({ ...accountInfo, email: e.target.value })}
                  className="h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contactNumber">Contact Number</Label>
                <Input
                  id="contactNumber"
                  type="tel"
                  placeholder="Enter your contact number"
                  value={accountInfo.contactNumber}
                  onChange={(e) =>
                    setAccountInfo({ ...accountInfo, contactNumber: e.target.value })
                  }
                  className="h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Position</Label>
                <Input
                  id="position"
                  type="text"
                  placeholder="Enter your position"
                  value={accountInfo.position}
                  onChange={(e) =>
                    setAccountInfo({ ...accountInfo, position: e.target.value })
                  }
                  className="h-11"
                />
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
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-6 text-gray-900">Change Password</h2>

            <form onSubmit={handleChangePassword} className="space-y-4">
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
