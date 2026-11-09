"""
DocuQuery AI - Frontend
A minimal, professional document intelligence interface.
"""

import datetime
import time
from typing import Dict, List, Optional, Tuple

import pymupdf as fitz
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="DocuQuery AI | Document Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Design System CSS
# - Light neutral background (#F8FAFC)
# - White surfaces (#FFFFFF)
# - Primary text (#1E293B, #0F172A)
# - Accent (#2563EB)
# - Borders (#E2E8F0)
# - Streamlit header preserved & transparent so sidebar collapse/reopen works seamlessly
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Base typography */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
    color: #1E293B;
}

.stApp {
    background-color: #F8FAFC;
}

/* Header & Sidebar Controls (CRITICAL: Preserves collapse/expand button) */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    z-index: 100 !important;
}

[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    top: 0.65rem !important;
    left: 0.65rem !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
    color: #475569 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebarCollapsedControl"]:hover {
    color: #2563EB !important;
    border-color: #CBD5E1 !important;
    background-color: #F8FAFC !important;
}

[data-testid="stSidebarCollapseButton"] {
    color: #64748B !important;
}

[data-testid="stSidebarCollapseButton"]:hover {
    color: #0F172A !important;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    padding-top: 0.75rem !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.75rem;
    padding-left: 0.85rem;
    padding-right: 0.85rem;
}

/* Main Container Spacing */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1360px;
}

/* Welcome Box */
.welcome-box {
    margin-bottom: 1.5rem;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid #E2E8F0;
}

.welcome-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #2563EB;
    background-color: #EFF6FF;
    border: 1px solid #DBEAFE;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.welcome-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.015em;
}

.welcome-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin: 0;
    line-height: 1.5;
}

/* Dashboard Section Cards */
.dash-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1.25rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.dash-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid #F1F5F9;
}

.dash-card-title {
    font-size: 0.925rem;
    font-weight: 600;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Upload Dropzone Container */
.upload-hero {
    background-color: #F8FAFC;
    border: 1.5px dashed #CBD5E1;
    border-radius: 8px;
    padding: 1.5rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
    transition: all 0.15s ease;
}

.upload-hero:hover {
    border-color: #2563EB;
    background-color: #EFF6FF;
}

.upload-icon-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: #EFF6FF;
    border: 1px solid #DBEAFE;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.75rem auto;
    color: #2563EB;
}

.upload-instruction {
    font-size: 0.875rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 0.25rem;
}

.upload-subtext {
    font-size: 0.75rem;
    color: #64748B;
    margin-bottom: 0.75rem;
}

.upload-spec-tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 500;
    color: #475569;
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
}

/* Document Row in Recent List */
.doc-item-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.75rem 0.95rem;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.15s ease;
}

.doc-item-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.doc-item-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.doc-item-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background-color: #EFF6FF;
    border: 1px solid #DBEAFE;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2563EB;
    flex-shrink: 0;
}

.doc-item-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 0.15rem;
}

.doc-item-meta {
    font-size: 0.725rem;
    color: #64748B;
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

/* Badges */
.badge-ready {
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.badge-source {
    background-color: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #DBEAFE;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
}

.badge-score {
    background-color: #F8FAFC;
    color: #475569;
    border: 1px solid #E2E8F0;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 500;
}

/* Empty State Box */
.empty-state-box {
    background-color: #FFFFFF;
    border: 1px dashed #CBD5E1;
    border-radius: 6px;
    padding: 2.25rem 1.5rem;
    text-align: center;
    color: #64748B;
}

.empty-state-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #F1F5F9;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.75rem auto;
    color: #94A3B8;
}

.empty-state-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 0.25rem;
}

.empty-state-text {
    font-size: 0.775rem;
    color: #64748B;
    line-height: 1.4;
    max-width: 320px;
    margin: 0 auto;
}

/* Chat Styling */
.chat-user-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.75rem;
}

.chat-user-bubble {
    background-color: #EFF6FF;
    color: #1E3A8A;
    border: 1px solid #DBEAFE;
    border-radius: 6px;
    padding: 0.65rem 0.95rem;
    font-size: 0.85rem;
    max-width: 85%;
    line-height: 1.45;
}

