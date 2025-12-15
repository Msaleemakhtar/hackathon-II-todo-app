"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Sparkles, CheckCircle2, Star, Zap, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function WelcomePage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coral mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if user is authenticated (redirect in progress)
  if (user) {
    return null;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-coral-50 via-purple-50 to-blue-50 relative overflow-hidden">
      {/* Animated background decorations */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-coral-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center px-6 max-w-4xl">
        {/* Sparkles icon */}
        <div className="flex justify-center mb-6 animate-bounce">
          <div className="relative">
            <Sparkles className="w-16 h-16 text-coral-500" strokeWidth={1.5} />
            <Star className="w-6 h-6 text-yellow-400 absolute -top-2 -right-2 animate-spin-slow" />
            <Zap className="w-6 h-6 text-purple-500 absolute -bottom-2 -left-2 animate-pulse" />
          </div>
        </div>

        {/* Main heading with gradient */}
        <h1 className="text-6xl md:text-7xl font-extrabold mb-4 leading-tight">
          <span className="bg-gradient-to-r from-coral-500 via-purple-500 to-blue-500 bg-clip-text text-transparent animate-gradient">
            Welcome to
          </span>
          <br />
          <span className="bg-gradient-to-r from-blue-600 via-coral-600 to-purple-600 bg-clip-text text-transparent animate-gradient-reverse">
            Task Dashboard
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-gray-600 mb-8 font-medium">
          Organize your life, one task at a time ✨
        </p>

        {/* Call to action buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Button
            asChild
            size="lg"
            className="bg-coral hover:bg-coral-600 text-white px-8 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            <Link href="/signup" className="gap-2">
              Get Started
              <ArrowRight className="w-5 h-5" />
            </Link>
          </Button>

          <Button
            asChild
            variant="outline"
            size="lg"
            className="border-2 border-coral text-coral hover:bg-coral hover:text-white px-8 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            <Link href="/login">
              Sign In
            </Link>
          </Button>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12 max-w-3xl mx-auto">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-coral-100 hover:scale-105 transform transition-transform">
            <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <h3 className="font-bold text-coral-700 mb-2">Stay Organized</h3>
            <p className="text-sm text-gray-600">Keep track of all your tasks in one place</p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-purple-100 hover:scale-105 transform transition-transform">
            <Star className="w-10 h-10 text-purple-500 mx-auto mb-3" />
            <h3 className="font-bold text-purple-700 mb-2">Prioritize</h3>
            <p className="text-sm text-gray-600">Focus on what matters most</p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-blue-100 hover:scale-105 transform transition-transform">
            <Zap className="w-10 h-10 text-blue-500 mx-auto mb-3" />
            <h3 className="font-bold text-blue-700 mb-2">Achieve More</h3>
            <p className="text-sm text-gray-600">Complete tasks efficiently and effectively</p>
          </div>
        </div>
      </div>

      {/* Add custom animations to globals.css */}
      <style jsx>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
        .animate-gradient-reverse {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite reverse;
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
      `}</style>
    </div>
  );
}
