"""
Styles for Offer Creation Tool
Clean light theme - ACG branding
"""

def get_custom_css():
    return """
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ✅ Modern font: Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ✅ IMPORTANT:
   DO NOT use "*" with !important, it breaks Streamlit icon fonts (Material Icons).
   Apply font only to text-ish elements so icons keep their own font.
*/
html, body, .stApp {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Noto Sans", sans-serif !important;
}

/* Apply to common text elements */
h1,h2,h3,h4,h5,h6,p,span,div,label,small,caption,li,a,strong,em,
button,input,textarea,select,option,table,thead,tbody,tr,th,td {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Noto Sans", sans-serif;
}

/* Keep box sizing */
* { box-sizing: border-box; }

:root{
    --bg: #ffffff;
    --text: #0b0f14;
    --muted: #6b7280;
    --border: #e5e7eb;
    --card: #f8fafc;
}

.stApp { background: var(--bg); color: var(--text); }

/* Page content */
.main > div:first-child {
    max-width: 1200px;
    margin: 0 auto;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-top: 2.2rem;
}

/* HEADER ROW: title left, logo right */
.header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 2rem;
    margin-bottom: 0.5rem;
}

.header-left { flex: 1; min-width: 0; }
.header-right { flex: 0 0 auto; display: flex; justify-content: flex-end; }

/* Logo */
.acg-logo-square{
    width: 180px;
    height: auto;
    border-radius: 0 !important;
    clip-path: none !important;
    object-fit: contain !important;
    background: transparent !important;
    box-shadow: none !important;
    display: block;
}

/* Title + subtitle */
.main-title {
    font-size: 3.2rem;
    font-weight: 900;
    text-align: left;
    color: var(--text);
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.02em;
    line-height: 1.05;
}

.subtitle {
    text-align: left;
    color: var(--muted);
    font-size: 1.1rem;
    margin: 0 0 2.0rem 0;
    font-weight: 500;
    max-width: 900px;
}

/* Section label */
.section-label {
    font-size: 1.05rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}

.department-section { margin: 2rem 0 1.4rem 0; }

/* Radio buttons */
.stRadio > div { flex-direction: row; gap: 0.8rem; }

.stRadio > div > label {
    background: #ffffff;
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1.6rem;
    cursor: pointer;
    transition: all 0.15s ease;
    font-size: 1rem;
    font-weight: 700;
    color: #374151;
}
.stRadio > div > label:hover {
    border-color: #0b0f14;
    background: var(--card);
}
.stRadio > div > label[data-checked="true"] {
    background: #0b0f14;
    color: #ffffff;
    border-color: #0b0f14;
}

/* Checkbox styling */
.stCheckbox > label {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}
.stCheckbox > label > div:first-child {
    margin-right: 0.6rem !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    padding: 0.9rem 1.4rem;
    font-size: 1rem;
    font-weight: 800;
    border-radius: 12px;
    border: none;
    background: #0b0f14;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.15s ease;
}
.stButton > button:hover { background: #111827; transform: translateY(-1px); }

.stDownloadButton > button {
    background: #16a34a;
    color: #ffffff;
    font-weight: 800;
    padding: 0.9rem 1.4rem;
    border-radius: 12px;
    width: 100%;
    border: none;
}
.stDownloadButton > button:hover { background: #15803d; }

/* Success box */
.success-box {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 14px;
    padding: 1.2rem;
    margin: 1.6rem 0;
}
.success-box h3 {
    color: #166534;
    margin: 0;
    font-weight: 900;
}

/* Data editor */
.stDataFrame, .stDataEditor {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #ffffff;
}

/* Divider */
hr {
    margin: 1.8rem 0;
    border: none;
    border-top: 1px solid var(--border);
}
</style>
"""
