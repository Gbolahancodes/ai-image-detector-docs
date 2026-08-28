import streamlit as st
import io
import base64
from PIL import Image

# Import your core engines exactly as they are in your folder structure
from core.ela_engine import generate_ela
from core.laplacian import analyze_laplacian_noise
from core.metadata_scan import extract_metadata
from core.frequency_fft import analyze_frequency_domain
from core.ai_vision import load_ai_model, analyze_with_deep_learning
from core.qr_scanner import scan_payloads

# --- CACHE & STATE MANAGEMENT ---
@st.cache_resource
def get_model():
    return load_ai_model()

def init_state():
    if 'view' not in st.session_state: st.session_state.view = 'upload'
    if 'results' not in st.session_state: st.session_state.results = []
    if 'active_index' not in st.session_state: st.session_state.active_index = 0

def change_view(view_name):
    st.session_state.view = view_name
    st.rerun()

def reset():
    st.session_state.results = []
    st.session_state.active_index = 0
    change_view('upload')

# --- PROCESSING LOGIC ---
def process_document(file, ai_model):
    image = Image.open(file)
    # Prevent RGBA crashes
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        bg = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == 'P': image = image.convert('RGBA')
        bg.paste(image, mask=image.split()[3] if len(image.split()) > 3 else None)
        image = bg
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    ela_map, ela_score = generate_ela(image)
    lap_map, lap_var, lap_score = analyze_laplacian_noise(image)
    fft_map, fft_score = analyze_frequency_domain(image)
    meta, flags, meta_score = extract_metadata(image)
    qr = scan_payloads(image)
    ai_label, ai_conf, ai_risk = analyze_with_deep_learning(image, ai_model)

    is_screenshot = (meta_score == 65.0) and (ela_score < 15.0)
    master_risk = round((0.20 * fft_score) + (0.80 * ai_risk) if is_screenshot else (0.10 * ela_score) + (0.10 * lap_score) + (0.15 * fft_score) + (0.25 * meta_score) + (0.40 * ai_risk), 1)

    if master_risk >= 45.0:
        verdict, v_class = "HIGH RISK FORGERY", "#ef4444"
        desc = "Deep learning models, Laplacian noise anomalies, or modified metadata indicate high tampering probability."
    elif master_risk >= 35.0:
        verdict, v_class = "MEDIUM RISK REVIEW", "#eab308"
        desc = "Mixed forensic signals detected. Document may have undergone compression, re-saving, or subtle editing."
    else:
        verdict, v_class = "AUTHENTIC", "#22c55e"
        desc = "Pixel physics, metadata integrity, and neural network inference confirm authentic provenance."

    return {
        'name': file.name, 'image': image, 'master_risk': master_risk, 'verdict': verdict, 'v_class': v_class,
        'desc': desc, 'lap_var': lap_var, 'ela_score': ela_score, 'fft_score': fft_score, 'qr': qr, 'flags': flags,
        'meta': meta, 'ela_map': ela_map, 'lap_map': lap_map, 'fft_map': fft_map
    }

