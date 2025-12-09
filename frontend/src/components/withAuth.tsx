import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';

const withAuth = (WrappedComponent: React.ComponentType) => {
  const AuthComponent = (props: any) => {
    const router = useRouter();
    const { user, loading } = useAuth();

    useEffect(() => {
      if (!loading && !user) {
        router.push('/login');
      }
    }, [user, loading, router]);

    if (loading || !user) {
      return <div>Loading...</div>; // Or a more sophisticated loading component
    }

    return <WrappedComponent {...props} />;
  };

  AuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return AuthComponent;
};

export default withAuth;
