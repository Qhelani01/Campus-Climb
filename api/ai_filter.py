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

CRITICAL RULES - BE STRICT:
- Questions (how, what, where, when, why, any?) = ALWAYS false
- Seeking advice, recommendations, or tips = ALWAYS false
- Discussions about opportunities (not offering one) = ALWAYS false
- "Looking for" from a job seeker (not employer) = ALWAYS false
- Only classify true if the post is EXPLICITLY offering a real opportunity (employer posting job/internship, organizer announcing workshop, etc.)
- When in doubt, classify as false to avoid false positives.
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
    # First try: look for "is_opportunity": true/false (use first occurrence as the actual answer)
    opp_match = re.search(r'"is_opportunity"\s*:\s*(true|false)', response_text, re.IGNORECASE)
    if opp_match:
        is_opportunity = opp_match.group(1).lower() == 'true'
        conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', response_text)
        confidence = float(conf_match.group(1)) if conf_match else 0.5
        confidence = max(0.0, min(1.0, confidence))
        reason_match = re.search(r'"reasoning"\s*:\s*"([^"]*)"', response_text)
        reasoning = reason_match.group(1) if reason_match else 'Parsed from response'
        return {'is_opportunity': is_opportunity, 'confidence': confidence, 'reasoning': reasoning}
    
    # Fallback: try full JSON parse (handles simple case)
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
    
    # Fallback: when JSON parsing fails, default to False to avoid false positives
    return {
        'is_opportunity': False,
        'confidence': 0.3,
        'reasoning': f'Parse failed, rejecting to avoid false positive: {response_text[:100]}'
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


def keyword_based_filter_fallback(title: str, description: str, source_name: str) -> bool:
    """
    Stricter keyword-based filtering when AI is unavailable.
    Filters out questions, discussions, and "for hire" posts.
    """
    combined_text = (title + ' ' + (description or '')).lower()
    title_lower = (title or '').lower().strip()

    # Question starters -> reject unless clear job posting
    question_starters = ['how', 'what', 'where', 'when', 'why', 'who', 'which', 'can', 'should', 'do', 'does', 'is', 'are']
    if any(title_lower.startswith(s + ' ') for s in question_starters):
        if not any(x in combined_text for x in ['apply', 'application', 'hiring', 'position', 'role', 'job opening']):
            return False

    question_patterns = [
        'how do i', 'how can i', 'how to', 'what is', 'what are', 'looking for advice', 'need advice',
        'any suggestions', 'can someone help', 'i\'m looking for', 'i am looking for', 'does anyone know', 'has anyone',
    ]
    for pattern in question_patterns:
        if pattern in combined_text:
            if not any(x in combined_text for x in ['apply', 'application', 'hiring', 'position', 'role', 'job opening', '[hiring]']):
                return False

    # "For hire" / job seeker posts
    exclude = ['[for hire]', 'for hire', '[for-hire]', 'hire me', 'open to work', 'job seeker', 'my services']
    for pattern in exclude:
        if pattern in combined_text and '[hiring]' not in combined_text:
            return False

    # Require strong hiring/opportunity language
    strong = ['[hiring]', 'we are hiring', 'job opening', 'position available', 'apply now', 'join our team',
              'internship program', 'workshop on', 'conference:', 'competition:']
    if not any(p in combined_text for p in strong):
        return False

    return True


def should_save_opportunity(opp_dict: dict) -> bool:
    """
    Central gate: only return True if this opportunity should be saved (real opportunity).
    Uses Ollama to classify; when Ollama is unavailable, rejects by default to avoid false positives.
    """
    title = (opp_dict.get('title') or '').strip()
    description = (opp_dict.get('description') or '')[:500]
    source = (opp_dict.get('source') or 'unknown').strip().lower()

    # Skip AI for configured sources (e.g. structured API job boards)
    skip_sources = getattr(Config, 'SOURCES_SKIP_AI_FILTER', []) or []
    if source in skip_sources:
        return True

    if not Config.is_ai_filter_enabled():
        return True  # Filter disabled -> allow all (backward compat)

    if not title:
        return False

    classification = classify_opportunity(title, description, opp_dict.get('source') or 'unknown')
    is_opportunity = classification.get('is_opportunity')
    confidence = classification.get('confidence', 0.0)
    error = classification.get('error')

    if is_opportunity is True:
        min_conf = getattr(Config, 'AI_FILTER_MIN_CONFIDENCE', 0.7)
        if confidence < min_conf:
            print(f"AI FILTER: Rejecting low-confidence (conf={confidence:.2f} < {min_conf}): {title[:50]}...")
            return False
        print(f"AI FILTER: Accept (conf={confidence:.2f}): {title[:50]}...")
        return True

    if is_opportunity is False:
        print(f"AI FILTER: Reject (not opportunity): {title[:50]}...")
        return False

    # is_opportunity is None -> error (Ollama down, timeout, etc.)
    reject_on_error = getattr(Config, 'AI_FILTER_REJECT_ON_ERROR', True)
    if reject_on_error:
        print(f"AI FILTER: Reject (Ollama error: {error}): {title[:50]}...")
        return False
    # Fallback to keyword filter
    use_fallback = keyword_based_filter_fallback(title, description, source)
    print(f"AI FILTER: Fallback keyword result={use_fallback}: {title[:50]}...")
    return use_fallback
