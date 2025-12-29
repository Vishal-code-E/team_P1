import React from 'react';
import { Message } from '@/types';
import ConfidenceBadge from './ConfidenceBadge';
import SourceBadge from './SourceBadge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 flex-shrink-0">
          <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white font-semibold">
            AI
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={`max-w-[75%] ${isUser ? 'order-first' : ''}`}>
        {/* Message Bubble */}
        <Card
          className={`px-5 py-4 ${
            isUser
              ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white border-0 shadow-lg'
              : 'bg-white border-slate-200 shadow-md'
          }`}
        >
          <p className={`text-[15px] leading-relaxed whitespace-pre-wrap ${
            isUser ? 'text-white' : 'text-slate-800'
          }`}>
            {message.content}
          </p>
        </Card>

        {/* AI Response Metadata */}
        {!isUser && (message.sources || message.confidence) && (
          <div className="mt-3 ml-1 space-y-3">
            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div>
                <p className="text-xs text-slate-600 mb-2 font-semibold">📚 Sources:</p>
                <div className="flex flex-wrap gap-2">
                  {message.sources.map((source, idx) => (
                    <SourceBadge key={idx} source={source} />
                  ))}
                </div>
              </div>
            )}

            {/* Confidence */}
            {message.confidence && (
              <div>
                <p className="text-xs text-slate-600 mb-2 font-semibold">🎯 Confidence:</p>
                <ConfidenceBadge confidence={message.confidence} />
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs mt-2 px-1 ${
          isUser ? 'text-slate-500 text-right' : 'text-slate-400'
        }`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {isUser && (
        <Avatar className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 flex-shrink-0">
          <AvatarFallback className="bg-gradient-to-br from-slate-700 to-slate-900 text-white font-semibold">
            You
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
