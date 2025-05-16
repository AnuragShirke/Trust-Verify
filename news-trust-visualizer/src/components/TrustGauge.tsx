
import React from 'react';
import { Progress } from '@/components/ui/progress';
import { cn } from "../utils.js";

interface TrustGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export default function TrustGauge({ 
  score, 
  size = 'md', 
  showLabel = true,
  className 
}: TrustGaugeProps) {
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'bg-trust-high';
    if (score >= 40) return 'bg-trust-medium';
    return 'bg-trust-low';
  };

  const getScoreText = (score: number) => {
    if (score >= 70) return 'High Trust';
    if (score >= 40) return 'Medium Trust';
    return 'Low Trust';
  };

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  return (
    <div className={cn("w-full", className)}>
      <div className="flex justify-between items-center mb-2">
        {showLabel && (
          <div className="flex items-center">
            <span className="text-sm font-medium text-gray-700">Trust Score</span>
          </div>
        )}
        <span className="text-sm font-medium">{score}%</span>
      </div>
      
      <Progress
        value={score}
        className={cn(
          "trust-score-gradient overflow-hidden",
          sizeClasses[size]
        )}
      />
      
      {showLabel && (
        <div className="mt-2 flex justify-end">
          <span 
            className={cn(
              "text-sm font-medium px-2 py-0.5 rounded-full",
              {
                'bg-trust-high/10 text-trust-high': score >= 70,
                'bg-trust-medium/10 text-trust-medium': score >= 40 && score < 70,
                'bg-trust-low/10 text-trust-low': score < 40,
              }
            )}
          >
            {getScoreText(score)}
          </span>
        </div>
      )}
    </div>
  );
}

