#  DocForensics: Multi-Layer Digital Document Forensics Engine

An enterprise-grade document tamper detection and provenance auditing engine designed for automated KYC compliance, loan verification, and fraud prevention pipelines. 

DocForensics detects image manipulation, text splicing, and Generative AI inpainting across utility bills, bank statements, and identity documents through a hybrid architecture combining deterministic computer vision mathematics and deep learning vision transformers.

---

##  Architecture Overview

```text
                              Incoming Document (JPG / PNG / JFIF)
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
    [ Deterministic Physics / Math ]                              [ Deep Learning Inference ]
    ├─ Error Level Analysis (ELA)                                 └─ Vision Transformer (ViT)
    ├─ Laplacian Noise Grain Filter                                    AI Inpainting / Diffusion
    ├─ Fast Fourier Transform (FFT)                                    Artifact Classifier
    ├─ EXIF Metadata & Provenance Scan
    └─ PyZbar QR / Barcode Payload Match
               │                                                               │
               └───────────────────────────────┬───────────────────────────────┘
                                               ▼
                              [ Dynamic Ensemble Scoring Engine ]
                                               │
                                ┌──────────────┴──────────────┐
                                ▼                             ▼
                    Calibrated Risk Metric (0-100%)    Tamper Heatmaps (Base64)
                    Low / Medium / High Risk Verdict    QR Integrity Records
```

---

##  Key Forensic Layers

1. **Vision Transformer (ViT) Classifier:** Scans local pixel structures for synthetic diffusion artifacts and deepfake generation patterns.
2. **Laplacian 2nd-Derivative Noise Filter:** Computes high-frequency sensor noise continuity across the document surface, identifying smooth "dead zones" left by AI inpainting and Photoshop clone tools.
3. **Error Level Analysis (ELA):** Analyzes JPEG compression gradient variances to detect spliced text and pasted digital layers.
4. **Fast Fourier Transform (FFT) Spectrum:** Converts spatial domain pixels into radial frequency power spectrums to expose unnatural periodic grid artifacts.
5. **Payload Cross-Verification:** Decodes embedded QR codes and barcodes using `pyzbar` / OpenCV to verify cryptographic hashes against printed document values.
6. **Provenance & Metadata Inspection:** Audits EXIF headers, camera hardware profiles, and software signatures (Photoshop, Canva, Gemini, etc.).

---

##  Performance & Benchmarks

* **Inference Latency:** < 1.2 seconds per document audit on CPU (< 300 ms on CUDA GPU).
* **Format Flexibility:** Supports JPEG, PNG, and JFIF document photographs and digital captures.
* **Architecture:** Decoupled FastAPI backend serving JSON verification reports and Base64-encoded visual heatmaps.

---

##  Project Structure

```text
document-forensics/
│
├── core/                           # Forensic mathematical and AI engines
│   ├── __init__.py
│   ├── ai_vision.py                # Hugging Face Vision Transformer loader
│   ├── ela_engine.py               # Error Level Analysis & variance scoring
│   ├── frequency_fft.py            # FFT radial frequency domain analysis
│   ├── laplacian.py                # 2nd-derivative Laplacian noise grain filter
│   ├── metadata_scan.py            # EXIF tag & provenance analyzer
│   └── qr_scanner.py               # PyZbar / OpenCV QR payload decoder
│
├── api.py                          # Production FastAPI REST backend
├── main.py                         # Streamlit diagnostic dashboard
├── requirements.txt                # Project dependencies
├── .gitignore                      # Git artifact filter
└── README.md                       # Documentation
```

---

##  Installation & Quickstart

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
cd document-forensics
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Server
```bash
uvicorn api:app --reload --port 8000
```
API Documentation and interactive Swagger UI will be available at `http://localhost:8000/docs`.

---

##  REST API Reference

### `POST /api/v1/analyze`
Submits a document image for multi-layer forensic evaluation.

**Request:** `multipart/form-data`
* `file`: Image file (JPG, PNG, JFIF)

**Sample JSON Response:**
```json
{
  "verdict": "HIGH_RISK_FORGERY",
  "master_risk_score": 78.4,
  "document_type": "Camera Photograph",
  "quality_alerts": {
    "is_screenshot": false,
    "is_blurry": false
  },
  "scores": {
    "ela_score": 42.1,
    "laplacian_variance": 124.5,
    "laplacian_score": 24.9,
    "fft_score": 68.2,
    "metadata_score": 65.0,
    "ai_risk_score": 91.2,
    "ai_confidence": 91.2,
    "ai_classification": "FAKE"
  },
  "metadata": {
    "flags": [],
    "raw_exif": {}
  },
  "qr_payloads": {
    "detected": true,
    "count": 1,
    "payloads": ["METER:0142948201;DATE:2021-06-16"],
    "records": [
      {
        "type": "QRCODE",
        "data": "METER:0142948201;DATE:2021-06-16"
      }
    ]
  },
  "heatmaps": {
    "ela_base64": "<base64_string>",
    "laplacian_base64": "<base64_string>",
    "fft_base64": "<base64_string>"
  }
}
```

---

##  Contributing

Contributions are welcome! If you would like to improve the forensic engines or expand file format support (e.g., native PDF stream parsing):

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/forensic-engine-upgrade`).
3. Commit your changes (`git commit -m 'feat: added new noise analysis module'`).
4. Push to the branch (`git push origin feature/forensic-engine-upgrade`).
5. Open a Pull Request.

---

##  Security & Privacy Notice
This pipeline operates purely locally or in private VPC instances. No document data, image buffers, or EXIF metadata are transmitted to external cloud APIs during inference.