.chat-assistant-bubble {
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.85rem 1.1rem;
    font-size: 0.85rem;
    line-height: 1.55;
    margin-bottom: 0.5rem;
}

.chat-assistant-header {
    font-size: 0.75rem;
    font-weight: 600;
    color: #2563EB;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

.source-item {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #3B82F6;
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    margin-top: 0.4rem;
    font-size: 0.775rem;
    color: #334155;
}

/* Button System Overrides (Zero Red, Clean Muted Blue & Slate) */
button, button[kind="primary"], div.stButton > button[kind="primary"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: 1px solid #1D4ED8 !important;
    border-radius: 6px !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease !important;
}

button[kind="primary"]:hover, div.stButton > button[kind="primary"]:hover {
    background-color: #1D4ED8 !important;
    border-color: #1E40AF !important;
    color: #FFFFFF !important;
}

button[kind="secondary"], div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
    box-shadow: none !important;
}

button[kind="secondary"]:hover, div.stButton > button[kind="secondary"]:hover {
    background-color: #F8FAFC !important;
    border-color: #CBD5E1 !important;
    color: #0F172A !important;
}

/* Sidebar navigation buttons */
[data-testid="stSidebar"] div.stButton > button {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.45rem 0.75rem !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    box-shadow: none !important;
    margin-bottom: 0.2rem !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    border: 1px solid #DBEAFE !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: #475569 !important;
    border: 1px solid transparent !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
    border: 1px solid #E2E8F0 !important;
}

/* File Uploader Clean Container */
[data-testid="stFileUploader"] {
    padding: 0 !important;
    background: transparent !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: #FAFAFA !important;
    border: 1.5px dashed #CBD5E1 !important;
    border-radius: 6px !important;
    padding: 1.25rem 0.75rem !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #2563EB !important;
    background-color: #EFF6FF !important;
}

/* Hide Streamlit default hamburger menu & footer, but preserve collapse/expand controls */
#MainMenu {
    display: none !important;
}

footer {
    display: none !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "active_nav": "Dashboard",  # "Dashboard" | "Documents" | "Workspace"
        "active_doc_id": None,
        "active_doc_title": "",
        "active_pdf_bytes": None,
        "pdf_page_number": 1,
        "pdf_total_pages": 1,
        "chat_history": {},  # doc_id -> list of message dicts
        "backend_online": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# -----------------------------------------------------------------------------
# Backend API Calls
# -----------------------------------------------------------------------------
def check_health() -> bool:
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        is_ok = res.status_code == 200
        st.session_state.backend_online = is_ok
        return is_ok
    except Exception:
        st.session_state.backend_online = False
        return False


def fetch_documents() -> List[Dict]:
    try:
        res = requests.get(f"{BACKEND_URL}/documents", timeout=4.0)
        if res.status_code == 200:
            return res.json().get("documents", [])
        return []
    except Exception:
        return []


def fetch_pdf_bytes(doc_id: str) -> Optional[bytes]:
    try:
        res = requests.get(f"{BACKEND_URL}/documents/{doc_id}/pdf", timeout=6.0)
        if res.status_code == 200:
            return res.content
        return None
    except Exception:
        return None


def upload_pdf(file_name: str, file_bytes: bytes) -> Tuple[bool, Dict, str]:
    try:
        files = {"file": (file_name, file_bytes, "application/pdf")}
        res = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60.0)
        if res.status_code == 200:
            return True, res.json(), "Success"
        error_msg = res.text
        try:
            error_msg = res.json().get("detail", error_msg)
        except Exception:
            pass
        return False, {}, error_msg
    except Exception as exc:
        return False, {}, f"Network error: {str(exc)}"


def ask_question(doc_id: str, question: str) -> Tuple[bool, Dict, str]:
    try:
        payload = {"document_id": doc_id, "question": question.strip()}
        res = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=60.0)
        if res.status_code == 200:
            return True, res.json(), "Success"
        error_msg = res.text
        try:
            error_msg = res.json().get("detail", error_msg)
        except Exception:
            pass
        return False, {}, error_msg
    except Exception as exc:
        return False, {}, f"Network error: {str(exc)}"


# -----------------------------------------------------------------------------
# PDF Utilities (PyMuPDF)
# -----------------------------------------------------------------------------
def get_pdf_total_pages(pdf_bytes: bytes) -> int:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return max(1, count)
    except Exception:
        return 1


