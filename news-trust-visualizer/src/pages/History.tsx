
import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { format } from 'date-fns';
import TrustGauge from '@/components/TrustGauge';
import { useAppContext } from '@/context/AppContext';
import { cn } from '@/lib/utils';

const History = () => {
  const { history, setCurrentAnalysis, clearHistory } = useAppContext();

  const handleViewDetails = (index: number) => {
    setCurrentAnalysis(history[index]);
    window.scrollTo(0, 0);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Analysis History</h1>
        {history.length > 0 && (
          <Button variant="outline" onClick={clearHistory} size="sm">
            Clear History
          </Button>
        )}
      </div>

      {history.length === 0 ? (
        <Card className="text-center p-12">
          <CardContent>
            <div className="flex flex-col items-center justify-center space-y-3">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-12 w-12 text-gray-400">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">No analysis history</h3>
              <p className="text-gray-500">
                Your analysis history will appear here once you analyze content.
              </p>
              <Button onClick={() => window.location.href = "/"}>
                Analyze Content
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {history.map((item, index) => (
            <Card key={index} className="overflow-hidden">
              <div className="grid md:grid-cols-4 gap-4">
                <div className="md:col-span-3 p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium truncate max-w-md">
                        {item.sourceType === 'url' && item.title ? (
                          item.title
                        ) : (
                          item.text.substring(0, 50) + '...'
                        )}
                      </h3>
                      {item.sourceType === 'url' && item.source && (
                        <p className="text-xs text-gray-600 mt-1">
                          Source: {item.source} {item.sourceCredibility && `(${item.sourceCredibility}% credibility)`}
                        </p>
                      )}
                      <p className="text-sm text-gray-500 mt-1">
                        {format(new Date(item.timestamp), 'MMM d, yyyy • h:mm a')}
                      </p>
                    </div>
                    <Badge
                      className={cn(
                        "text-white ml-2",
                        item.prediction === 'REAL' ? "bg-trust-high" : "bg-trust-low"
                      )}
                    >
                      {item.prediction}
                    </Badge>
                  </div>

                  <Separator className="my-4" />

                  <div className="flex justify-between items-center">
                    <div className="w-48">
                      <TrustGauge score={item.trustScore} size="sm" />
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleViewDetails(index)}>
                      View Details
                    </Button>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 md:border-l">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Key Factors</h4>
                  <ul className="space-y-1">
                    <li className="flex justify-between text-sm">
                      <span className="text-gray-600">Source:</span>
                      <span>{item.factors.source_credibility}%</span>
                    </li>
                    <li className="flex justify-between text-sm">
                      <span className="text-gray-600">Content:</span>
                      <span>{item.factors.content_analysis}%</span>
                    </li>
                    <li className="flex justify-between text-sm">
                      <span className="text-gray-600">Language:</span>
                      <span>{item.factors.language_analysis}%</span>
                    </li>
                    <li className="flex justify-between text-sm">
                      <span className="text-gray-600">Facts:</span>
                      <span>{item.factors.fact_verification}%</span>
                    </li>
                  </ul>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
