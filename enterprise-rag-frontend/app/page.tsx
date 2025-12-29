'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import LoadingIndicator from '@/components/LoadingIndicator';
import { Message } from '@/types';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (message: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.',
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setUploadSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setUploadSuccess(`✅ ${data.message}`);

      // Clear success message after 5 seconds
      setTimeout(() => setUploadSuccess(null), 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Enterprise AI Knowledge Assistant
                </h1>
                <p className="text-sm text-slate-600">Powered by RAG + Agentic AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Badge variant={error ? "destructive" : "default"} className="flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-full ${error ? 'bg-red-300' : 'bg-green-300'} animate-pulse`}></div>
                {error ? 'Disconnected' : 'Connected'}
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Notification Bar */}
      {(error || uploadSuccess) && (
        <div className="bg-white/80 backdrop-blur-sm border-b">
          <div className="max-w-5xl mx-auto px-6 py-3">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="text-lg">⚠️</span>
                  <span>{error}</span>
                </div>
                <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700 transition-colors">
                  ✕
                </button>
              </div>
            )}
            {uploadSuccess && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="text-lg">✅</span>
                  <span>{uploadSuccess}</span>
                </div>
                <button onClick={() => setUploadSuccess(null)} className="text-green-500 hover:text-green-700 transition-colors">
                  ✕
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <ScrollArea className="flex-1">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center py-16">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">
                Welcome to Your AI Assistant
              </h2>
              <p className="text-slate-600 max-w-md mb-8">
                Ask questions about your documents. Upload new documents using the paperclip icon below.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
                <Card
                  className="p-5 border-2 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer group"
                  onClick={() => handleSend("What documents do you have access to?")}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">📚</div>
                    <div className="text-left">
                      <p className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Available documents</p>
                      <p className="text-xs text-slate-500 mt-1">What can you help me with?</p>
                    </div>
                  </div>
                </Card>
                <Card
                  className="p-5 border-2 hover:border-purple-400 hover:shadow-lg transition-all cursor-pointer group"
                  onClick={() => handleSend("Summarize the key points from the documentation")}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">📝</div>
                    <div className="text-left">
                      <p className="text-sm font-semibold text-slate-900 group-hover:text-purple-600 transition-colors">Quick summary</p>
                      <p className="text-xs text-slate-500 mt-1">Get an overview</p>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex justify-start mb-4">
                  <div className="max-w-[80%]">
                    <LoadingIndicator />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t bg-white/80 backdrop-blur-sm shadow-lg">
        <ChatInput
          onSend={handleSend}
          onFileUpload={handleFileUpload}
          disabled={isLoading}
          isUploading={isUploading}
        />
      </div>
    </div>
  );
}
