

from gtts import gTTS
import base64
import io
import os
from googletrans import Translator # Import the Translator

class TTSService:
    def __init__(self):
        # Define a mapping for user-friendly names to gTTS language codes
        self.language_map = {
            "english": "en",
            "hindi": "hi",
            "marathi": "mr",
            "gujarati": "gu"
            # Add more languages if needed. Ensure these keys match what you'll get from frontend.
        }
        self.temp_dir = "temp_audio" # Ensure this directory exists or is created
        os.makedirs(self.temp_dir, exist_ok=True) 

        self.translator = Translator() # Initialize the translator

    def text_to_speech(self, text, language='en'):
        """Convert text to speech and return base64 encoded audio"""
        try:
            # Get the gTTS language code
            tts_language_code = self.language_map.get(language.lower(), 'en')

            # Create TTS object
            tts = gTTS(text=text, lang=tts_language_code, slow=False)
            
            # Use in-memory buffer for efficiency
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
            return audio_base64

        except Exception as e:
            print(f"Error converting text to speech for language '{language}': {e}")
            return None

    def create_quick_summary_audio(self, disease, confidence, risk_level, language_code="en"):
        # The base English text for the summary
        english_text = f"Detected {disease} with {confidence*100:.1f}% confidence. The risk level is {risk_level}."
        
        final_text = english_text
        # Translate if the target language is not English
        if language_code.lower() != 'english' and language_code.lower() in self.language_map:
            try:
                # Use the gTTS language code for translation destination
                dest_lang = self.language_map[language_code.lower()]
                translated_obj = self.translator.translate(english_text, dest=dest_lang)
                if translated_obj and translated_obj.text:
                    final_text = translated_obj.text
                else:
                    print(f"Warning: Translation failed for '{english_text}' to '{dest_lang}'. Using English text.")
            except Exception as e:
                print(f"Error during translation: {e}. Using English text.")
        
        # Pass the (potentially translated) text and the original language_code to text_to_speech
        return self.text_to_speech(final_text, language=language_code)


    def create_comprehensive_audio(self, disease, remedy_text, risk_assessment, language_code="en"):
        # The base English text for the comprehensive summary
        english_comprehensive_text = (
            f"For the detected disease: {disease}. "
            f"Risk assessment indicates: {risk_assessment}. "
            f"Recommended remedy: {remedy_text}."
        )

        final_text = english_comprehensive_text
        # Translate if the target language is not English
        if language_code.lower() != 'english' and language_code.lower() in self.language_map:
            try:
                dest_lang = self.language_map[language_code.lower()]
                translated_obj = self.translator.translate(english_comprehensive_text, dest=dest_lang)
                if translated_obj and translated_obj.text:
                    final_text = translated_obj.text
                else:
                    print(f"Warning: Translation failed for comprehensive text to '{dest_lang}'. Using English text.")
            except Exception as e:
                print(f"Error during translation of comprehensive text: {e}. Using English text.")
        
        return self.text_to_speech(final_text, language=language_code)