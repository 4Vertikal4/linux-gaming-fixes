import sys
import os
import json
import argparse

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Phyre Smart Injector")
    parser.add_argument("phyre_file", help="Główny plik kontenera (.phyre)")
    parser.add_argument("json_map", help="Mapa tekstur (.json)")
    parser.add_argument("texture_name", help="Nazwa tekstury (np. MENUTEX_130_02)")
    parser.add_argument("input_dds", help="Plik DDS do wstrzyknięcia")
    return parser.parse_args()

def inject_texture(args):
    print(f"--- PHYRE SMART INJECTOR V3: {args.texture_name} ---")

    # 1. Wczytaj mapę
    try:
        with open(args.json_map, "r") as f:
            texture_map = json.load(f)
    except Exception as e:
        print(f"[!] Błąd odczytu mapy JSON: {e}")
        sys.exit(1)

    # 2. Szukanie wpisu
    target_info = None
    if isinstance(texture_map, list):
        for entry in texture_map:
            name_in_json = entry.get('filename') or entry.get('name') or ""
            if args.texture_name in name_in_json:
                target_info = entry
                break
    else:
        print("[!] Mapa JSON nie jest listą! Sprawdź format.")
        sys.exit(1)

    if not target_info:
        print(f"[!] Nie znaleziono tekstury '{args.texture_name}' w mapie JSON.")
        sys.exit(1)

    print(f"[*] Znaleziono wpis: {target_info.get('filename', 'Unknown')}")

    # 3. Logika Offsetu i Rozmiaru (POPRAWIONA)
    offset = None
    size = None

    # A. Próba znalezienia offsetu
    if 'start_offset' in target_info:
        offset = target_info['start_offset']
    elif 'offset' in target_info:
        offset = target_info['offset']
    
    # B. Próba obliczenia lub znalezienia rozmiaru
    if 'end_offset' in target_info and 'start_offset' in target_info:
        # Obliczamy rozmiar z różnicy offsetów
        size = target_info['end_offset'] - target_info['start_offset']
    elif 'size' in target_info:
        size = target_info['size']

    # Weryfikacja danych
    if offset is None or size is None:
        print(f"[!] BŁĄD DANYCH: Nie udało się ustalić offsetu lub rozmiaru.")
        print(f"    Dane wpisu: {target_info}")
        sys.exit(1)

    print(f"[*] Cel namierzony: Offset {offset} (0x{offset:X})")
    print(f"[*] Miejsce w kontenerze: {size} bajtów")

    # 4. Wczytaj nowy plik DDS
    try:
        with open(args.input_dds, "rb") as f:
            new_data = f.read()
    except Exception as e:
        print(f"[!] Błąd odczytu pliku wejściowego DDS: {e}")
        sys.exit(1)

    input_len = len(new_data)
    print(f"[*] Wczytano nowy plik: {input_len} bajtów")

    # 5. Weryfikacja rozmiaru
    if input_len > size:
        diff = input_len - size
        print(f"[!] BŁĄD KRYTYCZNY: Nowy plik jest za duży o {diff} bajtów!")
        sys.exit(1)

    if input_len < size:
        diff = size - input_len
        print(f"[*] INFO: Nowy plik jest mniejszy o {diff} bajtów.")
        print("    Dopełniam zerami (padding), aby zachować strukturę pliku.")
        new_data += b'\x00' * diff

    # 6. Iniekcja
    print("[*] Wykonuję operację zapisu...")
    try:
        with open(args.phyre_file, "r+b") as f:
            f.seek(offset)
            f.write(new_data)
    except Exception as e:
        print(f"[!] Błąd zapisu do pliku .phyre: {e}")
        sys.exit(1)

    print("[+] SUKCES! Tekstura podmieniona.")

if __name__ == "__main__":
    params = get_params()
    inject_texture(params)
