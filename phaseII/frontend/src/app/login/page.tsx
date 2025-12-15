"use client";

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { signIn } from '@/lib/auth';

// Component that uses useSearchParams - must be wrapped in Suspense
const SessionExpiredNotice = ({ onSessionExpired }: { onSessionExpired: (message: string) => void }) => {
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check if redirected due to session expiration
    if (searchParams.get('session_expired') === 'true') {
      onSessionExpired('Your session has expired. Please sign in again.');
    }
  }, [searchParams, onSessionExpired]);

  return null;
};

const LoginForm = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSessionExpiredMessage(''); // Clear session expired message on submit
    setIsLoading(true);

    try {
      // Use Better Auth's email/password signIn method
      const result = await signIn.email({
        email: formData.email,
        password: formData.password,
      });

      // Check if sign in was successful
      if (result.error) {
        setError(result.error.message || 'Invalid email or password');
        setIsLoading(false);
        return;
      }

      // Redirect to dashboard on successful login
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-coral-50 to-orange-50">
      <Suspense fallback={null}>
        <SessionExpiredNotice onSessionExpired={setSessionExpiredMessage} />
      </Suspense>

      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
            <p className="text-gray-600">Sign in to continue to your dashboard</p>
          </div>

          {/* Session Expired Message */}
          {sessionExpiredMessage && (
            <div className="bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded-lg text-sm">
              {sessionExpiredMessage}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                className="h-11"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                className="h-11"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox id="remember" />
                <label htmlFor="remember" className="text-sm text-gray-600 cursor-pointer">
                  Remember me
                </label>
              </div>

              <Link href="/forgot-password" className="text-sm text-coral hover:text-coral-600">
                Forgot Password?
              </Link>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-coral hover:bg-coral-600 text-white h-11 text-base font-medium"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Sign Up Link */}
          <div className="text-center pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Don&apos;t have an account?{' '}
              <Link href="/signup" className="text-coral hover:text-coral-600 font-medium">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
