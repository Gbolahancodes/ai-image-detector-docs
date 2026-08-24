import streamlit as st
from PIL import Image

# Core Forensic Engines
from core.ela_engine import generate_ela
from core.laplacian import analyze_laplacian_noise
from core.metadata_scan import extract_metadata
from core.frequency_fft import analyze_frequency_domain
from core.ai_vision import load_ai_model, analyze_with_deep_learning
from core.qr_scanner import scan_payloads

@st.cache_resource
def init_model():
    return load_ai_model()

def render_dashboard():
    st.set_page_config(page_title="DocForensics Enterprise", layout="wide")
    
    st.title("🔍 Enterprise Multi-Layer Document Forensics")
    st.markdown("Digital Document & Financial Statement Tamper Detector for KYC, Loan, and Utility Bill Audits.")
    st.divider()

    # --- UPLOAD INSTRUCTIONS & QUALITY GUIDELINES ---
    st.info(
        """
        📸 **Document Upload Requirements:**
        * **Direct Camera Photos Only:** Take a clear, well-lit photo of the physical document.
        * **No Screenshots:** Screenshots strip device EXIF metadata and sensor noise, which will elevate the fraud risk score.
        * **Avoid Blurry / Glare-Heavy Shots:** Ensure all text, serial numbers, and QR codes are in focus and legible.
        """
    )

    ai_model = init_model()
    uploaded_file = st.file_uploader(
        "Upload Physical Document Photograph (JPG, JPEG, PNG, JFIF)", 
        type=["jpg", "jpeg", "png", "jfif"]
    )

    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        with st.spinner("Executing Multi-Layer Forensic Pipeline (< 2s)..."):
            # 1. Physics & Mathematical Operators
            ela_heatmap, ela_score = generate_ela(original_image)
            lap_heatmap, lap_var, lap_score = analyze_laplacian_noise(original_image)
            fft_heatmap, fft_score = analyze_frequency_domain(original_image)
            
            # 2. Metadata & Payload Verification
            metadata, flags, meta_score = extract_metadata(original_image)
            qr_data = scan_payloads(original_image)
            
            # 3. Deep Learning Vision Inference
            ai_label, ai_conf, ai_risk = analyze_with_deep_learning(original_image, ai_model)
            
            # 4. Quality & Format Checks
            is_screenshot = (meta_score == 65.0) and (ela_score < 15.0)
            is_blurry = lap_var < 50.0  # Low Laplacian variance indicates unfocused/blurry capture
            
            if is_screenshot:
                master_risk = (0.20 * fft_score) + (0.80 * ai_risk)
                doc_type = "Digital Screenshot"
            else:
                master_risk = (0.10 * ela_score) + (0.10 * lap_score) + (0.15 * fft_score) + (0.25 * meta_score) + (0.40 * ai_risk)
                doc_type = "Camera Photograph"

            master_risk = round(master_risk, 1)

        # --- QUALITY ALERT ADVISORIES ---
        if is_screenshot:
            st.warning("⚠️ **Screenshot Detected:** This document lacks camera hardware metadata. For full verification accuracy, please upload an original camera photo.")
        elif is_blurry:
            st.warning("⚠️ **Low Image Sharpness:** This photograph appears blurry or low-resolution. Consider re-taking the photo with better lighting and focus.")

        # --- MASTER VERDICT BANNER ---
        st.subheader("🎯 Master Forensic Verdict")
        v_col1, v_col2 = st.columns([1, 3])
        
        with v_col1:
            st.metric(label="Overall Risk Score", value=f"{master_risk}%")
            st.caption(f"Detected Format: **{doc_type}**")
            
        with v_col2:
            if master_risk >= 45.0:
                st.error("🚨 HIGH RISK: FORGERY DETECTED")
                st.write("**Analysis:** Deep learning models, Laplacian noise anomalies, or modified metadata indicate high tampering probability.")
            elif master_risk >= 35.0:
                st.warning("⚠️ MEDIUM RISK: REQUIRES MANUAL REVIEW")
                st.write("**Analysis:** Mixed forensic signals detected. Document may have undergone compression, re-saving, or subtle editing.")
            else:
                st.success("✅ LOW RISK: AUTHENTIC DOCUMENT")
                st.write("**Analysis:** Pixel physics, metadata integrity, and neural network inference confirm authentic provenance.")
        
        st.divider()

        # --- 5 FORENSIC EVIDENCE TABS ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧠 AI Vision", "🔬 Laplacian Grain", "🔥 ELA Heatmap", "📱 QR/Barcode Payload", "💾 Metadata"
        ])
        
        with tab1:
            st.subheader("Vision Transformer Analysis")
            st.write(f"**Classification:** `{ai_label}` (Model Confidence: `{ai_conf}%`)")
            st.progress(int(ai_risk))
            
        with tab2:
            st.subheader("Laplacian Noise Grain Filter")
            st.image(lap_heatmap, use_container_width=True)
            st.caption(f"Laplacian Variance: **{lap_var}** (Normalized Score: {lap_score}/100). Highlights sensor noise continuity and localized inpainting dead-zones.")
            
        with tab3:
            st.subheader("Error Level Analysis (ELA)")
            st.image(ela_heatmap, use_container_width=True)
            st.caption(f"Compression Variance: {ela_score}/100. Pinpoints resaved/pasted digital artifacts.")
            
        with tab4:
            st.subheader("QR / Barcode Payload Verification")
            if qr_data["detected"]:
                st.success(f"✅ Found {qr_data['count']} embedded code(s).")
                for item in qr_data["records"]:
                    st.code(f"Type: {item['type']}\nPayload: {item['data']}")
            else:
                st.info("ℹ️ No readable QR code or barcode detected on this document.")
                
        with tab5:
            st.subheader("EXIF & Provenance Integrity")
            if flags:
                for f in flags:
                    st.error(f)
            else:
                st.success("No editing software signatures found.")
            st.json(metadata)
            