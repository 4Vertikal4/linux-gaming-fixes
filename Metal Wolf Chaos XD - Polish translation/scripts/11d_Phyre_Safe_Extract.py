import os
import struct
import math

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted_safe")

def create_valid_dxt5_header(width, height):
    # Standard DXT5 Header
    # Obliczamy wymagany rozmiar danych dla DXT5 (16 bajtów na blok 4x4)
    # PitchOrLinearSize dla DXT to rozmiar głównego obrazu
    linear_size = max(1, width // 4) * max(1, height // 4) * 16
    
    header = bytearray(128)
    # Magic 'DDS '
    header[0:4] = b'\x44\x44\x53\x20'
    
    # dwSize (124)
    struct.pack_into('<I', header, 4, 124)
    
    # dwFlags (CAPS | HEIGHT | WIDTH | PIXELFORMAT | LINEARSIZE)
    # 0x00081007 = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE
    struct.pack_into('<I', header, 8, 0x00081007)
    
    # dwHeight, dwWidth
    struct.pack_into('<I', header, 12, height)
    struct.pack_into('<I', header, 16, width)
    
    # dwPitchOrLinearSize
    struct.pack_into('<I', header, 20, linear_size)
    
    # dwDepth, dwMipMapCount (Ustawiamy 1, żeby GIMP nie szukał dalej)
    struct.pack_into('<I', header, 28, 1)
    
    # PIXELFORMAT (start at 76)
    struct.pack_into('<I', header, 76, 32) # size
    struct.pack_into('<I', header, 80, 0x00000004) # DDPF_FOURCC
    header[84:88] = b'DXT5' # FourCC
    
    # CAPS (start at 108)
    struct.pack_into('<I', header, 108, 0x00001000) # DDSCAPS_TEXTURE
    
    return header, linear_size

def extract_safe():
    print(f"--- 11d_Phyre_Safe_Extract (Padding Mode) ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # 1. Znajdź wszystkie nazwy tekstur
    offsets = []
    start = 0
    while True:
        idx = data.find(b"Textures/", start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + 1

    print(f"Znaleziono {len(offsets)} fragmentów.")

    for i in range(len(offsets)):
        meta_start = offsets[i]
        
        # Nazwa pliku
        end_name = data.find(b'\x00', meta_start)
        filename_raw = data[meta_start:end_name].decode('utf-8', errors='ignore')
        clean_name = os.path.basename(filename_raw)
        
        # Ustalamy koniec chunka (początek następnej nazwy lub koniec pliku)
        if i < len(offsets) - 1:
            chunk_end = offsets[i+1]
        else:
            chunk_end = len(data)
            
        # Początek danych - próbujemy heurystykę +128 bajtów od nazwy
        # (W poprzednim skrypcie to działało jako punkt startu, ale rozmiar był zły)
        data_start = meta_start + 128 
        raw_chunk = data[data_start:chunk_end]
        actual_size = len(raw_chunk)
        
        # Zgadujemy rozdzielczość "na wyrost" (lepiej za duża niż za mała)
        # Dla ID 00 (443KB) -> spróbujmy 1024x1024 (1MB)
        # Dla ID 01 (1.7MB) -> spróbujmy 2048x2048 (4MB)
        
        if actual_size < 500000: # < 500KB
            w, h = 1024, 1024 
        elif actual_size < 2000000: # < 2MB
            w, h = 2048, 2048
        elif actual_size < 5000000: # < 5MB
            w, h = 2048, 2048 # Może być więcej mipsów
        else:
            w, h = 4096, 4096

        header, required_size = create_valid_dxt5_header(w, h)
        
        # === KLUCZOWY MOMENT: PADDING ===
        # Jeśli mamy mniej danych niż wymaga DXT5 dla tej rozdzielczości,
        # dopychamy zerami. To uratuje GIMP-a przed crashem.
        
        final_data = bytearray(raw_chunk)
        if len(final_data) < required_size:
            missing = required_size - len(final_data)
            final_data.extend(b'\x00' * missing)
            padding_info = f"(PADDED +{missing} bytes)"
        else:
            # Jeśli danych jest za dużo, przycinamy (rzadkie, ale możliwe dla DXT)
            final_data = final_data[:required_size]
            padding_info = "(TRIMMED)"

        # Składamy plik
        full_dds = header + final_data
        
        out_name = f"safe_{i:02d}_{clean_name}_{w}x{h}.dds"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        with open(out_path, "wb") as out_f:
            out_f.write(full_dds)
            
        print(f"[{i:02d}] {clean_name} -> {w}x{h} | Real: {actual_size} -> Target: {required_size} {padding_info}")

    print(f"\nGotowe. Sprawdź folder '{OUTPUT_DIR}'.")
    print("Jeśli obraz to 'śnieg/szum' = dane są skompresowane.")
    print("Jeśli obraz jest ucięty (czarny dół), ale czytelny = mamy sukces!")

if __name__ == "__main__":
    extract_safe()
