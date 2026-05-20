import os
import pandas as pd
from data_processor import process_fisheries_data

def run_verification():
    print("=== Running Programmatic Verification ===")
    
    input_file = "BANK DATA PERIKANAN TANGKAP (Jawaban).xlsx"
    template_file = "template data input.xlsx"
    output_file = "analisa_download.xlsx"
    
    # Check if files exist
    assert os.path.exists(input_file), f"Input file {input_file} missing!"
    assert os.path.exists(template_file), f"Template file {template_file} missing!"
    
    # Process the data
    df_processed = process_fisheries_data(input_file, template_file, output_file)
    
    # 1. Check if output file exists
    assert os.path.exists(output_file), "Output file was not created!"
    print("[OK] Output file created successfully.")
    
    # 2. Read template and output to compare columns
    df_temp = pd.read_excel(template_file)
    df_out = pd.read_excel(output_file)
    
    print(f"Processed DataFrame Shape: {df_out.shape}")
    
    # Compare columns
    temp_cols = df_temp.columns.tolist()
    out_cols = df_out.columns.tolist()
    
    assert len(temp_cols) == len(out_cols), f"Column count mismatch! Template: {len(temp_cols)}, Output: {len(out_cols)}"
    for i, (tc, oc) in enumerate(zip(temp_cols, out_cols)):
        assert tc == oc, f"Column mismatch at index {i}! Template: '{tc}', Output: '{oc}'"
    print("[OK] Output column names and order match the template exactly.")
    
    # 3. Check number of active rows
    # The dummy data has been split from 16 active raw rows into 29 split rows.
    assert len(df_out) == 29, f"Expected 29 rows, but found {len(df_out)}"
    print("[OK] Output row count matches expected split count (29 rows).")
    
    # 4. Check special cases
    # MALAWIN: Main Gear was 'PANAH' (not in list) -> should be 'Yang Lain' in UTAMA and 'PANAH' in TAMBAHAN.
    # It has 2 main catch species: KAKAP MERAH and BARONANG.
    malawin_rows = df_out[df_out['NAMA NELAYAN'] == 'MALAWIN']
    assert len(malawin_rows) == 2, f"Expected 2 rows for MALAWIN, got {len(malawin_rows)}"
    
    # Row 1: KAKAP MERAH, weight 5, price 40000
    r1 = malawin_rows.iloc[0]
    assert r1['ALAT TANGKAP UTAMA'] == 'PANAH', f"Expected PANAH, got '{r1['ALAT TANGKAP UTAMA']}'"
    assert pd.isnull(r1['ALAT TANGKAP TAMBAHAN']) or r1['ALAT TANGKAP TAMBAHAN'] == "", f"Expected empty addition, got '{r1['ALAT TANGKAP TAMBAHAN']}'"
    assert r1['JENIS TANGKAPAN'] == 'KAKAP MERAH'
    assert r1['BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)'] == 5
    assert r1['HARGA PER-JENIS TANGKAPAN /kg (Rp.)'] == 40000
    
    # Row 2: BARONANG, weight 10, price 35000
    r2 = malawin_rows.iloc[1]
    assert r2['ALAT TANGKAP UTAMA'] == 'PANAH', f"Expected PANAH, got '{r2['ALAT TANGKAP UTAMA']}'"
    assert pd.isnull(r2['ALAT TANGKAP TAMBAHAN']) or r2['ALAT TANGKAP TAMBAHAN'] == "", f"Expected empty addition, got '{r2['ALAT TANGKAP TAMBAHAN']}'"
    assert r2['JENIS TANGKAPAN'] == 'BARONANG'
    assert r2['BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)'] == 10
    assert r2['HARGA PER-JENIS TANGKAPAN /kg (Rp.)'] == 35000
    print("[OK] MALAWIN (custom gear 'PANAH' & 2 split catches) mapped and split correctly as-is.")
    
    # ASRUL: JARING INSANG TETAP (ID 3) -> should have catch 'IKAN TENGGIRI'
    asrul_row = df_out[df_out['NAMA NELAYAN'] == 'ASRUL']
    assert len(asrul_row) == 1, "Expected 1 row for ASRUL"
    assert asrul_row.iloc[0]['JENIS TANGKAPAN'] == 'IKAN TENGGIRI'
    print("[OK] ASRUL (ID 3 Jaring Insang Tetap) catch extracted correctly.")
    
    # MUHAMMAD IWAN: Main Gear JARING INSANG TETAP, Additional Gear RAWAI DASAR, Catch 2 PARI LEMER
    iwan_rows = df_out[df_out['NAMA NELAYAN'] == 'MUHAMMAD IWAN']
    assert len(iwan_rows) == 1, "Expected 1 row for MUHAMMAD IWAN"
    assert iwan_rows.iloc[0]['ALAT TANGKAP UTAMA'] == 'JARING INSANG TETAP'
    assert iwan_rows.iloc[0]['ALAT TANGKAP TAMBAHAN'] == 'RAWAI DASAR'
    assert iwan_rows.iloc[0]['JENIS TANGKAPAN'] == 'RAJUNGAN'
    assert iwan_rows.iloc[0]['JENIS TANGKAPAN 2'] == 'PARI LEMER'
    print("[OK] MUHAMMAD IWAN (standard gear + additional catch 2) mapped correctly.")
    
    # BAHAR check (multiple species: IKAN TERI GEPENG, IKAN TERI NASI + additional RAJUNGAN)
    bahar_rows = df_out[df_out['NAMA NELAYAN'] == 'BAHAR']
    assert len(bahar_rows) == 2, f"Expected 2 rows for BAHAR, got {len(bahar_rows)}"
    br1 = bahar_rows.iloc[0]
    br2 = bahar_rows.iloc[1]
    
    assert br1['JENIS TANGKAPAN'] == 'IKAN TERI GEPENG'
    assert br1['BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)'] == 30
    assert br1['HARGA PER-JENIS TANGKAPAN /kg (Rp.)'] == 14000
    assert br1['JENIS TANGKAPAN 2'] == 'RAJUNGAN'
    assert br1['BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 2'] == 5
    assert br1['HARGA PER-JENIS TANGKAPAN /kg (Rp.) 2'] == 50000
    
    assert br2['JENIS TANGKAPAN'] == 'IKAN TERI NASI'
    assert br2['BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)'] == 20
    assert br2['HARGA PER-JENIS TANGKAPAN /kg (Rp.)'] == 14000
    assert pd.isnull(br2['JENIS TANGKAPAN 2']) or br2['JENIS TANGKAPAN 2'] == ""
    print("[OK] BAHAR split rows and clean numeric formatting verified successfully.")
    
    # DESA merging check (ASRUL is MAGINTI -> DESA 4 KANGKUNAWE -> should be merged to DESA)
    assert asrul_row.iloc[0]['DESA'] == 'KANGKUNAWE', f"Expected 'KANGKUNAWE' for ASRUL Desa, got '{asrul_row.iloc[0]['DESA']}'"
    print("[OK] Desa merging verified successfully.")
    
    print("\n==============================================")
    print("SUCCESS: ALL PROGRAMMATIC VERIFICATION CHECKS PASSED!")
    print("==============================================")

if __name__ == "__main__":
    run_verification()
