
import React from 'react';
import AnalysisForm from '@/components/AnalysisForm';
import AnalysisResults from '@/components/AnalysisResults';
import LoginPrompt from '@/components/LoginPrompt';
import { useAppContext } from '@/context/AppContext';
import { useAuth } from '@/context/AuthContext';

const Index = () => {
  const { currentAnalysis, isAnalyzing } = useAppContext();
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto flex items-center justify-center py-20">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="relative h-16 w-16">
            <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
            <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
          </div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {!currentAnalysis ? (
        <div className="space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Fake News Detector & Trust Score
            </h1>
            <p className="max-w-2xl mx-auto text-lg text-gray-600">
              Verify the credibility of news articles and content with our advanced AI analysis.
              Get instant feedback on reliability and trustworthiness.
            </p>
          </div>

          {isAnalyzing ? (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <div className="relative h-16 w-16">
                <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
                <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
              </div>
              <p className="text-gray-600 animate-pulse-subtle">Analyzing content...</p>
            </div>
          ) : (
            isAuthenticated ? (
              <AnalysisForm />
            ) : (
              <LoginPrompt />
            )
          )}

          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm">
              <div className="h-12 w-12 bg-blue-100 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714a2.25 2.25 0 01-.659 1.591L9.75 14.5M15 3.186a24.317 24.317 0 00-4.5 0M5 14.5v.75a3 3 0 002.652 2.982l1.646.269a3.719 3.719 0 002.704 0l1.646-.269A3 3 0 0015 15.25v-.75" />
                </svg>
              </div>
              <h3 className="font-medium">Content Analysis</h3>
              <p className="text-sm text-gray-500 mt-2">
                Our system analyzes article text for indicators of fake news and misinformation.
              </p>
            </div>

            <div className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm">
              <div className="h-12 w-12 bg-blue-100 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
              </div>
              <h3 className="font-medium">Trust Score</h3>
              <p className="text-sm text-gray-500 mt-2">
                Get a comprehensive trustworthiness rating on a scale from 0-100.
              </p>
            </div>

            <div className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm">
              <div className="h-12 w-12 bg-blue-100 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                </svg>
              </div>
              <h3 className="font-medium">Detailed Breakdown</h3>
              <p className="text-sm text-gray-500 mt-2">
                See the factors that contribute to the overall trust score.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <AnalysisResults />
      )}
    </div>
  );
};

export default Index;
