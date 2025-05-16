import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import TrustGauge from './TrustGauge';
import { useAppContext } from '@/context/AppContext';
import { useNavigate } from 'react-router-dom';

interface AnalysisCardProps {
  title: string;
  source?: string;
  sourceCredibility?: number;
  prediction: 'REAL' | 'FAKE';
  trustScore: number;
  trustLevel: string;
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
  onViewDetails: () => void;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({
  title,
  source,
  sourceCredibility,
  prediction,
  trustScore,
  trustLevel,
  factors,
  onViewDetails
}) => {
  return (
    <Card className="w-full overflow-hidden">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-semibold">{title}</h2>
            {source && (
              <p className="text-sm text-gray-600 mt-1">
                Source: {source} {sourceCredibility && `(${sourceCredibility}% credibility)`}
              </p>
            )}
          </div>
          <Badge
            className={`text-white ${prediction === 'REAL' ? 'bg-green-500' : 'bg-red-500'}`}
          >
            {prediction}
          </Badge>
        </div>

        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Trust Score</p>
            <div className="text-2xl font-bold">{trustScore}%</div>
            <div className="text-sm text-gray-600">{trustLevel}</div>
          </div>
          <TrustGauge score={trustScore} size="lg" />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          {Object.entries(factors).map(([key, value]) => (
            <div key={key} className="bg-gray-50 p-3 rounded-md">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">
                  {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}:
                </span>
                <span className="text-sm font-medium">{value}%</span>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <Button onClick={onViewDetails}>View Details</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisCard;
