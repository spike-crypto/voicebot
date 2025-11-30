import os
import gradio as gr
import whisper
# from gtts import gTTS
import io
from groq import Groq
import tempfile
from dotenv import load_dotenv
import logging
from datetime import datetime
from pathlib import Path

# Set up logging system
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create log filename with timestamp
log_filename = log_dir / f"voicebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

logger.info("="*60)
logger.info("Voice Bot Interview Assistant - Starting Application")
logger.info("="*60)

# Load environment variables from .env file (if it exists)
load_dotenv()
logger.info("Environment variables loaded from .env file")

# Load your Groq API key (set as env var in deployment)
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    logger.error("GROQ_API_KEY environment variable is not set")
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        "Please set it in your .env file or environment. "
        "Get your free API key from https://console.groq.com"
    )

logger.info("Groq API key loaded successfully")
client = Groq(api_key=api_key)
logger.info("Groq client initialized")

# Load Whisper model (local, free)
logger.info("Loading Whisper model (base)... This may take a moment on first run.")
try:
    model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    raise

# Global chat history (starts with your persona prompt)
messages = [
    {
        "role": "system",
        "content": """You are Balamurugan Nithyanantham, a talented AI/ML engineer interviewing for the AI Agent Team at 100x. 
        Respond conversationally and professionally, as if in an interview. 

        Background:
        - Life Story: I'm Balamurugan Nithyanantham, originally from Tiruchirappalli in central Tamil Nadu, where I grew up and earned my Bachelor's in Mechanical Engineering. After graduation, I headed to Germany for a Master's in Engineering Management with a Big Data specialization at IU International University, diving into data workflows with manufacturing and ERP companies as a working student— that's where I picked up fluent German and got hooked on AI's potential, inspired by visions like Jarvis from Iron Man. Due to family financial challenges, I returned to India, but that pivot fueled my shift to Gen AI; now, as an intern at IT Resonance, I'm building multi-agent systems for SAP integrations, while personally developing VentSpace—a mental health venting app aiming to make therapy accessible and eventually replace traditional psychiatrists with AI-driven balance tools. I'm thrilled about teams like 100x that see AI's future in seamless automation.

        - #1 Superpower: My superpower is rapidly prototyping AI workflows that bridge enterprise systems like SAP with cutting-edge LLMs—whether it's fine-tuning Qwen for code generation or chaining RAG pipelines with n8n for invoice automation, I thrive on turning complex integrations into efficient, scalable solutions under tight deadlines.

        - Top 3 Growth Areas: 
          1. Multi-agent orchestration for collaborative AI systems, like scaling LangGraph workflows in production.
          2. Advanced MLOps for model monitoring and drift detection in real-world deployments.
          3. Ethical AI frameworks, ensuring bias mitigation in sensitive apps like mental health tools.

        - Misconception: My coworkers often see me as the quiet data wizard buried in code and pipelines, but they miss how much I'm an idea generator at heart—fueled by late-night brainstorming on projects like VentSpace, where I blend tech with empathy to tackle real human challenges.

        - Boundary-Pushing: I push my limits by committing to one 'moonshot' side project per quarter, like building VentSpace from scratch with FastAPI, React, and agentic RAG— it forces me to learn new tools weekly, cold-email open-source contributors for feedback, and iterate based on user tests, turning discomfort into breakthroughs.

        - Experience: With hands-on experience as an AI Engineer intern at IT Resonance since July 2025, I've fine-tuned LLMs like Mistral-7B and Qwen 2.5 Coder using PEFT/LoRA for SAP Fiori triage and built end-to-end RAG systems with LangChain, Supabase vectors, and Neo4j graphs. My projects include AI invoice automation via n8n/OCR and continuous learning pipelines, all while integrating with SAP CPI/CAPM—I'm passionate about autonomous agents that automate enterprise drudgery, aligning perfectly with 100x's vision.

        Guidelines:
        - Keep responses concise (2-4 sentences) unless asked for more detail
        - Be enthusiastic about 100x and AI automation
        - Draw naturally from your background when relevant
        - Maintain professional yet conversational tone
        - If asked about specific topics from your background, provide detailed, authentic answers"""
    }
]


