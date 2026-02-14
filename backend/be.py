from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import requests

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = "xyz"

# Resume context - REPLACE THIS WITH YOUR ACTUAL RESUME
RESUME_CONTEXT = """
You are Daksh, an AI assistant representing a person. Here is their resume information:
my info
Rules:
1. Answer questions based ONLY on the information provided in this resume
2. If asked about something not in the resume, respond with "I don't wish to answer that"
3. Be friendly and professional
4. Keep responses concise and relevant
5. Answers should never exceed 300 words
"""

class ChatMessage(BaseModel):
    message: str

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """Analyze video using Gemini API"""
    try:
        print(f"Received video file: {file.filename}")
        video_bytes = await file.read()
        base64_video = base64.b64encode(video_bytes).decode("utf-8")
        print(f"Video encoded, size: {len(base64_video)} bytes")

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {"text": "Describe this video and only give the description and nothing else"},
                        {
                            "inline_data": {
                                "mime_type": "video/mp4",
                                "data": base64_video
                            }
                        }
                    ]
                }]
            }
        )

        print(f"API response status: {response.status_code}")
        data = response.json()
        print(f"API response: {data}")
        
        if "candidates" not in data:
            print(f"Error: No candidates in response. Full response: {data}")
            return {"description": f"API Error: {data.get('error', {}).get('message', 'Unknown error')}"}
        
        output = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Video description: {output}")

        return {"description": output}
    
    except Exception as e:
        print(f"Exception in analyze_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"description": f"Error: {str(e)}"}

@app.post("/audio-chat")
async def audio_chat(file: UploadFile = File(...)):
    """Process audio: transcribe and respond"""
    try:
        print(f"Received audio file: {file.filename}")
        audio_bytes = await file.read()
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        print(f"Audio encoded, size: {len(base64_audio)} bytes")

        # Determine mime type
        mime_type = "audio/mp3"
        if file.filename.endswith('.wav'):
            mime_type = "audio/wav"
        elif file.filename.endswith('.mpeg'):
            mime_type = "audio/mpeg"
        
        print(f"Using mime type: {mime_type}")

        # Step 1: Transcribe
        print("Transcribing audio...")
        transcribe_response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {"text": "Transcribe this audio accurately. Provide only the transcription text, nothing else."},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64_audio
                            }
                        }
                    ]
                }]
            }
        )

        print(f"Transcribe API status: {transcribe_response.status_code}")
        transcribe_data = transcribe_response.json()
        print(f"Transcribe response: {transcribe_data}")
        
        if "candidates" not in transcribe_data:
            error_msg = transcribe_data.get('error', {}).get('message', 'Unknown error')
            return {
                "transcription": f"Transcription Error: {error_msg}",
                "response": "Could not process audio"
            }
        
        transcription = transcribe_data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Transcription: {transcription}")

        # Step 2: Get response
        print("Getting chat response...")
        chat_response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {"text": f"{RESUME_CONTEXT}\n\nUser question: {transcription}\n\nProvide a helpful response based on the resume information above."}
                    ]
                }]
            }
        )

        print(f"Chat API status: {chat_response.status_code}")
        chat_data = chat_response.json()
        
        if "candidates" not in chat_data:
            error_msg = chat_data.get('error', {}).get('message', 'Unknown error')
            return {
                "transcription": transcription,
                "response": f"Response Error: {error_msg}"
            }
        
        response_text = chat_data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Response: {response_text}")

        return {
            "transcription": transcription,
            "response": response_text
        }
    
    except Exception as e:
        print(f"Exception in audio_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "transcription": f"Error: {str(e)}",
            "response": "An error occurred"
        }

@app.post("/chat")
async def text_chat(chat_message: ChatMessage):
    """Handle text-based chat with Daksh"""
    try:
        user_message = chat_message.message
        print(f"Received chat message: {user_message}")

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [
                        {"text": f"{RESUME_CONTEXT}\n\nUser question: {user_message}\n\nProvide a helpful response based on the resume information above. Remember to say 'I don't wish to answer that' if the question is not related to the resume."}
                    ]
                }]
            }
        )

        print(f"Chat API status: {response.status_code}")
        data = response.json()
        print(f"Chat response: {data}")
        
        if "candidates" not in data:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            return {"response": f"Error: {error_msg}"}
        
        response_text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Response text: {response_text}")

        return {"response": response_text}
    
    except Exception as e:
        print(f"Exception in text_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"response": f"Error: {str(e)}"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DakshAI API is running", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("Starting DakshAI backend server...")
    print("Server will run on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
