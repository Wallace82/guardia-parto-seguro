"""
GuardIA — Audio Domain Service (Azure Integration)
"""
import os
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

app = FastAPI(title="GuardIA — Audio Service", version="1.0.0")

class AudioAnalyzeRequest(BaseModel):
    file_path: str

class AudioAnalyzeResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float

def analyze_audio_with_azure(file_path: str):
    speech_key = os.environ.get("AZURE_SPEECH_KEY")
    speech_region = os.environ.get("AZURE_SPEECH_REGION")
    language_key = os.environ.get("AZURE_LANGUAGE_KEY")
    language_endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")

    if not all([speech_key, speech_region, language_key, language_endpoint]):
        raise HTTPException(status_code=500, detail="Azure credentials missing in .env")

    # 1. Azure Speech (STT)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = "pt-BR"
    
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        text = speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        raise HTTPException(status_code=400, detail="No speech could be recognized")
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        raise HTTPException(status_code=500, detail=f"Speech Recognition canceled: {cancellation_details.reason}")
        
    # 2. Azure AI Language (Sentiment)
    credential = AzureKeyCredential(language_key)
    text_analytics_client = TextAnalyticsClient(endpoint=language_endpoint, credential=credential)
    
    documents = [text]
    response = text_analytics_client.analyze_sentiment(documents=documents, language="pt")[0]
    
    if response.is_error:
        raise HTTPException(status_code=500, detail=f"Text Analytics Error: {response.error.message}")
        
    sentiment = response.sentiment
    confidence = getattr(response.confidence_scores, sentiment, 0.0)

    return {"text": text, "sentiment": sentiment, "confidence": confidence}

@app.get("/api/v1/audio/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "audio"}

@app.post("/api/v1/audio/analyze", status_code=status.HTTP_200_OK, response_model=AudioAnalyzeResponse)
async def analyze(data: AudioAnalyzeRequest):
    result = analyze_audio_with_azure(data.file_path)
    return AudioAnalyzeResponse(
        text=result["text"],
        sentiment=result["sentiment"],
        confidence=result["confidence"]
    )
