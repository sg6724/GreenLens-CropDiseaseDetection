// GreenLens Application JavaScript

class GreenLensApp {
    constructor() {
        this.currentAudio = null;
        this.isAnalyzing = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        feather.replace();
    }

    setupEventListeners() {
        // Upload trigger
        document.getElementById('uploadTrigger').addEventListener('click', () => {
            document.getElementById('imageInput').click();
        });

        // File input change
        document.getElementById('imageInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeImage();
        });

        // Audio controls
        document.getElementById('playAudioBtn').addEventListener('click', () => {
            this.playAudio();
        });

        // Treatment action buttons
        document.getElementById('copyTreatmentBtn').addEventListener('click', () => {
            this.copyTreatmentPlan();
        });

        document.getElementById('printTreatmentBtn').addEventListener('click', () => {
            this.printTreatmentPlan();
        });

        // Location input enter key
        document.getElementById('locationInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeImage();
            }
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showError('Please select a valid image file.');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size must be less than 10MB.');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('previewImage').src = e.target.result;
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('imagePreview').classList.remove('hidden');
        };
        reader.readAsDataURL(file);

        // Store file for analysis
        this.selectedFile = file;
        this.enableAnalyzeButton();
    }

    enableAnalyzeButton() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('btn-disabled');
    }

    async analyzeImage() {
        if (!this.selectedFile) {
            this.showError('Please select an image first.');
            return;
        }

        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.showLoading();

        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('location', document.getElementById('locationInput').value || 'New York');

            const response = await axios.post('/api/detect-disease', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                timeout: 120000 // 120 seconds timeout
            });

            if (response.data.success) {
                this.displayResults(response.data);
            } else {
                throw new Error(response.data.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(error.response?.data?.detail || error.message || 'Analysis failed. Please try again.');
        } finally {
            this.isAnalyzing = false;
            this.hideLoading();
        }
    }

    displayResults(data) {
        // Hide error section
        document.getElementById('errorSection').classList.add('hidden');

        // Show results section
        document.getElementById('resultsSection').classList.remove('hidden');
        document.getElementById('resultsSection').classList.add('fade-in');

        // Display disease detection results
        document.getElementById('detectedDisease').textContent = 
            data.disease.replace(/_/g, ' ').replace(/\(/g, '').replace(/\)/g, '');

        // Display Grad-CAM visualization
        if (data.gradcam_image) {
            document.getElementById('gradcamImage').src = data.gradcam_image;
        }

        // Display weather information
        if (data.weather) {
            document.getElementById('weatherLocation').textContent = 
                `${data.weather.location}, ${data.weather.country}`;
            document.getElementById('weatherTemp').textContent = 
                `${data.weather.temperature}°C`;
            document.getElementById('weatherHumidity').textContent = 
                `${data.weather.humidity}%`;
            document.getElementById('weatherCondition').textContent = 
                data.weather.condition;
        }

        // Display risk assessment
        if (data.risk_assessment) {
            const riskBadge = document.getElementById('riskBadge');
            const riskLevel = document.getElementById('riskLevel');
            const riskAssessment = document.getElementById('riskAssessment');

            // Clear previous classes
            riskBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-3';
            
            // Add risk-specific styling
            const risk = data.risk_assessment.risk_level.toLowerCase();
            riskBadge.classList.add(`risk-${risk}`);
            
            riskLevel.textContent = data.risk_assessment.risk_level.toUpperCase();
            riskAssessment.textContent = data.risk_assessment.assessment;
        }

        // Display AI-generated remedy with interactive formatting
        if (data.remedy) {
            this.displayTreatmentPlan(data.remedy, data.confidence);
        }

        // Display image analysis
        if (data.image_analysis) {
            document.getElementById('imageAnalysisContent').textContent = data.image_analysis;
        }

        // Setup audio
        if (data.audio) {
            this.setupAudio(data.audio);
        }

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    setupAudio(audioBase64) {
        const audioPlayer = document.getElementById('audioPlayer');
        const audioBlob = this.base64ToBlob(audioBase64, 'audio/mpeg');
        const audioUrl = URL.createObjectURL(audioBlob);
        
        audioPlayer.src = audioUrl;
        audioPlayer.classList.remove('hidden');
        
        // Store for play button
        this.currentAudio = audioPlayer;
    }

    playAudio() {
        if (this.currentAudio) {
            const playBtn = document.getElementById('playAudioBtn');
            const icon = playBtn ? playBtn.querySelector('i') : null;
            
            if (this.currentAudio.paused) {
                this.currentAudio.play();
                if (icon) {
                    icon.setAttribute('data-feather', 'pause');
                    const textSpan = playBtn.querySelector('span');
                    if (textSpan) textSpan.textContent = 'Pause Audio';
                }
            } else {
                this.currentAudio.pause();
                if (icon) {
                    icon.setAttribute('data-feather', 'play');
                    const textSpan = playBtn.querySelector('span');
                    if (textSpan) textSpan.textContent = 'Play Audio Guide';
                }
            }
            
            feather.replace();
        }
    }

    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimeType });
    }

    showLoading() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeText = document.getElementById('analyzeText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('btn-disabled');
        analyzeText.textContent = 'Analyzing...';
        loadingSpinner.classList.remove('hidden');
    }

    hideLoading() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeText = document.getElementById('analyzeText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('btn-disabled');
        analyzeText.textContent = 'Analyze Crop';
        loadingSpinner.classList.add('hidden');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
        
        // Hide results section
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Scroll to error
        errorSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    displayTreatmentPlan(remedyText, confidence) {
        // Parse and format the AI remedy text into structured sections
        const sections = this.parseRemedyText(remedyText);
        
        // Display summary
        if (sections.summary) {
            document.getElementById('summaryText').innerHTML = this.formatTextWithBold(sections.summary);
        }
        
        // Display treatment steps
        this.displayTreatmentSteps(sections.steps);
        
        // Display prevention tips
        this.displayPreventionTips(sections.prevention);
        
        // Display timeline
        if (sections.timeline) {
            document.getElementById('timelineText').innerHTML = this.formatTextWithBold(sections.timeline);
        }
        
        // Show emergency action if needed
        if (sections.emergency) {
            document.getElementById('emergencyAction').classList.remove('hidden');
            document.getElementById('emergencyText').textContent = sections.emergency;
        }
    }

    parseRemedyText(text) {
        const sections = {
            summary: '',
            steps: [],
            prevention: [],
            timeline: '',
            emergency: ''
        };
        
        const lines = text.split('\n').filter(line => line.trim());
        let currentSection = '';
        
        for (const line of lines) {
            const cleanLine = line.trim();
            
            // Check for section headers
            if (cleanLine.toUpperCase().includes('SUMMARY:')) {
                currentSection = 'summary';
                continue;
            } else if (cleanLine.toUpperCase().includes('TREATMENT') && cleanLine.includes(':')) {
                currentSection = 'steps';
                continue;
            } else if (cleanLine.toUpperCase().includes('PREVENTION:')) {
                currentSection = 'prevention';
                continue;
            } else if (cleanLine.toUpperCase().includes('TIMELINE:')) {
                currentSection = 'timeline';
                continue;
            }
            
            // Process content based on current section
            if (currentSection === 'summary' && cleanLine.length > 0) {
                sections.summary = cleanLine;
            } else if (currentSection === 'steps') {
                if (cleanLine.match(/^\d+\./)) {
                    const stepText = cleanLine.replace(/^\d+\.\s*/, '');
                    sections.steps.push(stepText);
                }
            } else if (currentSection === 'prevention') {
                if (cleanLine.startsWith('-') || cleanLine.startsWith('•')) {
                    const preventionText = cleanLine.replace(/^[-•]\s*/, '');
                    sections.prevention.push(preventionText);
                }
            } else if (currentSection === 'timeline' && cleanLine.length > 0) {
                sections.timeline += cleanLine + ' ';
            }
        }
        
        // Fallback parsing if structured format not found
        if (sections.steps.length === 0) {
            const sentences = text.split('.').filter(s => s.trim().length > 10);
            sections.summary = sentences[0] || 'Disease detected - treatment recommendations follow.';
            sections.steps = sentences.slice(1, 4).map(s => s.trim()).filter(s => s);
            sections.prevention = ['Monitor plant health regularly', 'Maintain proper irrigation', 'Apply preventive treatments'];
            sections.timeline = 'Monitor progress over 1-2 weeks and consult an expert if symptoms persist.';
        }
        
        return sections;
    }

    displayTreatmentSteps(steps) {
        const container = document.getElementById('stepsContainer');
        container.innerHTML = '';
        
        steps.forEach((step, index) => {
            if (step.trim()) {
                const stepElement = document.createElement('div');
                stepElement.className = 'flex items-start bg-white/60 rounded-lg p-4 border border-green-200';
                stepElement.innerHTML = `
                    <div class="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-4 flex-shrink-0">
                        ${index + 1}
                    </div>
                    <div class="flex-1">
                        <p class="text-gray-800 leading-relaxed">${this.formatTextWithBold(step)}</p>
                    </div>
                `;
                container.appendChild(stepElement);
            }
        });
    }

    displayPreventionTips(tips) {
        const container = document.getElementById('preventionContainer');
        container.innerHTML = '';
        
        tips.forEach(tip => {
            if (tip.trim()) {
                const tipElement = document.createElement('div');
                tipElement.className = 'flex items-center text-gray-700';
                tipElement.innerHTML = `
                    <i data-feather="check-circle" class="text-blue-500 mr-3 flex-shrink-0" size="16"></i>
                    <span>${this.formatTextWithBold(tip)}</span>
                `;
                container.appendChild(tipElement);
            }
        });
        
        // Re-render feather icons
        feather.replace();
    }

    formatTextWithBold(text) {
        // Convert **text** to <strong>text</strong>
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    copyTreatmentPlan() {
        const treatmentText = this.extractTreatmentText();
        navigator.clipboard.writeText(treatmentText).then(() => {
            this.showToast('Treatment plan copied to clipboard!', 'success');
        }).catch(() => {
            this.showToast('Failed to copy treatment plan', 'error');
        });
    }

    printTreatmentPlan() {
        const treatmentContent = document.getElementById('treatmentPlan').cloneNode(true);
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>GreenLens Treatment Plan</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .space-y-6 > * + * { margin-top: 1.5rem; }
                        .space-y-4 > * + * { margin-top: 1rem; }
                        .space-y-3 > * + * { margin-top: 0.75rem; }
                        .space-y-2 > * + * { margin-top: 0.5rem; }
                        .bg-white\\/70, .bg-blue-50, .bg-amber-50, .bg-red-50 { 
                            background-color: #f9fafb; 
                            padding: 1rem; 
                            border-radius: 8px; 
                            border-left: 4px solid #10b981; 
                            margin: 1rem 0; 
                        }
                    </style>
                </head>
                <body>
                    <h1>GreenLens AI Treatment Plan</h1>
                    ${treatmentContent.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    extractTreatmentText() {
        const summary = document.getElementById('summaryText').textContent;
        const steps = Array.from(document.querySelectorAll('#stepsContainer > div')).map((step, index) => 
            `${index + 1}. ${step.querySelector('p').textContent}`
        ).join('\n');
        const timeline = document.getElementById('timelineText').textContent;
        
        return `GREENLENS AI TREATMENT PLAN\n\n` +
               `SUMMARY:\n${summary}\n\n` +
               `TREATMENT STEPS:\n${steps}\n\n` +
               `EXPECTED TIMELINE:\n${timeline}`;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GreenLensApp();
});

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
