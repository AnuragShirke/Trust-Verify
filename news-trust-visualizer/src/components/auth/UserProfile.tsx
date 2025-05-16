import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Avatar, AvatarFallback } from '../../components/ui/avatar';
import { Separator } from '../../components/ui/separator';
import { useAuth } from '../../context/AuthContext';
import { fetchUserProfile, fetchUserAnalyses } from './api';

interface UserAnalysis {
  id: string;
  title: string;
  content_type: string;
  prediction: string;
  trust_score: number;
  created_at: string;
}

export default function UserProfile() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [analyses, setAnalyses] = useState<UserAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUserData = async () => {
      if (!user) return;

      setIsLoading(true);
      try {
        const [profileData, analysesData] = await Promise.all([
          fetchUserProfile(),
          fetchUserAnalyses()
        ]);

        setProfile(profileData);
        setAnalyses(analysesData);
      } catch (err) {
        setError('Failed to load user data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, [user]);

  if (!user) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center">Please log in to view your profile</p>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center">Loading profile...</p>
        </CardContent>
      </Card>
    );
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Avatar className="h-12 w-12">
              <AvatarFallback>{getInitials(user.username || user.email)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle>{user.username || 'User'}</CardTitle>
              <CardDescription>{user.email}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Member since</span>
              <span className="text-sm">
                {new Date(user.created_at).toLocaleDateString()}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Last login</span>
              <span className="text-sm">
                {user.last_login
                  ? new Date(user.last_login).toLocaleDateString()
                  : 'N/A'}
              </span>
            </div>

            <Separator />

            <div className="flex justify-end">
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Your Analyses</CardTitle>
          <CardDescription>
            History of your recent content analyses
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analyses.length === 0 ? (
            <p className="text-center text-gray-500 py-4">
              You haven't analyzed any content yet
            </p>
          ) : (
            <div className="space-y-4">
              {analyses.map((analysis) => (
                <div key={analysis.id} className="p-4 border rounded-md">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-sm">
                        {analysis.title || `${analysis.content_type.toUpperCase()} Analysis`}
                      </h3>
                      <p className="text-xs text-gray-500">
                        {new Date(analysis.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        analysis.prediction === 'REAL'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {analysis.prediction}
                      </span>
                      <span className="text-xs font-medium">
                        {analysis.trust_score}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
