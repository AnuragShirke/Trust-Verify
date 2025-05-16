import React from 'react';
import { useNavigate } from 'react-router-dom';
import UserProfile from '@/components/auth/UserProfile';
import { useAuth } from '@/context/AuthContext';

export default function ProfilePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  
  // Redirect if not logged in
  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    return (
      <div className="container max-w-screen-xl mx-auto px-4 py-8">
        <p className="text-center">Loading...</p>
      </div>
    );
  }

  return (
    <div className="container max-w-screen-xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Your Profile</h1>
      <UserProfile />
    </div>
  );
}
