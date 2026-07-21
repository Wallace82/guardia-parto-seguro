import os
import sys

# Simula o ambiente FastAPI para podermos instanciar o Processor
sys.path.append('/app')
import asyncio
from app.services.processor import VideoProcessor

def run():
    processor = VideoProcessor()
    
    videos = [
        {"session_id": 19, "media_id": 160, "blob_url": "file:////shared_media/19_video_video_ira_alto.mp4"}
    ]
    
    for video in videos:
        sess = video["session_id"]
        media = video["media_id"]
        url = video["blob_url"]
        print(f"Processing {media}...")
        processor.process_video(sess, media, url)
        print(f"Finished {media}")

if __name__ == "__main__":
    run()
