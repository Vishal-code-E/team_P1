import React from 'react';

interface ConfidenceBadgeProps {
  confidence: 'High' | 'Medium' | 'Low';
}

export default function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const getColors = () => {
    switch (confidence) {
      case 'High':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low':
        return 'bg-orange-100 text-orange-800 border-orange-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getColors()}`}
    >
      {confidence}
    </span>
  );
}
