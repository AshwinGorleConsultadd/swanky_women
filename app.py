# import streamlit as st
# import tempfile
# import os
# import shutil
# import base64
# from main import generate_techpack

# # Page configuration
# st.set_page_config(
#     page_title="Swanky Tech Pack Generator",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Constants
# LOGO_PATH = "assets/brand_logo.png"

# # Enhanced styling for light theme
# st.markdown("""
# <style>
#     /* Global styles */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
#     body {
#         font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
#     }
    
#     /* Main container */
#     .main {
#         padding: 2rem;
#         background: linear-gradient(135deg, #f8f9ff 0%, #fff5f7 100%);
#     }
    
#     /* Section styling with light theme */
#     .section {
#         padding: 28px;
#         border-radius: 20px;
#         background: rgba(255, 255, 255, 0.95);
#         backdrop-filter: blur(20px);
#         border: 1px solid rgba(124, 58, 237, 0.08);
#         margin-bottom: 1.5rem;
#         box-shadow: 0 8px 32px rgba(124, 58, 237, 0.06);
#     }
    
#     /* Button styling */
#     .stButton > button {
#         background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
#         color: white;
#         border: none;
#         padding: 14px 32px;
#         border-radius: 14px;
#         font-weight: 600;
#         font-size: 16px;
#         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
#         box-shadow: 0 8px 24px rgba(124, 58, 237, 0.25);
#         width: 100%;
#         letter-spacing: 0.3px;
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 12px 32px rgba(124, 58, 237, 0.35);
#         background: linear-gradient(135deg, #6d28d9 0%, #9333ea 100%);
#     }
    
#     .stButton > button:active {
#         transform: translateY(-1px);
#     }
    
#     /* Upload area styling */
#     [data-testid="stFileUploader"] {
#         border: 2px dashed rgba(124, 58, 237, 0.2);
#         padding: 28px;
#         border-radius: 18px;
#         background: linear-gradient(135deg, rgba(124, 58, 237, 0.03), rgba(168, 85, 247, 0.02));
#         transition: all 0.3s ease;
#     }
    
#     [data-testid="stFileUploader"]:hover {
#         border-color: rgba(124, 58, 237, 0.4);
#         background: linear-gradient(135deg, rgba(124, 58, 237, 0.05), rgba(168, 85, 247, 0.04));
#         box-shadow: 0 4px 16px rgba(124, 58, 237, 0.08);
#     }
    
#     /* Text area styling */
#     .stTextArea textarea {
#         background: rgba(255, 255, 255, 0.9);
#         border: 2px solid rgba(124, 58, 237, 0.15);
#         border-radius: 14px;
#         color: #1f2937;
#         padding: 16px;
#         font-size: 15px;
#         font-family: 'Inter', sans-serif;
#         transition: all 0.3s ease;
#     }
    
#     .stTextArea textarea:focus {
#         border-color: rgba(124, 58, 237, 0.5);
#         box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
#         background: white;
#     }
    
#     .stTextArea textarea::placeholder {
#         color: rgba(31, 41, 55, 0.4);
#     }
    
#     /* Header styling */
#     h1 {
#         color: #1f2937;
#         font-weight: 800;
#         font-size: 2.5rem;
#         margin-bottom: 0.5rem;
#         background: linear-gradient(135deg, #7c3aed, #ec4899);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text;
#     }
    
#     h2 {
#         color: #374151;
#         font-size: 1.5rem;
#         margin-top: 1.8rem;
#         margin-bottom: 0.8rem;
#         font-weight: 700;
#     }
    
#     h3 {
#         color: #4b5563;
#         font-weight: 600;
#     }
    
#     /* Divider styling */
#     hr {
#         border: none;
#         height: 2px;
#         background: linear-gradient(
#             90deg,
#             transparent,
#             rgba(124, 58, 237, 0.2),
#             transparent
#         );
#         margin: 2.5rem 0;
#     }
    
