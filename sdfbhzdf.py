import os
from PIL import Image
import numpy as np
import pyttsx3

class RGBImageSteganography:
    def __init__(self, verbose: bool = True):
        self.delimiter = "###END###"
        self.verbose = verbose
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self._log("Text-to-speech engine initialized")
        except Exception as e:
            self._log(f"Failed to initialize text-to-speech engine: {str(e)}")
            self.tts_engine = None
    
    def _log(self, message: str):
        if self.verbose:
            print(message)
    
    def validate_image(self, image_path: str) -> bool:
        try:
            if not os.path.isfile(image_path):
                self._log(f"Image file '{image_path}' not found.")
                return False
            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self._log("Only PNG or JPEG images are supported.")
                return False
            img = Image.open(image_path)
            img.verify()
            img.close()
            self._log(f"Valid image: {image_path}")
            return True
        except Exception as e:
            self._log(f"Error validating image: {str(e)}")
            return False

    def hide_text_in_image(self, image_path: str, text: str, output_path: str) -> bool:
        try:
            if not self.validate_image(image_path):
                return False
            img = Image.open(image_path).convert("RGB")
            pixels = np.array(img)
            height, width, _ = pixels.shape
            delimited_text = text + self.delimiter
            binary_text = ''.join(format(ord(char), '08b') for char in delimited_text)
            max_bits = width * height * 3
            if len(binary_text) > max_bits:
                self._log(f"Message too long! Needs {len(binary_text)} bits, capacity {max_bits} bits")
                return False
            flat_pixels = pixels.ravel()
            for i in range(len(binary_text)):
                flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(binary_text[i])
            steg_img = Image.fromarray(pixels, "RGB")
            steg_img.save(output_path)
            self._log(f"Text hidden in '{output_path}' ({len(text)} chars, {len(binary_text)} bits)")
            return True
        except Exception as e:
            self._log(f"Error hiding text: {str(e)}")
            return False

    def extract_text_from_image(self, image_path: str) -> str:
        try:
            if not self.validate_image(image_path):
                return f"Invalid image file '{image_path}'"
            img = Image.open(image_path).convert("RGB")
            pixels = np.array(img).ravel()
            binary_data = ''.join(str(p & 1) for p in pixels)
            message = ""
            delimiter_bits = ''.join(format(ord(c), '08b') for c in self.delimiter)
            for i in range(0, len(binary_data), 8):
                byte = binary_data[i:i+8]
                if i + len(delimiter_bits) <= len(binary_data) and binary_data[i:i+len(delimiter_bits)] == delimiter_bits:
                    break
                char_code = int(byte, 2)
                message += chr(char_code)
            if message:
                self._log(f"Extracted: {message}")
                if self.tts_engine:
                    try:
                        self.tts_engine.say(message)
                        self.tts_engine.runAndWait()
                        self._log("Message spoken aloud")
                    except Exception as e:
                        self._log(f"Failed to speak message: {str(e)}")
                else:
                    self._log("Text-to-speech engine not available")
                return message
            else:
                self._log("No hidden message found.")
                if self.tts_engine:
                    try:
                        self.tts_engine.say("No hidden message found")
                        self.tts_engine.runAndWait()
                        self._log("Default message spoken aloud")
                    except Exception as e:
                        self._log(f"Failed to speak default message: {str(e)}")
                return "No hidden message found."
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def get_image_info(self, image_path: str) -> dict:
        try:
            if not self.validate_image(image_path):
                return {"error": f"Invalid image file '{image_path}'"}
            img = Image.open(image_path)
            total_pixels = img.width * img.height
            max_bits = total_pixels * 3
            return {
                "width": img.width,
                "height": img.height,
                "total_pixels": total_pixels,
                "max_bits": max_bits,
                "max_characters": max_bits // 8,
                "format": img.format,
                "mode": img.mode
            }
        except Exception as e:
            return {"error": str(e)}

def interactive_demo():
    steg = RGBImageSteganography()
    while True:
        print("\nRGB Image Steganography Tool")
        print("1. Validate image (PNG or JPEG)")
        print("2. Hide text in image")
        print("3. Extract text from image (with speech)")
        print("4. Get image info")
        print("5. Exit")
        choice = input("Enter choice (1-5): ").strip()
        if choice == "1":
            image_path = input("Enter image path (image.png or image.jpg): ").strip()
            if image_path:
                steg.validate_image(image_path)
            else:
                print("Missing image path.")
        elif choice == "2":
            image_path = input("Source image path (image.png or image.jpg): ").strip()
            message = input("Text to hide: ").strip()
            output_path = input("Output filename (default 'hidden.png'): ").strip() or "hidden.png"
            if image_path and message:
                steg.hide_text_in_image(image_path, message, output_path)
            else:
                print("Missing image path or message.")
        elif choice == "3":
            image_path = input("Image path to extract (image.png or image.jpg): ").strip()
            if image_path:
                steg.extract_text_from_image(image_path)
            else:
                print("Missing image path.")
        elif choice == "4":
            image_path = input("Image path (image.png or image.jpg): ").strip()
            if image_path:
                info = steg.get_image_info(image_path)
                if "error" not in info:
                    print(f"Dimensions: {info['width']}x{info['height']}, Capacity: ~{info['max_characters']} chars")
                    print(f"Format: {info['format']}, Mode: {info['mode']}")
                else:
                    print(info["error"])
            else:
                print("Missing image path.")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1-5.")

if __name__ == "__main__":
    interactive_demo()