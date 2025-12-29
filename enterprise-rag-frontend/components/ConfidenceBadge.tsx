import React from 'react';
import { Badge } from '@/components/ui/badge';

interface ConfidenceBadgeProps {
  confidence: 'High' | 'Medium' | 'Low';
}

export default function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const getColors = () => {
    switch (confidence) {
      case 'High':
        return 'bg-green-100 text-green-700 border-green-300 hover:bg-green-200';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300 hover:bg-yellow-200';
      case 'Low':
        return 'bg-orange-100 text-orange-700 border-orange-300 hover:bg-orange-200';
    }
  };

  const getIcon = () => {
    switch (confidence) {
      case 'High':
        return '✓';
      case 'Medium':
        return '~';
      case 'Low':
        return '!';
    }
  };

  return (
    <Badge
      variant="outline"
      className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold border-2 shadow-sm ${getColors()}`}
    >
      <span>{getIcon()}</span>
      {confidence}
    </Badge>
  );
}
