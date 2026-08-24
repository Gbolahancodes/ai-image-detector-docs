import cv2
import numpy as np
from PIL import Image

def scan_payloads(image):
    """
    Decodes QR codes and Barcodes from document images using PyZbar
    with an OpenCV fallback. Extracts embedded verification payloads.
    """
    img_np = np.array(image.convert('RGB'))
    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    results = []
    
    # 1. Try PyZbar (Reads QR codes, Code 128, EAN, PDF417)
    try:
        from pyzbar.pyzbar import decode
        decoded_objects = decode(img_gray)
        for obj in decoded_objects:
            data_str = obj.data.decode('utf-8', errors='ignore')
            results.append({
                "type": str(obj.type),
                "data": data_str
            })
    except Exception:
        pass
    
    # 2. Fallback to OpenCV QRCodeDetector if pyzbar finds nothing
    if len(results) == 0:
        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(img_gray)
        if data:
            results.append({
                "type": "QRCODE",
                "data": data
            })
            
    is_detected = len(results) > 0
    payload_list = [item["data"] for item in results]
    
    return {
        "detected": is_detected,
        "count": len(results),
        "payloads": payload_list,
        "records": results
    }