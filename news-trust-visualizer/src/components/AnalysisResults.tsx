
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Check, X, ArrowLeft } from 'lucide-react';
import { cn } from "../utils.js";
import TrustGauge from './TrustGauge';
import FactorBreakdown from './FactorBreakdown';
import TrustScoreDetail from './TrustScoreDetail';
import SourceCredibility from './SourceCredibility';
import AnalysisCard from './AnalysisCard';
import LoginPrompt from './LoginPrompt';
import { useAppContext } from '@/context/AppContext';
import { useAuth } from '@/context/AuthContext';

export default function AnalysisResults() {
  const { currentAnalysis, setCurrentAnalysis, analyses } = useAppContext();
  const { isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const tabsRef = useRef<HTMLDivElement>(null);

  const handleViewDetails = () => {
    setActiveTab('detailed');
    // Scroll to the tabs if needed
    if (tabsRef.current) {
      tabsRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
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

  // If not authenticated, show login prompt
  if (!isAuthenticated) {
    return <LoginPrompt />;
  }

  if (!currentAnalysis) return null;

  const {
    prediction,
    confidence,
    trustScore,
    trustLevel,
    factors,
    details,
    sourceType,
    title,
    url,
    source,
    sourceCredibility,
    extractionMethod,
    isKnownFakeNews
  } = currentAnalysis;

  // Find similar analyses for comparison
  const similarAnalyses = (analyses || [])
    .filter(a => a !== currentAnalysis)
    .slice(0, 3); // Get up to 3 other analyses for comparison

  const handleBackClick = () => {
    setCurrentAnalysis(null);
  };

  const isPredictionReal = prediction === 'REAL';
  const confidencePercentage = Math.round(confidence * 100);
  const isUrlAnalysis = sourceType === 'url';

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBackClick}
          className="flex items-center space-x-1"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </Button>
      </div>

      <div ref={tabsRef}>
        <Tabs value={activeTab} className="w-full" onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-3 mb-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="detailed">Detailed Analysis</TabsTrigger>
          <TabsTrigger value="compare" disabled={similarAnalyses.length === 0}>
            Compare
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <AnalysisCard
            title={title || (isUrlAnalysis ? "Article Analysis" : "Text Analysis")}
            source={source}
            sourceCredibility={sourceCredibility}
            prediction={prediction}
            trustScore={trustScore}
            trustLevel={trustLevel || (
              trustScore >= 70 ? "High Trust" :
              trustScore >= 50 ? "Medium Trust" : "Low Trust"
            )}
            factors={factors}
            onViewDetails={handleViewDetails}
          />

          <div className="bg-gray-50 p-4 rounded-md border">
            <h3 className="text-sm font-medium mb-2">
              {isUrlAnalysis ? "Article Preview" : "Analyzed Text Preview"}
            </h3>
            <div className="bg-white p-3 rounded-md border text-sm overflow-hidden relative max-h-36">
              <p className="line-clamp-5">{currentAnalysis.text}</p>
              <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent"></div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <FactorBreakdown factors={factors} />
            </Card>

            {isUrlAnalysis ? (
              <SourceCredibility
                source={source || ''}
                credibilityScore={sourceCredibility || 50}
                isKnownFakeNews={isKnownFakeNews}
                extractionMethod={extractionMethod}
              />
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Additional Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="space-y-2">
                    {Object.entries(details).map(([key, value]) => (
                      <div key={key} className="grid grid-cols-2 gap-2">
                        <dt className="text-sm font-medium text-gray-600 capitalize">
                          {key.replace(/_/g, ' ')}:
                        </dt>
                        <dd className="text-sm">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value.toString()}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="detailed">
          <div className="space-y-6">
            <TrustScoreDetail
              score={trustScore}
              trustLevel={trustLevel || (
                trustScore >= 70 ? "High Trust" :
                trustScore >= 50 ? "Medium Trust" : "Low Trust"
              )}
              factors={factors}
              details={details}
              prediction={prediction}
              confidence={confidence}
            />

            {isUrlAnalysis && (
              <Card>
                <CardHeader>
                  <CardTitle>Article Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium">{title}</h3>
                      {url && (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-xs"
                        >
                          {url}
                        </a>
                      )}
                    </div>

                    <Separator />

                    <div className="max-h-96 overflow-y-auto p-4 bg-gray-50 rounded-md border">
                      <p className="whitespace-pre-line">{currentAnalysis.text}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="compare">
          {similarAnalyses.length > 0 ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Comparison with Previous Analyses</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-md border">
                      <h3 className="font-medium mb-2">Current Analysis</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Trust Score:</span>
                          <span className="text-sm font-medium">{trustScore}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Prediction:</span>
                          <span className="text-sm font-medium">{prediction}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Confidence:</span>
                          <span className="text-sm font-medium">{confidencePercentage}%</span>
                        </div>
                      </div>
                    </div>

                    {similarAnalyses.map((analysis, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-md border">
                        <h3 className="font-medium mb-2">
                          {analysis.title || analysis.source || `Analysis ${index + 1}`}
                        </h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm">Trust Score:</span>
                            <span className="text-sm font-medium">{analysis.trustScore}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Prediction:</span>
                            <span className="text-sm font-medium">{analysis.prediction}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Confidence:</span>
                            <span className="text-sm font-medium">{Math.round(analysis.confidence * 100)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Trust Score Comparison</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[currentAnalysis, ...similarAnalyses].map((analysis, index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex justify-between">
                            <span className="text-sm">
                              {analysis.title || analysis.source || `Analysis ${index === 0 ? 'Current' : index}`}
                            </span>
                            <span className="text-sm font-medium">{analysis.trustScore}%</span>
                          </div>
                          <Progress
                            value={analysis.trustScore}
                            className={`h-2 ${
                              analysis.trustScore >= 70 ? 'bg-green-500' :
                              analysis.trustScore >= 50 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`}
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <div className="text-center p-8 bg-gray-50 rounded-md border">
              <p>No previous analyses available for comparison.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
      </div>
    </div>
  );
}