# --- MAIN RENDERER ---
def render_dashboard():
    st.set_page_config(page_title="Tampect", layout="centered")
    init_state()
    ai_model = get_model()

    # INJECT YOUR EXACT REACT CSS STYLING
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #000000; color: #ffffff; }
        [data-testid="stHeader"], footer { display: none !important; }
        .glass-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 24px; margin-bottom: 24px; backdrop-filter: blur(12px); }
        .verdict-title { font-size: 2rem; font-weight: 900; text-transform: uppercase; margin: 0; display: flex; align-items: center; gap: 16px; }
        .verdict-score { font-size: 4rem; font-weight: 900; margin: 0; line-height: 1; text-align: right; }
        .score-label { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: rgba(255,255,255,0.5); letter-spacing: 1px; text-align: right; display: block; }
        /* Style Streamlit Tabs to look like React EvidenceTabs */
        [data-baseweb="tab-list"] { gap: 8px; background: transparent; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        [data-baseweb="tab"] { background: rgba(255,255,255,0.05); border-radius: 8px; border: none !important; padding: 10px 20px; color: rgba(255,255,255,0.5); }
        [aria-selected="true"] { background: rgba(255,255,255,0.15) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    # Top Navbar Replica
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; margin-top: -30px;">
        <h1 style="font-size: 1.5rem; font-weight: bold; margin:0; display:flex; gap:10px;"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Tampect</h1>
        <div style="border: 1px solid rgba(255,255,255,0.1); padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; color: #a1a1aa;">System Specs</div>
    </div>
    """, unsafe_allow_html=True)

    # --- VIEW 1: UPLOAD ---
    if st.session_state.view == 'upload':
        st.markdown("<h2 style='text-align: center; font-size: 2.5rem; font-weight: 800;'>Document Verification</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 30px;'>Upload a physical document capture to detect digital forgery.</p>", unsafe_allow_html=True)
        
        mode = st.radio("Mode", ["Single Upload", "Batch Processing"], horizontal=True, label_visibility="collapsed")
        is_batch = mode == "Batch Processing"
        
        files = st.file_uploader("", type=["jpg", "png", "webp"], accept_multiple_files=is_batch)
        
        if files:
            if not isinstance(files, list): files = [files]
            if st.button(f"Analyze Document{'s' if len(files)>1 else ''}", use_container_width=True):
                for f in files:
                    with st.spinner(f"Analyzing {f.name}..."):
                        st.session_state.results.append(process_document(f, ai_model))
                change_view('single' if len(files) == 1 else 'batch')

    # --- VIEW 2: BATCH RESULTS ---
    elif st.session_state.view == 'batch':
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"<h2>Batch Results ({len(st.session_state.results)})</h2>", unsafe_allow_html=True)
        if c2.button("← Start Over", use_container_width=True): reset()

        for i, res in enumerate(st.session_state.results):
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center; padding: 16px;">
                    <div><h4 style="margin:0;">{res['name']}</h4><p style="margin:0; color:{res['v_class']};">Risk: {res['master_risk']}%</p></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View Report", key=f"view_{i}"):
                    st.session_state.active_index = i
                    change_view('single')

    # --- VIEW 3: SINGLE ANALYSIS ---
    elif st.session_state.view == 'single':
        res = st.session_state.results[st.session_state.active_index]
        is_batch = len(st.session_state.results) > 1

        if st.button("← Analyze Another" if not is_batch else "← Back to Batch"):
            change_view('batch') if is_batch else reset()

        # Verdict Card Replica
        st.markdown(f"""
        <div class="glass-card" style="display: flex; justify-content: space-between; align-items: center; border-color: {res['v_class']}40;">
            <div class="verdict-title"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="{res['v_class']}" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> {res['verdict']}</div>
            <div>
                <p class="verdict-score" style="color: {res['v_class']};">{res['master_risk']}%</p>
                <span class="score-label">Overall Risk Score</span>
            </div>
        </div>
        <div class="glass-card"><p style="font-size: 0.75rem; color: #a1a1aa; font-weight: bold; text-transform: uppercase;">Analysis</p><p style="margin:0;">{res['desc']}</p></div>
        """, unsafe_allow_html=True)

        # Evidence Tabs Replica
        t1, t2, t3, t4 = st.tabs(["Laplacian Grain", "ELA Heatmap", "QR/Barcode", "Metadata"])
        with t1:
            c1, c2 = st.columns(2)
            c1.image(res['image'], caption="ORIGINAL", use_container_width=True)
            c2.image(res['lap_map'], caption=f"NOISE MAP (VAR: {res['lap_var']})", use_container_width=True)
        with t2:
            c1, c2 = st.columns(2)
            c1.image(res['image'], caption="ORIGINAL", use_container_width=True)
            c2.image(res['ela_map'], caption=f"COMPRESSION MAP (SCORE: {res['ela_score']})", use_container_width=True)
        with t3:
            if res['qr'].get('detected'):
                for r in res['qr'].get('records', []):
                    st.info(f"**{r.get('type')}**: {r.get('data')}")
            else:
                st.warning("No QR code or Barcode detected.")
        with t4:
            if res['flags']:
                for f in res['flags']: st.error(f)
            st.json(res['meta'])
