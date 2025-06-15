/**
 * API service for connecting to the FastAPI backend
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MLOPS_BASE_URL = import.meta.env.VITE_MLOPS_URL || 'http://localhost:8001';

// Ensure URLs always end without a trailing slash
const normalizeUrl = (url: string) => url.replace(/\/$/, '');

interface PredictionResponse {
  prediction: 'REAL' | 'FAKE';
  confidence: number;
  text_length?: number;
}

interface TrustScoreResponse {
  score: number;
  trust_level?: string;
  prediction?: 'REAL' | 'FAKE';
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
  details: {
    [key: string]: string | number;
  };
}

interface ArticleContent {
  title: string;
  content: string;
  source: string;
  source_credibility: number;
  extraction_method: string;
  url: string;
}

interface UrlAnalysisResponse {
  prediction: 'REAL' | 'FAKE';
  confidence: number;
  trust_score: number;
  trust_level: string;
  factors: {
    source_credibility: number;
    content_analysis: number;
    language_analysis: number;
    fact_verification: number;
  };
  details: {
    [key: string]: string | number;
  };
  article: ArticleContent;
}

export const analyzeText = async (text: string): Promise<PredictionResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error analyzing text:', error);
    throw error;
  }
};

export const getTrustScore = async (text: string): Promise<TrustScoreResponse> => {
  try {
    // Get token from localStorage if available
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/trust-score`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      // If unauthorized but we're trying to use a token, try again without the token
      if (response.status === 401 && token) {
        console.warn('Authentication failed, retrying without token');
        return getTrustScore(text);
      }
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching trust score:', error);
    throw error;
  }
};

// Mock API functions for development without the backend
export const mockAnalyzeText = async (text: string): Promise<PredictionResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  // Simple heuristic - if text contains these words, it's more likely "fake"
  const fakeWords = ['shocking', 'amazing', 'unbelievable', 'secret', 'conspiracy', '100%'];
  const fakeWordCount = fakeWords.filter(word => text.toLowerCase().includes(word)).length;

  // Basic algorithm to determine if content might be fake news based on trigger words
  const isFake = fakeWordCount > 0 || text.length < 100;
  const confidence = isFake
    ? Math.min(0.5 + fakeWordCount * 0.1, 0.95)
    : Math.max(0.7 - (fakeWordCount * 0.05), 0.55);

  return {
    prediction: isFake ? 'FAKE' : 'REAL',
    confidence: Number(confidence.toFixed(2)),
  };
};

export const mockGetTrustScore = async (text: string): Promise<TrustScoreResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1800));

  // Simple heuristic based on text length and certain words
  const wordCount = text.split(/\s+/).length;
  const hasLinks = text.includes('http');
  const hasCitations = text.includes('according to') || text.includes('reported by');
  const sensationalismWords = ['shocking', 'amazing', 'unbelievable', 'secret', 'conspiracy', '100%'];
  const sensationalismScore = sensationalismWords.filter(word => text.toLowerCase().includes(word)).length;

  // Calculate component scores
  const sourceCredibility = hasCitations ? 0.6 + Math.random() * 0.3 : 0.3 + Math.random() * 0.3;
  const contentAnalysis = wordCount > 100 ? 0.5 + Math.random() * 0.4 : 0.2 + Math.random() * 0.4;
  const languageAnalysis = sensationalismScore > 0
    ? Math.max(0.2, 0.7 - sensationalismScore * 0.15)
    : 0.6 + Math.random() * 0.3;
  const factVerification = hasLinks ? 0.5 + Math.random() * 0.4 : 0.3 + Math.random() * 0.3;

  // Overall score (weighted average)
  const score = Math.round(
    (sourceCredibility * 0.3 +
    contentAnalysis * 0.25 +
    languageAnalysis * 0.25 +
    factVerification * 0.2) * 100
  );

  // Determine trust level
  let trust_level = "Low Trust";
  if (score >= 70) {
    trust_level = "High Trust";
  } else if (score >= 50) {
    trust_level = "Medium Trust";
  }

  return {
    score,
    trust_level,
    factors: {
      source_credibility: Math.round(sourceCredibility * 100),
      content_analysis: Math.round(contentAnalysis * 100),
      language_analysis: Math.round(languageAnalysis * 100),
      fact_verification: Math.round(factVerification * 100),
    },
    details: {
      word_count: wordCount,
      has_citations: hasCitations ? 1 : 0,  // Convert boolean to number
      has_links: hasLinks ? 1 : 0,          // Convert boolean to number
      sensationalism_level: sensationalismScore,
    }
  };
};

// New functions for URL analysis
export const extractUrl = async (url: string): Promise<ArticleContent> => {
  try {
    const response = await fetch(`${API_BASE_URL}/extract-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error extracting URL content:', error);
    throw error;
  }
};

export const analyzeUrl = async (url: string): Promise<UrlAnalysisResponse> => {
  try {
    console.log(`Analyzing URL: ${url}`);

    // Ensure URL has http:// or https:// prefix
    let processedUrl = url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      processedUrl = `https://${url}`;
      console.log(`Added https:// prefix to URL: ${processedUrl}`);
    }

    // Create a simple form data approach
    const formData = new FormData();
    formData.append('url', processedUrl);

    console.log('Sending URL:', processedUrl);

    // Try with form data first
    try {
      const response = await fetch(`${API_BASE_URL}/analyze-url`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        return await response.json();
      }

      console.log('Form data approach failed, trying JSON');

      // If form data fails, try with JSON
      const jsonResponse = await fetch(`${API_BASE_URL}/analyze-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: processedUrl }),
      });

      if (jsonResponse.ok) {
        return await jsonResponse.json();
      }

      // If both approaches fail, throw an error
      console.error('Both form data and JSON approaches failed');

      // Try to get error details from the response
      try {
        const errorData = await jsonResponse.json();
        throw new Error(errorData.detail || `Error: ${jsonResponse.status}`);
      } catch (e) {
        throw new Error(`Error analyzing URL (${jsonResponse.status}): Please check the URL format and try again.`);
      }
    } catch (innerError) {
      console.error('Error in fetch:', innerError);
      throw innerError;
    }
  } catch (error) {
    console.error('Error analyzing URL:', error);
    throw error;
  }
};

// Mock functions for URL analysis
export const mockExtractUrl = async (url: string): Promise<ArticleContent> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Extract domain from URL
  const domain = new URL(url).hostname.replace('www.', '');

  // Generate mock article content
  return {
    title: `Sample Article from ${domain}`,
    content: `This is a sample article extracted from ${url}. It contains mock content for testing purposes. The article discusses various topics related to the domain ${domain} and provides information that would typically be found in a news article.`,
    source: domain,
    source_credibility: domain.includes('bbc') || domain.includes('reuters') ? 85 : 65,
    extraction_method: 'mock',
    url: url
  };
};

export const mockAnalyzeUrl = async (url: string): Promise<UrlAnalysisResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2500));

  // Extract domain from URL
  const domain = new URL(url).hostname.replace('www.', '');

  // Determine if the domain is trustworthy
  const isTrusted = domain.includes('bbc') || domain.includes('reuters') || domain.includes('nytimes');
  const isFake = domain.includes('fake') || domain.includes('conspiracy');

  // Generate mock article content
  const article = await mockExtractUrl(url);

  // Generate mock analysis results
  const trustScore = isTrusted ? 75 + Math.floor(Math.random() * 15) :
                    isFake ? 25 + Math.floor(Math.random() * 15) :
                    45 + Math.floor(Math.random() * 30);

  // Determine trust level
  let trustLevel = "Low Trust";
  if (trustScore >= 70) {
    trustLevel = "High Trust";
  } else if (trustScore >= 50) {
    trustLevel = "Medium Trust";
  }

  return {
    prediction: isTrusted ? 'REAL' : isFake ? 'FAKE' : Math.random() > 0.5 ? 'REAL' : 'FAKE',
    confidence: 0.7 + Math.random() * 0.2,
    trust_score: trustScore,
    trust_level: trustLevel,
    factors: {
      source_credibility: article.source_credibility,
      content_analysis: 50 + Math.floor(Math.random() * 40),
      language_analysis: 60 + Math.floor(Math.random() * 30),
      fact_verification: isTrusted ? 70 + Math.floor(Math.random() * 20) : 40 + Math.floor(Math.random() * 30)
    },
    details: {
      word_count: article.content.split(/\s+/).length,
      has_citations: Math.random() > 0.5 ? 1 : 0,
      sensationalism_level: isFake ? 3 : Math.floor(Math.random() * 2),
      readability_score: 65 + Math.floor(Math.random() * 20),
      sentiment_polarity: Math.random().toFixed(2),
      prediction_confidence: (0.7 + Math.random() * 0.2).toFixed(2)
    },
    article: article
  };
};

