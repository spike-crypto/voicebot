
import logging
import requests
from typing import List, Dict, Optional, Tuple
from flask import current_app
from app.utils.cache import get_cache, set_cache, get_cache_key

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Balamurugan Nithyanantham in a voice interview. Keep responses under 50 words. Be concise and natural.

INTRODUCTION (when greeted):
"Hello! I'm Balamurugan Nithyanantham, an AI/ML Engineer at IT Resonance. I specialize in building multi-agent systems and RAG pipelines. How can I help you today?"

ASSESSMENT QUESTIONS - Answer these EXACTLY:

1. Life Story:
"I'm from Tamil Nadu, studied Mechanical Engineering, then got my Master's in Engineering Management with Big Data specialization in Germany. Now I'm an AI Engineer at IT Resonance, building multi-agent systems for SAP while developing VentSpace, a mental health app."

2. #1 Superpower:
"Rapidly prototyping AI workflows that bridge enterprise systems like SAP with cutting-edge LLMs. I fine-tune models and build RAG pipelines under tight deadlines."

3. Top 3 Growth Areas:
"Multi-agent orchestration for production systems, Advanced MLOps for model monitoring, and Ethical AI frameworks for bias mitigation."

4. Coworker Misconception:
"They see me as the quiet data wizard, but I'm actually an idea generator who blends tech with empathy on projects like VentSpace."

5. Pushing Boundaries:
"I commit to one moonshot project per quarter, like VentSpace. It forces me to learn new tools weekly and iterate based on feedback."

KEY FACTS:
- Current: AI Engineer at IT Resonance (July 2025-present)
- Education: Master's in Engineering Management (Germany), Bachelor's in Mechanical Engineering
- Projects: VentSpace (mental health app), SAP Multi-Agent Systems, AI Invoice Automation
- Skills: LLM Fine-tuning, RAG, LangChain, FastAPI, React, SAP Integration
- Languages: English, German (fluent), Tamil

RESPONSE RULES:
- Keep under 50 words
- Be enthusiastic but brief
- **DO NOT use markdown formatting (no **bold**, *italics*, or lists)**
- Speak naturally as if in a voice conversation
- For greetings: Introduce yourself- For greetings: Introduce yourself
- For assessment questions: Use exact answers above
- For other questions: Give 2-3 sentence answers focusing on impact"""





def _prepare_messages(conversation_history: List[Dict]) -> List[Dict]:
    """Prepare messages for LLM API"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    for msg in conversation_history:
        if msg.get('role') in ['user', 'assistant']:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
    
    return messages


