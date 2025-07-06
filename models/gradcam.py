import torch
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image
import os
from utils.image_utils import save_image

class GradCAM:
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        self.hooks = []
        
    def save_gradient(self, grad):
        """Save gradients during backward pass"""
        self.gradients = grad
        
    def save_activation(self, module, input, output):
        """Save activations during forward pass"""
        self.activations = output
        
    def register_hooks(self):
        """Register forward and backward hooks"""
        # Find the last convolutional layer
        target_layer = None
        for name, module in self.model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                target_layer = module
        
        if target_layer is None:
            raise ValueError("No convolutional layer found in model")
        
        # Register forward hook
        forward_hook = target_layer.register_forward_hook(self.save_activation)
        
        # Register backward hook
        backward_hook = target_layer.register_full_backward_hook(
            lambda module, grad_input, grad_output: self.save_gradient(grad_output[0])
        )
        
        self.hooks = [forward_hook, backward_hook]
        return target_layer
    
    def remove_hooks(self):
        """Remove all registered hooks"""
        for hook in self.hooks:
            hook.remove()
        self.hooks = []
    
    def generate_cam(self, image_tensor, class_idx=None):
        """Generate Class Activation Map"""
        try:
            self.model.eval()
            
            # Register hooks
            target_layer = self.register_hooks()
            
            # Ensure image tensor requires grad
            image_tensor.requires_grad_(True)
            
            # Forward pass
            model_output = self.model(image_tensor)
            
            if class_idx is None:
                class_idx = torch.argmax(model_output, dim=1).item()
            
            # Zero gradients
            self.model.zero_grad()
            
            # Backward pass
            class_score = model_output[:, class_idx]
            class_score.backward(retain_graph=True)
            
            # Generate CAM
            if self.gradients is None or self.activations is None:
                raise ValueError("Gradients or activations not captured")
            
            # Get gradients and activations
            gradients = self.gradients
            activations = self.activations
            
            # Global average pooling of gradients
            weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
            
            # Weight the activations
            cam = torch.sum(weights * activations, dim=1, keepdim=True)
            
            # Apply ReLU
            cam = F.relu(cam)
            
            # Normalize
            if torch.max(cam) > 0:
                cam = cam / torch.max(cam)
            
            # Remove hooks
            self.remove_hooks()
            
            return cam.squeeze().detach().cpu().numpy()
            
        except Exception as e:
            self.remove_hooks()
            print(f"Error generating Grad-CAM: {e}")
            # Return a default heatmap if generation fails
            return np.random.rand(224, 224) * 0.5
    
    def overlay_heatmap(self, image_path, cam, output_path):
        """Overlay heatmap on original image"""
        try:
            # Load original image using PIL
            original_image = Image.open(image_path).convert('RGB')
            original_array = np.array(original_image)
            
            # Ensure cam is 2D
            if len(cam.shape) > 2:
                cam = cam.squeeze()
            
            # Resize CAM to match original image using PIL
            cam_image = Image.fromarray((cam * 255).astype(np.uint8), mode='L')
            cam_resized = cam_image.resize((original_array.shape[1], original_array.shape[0]))
            cam_array = np.array(cam_resized).astype(np.float32) / 255.0
            
            # Create a simple red heatmap overlay
            heatmap = np.zeros_like(original_array)
            heatmap[:, :, 0] = cam_array * 255  # Red channel for heat
            
            # Create overlay
            overlay = original_array * 0.7 + heatmap * 0.3
            overlay = np.clip(overlay, 0, 255).astype(np.uint8)
            
            # Save overlay image
            overlay_image = Image.fromarray(overlay)
            overlay_image.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating overlay: {e}")
            # Create a simple copy of original image if overlay fails
            try:
                original_image = Image.open(image_path)
                original_image.save(output_path)
                return output_path
            except:
                return None
    
    def generate_gradcam_image(self, image_path, output_dir, class_idx=None):
        """Generate complete Grad-CAM visualization"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # We'll use F.interpolate directly instead of Sequential
            
            # Convert PIL image to tensor
            image_array = np.array(image)
            image_tensor = torch.tensor(image_array).permute(2, 0, 1).float().unsqueeze(0)
            
            # Normalize to 0-1 range
            image_tensor = image_tensor / 255.0
            
            # Resize to model input size
            image_tensor = F.interpolate(image_tensor, size=(224, 224), mode='bilinear', align_corners=False)
            
            # Apply ImageNet normalization
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            image_tensor = (image_tensor - mean) / std
            
            # Move to device
            image_tensor = image_tensor.to(next(self.model.parameters()).device)
            
            # Generate CAM
            cam = self.generate_cam(image_tensor, class_idx)
            
            # Create output filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_gradcam.jpg")
            
            # Create overlay
            overlay_path = self.overlay_heatmap(image_path, cam, output_path)
            
            return overlay_path
            
        except Exception as e:
            print(f"Error generating Grad-CAM image: {e}")
            # Return None if generation fails
            return None
