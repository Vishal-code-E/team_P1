import { NextRequest, NextResponse } from 'next/server';

// Production backend URL - NO LOCALHOST
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://memorg-ai.onrender.com';

// Cold start tolerance settings
const HEALTH_CHECK_TIMEOUT = 5000; // 5s to wake backend
const CHAT_REQUEST_TIMEOUT = 45000; // 45s for LLM processing
const MAX_RETRIES = 1;

/**
 * Wake backend from cold start by calling health endpoint
 * Critical for Render free tier reliability
 */
async function wakeBackend(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
    
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      signal: controller.signal,
      headers: { 'Accept': 'application/json' }
    });
    
    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    console.warn('[Health Check] Backend cold start detected, proceeding anyway:', error);
    return false; // Continue even if health check fails
  }
}

/**
 * Fetch with timeout and retry logic
 */
async function fetchWithRetry(url: string, options: RequestInit, retries = MAX_RETRIES): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CHAT_REQUEST_TIMEOUT);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok && retries > 0) {
      console.warn(`[Retry] Request failed with ${response.status}, retrying... (${retries} left)`);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s before retry
      return fetchWithRetry(url, options, retries - 1);
    }
    
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (retries > 0 && (error instanceof Error && error.name === 'AbortError')) {
      console.warn(`[Retry] Timeout, retrying... (${retries} left)`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      return fetchWithRetry(url, options, retries - 1);
    }
    
    throw error;
  }
}

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

    // CRITICAL: Wake backend first to handle cold starts
    console.log('[Backend Wake] Checking backend health...');
    await wakeBackend();
    
    console.log('[Chat Request] Sending to backend:', BACKEND_URL);

    // Call Python backend with retry logic
    const response = await fetchWithRetry(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Backend Error]', response.status, errorText);
      throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    console.log('[Chat Success] Received response from backend');

    // Return response in expected format
    return NextResponse.json({
      answer: data.answer || data.response || 'No response from backend',
      sources: data.sources || [],
      confidence: data.confidence || 'Medium',
    });
  } catch (error) {
    console.error('[Chat Error] Failed:', error);
    
    // Graceful error message for users
    const userMessage = error instanceof Error && error.name === 'AbortError'
      ? 'Request timed out. The AI is taking longer than expected. Please try again.'
      : 'Failed to connect to the AI backend. The service may be starting up (this can take 30-60 seconds on first request). Please try again.';
    
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Internal server error',
        answer: userMessage,
        sources: [],
        confidence: 'Low',
      },
      { status: 500 }
    );
  }
}
