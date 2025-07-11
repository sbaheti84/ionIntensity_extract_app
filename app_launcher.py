
"""
################################################################################
This script extract ion intensity from raw file

Input file: Plasma_pME-Glycan_Na_CE-25_060725.mzML

Created on July 9th 2025
Modified on July 9th 2025
################################################################################
"""
__author__ = ("Saurabh Baheti: baheti.saurabh@mayo.edu")




import streamlit as st
import pandas as pd
import numpy as np
from pyteomics import mzml, mgf
import io
import matplotlib.pyplot as plt

@st.cache_data(show_spinner=False)
def extract_cached(file_bytes: bytes, file_type: str, target_mzs: list[float], ppm_tolerance: float) -> pd.DataFrame:
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        return extract_from_file(tmp.name, file_type)


st.set_page_config(layout="wide")
st.title("🧪 Fragment Ion Intensity Extractor")

# User input for target m/z values
default_mzs = [111.046, 154.089, 187.099, 196.100, 246.137, 260.153,
               312.149, 344.176, 362.186, 376.202, 432.230, 464.256]
default_mz_str = ", ".join(map(str, default_mzs))
target_mz_input = st.text_input("Enter target m/z values (comma-separated)", value=default_mz_str)

try:
    target_mzs = [float(m.strip()) for m in target_mz_input.split(",") if m.strip()]
except ValueError:
    st.error("Please enter valid numeric m/z values.")
    st.stop()

ppm_tolerance = 10  # ppm

def extract_ions_from_scan(scan_data, scan_id):
    mz_array = scan_data['m/z array']
    intensity_array = scan_data['intensity array']
    results = []

    for target in target_mzs:
        delta = target * ppm_tolerance / 1e6
        mask = (mz_array >= target - delta) & (mz_array <= target + delta)
        matching_intensities = intensity_array[mask]
        max_intensity = matching_intensities.max() if matching_intensities.size > 0 else 0
        results.append({'Scan': scan_id, 'm/z': target, 'Intensity': max_intensity})
    return results

def extract_from_file(file_path, file_type='mzml'):
    out = []
    if file_type == 'mzml':
        with mzml.read(file_path) as reader:
            for spectrum in reader:
                if spectrum.get('ms level') == 2:
                    scan_id = spectrum.get('id', 'unknown')
                    out.extend(extract_ions_from_scan(spectrum, scan_id))
    elif file_type == 'mgf':
        with mgf.read(file_path) as reader:
            for spectrum in reader:
                scan_id = spectrum.get('params', {}).get('title', 'unknown')
                out.extend(extract_ions_from_scan(spectrum, scan_id))
    return pd.DataFrame(out)

# File uploader
uploaded_file = st.file_uploader("Upload .mzML or .mgf file", type=["mzML", "mgf"])
file_type = st.radio("File Type", ["mzml", "mgf"])

if uploaded_file is not None:
    st.info("Processing file...")

    file_bytes = uploaded_file.read()

    df = extract_cached(file_bytes, file_type, target_mzs, ppm_tolerance)
    if df.empty:
        st.warning("No MS2 scans found or target ions not present.")
    else:
        df['ScanNumber'] = df['Scan'].str.extract(r'scan=(\d+)').astype(float)
        matrix = df.pivot(index='ScanNumber', columns='m/z', values='Intensity')

        st.subheader("🧾 Intensity Matrix (Scan × m/z)")
        count = (matrix > 0).any(axis=1).sum()
        total_scans = matrix.shape[0]
        st.info(f"📊 Total MS/MS scans: {total_scans}")
        st.success(f"🔢 Scans with ≥1 fragment ion: {count}")
        st.dataframe(matrix.fillna(0), use_container_width=True)

        # Download buttons
        matrix_nonzero = matrix[(matrix > 0).any(axis=1)].fillna(0)
        matrix_full = matrix[(matrix > 0).all(axis=1)]

        st.download_button("⬇️ Download Matrix with ≥1 value", matrix_nonzero.to_csv(index=True),
                           "fragment_matrix_nonzero.csv", mime="text/csv")
        st.download_button("⬇️ Download Matrix with all values present", matrix_full.to_csv(index=True),
                           "fragment_matrix_full.csv", mime="text/csv")

        # Plot histogram
        mz_counts_per_scan = (matrix > 0).sum(axis=1)
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.hist(mz_counts_per_scan, bins=range(1, len(target_mzs) + 2), edgecolor='black', align='left')
        ax.set_title("Distribution of Detected Fragment Ions per Scan")
        ax.set_xlabel("Number of m/z values detected")
        ax.set_ylabel("Number of Scans")
        ax.set_xticks(range(1, len(target_mzs) + 1))

        st.pyplot(fig)
