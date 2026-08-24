from transformers import pipeline

def load_ai_model():
    # Reverting to the stable, working model
    model_name = "dima806/deepfake_vs_real_image_detection"
    return pipeline("image-classification", model=model_name)

def analyze_with_deep_learning(image, ai_model):
    img_rgb = image.convert('RGB')
    results = ai_model(img_rgb)
    
    top_result = results[0]
    label = top_result['label'].upper()
    confidence = top_result['score'] * 100.0
    
    if label == "FAKE":
        ai_risk_score = confidence
    else:
        ai_risk_score = 100.0 - confidence
        
    return label, round(confidence, 1), round(ai_risk_score, 1)