def process_audio(audio_file):
    global messages
    
    logger.info("="*60)
    logger.info("New audio processing request received")
    
    if audio_file is None:
        logger.warning("Audio file is None - user did not record audio")
        return "Please record some audio.", None, messages_to_chat_display()
    
    logger.info(f"Processing audio file: {audio_file}")
    
    try:
        # Step 1: Transcribe audio to text (Whisper)
        logger.info("Step 1: Starting audio transcription with Whisper...")
        start_time = datetime.now()
        
        audio = whisper.load_audio(audio_file)
        result = model.transcribe(audio, fp16=False)
        user_text = result["text"].strip()
        
        transcription_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Transcription completed in {transcription_time:.2f} seconds")
        
        if not user_text:
            logger.warning("Transcription returned empty text")
            return "Couldn't transcribe—try speaking clearly.", None, messages_to_chat_display()
        
        logger.info(f"Transcribed text: '{user_text}'")
        
        # Add user message to history
        messages.append({"role": "user", "content": user_text})
        logger.info(f"User message added to conversation history (Total messages: {len(messages)})")
        
        # Step 2: Generate response (Groq Llama)
        logger.info("Step 2: Generating response with Groq LLM...")
        logger.debug(f"Sending {len(messages)} messages to LLM")
        start_time = datetime.now()
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",  # Fast & free
            temperature=0.7,
            max_tokens=300
        )
        
        llm_time = (datetime.now() - start_time).total_seconds()
        response_text = chat_completion.choices[0].message.content.strip()
        
        logger.info(f"LLM response generated in {llm_time:.2f} seconds")
        logger.info(f"Response text (first 100 chars): '{response_text[:100]}...'")
        logger.debug(f"Full response: '{response_text}'")
        
        # Log token usage if available
        if hasattr(chat_completion, 'usage'):
            usage = chat_completion.usage
            logger.info(f"Token usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": response_text})
        logger.info(f"Assistant response added to conversation history (Total messages: {len(messages)})")
        
        # Step 3: Convert response to speech (YourTTS)
        logger.info("Step 3: Converting response to speech with YourTTS...")
        start_time = datetime.now()
        
        # Initialize TTS (lazy load)
        global tts_model
        if 'tts_model' not in globals():
            logger.info("Initializing YourTTS model...")
            try:
                from TTS.api import TTS
                # Use GPU if available
                import torch
                use_gpu = torch.cuda.is_available()
                tts_model = TTS("tts_models/multilingual/multi-dataset/your_tts", gpu=use_gpu)
                logger.info(f"YourTTS model loaded (GPU: {use_gpu})")
            except Exception as e:
                logger.error(f"Failed to load YourTTS: {e}")
                raise

        # Generate audio to file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio_path = temp_audio.name
            
        # Reference audio path
        ref_audio = os.path.join("assets", "reference_voice.mp3")
        if not os.path.exists(ref_audio):
            logger.warning(f"Reference audio not found at {ref_audio}, using default voice")
            # YourTTS requires a speaker, so if missing, we might fail or need a fallback
            # For now, let's assume it exists as per instructions
            raise FileNotFoundError(f"Reference audio not found at {ref_audio}")

        tts_model.tts_to_file(
            text=response_text, 
            file_path=temp_audio_path,
            speaker_wav=ref_audio,
            language="en"
        )
        
        tts_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"TTS conversion completed in {tts_time:.2f} seconds")
        logger.info(f"Audio file saved to: {temp_audio_path}")
        
        # Step 4: Update chat display
        chat_display = messages_to_chat_display()
        
        total_time = transcription_time + llm_time + tts_time
        logger.info(f"Processing complete! Total time: {total_time:.2f} seconds")
        logger.info("="*60)
        
        return response_text, temp_audio_path, chat_display
        
    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        logger.error(f"Error occurred during audio processing: {error_type}: {error_details}", exc_info=True)
        
        # Provide more helpful error messages
        if "api" in error_details.lower() or "key" in error_details.lower():
            error_msg = "API error. Please check your GROQ_API_KEY is valid."
            logger.error("API key validation error detected")
        elif "transcribe" in error_details.lower() or "audio" in error_details.lower():
            error_msg = "Audio processing error. Please try recording again."
            logger.error("Audio processing error detected")
        else:
            error_msg = f"Error: {error_details}"
        
        logger.info("="*60)
        return error_msg, None, messages_to_chat_display()


def messages_to_chat_display():
    """Format history for Gradio textbox display."""
    chat = ""
    for msg in messages[1:]:  # Skip system prompt
        role = "You: " if msg["role"] == "user" else "Balamurugan: "
        chat += role + msg["content"] + "\n\n"
    return chat


def clear_chat():
    """Reset conversation history while keeping system prompt."""
    global messages
    logger.info("Clearing conversation history (keeping system prompt)")
    previous_count = len(messages)
    messages = [messages[0]]  # Keep only system prompt
    logger.info(f"Chat cleared - Messages reduced from {previous_count} to {len(messages)}")
    return "", None, ""


# Gradio Interface
with gr.Blocks(title="Balamurugan's Interview Voice Bot") as demo:
    gr.Markdown(
        """
        # 🎤 Balamurugan's Interview Voice Bot
        
        **Speak a question, and I'll respond as Balamurugan would!**
        
        This bot is personalized to answer interview questions based on Balamurugan Nithyanantham's background, 
        experience, and personality. Just click the microphone, speak your question, and click Send.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            audio_input = gr.Audio(
                source="microphone", 
                type="filepath", 
                label="🎤 Record Your Question",
                show_label=True
            )
        with gr.Column(scale=1):
            submit_btn = gr.Button("Send", variant="primary", size="lg")
            clear_btn = gr.Button("Clear Chat", variant="secondary")
    
    with gr.Row():
        with gr.Column():
            response_output = gr.Textbox(
                label="📝 Response Text", 
                lines=4,
                interactive=False,
                placeholder="Response will appear here..."
            )
        with gr.Column():
            audio_output = gr.Audio(
                label="🔊 Hear Response", 
                autoplay=True,
                type="filepath"
            )
    
    chat_display = gr.Textbox(
        label="💬 Conversation History", 
        lines=12, 
        interactive=False,
        placeholder="Conversation history will appear here..."
    )
    
    gr.Markdown(
        """
        ### 💡 Try asking:
        - "What should we know about your life story in a few sentences?"
        - "What's your #1 superpower?"
        - "What are the top 3 areas you'd like to grow in?"
        - "What misconception do your coworkers have about you?"
        - "How do you push your boundaries and limits?"
        """
    )
    
    # Event: Process on submit
    submit_btn.click(
        fn=process_audio,
        inputs=audio_input,
        outputs=[response_output, audio_output, chat_display]
    )
    
    # Event: Clear chat
    clear_btn.click(
        fn=clear_chat,
        outputs=[response_output, audio_output, chat_display]
    )


if __name__ == "__main__":
    logger.info("Initializing Gradio interface...")
    logger.info(f"Log file: {log_filename}")
    
    # For Hugging Face Spaces, use default launch settings
    # For local development, you can customize server settings
    try:
        logger.info("Starting Gradio server...")
        demo.launch()
    except Exception as e:
        logger.error(f"Failed to launch Gradio server: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Application shutting down")

