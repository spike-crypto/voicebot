"""
Test script for Local XTTS-v2 Text-to-Speech
Uses coqui-tts library
"""
import os
import torch
from TTS.api import TTS

def test_local_xtts():
    print("=" * 60)
    print("Testing Local XTTS-v2 (Coqui TTS)")
    print("=" * 60)

    # Check for GPU
    use_gpu = torch.cuda.is_available()
    print(f"🔌 GPU Available: {use_gpu}")
    if use_gpu:
        print(f"🎮 GPU Name: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️  Running on CPU - this might be slow")

    # Reference audio
    # Using one found in uploads
    ref_audio = os.path.join("uploads", "4c44457b-d1a1-4725-9eec-763f2ff2d0ae.mp3")
    
    # Fallback if specific file doesn't exist, try to find any mp3/wav in uploads
    if not os.path.exists(ref_audio):
        print(f"⚠️  Reference file {ref_audio} not found.")
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            files = [f for f in os.listdir(uploads_dir) if f.endswith(('.mp3', '.wav'))]
            if files:
                ref_audio = os.path.join(uploads_dir, files[0])
                print(f"✓ Using alternative reference: {ref_audio}")
            else:
                print("❌ No audio files found in uploads/ for reference voice.")
                return
        else:
            print("❌ uploads/ directory not found.")
            return

    output_file = "output_local_xtts.wav"
    
    try:
        print("\n⏳ Initializing TTS model (this will download the model on first run)...")
        # Initialize TTS
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        
        text = "It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent."
        
        print(f"\n🗣️  Generating speech...")
        print(f"📝 Text: '{text}'")
        print(f"🎤 Reference: {ref_audio}")
        
        # Generate
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker_wav=ref_audio,
            language="en"
        )
        
        print(f"\n✅ SUCCESS! Audio generated.")
        print(f"📁 Saved to: {output_file}")
        print(f"📦 Size: {os.path.getsize(output_file)} bytes")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_xtts()
