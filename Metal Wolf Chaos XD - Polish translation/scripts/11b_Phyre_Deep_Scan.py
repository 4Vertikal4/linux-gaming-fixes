import os
import struct

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")

def hex_dump(data, start, length=16):
    return " ".join(f"{b:02X}" for b in data[start:start+length])

def deep_scan():
    print(f"--- 11b_Phyre_Deep_Scan v1.0 ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    print(f"Rozmiar pliku: {len(data)} bajtów")
    
    # 1. Sprawdźmy nagłówek pliku
    print(f"\n[NAGŁÓWEK PLIKU (0-32 bytes)]")
    print(hex_dump(data, 0, 32))
    print(f"ASCII: {data[0:16]}")

    # 2. Szukamy nazw plików tekstur, o których wiemy
    search_term = b"MENUTEX"
    print(f"\n[SZUKANIE '{search_term.decode()}']")
    
    offset = 0
    count = 0
    while True:
        offset = data.find(search_term, offset)
        if offset == -1:
            break
        
        # Pokażmy co jest PRZED nazwą (często tam są rozmiary/offsety)
        context_start = max(0, offset - 32)
        context_end = min(len(data), offset + 48)
        
        print(f"\n--- Znalezisko #{count+1} @ {hex(offset)} ---")
        print(f"Context Hex (od -32): {hex_dump(data, context_start, 80)}")
        
        # Próba odczytania całego stringa
        try:
            # Szukamy końca stringa (0x00)
            end_str = data.find(b'\x00', offset)
            full_name = data[offset:end_str].decode('utf-8', errors='ignore')
            print(f"Full Name: {full_name}")
        except:
            pass

        count += 1
        offset += 1
        if count >= 5: # Wystarczy nam 5 pierwszych próbek
            print("... (przerwano po 5 próbkach)")
            break

    if count == 0:
        print("Nie znaleziono ciągu 'MENUTEX'. Spróbujmy 'Textures/'")
        # Tu można by dodać fallback

if __name__ == "__main__":
    deep_scan()
