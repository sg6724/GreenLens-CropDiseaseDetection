
# 🌿 GreenLens: AI-Powered Crop Disease Detection & Remedy System

GreenLens is a full-stack, AI-driven plant disease detection platform designed to assist farmers and agronomists in identifying crop issues, understanding affected areas, and receiving actionable remedies based on real-time weather conditions and AI reasoning. Combining computer vision, LLMs, and voice interaction, GreenLens delivers an accessible and intelligent solution for sustainable agriculture.

---

## 🚀 Features

* ✅ **Crop Disease Detection** using fine-tuned EfficientNet-B0
* 🔴 **Grad-CAM Heatmap** highlighting infected regions on the leaf
* 🤖 **Google Gemini LLM** (via LangChain) for disease explanation and remedies
* ☁️ **Weather Integration** using WeatherAPI to suggest climate suitability
* 🔊 **Text-to-Speech** using gTTS for auditory feedback in regional language
* 🌐 **Modern UI** built with React.js and TailwindCSS
* ⚡ **FastAPI Backend** for efficient model inference and logic orchestration

---

## 🧠 Tech Stack

**Frontend**

* React.js
* TailwindCSS
* Axios
* Audio player for TTS

**Backend**

* FastAPI
* PyTorch (EfficientNet-B0 + Grad-CAM)
* Gemini LLM (free tier)
* gTTS (Google Text-to-Speech)
* WeatherAPI
* Pillow, NumPy, Requests

---

## 🖼 Project Workflow

1. **User Uploads Image:**
   A crop leaf image is uploaded through the web interface.

2. **Backend Processing:**

   * The image is sent to the backend.
   * The trained EfficientNet-B0 model predicts the disease class.
   * Grad-CAM highlights the infected areas as red spots on the image.
   * The model returns both the class name and the heatmap.

3. **LLM Interpretation:**

   * LangChain sends the disease name and Grad-CAM explanation to Gemini.
   * Gemini generates a textual output explaining the disease and suggesting remedies.

4. **Weather-Based Advice:**

   * Current weather data is fetched using WeatherAPI.
   * The climate is cross-checked with disease-specific weather rules.
   * A dynamic message is added to suggest favorable or risky conditions.

5. **Text-to-Speech:**

   * The entire AI output (disease + remedy + weather advice) is converted to speech using gTTS.
   * The audio file is sent to the frontend for playback.

6. **User Interface:**

   * The frontend displays the predicted disease, Grad-CAM image, remedy text, weather status, and plays the voice message.



## ⚙️ Setup Instructions

### 🔧 Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Environment Variables (`.env`):**

```
WEATHER_API_KEY=your_weatherapi_key
GOOGLE_API_KEY=your_gemini_api_key
```

**Run FastAPI server:**

```bash
uvicorn main:app --reload
```


## 📌 Dataset Used

**Crop Pest and Disease Detection**
📦 [Kaggle Dataset Link](https://www.kaggle.com/datasets/nirmalsankalana/crop-pest-and-disease-detection)


