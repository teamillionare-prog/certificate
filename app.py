
import io
import zipfile
from typing import Dict, Tuple, List

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Certificate Generator", page_icon="🏅", layout="wide")

st.title("🏅 Certificate Generator")
st.write("Upload a single **template image** (PNG/JPG)** and a **CSV/Excel** file of recipients. Place text fields, preview, and export all certificates as PNG or PDF.")

with st.expander("1) Upload files", expanded=True):
    tpl_file = st.file_uploader("Template image (.png or .jpg)", type=["png", "jpg", "jpeg"])
    data_file = st.file_uploader("Recipients list (.csv or .xlsx)", type=["csv", "xlsx"])
    font_file = st.file_uploader("Optional font (.ttf, .otf)", type=["ttf", "otf"])

@st.cache_data
def load_data(data_file):
    if data_file is None:
        return None
    if data_file.name.lower().endswith(".csv"):
        return pd.read_csv(data_file)
    else:
        return pd.read_excel(data_file)

def load_template(img_file):
    if img_file is None:
        return None
    img = Image.open(img_file).convert("RGBA")
    return img

def get_font(font_file, size):
    try:
        if font_file is not None:
            return ImageFont.truetype(font_file, size=size)
        # Attempt to use a common default font (works in many Linux/Streamlit envs)
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()

def draw_multiline_center(draw, text, xy, font, fill, max_width):
    # Manual wrapping for long names/fields to stay within width
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        tw, th = draw.textsize(test, font=font)
        if tw <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    total_h = sum([draw.textsize(l, font=font)[1] for l in lines]) + (len(lines)-1)*6
    x, y = xy
    cursor_y = y - total_h/2
    for l in lines:
        tw, th = draw.textsize(l, font=font)
        draw.text((x - tw/2, cursor_y), l, font=font, fill=fill)
        cursor_y += th + 6

# Sidebar: field configuration
st.sidebar.header("Field settings")
st.sidebar.write("Define up to 4 text fields and their positions. Use the preview to fine‑tune.")
default_fields = [
    {"label": "Name", "text": "{Name}", "x": 827, "y": 470, "size": 64, "color": "#333333", "max_width": 900, "centered": True, "bold": True},
    {"label": "Course", "text": "{Course}", "x": 827, "y": 660, "size": 44, "color": "#444444", "max_width": 900, "centered": True, "bold": False},
    {"label": "Date", "text": "Date: {Date}", "x": 500, "y": 930, "size": 32, "color": "#444444", "max_width": 600, "centered": False, "bold": False},
    {"label": "Custom", "text": "", "x": 827, "y": 820, "size": 36, "color": "#444444", "max_width": 900, "centered": True, "bold": False},
]

num_fields = st.sidebar.slider("How many fields?", 1, 4, 3)
field_cfgs: List[Dict] = []

for i in range(num_fields):
    f = default_fields[i].copy()
    with st.sidebar.expander(f"Field {i+1}: {f['label']}", expanded=(i==0)):
        f["label"] = st.text_input(f"Label {i+1}", f["label"], key=f"label{i}")
        f["text"] = st.text_input("Text (you can reference columns like {Name} or {Course})", f["text"], key=f"text{i}")
        col1, col2 = st.columns(2)
        f["x"] = col1.number_input("X position", value=f["x"], step=5, key=f"x{i}")
        f["y"] = col2.number_input("Y position", value=f["y"], step=5, key=f"y{i}")
        f["size"] = st.number_input("Font size", value=f["size"], step=2, key=f"size{i}")
        f["color"] = st.color_picker("Color", value=f["color"], key=f"color{i}")
        col3, col4 = st.columns(2)
        f["max_width"] = col3.number_input("Max text width (px) for wrapping/centering", value=f["max_width"], step=20, key=f"mw{i}")
        f["centered"] = col4.checkbox("Center this field", value=f["centered"], key=f"center{i}")
        f["bold"] = st.checkbox("Use bold font (if available)", value=f["bold"], key=f"bold{i}")
    field_cfgs.append(f)