#     /* Download button */
#     .stDownloadButton > button {
#         background: linear-gradient(135deg, #10b981 0%, #059669 100%);
#         color: white;
#         border: none;
#         padding: 12px 28px;
#         border-radius: 12px;
#         font-weight: 600;
#         margin-bottom: 1.5rem;
#         box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
#         transition: all 0.3s ease;
#     }
    
#     .stDownloadButton > button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 8px 28px rgba(16, 185, 129, 0.35);
#     }
    
#     /* Status messages */
#     .stAlert {
#         border-radius: 14px;
#         border-left: 4px solid;
#         box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
#     }
    
#     /* Success alert */
#     [data-baseweb="notification"] [kind="success"] {
#         background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
#         border-left-color: #10b981;
#     }
    
#     /* Info alert */
#     [data-baseweb="notification"] [kind="info"] {
#         background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
#         border-left-color: #3b82f6;
#     }
    
#     /* Warning alert */
#     [data-baseweb="notification"] [kind="warning"] {
#         background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
#         border-left-color: #f59e0b;
#     }
    
#     /* Error alert */
#     [data-baseweb="notification"] [kind="error"] {
#         background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
#         border-left-color: #ef4444;
#     }
    
#     /* Caption styling */
#     .caption {
#         text-align: center;
#         color: rgba(107, 114, 128, 0.7);
#         font-size: 0.95rem;
#         margin-top: 3rem;
#         font-weight: 500;
#     }
    
#     /* Card effect for columns */
#     [data-testid="column"] > div {
#         background: rgba(255, 255, 255, 0.6);
#         padding: 2rem;
#         border-radius: 24px;
#         box-shadow: 0 8px 32px rgba(124, 58, 237, 0.08);
#         border: 1px solid rgba(124, 58, 237, 0.06);
#     }
    
#     /* Helper text styling */
#     .helper-text {
#         color: #6b7280;
#         font-size: 0.95rem;
#         margin-bottom: 1.2rem;
#         line-height: 1.6;
#     }
    
#     /* Badge styling for file count */
#     .file-badge {
#         display: inline-block;
#         background: linear-gradient(135deg, #10b981, #059669);
#         color: white;
#         padding: 6px 16px;
#         border-radius: 20px;
#         font-size: 0.9rem;
#         font-weight: 600;
#         box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
#     }
    
#     /* PDF preview container */
#     .pdf-preview {
#         border-radius: 16px;
#         overflow: hidden;
#         box-shadow: 0 12px 40px rgba(124, 58, 237, 0.15);
#         border: 2px solid rgba(124, 58, 237, 0.1);
#     }
# </style>
# """, unsafe_allow_html=True)

# # Layout
# col1, col2 = st.columns([2, 3], gap="large")

# # Left column - Input section
# with col1:
#     # Logo and header
#     if os.path.exists(LOGO_PATH):
#         st.image(LOGO_PATH, width=150)
    
#     st.markdown("# 🎨 Swanky Tech Pack Studio")
#     st.markdown("""
#         <p class='helper-text'>
#             Upload garment images and provide context to generate 
#             professional tech pack PDFs instantly.
#         </p>
#     """, unsafe_allow_html=True)
    
#     # Image upload section
#     st.markdown("## 📸 Upload Garment Images")
#     st.markdown(
#         "<p class='helper-text'>"
#         "Upload front and back views • Drag & drop supported</p>",
#         unsafe_allow_html=True
#     )
    
#     uploaded_images = st.file_uploader(
#         "Upload images",
#         type=["png", "jpg", "jpeg"],
#         accept_multiple_files=True,
#         help="Upload front and back garment images for best results",
#         label_visibility="collapsed"
#     )
    
#     # Show uploaded file count with badge
#     if uploaded_images:
#         st.markdown(
#             f"<span class='file-badge'>✓ {len(uploaded_images)} image(s) uploaded</span>",
#             unsafe_allow_html=True
#         )
    
#     st.markdown("---")
    
#     # Context input section
#     st.markdown("## 📝 Specification Context")
#     st.markdown(
#         "<p class='helper-text'>"
#         "Provide design brief, measurements, or special requirements</p>",
#         unsafe_allow_html=True
#     )
    
