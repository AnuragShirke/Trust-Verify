
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend
} from 'recharts';

interface Factor {
  name: string;
  value: number;
  description: string;
}

interface FactorBreakdownProps {
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
}

export default function FactorBreakdown({ factors }: FactorBreakdownProps) {
  const [activeTab, setActiveTab] = useState('bars');

  const factorsList: Factor[] = [
    {
      name: 'Source Credibility',
      value: factors.source_credibility,
      description: 'Evaluates the reputation and reliability of the content source.',
    },
    {
      name: 'Content Analysis',
      value: factors.content_analysis,
      description: 'Analyzes the structure, coherence, and quality of the content.',
    },
    {
      name: 'Language Analysis',
      value: factors.language_analysis,
      description: 'Examines the language style, tone, and potential bias indicators.',
    },
    {
      name: 'Fact Verification',
      value: factors.fact_verification,
      description: 'Checks for verifiable facts and cross-references with known information.',
    },
  ];

  // Format data for charts
  const chartData = factorsList.map(factor => ({
    name: factor.name,
    value: factor.value
  }));

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-trust-high';
    if (score >= 40) return 'bg-trust-medium';
    return 'bg-trust-low';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Trust Factor Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="bars" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="bars">Bars</TabsTrigger>
            <TabsTrigger value="radar">Radar</TabsTrigger>
            <TabsTrigger value="list">List</TabsTrigger>
          </TabsList>

          <TabsContent value="bars" className="space-y-4">
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10 }}
                    angle={-45}
                    textAnchor="end"
                    height={50}
                  />
                  <YAxis domain={[0, 100]} />
                  <RechartsTooltip />
                  <Bar
                    dataKey="value"
                    fill="#3b82f6"
                    radius={[4, 4, 0, 0]}
                    label={{ position: 'top', fontSize: 10 }}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="radar" className="space-y-4">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart outerRadius={90} data={chartData}>
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

          <TabsContent value="list" className="space-y-4">
            <div className="space-y-4">
              {factorsList.map((factor) => (
                <div key={factor.name} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-sm">{factor.name}</span>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="cursor-help">
                              <Info className="h-4 w-4 text-gray-400" />
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p className="max-w-xs">{factor.description}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    <span className="text-sm font-medium">{factor.value}%</span>
                  </div>
                  <Progress
                    value={factor.value}
                    className={cn("h-2", getScoreColor(factor.value))}
                  />
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {activeTab !== 'list' && (
          <div className="space-y-2 mt-4 pt-4 border-t border-gray-100">
            {factorsList.map((factor) => (
              <div key={factor.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-xs">{factor.name}</span>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-help">
                          <Info className="h-3 w-3 text-gray-400" />
                        </span>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs">{factor.description}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <span className="text-xs font-medium">{factor.value}%</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
