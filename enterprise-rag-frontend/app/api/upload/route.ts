import { NextRequest, NextResponse } from 'next/server';

// Use 127.0.0.1 instead of localhost to avoid IPv6 (::1) resolution issues on macOS
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { success: false, message: 'No file provided' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = ['.md', '.pdf', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      return NextResponse.json(
        { 
          success: false, 
          message: `Invalid file type. Allowed: ${allowedTypes.join(', ')}` 
        },
        { status: 400 }
      );
    }

    // Forward file to Python backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      throw new Error(`Backend upload failed: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: data.message || `Successfully uploaded ${file.name}`,
      filename: file.name,
    });
  } catch (error) {
    console.error('Upload API error:', error);
    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error 
          ? error.message 
          : 'Upload failed. Please ensure the Python backend is running.',
      },
      { status: 500 }
    );
  }
}
