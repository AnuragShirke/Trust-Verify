import React from 'react';
import { useNavigate } from 'react-router-dom';
import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm';
import { useAuth } from '@/context/AuthContext';

export default function ForgotPasswordPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // Redirect if already logged in
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/profile');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="container max-w-screen-xl mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold text-center mb-6">
          Reset Your Password
        </h1>
        <ForgotPasswordForm />
      </div>
    </div>
  );
}
