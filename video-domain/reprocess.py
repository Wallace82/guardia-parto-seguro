import os
import sys

# Simula o ambiente FastAPI para podermos instanciar o Processor
sys.path.append('/app')
import asyncio
from app.services.processor import VideoProcessor

def run():
    processor = VideoProcessor()
    
    videos = [
        ("21", "147", "file:////shared_media/21_video_cena_1.mp4"),
        ("21", "149", "file:////shared_media/21_video_cena_2.mp4"),
        ("21", "151", "file:////shared_media/21_video_cena_3.mp4"),
    ]
    
    for sess, media, url in videos:
        print(f"Processing {media}...")
        processor.process_video(sess, media, url)
        print(f"Finished {media}")

if __name__ == "__main__":
    run()
