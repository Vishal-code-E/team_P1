# Component Showcase

## UI Components Library

### 1. ChatMessage Component

**Purpose**: Display user and AI messages in the chat

**Props**:
- `message: Message` - Message object with content, role, sources, confidence

**Features**:
- User messages: Blue background, right-aligned
- AI messages: Gray background, left-aligned
- Sources displayed as badges below AI messages
- Confidence level with color-coded badge
- Timestamps on all messages
- Responsive design

**Usage**:
```tsx
<ChatMessage message={{
  id: "1",
  role: "assistant",
  content: "Based on the budget policy...",
  sources: ["aws_budget_policy.md"],
  confidence: "High",
  timestamp: Date.now()
}} />
```

---

### 2. ChatInput Component

**Purpose**: Message input with file upload capability

**Props**:
- `onSend: (message: string) => void` - Callback when user sends message
- `onFileUpload: (file: File) => void` - Callback when user uploads file
- `disabled: boolean` - Disable input during AI response
- `isUploading: boolean` - Show upload loading state

**Features**:
- Auto-resize textarea
- File upload button (paperclip icon)
- Send button (paper plane icon)
- Keyboard shortcuts:
  - Enter: Send message
  - Shift + Enter: New line
- File type validation (client-side)
- Loading states

**Usage**:
```tsx
<ChatInput
  onSend={(msg) => handleSend(msg)}
  onFileUpload={(file) => handleUpload(file)}
  disabled={isLoading}
  isUploading={isUploading}
/>
```

---

### 3. SourceBadge Component

**Purpose**: Display document source

**Props**:
- `source: string` - Source filename

**Features**:
- Clean badge design
- Document icon (📄)
- Truncates long filenames
- Subtle background color

**Usage**:
```tsx
<SourceBadge source="aws_budget_policy.md" />
```

**Appearance**: 
`📄 aws_budget_policy.md` in a light gray badge

---

### 4. ConfidenceBadge Component

**Purpose**: Display AI confidence level

**Props**:
- `confidence: 'High' | 'Medium' | 'Low'` - Confidence level

**Features**:
- Color-coded badges:
  - High: Green (#10B981)
  - Medium: Yellow (#F59E0B)
  - Low: Orange (#F97316)
- Small, unobtrusive design
- Clear text

**Usage**:
```tsx
<ConfidenceBadge confidence="High" />
```

**Appearance**:
- High: Green badge with "High" text
- Medium: Yellow badge with "Medium" text
- Low: Orange badge with "Low" text

---

### 5. LoadingIndicator Component

**Purpose**: Show AI is processing

**Props**: None

**Features**:
- Animated bouncing dots
- "Thinking..." text
- Non-blocking UI
- Smooth animation

**Usage**:
```tsx
{isLoading && <LoadingIndicator />}
```

**Appearance**: 
Three gray dots bouncing with "Thinking..." text

---

## Page Layout

### Main Chat Page (app/page.tsx)

**Structure**:
```
┌─────────────────────────────────────┐
│ Header: Enterprise AI Assistant     │
│ Status: Connected (green dot)        │
├─────────────────────────────────────┤
│ Notification Bar (errors/success)   │
├─────────────────────────────────────┤
│                                      │
│ Chat Messages (scrollable)           │
│   - ChatMessage (user)               │
│   - ChatMessage (assistant)          │
│   - LoadingIndicator (if loading)    │
│                                      │
├─────────────────────────────────────┤
│ ChatInput (fixed at bottom)          │
└─────────────────────────────────────┘
```

**Key Features**:
1. **Header**:
   - Product name
   - Tagline: "Powered by RAG + Agentic AI"
   - Connection status indicator

2. **Notification Bar**:
   - Error messages (red)
   - Success messages (green)
   - Dismissible
   - Auto-hide after 5s (success only)

3. **Chat Area**:
   - Auto-scrolls to latest message
   - Empty state with welcome message
   - Suggested questions (clickable)
   - Smooth animations

4. **Input Area**:
   - Fixed at bottom
   - Always accessible
   - Upload + text input + send button

---

## Type Definitions

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: 'High' | 'Medium' | 'Low';
  timestamp: number;
}

interface ChatResponse {
  answer: string;
  sources?: string[];
  confidence?: 'High' | 'Medium' | 'Low';
}

interface UploadResponse {
  success: boolean;
  message: string;
  filename?: string;
}
```

---

## Color Palette

### Primary Colors
- **Blue 600**: `#2563EB` - User messages, primary actions
- **Slate 900**: `#0F172A` - Primary text
- **Slate 100**: `#F1F5F9` - AI message background
- **White**: `#FFFFFF` - Main background

### Semantic Colors
- **Green 500**: `#10B981` - Success, high confidence, connected
- **Yellow 500**: `#F59E0B` - Medium confidence
- **Orange 500**: `#F97316` - Low confidence
- **Red 500**: `#EF4444` - Errors, disconnected

### Neutral Colors
- **Slate 200**: `#E2E8F0` - Borders
- **Slate 300**: `#CBD5E1` - Input borders
- **Slate 400**: `#94A3B8` - Timestamps
- **Slate 500**: `#64748B` - Helper text
- **Slate 600**: `#475569` - Icons

---

## Responsive Breakpoints

```css
/* Mobile First */
Default: 0-640px (mobile)
sm: 640px (large phones)
md: 768px (tablets)
lg: 1024px (desktops)
xl: 1280px (large desktops)
```

**Chat Container**: Max-width 4xl (896px) for optimal reading

---

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Focus States**: Clear focus indicators
- **ARIA Labels**: Screen reader friendly
- **Color Contrast**: WCAG AA compliant
- **Alt Text**: All icons have descriptive labels

---

## Animation Details

**Message Entry**: Fade in with slide up
```css
animation: fadeInUp 0.3s ease-out
```

**Loading Dots**: Staggered bounce
```css
animation: bounce 1s infinite
animation-delay: 0ms, 150ms, 300ms
```

**Smooth Scroll**: 
```javascript
scrollIntoView({ behavior: 'smooth' })
```

**Hover States**: 
```css
transition: all 0.2s ease-in-out
```

---

## Best Practices

1. **Component Composition**: Small, focused components
2. **Type Safety**: Full TypeScript coverage
3. **State Management**: React hooks only (no external library)
4. **Performance**: Lazy loading, memoization where needed
5. **Error Boundaries**: Graceful error handling
6. **Loading States**: Always show feedback to user
7. **Optimistic Updates**: UI updates before backend confirms
8. **Accessibility**: WCAG 2.1 AA compliance

---

**Components built with care. Ready for production.** 🎨
