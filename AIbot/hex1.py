import cv2
import numpy as np
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, Label, Button, Text, Scrollbar, Frame
from PIL import ImageTk

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
    
    def hide_code_in_image(self, image_path, code_to_hide, output_path):
        """Hide code/text in an image using LSB steganography."""
        try:
            if not os.path.isfile(image_path):
                raise ValueError(f"Image file does not exist: {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            code_with_delimiter = code_to_hide + self.delimiter
            binary_data = self.string_to_binary(code_with_delimiter)
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
            
            print(f"Code successfully hidden in {output_path}")
            print(f"Hidden {len(code_to_hide)} characters of code")
            return True
        except Exception as e:
            print(f"Error hiding code: {str(e)}")
            return False
    
    def extract_code_from_image(self, image_path):
        """Extract hidden code from an image."""
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
                return "No hidden data found or delimiter not detected"
        except Exception as e:
            print(f"Error extracting code: {str(e)}")
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

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography - Code Extractor")
        self.steg = ImageSteganography()
        
        # GUI elements
        self.frame = Frame(self.root)
        self.frame.pack(padx=10, pady=10)
        
        self.select_button = Button(self.frame, text="Select Image", command=self.select_image)
        self.select_button.pack(pady=5)
        
        self.image_label = Label(self.frame)
        self.image_label.pack(pady=5)
        
        self.code_text = Text(self.frame, height=10, width=50)
        self.code_text.pack(pady=5)
        self.scrollbar = Scrollbar(self.frame, orient="vertical", command=self.code_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.code_text.config(yscrollcommand=self.scrollbar.set)
        
        self.execute_button = Button(self.frame, text="Execute Code", command=self.execute_code, state="disabled")
        self.execute_button.pack(pady=5)
        
        self.status_label = Label(self.frame, text="", wraplength=400)
        self.status_label.pack(pady=5)
        
        self.extracted_code = None
        
        # Create sample image with hidden code
        self.create_sample_image_with_code()
    
    def create_sample_image_with_code(self):
        """Create a sample image with hidden code for testing."""
        sample_code = input("Enter a data:")
        
        sample_img = self.steg.create_sample_image()
        if sample_img:
            output_image = "image_with_hidden_code.png"
            if self.steg.hide_code_in_image(sample_img, sample_code, output_image):
                self.status_label.config(text=f"Sample image with hidden code created: {output_image}")
                try:
                    if os.path.exists(sample_img):
                        os.remove(sample_img)
                        print(f"Cleaned up sample image: {sample_img}")
                except Exception as e:
                    print(f"Error cleaning up sample image: {str(e)}")
            else:
                self.status_label.config(text="Failed to hide code in sample image.")
        else:
            self.status_label.config(text="Failed to create sample image.")
    
    def select_image(self):
        """Open file dialog to select an image and extract code."""
        image_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        
        if not image_path:
            self.status_label.config(text="No image selected.")
            return
        
        # Display the image
        try:
            img = Image.open(image_path)
            img = img.resize((300, 200), Image.LANCZOS)  # Resize for display
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk  # Keep a reference
        except Exception as e:
            self.status_label.config(text=f"Error loading image for display: {str(e)}")
            return
        
        # Extract code
        self.extracted_code = self.steg.extract_code_from_image(image_path)
        self.code_text.delete(1.0, tk.END)
        
        if self.extracted_code and self.extracted_code != "No hidden data found or delimiter not detected":
            self.code_text.insert(tk.END, self.extracted_code)
            self.execute_button.config(state="normal")
            self.status_label.config(text="Code extracted successfully. Click 'Execute Code' to run.")
        else:
            self.code_text.insert(tk.END, "No hidden code found or extraction failed.")
            self.execute_button.config(state="disabled")
            self.status_label.config(text="No executable code found in the image.")
    
    def execute_code(self):
        """Execute the extracted code."""
        if self.extracted_code:
            try:
                exec(self.extracted_code)
                self.status_label.config(text="Code executed successfully.")
            except Exception as e:
                self.status_label.config(text=f"Error executing code: {str(e)}")
        else:
            self.status_label.config(text="No code to execute.")

def main():
    print("Image Steganography - GUI Code Execution Demo")
    print("="*50)
    
    try:
        import cv2
        import numpy
        import PIL
        import tkinter
        from PIL import ImageTk
        
        root = tk.Tk()
        app = SteganographyGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"Missing required library: {str(e)}")
        print("Install with: pip install opencv-python pillow numpy")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()