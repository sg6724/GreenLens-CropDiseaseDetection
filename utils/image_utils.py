import os
import uuid
from PIL import Image
import cv2
import numpy as np

def save_uploaded_image(file_data, upload_dir):
    """Save uploaded image file"""
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        return filepath
        
    except Exception as e:
        print(f"Error saving uploaded image: {e}")
        raise

def validate_image(filepath):
    """Validate if file is a valid image"""
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except Exception:
        return False

def resize_image(image_path, target_size=(224, 224)):
    """Resize image to target size"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img_resized = img.resize(target_size, Image.LANCZOS)
            return img_resized
    except Exception as e:
        print(f"Error resizing image: {e}")
        raise

def save_image(image, filepath):
    """Save PIL image to file"""
    try:
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        raise

def create_heatmap_overlay(original_image_path, heatmap_array, output_path, alpha=0.4):
    """Create heatmap overlay on original image"""
    try:
        # Load original image
        original = cv2.imread(original_image_path)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        
        # Resize heatmap to match original image
        heatmap_resized = cv2.resize(heatmap_array, (original.shape[1], original.shape[0]))
        
        # Convert to heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Create overlay
        overlay = original * (1 - alpha) + heatmap * alpha
        overlay = np.uint8(overlay)
        
        # Save overlay
        overlay_image = Image.fromarray(overlay)
        overlay_image.save(output_path)
        
        return output_path
        
    except Exception as e:
        print(f"Error creating heatmap overlay: {e}")
        raise

def cleanup_temp_files(directory, max_age_hours=24):
    """Clean up temporary files older than max_age_hours"""
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getctime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    print(f"Cleaned up old file: {filepath}")
                    
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")
