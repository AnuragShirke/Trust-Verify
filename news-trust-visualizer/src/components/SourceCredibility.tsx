import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Info, CheckCircle, XCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface SourceCredibilityProps {
  source: string;
  credibilityScore: number;
  isKnownFakeNews?: boolean;
  extractionMethod?: string;
}

const SourceCredibility: React.FC<SourceCredibilityProps> = ({
  source,
  credibilityScore,
  isKnownFakeNews = false,
  extractionMethod
}) => {
  // Get color based on credibility score
  const getCredibilityColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-green-400';
    if (score >= 40) return 'bg-yellow-500';
    if (score >= 20) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // Get credibility level text
  const getCredibilityLevel = (score: number) => {
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    if (score >= 20) return 'Low';
    return 'Very Low';
  };

  // Get extraction method description
  const getExtractionMethodDescription = (method: string) => {
    switch (method) {
      case 'newspaper':
        return 'Extracted using Newspaper3k, a comprehensive article extraction library';
      case 'trafilatura':
        return 'Extracted using Trafilatura, a web scraping library focused on text extraction';
      case 'readability':
        return 'Extracted using Readability, a content extraction algorithm';
      case 'cache':
        return 'Retrieved from cache';
      default:
        return 'Extracted using an unknown method';
    }
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle>Source Information</CardTitle>
          {isKnownFakeNews && (
            <Badge variant="destructive" className="ml-2">
              Known Fake News Source
            </Badge>
          )}
        </div>
        <CardDescription>
          Credibility assessment for this source
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Source:</span>
            <span className="text-sm">{source}</span>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Credibility Score</span>
              <span className="text-sm font-medium">{credibilityScore}%</span>
            </div>
            <Progress value={credibilityScore} className={`h-3 ${getCredibilityColor(credibilityScore)}`} />
            <div className="mt-1 text-sm text-right font-medium">
              {getCredibilityLevel(credibilityScore)} Credibility
            </div>
          </div>

          {extractionMethod && (
            <div className="flex items-center justify-between mt-4 text-sm">
              <span className="font-medium">Extraction Method:</span>
              <div className="flex items-center">
                <span>{extractionMethod}</span>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Info className="ml-1 h-4 w-4 text-gray-500" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="max-w-xs">{getExtractionMethodDescription(extractionMethod)}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
          )}

          <div className="mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-medium mb-2">Credibility Indicators</h4>
            <ul className="space-y-2">
              <li className="flex items-center text-sm">
                {credibilityScore >= 60 ? (
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="mr-2 h-4 w-4 text-red-500" />
                )}
                <span>Established reputation</span>
              </li>
              <li className="flex items-center text-sm">
                {!isKnownFakeNews ? (
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="mr-2 h-4 w-4 text-red-500" />
                )}
                <span>Not known for misinformation</span>
              </li>
              <li className="flex items-center text-sm">
                {credibilityScore >= 40 ? (
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="mr-2 h-4 w-4 text-red-500" />
                )}
                <span>Editorial standards</span>
              </li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SourceCredibility;
