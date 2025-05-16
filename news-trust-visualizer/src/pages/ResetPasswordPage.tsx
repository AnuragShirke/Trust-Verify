import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ResetPasswordForm from '@/components/auth/ResetPasswordForm';
import { useAuth } from '@/context/AuthContext';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ResetPasswordPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Get token from URL query parameters
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const tokenParam = searchParams.get('token');
    
    if (!tokenParam) {
      setError('Invalid or missing reset token. Please request a new password reset link.');
    } else {
      setToken(tokenParam);
    }
  }, [location.search]);
  
  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/profile');
    }
  }, [isAuthenticated, navigate]);

  if (error) {
    return (
      <div className="container max-w-screen-xl mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <h1 className="text-2xl font-bold text-center mb-6">
            Reset Your Password
          </h1>
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-screen-xl mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold text-center mb-6">
          Reset Your Password
        </h1>
        {token && <ResetPasswordForm token={token} />}
      </div>
    </div>
  );
}
