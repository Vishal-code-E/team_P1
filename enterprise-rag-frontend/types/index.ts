export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: 'High' | 'Medium' | 'Low';
  timestamp: number;
}

export interface ChatResponse {
  answer: string;
  sources?: string[];
  confidence?: 'High' | 'Medium' | 'Low';
}

export interface UploadResponse {
  success: boolean;
  message: string;
  filename?: string;
}
