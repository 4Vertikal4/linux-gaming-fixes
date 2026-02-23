import sys
import os
import argparse
import struct

# KONFIGURACJA METAL WOLF CHAOS XD
BLOCK_W = 4
BLOCK_H = 4
BYTES_PER_BLOCK = 16
DEFAULT_TILE = 64  # Kafelki 64x64 piksele

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Smart Swizzler (DDS Support)")
    parser.add_argument("mode", choices=["unswizzle", "reswizzle"], help="Tryb pracy")
    parser.add_argument("input_file", help="Plik wejściowy (.dds)")
    parser.add_argument("output_file", help="Plik wyjściowy (.dds)")
    parser.add_argument("--width", type=int, help="Wymuś szerokość (opcjonalne)")
    parser.add_argument("--height", type=int, help="Wymuś wysokość (opcjonalne)")
    parser.add_argument("--tile", type=int, default=DEFAULT_TILE, help="Rozmiar kafelka (domyślnie 64)")
    return parser.parse_args()

def parse_dds_header(data):
    # Prosta heurystyka DDS
    if data[0:4] != b'DDS ':
        print("[!] Brak magii 'DDS '. Traktuję plik jako RAW DATA.")
        return 0, 0, 0
    
    header_size = 128
    height = struct.unpack('<I', data[12:16])[0]
    width = struct.unpack('<I', data[16:20])[0]
    
    # Sprawdzenie DX10 header
    pf_flags = struct.unpack('<I', data[80:84])[0]
    four_cc = data[84:88]
    
    if four_cc == b'DX10':
        header_size = 148 # 128 + 20 bajtów DX10 header
        print(f"[*] Wykryto nagłówek DX10 (rozmiar {header_size} bajtów).")
    else:
        print(f"[*] Wykryto standardowy nagłówek DDS (rozmiar {header_size} bajtów).")
        
    return header_size, width, height

def process_texture(args):
    print(f"--- MWC XD SWIZZLER: {args.mode.upper()} ---")

    try:
        with open(args.input_file, "rb") as f:
            full_data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[!] BŁĄD: Brak pliku {args.input_file}")
        sys.exit(1)

    # Analiza nagłówka
    header_offset, dds_w, dds_h = parse_dds_header(full_data)
    
    # Ustalanie wymiarów
    width = args.width if args.width else dds_w
    height = args.height if args.height else dds_h
    
    if width == 0 or height == 0:
        print("[!] BŁĄD: Nie można ustalić wymiarów z nagłówka. Podaj --width i --height ręcznie.")
        sys.exit(1)

    print(f"[*] Przetwarzanie obrazu: {width}x{height}")
    
    # Oddzielenie nagłówka od danych
    header_data = full_data[:header_offset]
    texture_data = full_data[header_offset:]
    
    # Weryfikacja rozmiaru danych
    img_w_blocks = width // BLOCK_W
    img_h_blocks = height // BLOCK_H
    expected_size = img_w_blocks * img_h_blocks * BYTES_PER_BLOCK
    
    if len(texture_data) < expected_size:
        print(f"[!] BŁĄD: Plik za krótki! Oczekiwano {expected_size} bajtów danych, jest {len(texture_data)}.")
        sys.exit(1)
        
    # Bufor na wynik
    output_texture = bytearray(len(texture_data))
    
    tile_w_blocks = args.tile // BLOCK_W
    tile_h_blocks = args.tile // BLOCK_H
    tiles_per_row = img_w_blocks // tile_w_blocks

    print(f"[*] Konfiguracja: {img_w_blocks}x{img_h_blocks} bloków, kafelki {args.tile}px")

    # Główna pętla (iterujemy po obrazie LINIOWYM)
    for by in range(img_h_blocks):
        for bx in range(img_w_blocks):
            
            # Adres w obrazie liniowym
            linear_idx = (by * img_w_blocks + bx) * BYTES_PER_BLOCK
            
            # Adres w obrazie kafelkowym (Morton/Tile Linear)
            tile_x = bx // tile_w_blocks
            tile_y = by // tile_h_blocks
            local_bx = bx % tile_w_blocks
            local_by = by % tile_h_blocks
            
            tile_idx = tile_y * tiles_per_row + tile_x
            local_idx = local_by * tile_w_blocks + local_bx
            
            tile_size = tile_w_blocks * tile_h_blocks * BYTES_PER_BLOCK
            swizzled_idx = (tile_idx * tile_size) + (local_idx * BYTES_PER_BLOCK)
            
            # Kopiowanie bloku 16 bajtów
            if args.mode == "unswizzle":
                # INPUT (Swizzled) -> OUTPUT (Linear)
                chunk = texture_data[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK]
                output_texture[linear_idx : linear_idx + BYTES_PER_BLOCK] = chunk
            else:
                # INPUT (Linear) -> OUTPUT (Swizzled)
                chunk = texture_data[linear_idx : linear_idx + BYTES_PER_BLOCK]
                output_texture[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK] = chunk

    # Składanie pliku wynikowego (Nagłówek + Przeliczone Dane)
    # Jeśli plik wejściowy miał śmieci na końcu (padding), też je doklejamy
    leftover = texture_data[expected_size:]
    final_data = header_data + output_texture[:expected_size] + leftover
    
    with open(args.output_file, "wb") as f:
        f.write(final_data)
        
    print(f"[+] GOTOWE: {args.output_file}")

if __name__ == "__main__":
    process_texture(get_params())
