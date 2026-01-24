import os
import struct
import math

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted_raw")
MAP_FILE = os.path.join(WORK_DIR, "texture_map_raw.json")

# Standardowe nagłówki DDS (DXT5) dla typowych rozmiarów
# Magic + Header (124 bytes) = 128 bytes total
def create_dxt5_header(width, height):
    # DDS Magic
    header = b'\x44\x44\x53\x20'
    # header size (124), flags (caps+pixelformat+width+height+linearsize)
    header += struct.pack('<I', 124) 
    header += struct.pack('<I', 0x00021007) # flags
    header += struct.pack('<I', height)
    header += struct.pack('<I', width)
    # Linear size (width * height) for DXT5 (1 byte per pixel effective)
    header += struct.pack('<I', width * height) 
    header += b'\x00' * 4 # Depth
    header += struct.pack('<I', 1) # Mipmaps (set to 1 for safety)
    header += b'\x00' * 44 # Reserved
    # Pixel Format (32 bytes)
    header += struct.pack('<I', 32) # size
    header += struct.pack('<I', 0x00000004) # flags (DDPF_FOURCC)
    header += b'DXT5' # FourCC
    header += b'\x00' * 20 # RGB bitmasks etc
    # Caps
    header += struct.pack('<I', 0x00001000) # caps1 (texture)
    header += b'\x00' * 16 # caps2-4 + reserved
    return header

def estimate_resolution(size_bytes):
    # DXT5 zajmuje 1 bajt na piksel (16 bajtów na blok 4x4)
    # Area = size_bytes
    # Side = sqrt(size_bytes)
    # Zaokrąglamy do najbliższej potęgi 2
    side = int(math.sqrt(size_bytes))
    power = 1
    while power < side:
        power *= 2
    
    # Sprawdzamy, czy lepiej pasuje power czy power/2
    # Np. dla 1024x512 rozmiar to 512KB. Sqrt to ~724. Power to 1024.
    # Wolisz zawyżyć szerokość (GIMP wyświetli połowę pustą) czy zaniżyć (GIMP wyświetli sieczkę)?
    # Bezpieczniej przyjąć kwadrat.
    return power, power

def extract_raw_chunks():
    print(f"--- 11c_Phyre_Raw_Extract (Frankenstein Mode) ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # 1. Znajdź wszystkie wystąpienia "Textures/"
    offsets = []
    search_str = b"Textures/"
    start = 0
    while True:
        idx = data.find(search_str, start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + 1

    print(f"Znaleziono {len(offsets)} znaczników tekstur.")

    map_data = []

    # 2. Cięcie
    for i in range(len(offsets)):
        # Początek metadanych tekstury
        meta_start = offsets[i]
        
        # Nazwa pliku (do pierwszego nulla)
        end_name = data.find(b'\x00', meta_start)
        filename_raw = data[meta_start:end_name].decode('utf-8', errors='ignore')
        clean_name = os.path.basename(filename_raw) # Tylko nazwa pliku bez ścieżki
        
        # Gdzie zaczynają się dane? 
        # Heurystyka: Szukamy "PTex" po nazwie, a dane są kawałek dalej.
        # W tym trybie "Brute Force" założymy, że dane zaczynają się np. 128 bajtów po nazwie
        # albo po prostu wytniemy blok od [Start obecnego] do [Start następnego] 
        # i usuniemy nagłówek ręcznie w GIMP (offset hack).
        
        # Ale spróbujmy mądrzej:
        # Pomiędzy 'meta_start' a następnym 'offsets[i+1]' jest cała tekstura.
        # Dane tekstury zazwyczaj są wyrównane do 256 bajtów (0x100).
        
        # Ustalmy koniec chunka
        if i < len(offsets) - 1:
            chunk_end = offsets[i+1]
        else:
            chunk_end = len(data)
            
        # Zgrubny rozmiar (zawiera metadane i padding)
        raw_size = chunk_end - meta_start
        
        # Szukamy początku danych pikseli.
        # Zazwyczaj po nazwie jest PTex (offset X) a potem padding zerami do wyrównania.
        # Przyjmijmy offset startowy danych jako np. meta_start + 256 bajtów (bezpieczny margines)
        # To spowoduje, że na początku pliku DDS będą śmieci, ale obraz będzie widoczny niżej.
        data_start = meta_start + 128 # Eksperymentalnie
        
        # Obliczamy rozmiar "czystych" danych do estymacji
        pixel_data_size = chunk_end - data_start
        
        # Zgadujemy rozdzielczość
        w, h = estimate_resolution(pixel_data_size)
        
        # Jeśli chunk jest bardzo mały (metadane), ignorujemy
        if pixel_data_size < 1024: 
            continue

        # Pobieramy dane
        chunk_data = data[data_start:chunk_end]
        
        # Doklejamy nagłówek
        header = create_dxt5_header(w, h)
        final_dds = header + chunk_data
        
        out_name = f"raw_{i:02d}_{clean_name}_{w}x{h}.dds"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        with open(out_path, "wb") as out_f:
            out_f.write(final_dds)
            
        print(f"[{i:02d}] {clean_name} -> {out_name} (Est: {w}x{h}) Size: {len(chunk_data)}")

        map_data.append({
            'id': i,
            'original_name': clean_name,
            'start_offset': data_start, # To jest miejsce gdzie wstrzykniemy
            'end_offset': chunk_end,
            'width': w,
            'height': h,
            'filename': out_name
        })

    import json
    with open(MAP_FILE, "w") as jf:
        json.dump(map_data, jf, indent=4)
        
    print(f"\nZapisano pliki w {OUTPUT_DIR}. Otwórz je w GIMP.")
    print("UWAGA: Na górze obrazka mogą być 'śmieci' (pozostałości metadanych).")
    print("Najważniejsze, żebyś widział przyciski.")

if __name__ == "__main__":
    extract_raw_chunks()
