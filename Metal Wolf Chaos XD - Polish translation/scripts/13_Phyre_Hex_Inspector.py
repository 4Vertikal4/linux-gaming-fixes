import os

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
TARGET_NAME = b"MENUTEX_130_02.dds"

def hex_dump(data, start_offset, length=128):
    chunk = data[start_offset : start_offset + length]
    print(f"\n--- HEX DUMP @ {hex(start_offset)} ---")
    
    # Wyświetlanie w rzędach po 16 bajtów
    for i in range(0, len(chunk), 16):
        row = chunk[i:i+16]
        hex_vals = " ".join(f"{b:02X}" for b in row)
        ascii_vals = "".join((chr(b) if 32 <= b < 127 else ".") for b in row)
        print(f"{hex(start_offset + i)}:  {hex_vals:<48}  |{ascii_vals}|")

def inspect():
    print(f"--- 13_Phyre_Hex_Inspector v1.0 ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"Brak pliku: {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    # Znajdź nazwę pliku
    name_offset = data.find(TARGET_NAME)
    if name_offset == -1:
        print("Nie znaleziono pliku.")
        return

    print(f"Znaleziono nazwę '{TARGET_NAME.decode()}' na offsecie {hex(name_offset)}")
    
    # Pokażmy bajty OD RAZU po nazwie pliku (+ długość nazwy)
    # Interesuje nas obszar do 256 bajtów po nazwie.
    # Tam powinny być metadane (rozmiar) i początek danych (magiczne bajty).
    
    start_inspection = name_offset + len(TARGET_NAME)
    
    # Cofnijmy się o kilka bajtów, żeby widzieć koniec nazwy (dla kontekstu)
    hex_dump(data, start_inspection - 4, 256)

    print("\nCzego szukamy?")
    print("- 78 9C / 78 DA (Zlib)")
    print("- 1F 8B (Gzip)")
    print("- 04 22 4D 18 (LZ4 Frame)")
    print("- PTex (Już to widzieliśmy, ale co jest PO TYM?)")

if __name__ == "__main__":
    inspect()
