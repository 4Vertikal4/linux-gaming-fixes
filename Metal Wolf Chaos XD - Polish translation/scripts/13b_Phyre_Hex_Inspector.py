import os
import struct

WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre")
# Celujemy w ten plik 2048x2048 (teoretycznie)
TARGET_NAME = b"MENUTEX_130_02.dds" 

def inspect():
    with open(SOURCE_FILE, "rb") as f:
        data = f.read()

    name_offset = data.find(TARGET_NAME)
    if name_offset == -1: return

    print(f"File: {TARGET_NAME.decode()} @ {hex(name_offset)}")
    
    # Pokażmy 128 bajtów PO nazwie
    start = name_offset + len(TARGET_NAME) + 1 # +1 bo null byte
    
    print("\n[Raw Data Dump]")
    for i in range(0, 128, 4):
        chunk = data[start+i : start+i+4]
        val_int = struct.unpack('<I', chunk)[0]
        val_hex = chunk.hex()
        print(f"+{i:03d}: {val_hex} | Int: {val_int} | Hex: {hex(val_int)}")

if __name__ == "__main__":
    inspect()
