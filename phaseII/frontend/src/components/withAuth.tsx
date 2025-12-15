import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

const withAuth = (WrappedComponent: React.ComponentType) => {
  const AuthComponent = (props: any) => {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [isInitialLoad, setIsInitialLoad] = useState(true);

    useEffect(() => {
      if (!loading && !user) {
        router.push('/login');
      }

      // After first load completes, mark as no longer initial
      if (!loading) {
        setIsInitialLoad(false);
      }
    }, [user, loading, router]);

    // Only show loading spinner on initial page load, not on navigation
    if (loading && isInitialLoad) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coral mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      );
    }

    // If not loading and no user, don't render anything (redirect is in progress)
    if (!loading && !user) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };

  AuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return AuthComponent;
};

export default withAuth;
