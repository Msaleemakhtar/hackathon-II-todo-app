"use client";
import withAuth from '@/components/withAuth';

function Home() {
  return (
    <div className="flex items-center justify-center h-full">
      <h1 className="text-4xl font-bold">Welcome to the Task Dashboard!</h1>
    </div>
  );
}

export default withAuth(Home);
