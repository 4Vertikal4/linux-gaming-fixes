import os
import struct
import sys

# Próba importu LZ4
try:
    import lz4.block
except ImportError:
    print("BŁĄD: Brak biblioteki lz4!")
    print("Zainstaluj ją komendą: pip install lz4")
    sys.exit(1)

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
OUTPUT_DIR = os.path.join(WORK_DIR, "extracted_lz4")

# Cel: MENUTEX_130_02 (Główne Menu)
TARGET_NAME = b"MENUTEX_130_02.dds"
# Oczekiwana rozdzielczość 2048x2048 w DXT5 to dokładnie 4,194,304 bajtów
EXPECTED_UNCOMPRESSED_SIZE = 4194304 
WIDTH = 2048
HEIGHT = 2048

def create_dxt5_header(width, height, size):
    header = bytearray(128)
    header[0:4] = b'\x44\x44\x53\x20' # Magic
    struct.pack_into('<I', header, 4, 124) # Size
    struct.pack_into('<I', header, 8, 0x00081007) # Flags
    struct.pack_into('<I', header, 12, height)
    struct.pack_into('<I', header, 16, width)
    struct.pack_into('<I', header, 20, size) # Linear Size
    struct.pack_into('<I', header, 28, 1) # Mipmaps
    struct.pack_into('<I', header, 76, 32) # PixelFormat Size
    struct.pack_into('<I', header, 80, 0x00000004) # FourCC Flag
    header[84:88] = b'DXT5'
    struct.pack_into('<I', header, 108, 0x00001000) # Caps
    return header

def brute_force_decompress():
    print(f"--- 12_Phyre_LZ4_Test v1.0 ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # 1. Znajdź offset nazwy pliku
    name_offset = data.find(TARGET_NAME)
    if name_offset == -1:
        print("Nie znaleziono pliku docelowego w kontenerze.")
        return

    print(f"Namierzono {TARGET_NAME.decode()} na offsecie {hex(name_offset)}")

    # 2. Heurystyka startu danych
    # Dane skompresowane zazwyczaj zaczynają się kawałek po nazwie.
    # W deep scan widzieliśmy PTex...
    # Spróbujmy znaleźć początek strumienia LZ4 metodą 'sliding window'
    # LZ4 nie ma wyraźnego nagłówka magicznego, więc to będzie trudne.
    # Ale wiemy, że przed danymi często jest podany rozmiar skompresowany.
    
    # Przyjmijmy strefę poszukiwań: od nazwy do +512 bajtów
    search_zone_start = name_offset
    search_zone_end = name_offset + 512
    
    print("Rozpoczynam próby dekompresji (Brute Force Offset)...")
    
    success = False
    
    # Przesuwamy się bajt po bajcie i próbujemy dekompresować
    for offset in range(search_zone_start, search_zone_end):
        # Zakładamy, że skompresowany chunk ma max 2MB (dla pliku 4MB to ok. 50% ratio)
        # Bierzemy spory kawał danych
        chunk_candidate = data[offset : offset + 2500000] 
        
        try:
            # Próba dekompresji
            decompressed = lz4.block.decompress(chunk_candidate, uncompressed_size=EXPECTED_UNCOMPRESSED_SIZE)
            
            # Jeśli funkcja nie rzuciła wyjątkiem i zwróciła dane o oczekiwanej długości...
            if len(decompressed) == EXPECTED_UNCOMPRESSED_SIZE:
                print(f"✅ SUKCES! Zdekompresowano dane na offsecie: {hex(offset)}")
                
                # Zapisz wynik
                header = create_dxt5_header(WIDTH, HEIGHT, EXPECTED_UNCOMPRESSED_SIZE)
                final_dds = header + decompressed
                
                out_path = os.path.join(OUTPUT_DIR, "DECOMPRESSED_MENU.dds")
                with open(out_path, "wb") as out_f:
                    out_f.write(final_dds)
                    
                print(f"Zapisano: {out_path}")
                print("Otwórz ten plik w GIMP. Jeśli widzisz przyciski - WYGRALIŚMY.")
                success = True
                break
                
        except Exception:
            # Błąd dekompresji to norma przy złym offsecie, ignorujemy
            continue
            
    if not success:
        print("❌ Nie udało się zdekompresować danych w pobliżu nagłówka.")
        print("Możliwe przyczyny:")
        print("1. Dane nie są LZ4.")
        print("2. Oczekiwany rozmiar po dekompresji jest inny niż 4194304.")
        print("3. Struktura pliku jest bardziej skomplikowana.")

if __name__ == "__main__":
    brute_force_decompress()
