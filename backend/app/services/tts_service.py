"""
Text-to-Speech service using Local XTTS-v2 (Coqui TTS)
"""
import logging
import os
import uuid
import torch
from typing import Tuple, Optional
from flask import current_app
from app.utils.cache import get_cache, set_cache, get_cache_key

# Import Coqui TTS
try:
    from TTS.api import TTS
except ImportError:
    TTS = None

logger = logging.getLogger(__name__)

# Global variable to hold the model instance (Singleton pattern)
_tts_model = None

def get_tts_model():
    """
    Get or initialize the TTS model.
    This ensures we only load the heavy model once.
    """
    global _tts_model
    if _tts_model is None:
        if TTS is None:
            raise ImportError("coqui-tts package not installed. Please install it to use local TTS.")
            
        logger.info("Initializing XTTS-v2 model... (this may take a moment)")
        use_gpu = torch.cuda.is_available()
        device = "cuda" if use_gpu else "cpu"
        logger.info(f"TTS Device: {device}")
        
        try:
            # Load the model (YourTTS is ~9x faster on CPU than XTTS-v2)
            _tts_model = TTS("tts_models/multilingual/multi-dataset/your_tts", gpu=use_gpu)
            logger.info("YourTTS model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize XTTS-v2 model: {str(e)}")
            raise e
            
    return _tts_model

def text_to_speech(text: str, use_cache: bool = True) -> Tuple[str, bool]:
    """
    Convert text to speech using local XTTS-v2 model
    
    Args:
        text: Text to convert to speech
        use_cache: Whether to use caching
    
    Returns:
        Tuple of (audio_file_path, cache_hit)
    """
    cache_hit = False
    
    # Try to get from cache
    if use_cache:
        cache_key = get_cache_key('tts', text)
        cached_path = get_cache(cache_key)
        if cached_path:
            # Validate cached path exists
            if os.path.exists(cached_path):
                logger.info("Cache hit for TTS")
                return cached_path, True
            
            # Check relative paths if absolute path not found
            # (Logic from previous implementation to handle path variations)
            try:
                if not os.path.isabs(cached_path):
                    possible_paths = [
                        os.path.join(current_app.root_path, cached_path),
                        os.path.join(os.path.abspath(os.path.join(current_app.root_path, '..')), cached_path),
                        os.path.join(os.getcwd(), cached_path)
                    ]
                    for p in possible_paths:
                        if os.path.exists(p):
                            logger.info("Cache hit for TTS (resolved relative path)")
                            return p, True
            except Exception:
                pass
                
            logger.info(f"Cached TTS path not found, will regenerate: {cached_path}")

    try:
        # Clean text for TTS
        clean_text = text.replace('**', '').replace('*', '').replace('__', '').replace('`', '')
        logger.info(f"Generating speech for: '{clean_text[:50]}...'")

        # Setup paths
        upload_rel = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        upload_folder = os.path.join(current_app.root_path, upload_rel)
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"{uuid.uuid4()}.wav"  # XTTS outputs wav by default
        audio_path = os.path.join(upload_folder, filename)
        audio_path = os.path.abspath(audio_path)
        
        # Get reference audio for voice cloning
        # Look for assets/reference_voice.mp3 first
        assets_dir = os.path.join(os.path.dirname(current_app.root_path), 'assets')
        ref_audio = os.path.join(assets_dir, 'reference_voice.mp3')
        
        if not os.path.exists(ref_audio):
            # Fallback to searching uploads if asset not found
            logger.warning(f"Reference voice not found at {ref_audio}, searching uploads...")
            uploads_search = os.path.join(current_app.root_path, 'uploads')
            if os.path.exists(uploads_search):
                files = [f for f in os.listdir(uploads_search) if f.endswith(('.mp3', '.wav'))]
                if files:
                    ref_audio = os.path.join(uploads_search, files[0])
                    logger.info(f"Using fallback reference audio: {ref_audio}")
                else:
                    raise FileNotFoundError("No reference audio found for voice cloning")
            else:
                raise FileNotFoundError("Uploads directory not found")
        
        # Get model instance
        tts = get_tts_model()
        
        # Generate speech
        tts.tts_to_file(
            text=clean_text,
            file_path=audio_path,
            speaker_wav=ref_audio,
            language="en"
        )
        
        # Verify output
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise Exception("TTS generation produced empty or missing file")
            
        logger.info(f"TTS generation successful: {audio_path}")
        
        # Cache result
        if use_cache:
            cache_key = get_cache_key('tts', text)
            set_cache(cache_key, audio_path, ttl=3600)
            
        return audio_path, cache_hit
        
    except Exception as e:
        logger.error(f"TTS error: {str(e)}", exc_info=True)
        raise Exception(f"Failed to convert text to speech: {str(e)}")

