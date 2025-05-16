
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          About TrustVerify
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Our mission is to help people identify misinformation and evaluate the trustworthiness of news content.
        </p>
      </div>
      
      <div className="space-y-8">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-semibold mb-4">Our Technology</h2>
            <p className="text-gray-700 mb-4">
              TrustVerify uses advanced natural language processing and machine learning techniques to analyze news articles and content. Our technology evaluates multiple factors to determine both the likelihood of content being fake news and to generate an overall trust score.
            </p>
            <p className="text-gray-700">
              The system is trained on a diverse dataset of verified real and fake news articles, allowing it to identify patterns and characteristics typical of misinformation. We continuously update our models to adapt to evolving fake news techniques.
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-semibold mb-4">Our Methodology</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-medium mb-2">Content Analysis</h3>
                <p className="text-gray-700">
                  We analyze the structure, tone, and language patterns of the content. Sensationalist language, excessive capitalization, and emotional manipulation are often indicators of potentially misleading content.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-medium mb-2">Source Verification</h3>
                <p className="text-gray-700">
                  Our system evaluates the credibility of the content source, checking against databases of known reliable and unreliable publishers. We also consider domain age, transparency, and history.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-medium mb-2">Fact Checking</h3>
                <p className="text-gray-700">
                  The system cross-references claims with established facts and identifies statements that conflict with widely accepted information. We compare content against a database of previously verified information.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-medium mb-2">Language Analysis</h3>
                <p className="text-gray-700">
                  We examine writing style, checking for clickbait techniques, misleading headlines, and biased language that may indicate intent to mislead rather than inform.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-semibold mb-4">Trust Score Explained</h2>
            <p className="text-gray-700 mb-4">
              Our Trust Score is calculated on a scale from 0 to 100, with higher scores indicating more trustworthy content. The score is a weighted combination of multiple factors:
            </p>
            
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li><span className="font-medium">Source Credibility (30%)</span> - Evaluates the reputation and reliability of the content source.</li>
              <li><span className="font-medium">Content Analysis (25%)</span> - Analyzes the structure, coherence, and quality of the content.</li>
              <li><span className="font-medium">Language Analysis (25%)</span> - Examines the language style, tone, and potential bias indicators.</li>
              <li><span className="font-medium">Fact Verification (20%)</span> - Checks for verifiable facts and cross-references with known information.</li>
            </ul>
            
            <div className="mt-4 p-4 bg-blue-50 rounded-md border border-blue-100">
              <p className="text-sm text-blue-700">
                <strong>Note:</strong> While our system is designed to be as accurate as possible, we recommend using it as one of multiple tools to evaluate information. Critical thinking remains essential when consuming news and information online.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default About;
