import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0
from PIL import Image
import numpy as np
from pathlib import Path
from config import MODEL_PATH, MODEL_INPUT_SIZE, NUM_CLASSES, DISEASE_CLASSES

class DiseaseClassifier:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
        # Enhanced preprocessing for better accuracy
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(MODEL_INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.load_model()

    def load_model(self):
        """Load the pre-trained EfficientNet model"""
        try:
            # Check if model file exists
            model_path = Path(MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

            print(f"🔍 Loading model from: {model_path}")
            
            # Create EfficientNet-B0 model
            self.model = efficientnet_b0(weights=None)  # No pretrained weights
            
            # Modify classifier for our number of classes
            num_features = self.model.classifier[1].in_features
            self.model.classifier[1] = nn.Linear(num_features, NUM_CLASSES)

            # Load the trained weights
            try:
                # Try loading with map_location for cross-platform compatibility
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
                
                # Handle different checkpoint formats
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        state_dict = checkpoint['model_state_dict']
                        print("📊 Loading from model_state_dict")
                    elif 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                        print("📊 Loading from state_dict")
                    else:
                        # Try to use the dict directly as state_dict
                        state_dict = checkpoint
                        print("📊 Loading checkpoint as state_dict")
                else:
                    # If it's the model directly (older torch.save format)
                    if hasattr(checkpoint, 'state_dict'):
                        state_dict = checkpoint.state_dict()
                        print("📊 Extracting state_dict from model")
                    else:
                        raise ValueError("Unknown checkpoint format")

                # Load state dict
                missing_keys, unexpected_keys = self.model.load_state_dict(state_dict, strict=False)
                
                if missing_keys:
                    print(f"⚠️  Missing keys: {missing_keys}")
                if unexpected_keys:
                    print(f"⚠️  Unexpected keys: {unexpected_keys}")

                print(f"✅ Model loaded successfully from {model_path}")
                
            except Exception as e:
                print(f"❌ Error loading model weights: {e}")
                print("⚠️  Using randomly initialized model - predictions may be inaccurate")

            # Move model to device and set to evaluation mode
            self.model.to(self.device)
            self.model.eval()
            
            print(f"🎯 Model initialized on {self.device}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    def preprocess_image(self, image_path):
        """Preprocess image for model inference"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0)
            return image_tensor.to(self.device), image
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            raise

    def predict(self, image_path):
        """Predict disease class from image"""
        try:
            image_tensor, original_image = self.preprocess_image(image_path)
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted_class = torch.max(probabilities, 1)

                # Get top predictions for better validation
                top_probs, top_indices = torch.topk(probabilities, min(3, len(DISEASE_CLASSES)), dim=1)
                
                predicted_idx = top_indices[0][0].item()
                confidence_score = top_probs[0][0].item()

                # Ensure predicted class is within valid range
                if predicted_idx >= len(DISEASE_CLASSES):
                    predicted_idx = 0  # Default to first class if out of range

                predicted_disease = DISEASE_CLASSES[predicted_idx]

                # Add confidence validation to reduce hallucination
                if confidence_score < 0.1:  # Very low confidence threshold
                    # Check if any healthy class has higher probability
                    healthy_indices = [i for i, name in enumerate(DISEASE_CLASSES) if 'healthy' in name.lower()]
                    if healthy_indices:
                        healthy_probs = [probabilities[0][i].item() for i in healthy_indices]
                        max_healthy_prob = max(healthy_probs)
                        if max_healthy_prob > confidence_score * 0.8:  # If healthy is competitive
                            best_healthy_idx = healthy_indices[healthy_probs.index(max_healthy_prob)]
                            predicted_disease = DISEASE_CLASSES[best_healthy_idx]
                            predicted_idx = best_healthy_idx
                            confidence_score = max_healthy_prob

                # Clean up disease name for display
                display_name = predicted_disease.replace('___', ' - ').replace('_', ' ')

                return {
                    'disease': display_name,
                    'confidence': confidence_score,
                    'class_index': predicted_idx,
                    'all_probabilities': probabilities.cpu().numpy().tolist()[0]
                }

        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            raise

    def get_feature_maps(self, image_path):
        """Get feature maps for Grad-CAM"""
        try:
            image_tensor, _ = self.preprocess_image(image_path)
            
            # Hook to capture feature maps
            feature_maps = []
            def hook_fn(module, input, output):
                feature_maps.append(output)

            # Register hook on the last convolutional layer
            last_conv_layer = None
            for name, module in self.model.named_modules():
                if isinstance(module, nn.Conv2d):
                    last_conv_layer = module

            if last_conv_layer is None:
                raise ValueError("No convolutional layer found in model")

            handle = last_conv_layer.register_forward_hook(hook_fn)

            # Forward pass
            with torch.no_grad():
                outputs = self.model(image_tensor)
                predicted_class = torch.argmax(outputs, dim=1)

            # Remove hook
            handle.remove()

            if not feature_maps:
                raise ValueError("No feature maps captured")

            return feature_maps[0], predicted_class, image_tensor

        except Exception as e:
            print(f"❌ Error getting feature maps: {e}")
            raise
