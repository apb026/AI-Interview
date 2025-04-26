# app/services/transcription_service.py
import os
import time
import threading
import queue
import tempfile
import wave
import numpy as np
from typing import List, Dict, Any, Callable, Optional
import openai
import whisper
import sounddevice as sd

class TranscriptionService:
    """Service for real-time speech-to-text transcription"""
    
    def __init__(self, model_name: str = "base", use_openai: bool = False, 
                openai_api_key: Optional[str] = None, buffer_duration: float = 5.0):
        """
        Initialize the transcription service
        
        Args:
            model_name: Whisper model name to use (tiny, base, small, medium, large)
            use_openai: Whether to use OpenAI's API instead of local Whisper
            openai_api_key: OpenAI API key (required if use_openai is True)
            buffer_duration: Duration in seconds for the audio buffer
        """
        self.use_openai = use_openai
        self.model_name = model_name
        self.buffer_duration = buffer_duration
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.transcription_thread = None
        self.callback = None
        self.sample_rate = 16000  # Hz
        
        # Set up the appropriate transcription engine
        if use_openai:
            if not openai_api_key and not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key is required when use_openai is True")
            openai.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        else:
            # Load local Whisper model
            self.model = whisper.load_model(model_name)
    
    def start_transcribing(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Start the transcription service
        
        Args:
            callback: Function to call with transcription results
        """
        if self.is_running:
            return
            
        self.callback = callback
        self.is_running = True
        
        # Start audio recording
        self.audio_thread = threading.Thread(target=self._record_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        # Start transcription processing
        self.transcription_thread = threading.Thread(target=self._process_audio)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def stop_transcribing(self):
        """Stop the transcription service"""
        self.is_running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        if self.transcription_thread and self.transcription_thread.is_alive():
            self.transcription_thread.join(timeout=1.0)
    
    def _record_audio(self):
        """Record audio from the microphone and add to the queue"""
        buffer_size = int(self.sample_rate * self.buffer_duration)
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if self.is_running:
                self.audio_queue.put(indata.copy())
        
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=self.sample_rate):
            while self.is_running:
                time.sleep(0.1)
    
    def _save_audio_to_file(self, audio_data: np.ndarray) -> str:
        """
        Save audio data to a temporary WAV file
        
        Args:
            audio_data: NumPy array of audio samples
            
        Returns:
            Path to the saved WAV file
        """
        fd, temp_filename = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        return temp_filename
    
    def _process_audio(self):
        """Process audio chunks from the queue and transcribe them"""
        buffer = []
        last_transcription_time = time.time()
        
        while self.is_running:
            try:
                # Get audio chunk from queue with a timeout
                audio_chunk = self.audio_queue.get(timeout=1.0)
                buffer.append(audio_chunk)
                
                current_time = time.time()
                buffer_duration = len(buffer) * self.buffer_duration
                
                # Process buffer when it reaches appropriate size or time threshold
                if buffer_duration >= 3.0 or (current_time - last_transcription_time) >= 5.0:
                    if buffer:
                        # Concatenate all chunks in the buffer
                        audio_data = np.concatenate(buffer)
                        
                        # Transcribe audio
                        transcription = self._transcribe_audio(audio_data)
                        
                        # If we got a valid transcription, call the callback
                        if transcription and transcription.get("text"):
                            if self.callback:
                                self.callback(transcription)
                        
                        # Clear buffer and update last transcription time
                        buffer = []
                        last_transcription_time = current_time
                
            except queue.Empty:
                pass
    
    def _transcribe_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: NumPy array of audio samples
            
        Returns:
            Transcription result with text and metadata
        """
        try:
            if self.use_openai:
                # Save audio to a temporary file
                temp_filename = self._save_audio_to_file(audio_data)
                
                # Transcribe using OpenAI API
                with open(temp_filename, "rb") as audio_file:
                    response = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file
                    )
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                return {
                    "text": response["text"],
                    "timestamp": time.time(),
                    "source": "openai"
                }
            else:
                # Transcribe using local Whisper model
                result = self.model.transcribe(audio_data, language="en", fp16=False)
                
                return {
                    "text": result["text"],
                    "timestamp": time.time(),
                    "segments": result.get("segments", []),
                    "source": "whisper-local"
                }
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return {"text": "", "error": str(e), "timestamp": time.time()}

    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcription result with text and metadata
        """
        try:
            if self.use_openai:
                with open(file_path, "rb") as audio_file:
                    response = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file
                    )
                
                return {
                    "text": response["text"],
                    "timestamp": time.time(),
                    "source": "openai"
                }
            else:
                # Transcribe using local Whisper model
                result = self.model.transcribe(file_path, language="en", fp16=False)
                
                return {
                    "text": result["text"],
                    "timestamp": time.time(),
                    "segments": result.get("segments", []),
                    "source": "whisper-local"
                }
                
        except Exception as e:
            print(f"File transcription error: {e}")
            return {"text": "", "error": str(e), "timestamp": time.time()}