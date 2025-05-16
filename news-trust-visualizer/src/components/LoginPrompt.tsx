import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { LockKeyhole, UserPlus } from 'lucide-react';

const LoginPrompt = () => {
  const navigate = useNavigate();

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Authentication Required</CardTitle>
        <CardDescription>
          Please log in or register to use the Fake News Detector
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800">
          <p className="text-sm">
            To ensure the quality of our service and prevent abuse, we require users to create an account
            before analyzing content. This helps us maintain the integrity of our platform and provide
            you with a personalized experience.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg border shadow-sm text-center">
            <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
              <LockKeyhole className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-medium mb-2">Already have an account?</h3>
            <p className="text-sm text-gray-500 mb-4">
              Sign in to your existing account to continue using the Fake News Detector.
            </p>
            <Button 
              onClick={() => navigate('/login')}
              className="w-full"
            >
              Log In
            </Button>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm text-center">
            <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
              <UserPlus className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-medium mb-2">New to Fake News Detector?</h3>
            <p className="text-sm text-gray-500 mb-4">
              Create a free account to start analyzing news articles and content.
            </p>
            <Button 
              onClick={() => navigate('/register')}
              variant="outline"
              className="w-full"
            >
              Register
            </Button>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-center border-t pt-6">
        <p className="text-sm text-gray-500">
          Your data is secure and will only be used to improve our service.
        </p>
      </CardFooter>
    </Card>
  );
};

export default LoginPrompt;
