
import React from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Card } from '@/components/ui/card';

const FAQ = () => {
  const faqs = [
    {
      question: "How accurate is the fake news detection?",
      answer: "Our system typically achieves 80-90% accuracy in identifying fake news. However, accuracy can vary depending on the content and context. We recommend using our tool as one of several methods to verify information, alongside critical thinking and checking multiple sources."
    },
    {
      question: "What factors contribute to the trust score?",
      answer: "The trust score is calculated based on several factors: source credibility (30%), content analysis (25%), language analysis (25%), and fact verification (20%). Each component evaluates different aspects of the content to provide a comprehensive assessment."
    },
    {
      question: "Can the system analyze content in languages other than English?",
      answer: "Currently, our system is optimized for English content. We're working on expanding to other languages in future updates."
    },
    {
      question: "How does the system determine if a source is credible?",
      answer: "We maintain a database of known publishers, rating them based on factors like accuracy of past reporting, transparency, editorial standards, and recognition by journalism organizations. We also consider domain age, ownership disclosure, and citation practices."
    },
    {
      question: "What types of fake news can the system detect?",
      answer: "Our system can identify various types of misinformation including completely fabricated content, manipulated content, misleading content, false context, imposter content, and content with misleading statistics or data representation."
    },
    {
      question: "Is the data I submit stored or shared?",
      answer: "If you're not logged in, we don't permanently store the content you submit for analysis. For logged-in users, we store your analysis history to provide the history feature, but this data is never shared with third parties."
    },
    {
      question: "Why might a reliable article receive a low trust score?",
      answer: "Several factors might cause this: the article could use sensationalist language despite being factual, it might lack sufficient citations, come from a newer source without established credibility, or contain controversial topics where facts are disputed. We continuously improve our algorithms to minimize false positives."
    },
    {
      question: "Can I analyze social media posts?",
      answer: "Yes, you can paste the text from social media posts for analysis. However, the system is primarily designed for news articles and longer content, so very short posts may not provide enough context for accurate analysis."
    },
    {
      question: "Does the system have political bias?",
      answer: "We design our algorithms to be politically neutral, focusing on journalistic standards rather than political leaning. Our system evaluates content based on factual accuracy, source credibility, and journalistic practices regardless of political perspective."
    },
    {
      question: "How often is the system updated?",
      answer: "We continuously update our databases and algorithms to improve accuracy and adapt to evolving misinformation techniques. Major updates typically occur monthly, with minor improvements implemented weekly."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          Frequently Asked Questions
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Find answers to common questions about our fake news detection and trust score system.
        </p>
      </div>
      
      <Card className="p-6">
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left font-medium">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-gray-700">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </Card>
      
      <div className="mt-8 bg-gray-50 border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Still have questions?</h2>
        <p className="text-gray-700 mb-4">
          If you couldn't find the answer to your question, please feel free to reach out to our support team.
        </p>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-5 w-5 text-primary">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span className="text-gray-700">support@trustverify.example</span>
          </div>
          <div className="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-5 w-5 text-primary">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span className="text-gray-700">(123) 456-7890</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQ;
