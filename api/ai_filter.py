"""
AI-based opportunity filtering module for Campus Climb.
Uses LLM to classify whether content is an actual opportunity or not.
"""
import requests
import json
import re
from typing import Dict, Optional
try:
    from api.config import Config
except ImportError:
    from config import Config


def build_classification_prompt(title: str, description: str, source: str) -> str:
    """
    Build a prompt for AI classification of opportunities.
    
    Args:
        title: Post title
        description: Post description/content
        source: Source name (e.g., 'reddit_internships')
    
    Returns:
        str: Formatted prompt for the LLM
    """
    # Truncate description to keep prompt small (faster inference, less timeout risk)
    max_description_length = 500
    if len(description) > max_description_length:
        description = description[:max_description_length] + "..."
    
    prompt = f"""You are a content classifier for a job/opportunity aggregation platform. Your task is to determine if a post is an ACTUAL OPPORTUNITY (job posting, internship offer, workshop announcement, etc.) or NOT an opportunity (question, discussion, request for help, etc.).

CLASSIFICATION RULES:
- ACTUAL OPPORTUNITY: Posts that are offering or announcing a job, internship, workshop, conference, competition, or similar opportunity that someone can apply to or participate in.
- NOT AN OPPORTUNITY: Questions about opportunities, discussions, requests for advice, people looking for work, general conversations, or any content that is NOT offering an actual opportunity.

EXAMPLES:

OPPORTUNITY (classify as true):
- "[Hiring] Software Engineer at Google - Remote position available. Apply at..."
- "Summer Internship Program 2024 - We're looking for interns in..."
- "Free Python Workshop Next Saturday - Learn web development..."
- "Tech Conference 2024 - Early bird tickets available now..."

NOT AN OPPORTUNITY (classify as false):
- "How do I find an internship? Looking for advice"
- "What's the best way to prepare for job interviews?"
- "Has anyone here done an internship at Google?"
- "Looking for internship opportunities, any suggestions?"
- "I'm a student looking for advice on finding workshops"

SOURCE: {source}
TITLE: {title}
DESCRIPTION: {description}

Analyze the content above and classify it. Respond ONLY with a valid JSON object in this exact format:
{{
    "is_opportunity": true or false,
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of your classification"
}}

Important: 
- If the post is asking a question, seeking advice, or discussing opportunities (rather than offering one), classify as false.
- If the post is clearly offering a job, internship, workshop, or similar opportunity, classify as true.
- Be strict: when in doubt, classify as false to avoid false positives.
"""
    return prompt


def parse_classification_response(response_text: str) -> Dict:
    """
    Parse the LLM response to extract classification result.
    
    Args:
        response_text: Raw text response from LLM
    
    Returns:
        dict: Parsed classification with 'is_opportunity', 'confidence', 'reasoning'
    """
    # Try to extract JSON from response (may have extra text)
    # Look for JSON object in the response
    json_match = re.search(r'\{[^{}]*"is_opportunity"[^{}]*\}', response_text, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group(0))
            # Validate and normalize
            is_opportunity = bool(result.get('is_opportunity', False))
            confidence = float(result.get('confidence', 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            reasoning = str(result.get('reasoning', 'No reasoning provided'))
            
            return {
                'is_opportunity': is_opportunity,
                'confidence': confidence,
                'reasoning': reasoning
            }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # If JSON parsing fails, try to infer from text
            pass
    
    # Fallback: try to infer from response text
    response_lower = response_text.lower()
    if 'true' in response_lower and 'false' not in response_lower:
        is_opportunity = True
    elif 'false' in response_lower:
        is_opportunity = False
    elif 'opportunity' in response_lower and ('yes' in response_lower or 'is' in response_lower):
        # Try to infer from context
        is_opportunity = 'not' not in response_lower and 'no' not in response_lower
    else:
        # Default to false if unclear
        is_opportunity = False
    
    return {
        'is_opportunity': is_opportunity,
        'confidence': 0.5,  # Low confidence for fallback
        'reasoning': f'Parsed from text (may be inaccurate): {response_text[:200]}'
    }


def classify_opportunity(title: str, description: str, source: str = 'unknown') -> Dict:
    """
    Classify whether a post is an actual opportunity using AI.
    
    Args:
        title: Post title
        description: Post description/content
        source: Source name (e.g., 'reddit_internships')
    
    Returns:
        dict: Classification result with:
            - 'is_opportunity': bool
            - 'confidence': float (0.0 to 1.0)
            - 'reasoning': str
            - 'error': str (if classification failed)
    """
    # Check if AI filtering is enabled
    if not Config.is_ai_filter_enabled():
        # Return default (will trigger fallback)
        return {
            'is_opportunity': None,  # None indicates fallback needed
            'confidence': 0.0,
            'reasoning': 'AI filtering disabled',
            'error': 'AI filtering is disabled'
        }
    
    # Validate inputs
    if not title or not title.strip():
        return {
            'is_opportunity': False,
            'confidence': 1.0,
            'reasoning': 'Empty title - not an opportunity',
            'error': None
        }
    
    # Build prompt
    prompt = build_classification_prompt(title, description or '', source)
    
    # Get model to use
    model = Config.AI_FILTER_MODEL or Config.OLLAMA_MODEL
    
    # Call Ollama directly with AI filter timeout (avoids ai_assistant's 60s limit; first run can be slow)
    url = Config.get_ollama_url()
    timeout = getattr(Config, 'AI_FILTER_TIMEOUT', None) or getattr(Config, 'OLLAMA_TIMEOUT', 120)
    
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            url,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        ollama_response = response.json()
        
        # Parse response
        response_text = ollama_response.get('response', '')
        if not response_text:
            raise ValueError("Empty response from Ollama")
        
        result = parse_classification_response(response_text)
        result['error'] = None
        return result
        
    except requests.exceptions.Timeout:
        return {
            'is_opportunity': None,  # None triggers fallback
            'confidence': 0.0,
            'reasoning': 'AI classification timed out',
            'error': f'Request timed out after {timeout} seconds'
        }
    except requests.exceptions.ConnectionError:
        return {
            'is_opportunity': None,  # None triggers fallback
            'confidence': 0.0,
            'reasoning': 'Cannot connect to Ollama',
            'error': 'Cannot connect to Ollama. Make sure Ollama is running.'
        }
    except Exception as e:
        return {
            'is_opportunity': None,  # None triggers fallback
            'confidence': 0.0,
            'reasoning': f'AI classification error: {str(e)}',
            'error': str(e)
        }
