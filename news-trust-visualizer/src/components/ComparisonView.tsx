import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';

interface Analysis {
  id: string;
  title?: string;
  source?: string;
  prediction: 'REAL' | 'FAKE';
  trustScore: number;
  trustLevel: string;
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
}

interface ComparisonViewProps {
  analyses: Analysis[];
}

const ComparisonView: React.FC<ComparisonViewProps> = ({ analyses }) => {
  if (!analyses || analyses.length === 0) {
    return <div>No analyses to compare</div>;
  }

  // Prepare data for the comparison chart
  const trustScoreData = analyses.map(analysis => ({
    name: analysis.title || analysis.source || `Analysis ${analysis.id.substring(0, 6)}`,
    score: analysis.trustScore,
    prediction: analysis.prediction
  }));

  // Prepare data for the factors comparison chart
  const factorsData = [
    {
      name: 'Source Credibility',
      ...analyses.reduce((acc, analysis, index) => {
        acc[`analysis${index + 1}`] = analysis.factors.source_credibility;
        return acc;
      }, {})
    },
    {
      name: 'Content Analysis',
      ...analyses.reduce((acc, analysis, index) => {
        acc[`analysis${index + 1}`] = analysis.factors.content_analysis;
        return acc;
      }, {})
    },
    {
      name: 'Language Analysis',
      ...analyses.reduce((acc, analysis, index) => {
        acc[`analysis${index + 1}`] = analysis.factors.language_analysis;
        return acc;
      }, {})
    },
    {
      name: 'Fact Verification',
      ...analyses.reduce((acc, analysis, index) => {
        acc[`analysis${index + 1}`] = analysis.factors.fact_verification;
        return acc;
      }, {})
    }
  ];

  // Generate colors for the bars
  const barColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis Comparison</CardTitle>
        <CardDescription>
          Compare trust scores and factors across multiple analyses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium mb-3">Trust Score Comparison</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={trustScoreData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value, name) => [`${value}%`, 'Trust Score']}
                    labelFormatter={(label) => `Source: ${label}`}
                  />
                  <Bar 
                    dataKey="score" 
                    fill="#3b82f6" 
                    radius={[4, 4, 0, 0]}
                    label={{ position: 'top', fontSize: 12 }}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium mb-3">Factors Comparison</h3>
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
                  <Legend />
                  {analyses.map((analysis, index) => (
                    <Bar 
                      key={index}
                      dataKey={`analysis${index + 1}`} 
                      name={analysis.title || analysis.source || `Analysis ${index + 1}`}
                      fill={barColors[index % barColors.length]} 
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {analyses.map((analysis, index) => (
              <Card key={index} className="overflow-hidden">
                <CardHeader className="p-4 pb-2">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-sm">
                      {analysis.title || analysis.source || `Analysis ${index + 1}`}
                    </CardTitle>
                    <Badge 
                      variant={analysis.prediction === 'REAL' ? 'default' : 'destructive'}
                      className="ml-2 text-xs"
                    >
                      {analysis.prediction}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-2">
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-xs">Trust Score</span>
                        <span className="text-xs font-medium">{analysis.trustScore}%</span>
                      </div>
                      <Progress 
                        value={analysis.trustScore} 
                        className={`h-2 ${
                          analysis.trustScore >= 70 ? 'bg-green-500' : 
                          analysis.trustScore >= 50 ? 'bg-yellow-500' : 
                          'bg-red-500'
                        }`} 
                      />
                      <div className="mt-1 text-xs text-right">{analysis.trustLevel}</div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {Object.entries(analysis.factors).map(([key, value], i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between">
                            <span className="text-xs">{key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</span>
                            <span className="text-xs font-medium">{value}%</span>
                          </div>
                          <Progress value={value} className="h-1" />
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ComparisonView;
