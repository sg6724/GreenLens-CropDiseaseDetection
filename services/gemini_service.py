import os
import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def generate_disease_remedy(self, disease_name, weather_info=None):
        """Generate remedy and care instructions for detected disease"""
        try:
            # Clean disease name for better prompt
            clean_disease = disease_name.replace('_', ' ').replace('(', '').replace(')', '')
            
            # Create comprehensive prompt with disease-specific guidance
            prompt = f"""
            You are an expert agricultural pathologist. A farmer has detected {clean_disease} in their crop.
            
            Important: Be specific and accurate. Only provide treatments that are scientifically proven for this exact disease. Do not provide generic advice.
            
            Please provide a comprehensive treatment plan using this EXACT format:
            
            SUMMARY:
            [Brief description of the specific disease, its symptoms, and immediate impact on the crop]
            
            TREATMENT STEPS:
            1. [Immediate action required - be specific about timing]
            2. [Chemical or biological treatment - include product types and application rates]
            3. [Follow-up treatment and monitoring - specify intervals]
            
            PREVENTION:
            - [Cultural practices specific to preventing this disease]
            - [Resistant varieties or crop rotation recommendations]
            - [Environmental management specific to this pathogen]
            
            TIMELINE:
            [Specific timeline: when to apply treatments, when to expect results, monitoring schedule]
            
            """
            
            if weather_info:
                prompt += f"""
                Current weather conditions:
                - Temperature: {weather_info.get('temperature', 'N/A')}°C
                - Humidity: {weather_info.get('humidity', 'N/A')}%
                - Condition: {weather_info.get('condition', 'N/A')}
                - Wind: {weather_info.get('wind_speed', 'N/A')} km/h
                
                Please include how current weather conditions may affect the disease and treatment.
                """
            
            prompt += """
            
            Use simple language that farmers can easily understand. Be specific and practical.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text or "Unable to generate remedy at this time."
            
        except Exception as e:
            print(f"Error generating remedy: {e}")
            return f"Error generating remedy: {str(e)}"
    
    def analyze_crop_image(self, image_path, disease_prediction):
        """Analyze crop image with disease context"""
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            prompt = f"""
            Analyze this crop image that has been diagnosed with {disease_prediction}.
            
            Please provide:
            1. Confirmation of visible symptoms
            2. Severity assessment (mild, moderate, severe)
            3. Affected areas description
            4. Urgent actions needed
            5. Prognosis for the crop
            
            Be specific and practical in your assessment.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",
                    ),
                    prompt
                ],
            )
            
            return response.text if response.text else "Unable to analyze image."
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"
    
    def get_seasonal_advice(self, disease_name, location):
        """Get seasonal advice for disease management"""
        try:
            prompt = f"""
            Provide seasonal advice for managing {disease_name} in {location}.
            
            Include:
            1. Best times for treatment
            2. Seasonal prevention strategies
            3. Climate-specific recommendations
            4. Crop rotation suggestions
            5. Long-term management plan
            
            Make it location and season specific.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text or "Unable to generate seasonal advice."
            
        except Exception as e:
            print(f"Error generating seasonal advice: {e}")
            return f"Error generating seasonal advice: {str(e)}"
