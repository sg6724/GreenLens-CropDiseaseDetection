import os
import json
import asyncio
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import local modules
from models.disease_classifier import DiseaseClassifier
from models.gradcam import GradCAM
from services.gemini_service import GeminiService
from services.weather_service import WeatherService
from services.tts_service import TTSService
from utils.image_utils import save_uploaded_image, validate_image, cleanup_temp_files
from config import UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR, HOST, PORT, DEBUG

# Initialize FastAPI app
app = FastAPI(
    title="GreenLens - AI Crop Disease Detection", 
    version="1.0.0",
    description="AI-powered crop disease detection system"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
disease_classifier = None
gradcam = None
gemini_service = GeminiService()
weather_service = WeatherService()
tts_service = TTSService()

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global disease_classifier, gradcam
    
    print("🌱 Starting GreenLens Local Server...")
    
    # Create necessary directories
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    STATIC_DIR.mkdir(exist_ok=True)
    
    # Create outputs directory in static for serving
    static_outputs = STATIC_DIR / "outputs"
    static_outputs.mkdir(exist_ok=True)
    
    # Initialize disease classifier
    print("📊 Loading disease classification model...")
    try:
        disease_classifier = DiseaseClassifier()
        print("✅ Disease classifier loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading disease classifier: {e}")
        raise
    
    # Initialize Grad-CAM
    print("🔍 Initializing Grad-CAM...")
    try:
        gradcam = GradCAM(disease_classifier.model)
        print("✅ Grad-CAM initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing Grad-CAM: {e}")
        raise
    
    print("🚀 GreenLens Local Server is ready!")
    print(f"🌐 Access the application at: http://{HOST}:{PORT}")

# Mount static files - Order matters!
@app.get("/")
async def root():
    """Serve the main application"""
    return FileResponse(STATIC_DIR / "index.html")

# API Routes first, then static files mount
@app.post("/api/detect-disease")
async def detect_disease(
    file: UploadFile = File(...),
    location: str = Form(default="New York")
):
    """Main endpoint for disease detection"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        file_content = await file.read()
        image_path = save_uploaded_image(file_content, str(UPLOAD_DIR))

        # Validate image
        if not validate_image(image_path):
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Check if models are loaded
        if disease_classifier is None:
            raise HTTPException(status_code=500, detail="Disease classifier not loaded")
        if gradcam is None:
            raise HTTPException(status_code=500, detail="Grad-CAM not initialized")

        # Predict disease
        print(f"🔍 Predicting disease for image: {image_path}")
        prediction = disease_classifier.predict(image_path)
        print(f"📊 Prediction: {prediction}")

        # Generate Grad-CAM visualization
        print("🎨 Generating Grad-CAM visualization...")
        gradcam_path = gradcam.generate_gradcam_image(
            image_path,
            str(STATIC_DIR / "outputs")
        )

        gradcam_url = None
        if gradcam_path:
            gradcam_url = f"/static/outputs/{Path(gradcam_path).name}"
            print(f"✅ Grad-CAM image saved: {gradcam_path}")
        else:
            print("❌ Failed to generate Grad-CAM image")

        # Get weather data
        print(f"🌤️ Getting weather data for: {location}")
        weather_data = weather_service.get_weather_data(location)

        # Assess disease risk based on weather
        print("⚠️ Assessing disease risk...")
        risk_assessment = weather_service.assess_disease_risk(
            prediction['disease'], weather_data
        )

        # Generate AI remedy
        print("🤖 Generating AI remedy...")
        remedy_text = gemini_service.generate_disease_remedy(
            prediction['disease'], weather_data
        )

        # Generate image analysis
        print("📸 Generating image analysis...")
        clean_disease = prediction['disease'].replace('___', ' - ').replace('_', ' ')
        image_analysis = f"Detected {clean_disease} with {prediction['confidence']*100:.1f}% confidence. Please review the highlighted areas in the visualization above for signs of disease symptoms."

        # Generate TTS audio
        print("🔊 Generating TTS audio...")
        audio_base64 = tts_service.create_comprehensive_audio(
            prediction['disease'], remedy_text, risk_assessment
        )

        # Prepare response
        response = {
            'success': True,
            'disease': prediction['disease'],
            'confidence': prediction['confidence'],
            'gradcam_image': gradcam_url,
            'weather': weather_data,
            'risk_assessment': risk_assessment,
            'remedy': remedy_text,
            'image_analysis': image_analysis,
            'audio': audio_base64,
            'location': location
        }

        print("✅ Analysis complete, sending response")

        # Cleanup temporary files
        cleanup_temp_files(str(UPLOAD_DIR), max_age_hours=1)

        return JSONResponse(content=response)

    except Exception as e:
        print(f"❌ Error in disease detection: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        'status': 'healthy',
        'model_loaded': disease_classifier is not None,
        'gradcam_ready': gradcam is not None
    })

# Mount static files after API routes
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def main():
    """Run the application"""
    print("🌱 GreenLens - AI Crop Disease Detection")
    print("=" * 50)
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()