#     input_context = st.text_area(
#         "Enter context",
#         height=220,
#         placeholder="Example: Cotton blend fabric, relaxed fit, contrast stitching on seams, ribbed crew neck...",
#         label_visibility="collapsed"
#     )
    
#     st.markdown("---")
    
#     # Generate button
#     generate_btn = st.button("🚀 Generate Tech Pack PDF", type="primary")

# # Right column - Preview section
# with col2:
#     preview_container = st.container()
#     status_container = st.container()

# # Generation logic
# if generate_btn:
#     if not uploaded_images:
#         st.warning("⚠️ Please upload at least one garment image to continue.")
#     else:
#         tmpdir = None
#         try:
#             # Save uploaded files
#             with st.spinner('📤 Preparing uploads...'):
#                 tmpdir = tempfile.mkdtemp(prefix='swanky_')
#                 saved_paths = []
                
#                 for idx, uploaded_file in enumerate(uploaded_images):
#                     ext = os.path.splitext(uploaded_file.name)[1]
#                     dest_path = os.path.join(tmpdir, f"img_{idx}{ext}")
                    
#                     with open(dest_path, "wb") as f:
#                         f.write(uploaded_file.getbuffer())
                    
#                     saved_paths.append(dest_path)
            
#             # Generate tech pack
#             with status_container:
#                 st.info("⚙️ Analyzing images and generating tech pack — this may take a minute...")
            
#             with st.spinner('🎨 Creating your professional tech pack...'):
#                 pdf_path = generate_techpack(saved_paths, input_context)
            
#             # Display results
#             if pdf_path and os.path.exists(pdf_path):
#                 with status_container:
#                     st.success("✅ Tech pack generated successfully!")
                
#                 with open(pdf_path, "rb") as f:
#                     pdf_bytes = f.read()
                
#                 with preview_container:
#                     st.markdown("## 📄 Your Tech Pack")
                    
#                     # Download button
#                     st.download_button(
#                         label="⬇️ Download Tech Pack PDF",
#                         data=pdf_bytes,
#                         file_name=os.path.basename(pdf_path),
#                         mime="application/pdf"
#                     )
                    
#                     # PDF preview
#                     try:
#                         b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
#                         pdf_display = f'''
#                             <div class="pdf-preview">
#                                 <iframe 
#                                     src="data:application/pdf;base64,{b64_pdf}" 
#                                     width="100%" 
#                                     height="700px" 
#                                     type="application/pdf"
#                                     style="border: none;">
#                                 </iframe>
#                             </div>
#                         '''
#                         st.markdown(pdf_display, unsafe_allow_html=True)
#                     except Exception as e:
#                         st.info(f"💾 PDF saved to: {os.path.abspath(pdf_path)}")
#             else:
#                 with status_container:
#                     st.error("❌ PDF generation failed. Please check the logs and try again.")
        
#         except Exception as e:
#             with status_container:
#                 st.error(f"❌ Generation error: {str(e)}")
        
#         finally:
#             # Cleanup temporary files
#             if tmpdir and os.path.exists(tmpdir):
#                 try:
#                     shutil.rmtree(tmpdir)
#                 except Exception:
#                     pass

# # Footer
# st.markdown("\n\n")
# st.markdown("---")
# st.markdown(
#     "<div class='caption'>Built with care ✨ — Swanky Tech Pack Generator</div>",
#     unsafe_allow_html=True
# )
import streamlit as st
import tempfile
import os
import shutil
import base64
from datetime import datetime
from main import generate_techpack
import streamlit.components.v1 as components


# -----------------------------
# Configuration
# -----------------------------

