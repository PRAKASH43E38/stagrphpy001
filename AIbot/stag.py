import cv2
import numpy as np
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
import pyttsx3

class ImageSteganography:
    def __init__(self):
        self.delimiter = "###END_OF_HIDDEN_DATA###"
    
    def string_to_binary(self, text):
        """Convert string to binary representation."""
        return ''.join(format(ord(char), '08b') for char in text)
    
    def binary_to_string(self, binary):
        """Convert binary to string."""
        binary = binary[:len(binary) - (len(binary) % 8)]
        chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            chars.append(chr(int(byte, 2)))
        return ''.join(chars)
    
    def hide_text_in_image(self, image_path, text_to_hide, output_path):
        """Hide text in an image using LSB steganography."""
        try:
            if not os.path.isfile(image_path):
                raise ValueError(f"Image file does not exist: {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            text_with_delimiter = text_to_hide + self.delimiter
            binary_data = self.string_to_binary(text_with_delimiter)
            data_length = len(binary_data)
            
            total_pixels = img.size
            if data_length > total_pixels:
                raise ValueError(f"Image too small to hold data. Required: {data_length} bits, Available: {total_pixels} bits")
            
            encoded_img = img.copy()
            flat_img = encoded_img.ravel()
            binary_array = np.array([int(bit) for bit in binary_data], dtype=np.uint8)
            flat_img[:data_length] = (flat_img[:data_length] & 0xFE) | binary_array
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            if not cv2.imwrite(output_path, encoded_img):
                raise ValueError(f"Failed to save image to {output_path}")
            
            print(f"Text successfully hidden in {output_path}")
            print(f"Hidden {len(text_to_hide)} characters of text")
            return True
        except Exception as e:
            print(f"Error hiding text: {str(e)}")
            return False
    
    def extract_text_from_image(self, image_path):
        """Extract hidden text from an image."""
        try:
            if not os.path.isfile(image_path):
                raise ValueError(f"Image file does not exist: {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            binary_data = ''.join(str(pixel & 1) for pixel in img.ravel())
            extracted_text = self.binary_to_string(binary_data)
            
            delimiter_pos = extracted_text.find(self.delimiter)
            if delimiter_pos != -1:
                return extracted_text[:delimiter_pos]
            else:
                return "No hidden text found or delimiter not detected"
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return None
    
    def create_sample_image(self, width=800, height=600, filename="sample_image.png"):
        """Create a sample image for testing."""
        try:
            img = np.zeros((height, width, 3), dtype=np.uint8)
            for i in range(height):
                for j in range(width):
                    img[i, j] = [
                        int(255 * i / height),
                        int(255 * j / width),
                        int(255 * (i + j) / (height + width))
                    ]
            
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            if not cv2.imwrite(filename, img):
                raise ValueError(f"Failed to save sample image to {filename}")
            
            print(f"Sample image created: {filename}")
            return filename
        except Exception as e:
            print(f"Error creating sample image: {str(e)}")
            return None

def demo_steganography():
    """Demonstration of the steganography system with text-to-speech output."""
    steg = ImageSteganography()
    
    # Prompt user for text to hide
    sample_text = input("Enter text to hide (or press Enter for default): ").strip()
    if not sample_text:
        sample_text = "This is a secret message hidden in the image!"
    
    # Create sample image and hide text
    print("Creating a sample image with hidden text for testing...")
    sample_img = steg.create_sample_image()
    if not sample_img:
        print("Failed to create sample image. Exiting demo.")
        return
    
    output_image = "image_with_hidden_text.png"
    if not steg.hide_text_in_image(sample_img, sample_text, output_image):
        print("Failed to hide text in image. Exiting demo.")
        return
    
    # Clean up sample image
    try:
        if os.path.exists(sample_img):
            os.remove(sample_img)
            print(f"Cleaned up sample image: {sample_img}")
    except Exception as e:
        print(f"Error cleaning up sample image: {str(e)}")
    
    # Initialize Tkinter for file dialog
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Prompt user to select an image file
    print("\nPlease select an image file to extract hidden text.")
    image_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
    )
    
    if not image_path:
        print("No image selected. Exiting demo.")
        return
    
    # Extract and display hidden text
    print("\n" + "="*50)
    print(f"EXTRACTING HIDDEN TEXT FROM IMAGE: {image_path}")
    print("="*50)
    
    extracted_text = steg.extract_text_from_image(image_path)
    
    if extracted_text and extracted_text != "No hidden text found or delimiter not detected":
        print("Successfully extracted hidden text:")
        print("-" * 40)
        print(extracted_text)
        print("-" * 40)
        
        # Initialize pyttsx3 engine and speak the text
        try:
            engine = pyttsx3.init()
            engine.say(extracted_text)
            engine.runAndWait()
            print("Text spoken successfully.")
        except Exception as e:
            print(f"Error with text-to-speech: {str(e)}")
    else:
        print("Failed to extract text from image")
        try:
            engine = pyttsx3.init()
            engine.say("No hidden text found or extraction failed.")
            engine.runAndWait()
        except Exception as e:
            print(f"Error with text-to-speech: {str(e)}")

if __name__ == "__main__":
    print("Image Steganography - Text Hiding and Text-to-Speech Demo")
    print("="*50)
    
    # Check if required libraries are available
    try:
        import cv2
        import numpy
        import PIL
        import tkinter
        import pyttsx3
        demo_steganography()
    except ImportError as e:
        print(f"Missing required library: {str(e)}")
        print("Install with: pip install opencv-python pillow numpy pyttsx3")
    except Exception as e:
        print(f"Error: {str(e)}")