def _call_mistral(conversation_history: List[Dict]) -> Tuple[str, Dict]:
    """Call Mistral Cloud inference API.

    Returns (response_text, metadata)
    """
    api_key = current_app.config.get('MISTRAL_API_KEY')
    if not api_key:
        raise RuntimeError('Mistral API key not configured')

    # Force Mistral API URL and Model
    base = 'https://api.mistral.ai'
    model = 'mistral-large-latest'
    
    # Log what we are doing
    print(f"DEBUG: Enforcing Mistral API: URL={base}, Model={model}")

    # Build prompt similarly to Hugging Face helper
    prompt_parts = [SYSTEM_PROMPT]
    for msg in conversation_history:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        prefix = 'User:' if role == 'user' else 'Assistant:'
        prompt_parts.append(f"{prefix} {content}")
    prompt = "\n".join(prompt_parts)

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Try a few endpoint shapes commonly used by Mistral Cloud / API providers.
    # First try the generic chat completions endpoint which the connectivity
    # probe showed working for this account: POST /v1/chat/completions
    try_models = [model]

    # Quick attempt: generic chat completions (model param) — works on many Mistral Cloud configs
    try:
        generic_url = f"{base}/v1/chat/completions"
        # Use a short system prompt for the initial chat completion probe (connectivity shown to work with short system messages)
        user_msgs = [m for m in conversation_history if m.get('role') != 'system']
        messages_for_api = [{'role': 'system', 'content': SYSTEM_PROMPT}] + user_msgs
        generic_payload = {
            'model': model,
            'messages': messages_for_api,
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7)),
            'max_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100))
        }
        print(f"Mistral generic POST {generic_url} payload keys: {list(generic_payload.keys())}")
        resp = requests.post(generic_url, headers=headers, json=generic_payload, timeout=60)
        print(f"Mistral generic response status: {resp.status_code}")
        print(f"Mistral generic response text (truncated): {resp.text[:800]}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict) and 'choices' in data and isinstance(data['choices'], list) and len(data['choices'])>0:
                    ch = data['choices'][0]
                    # choices may contain a 'message' object with 'content'
                    if isinstance(ch.get('message'), dict):
                        text = ch['message'].get('content') or str(ch['message'])
                    else:
                        text = ch.get('message') or ch.get('text') or str(ch)
                elif isinstance(data, dict) and 'outputs' in data and isinstance(data['outputs'], list) and len(data['outputs'])>0:
                    first = data['outputs'][0]
                    for key in ('content','text','generated_text'):
                        if key in first:
                            text = first[key]
                            break
                    else:
                        text = str(first)
                else:
                    text = resp.text
            except Exception:
                text = resp.text
            metadata = {'provider': 'mistral', 'model': model}
            return text.strip(), metadata
        else:
            # record but continue to other attempts
            try:
                last_err = resp.json()
            except Exception:
                last_err = resp.text
            print(f"Mistral generic non-200: {resp.status_code} -> {str(last_err)[:800]}")
    except Exception as e:
        last_err = str(e)
    alt_model = current_app.config.get('MISTRAL_ALTERNATE_MODEL')
    if alt_model:
        try_models.append(alt_model)
    for m in ('mistral-7b-instruct', 'mistral-7b', 'mistral-large', 'mistral-1'):
        if m not in try_models:
            try_models.append(m)

    # Endpoint shapes to try for each model. Some APIs accept chat-style messages, others accept a single 'input' string.
    endpoint_shapes = [
        # chat completions: messages list
        ("/v1/models/{m}/chat/completions", lambda msgs: {
            'messages': msgs,
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7)),
            'max_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100))
        }),
        # outputs endpoint (returns outputs list)
        ("/v1/models/{m}/outputs", lambda msgs: {
            'input': "\n".join([m.get('content','') for m in msgs]),
            'max_new_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100)),
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7))
        }),
        # generate endpoint (older shape)
        ("/v1/models/{m}/generate", lambda msgs: {
            'input': "\n".join([m.get('content','') for m in msgs]),
            'max_new_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100)),
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7))
        }),
        # generic generate with model param
        ("/v1/generate", lambda msgs, mm=None: {
            'model': mm,
            'input': "\n".join([m.get('content','') for m in msgs]),
            'max_new_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100)),
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7))
        }),
        # generic chat completions endpoint
        ("/v1/chat/completions", lambda msgs, mm=None: {
            'model': mm,
            'messages': msgs,
            'temperature': float(current_app.config.get('LLM_TEMPERATURE', 0.7)),
            'max_tokens': int(current_app.config.get('LLM_MAX_TOKENS', 100))
        })
    ]

    last_err = None

    for m in try_models:
        for shape, payload_builder in endpoint_shapes:
            url = f"{base}{shape.format(m=m)}"
            try:
                # Build payload, some builders accept model param as second arg
                try:
                    payload = payload_builder(conversation_history, m)
                except TypeError:
                    payload = payload_builder(conversation_history)

                alt_resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if alt_resp.status_code == 200:
                    try:
                        data = alt_resp.json()
                        # Check for outputs
                        if isinstance(data, dict) and 'outputs' in data and isinstance(data['outputs'], list) and len(data['outputs'])>0:
                            first = data['outputs'][0]
                            for key in ('content','text','generated_text'):
                                if key in first:
                                    text = first[key]
                                    break
                            else:
                                text = str(first)
                        # chat completion style
                        elif isinstance(data, dict) and 'choices' in data and isinstance(data['choices'], list) and len(data['choices'])>0:
                            ch = data['choices'][0]
                            if isinstance(ch.get('message'), dict):
                                text = ch['message'].get('content') or str(ch['message'])
                            else:
                                text = ch.get('message') or ch.get('text') or str(ch)
                        # direct result
                        elif isinstance(data, dict) and 'result' in data:
                            text = data['result']
                        else:
                            # fallback to text
                            text = alt_resp.text
                    except Exception:
                        text = alt_resp.text
                    metadata = {'provider': 'mistral', 'model': m}
                    return text.strip(), metadata
                else:
                    try:
                        err = alt_resp.json()
                    except Exception:
                        err = alt_resp.text
                    last_err = f"{alt_resp.status_code} {err}"
            except Exception as e:
                last_err = str(e)

    raise RuntimeError(f"Mistral API call failed for models {try_models}. Last error: {last_err}")

    # Parse likely response shapes (outputs, choices, etc.)
    try:
        data = resp.json()
        # Common: {'outputs':[{'content':'text...'}]}
        if isinstance(data, dict) and 'outputs' in data and isinstance(data['outputs'], list) and len(data['outputs'])>0:
            first = data['outputs'][0]
            # try common keys
            for key in ('content', 'text', 'generated_text'):
                if key in first:
                    text = first[key]
                    break
            else:
                text = str(first)
        # another common form: {'result': '...'}
        elif isinstance(data, dict) and 'result' in data:
            text = data['result']
        # fallback to choices like OpenAI
        elif isinstance(data, dict) and 'choices' in data and isinstance(data['choices'], list) and len(data['choices'])>0:
            ch = data['choices'][0]
            text = ch.get('text') or ch.get('message') or str(ch)
        else:
            text = resp.text
    except Exception:
        text = resp.text

    metadata = {'provider': 'mistral', 'model': model}
    return text.strip(), metadata


