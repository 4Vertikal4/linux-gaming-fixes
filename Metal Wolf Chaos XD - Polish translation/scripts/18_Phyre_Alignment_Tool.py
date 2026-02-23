import sys
import os
import argparse
import struct

# KONFIGURACJA
# Header DX10 ma 148 bajtów.
# 148 nie dzieli się przez 16 (rozmiar bloku BC7). Reszta to 4.
# Żeby wyrównać do 16, potrzebujemy 12 bajtów paddingu (148 + 12 = 160).
HEADER_SIZE = 148
PADDING_SIZE = 12

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Alignment Fixer (Rainbow Remover)")
    parser.add_argument("mode", choices=["clean", "restore"], help="Tryb pracy")
    parser.add_argument("input_file", help="Plik wejściowy (.dds)")
    parser.add_argument("output_file", help="Plik wyjściowy (.dds)")
    return parser.parse_args()

def process_file(args):
    print(f"--- MWC XD ALIGNMENT TOOL: {args.mode.upper()} ---")
    
    try:
        with open(args.input_file, "rb") as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[!] Błąd: Nie znaleziono pliku {args.input_file}")
        sys.exit(1)

    # Weryfikacja nagłówka DDS
    if data[0:4] != b'DDS ':
        print("[!] OSTRZEŻENIE: Brak nagłówka DDS! Operacja może się nie udać.")
    
    # Sprawdzenie czy to DX10
    if data[84:88] == b'DX10':
        print("[*] Wykryto nagłówek DX10 (Standard).")
    else:
        print("[!] Uwaga: To nie wygląda na nagłówek DX10. Kontynuuję na własne ryzyko.")

    if args.mode == "clean":
        # TRYB DLA GIMPA: Usuwamy padding, żeby GIMP czytał dane od razu po nagłówku
        # Input:  [Header 148] + [Padding 12] + [Data...]
        # Output: [Header 148] + [Data...]
        
        print(f"[*] Usuwanie {PADDING_SIZE} bajtów paddingu (Dla GIMPa)...")
        
        # Bierzemy nagłówek
        header = data[:HEADER_SIZE]
        
        # Bierzemy dane, przeskakując padding
        # Zakładamy, że padding jest ZARAZ PO nagłówku (offset 148-160)
        pixel_data = data[HEADER_SIZE + PADDING_SIZE:]
        
        final_data = header + pixel_data
        
    else: # restore
        # TRYB DLA GRY: Dodajemy padding z powrotem
        # Input:  [Header 148] + [Data...] (z GIMPa)
        # Output: [Header 148] + [Padding 12] + [Data...]
        
        print(f"[*] Przywracanie {PADDING_SIZE} bajtów paddingu (Dla Gry)...")
        
        header = data[:HEADER_SIZE]
        pixel_data = data[HEADER_SIZE:]
        
        padding_bytes = b'\x00' * PADDING_SIZE
        
        final_data = header + padding_bytes + pixel_data

    # Zapis
    with open(args.output_file, "wb") as f:
        f.write(final_data)
        
    print(f"[+] Sukces! Zapisano: {args.output_file}")
    print(f"    Rozmiar wejściowy: {len(data)} -> Wyjściowy: {len(final_data)}")

if __name__ == "__main__":
    process_file(get_params())