# Load files
tpl_img = load_template(tpl_file) if tpl_file else None
data = load_data(data_file) if data_file else None

colA, colB = st.columns([3,2])

with colA:
    st.subheader("2) Preview")
    if tpl_img is None:
        st.info("Upload a template image to start. You can also try with the sample files in the download bundle.")
    else:
        # Row selection
        if data is not None:
            st.write("Select a sample row for preview:")
            idx = st.number_input("Row index (1 = first row)", min_value=1, max_value=len(data), value=1)
            row = data.iloc[idx-1].to_dict()
        else:
            row = {"Name": "Sample Name", "Course": "Sample Course", "Date": "2025-08-12"}

        preview = tpl_img.copy()
        draw = ImageDraw.Draw(preview)

        for f in field_cfgs:
            txt = f["text"].format(**{k:str(v) for k,v in row.items()})
            size = int(f["size"])
            # Font selection
            font = None
            if f["bold"] and font_file is not None:
                try:
                    font = ImageFont.truetype(font_file, size=size)
                except:
                    font = None
            if font is None:
                font = get_font(font_file, size)

            if f["centered"]:
                draw_multiline_center(draw, txt, (int(f["x"]), int(f["y"])), font, f["color"], int(f["max_width"]))
            else:
                draw.text((int(f["x"]), int(f["y"])), txt, fill=f["color"], font=font)

        st.image(preview, caption="Live preview", use_container_width=True)

with colB:
    st.subheader("3) Export")
    fmt = st.selectbox("Output format", ["PNG (images)", "PDF (one per certificate)"])
    btn = st.button("Generate for all rows", type="primary", disabled=(tpl_img is None or data is None))

    if btn:
        if data is None:
            st.error("Please upload a recipients file.")
        else:
            buf = io.BytesIO()
            zf = zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED)

            for i, r in data.iterrows():
                img = tpl_img.copy()
                d = ImageDraw.Draw(img)

                # Draw every configured field
                for f in field_cfgs:
                    txt = f["text"].format(**{k:str(v) for k,v in r.items()})
                    size = int(f["size"])
                    font = None
                    if f["bold"] and font_file is not None:
                        try:
                            font = ImageFont.truetype(font_file, size=size)
                        except:
                            font = None
                    if font is None:
                        font = get_font(font_file, size)

                    if f["centered"]:
                        # Use wrapping + center
                        draw_multiline_center(d, txt, (int(f["x"]), int(f["y"])), font, f["color"], int(f["max_width"]))
                    else:
                        d.text((int(f["x"]), int(f["y"])), txt, fill=f["color"], font=font)

                name_part = str(r.get("Name", f"row{i+1}")).strip().replace("/", "-")
                if fmt.startswith("PNG"):
                    out_name = f"certificates/{name_part}.png"
                    # Ensure folder path inside zip
                    zf.writestr(out_name, b"")  # placeholder to ensure dir exists in some zip tools
                    # Save image bytes
                    img_bytes = io.BytesIO()
                    img.convert("RGB").save(img_bytes, format="PNG", optimize=True)
                    zf.writestr(out_name, img_bytes.getvalue())
                else:
                    out_name = f"certificates/{name_part}.pdf"
                    pdf_bytes = io.BytesIO()
                    img_rgb = img.convert("RGB")
                    img_rgb.save(pdf_bytes, format="PDF")
                    zf.writestr(out_name, pdf_bytes.getvalue())

            zf.close()
            buf.seek(0)
            st.download_button("Download ZIP of certificates", data=buf, file_name="certificates.zip", mime="application/zip")
            st.success("Done! Your ZIP is ready to download.")

st.markdown("---")
st.caption("Tip: Use {ColumnName} in the field text to pull values from your CSV/Excel columns. Example: '**Awarded to {Name} for {Course}**'.")
