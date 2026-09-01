import numpy as np
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import io
import base64

class FrequencyAnalyzer:
    def __init__(self):
        pass

    def generate_spectrum(self, image: Image.Image) -> str:
        """
        Generates a 2D Frequency Spectrum (Magnitude Plot) from a PIL Image.
        Returns a base64 encoded PNG string of the spectrum.
        """
        try:
            # 1. Convert to Grayscale
            img_gray = image.convert('L')
            
            # 2. Convert to Numpy Array
            img_array = np.array(img_gray)
            
            # 3. Compute FFT (Fast Fourier Transform)
            # f = np.fft.fft2(img_array)
            # fshift = np.fft.fftshift(f)
            # magnitude_spectrum = 20 * np.log(np.abs(fshift))
             
            # Use a slightly more robust method for visualization
            f = np.fft.fft2(img_array)
            fshift = np.fft.fftshift(f)
            # Add epsilon to avoid log(0)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-9)

            # 4. Normalize to 0-255 for standard image display
            mag_min = magnitude_spectrum.min()
            mag_max = magnitude_spectrum.max()
            
            # Avoid division by zero if image is blank
            if mag_max == mag_min:
                normalized = np.zeros_like(magnitude_spectrum, dtype=np.uint8)
            else:
                normalized = 255 * (magnitude_spectrum - mag_min) / (mag_max - mag_min)
                normalized = np.uint8(normalized)

            # 5. Convert back to PIL Image
            spectrum_img = Image.fromarray(normalized)

            # 6. Encode to Base64
            buffered = io.BytesIO()
            spectrum_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return img_str
            
        except Exception as e:
            print(f"Error generating frequency spectrum: {e}")
            return ""

    def generate_pattern_map(self, image: Image.Image) -> str:
        """
        Generates a Noise Pattern Map (High-Pass/Laplacian) to visualize
        checkerboard artifacts.
        """
        try:
            # 1. Convert to Grayscale
            img_gray = image.convert('L')
            
            # 2. Apply Laplacian Filter (High-Pass)
            # This removes smooth areas and keeps edges/noise
            noise_map = img_gray.filter(ImageFilter.FIND_EDGES) 
            # Note: FIND_EDGES is a simple approximation. For better grid visualization,
            # we can use a Kernel, but this is usually sufficient for "seeing" the grid.
            
            # 3. Invert to make lines black on white (easier to see)
            # noise_map = ImageOps.invert(noise_map)
            # Actually, white on black (default) effectively shows the "glowing" grid lines.
            
            # 4. Enhance Contrast/Brightness to make faint artifacts visible
            # We convert to numpy to scale
            arr = np.array(noise_map).astype(float)
            
            # Amplify
            arr = arr * 5.0 # Boost signal
            arr = np.clip(arr, 0, 255).astype(np.uint8)
            
            enhanced_map = Image.fromarray(arr)
            
            # 5. Encode
            buffered = io.BytesIO()
            enhanced_map.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return img_str
            
        except Exception as e:
            print(f"Error generating pattern map: {e}")
            return ""
