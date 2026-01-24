import os
import struct

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted_precision")

# Lista znanych tekstur z wyliczonymi wymiarami
TARGETS = {
    # ID: (Szerokość, Wysokość)
    0: (576, 576),    # MENUTEX_130_01 (443KB)
    1: (1152, 1152),  # MENUTEX_130_02 (1.7MB) - GŁÓWNE MENU!
    3: (2048, 2048),  # MENUTEX_900_02 (3.5MB) - Tu pasuje 2048 (bo 3.5MB to prawie 4MB)
    4: (1152, 1152),  # MENUTEX_150_00 (1.7MB)
    5: (2048, 2048),  # MENUTEX_510_50
}

def create_dx10_bc7_header(width, height, mipmaps=1):
    linear_size = max(1, width // 4) * max(1, height // 4) * 16
    
    header = bytearray(128)
    header[0:4] = b'\x44\x44\x53\x20'
    struct.pack_into('<I', header, 4, 124)
    struct.pack_into('<I', header, 8, 0x00081007)
    struct.pack_into('<I', header, 12, height)
    struct.pack_into('<I', header, 16, width)
    struct.pack_into('<I', header, 20, linear_size)
    struct.pack_into('<I', header, 28, mipmaps)
    struct.pack_into('<I', header, 76, 32)
    struct.pack_into('<I', header, 80, 0x00000004)
    header[84:88] = b'DX10'
    struct.pack_into('<I', header, 108, 0x00001000)
    
    dx10_header = bytearray(20)
    struct.pack_into('<I', dx10_header, 0, 98) # BC7_UNORM
    struct.pack_into('<I', dx10_header, 4, 3)  # Tex2D
    struct.pack_into('<I', dx10_header, 12, 1) # ArraySize 1
    
    return header + dx10_header, linear_size

def extract_precision():
    print(f"--- 15_Phyre_Precision_Extract ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # Znajdź offsety
    offsets = []
    start = 0
    while True:
        idx = data.find(b"Textures/", start)
        if idx == -1: break
        offsets.append(idx)
        start = idx + 1

    print(f"Znaleziono {len(offsets)} tekstur.")

    for i in range(len(offsets)):
        # Pobierz wymiary z naszej magicznej listy
        if i in TARGETS:
            w, h = TARGETS[i]
        else:
            # Domyślnie dla nieznanych (np. tło)
            w, h = 4096, 4096 

        meta_start = offsets[i]
        end_name = data.find(b'\x00', meta_start)
        clean_name = os.path.basename(data[meta_start:end_name].decode('utf-8', errors='ignore'))
        
        if i < len(offsets) - 1:
            chunk_end = offsets[i+1]
        else:
            chunk_end = len(data)
            
        data_start = meta_start + 128
        raw_chunk = data[data_start:chunk_end]
        
        # Generuj nagłówek
        # Ustawiamy mipmaps na 0 lub 1 (zobaczymy co GIMP woli, 1 jest bezpieczne)
        full_header, required_size = create_dx10_bc7_header(w, h, mipmaps=1)
        
        # Padding
        final_data = bytearray(raw_chunk)
        if len(final_data) < required_size:
            final_data.extend(b'\x00' * (required_size - len(final_data)))
            
        out_name = f"final_{i:02d}_{clean_name}_{w}x{h}.dds"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        with open(out_path, "wb") as out_f:
            out_f.write(full_header + final_data)
            
        print(f"[{i:02d}] {clean_name} -> {w}x{h} (BC7) -> {out_name}")

    print(f"\nGotowe. Sprawdź folder '{OUTPUT_DIR}'.")
    print("Otwórz 'final_01_MENUTEX_130_02...' w GIMP.")
    print("Obraz powinien być IDEALNY.")

if __name__ == "__main__":
    extract_precision()
