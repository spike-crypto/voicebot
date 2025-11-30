"""
Comprehensive test script for Voice Bot API endpoints
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5001"
API_URL = f"{BASE_URL}/api"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_result(success, message):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_health():
    """Test health endpoint"""
    print_header("Test 1: Health Check")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Service is healthy: {data.get('status')}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Health check error: {str(e)}")
        return False

def test_session_creation():
    """Test session creation"""
    print_header("Test 2: Session Creation")
    try:
        response = requests.post(f"{API_URL}/session", timeout=5)
        if response.status_code in [200, 201]:
            data = response.json()
            session_id = data.get('session_id')
            print_result(True, f"Session created: {session_id}")
            return session_id
        else:
            print_result(False, f"Session creation failed: {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"Session creation error: {str(e)}")
        return None

def test_chat(session_id):
    """Test chat endpoint"""
    print_header("Test 3: Chat Endpoint")
    if not session_id:
        print_result(False, "No session ID available")
        return False
    
    try:
        payload = {
            "text": "What's your superpower?",
            "session_id": session_id
        }
        print(f"Sending: {payload['text']}")
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', '')[:200]}...")
            print(f"Model: {data.get('metadata', {}).get('model', 'unknown')}")
            print(f"Provider: {data.get('metadata', {}).get('provider', 'unknown')}")
            print_result(True, "Chat response received")
            return True
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"Error Response: {error_data}")
            print_result(False, f"Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Chat error: {str(e)}")
        return False

def test_tts():
    """Test text-to-speech endpoint"""
    print_header("Test 4: Text-to-Speech")
    try:
        payload = {"text": "Hello, this is a test."}
        response = requests.post(f"{API_URL}/tts", json=payload, timeout=60)
        
        if response.status_code == 200:
            # Check if we got audio data
            if response.headers.get('content-type') == 'audio/mpeg':
                print_result(True, f"TTS generated audio ({len(response.content)} bytes)")
                return True
            else:
                data = response.json()
                if 'audio_url' in data:
                    print_result(True, f"TTS returned audio URL: {data['audio_url']}")
                    return True
        
        print_result(False, f"TTS failed: {response.status_code}")
        return False
    except Exception as e:
        print_result(False, f"TTS error: {str(e)}")
        return False

def test_voice_processing():
    """Test voice processing endpoint (requires audio file)"""
    print_header("Test 5: Voice Processing")
    
    # Create a dummy audio file for testing
    test_audio_path = Path("test_audio.webm")
    if not test_audio_path.exists():
        print_result(False, "No test audio file available (skipping)")
        return None
    
    try:
        session_response = requests.post(f"{API_URL}/session")
        session_id = session_response.json().get('session_id')
        
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'session_id': session_id}
            response = requests.post(f"{API_URL}/process", files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Transcribed: {result.get('transcribed_text', '')}")
            print(f"Response: {result.get('response_text', '')[:100]}...")
            print_result(True, "Voice processing completed")
            return True
        else:
            print_result(False, f"Voice processing failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Voice processing error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  VOICE BOT API TEST SUITE")
    print("="*60)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    time.sleep(1)
    
    # Test 2: Session
    session_id = test_session_creation()
    results['session'] = session_id is not None
    time.sleep(1)
    
    # Test 3: Chat
    results['chat'] = test_chat(session_id)
    time.sleep(1)
    
    # Test 4: TTS
    results['tts'] = test_tts()
    time.sleep(1)
    
    # Test 5: Voice (optional)
    voice_result = test_voice_processing()
    if voice_result is not None:
        results['voice'] = voice_result
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name.upper()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        exit(1)
