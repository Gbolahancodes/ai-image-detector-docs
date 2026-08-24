from PIL import Image, ImageChops, ImageEnhance
import numpy as np

def generate_ela(image, quality=90):
    img_rgb = image.convert('RGB')
    img_rgb.save("temp_ela.jpg", "JPEG", quality=quality)
    resaved = Image.open("temp_ela.jpg")
    
    ela_image = ImageChops.difference(img_rgb, resaved)
    
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0: max_diff = 1
    
    scale = 255.0 / max_diff
    ela_enhanced = ImageEnhance.Brightness(ela_image).enhance(scale)
    
    gray_ela = ela_enhanced.convert('L')
    variance = float(np.std(np.array(gray_ela)))
    score = min((variance / 50.0) * 100.0, 100.0)
    
    return ela_enhanced, round(score, 1)