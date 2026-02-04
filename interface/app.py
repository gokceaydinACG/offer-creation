"""
Offer Creation Tool - Main Application

Clean, modular Streamlit interface for converting supplier offers.
"""

import streamlit as st
import tempfile
from pathlib import Path

from styles import get_custom_css
from components import (
    render_header,
    render_department_selector,
    render_file_uploader,
    render_process_button,
    render_success_message,
    render_selectable_table,
    render_product_image_uploader,
    render_download_buttons,
    render_reset_button,
)
from processor import process_uploaded_file


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Offer Creator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# APPLY STYLES
# ============================================================================
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "processed" not in st.session_state:
    st.session_state.processed = False
if "output_path" not in st.session_state:
    st.session_state.output_path = None
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_df" not in st.session_state:
    st.session_state.selected_df = None
if "row_selected" not in st.session_state:
    st.session_state.row_selected = None
if "double_stackable" not in st.session_state:
    st.session_state.double_stackable = False
if "extract_price" not in st.session_state:
    st.session_state.extract_price = False
if "product_images" not in st.session_state:
    st.session_state.product_images = {}
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "dept_type" not in st.session_state:
    st.session_state.dept_type = None


# ============================================================================
# MAIN APP FLOW
# ============================================================================
render_header()

dept_type, double_stackable, extract_price = render_department_selector()
st.session_state.double_stackable = double_stackable
st.session_state.extract_price = extract_price
st.session_state.dept_type = dept_type

if dept_type:
    uploaded_file = render_file_uploader()

    if uploaded_file:
        # Store uploaded file for potential re-processing
        st.session_state.uploaded_file_data = uploaded_file

        process_btn = render_process_button()

        if process_btn:
            with st.spinner("🔄 Processing your offer..."):
                # Process WITHOUT images initially
                success, output_path, df, error = process_uploaded_file(
                    uploaded_file=uploaded_file,
                    dept_type=dept_type,
                    double_stackable=st.session_state.double_stackable,
                    extract_price=st.session_state.extract_price,
                    product_images=None,  # No images on first processing
                )

                if success:
                    st.session_state.processed = True
                    st.session_state.output_path = output_path
                    st.session_state.df = df
                    st.session_state.selected_df = None
                    st.session_state.product_images = {}

                    # Reset selection each new processing
                    st.session_state.row_selected = None
                else:
                    st.error(f"❌ Error: {error}")


# ============================================================================
# RESULTS SECTION
# ============================================================================
if st.session_state.processed and st.session_state.df is not None:
    render_success_message()

    # STEP 1: Select products (editor returns a DF that includes "Include" column)
    edited_df = render_selectable_table(st.session_state.df)

    # Convert edited_df -> selected rows only
    if edited_df is not None and len(edited_df) > 0 and "Include" in edited_df.columns:
        selected_df = edited_df[edited_df["Include"] == True].copy()  # noqa: E712
        selected_df.drop(columns=["Include"], inplace=True, errors="ignore")
        selected_df.reset_index(drop=True, inplace=True)
    else:
        selected_df = edited_df.copy() if edited_df is not None else None
        if selected_df is not None:
            selected_df.reset_index(drop=True, inplace=True)

    st.session_state.selected_df = selected_df

    # STEP 2: Add images (for selected products only)
    product_images = render_product_image_uploader(selected_df)
    st.session_state.product_images = product_images

    # STEP 3: Download buttons
    action, images_to_use = render_download_buttons(
        selected_df,
        product_images,
        dept_type=st.session_state.dept_type,
        base_filename=st.session_state.output_path.name,
    )

    # ------------------------------------------------------------------------
    # NO-IMAGES DOWNLOAD: use SAME TEMPLATE as images version, just no images.
    # ------------------------------------------------------------------------
    # IMPORTANT: if your render_download_buttons returns "data_only" instead of
    # "no_images", then change the next line condition to:
    # if action in ("no_images", "data_only"):
    if action == "no_images" and selected_df is not None and len(selected_df) > 0:
        with st.spinner("📄 Generating Excel (no images)..."):
            from writers.excel_writer import write_rows_to_xlsx
            from domain.schemas import FOOD_HEADERS, HPC_HEADERS

            headers = FOOD_HEADERS if st.session_state.dept_type == "food" else HPC_HEADERS
            rows = selected_df.to_dict(orient="records")

            base = st.session_state.output_path.name if st.session_state.output_path else "offer.xlsx"
            output_no_images = Path(tempfile.gettempdir()) / f"no_images_{base}"

            write_rows_to_xlsx(
                output_path=output_no_images,
                sheet_name=st.session_state.dept_type.upper(),
                headers=headers,
                rows=rows,
                product_images=None,  # only difference
            )

            st.success("✅ Excel (no images) generated!")

            with open(output_no_images, "rb") as f:
                st.download_button(
                    label="📥 Download Excel (No Images)",
                    data=f,
                    file_name=output_no_images.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    use_container_width=True,
                    key="download_no_images",
                )

    # ------------------------------------------------------------------------
    # WITH-IMAGES DOWNLOAD: FAST (no LLM re-run)
    # ------------------------------------------------------------------------
    if action == "with_images" and images_to_use and selected_df is not None and len(selected_df) > 0:
        with st.spinner("🎨 Generating Excel with images..."):
            from writers.excel_writer import write_rows_to_xlsx
            from domain.schemas import FOOD_HEADERS, HPC_HEADERS

            headers = FOOD_HEADERS if st.session_state.dept_type == "food" else HPC_HEADERS

            # Save images to temp directory
            temp_dir = Path(tempfile.gettempdir()) / "offer_images"
            temp_dir.mkdir(exist_ok=True)

            # Create image paths list matching selected products (index 0..n-1)
            image_paths: list[Path | None] = []
            for idx in range(len(selected_df)):
                if idx in images_to_use:
                    img_file = images_to_use[idx]
                    img_ext = Path(img_file.name).suffix
                    img_path = temp_dir / f"product_{idx}{img_ext}"

                    with open(img_path, "wb") as f:
                        f.write(img_file.getbuffer())

                    image_paths.append(img_path)
                else:
                    image_paths.append(None)

            rows = selected_df.to_dict(orient="records")

            base = st.session_state.output_path.name if st.session_state.output_path else "offer.xlsx"
            output_with_images = Path(tempfile.gettempdir()) / f"with_images_{base}"

            write_rows_to_xlsx(
                output_path=output_with_images,
                sheet_name=st.session_state.dept_type.upper(),
                headers=headers,
                rows=rows,
                product_images=image_paths,
            )

            st.success("✅ Excel with images generated!")

            with open(output_with_images, "rb") as f:
                st.download_button(
                    label="📥 Download Excel with Images",
                    data=f,
                    file_name=output_with_images.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    key="final_download",
                )

    # Reset button
    if render_reset_button():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()