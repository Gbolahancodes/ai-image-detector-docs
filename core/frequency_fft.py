import numpy as np
import cv2
from PIL import Image

def analyze_frequency_domain(image):
    # 1. Convert to grayscale math array
    img_array = np.array(image.convert('L'))
    
    # 2. Fast Fourier Transform (FFT) - Breaks image into wave frequencies
    f_transform = np.fft.fft2(img_array)
    f_shift = np.fft.fftshift(f_transform) # Shift zero-frequency to the center
    
    # 3. Calculate Magnitude Spectrum
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1e-9)
    
    # Apply Viridis heatmap (just like the image-provenance repo)
    mag_normalized = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    fft_heatmap = cv2.applyColorMap(mag_normalized, cv2.COLORMAP_VIRIDIS)
    
    # 4. Calculate Radial High-Frequency Anomaly Score
    # AI leaves unnatural variance in the outer edges (high frequencies)
    h, w = img_array.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    
    # Mask out the low-frequency center
    mask_radius = min(h, w) // 4
    mask = (x - cx)**2 + (y - cy)**2 <= mask_radius**2
    high_freq_components = np.abs(f_shift)[~mask]
    
    # Variance of high frequencies
    hf_variance = np.var(high_freq_components)
    
    # Map to a 0-100 risk score based on heuristic AI generation thresholds
    risk_score = min((hf_variance / 50000.0) * 100.0, 99.9)
    
    return Image.fromarray(cv2.cvtColor(fft_heatmap, cv2.COLOR_BGR2RGB)), round(risk_score, 1)