st.set_page_config(
    page_title="Swanky Tech Pack Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOGO_PATH = "assets/brand_logo.png"
PUBLIC_UPLOAD_DIR = "public/uploads"


# -----------------------------
# Helpers
# -----------------------------

def save_images_to_public(uploaded_images):
    """
    Saves uploaded images to public/uploads and returns file paths
    """
    os.makedirs(PUBLIC_UPLOAD_DIR, exist_ok=True)
    saved_paths = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for idx, uploaded_file in enumerate(uploaded_images):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        safe_name = uploaded_file.name.replace(" ", "_")
        filename = f"{timestamp}_{idx}_{safe_name}"
        dest_path = os.path.join(PUBLIC_UPLOAD_DIR, filename)

        with open(dest_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        saved_paths.append(dest_path)

    return saved_paths


# -----------------------------
# Styling
# -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body { font-family: 'Inter', sans-serif; }

.main {
    padding: 2rem;
    background: linear-gradient(135deg, #f8f9ff 0%, #fff5f7 100%);
}

.section {
    padding: 28px;
    border-radius: 20px;
    background: white;
    border: 1px solid rgba(124, 58, 237, 0.08);
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.06);
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white;
    border-radius: 14px;
    padding: 14px 32px;
    font-weight: 600;
    width: 100%;
}

.file-badge {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Layout
# -----------------------------

col1, col2 = st.columns([2, 3], gap="large")

# -----------------------------
# Left Column (Inputs)
# -----------------------------

with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)

    st.markdown("# 🎨 Swanky Tech Pack Studio")
    st.markdown(
        "<p>Upload garment images and generate professional tech packs.</p>",
        unsafe_allow_html=True
    )

    st.markdown("## 📸 Upload Garment Images")

    uploaded_images = st.file_uploader(
        "Upload images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_images:
        st.markdown(
            f"<span class='file-badge'>✓ {len(uploaded_images)} image(s) uploaded</span>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("## 📝 Specification Context")

    input_context = st.text_area(
        "Enter context",
        height=220,
        placeholder="Fabric, fit, measurements, trims, construction notes...",
        label_visibility="collapsed"
    )

    st.markdown("---")

    generate_btn = st.button("🚀 Generate Tech Pack PDF", type="primary")


# -----------------------------
# Right Column (Output)
# -----------------------------

with col2:
    preview_container = st.container()
    status_container = st.container()


# -----------------------------
# Generation Logic
# -----------------------------

if generate_btn:
    if not uploaded_images:
        st.warning("⚠️ Please upload at least one garment image.")
    else:
        try:
            # with st.spinner("📤 Saving images to public folder..."):
            #     saved_paths = save_images_to_public(uploaded_images)

            # with status_container:
            #     st.info("⚙️ Analyzing images and generating tech pack...")

            # with st.spinner("🎨 Creating tech pack..."):
            #     pdf_path = generate_techpack(saved_paths, input_context)

            pdf_path = "Tech_Pack.pdf"
            if pdf_path and os.path.exists(pdf_path):
                with status_container:
                    st.success("✅ Tech pack generated successfully!")
                

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                with preview_container:
                    st.markdown("## 📄 Your Tech Pack")

                    st.download_button(
                        label="⬇️ Download Tech Pack PDF",
                        data=pdf_bytes,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )

                    try:
                        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

                        components.html(
                            f"""
                            <html>
                                <head>
                                    <style>
                                        body {{
                                            margin: 0;
                                            background: #f9fafb;
                                        }}
                                        .pdf-wrapper {{
                                            width: 100%;
                                            height: 90vh;
                                            padding: 12px;
                                            box-sizing: border-box;
                                        }}
                                        iframe {{
                                            width: 100%;
                                            height: 100%;
                                            border: none;
                                            border-radius: 12px;
                                            background: white;
                                        }}
                                    </style>
                                </head>
                                <body>
                                    <div class="pdf-wrapper">
                                        <iframe
                                            src="data:application/pdf;base64,{b64_pdf}#toolbar=1&navpanes=0&scrollbar=1">
                                        </iframe>
                                    </div>
                                </body>
                            </html>
                            """,
                            height=900,
                        )

                    except Exception:
                        st.info(f"PDF saved at: {os.path.abspath(pdf_path)}")

            else:
                st.error("❌ PDF generation failed.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# -----------------------------
# Footer
# -----------------------------

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6b7280;'>Built with care ✨ — Swanky Tech Pack Generator</div>",
    unsafe_allow_html=True
)
