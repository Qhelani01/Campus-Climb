"""
AI Assistant module for Campus Climb.
Handles interactions with Ollama LLM for application assistance.
"""
import requests
import json
try:
    from api.config import Config
except ImportError:
    from config import Config

def build_prompt(opportunity, user_info, request_type):
    """
    Build a prompt for the AI assistant based on opportunity and user info.
    
    Args:
        opportunity: Opportunity object with title, description, requirements, etc.
        user_info: Dict with resume_summary, skills, career_goals
        request_type: Type of assistance (resume_tips, cover_letter, interview_prep, application_review)
    
    Returns:
        str: Formatted prompt for the LLM
    """
    opportunity_text = f"""
Opportunity Details:
- Title: {opportunity.get('title', 'N/A')}
- Company: {opportunity.get('company', 'N/A')}
- Type: {opportunity.get('type', 'N/A')}
- Location: {opportunity.get('location', 'N/A')}
- Description: {opportunity.get('description', 'N/A')}
- Requirements: {opportunity.get('requirements', 'Not specified')}
- Deadline: {opportunity.get('deadline', 'Not specified')}
"""
    
    user_text = ""
    if user_info:
        resume_summary = user_info.get('resume_summary', '')
        skills = user_info.get('skills', [])
        career_goals = user_info.get('career_goals', '')
        
        if resume_summary:
            user_text += f"\nStudent Background:\n{resume_summary}\n"
        if skills:
            skills_str = ', '.join(skills) if isinstance(skills, list) else skills
            user_text += f"Skills: {skills_str}\n"
        if career_goals:
            user_text += f"Career Goals: {career_goals}\n"
    
    prompts = {
        'resume_tips': f"""You are a career counselor helping a WVSU student tailor their resume for a specific opportunity.

{opportunity_text}
{user_text}

Provide specific, actionable advice on how to tailor their resume for this opportunity. Focus on:
1. Which skills/experiences to emphasize
2. How to align their background with the job requirements
3. Keywords to include
4. Formatting suggestions
5. What to highlight in their experience section

Be concise, practical, and encouraging. Format your response with clear bullet points.""",

        'cover_letter': f"""You are a career counselor helping a WVSU student write a cover letter for a specific opportunity.

{opportunity_text}
{user_text}

Provide guidance on writing a compelling cover letter. Include:
1. Opening paragraph suggestions that grab attention
2. Key points to address in the body paragraphs
3. How to connect their experience to the opportunity requirements
4. Closing paragraph suggestions
5. Overall tone and style recommendations

Be specific and provide example phrases or sentences they could use.""",

        'interview_prep': f"""You are a career counselor helping a WVSU student prepare for an interview for a specific opportunity.

{opportunity_text}
{user_text}

Provide comprehensive interview preparation advice:
1. Common questions they should expect
2. How to answer questions using their background
3. Questions they should ask the interviewer
4. Key points to emphasize about their fit for the role
5. Tips for demonstrating their skills and experience

Be practical and help them feel confident and prepared.""",

        'application_review': f"""You are a career counselor reviewing a WVSU student's application materials for a specific opportunity.

{opportunity_text}
{user_text}

Review their application and provide:
1. Strengths of their application
2. Areas for improvement
3. Specific suggestions to strengthen their application
4. How well their background aligns with the opportunity
5. Any gaps they should address

Be constructive, specific, and encouraging."""
    }
    
    return prompts.get(request_type, prompts['resume_tips'])

def call_ollama(prompt, model=None):
    """
    Call Ollama API to generate a response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name (defaults to config setting)
    
    Returns:
        dict: Response from Ollama with 'response' and 'done' keys
    """
    if not Config.is_ai_enabled():
        raise Exception("AI Assistant is disabled")
    
    model = model or Config.OLLAMA_MODEL
    url = Config.get_ollama_url()
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=Config.OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Make sure Ollama is running on the configured URL.")
    except requests.exceptions.Timeout:
        raise Exception(f"Ollama request timed out after {Config.OLLAMA_TIMEOUT} seconds.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling Ollama API: {str(e)}")

def parse_response(ollama_response):
    """
    Parse and format the response from Ollama.
    
    Args:
        ollama_response: Raw response from Ollama API
    
    Returns:
        dict: Formatted response with advice and suggestions
    """
    if not ollama_response:
        return {
            'advice': 'No response received from AI assistant.',
            'suggestions': []
        }
    
    response_text = ollama_response.get('response', '')
    
    # Extract suggestions (bullet points or numbered lists)
    suggestions = []
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        if line and (line.startswith('-') or line.startswith('•') or 
                    line.startswith('*') or line[0].isdigit() and '.' in line[:3]):
            # Remove bullet/number markers
            clean_line = line.lstrip('-•*0123456789. ')
            if clean_line:
                suggestions.append(clean_line)
    
    return {
        'advice': response_text,
        'suggestions': suggestions if suggestions else [response_text],
        'model_used': ollama_response.get('model', Config.OLLAMA_MODEL)
    }

def generate_application_advice(opportunity_dict, user_info, request_type):
    """
    Main function to generate application advice.
    
    Args:
        opportunity_dict: Dictionary representation of opportunity
        user_info: Dictionary with user's background info
        request_type: Type of assistance requested
    
    Returns:
        dict: Formatted advice with suggestions
    """
    try:
        prompt = build_prompt(opportunity_dict, user_info, request_type)
        ollama_response = call_ollama(prompt)
        parsed_response = parse_response(ollama_response)
        return {
            'success': True,
            **parsed_response
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'advice': f'I apologize, but I encountered an error: {str(e)}. Please make sure Ollama is running and configured correctly.',
            'suggestions': []
        }

