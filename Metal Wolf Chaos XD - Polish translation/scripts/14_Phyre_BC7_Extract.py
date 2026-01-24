import os
import struct

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted_bc7")

def create_dx10_bc7_header(width, height):
    # BC7 zajmuje tyle samo miejsca co DXT5 (1 bajt na piksel, blok 16 bajtów)
    # Ale wymaga nagłówka DX10
    linear_size = max(1, width // 4) * max(1, height // 4) * 16
    
    # 1. Standardowy nagłówek DDS (128 bajtów)
    header = bytearray(128)
    header[0:4] = b'\x44\x44\x53\x20' # Magic 'DDS '
    struct.pack_into('<I', header, 4, 124) # Size
    
    # Flags: CAPS | HEIGHT | WIDTH | PIXELFORMAT | LINEARSIZE
    struct.pack_into('<I', header, 8, 0x00081007) 
    
    struct.pack_into('<I', header, 12, height)
    struct.pack_into('<I', header, 16, width)
    struct.pack_into('<I', header, 20, linear_size)
    struct.pack_into('<I', header, 28, 1) # Mipmaps = 1 (żeby nie szukał dalej)
    
    # PixelFormat (Standardowy DDS mówi: "Patrz na rozszerzenie DX10")
    struct.pack_into('<I', header, 76, 32) # Size
    struct.pack_into('<I', header, 80, 0x00000004) # DDPF_FOURCC
    header[84:88] = b'DX10' # FourCC = 'DX10' (To klucz!)
    
    struct.pack_into('<I', header, 108, 0x00001000) # Caps (Texture)
    
    # 2. Nagłówek rozszerzony DX10 (20 bajtów)
    # struct DDS_HEADER_DXT10 {
    #   DXGI_FORMAT dxgiFormat;
    #   D3D10_RESOURCE_DIMENSION resourceDimension;
    #   UINT miscFlag;
    #   UINT arraySize;
    #   UINT miscFlags2;
    # }
    dx10_header = bytearray(20)
    
    # DXGI_FORMAT_BC7_UNORM = 98 (0x62)
    # DXGI_FORMAT_BC7_UNORM_SRGB = 99 (0x63) - Spróbujmy zwykłego 98
    struct.pack_into('<I', dx10_header, 0, 98) 
    
    # D3D10_RESOURCE_DIMENSION_TEXTURE2D = 3
    struct.pack_into('<I', dx10_header, 4, 3)
    
    # miscFlag = 0
    # arraySize = 1
    struct.pack_into('<I', dx10_header, 12, 1)
    # miscFlags2 = 0 (Alpha Mode Unknown)
    
    return header + dx10_header, linear_size

def extract_bc7():
    print(f"--- 14_Phyre_BC7_Extract (DX10 Mode) ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # Znajdź znaczniki "Textures/"
    offsets = []
    start = 0
    while True:
        idx = data.find(b"Textures/", start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + 1

    print(f"Znaleziono {len(offsets)} tekstur.")

    for i in range(len(offsets)):
        meta_start = offsets[i]
        
        # Nazwa
        end_name = data.find(b'\x00', meta_start)
        clean_name = os.path.basename(data[meta_start:end_name].decode('utf-8', errors='ignore'))
        
        # Koniec chunka
        if i < len(offsets) - 1:
            chunk_end = offsets[i+1]
        else:
            chunk_end = len(data)
            
        # Start danych (Heurystyka +128 bajtów od nazwy - dostosuj jeśli utnie grafikę)
        data_start = meta_start + 128
        raw_chunk = data[data_start:chunk_end]
        actual_size = len(raw_chunk)
        
        # Szacowanie rozdzielczości (BC7 ma taką samą wagę jak DXT5)
        if actual_size < 500000: w, h = 1024, 1024
        elif actual_size < 2000000: w, h = 2048, 2048
        elif actual_size < 5000000: w, h = 2048, 2048
        else: w, h = 4096, 4096
        
        # Generowanie nagłówka DX10
        full_header, required_size = create_dx10_bc7_header(w, h)
        
        # Padding (Dopełnienie zerami)
        final_data = bytearray(raw_chunk)
        if len(final_data) < required_size:
            final_data.extend(b'\x00' * (required_size - len(final_data)))
        else:
            final_data = final_data[:required_size]

        out_name = f"bc7_{i:02d}_{clean_name}_{w}x{h}.dds"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        with open(out_path, "wb") as out_f:
            out_f.write(full_header + final_data)
            
        print(f"[{i:02d}] {clean_name} -> {w}x{h} (BC7) | Saved to {out_name}")

    print(f"\nGotowe. Sprawdź folder '{OUTPUT_DIR}'.")
    print("Otwórz w GIMP. Jeśli widzisz obraz - wygraliśmy.")

if __name__ == "__main__":
    extract_bc7()
