
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Toggle } from '@/components/ui/toggle';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Info } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAppContext } from '@/context/AppContext';
import {
  analyzeText,
  getTrustScore,
  mockAnalyzeText,
  mockGetTrustScore,
  analyzeUrl,
  mockAnalyzeUrl
} from '@/services/api';

export default function AnalysisForm() {
  const [inputText, setInputText] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [inputType, setInputType] = useState<'text' | 'url'>('text');
  const [useMockData, setUseMockData] = useState(false);

  const { toast } = useToast();
  const { setIsAnalyzing, setCurrentAnalysis, setError, addAnalysis } = useAppContext();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if ((inputType === 'text' && !inputText.trim()) ||
        (inputType === 'url' && !inputUrl.trim())) {
      toast({
        title: "Input required",
        description: `Please enter ${inputType === 'text' ? 'text' : 'a URL'} to analyze.`,
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      if (inputType === 'text') {
        // Text analysis path
        const textToAnalyze = inputText;

        // Use either mock or real API based on toggle
        const predictFn = useMockData ? mockAnalyzeText : analyzeText;
        const trustScoreFn = useMockData ? mockGetTrustScore : getTrustScore;

        const [predictionResult, trustScoreResult] = await Promise.all([
          predictFn(textToAnalyze),
          trustScoreFn(textToAnalyze),
        ]);

        const analysisResult = {
          text: textToAnalyze,
          prediction: predictionResult.prediction,
          confidence: predictionResult.confidence,
          trustScore: trustScoreResult.score,
          trustLevel: trustScoreResult.trust_level ||
            (trustScoreResult.score >= 70 ? "High Trust" :
             trustScoreResult.score >= 50 ? "Medium Trust" : "Low Trust"),
          factors: trustScoreResult.factors,
          details: trustScoreResult.details,
          timestamp: new Date(),
          sourceType: 'text',
        };

        setCurrentAnalysis(analysisResult);
        addAnalysis(analysisResult);

        toast({
          title: "Analysis complete",
          description: `Analysis completed with a trust score of ${trustScoreResult.score}%`,
        });
      } else {
        // URL analysis path
        let urlToAnalyze = inputUrl.trim();

        // Basic validation - just make sure it's not empty
        if (!urlToAnalyze) {
          toast({
            title: "URL Required",
            description: "Please enter a URL to analyze",
            variant: "destructive",
          });
          setIsAnalyzing(false);
          return;
        }

        // Remove any whitespace
        urlToAnalyze = urlToAnalyze.trim();

        // Add https:// prefix if missing
        if (!urlToAnalyze.startsWith('http://') && !urlToAnalyze.startsWith('https://')) {
          urlToAnalyze = `https://${urlToAnalyze}`;
        }

        console.log(`Analyzing URL: ${urlToAnalyze}`);

        // Use either mock or real API based on toggle
        const analyzeUrlFn = useMockData ? mockAnalyzeUrl : analyzeUrl;

        // Analyze the URL
        const urlAnalysisResult = await analyzeUrlFn(urlToAnalyze);

        // Create analysis result object
        const analysisResult = {
          text: urlAnalysisResult.article.content,
          title: urlAnalysisResult.article.title,
          url: urlAnalysisResult.article.url,
          source: urlAnalysisResult.article.source,
          sourceCredibility: urlAnalysisResult.article.source_credibility,
          extractionMethod: urlAnalysisResult.article.extraction_method,
          prediction: urlAnalysisResult.prediction,
          confidence: urlAnalysisResult.confidence,
          trustScore: urlAnalysisResult.trust_score,
          trustLevel: urlAnalysisResult.trust_level,
          factors: urlAnalysisResult.factors,
          details: urlAnalysisResult.details,
          timestamp: new Date(),
          sourceType: 'url',
        };

        setCurrentAnalysis(analysisResult);
        addAnalysis(analysisResult);

        toast({
          title: "URL Analysis complete",
          description: `Analysis completed with a trust score of ${urlAnalysisResult.trust_score}%`,
        });
      }
    } catch (error) {
      console.error('Error during analysis:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setError(errorMessage);

      // Provide more specific error messages based on the error
      let description = "There was an error analyzing the content. Please try again.";

      if (errorMessage.includes('URL')) {
        description = "Please check that the URL is valid and accessible. Make sure it starts with http:// or https://";
      } else if (errorMessage.includes('422')) {
        description = "The URL format is invalid. Please make sure it starts with http:// or https://";
      } else if (errorMessage.includes('404')) {
        description = "Could not extract content from this URL. Please try a different news article.";
      } else if (errorMessage.includes('503')) {
        description = "The analysis service is temporarily unavailable. Please try again later.";
      }

      toast({
        title: "Analysis failed",
        description: description,
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto bg-white rounded-lg shadow-sm p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <Tabs defaultValue="text" onValueChange={(value) => setInputType(value as 'text' | 'url')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="text">Analyze Text</TabsTrigger>
            <TabsTrigger value="url">Analyze URL</TabsTrigger>
          </TabsList>

          <TabsContent value="text" className="space-y-4 mt-4">
            <Textarea
              placeholder="Paste the news article or content here..."
              className="min-h-[200px] resize-none"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </TabsContent>

          <TabsContent value="url" className="space-y-4 mt-4">
            <Input
              type="url"
              placeholder="https://example.com/article"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Enter the URL of a news article to analyze its content.
            </p>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-2 p-2 rounded-md ${useMockData ? 'bg-yellow-50 border border-yellow-200' : 'bg-green-50 border border-green-200'}`}>
              <Toggle
                pressed={useMockData}
                onPressedChange={setUseMockData}
                variant={useMockData ? "outline" : "default"}
                size="sm"
                className={useMockData ? "border-yellow-500 text-yellow-700" : "border-green-500 text-green-700"}
              >
                {useMockData ? "Using mock data" : "Using real API"}
              </Toggle>
              <span className={`text-sm font-medium ${useMockData ? "text-yellow-700" : "text-green-700"}`}>
                {useMockData ? "(Development mode)" : "(Production mode)"}
              </span>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="cursor-help">
                      <Info className={`h-4 w-4 ${useMockData ? "text-yellow-700" : "text-green-700"}`} />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p>
                      {useMockData
                        ? "Development mode uses mock data and doesn't require a backend connection. Results are simulated."
                        : "Production mode connects to the real API backend for actual analysis. Make sure the backend is running."}
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>

          <Button type="submit">
            Analyze Content
          </Button>
        </div>
      </form>
    </div>
  );
}
