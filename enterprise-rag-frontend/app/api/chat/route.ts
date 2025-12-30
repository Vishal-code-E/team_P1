import { NextRequest, NextResponse } from 'next/server';

// Use 127.0.0.1 instead of localhost to avoid IPv6 (::1) resolution issues on macOS
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Return response in expected format
    return NextResponse.json({
      answer: data.answer || data.response || 'No response from backend',
      sources: data.sources || [],
      confidence: data.confidence || 'Medium',
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Internal server error',
        answer: 'Failed to connect to the AI backend. Please ensure the Python service is running on port 8000.',
        sources: [],
        confidence: 'Low',
      },
      { status: 500 }
    );
  }
}
