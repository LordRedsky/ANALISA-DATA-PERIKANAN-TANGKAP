import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from data_processor import process_fisheries_data

# Set wide layout and premium title
st.set_page_config(
    page_title="Sistem Analisis Data Perikanan Tangkap",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Dark Theme & Glassmorphism Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    }

    /* Glassmorphic card styling */
    .metric-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 139, 253, 0.6);
        box-shadow: 0 12px 40px 0 rgba(56, 139, 253, 0.15);
    }
    .metric-title {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(45deg, #58a6ff, #1f6feb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-sub {
        font-size: 12px;
        color: #58a6ff;
        margin-top: 4px;
    }

    /* Section styling */
    .section-title {
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 20px;
        border-bottom: 2px solid #30363d;
        padding-bottom: 8px;
        color: #f0f6fc;
        letter-spacing: 0.5px;
    }

    /* Gradient header styling */
    .title-gradient {
        background: linear-gradient(45deg, #58a6ff, #50e3c2, #1f6feb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for calculations & analytics parsing
def clean_val(val):
    if pd.isnull(val):
        return 0
    try:
        return float(val)
    except Exception:
        # Extract first number
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', str(val))
        return float(nums[0]) if nums else 0.0

def parse_complex_catch(sp_str, w_str, p_str):
    if pd.isnull(sp_str) or not str(sp_str).strip():
        return []
    sp_str = str(sp_str).strip()
    w_str = str(w_str).strip() if pd.notnull(w_str) else ""
    p_str = str(p_str).strip() if pd.notnull(p_str) else ""
    
    if sp_str.lower() in ["tidak ada", "tidak ada.", "nan", "0", ""]:
        return []
        
    try:
        w_val = float(w_str) if w_str else 0.0
        p_val = float(p_str) if p_str else 0.0
        return [{'species': sp_str, 'weight': w_val, 'price': p_val, 'revenue': w_val * p_val}]
    except ValueError:
        pass
        
    # Multiline or list formats
    parts = re.split(r'[\n,\r|]|\bDAN\b|\bdan\b', sp_str)
    species_list = [p.strip() for p in parts if p.strip() and p.strip().lower() not in ["tidak ada", "nan"]]
    
    weights = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', w_str)]
    prices = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', p_str)]
    
    records = []
    for idx, sp in enumerate(species_list):
        w = weights[idx] if idx < len(weights) else (weights[0] if len(weights) == 1 else 0.0)
        p = prices[idx] if idx < len(prices) else (prices[0] if len(prices) == 1 else 0.0)
        records.append({
            'species': sp.upper(),
            'weight': w,
            'price': p,
            'revenue': w * p
        })
    return records

def calculate_analytics(df):
    """Parses species, weight, and prices per row to get comprehensive analytics."""
    rows_data = []
    species_records = []
    
    for idx, row in df.iterrows():
        nelayan = row.get('NAMA NELAYAN')
        kecamatan = row.get('KECAMATAN')
        desa = row.get('DESA')
        gear = row.get('ALAT TANGKAP UTAMA')
        trips = clean_val(row.get('JUMLAH TRIP DALAM SEBULAN (HARI)'))
        if trips == 0:
            trips = 20 # default average fallback
            
        # Parse main catch (triplets 1-11)
        main_jenis = row.get('JENIS TANGKAPAN', '')
        main_berat = row.get('BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)', 0)
        main_harga = row.get('HARGA PER-JENIS TANGKAPAN /kg (Rp.)', 0)
        
        # Parse additional catch (triplet 12 mapped to 2)
        add_jenis = row.get('JENIS TANGKAPAN 2', '')
        add_berat = row.get('BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 2', 0)
        add_harga = row.get('HARGA PER-JENIS TANGKAPAN /kg (Rp.) 2', 0)
        
        catches = parse_complex_catch(main_jenis, main_berat, main_harga) + parse_complex_catch(add_jenis, add_berat, add_harga)
        
        tot_weight_trip = sum([c['weight'] for c in catches])
        tot_rev_trip = sum([c['revenue'] for c in catches])
        tot_rev_month = tot_rev_trip * trips
        tot_weight_month = tot_weight_trip * trips
        
        for c in catches:
            species_records.append({
                'Nelayan': nelayan,
                'Kecamatan': kecamatan,
                'Desa': desa,
                'Alat Tangkap': gear,
                'Species': c['species'],
                'Weight (Trip)': c['weight'],
                'Price/kg': c['price'],
                'Revenue (Trip)': c['revenue'],
                'Revenue (Month)': c['revenue'] * trips,
                'Weight (Month)': c['weight'] * trips
            })
            
        rows_data.append({
            'Nelayan': nelayan,
            'Kecamatan': kecamatan,
            'Desa': desa,
            'Gear': gear,
            'Trips': trips,
            'Weight/Trip': tot_weight_trip,
            'Revenue/Trip': tot_rev_trip,
            'Weight/Month': tot_weight_month,
            'Revenue/Month': tot_rev_month
        })
        
    return pd.DataFrame(rows_data), pd.DataFrame(species_records)

# ==================== MAIN INTERFACE ====================

# Sidebar Navigation / Options
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 MENU NAVIGASI</h2>", unsafe_allow_html=True)
    st.markdown("---")
    app_mode = st.radio(
        "Pilih Halaman:",
        ["📥 Pemrosesan & Unggah File", "📊 Dashboard Analisis Interaktif", "🔍 Penjelajah Data Nelayan"]
    )
    st.markdown("---")
    st.markdown("""
    **Tentang Aplikasi:**
    Sistem analisis canggih berbasis AI untuk membersihkan, memetakan, dan memvisualisasikan data Nelayan Perikanan Tangkap Kabupaten Muna Barat.
    
    """)

# Header Banner
st.markdown("""
<div style='background: linear-gradient(90deg, #161b22 0%, #1f6feb 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(56,139,253,0.3); margin-bottom: 30px;'>
    <h1 style='margin:0; font-size: 38px; color: #f0f6fc;'>🎣 SISTEM ANALISIS PERIKANAN TANGKAP</h1>
    <p style='margin:10px 0 0 0; font-size: 16px; color: #8b949e; letter-spacing: 0.5px;'>
        Pembersihan, Pemetaan Otomatis, dan Visualisasi Data Kuesioner Nelayan secara Real-Time.
    </p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'df_summary' not in st.session_state:
    st.session_state.df_summary = None
if 'df_species' not in st.session_state:
    st.session_state.df_species = None

# PAGE 1: Upload and Process File
if app_mode == "📥 Pemrosesan & Unggah File":
    st.markdown("<h2 class='section-title'>📥 UNGGUH & PROSES DATA BARU</h2>", unsafe_allow_html=True)
    
    col_up1, col_up2 = st.columns([2, 1])
    
    with col_up1:
        st.markdown("""
        ### Petunjuk Penggunaan:
        1. **Unggah File Excel**: Silakan drag-and-drop atau pilih file Excel mentah dari Google Form Tangkapan Anda (`BANK DATA...xlsx`).
        2. **Proses Data**: Tekan tombol **Proses Pemetaan Data** untuk menjalankan algoritma pembersihan data secara otomatis.
        3. **Unduh Hasil**: Setelah sukses, Anda dapat melihat pratinjau data dan langsung mengunduh file Excel yang telah terstruktur rapi sesuai template hasil (**`analisa_download.xlsx`**).
        """)
        
        uploaded_file = st.file_uploader("Pilih File Excel Bank Data (.xlsx)", type=["xlsx"])
        
        if uploaded_file is not None:
            st.success("🎉 File berhasil diunggah!")
            
            # Temporary file write
            with open("temp_input.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🚀 MULAI PEMETAAN DATA NELAYAN", use_container_width=True):
                with st.spinner("Sedang memproses, membersihkan, dan memetakan data nelayan..."):
                    try:
                        template_path = "template data input.xlsx"
                        output_path = "analisa_download.xlsx"
                        
                        if not os.path.exists(template_path):
                            st.error(f"Template '{template_path}' tidak ditemukan di workspace! Pastikan file template tersebut ada.")
                        else:
                            # Process data
                            df_proc = process_fisheries_data("temp_input.xlsx", template_path, output_path)
                            
                            # Perform calculations for dashboard
                            df_summary, df_species = calculate_analytics(df_proc)
                            
                            # Store in session state
                            st.session_state.processed_data = df_proc
                            st.session_state.df_summary = df_summary
                            st.session_state.df_species = df_species
                            
                            st.balloons()
                            st.success("✅ Pemrosesan Selesai! Data berhasil dibersihkan, digabungkan, dan diselaraskan sesuai template.")
                            
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat memproses data: {e}")
                        
            # Show download button if processing completed
            if st.session_state.processed_data is not None and os.path.exists("analisa_download.xlsx"):
                st.markdown("### 📥 UNDUH HASIL")
                with open("analisa_download.xlsx", "rb") as file:
                    st.download_button(
                        label="💾 UNDUH FILE HASIL (analisa_download.xlsx)",
                        data=file,
                        file_name="analisa_download.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
    with col_up2:
        st.markdown("<div class='metric-card'><h4 class='metric-title'>⚙️ Status Aplikasi</h4>", unsafe_allow_html=True)
        if st.session_state.processed_data is not None:
            st.markdown(f"<div class='metric-value'>READY</div>", unsafe_allow_html=True)
            unique_nelayan = st.session_state.processed_data['NAMA NELAYAN'].nunique()
            st.markdown(f"<p class='metric-sub'>{unique_nelayan} nelayan aktif termuat</p></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-value' style='color:#f85149;'>EMPTY</div>", unsafe_allow_html=True)
            st.markdown("<p class='metric-sub'>Menunggu unggahan file baru...</p></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # If no file uploaded, let's load dummy/current file if it already exists
        if st.session_state.processed_data is None:
            if os.path.exists("analisa_download.xlsx") and os.path.exists("BANK DATA PERIKANAN TANGKAP (Jawaban).xlsx"):
                if st.button("💡 Muat Data Dummy yang Ada"):
                    with st.spinner("Memuat data dummy saat ini..."):
                        df_proc = pd.read_excel("analisa_download.xlsx")
                        df_summary, df_species = calculate_analytics(df_proc)
                        st.session_state.processed_data = df_proc
                        st.session_state.df_summary = df_summary
                        st.session_state.df_species = df_species
                        st.success("Berhasil memuat data dummy dari penyimpanan lokal!")
                        st.rerun()

# PAGE 2: Interactive Dashboard
elif app_mode == "📊 Dashboard Analisis Interaktif":
    st.markdown("<h2 class='section-title'>📊 DASHBOARD ANALISIS INTERAKTIF</h2>", unsafe_allow_html=True)
    
    if st.session_state.processed_data is None:
        st.info("⚠️ Belum ada data aktif. Silakan masuk ke halaman **📥 Pemrosesan & Unggah File** terlebih dahulu untuk mengunggah atau memuat data!")
    else:
        df_summary = st.session_state.df_summary
        df_species = st.session_state.df_species
        
        # 1. Row of KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        total_nelayan = df_summary['Nelayan'].nunique()
        total_catch_trip = df_summary['Weight/Trip'].sum()
        total_rev_month = df_summary['Revenue/Month'].sum()
        avg_trips = df_summary.drop_duplicates(subset=['Nelayan'])['Trips'].mean()
        
        with kpi1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Total Nelayan</div>
                <div class='metric-value'>{total_nelayan}</div>
                <div class='metric-sub'>Muna Barat</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Catch Weight (Trip)</div>
                <div class='metric-value'>{total_catch_trip:,.1f} Kg</div>
                <div class='metric-sub'>Total tangkapan per trip</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Estimasi Revenue (Bulan)</div>
                <div class='metric-value'>Rp {total_rev_month:,.0f}</div>
                <div class='metric-sub'>Potensi omzet per bulan</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Rata-rata Trip / Bulan</div>
                <div class='metric-value'>{avg_trips:,.1f} Hari</div>
                <div class='metric-sub'>Hari melaut rata-rata</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Charts Row 1: Kecamatan comparisons
        st.markdown("### 🗺️ Analisis Wilayah (Kecamatan)")
        c_col1, c_col2 = st.columns(2)
        
        # Group by Kecamatan
        df_kec = df_summary.groupby('Kecamatan').agg({
            'Nelayan': 'count',
            'Weight/Month': 'sum',
            'Revenue/Month': 'sum'
        }).reset_index()
        
        with c_col1:
            fig1 = px.bar(
                df_kec,
                x='Kecamatan',
                y='Weight/Month',
                title='Total Volume Tangkapan per Bulan (KG) per Kecamatan',
                labels={'Weight/Month': 'Tangkapan (Kg)'},
                color='Weight/Month',
                color_continuous_scale='tealgrn',
                template='plotly_dark'
            )
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
            
        with c_col2:
            fig2 = px.bar(
                df_kec,
                x='Kecamatan',
                y='Revenue/Month',
                title='Total Omzet Nelayan per Bulan (Rp) per Kecamatan',
                labels={'Revenue/Month': 'Omzet (Rp)'},
                color='Revenue/Month',
                color_continuous_scale='blues',
                template='plotly_dark'
            )
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Charts Row 2: Alat Tangkap and Species Distribution
        st.markdown("### 🐠 Analisis Alat Tangkap & Komoditas Spesies")
        c_col3, c_col4 = st.columns(2)
        
        with c_col3:
            # Distribution of Gears (Main Gears)
            df_gear = df_summary.groupby('Gear').size().reset_index(name='Jumlah')
            fig3 = px.pie(
                df_gear,
                values='Jumlah',
                names='Gear',
                title='Distribusi Penggunaan Alat Tangkap Utama',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template='plotly_dark'
            )
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)
            
        with c_col4:
            # Top Species by weight
            df_sp_grouped = df_species.groupby('Species').agg({
                'Weight (Month)': 'sum',
                'Revenue (Month)': 'sum'
            }).reset_index().sort_values(by='Weight (Month)', ascending=False).head(10)
            
            fig4 = px.bar(
                df_sp_grouped,
                x='Weight (Month)',
                y='Species',
                orientation='h',
                title='10 Komoditas Utama Hasil Tangkapan per Bulan (KG)',
                labels={'Weight (Month)': 'Volume Tangkapan (Kg)', 'Species': 'Spesies/Jenis Tangkapan'},
                color='Weight (Month)',
                color_continuous_scale='viridis',
                template='plotly_dark'
            )
            fig4.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)

# PAGE 3: Data Explorer
elif app_mode == "🔍 Penjelajah Data Nelayan":
    st.markdown("<h2 class='section-title'>🔍 PENJELAJAH DATA NELAYAN INTERAKTIF</h2>", unsafe_allow_html=True)
    
    if st.session_state.processed_data is None:
        st.info("⚠️ Belum ada data aktif. Silakan masuk ke halaman **📥 Pemrosesan & Unggah File** terlebih dahulu!")
    else:
        df_proc = st.session_state.processed_data
        
        # Sidebar/Top filter options
        st.markdown("### 🎛️ Filter Pencarian")
        kecamatans = ["SEMUA"] + list(df_proc['KECAMATAN'].dropna().unique())
        selected_kec = st.selectbox("Filter berdasarkan Kecamatan:", kecamatans)
        
        # Text Search
        search_query = st.text_input("Cari nama Nelayan, Nama Kapal, atau Petugas:")
        
        # Apply filters
        df_filtered = df_proc.copy()
        if selected_kec != "SEMUA":
            df_filtered = df_filtered[df_filtered['KECAMATAN'] == selected_kec]
            
        if search_query:
            df_filtered = df_filtered[
                df_filtered['NAMA NELAYAN'].astype(str).str.contains(search_query, case=False) |
                df_filtered['NAMA KAPAL'].astype(str).str.contains(search_query, case=False) |
                df_filtered['NAMA PETUGAS '].astype(str).str.contains(search_query, case=False)
            ]
            
        st.markdown(f"**Ditemukan {len(df_filtered)} Nelayan berdasarkan filter.**")
        
        # Display main clean table
        display_cols = [
            'NAMA NELAYAN', 'KECAMATAN', 'DESA', 'NAMA KAPAL', 'STATUS PEMILIKAN KAPAL',
            'ALAT TANGKAP UTAMA', 'JENIS TANGKAPAN', 'BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)',
            'ALAT TANGKAP TAMBAHAN', 'JENIS TANGKAPAN 2', 'BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 2',
            'JUMLAH TRIP DALAM SEBULAN (HARI)', 'TOTAL BIAYA KESELURUHAN KEBUTUHAN OPERASIONAL (Rp.)'
        ]
        
        st.dataframe(
            df_filtered[display_cols].style.format(precision=1),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Detail view for single fisher
        st.markdown("### 🔍 Detail Nelayan Terpilih")
        selected_nelayan = st.selectbox("Pilih Nelayan untuk melihat detail kuesioner lengkap:", df_filtered['NAMA NELAYAN'].unique())
        
        if selected_nelayan:
            nelayan_details = df_filtered[df_filtered['NAMA NELAYAN'] == selected_nelayan].iloc[0].to_dict()
            
            det_col1, det_col2 = st.columns(2)
            
            with det_col1:
                st.markdown(f"#### 👤 Identitas & Perizinan")
                st.markdown(f"**Nama Nelayan:** {nelayan_details.get('NAMA NELAYAN')}")
                st.markdown(f"**Kecamatan / Desa:** {nelayan_details.get('KECAMATAN')} / {nelayan_details.get('DESA')}")
                st.markdown(f"**No. KTP:** {nelayan_details.get('No. KTP')}")
                st.markdown(f"**No. KUSUKA:** {nelayan_details.get('No. KUSUKA')}")
                st.markdown(f"**No. Handphone:** {nelayan_details.get('No. HANDPHONE')}")
                st.markdown(f"**Jenis Usaha / Keahlian:** {nelayan_details.get('JENIS USAHA')} / {nelayan_details.get('KEAHLIAN NELAYAN')}")
                st.markdown(f"**Surat Izin Berusaha:** {nelayan_details.get('SURAT IZIN BERUSAHA')}")
                st.markdown(f"**Petugas Pengumpul Data:** {nelayan_details.get('NAMA PETUGAS ')}")
                
            with det_col2:
                st.markdown(f"#### 🚢 Armada Kapal & Alat Tangkap")
                st.markdown(f"**Nama / Pemilikan Kapal:** {nelayan_details.get('NAMA KAPAL')} ({nelayan_details.get('STATUS PEMILIKAN KAPAL')})")
                st.markdown(f"**No. SIPI/SIKPI/BPKB:** {nelayan_details.get('No. SIPI/SIKPI/BPKB')}")
                st.markdown(f"**Jumlah Awak Kapal:** {nelayan_details.get('JUMLAH AWAK KAPAL (ORANG)')} Orang")
                st.markdown(f"**Jenis / GT Kapal:** {nelayan_details.get('JENIS KAPAL')} ({nelayan_details.get('UKURAN GT KAPAL')} GT)")
                st.markdown(f"**Mesin Kapal:** {nelayan_details.get('JUMLAH MESIN')} Unit / {nelayan_details.get('UKURAN DAYA MESIN (PK)')} PK")
                st.markdown(f"**Dimensi Kapal (P x L):** {nelayan_details.get('UKURAN PANJANG KAPAL (METER)')} m x {nelayan_details.get('UKURAN LEBAR KAPAL (METER)')} m")
                st.markdown(f"**Alat Tangkap Utama:** {nelayan_details.get('ALAT TANGKAP UTAMA')}")
                st.markdown(f"**Alat Tangkap Tambahan:** {nelayan_details.get('ALAT TANGKAP TAMBAHAN')}")

            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(f"#### 🐟 Rincian Komoditas Tangkapan")
            
            catch_rows = []
            nelayan_rows = df_filtered[df_filtered['NAMA NELAYAN'] == selected_nelayan]
            for _, r_val in nelayan_rows.iterrows():
                # Main Catch
                sp_main = r_val.get('JENIS TANGKAPAN')
                if pd.notnull(sp_main) and str(sp_main).strip() != "":
                    w_main = r_val.get('BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)')
                    p_main = r_val.get('HARGA PER-JENIS TANGKAPAN /kg (Rp.)')
                    catch_rows.append({
                        'Kategori Tangkapan': '🐟 Tangkapan Utama',
                        'Jenis/Spesies Ikan': str(sp_main).upper(),
                        'Berat (Kg)': float(w_main) if pd.notnull(w_main) and w_main != "" else 0.0,
                        'Harga / Kg (Rp.)': float(p_main) if pd.notnull(p_main) and p_main != "" else 0.0,
                        'Estimasi Pendapatan / Trip (Rp.)': (float(w_main) if pd.notnull(w_main) and w_main != "" else 0.0) * (float(p_main) if pd.notnull(p_main) and p_main != "" else 0.0)
                    })
                # Additional Catch
                sp_add = r_val.get('JENIS TANGKAPAN 2')
                if pd.notnull(sp_add) and str(sp_add).strip() != "":
                    w_add = r_val.get('BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 2')
                    p_add = r_val.get('HARGA PER-JENIS TANGKAPAN /kg (Rp.) 2')
                    catch_rows.append({
                        'Kategori Tangkapan': '🐠 Tangkapan Tambahan',
                        'Jenis/Spesies Ikan': str(sp_add).upper(),
                        'Berat (Kg)': float(w_add) if pd.notnull(w_add) and w_add != "" else 0.0,
                        'Harga / Kg (Rp.)': float(p_add) if pd.notnull(p_add) and p_add != "" else 0.0,
                        'Estimasi Pendapatan / Trip (Rp.)': (float(w_add) if pd.notnull(w_add) and w_add != "" else 0.0) * (float(p_add) if pd.notnull(p_add) and p_add != "" else 0.0)
                    })
                    
            df_catches = pd.DataFrame(catch_rows).drop_duplicates()
            if not df_catches.empty:
                st.dataframe(
                    df_catches.style.format({
                        'Berat (Kg)': '{:.1f} Kg',
                        'Harga / Kg (Rp.)': 'Rp. {:,.0f}',
                        'Estimasi Pendapatan / Trip (Rp.)': 'Rp. {:,.0f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Tidak ada data tangkapan aktif untuk nelayan ini.")
                
            st.markdown("---")
            st.markdown(f"#### 📅 Operasional & Hambatan")
            st.markdown(f"**Jumlah Trip Sebulan:** {nelayan_details.get('JUMLAH TRIP DALAM SEBULAN (HARI)')} Hari Melaut")
            st.markdown(f"**Daerah Penangkapan:** {nelayan_details.get('DAERAH PENANGKAPAN')}")
            st.markdown(f"**Kebutuhan Operasional:** {nelayan_details.get('KEBUTUHAN OPERASIONAL')}")
            st.markdown(f"**Total Biaya Operasional / Trip:** Rp. {clean_val(nelayan_details.get('TOTAL BIAYA KESELURUHAN KEBUTUHAN OPERASIONAL (Rp.)')):,.0f}")
            st.markdown(f"**Tempat Penjualan Hasil:** {nelayan_details.get('TEMPAT PENJUALAN HASIL TANGKAPAN ')}")
            st.markdown(f"**Hambatan / Kendala:** {nelayan_details.get('HAMBATAN DAN KENDALA')}")
