# Deployment Guide - Hugging Face Spaces

This guide will help you deploy the Voice Bot Interview Assistant to Hugging Face Spaces for free, public access.

## Prerequisites

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co) (free)
2. **Groq API Key**: Get your free API key from [console.groq.com](https://console.groq.com)

## Step-by-Step Deployment

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"New Space"** button
3. Fill in the details:
   - **Space name**: `balamurugan-100x-voicebot` (or your preferred name)
   - **SDK**: Select **"Gradio"**
   - **Visibility**: Select **"Public"** (so anyone can access it)
   - **Hardware**: **CPU Basic** (free tier is sufficient)
4. Click **"Create Space"**

### Step 2: Upload Files

You can upload files in two ways:

#### Option A: Web Interface (Easier)

1. In your Space, click the **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `assets/` folder (Critical: contains reference voice)

#### Option B: Git (Recommended for updates)

1. In your Space, you'll see Git instructions
2. Clone the repository:
   ```bash
   git clone https://huggingface.co/spaces/[your-username]/balamurugan-100x-voicebot
   ```
3. Copy your files into the cloned directory
4. Commit and push:
   ```bash
   git add .
   git commit -m "Initial commit: Voice bot interview assistant"
   git push
   ```

### Step 3: Configure API Key Secret

1. In your Space, go to **"Settings"** tab
2. Scroll down to **"Repository secrets"** section
3. Click **"New secret"**
4. Add:
   - **Secret name**: `GROQ_API_KEY`
   - **Secret value**: Your Groq API key (paste it here)
5. Click **"Add secret"**

**Important**: The secret is hidden from public view, so your API key stays secure.

### Step 4: Wait for Build

1. After uploading files, Hugging Face will automatically start building your Space
2. You'll see a build log - wait for it to complete (usually 2-5 minutes)
3. The build will:
   - Install Python dependencies from `requirements.txt`
   - Download Whisper model (first time only, ~500MB)
   - Start the Gradio application

### Step 5: Test Your Deployment

1. Once the build completes, you'll see a **"Running"** status
2. Click the **"App"** tab or visit your Space URL:
   ```
   https://huggingface.co/spaces/[your-username]/balamurugan-100x-voicebot
   ```
3. Test the voice bot:
   - Click the microphone
   - Speak a question
   - Click "Send"
   - Verify the response

## Troubleshooting

### Build Fails

- **Check `requirements.txt`**: Ensure all dependencies are listed
- **Check `app.py`**: Look for syntax errors in the build log
- **Check API key**: Ensure `GROQ_API_KEY` secret is set correctly

### App Runs But No Response

- **Check API key**: Verify `GROQ_API_KEY` secret is correct
- **Check logs**: Go to "Logs" tab to see error messages
- **Test API key**: Verify your Groq API key works (check rate limits)

### Whisper Model Download Issues

- **First build takes longer**: The Whisper model (~500MB) downloads on first run
- **Check internet**: Ensure Hugging Face can download the model
- **Retry build**: If download fails, rebuild the Space

### Audio Not Working

- **Browser permissions**: Ensure microphone access is granted
- **HTTPS required**: Modern browsers require HTTPS for microphone access (Hugging Face provides this)
- **Test in different browser**: Try Chrome, Firefox, or Edge

## Updating Your Deployment

### To Update Code

1. **Via Web Interface**:
   - Go to "Files and versions" tab
   - Click "Edit" on the file you want to change
   - Make changes and commit

2. **Via Git**:
   ```bash
   git pull  # Get latest changes
   # Make your changes
   git add .
   git commit -m "Update: [description]"
   git push
   ```

### To Update API Key

1. Go to Settings → Repository secrets
2. Edit the `GROQ_API_KEY` secret
3. Save changes
4. Restart the Space (Settings → Restart this Space)

## Continuous Deployment (GitHub Actions)

The project includes a GitHub Action to automatically sync changes to Hugging Face.

### Setup
1. **Get Hugging Face Token**:
   - Go to [Hugging Face Settings > Tokens](https://huggingface.co/settings/tokens)
   - Create a new token with **Write** permissions.

2. **Configure GitHub Secrets**:
   - Go to your GitHub Repo > Settings > Secrets and variables > Actions
   - Click **New repository secret**
   - Name: `HF_TOKEN`
   - Value: (Paste your Hugging Face token)

3. **Update Workflow File**:
   - Open `.github/workflows/sync_to_hub.yml`
   - Update the URL in the last line to match your Space:
     `https://hf_user:$HF_TOKEN@huggingface.co/spaces/[YOUR_USERNAME]/[YOUR_SPACE_NAME]`

4. **Push to GitHub**:
   - Any push to `main` will now automatically deploy to Hugging Face!

## Space Settings

### Recommended Settings

- **Hardware**: CPU Basic (free) - sufficient for this app
- **Sleep time**: 48 hours (free tier sleeps after inactivity)
- **Visibility**: Public (for interview assessment)

### Cost

- **Free tier**: Completely free for public Spaces
- **No credit card required**
- **Rate limits**: Groq free tier has usage limits (check their docs)

## Security Notes

✅ **DO**:
- Store API keys as secrets (never in code)
- Keep Space public for assessment
- Monitor API usage

❌ **DON'T**:
- Commit API keys to repository
- Share API keys publicly
- Exceed rate limits (may cause temporary blocking)

## Submission Checklist

Before submitting your assessment:

- [ ] Space is publicly accessible
- [ ] Voice input works correctly
- [ ] Responses are personalized and accurate
- [ ] Conversation history maintains context
- [ ] Audio playback works
- [ ] No API keys exposed in code
- [ ] README is clear and helpful
- [ ] Tested on different browsers

## Your Submission URL

Once deployed, your submission URL will be:
```
https://huggingface.co/spaces/[your-username]/balamurugan-100x-voicebot
```

Include this URL in your email to bhumika@100x.inc

---

**Need Help?** Check Hugging Face Spaces [documentation](https://huggingface.co/docs/hub/spaces) or Gradio [documentation](https://gradio.app/docs/).

