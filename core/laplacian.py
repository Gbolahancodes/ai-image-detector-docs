import cv2
import numpy as np
from PIL import Image

def analyze_laplacian_noise(image):
    """
    Computes a 2nd-derivative Laplacian operator to isolate microscopic
    camera noise grain and expose localized inpainting smoothing.
    """
    # 1. Convert PIL image to grayscale numpy array
    img_array = np.array(image.convert('L'))
    
    # 2. Compute 2nd-derivative Laplacian kernel
    laplacian = cv2.Laplacian(img_array, cv2.CV_64F, ksize=3)
    
    # 3. Calculate Laplacian variance (Global focus & sensor noise density)
    lap_variance = float(laplacian.var())
    
    # 4. Generate high-contrast visual heatmap of the noise/grain distribution
    lap_abs = np.absolute(laplacian)
    lap_normalized = cv2.normalize(lap_abs, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    lap_heatmap = cv2.applyColorMap(lap_normalized, cv2.COLORMAP_INFERNO)
    
    # Scale variance to a 0-100 metric for dashboard display
    lap_metric = round(min((lap_variance / 500.0) * 100.0, 100.0), 1)
    
    heatmap_pil = Image.fromarray(cv2.cvtColor(lap_heatmap, cv2.COLOR_BGR2RGB))
    return heatmap_pil, round(lap_variance, 2), lap_metric