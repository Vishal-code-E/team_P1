import React from 'react';
import { Message } from '@/types';
import ConfidenceBadge from './ConfidenceBadge';
import SourceBadge from './SourceBadge';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-slate-100 text-slate-900'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* AI Response Metadata */}
        {!isUser && (message.sources || message.confidence) && (
          <div className="mt-3 space-y-2">
            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1.5 font-medium">Sources:</p>
                <div className="flex flex-wrap gap-1.5">
                  {message.sources.map((source, idx) => (
                    <SourceBadge key={idx} source={source} />
                  ))}
                </div>
              </div>
            )}

            {/* Confidence */}
            {message.confidence && (
              <div>
                <p className="text-xs text-slate-500 mb-1.5 font-medium">Confidence:</p>
                <ConfidenceBadge confidence={message.confidence} />
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-slate-400 mt-1.5 px-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
