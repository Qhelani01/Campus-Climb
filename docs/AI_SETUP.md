# AI Assistant Setup Guide

This guide explains how to set up and use the AI Application Assistant feature in Campus Climb.

## Overview

The AI Assistant helps WVSU students tailor their applications, resumes, and cover letters to specific opportunities using local LLM models via Ollama.

## Prerequisites

1. **Ollama installed** on your system
2. **A compatible LLM model** downloaded (e.g., llama2, mistral, codellama)

## Installation Steps

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai)

### 2. Download a Model

```bash
# Download llama2 (recommended for general use)
ollama pull llama2

# Or download other models:
ollama pull mistral      # Good alternative
ollama pull codellama     # Better for code-related advice
```

### 3. Start Ollama Server

```bash
ollama serve
```

This starts the Ollama server on `http://localhost:11434` (default port).

### 4. Configure Environment Variables

Create a `.env` file in the project root (or set in Vercel):

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60
AI_ASSISTANT_ENABLED=true
AI_RATE_LIMIT_PER_HOUR=10
```

### 5. Run Database Migration

If you have an existing database, run the migration to add user profile fields:

```sql
-- Run database/05_add_user_profile_fields.sql in your Supabase SQL Editor
```

Or the migration will run automatically on first use (if using SQLAlchemy's `db.create_all()`).

## Usage

### For Students

1. **Browse Opportunities**: Find an opportunity you're interested in
2. **Click "AI Help"**: Click the purple "AI Help" button on any opportunity card
3. **Select Assistance Type**: Choose from:
   - **Resume Tips**: Get advice on tailoring your resume
   - **Cover Letter**: Get help writing a cover letter
   - **Interview Prep**: Prepare for interviews
   - **Application Review**: Get feedback on your application
4. **Provide Background** (Optional): Enter your resume summary, skills, and career goals
5. **Generate Advice**: Click "Generate AI Advice" to get personalized recommendations
6. **Save Profile**: Save your background info for future use

### For Developers

#### Testing the AI Assistant

```bash
# Start Ollama server
ollama serve

# In another terminal, start your Flask app
cd api
python3 index.py

# Test the endpoint
curl -X POST http://localhost:8000/api/ai/assistant \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session-cookie" \
  -d '{
    "opportunity_id": 1,
    "assistance_type": "resume_tips",
    "user_info": {
      "resume_summary": "Computer Science student with Python experience",
      "skills": ["Python", "JavaScript"],
      "career_goals": "Software development"
    }
  }'
```

## Troubleshooting

### Ollama Connection Errors

**Error: "Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check the URL in your `.env` file matches Ollama's address
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags`

**Error: "Model not found"**
- Download the model: `ollama pull llama2`
- Check model name matches `OLLAMA_MODEL` in your config

### Slow Responses

- Try a smaller/faster model (e.g., `mistral` instead of `llama2`)
- Increase `OLLAMA_TIMEOUT` in your config
- Check system resources (CPU/RAM)

### Production Deployment

For production (Vercel), you have several options:

1. **Separate Server**: Run Ollama on a separate server/VM and update `OLLAMA_BASE_URL`
2. **Cloud Service**: Use a cloud-hosted Ollama service
3. **Alternative API**: Switch to OpenAI/Anthropic APIs (modify `ai_assistant.py`)

## API Endpoints

### POST `/api/ai/assistant`

Request:
```json
{
  "opportunity_id": 123,
  "assistance_type": "resume_tips",
  "user_info": {
    "resume_summary": "...",
    "skills": ["Python", "JavaScript"],
    "career_goals": "..."
  }
}
```

Response:
```json
{
  "success": true,
  "advice": "Based on the opportunity requirements...",
  "suggestions": [
    "Highlight your Python experience...",
    "Emphasize your project work..."
  ],
  "model_used": "llama2"
}
```

### PUT `/api/user/profile`

Update user profile information:

```json
{
  "resume_summary": "...",
  "skills": ["Python", "JavaScript"],
  "career_goals": "..."
}
```

## Security Considerations

- AI Assistant requires user authentication
- User input is validated before sending to AI
- AI responses are sanitized before displaying
- Rate limiting prevents abuse (configurable via `AI_RATE_LIMIT_PER_HOUR`)
- Sensitive data is not stored in prompts

## Future Enhancements

- Conversation history
- Multi-turn conversations
- Resume parsing integration
- Export formatted documents
- Comparison between opportunities

