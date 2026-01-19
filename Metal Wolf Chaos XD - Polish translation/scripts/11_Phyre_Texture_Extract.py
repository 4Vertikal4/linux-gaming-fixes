import os
import struct
import json

# === KONFIGURACJA ===
# Ścieżki relatywne do folderu scripts/
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted")
MAP_FILE = os.path.join(WORK_DIR, "texture_map.json")

def scan_and_extract():
    print(f"--- 11_Phyre_Texture_Extract v1.0 ---")
    
    if not os.path.exists(WORK_DIR):
        print(f"BŁĄD: Nie znaleziono katalogu roboczego: {os.path.abspath(WORK_DIR)}")
        print("Utwórz folder 'phyre_work' obok folderu 'scripts' i wrzuć tam plik .phyre.")
        return

    if not os.path.exists(SOURCE_FILE):
        print(f"BŁĄD: Nie znaleziono pliku źródłowego: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Utworzono katalog wyjściowy: {OUTPUT_DIR}")

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    file_size = len(data)
    print(f"Wczytano {os.path.basename(SOURCE_FILE)} ({file_size} bajtów). Skanowanie...")

    # Szukamy magic bytes: 'DDS ' (0x44 0x44 0x53 0x20)
    offsets = []
    offset = 0
    while True:
        offset = data.find(b'\x44\x44\x53\x20', offset)
        if offset == -1:
            break
        offsets.append(offset)
        offset += 4

    print(f"Znaleziono {len(offsets)} tekstur DDS.")

    map_data = []

    for i, start_offset in enumerate(offsets):
        # Koniec obecnej tekstury to początek następnej lub koniec pliku
        if i < len(offsets) - 1:
            end_offset = offsets[i+1]
        else:
            end_offset = file_size

        chunk_size = end_offset - start_offset
        raw_data = data[start_offset:end_offset]

        # Próba odczytu nagłówka DDS (wysokość/szerokość/format)
        # Header DDS ma 124 bajty + 4 magic bytes
        try:
            height = struct.unpack('<I', raw_data[12:16])[0]
            width = struct.unpack('<I', raw_data[16:20])[0]
            # FourCC code (np. DXT1, DXT5) jest na offsecie 84
            fmt_code = raw_data[84:88].decode('utf-8', errors='ignore').strip('\x00')
        except:
            height, width, fmt_code = (0, 0, "UNK")

        # Nazwa pliku zawiera ID, wymiary i format dla ułatwienia pracy w GIMP
        filename = f"tex_{i:03d}_{width}x{height}_{fmt_code}.dds"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "wb") as out_f:
            out_f.write(raw_data)

        print(f"[{i:03d}] Offset: {hex(start_offset)} | MaxSize: {chunk_size} | {width}x{height} | {fmt_code}")

        # Zapis do mapy - to jest KLUCZOWE dla injectora
        map_data.append({
            'id': i,
            'original_offset': start_offset,
            'max_size': chunk_size,
            'width': width,
            'height': height,
            'format': fmt_code,
            'filename': filename
        })

    with open(MAP_FILE, "w") as jf:
        json.dump(map_data, jf, indent=4)
    
    print(f"\nSUKCES. Wyeksportowano {len(offsets)} plików.")
    print(f"Mapa offsetów zapisana w: {MAP_FILE}")
    print("Możesz teraz edytować pliki w folderze 'extracted'.")
    print("Edytowane pliki zapisuj w folderze 'modified' (w phyre_work).")

if __name__ == "__main__":
    scan_and_extract()
