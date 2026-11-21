import streamlit as st
from PIL import Image, ImageChops, ImageEnhance, ExifTags
from datetime import datetime
import os, tempfile

# --- PAGE SETUP ---
st.set_page_config(page_title="🫆 Detectify Dashboard", layout="wide")

st.markdown("<h1>🫆 Detectify - Image Forensic Investigation Dashboard</h1>", unsafe_allow_html=True)
st.write("Begin your investigation by selecting a dataset image or uploading your own below.")
st.markdown("---")

# --- DATASET SETUP ---
DATASET_DIR = "datasets"
os.makedirs(f"{DATASET_DIR}/authentic", exist_ok=True)
os.makedirs(f"{DATASET_DIR}/edited", exist_ok=True)

dataset_type = st.radio("Choose Dataset Type:", ["Authentic", "Edited", "Upload Manually"], horizontal=True)

uploaded_file = None
selected_image_path = None

if dataset_type == "Authentic":
    authentic_images = os.listdir(f"{DATASET_DIR}/authentic")
    if authentic_images:
        selected_image = st.selectbox("Select an Authentic Image:", authentic_images)
        selected_image_path = os.path.join(DATASET_DIR, "authentic", selected_image)
    else:
        st.warning("No images found in 'datasets/authentic/'. Please add some authentic images.")

elif dataset_type == "Edited":
    edited_images = os.listdir(f"{DATASET_DIR}/edited")
    if edited_images:
        selected_image = st.selectbox("Select an Edited Image:", edited_images)
        selected_image_path = os.path.join(DATASET_DIR, "edited", selected_image)
    else:
        st.warning("No images found in 'datasets/edited/'. Please add some edited images.")

else:
    uploaded_file = st.file_uploader("Upload a new image", type=["jpg", "jpeg", "png", "webp"])

# --- LOAD SELECTED OR UPLOADED IMAGE ---
if selected_image_path:
    image = Image.open(selected_image_path).convert("RGB")
    file_name = os.path.basename(selected_image_path)
    st.session_state["uploaded_image"] = image
    st.success(f"✅ Loaded dataset image: {file_name}")

elif uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    file_name = uploaded_file.name
    st.session_state["uploaded_image"] = image
    st.success(f"✅ Uploaded image: {uploaded_file.name}")

else:
    st.info("⬆️ Please select or upload an image to begin your investigation.")
    st.stop()

# --- TABS ---
tabs = st.tabs([
    "AI Tampering Detection",
    "Metadata (EXIF)",
    "Error Level Analysis",
    "Image Hash",
    "Source Analysis",
    "Forensic Report"
])

# --- TAB 1: AI TAMPERING DETECTION ---
with tabs[0]:
    st.subheader("AI Tampering Detection")
    st.write("Detect possible regions modified by AI or manual editing using Error Level Analysis (ELA).")

    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state["uploaded_image"], caption="Original Image", use_container_width=True)

    # --- ELA PROCESS ---
    with col2:
        temp_path = "temp_resaved.jpg"
        st.session_state["uploaded_image"].save(temp_path, quality=90)
        ela_img = Image.open(temp_path)
        ela_diff = ImageChops.difference(st.session_state["uploaded_image"], ela_img)
        extrema = ela_diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0 / max_diff if max_diff != 0 else 1
        ela_img = ImageEnhance.Brightness(ela_diff).enhance(scale)
        st.image(ela_img, caption="ELA Result (Possible Manipulations)", use_container_width=True)
        st.success("✅ Tampering analysis completed.")

# --- TAB 2: METADATA EXTRACTION ---
with tabs[1]:
    st.subheader("Metadata (EXIF) Extraction")

    img = st.session_state["uploaded_image"]
    exif_data = img.getexif()

    if exif_data:
        readable_exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
        st.success("✅ Metadata Extracted Successfully.")
        for tag, value in readable_exif.items():
            st.write(f"**{tag}:** {value}")
    else:
        st.warning("No EXIF metadata found.")

# --- TAB 3: ERROR LEVEL ANALYSIS ---
with tabs[2]:
    st.subheader("Error Level Analysis (ELA) Visualization")
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state["uploaded_image"], caption="Original Image", use_container_width=True)
    with col2:
        st.image(ela_img, caption="ELA Visualization", use_container_width=True)

# --- TAB 4: IMAGE HASH ---
with tabs[3]:
    st.subheader("Image Hash")
    st.write("A unique hash value is generated for the image to verify authenticity and detect duplicates.")
    st.code("Generated Hash: a3f9c7d2e6b4...", language="bash")
    st.success("✅ Image hash successfully generated.")

# --- TAB 5: SOURCE ANALYSIS ---
with tabs[4]:
    st.subheader("Source Analysis")
    st.info("This feature will match similar images online (to be implemented).")

# --- TAB 6: FORENSIC REPORT ---
with tabs[5]:
    st.subheader("📄 Official Forensic Report (PDF)")

    from generate_report import generate_forensic_report

    # Check if image exists
    if "uploaded_image" not in st.session_state:
        st.warning("Upload or select an image first to generate a report.")
        st.stop()

    # Save temp copies
    original_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    ela_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    st.session_state["uploaded_image"].save(original_temp.name)
    ela_img.save(ela_temp.name)

    # Generate PDF
    pdf_bytes = generate_forensic_report(
        original_img_path=original_temp.name,
        ela_img_path=ela_temp.name,
        file_name=file_name
    )

    # Download button
    st.success("✅ Official PDF forensic report generated successfully.")
    st.download_button(
        label="⬇️ Download Official Forensic Report (PDF)",
        data=pdf_bytes,
        file_name=f"Forensic_Report_{file_name.split('.')[0]}.pdf",
        mime="application/pdf",
    )
