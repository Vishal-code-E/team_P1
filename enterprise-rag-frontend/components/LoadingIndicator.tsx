import React from 'react';
import { Card } from '@/components/ui/card';

export default function LoadingIndicator() {
  return (
    <Card className="inline-flex items-center gap-3 px-5 py-4 bg-white border-slate-200 shadow-md">
      <div className="flex space-x-1.5">
        <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-sm text-slate-600 font-medium">AI is thinking...</span>
    </Card>
  );
}
