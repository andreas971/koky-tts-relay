import os
from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel
import edge_tts

app = FastAPI()

# اختيار توكن أمان اختياري مطابق لـ KOKY_EDGE_TTS_TOKEN
RELAY_TOKEN = os.getenv("RELAY_TOKEN", "")

class TTSRequest(BaseModel):
    text: str
    voice: str = "ar-EG-SalmaNeural" # الصوت النسائي الافتراضي بالعربية

@app.post("/api/koky-tts")
async def text_to_speech(req: TTSRequest, authorization: str = Header(None)):
    # التحقق من التوكن إن وجد
    if RELAY_TOKEN:
        if not authorization or authorization != f"Bearer {RELAY_TOKEN}":
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        communicate = edge_tts.Communicate(req.text, req.voice)
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
                
        return Response(content=bytes(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
