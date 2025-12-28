# Enterprise AI Knowledge Assistant - Frontend

A professional, production-ready Next.js frontend for the Enterprise RAG chatbot system.

## 🎯 Features

- **ChatGPT-Style Interface**: Clean, modern chat UI with smooth scrolling
- **Real-time AI Responses**: Seamless backend integration with loading indicators
- **Document Upload**: Drag-and-drop file upload with instant re-indexing
- **Source Attribution**: Clear display of document sources and confidence levels
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Error Handling**: Graceful degradation when backend is unavailable
- **Enterprise Ready**: Professional design suitable for demos and production

## 🏗️ Architecture

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)

### Backend Integration
- **API Routes**: Next.js API routes proxy to Python backend
- **Endpoints**:
  - `POST /api/chat` - Send messages to AI
  - `POST /api/upload` - Upload and index documents

### Component Structure
```
app/
├── layout.tsx          # Root layout
├── page.tsx            # Main chat page
├── globals.css         # Global styles
└── api/
    ├── chat/
    │   └── route.ts    # Chat API proxy
    └── upload/
        └── route.ts    # Upload API proxy

components/
├── ChatMessage.tsx     # Message bubble component
├── ChatInput.tsx       # Input box with upload button
├── ConfidenceBadge.tsx # Confidence level indicator
├── SourceBadge.tsx     # Document source badge
└── LoadingIndicator.tsx # AI thinking animation

types/
└── index.ts            # TypeScript interfaces
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python backend running on port 8000

### Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd enterprise-rag-frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   The `.env.local` file is already set up:
   ```
   BACKEND_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔧 Running Frontend + Backend Together

### Terminal 1 - Python Backend
```bash
cd enterprise-rag

# Install Flask dependencies (first time only)
pip install flask flask-cors

# Start the API server
python api_server.py
```

Backend will run on `http://localhost:8000`

### Terminal 2 - Next.js Frontend
```bash
cd enterprise-rag-frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📋 Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🎨 UI/UX Design

### Design Principles
- **Minimal & Clean**: Enterprise-friendly neutral color palette
- **Clear Hierarchy**: Visual separation between user and AI messages
- **Accessible**: High contrast, readable fonts, keyboard navigation
- **Responsive**: Mobile-first design that scales beautifully

### Color Scheme
- **Primary**: Blue 600 (#2563EB) - Actions and user messages
- **Background**: White (#FFFFFF) - Main background
- **AI Messages**: Slate 100 (#F1F5F9) - Assistant responses
- **Text**: Slate 900 (#0F172A) - Primary text
- **Borders**: Slate 200 (#E2E8F0) - Subtle dividers

### Components

#### ChatMessage
- User messages: Blue background, right-aligned
- AI messages: Gray background, left-aligned
- Sources and confidence displayed below AI messages
- Timestamps for all messages

#### ChatInput
- Fixed at bottom of screen
- Upload button (paperclip icon)
- Text input with auto-resize
- Send button (paper plane icon)
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)

#### LoadingIndicator
- Animated dots showing AI is thinking
- Non-intrusive, professional appearance

## 🔌 API Integration

### Chat Endpoint
**Request**:
```typescript
POST /api/chat
{
  "message": "What is the budget policy?"
}
```

**Response**:
```typescript
{
  "answer": "Based on the documents...",
  "sources": ["aws_budget_policy.md"],
  "confidence": "High"
}
```

### Upload Endpoint
**Request**:
```typescript
POST /api/upload
FormData: { file: File }
```

**Response**:
```typescript
{
  "success": true,
  "message": "Successfully uploaded and indexed document.md",
  "filename": "document.md"
}
```

## 📱 Features Detail

### 1. Chat Interface
- Smooth auto-scrolling to latest message
- Message history preserved during session
- Loading indicator while AI responds
- Error messages shown inline

### 2. Document Upload
- Supports .md, .pdf, .txt files
- Visual upload progress
- Success/error notifications
- Automatic re-indexing on backend

### 3. AI Response Display
- Answer text with proper formatting
- Source documents as clickable badges
- Confidence level (High/Medium/Low) with color coding
- Timestamps for message tracking

### 4. Error Handling
- Backend connection status indicator
- Graceful error messages
- Retry capability
- Network error detection

## 🎯 User Flow

1. **Landing**: User sees welcome screen with suggested questions
2. **Ask Question**: User types question and presses Enter
3. **Processing**: Loading indicator appears
4. **Response**: AI answer displays with sources and confidence
5. **Upload** (Optional): User clicks paperclip to upload document
6. **Re-index**: Backend processes document and confirms
7. **Continue**: User asks more questions with new context

## 🔒 Security Notes

- No API keys exposed to frontend
- All LLM calls happen on backend
- File upload validation (type and size)
- CORS configured for localhost only
- No authentication (out of scope for demo)

## 🚢 Production Deployment

### Build for Production
```bash
npm run build
npm run start
```

### Environment Variables
Update `.env.local` for production:
```
BACKEND_URL=https://your-backend-api.com
```

### Hosting Options
- **Vercel**: Optimized for Next.js (recommended)
- **Netlify**: Supports Next.js with adapters
- **AWS Amplify**: Full-stack deployment
- **Docker**: Containerize for any platform

## 📊 Performance

- **First Load**: < 2s
- **Chat Response**: Depends on backend (typically 2-5s)
- **Upload**: Depends on file size and re-indexing
- **Bundle Size**: ~200KB (optimized)

## 🐛 Troubleshooting

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and reinstall
- Check port 3000 is available

### Backend connection fails
- Ensure Python backend is running on port 8000
- Check `.env.local` has correct `BACKEND_URL`
- Verify CORS is enabled on backend

### Upload fails
- Check file type is .md, .pdf, or .txt
- Ensure backend has write permissions to `data/raw/`
- Check file size (default limit: 16MB)

## 📝 Customization

### Change Colors
Edit [tailwind.config.ts](tailwind.config.ts) to modify the color scheme.

### Modify Layout
Edit [app/page.tsx](app/page.tsx) to change the chat layout.

### Add Features
- Create new components in `components/`
- Add new API routes in `app/api/`
- Update types in `types/index.ts`

## 🎓 Demo Tips

1. **Prepare Data**: Upload relevant documents before demo
2. **Test Questions**: Have sample questions ready
3. **Show Sources**: Highlight how sources are displayed
4. **Error Handling**: Demonstrate graceful error states
5. **Upload**: Show live document upload and re-indexing

## 📄 License

This project is part of the Enterprise RAG system. See main project for license details.

## 🤝 Contributing

This is a demo/competition project. Contributions welcome via pull requests.

---

**Built with discipline. Built like a professional product.**
