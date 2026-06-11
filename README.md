# AI Learning Assistant

A full-stack intelligent learning platform that combines Retrieval-Augmented Generation (RAG), real-time chat, document management, and analytics to provide personalized educational experiences.

## 🚀 Features

- **Interactive Chat**: Real-time chat with AI powered by Groq/OpenAI
- **Document Management**: Upload and manage learning documents (up to 25MB)
- **RAG Pipeline**: Intelligent document indexing and semantic search
- **Learning History**: Track your learning journey and progress
- **User Dashboard**: View statistics and learning insights
- **User Authentication**: Secure JWT-based authentication
- **Profile Management**: Customize your learning preferences

## 📋 Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints (v1)
│   │   │   └── v1/         # Authentication, Chat, Documents, etc.
│   │   ├── core/           # Config, security, rate limiting
│   │   ├── db/             # Database clients
│   │   ├── models/         # Data models
│   │   ├── schemas/        # Request/response schemas
│   │   ├── services/       # Business logic (auth, chat, RAG)
│   │   └── utils/          # Utilities
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── features/       # Feature-specific components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities (API, auth, Supabase)
│   │   ├── pages/          # Page components
│   │   └── store/          # Zustand state management
│   ├── vite.config.ts      # Vite configuration
│   └── tailwind.config.js  # Tailwind CSS config
│
└── supabase/               # Database migrations
    └── migrations/         # SQL migrations
```

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: Supabase (PostgreSQL)
- **LLM Providers**: Groq & OpenAI
- **Embeddings**: HuggingFace (sentence-transformers)
- **Server**: Uvicorn ASGI

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Backend Integration**: Supabase client, Custom API layer

### Infrastructure
- **Database**: Supabase
- **Deployment**: Render (for backend)
- **Storage**: Supabase Storage
- **Authentication**: Supabase Auth + JWT

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn
- Supabase account
- API keys (Groq, OpenAI, HuggingFace)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_huggingface_key
```

5. Run the backend:
```bash
python start.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables in `.env.local`:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 📚 API Documentation

Base URL: `http://localhost:8000/api/v1`

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Chat
- `POST /chat/send` - Send message and get AI response
- `GET /chat/history` - Get chat history

### Documents
- `POST /documents/upload` - Upload a document
- `GET /documents` - List user documents
- `DELETE /documents/{doc_id}` - Delete a document

### Dashboard
- `GET /dashboard/stats` - Get learning statistics
- `GET /dashboard/analytics` - Get detailed analytics

### User Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

## 🔐 Security Features

- JWT token-based authentication
- Rate limiting (60 requests/minute)
- CORS protection
- Supabase Row Level Security (RLS)
- Secure API key management
- Input validation and sanitization

## 📊 File Upload Limits

- Maximum file size: 25MB
- Supported formats: PDF, TXT, DOCX, etc.
- Storage: Supabase Storage bucket

## 🎨 UI/UX Features

- Responsive design with Tailwind CSS
- Modern component-based architecture
- Real-time notifications
- Toast notifications for user feedback
- Clean and intuitive navigation

## 📝 Environment Configuration

The application uses environment variables for configuration:

**Backend** (`.env`):
- `APP_ENV`, `APP_HOST`, `APP_PORT` - Server config
- `SUPABASE_*` - Database credentials
- `CHAT_PROVIDER` - LLM provider (groq/openai)
- `GROQ_API_KEY`, `OPENAI_API_KEY` - LLM keys
- `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL` - Embedding config
- `RATE_LIMIT_PER_MINUTE` - Rate limiting

**Frontend** (`.env.local`):
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anonymous key

## 🧪 Testing

Run tests:
```bash
cd backend
pytest tests/
```

## 📦 Deployment

### Backend (Render)
The `render.yaml` file is configured for automatic deployment.

### Frontend
Build for production:
```bash
cd frontend
npm run build
```

Deploy the `dist/` folder to any static hosting service.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues or questions, please open an issue in the repository.