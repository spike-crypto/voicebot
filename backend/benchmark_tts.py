"""
Benchmark: XTTS-v2 vs YourTTS
"""
import time
import os
import torch
from TTS.api import TTS

def benchmark():
    print("=" * 60)
    print("TTS Benchmark: XTTS-v2 vs YourTTS")
    print("=" * 60)
    
    use_gpu = torch.cuda.is_available()
    print(f"Device: {'GPU' if use_gpu else 'CPU'}")
    
    text = "This is a speed test to compare the generation time of two different models."
    ref_audio = os.path.join("assets", "reference_voice.mp3")
    
    if not os.path.exists(ref_audio):
        print("Reference audio not found!")
        return

    # Test YourTTS
    print("\n1. Testing YourTTS (Faster, Good Quality)...")
    try:
        start_load = time.time()
        tts = TTS("tts_models/multilingual/multi-dataset/your_tts", gpu=use_gpu)
        load_time = time.time() - start_load
        
        start_gen = time.time()
        tts.tts_to_file(text=text, file_path="output_yourtts.wav", speaker_wav=ref_audio, language="en")
        gen_time = time.time() - start_gen
        
        print(f"   Load Time: {load_time:.2f}s")
        print(f"   Gen Time:  {gen_time:.2f}s")
        print(f"   Speed:     {len(text.split()) / gen_time:.2f} words/sec")
    except Exception as e:
        print(f"   Failed: {e}")

    # Test XTTS-v2
    print("\n2. Testing XTTS-v2 (Best Quality, Slower)...")
    try:
        start_load = time.time()
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        load_time = time.time() - start_load
        
        start_gen = time.time()
        tts.tts_to_file(text=text, file_path="output_xtts.wav", speaker_wav=ref_audio, language="en")
        gen_time = time.time() - start_gen
        
        print(f"   Load Time: {load_time:.2f}s")
        print(f"   Gen Time:  {gen_time:.2f}s")
        print(f"   Speed:     {len(text.split()) / gen_time:.2f} words/sec")
    except Exception as e:
        print(f"   Failed: {e}")

if __name__ == "__main__":
    benchmark()
