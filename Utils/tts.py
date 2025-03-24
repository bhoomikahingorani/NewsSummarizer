import os
import torch
import logging
from googletrans import Translator
import tempfile
import scipy.io.wavfile as wavfile
import numpy as np
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToSpeech:
    """Class to convert text to speech in Hindi."""
    
    def __init__(self):
        """Initialize TTS engine."""
        self.translator = Translator()
        self.model = None
        self.processor = None
        self.temp_dir = tempfile.mkdtemp()
        
        # Load TTS model
        try:
            from transformers import AutoProcessor, AutoModelForTextToSpeech
            
            # Load Hindi TTS model from HuggingFace
            model_name = "coqui/xtts-v2" # Model that supports Hindi
            
            logger.info(f"Loading TTS model: {model_name}")
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.model = AutoModelForTextToSpeech.from_pretrained(model_name)
            
            logger.info("TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading TTS model: {e}")
            logger.info("Will use dummy TTS implementation")
    
    def translate_to_hindi(self, text: str) -> str:
        """
        Translate text to Hindi.
        
        Args:
            text: English text to translate
            
        Returns:
            Hindi translation
        """
        try:
            result = self.translator.translate(text, src='en', dest='hi')
            return result.text
        except Exception as e:
            logger.error(f"Error translating to Hindi: {e}")
            return text  # Return original text on error
    
    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Convert text to speech in Hindi.
        
        Args:
            text: Text to convert
            output_file: Optional output file path
            
        Returns:
            Path to the audio file
        """
        # Translate text to Hindi
        hindi_text = self.translate_to_hindi(text)
        
        if not output_file:
            output_file = os.path.join(self.temp_dir, "output.wav")
        
        try:
            if self.model and self.processor:
                # Generate speech using the model
                inputs = self.processor(
                    text=hindi_text,
                    return_tensors="pt"
                )
                
                # Generate audio
                speech = self.model.generate_speech(
                    inputs["input_ids"],
                    inputs["attention_mask"],
                    vocoder=None
                )
                
                # Convert tensor to numpy array
                audio_data = speech.numpy()
                
                # Save audio file
                sample_rate = 24000  # Default sample rate for most TTS models
                wavfile.write(output_file, sample_rate, audio_data)
                
            else:
                # Create a dummy audio file
                logger.warning("Using dummy TTS implementation")
                self._create_dummy_audio(output_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error in text to speech conversion: {e}")
            self._create_dummy_audio(output_file)
            return output_file
    
    def _create_dummy_audio(self, output_file: str):
        """
        Create a dummy audio file when TTS fails.
        
        Args:
            output_file: Path to save the dummy audio
        """
        # Generate a simple sine wave
        sample_rate = 24000
        duration = 3  # seconds
        frequency = 440  # Hz (A4 note)
        
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        wavfile.write(output_file, sample_rate, audio_data)
