"""
Diagnostic script to check current configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("CONFIGURATION DIAGNOSTIC")
print("=" * 60)

# Mistral Keys
print("\n🤖 MISTRAL CONFIGURATION:")
mistral_key = os.environ.get('MISTRAL_API_KEY')
mistral_base = os.environ.get('MISTRAL_API_BASE')
mistral_model = os.environ.get('MISTRAL_MODEL')

print(f"Mistral Key: {'✅ SET' if mistral_key else '❌ NOT SET'} ({mistral_key[:20] + '...' if mistral_key else 'None'})")
print(f"Mistral Base: {mistral_base or 'NOT SET (will use default: https://api.mistral.ai)'}")
print(f"Mistral Model: {mistral_model or 'NOT SET (will use default: mistral-large-latest)'}")

# Groq (should not be used)
print("\n⚠️ GROQ CONFIGURATION (should be ignored):")
groq_key = os.environ.get('GROQ_API_KEY')
groq_model = os.environ.get('GROQ_MODEL')
print(f"Groq Key: {'SET (but ignored)' if groq_key else 'NOT SET'}")
print(f"Groq Model: {groq_model or 'NOT SET'}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

if not mistral_key:
    print("❌ Add MISTRAL_API_KEY to .env")

print("\n✅ All checks complete!")