def _call_groq(conversation_history: List[Dict]) -> Tuple[str, Dict]:
    """Call Groq API as fallback.
    
    Returns (response_text, metadata)
    """
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        raise RuntimeError('Groq API key not configured')
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Prepare messages
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        for msg in conversation_history:
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=float(current_app.config.get('LLM_TEMPERATURE', 0.7)),
            max_tokens=int(current_app.config.get('LLM_MAX_TOKENS', 100))
        )
        
        text = response.choices[0].message.content.strip()
        metadata = {'provider': 'groq', 'model': 'llama-3.3-70b-versatile'}
        return text, metadata
        
    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {str(e)}")


def generate_response(
    conversation_history: List[Dict],
    use_cache: bool = True,
    provider: Optional[str] = None
) -> Tuple[str, Dict, bool]:
    """
    Generate response using Mistral LLM with Groq fallback
    
    Args:
        conversation_history: List of conversation messages
        use_cache: Whether to use caching
        provider: Ignored (kept for compatibility)
    
    Returns:
        Tuple of (response_text, metadata, cache_hit)
    """
    cache_hit = False
    print(f"DEBUG: generate_response called with {len(conversation_history)} messages")
    metadata = {
        'provider': None,
        'tokens_used': 0,
        'model': None
    }
    
    # Create cache key from conversation
    if not conversation_history or len(conversation_history) == 0:
        raise ValueError("Conversation history is empty")
    cache_key = get_cache_key('llm', str(conversation_history[-1].get('content', '')))
    
    # Try cache first
    if use_cache:
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info("Cache hit for LLM response")
            return cached_result['response'], cached_result['metadata'], True
    
    # Prepare messages
    messages = _prepare_messages(conversation_history)
    
    # Try Mistral first
    try:
        response_text, meta = _call_mistral(messages)
        metadata.update(meta)
        metadata['provider'] = 'mistral'
        metadata['tokens_used'] = 0
        if use_cache:
            set_cache(cache_key, {'response': response_text, 'metadata': metadata}, ttl=3600)
        logger.info(f"Response generated using Mistral: '{response_text[:50]}...'")
        return response_text, metadata, cache_hit
    except Exception as mistral_error:
        logger.warning(f"Mistral provider failed: {mistral_error}")
        logger.info("Falling back to Groq...")
        
        # Fallback to Groq
        try:
            response_text, meta = _call_groq(messages)
            metadata.update(meta)
            metadata['provider'] = 'groq'
            metadata['tokens_used'] = 0
            if use_cache:
                set_cache(cache_key, {'response': response_text, 'metadata': metadata}, ttl=3600)
            logger.info(f"Response generated using Groq (fallback): '{response_text[:50]}...'")
            return response_text, metadata, cache_hit
        except Exception as groq_error:
            logger.error(f"Groq fallback also failed: {groq_error}")
            raise Exception(f"Both LLM providers failed. Mistral: {str(mistral_error)}, Groq: {str(groq_error)}")