def render_pdf_page(pdf_bytes: bytes, page_num: int) -> Optional[bytes]:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if page_num < 1 or page_num > len(doc):
            page_num = 1
        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(dpi=140)
        png = pix.tobytes("png")
        doc.close()
        return png
    except Exception:
        return None


def open_document(doc_id: str, title: str, pdf_bytes: Optional[bytes] = None):
    st.session_state.active_doc_id = doc_id
    st.session_state.active_doc_title = title

    if pdf_bytes is None:
        pdf_bytes = fetch_pdf_bytes(doc_id)

    st.session_state.active_pdf_bytes = pdf_bytes
    if pdf_bytes:
        st.session_state.pdf_total_pages = get_pdf_total_pages(pdf_bytes)
    else:
        st.session_state.pdf_total_pages = 1

    st.session_state.pdf_page_number = 1
    st.session_state.active_nav = "Workspace"
    st.rerun()


# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        # App Title & Minimal Icon
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1.25rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <span style="font-weight: 600; font-size: 0.95rem; color: #0F172A; letter-spacing: -0.01em;">DocuQuery AI</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Primary Navigation
        curr = st.session_state.active_nav

        dash_type = "primary" if curr == "Dashboard" else "secondary"
        if st.button("Dashboard", key="nav_dash", type=dash_type, use_container_width=True):
            st.session_state.active_nav = "Dashboard"
            st.rerun()

        docs_type = "primary" if curr == "Documents" else "secondary"
        if st.button("My Documents", key="nav_docs", type=docs_type, use_container_width=True):
            st.session_state.active_nav = "Documents"
            st.rerun()

        # If a document is currently active, show a subtle workspace link
        if st.session_state.active_doc_id:
            st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            st.caption("ACTIVE DOCUMENT")

            ws_type = "primary" if curr == "Workspace" else "secondary"
            doc_label = st.session_state.active_doc_title
            if len(doc_label) > 20:
                doc_label = doc_label[:18] + "..."

            if st.button(f"Workspace ({doc_label})", key="nav_ws", type=ws_type, use_container_width=True):
                st.session_state.active_nav = "Workspace"
                st.rerun()

        # Subtle Connection Indicator at the bottom
        st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        is_online = check_health()
        dot_color = "#10B981" if is_online else "#EF4444"
        status_label = "Connected" if is_online else "Disconnected"

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #64748B;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background-color: {dot_color}; display: inline-block;"></span>
                <span>Backend {status_label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------------------------------------------------------
# Screen 1: Dashboard
# -----------------------------------------------------------------------------
def render_dashboard():
    # 1. Welcome Section
    st.markdown(
        """
        <div class="welcome-box">
            <div class="welcome-badge">Grounded RAG Intelligence</div>
            <h1 class="welcome-title">Document Intelligence Dashboard</h1>
            <p class="welcome-subtitle">Upload your PDF documents to index embeddings with FAISS and ask precise questions with verified page citations using Gemini.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2-Column Balanced Layout: Left = Upload PDF, Right = Recent Documents
    col_upload, col_recent = st.columns([5, 7], gap="large")

    # ---------------------------------------------------------
    # LEFT COLUMN: PDF Upload Section
    # ---------------------------------------------------------
    with col_upload:
        st.markdown(
            """
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <span>Upload PDF Document</span>
                    </div>
                    <span class="upload-spec-tag">Max 20 MB</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        # Upload Container with visual drag & drop instruction
        st.markdown(
            """
            <div class="upload-hero">
                <div class="upload-icon-circle">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="12" y1="18" x2="12" y2="12"></line>
                        <polyline points="9 15 12 12 15 15"></polyline>
                    </svg>
                </div>
                <div class="upload-instruction">Drag and drop your PDF here</div>
                <div class="upload-subtext">Click browse below to select from your device</div>
                <span class="upload-spec-tag">Supported format: PDF</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            label_visibility="collapsed",
            help="Select a PDF document up to 20 MB."
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_size_kb = len(file_bytes) / 1024

            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.65rem 0.85rem; margin-top: 0.75rem; margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
                    <div style="font-size: 0.8rem; font-weight: 500; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 75%;">
                        📄 {uploaded_file.name}
                    </div>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">{file_size_kb:.1f} KB</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Upload and Process Document →", type="primary", use_container_width=True):
                with st.spinner("Extracting text, generating Gemini embeddings, and indexing FAISS vectors..."):
                    success, data, error = upload_pdf(uploaded_file.name, file_bytes)
                    if success:
                        new_id = data.get("document_id")
                        open_document(doc_id=new_id, title=uploaded_file.name, pdf_bytes=file_bytes)
                    else:
                        st.error(f"Upload failed: {error}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # RIGHT COLUMN: Recent Documents Section
    # ---------------------------------------------------------
    with col_recent:
        docs = fetch_documents()

        st.markdown(
            f"""
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        <span>Recent Documents</span>
                    </div>
                    <span style="font-size: 0.725rem; color: #64748B; font-weight: 500;">{len(docs)} document{'s' if len(docs) != 1 else ''}</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        if not docs:
            # Clean Empty State
            st.markdown(
                """
                <div class="empty-state-box">
                    <div class="empty-state-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                    </div>
                    <div class="empty-state-title">No documents uploaded yet</div>
                    <div class="empty-state-text">Upload your first PDF document using the panel on the left to start asking grounded questions.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for idx, doc in enumerate(docs[:7]):
                doc_id = doc.get("document_id")
                title = doc.get("title", f"Document-{doc_id[:8]}")
                total_pages = doc.get("total_pages", 1)
                total_chunks = doc.get("total_chunks", 0)
                file_size_kb = doc.get("file_size", 0) / 1024
                created = doc.get("created_at", 0)

                date_str = ""
                if created:
                    date_str = datetime.datetime.fromtimestamp(created).strftime("%b %d, %Y")

                col_item_info, col_item_btn = st.columns([4, 1.2])
                with col_item_info:
                    st.markdown(
                        f"""
                        <div class="doc-item-card" style="margin-bottom: 0;">
                            <div class="doc-item-left">
                                <div class="doc-item-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                        <polyline points="14 2 14 8 20 8"></polyline>
                                        <line x1="16" y1="13" x2="8" y2="13"></line>
                                        <line x1="16" y1="17" x2="8" y2="17"></line>
                                    </svg>
                                </div>
                                <div style="overflow: hidden;">
                                    <div class="doc-item-title" title="{title}">{title}</div>
                                    <div class="doc-item-meta">
                                        <span>{total_pages} page{'s' if total_pages != 1 else ''}</span>
                                        <span>{total_chunks} chunks</span>
                                        <span>{file_size_kb:.1f} KB</span>
                                        <span>{date_str}</span>
                                        <span class="badge-ready"><span style="width: 5px; height: 5px; border-radius: 50%; background: #059669; display: inline-block;"></span> Ready</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_item_btn:
                    st.markdown("<div style='padding-top: 0.15rem;'></div>", unsafe_allow_html=True)
                    if st.button("Open Document →", key=f"open_dash_{doc_id}_{idx}", use_container_width=True, type="secondary"):
                        open_document(doc_id=doc_id, title=title)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Screen 2: Document Workspace (Two-Panel Layout)
# -----------------------------------------------------------------------------
def render_workspace():
    doc_id = st.session_state.active_doc_id
    doc_title = st.session_state.active_doc_title or f"Document-{doc_id[:8]}"

    if not doc_id:
        st.info("No document currently active.")
        if st.button("Go to Dashboard", type="primary"):
            st.session_state.active_nav = "Dashboard"
            st.rerun()
        return

    # Load PDF bytes if missing
    if st.session_state.active_pdf_bytes is None:
        with st.spinner("Loading document..."):
            st.session_state.active_pdf_bytes = fetch_pdf_bytes(doc_id)
            if st.session_state.active_pdf_bytes:
                st.session_state.pdf_total_pages = get_pdf_total_pages(st.session_state.active_pdf_bytes)

    pdf_bytes = st.session_state.active_pdf_bytes
    total_pages = st.session_state.pdf_total_pages

    # Workspace Top Bar
    col_info, col_close = st.columns([4, 1.2])
    with col_info:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 1.15rem; font-weight: 600; color: #0F172A; display: flex; align-items: center; gap: 8px;">
                    <span>{doc_title}</span>
                    <span class="badge-ready"><span style="width: 5px; height: 5px; border-radius: 50%; background: #059669; display: inline-block;"></span> Ready</span>
                </div>
                <div style="font-size: 0.775rem; color: #64748B; margin-top: 0.15rem;">
                    ID: <code>{doc_id}</code> &nbsp;•&nbsp; {total_pages} page{'s' if total_pages != 1 else ''}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_close:
        if st.button("← Back to Dashboard", type="secondary", use_container_width=True):
            st.session_state.active_nav = "Dashboard"
            st.rerun()

    st.markdown("<hr style='margin: 0.25rem 0 1.25rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Two-Panel Layout
    col_pdf, col_chat = st.columns([1, 1], gap="medium")

    # ---------------------------------------------------------
    # LEFT PANEL: PDF Viewer
    # ---------------------------------------------------------
    with col_pdf:
        st.markdown("<div style='font-size: 0.875rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;'>PDF Viewer</div>", unsafe_allow_html=True)

        if not pdf_bytes:
            st.error("Unable to load document bytes from backend.")
        else:
            curr_page = st.session_state.pdf_page_number

            col_p, col_ind, col_n, col_dl = st.columns([1, 1.5, 1, 1.5])
            with col_p:
                if st.button("◀ Prev", key="btn_prev", use_container_width=True, type="secondary", disabled=(curr_page <= 1)):
                    st.session_state.pdf_page_number = max(1, curr_page - 1)
                    st.rerun()

            with col_ind:
                page_sel = st.number_input(
                    "Page",
                    min_value=1,
                    max_value=max(1, total_pages),
                    value=curr_page,
                    step=1,
                    label_visibility="collapsed",
                    key="sel_page"
                )
                if page_sel != curr_page:
                    st.session_state.pdf_page_number = page_sel
                    st.rerun()

            with col_n:
                if st.button("Next ▶", key="btn_next", use_container_width=True, type="secondary", disabled=(curr_page >= total_pages)):
                    st.session_state.pdf_page_number = min(total_pages, curr_page + 1)
                    st.rerun()

            with col_dl:
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"{doc_title if doc_title.endswith('.pdf') else doc_title + '.pdf'}",
                    mime="application/pdf",
                    use_container_width=True,
                    type="secondary"
                )

            st.caption(f"Page {st.session_state.pdf_page_number} of {total_pages}")

            # Render Page
            page_png = render_pdf_page(pdf_bytes, st.session_state.pdf_page_number)
            if page_png:
                st.image(page_png, use_container_width=True)

    # ---------------------------------------------------------
    # RIGHT PANEL: AI Chat
    # ---------------------------------------------------------
    with col_chat:
        st.markdown("<div style='font-size: 0.875rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;'>AI Assistant</div>", unsafe_allow_html=True)

        if doc_id not in st.session_state.chat_history:
            st.session_state.chat_history[doc_id] = []

        history = st.session_state.chat_history[doc_id]

        if not history:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 6px; padding: 2rem 1.5rem; text-align: center; color: #64748B; margin-bottom: 1rem; font-size: 0.85rem;">
                    Ask questions about this document below.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for msg_idx, message in enumerate(history):
                role = message.get("role")
                content = message.get("content", "")
                sources = message.get("sources", [])

                if role == "user":
                    st.markdown(
                        f"""
                        <div class="chat-user-row">
                            <div class="chat-user-bubble">{content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-assistant-bubble">
                            <div class="chat-assistant-header">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"></path>
                                    <rect x="3" y="8" width="18" height="12" rx="2"></rect>
                                </svg>
                                <span>AI Assistant</span>
                            </div>
                            <div>{content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Copy answer popover
                    with st.popover("Copy Answer"):
                        st.text_area("Answer Text", value=content, height=120, label_visibility="collapsed")

                    # Sources list
                    if sources:
                        with st.expander(f"Sources ({len(sources)})", expanded=False):
                            for s_idx, src in enumerate(sources):
                                page_no = src.get("page_number", 1)
                                score = src.get("score")
                                text_snippet = src.get("text", "").strip()

                                score_text = f"<span class='badge-score'>{score:.1%}</span>" if score is not None else ""

                                col_s_text, col_s_btn = st.columns([3, 1.2])
                                with col_s_text:
                                    st.markdown(
                                        f"""
                                        <div class="source-item">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                                <span class="badge-source">Page {page_no}</span>
                                                {score_text}
                                            </div>
                                            <div style="font-size: 0.75rem; color: #475569; line-height: 1.4;">
                                                "{text_snippet[:220]}..."
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                with col_s_btn:
                                    if st.button(f"Go to P.{page_no}", key=f"jump_{msg_idx}_{s_idx}", type="secondary"):
                                        st.session_state.pdf_page_number = page_no
                                        st.rerun()

        # Chat Input
        prompt = st.chat_input("Ask a question about this document...")
        if prompt:
            clean_q = prompt.strip()
            if clean_q:
                # Append user query
                st.session_state.chat_history[doc_id].append({
                    "role": "user",
                    "content": clean_q,
                    "timestamp": time.time()
                })

                with st.spinner("Thinking..."):
                    success, res_data, err_msg = ask_question(doc_id, clean_q)
                    if success:
                        answer = res_data.get("answer", "No answer received.")
                        sources = res_data.get("sources", [])
                        st.session_state.chat_history[doc_id].append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "timestamp": time.time()
                        })
                        st.rerun()
                    else:
                        st.error(f"Error answering question: {err_msg}")


# -----------------------------------------------------------------------------
# Screen 3: My Documents (Library View)
# -----------------------------------------------------------------------------
def render_documents():
    st.markdown(
        """
        <div class="welcome-box">
            <div class="welcome-badge">Repository</div>
            <h1 class="welcome-title">My Documents</h1>
            <p class="welcome-subtitle">Persistent library of indexed PDF documents ready for retrieval.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    docs = fetch_documents()

    if not docs:
        st.markdown(
            """
            <div class="empty-state-box">
                <div class="empty-state-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                </div>
                <div class="empty-state-title">No documents in library yet</div>
                <div class="empty-state-text">Upload your first PDF document from the Dashboard to build the vector library.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Go to Dashboard", type="primary"):
            st.session_state.active_nav = "Dashboard"
            st.rerun()
        return

    # Filter
    query = st.text_input("Filter documents", placeholder="Search documents by title...", label_visibility="collapsed")
    filtered = docs
    if query:
        q = query.lower().strip()
        filtered = [d for d in docs if q in d.get("title", "").lower() or q in d.get("document_id", "").lower()]

    st.caption(f"{len(filtered)} document{'s' if len(filtered) != 1 else ''} available")

    for idx, doc in enumerate(filtered):
        doc_id = doc.get("document_id")
        title = doc.get("title", f"Document-{doc_id[:8]}")
        total_pages = doc.get("total_pages", 1)
        total_chunks = doc.get("total_chunks", 0)
        file_size_kb = doc.get("file_size", 0) / 1024
        created = doc.get("created_at", 0)

        date_str = ""
        if created:
            date_str = datetime.datetime.fromtimestamp(created).strftime("%Y-%m-%d")

        col_card, col_action = st.columns([4, 1.2])
        with col_card:
            st.markdown(
                f"""
                <div class="doc-item-card">
                    <div class="doc-item-left">
                        <div class="doc-item-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                            </svg>
                        </div>
                        <div>
                            <div class="doc-item-title">{title}</div>
                            <div class="doc-item-meta">
                                <span>{total_pages} page{'s' if total_pages != 1 else ''}</span>
                                <span>{total_chunks} chunks</span>
                                <span>{file_size_kb:.1f} KB</span>
                                <span>{date_str}</span>
                                <span class="badge-ready"><span style="width: 5px; height: 5px; border-radius: 50%; background: #059669; display: inline-block;"></span> Ready</span>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_action:
            st.markdown("<div style='padding-top: 0.15rem;'></div>", unsafe_allow_html=True)
            if st.button("Open Document →", key=f"open_lib_{doc_id}_{idx}", use_container_width=True, type="secondary"):
                open_document(doc_id=doc_id, title=title)


# -----------------------------------------------------------------------------
# Main Application Router
# -----------------------------------------------------------------------------
def main():
    render_sidebar()

    nav = st.session_state.active_nav

    if nav == "Dashboard":
        render_dashboard()
    elif nav == "Documents":
        render_documents()
    elif nav == "Workspace":
        render_workspace()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
