import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend
} from 'recharts';

interface TrustScoreDetailProps {
  score: number;
  trustLevel: string;
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
  details: {
    [key: string]: string | number;
  };
  prediction: 'REAL' | 'FAKE';
  confidence: number;
}

const TrustScoreDetail: React.FC<TrustScoreDetailProps> = ({
  score,
  trustLevel,
  factors,
  details,
  prediction,
  confidence
}) => {
  // Format the factors data for the charts
  const factorsData = [
    { name: 'Source Credibility', value: factors.source_credibility },
    { name: 'Content Analysis', value: factors.content_analysis },
    { name: 'Language Analysis', value: factors.language_analysis },
    { name: 'Fact Verification', value: factors.fact_verification },
  ];

  // Format the details data for display
  const detailItems = [
    { name: 'Word Count', value: details.word_count },
    { name: 'Has Citations', value: details.has_citations ? 'Yes' : 'No' },
    { name: 'Sensationalism Level', value: details.sensationalism_level },
    { name: 'Readability Score', value: details.readability_score },
    { name: 'Sentiment Polarity', value: details.sentiment_polarity },
    { name: 'Prediction Confidence', value: `${Math.round(Number(details.prediction_confidence) * 100)}%` },
  ];

  // Add source credibility if available
  if (details.source_credibility) {
    detailItems.push({ name: 'Source Credibility', value: details.source_credibility });
  }

  // Add is_known_fake_news if available
  if (details.is_known_fake_news !== undefined) {
    detailItems.push({ 
      name: 'Known Fake News Source', 
      value: details.is_known_fake_news ? 'Yes' : 'No' 
    });
  }

  // Add reading time if available
  if (details.reading_time_minutes) {
    detailItems.push({ 
      name: 'Reading Time', 
      value: `${details.reading_time_minutes} min` 
    });
  }

  // Get color based on trust score
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Get color based on factor score
  const getFactorColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle>Trust Score Analysis</CardTitle>
            <Badge 
              variant={prediction === 'REAL' ? 'default' : 'destructive'}
              className="ml-2"
            >
              {prediction}
            </Badge>
          </div>
          <CardDescription>
            Detailed breakdown of the trust score factors
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium">Overall Trust Score</span>
                <span className="text-sm font-medium">{score}%</span>
              </div>
              <Progress value={score} className={`h-3 ${getScoreColor(score)}`} />
              <div className="mt-1 text-sm text-right font-medium">{trustLevel}</div>
            </div>

            <Tabs defaultValue="bar" className="mt-6">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="bar">Bar Chart</TabsTrigger>
                <TabsTrigger value="radar">Radar Chart</TabsTrigger>
                <TabsTrigger value="details">Details</TabsTrigger>
              </TabsList>
              
              <TabsContent value="bar" className="pt-4">
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={factorsData}
                      margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Bar 
                        dataKey="value" 
                        fill="#3b82f6" 
                        radius={[4, 4, 0, 0]}
                        label={{ position: 'top', fontSize: 12 }}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </TabsContent>
              
              <TabsContent value="radar" className="pt-4">
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart outerRadius={90} data={factorsData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis domain={[0, 100]} />
                      <Radar
                        name="Trust Factors"
                        dataKey="value"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.6}
                      />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </TabsContent>
              
              <TabsContent value="details" className="pt-4">
                <div className="grid grid-cols-2 gap-4">
                  {detailItems.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-600">{item.name}:</span>
                      <span className="text-sm font-medium">{item.value}</span>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>

            <div className="grid grid-cols-2 gap-4 mt-4">
              {factorsData.map((factor, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-xs">{factor.name}</span>
                    <span className={`text-xs font-medium ${getFactorColor(factor.value)}`}>
                      {factor.value}%
                    </span>
                  </div>
                  <Progress value={factor.value} className="h-2" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrustScoreDetail;
