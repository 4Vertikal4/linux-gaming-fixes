import sys
import os
import json
import argparse

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Phyre Texture Injector")
    parser.add_argument("phyre_file", help="Główny plik kontenera (.phyre)")
    parser.add_argument("json_map", help="Mapa tekstur (.json)")
    parser.add_argument("texture_name", help="Nazwa tekstury do podmienienia (np. MENUTEX_130_02)")
    parser.add_argument("input_dds", help="Plik DDS do wstrzyknięcia (musi mieć idealny rozmiar!)")
    return parser.parse_args()

def inject_texture(args):
    print(f"--- PHYRE INJECTOR: {args.texture_name} ---")
    
    # 1. Wczytaj mapę, żeby znaleźć offset
    try:
        with open(args.json_map, "r") as f:
            texture_map = json.load(f)
    except Exception as e:
        print(f"[!] Błąd odczytu mapy JSON: {e}")
        sys.exit(1)
        
    # Szukanie wpisu
    target_info = None
    for entry in texture_map:
        if args.texture_name in entry['filename']:
            target_info = entry
            break
            
    if not target_info:
        print(f"[!] Nie znaleziono tekstury '{args.texture_name}' w mapie JSON.")
        sys.exit(1)
        
    offset = target_info['offset']
    size = target_info['size']
    print(f"[*] Cel namierzony: Offset {hex(offset)}, Oczekiwany rozmiar: {size} bajtów")

    # 2. Wczytaj nowy plik DDS
    try:
        with open(args.input_dds, "rb") as f:
            new_data = f.read()
    except Exception as e:
        print(f"[!] Błąd odczytu pliku wejściowego: {e}")
        sys.exit(1)
        
    print(f"[*] Wczytano nowy plik: {len(new_data)} bajtów")

    # 3. Weryfikacja rozmiaru (KRYTYCZNE!)
    # Uwaga: Phyre często ma padding na końcu pliku wewnątrz kontenera.
    # Nowy plik nie może być WIĘKSZY niż miejsce w kontenerze.
    # Jeśli jest mniejszy, resztę wypełnimy zerami (lub zostawimy stare dane, ale lepiej nadpisać).
    
    if len(new_data) > size:
        diff = len(new_data) - size
        print(f"[!] BŁĄD KRYTYCZNY: Nowy plik jest za duży o {diff} bajtów!")
        print("    Nie można wstrzyknąć bez niszczenia reszty kontenera.")
        sys.exit(1)
    
    if len(new_data) < size:
        diff = size - len(new_data)
        print(f"[!] Ostrzeżenie: Nowy plik jest mniejszy o {diff} bajtów.")
        print("    Zostanie dodany padding zerowy.")
        new_data += b'\x00' * diff

    # 4. Operacja na otwartym sercu
    print("[*] Rozpoczynam iniekcję...")
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
