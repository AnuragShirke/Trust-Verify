
import React, { createContext, useContext, useState } from 'react';

interface AnalysisResult {
  text: string;
  prediction: 'REAL' | 'FAKE';
  confidence: number;
  trustScore: number;
  trustLevel?: string;
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
  details: {
    [key: string]: string | number;
  };
  timestamp: Date;
  sourceType?: 'text' | 'url';

  // URL-specific fields
  title?: string;
  url?: string;
  source?: string;
  sourceCredibility?: number;
  extractionMethod?: string;
}

interface AppContextType {
  history: AnalysisResult[];
  analyses: AnalysisResult[]; // Alias for history for backward compatibility
  currentAnalysis: AnalysisResult | null;
  isAnalyzing: boolean;
  error: string | null;
  addAnalysis: (result: AnalysisResult) => void;
  setCurrentAnalysis: (result: AnalysisResult | null) => void;
  setIsAnalyzing: (state: boolean) => void;
  setError: (error: string | null) => void;
  clearHistory: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addAnalysis = (result: AnalysisResult) => {
    setHistory((prev) => [result, ...prev]);
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return (
    <AppContext.Provider
      value={{
        history,
        analyses: history, // Alias for history for backward compatibility
        currentAnalysis,
        isAnalyzing,
        error,
        addAnalysis,
        setCurrentAnalysis,
        setIsAnalyzing,
        setError,
        clearHistory,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
