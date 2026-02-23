import sys
import os
import argparse
import struct

# KONFIGURACJA MWC XD
BLOCK_W = 4
BLOCK_H = 4
BYTES_PER_BLOCK = 16
DEFAULT_TILE_SIZE = 64 # 64x64 piksele

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Final Tile Swizzler (Aligned)")
    parser.add_argument("mode", choices=["unswizzle", "reswizzle"], help="Tryb pracy")
    parser.add_argument("input_file", help="Plik wejściowy")
    parser.add_argument("output_file", help="Plik wyjściowy")
    parser.add_argument("--width", type=int, help="Wymuś szerokość")
    parser.add_argument("--height", type=int, help="Wymuś wysokość")
    parser.add_argument("--tile", type=int, default=DEFAULT_TILE_SIZE, help="Rozmiar kafelka")
    return parser.parse_args()

def parse_dds_header(data):
    if data[0:4] != b'DDS ':
        print("[!] Brak nagłówka DDS.")
        return 0, 0, 0, 0
    
    height = struct.unpack('<I', data[12:16])[0]
    width = struct.unpack('<I', data[16:20])[0]
    four_cc = data[84:88]
    
    header_raw_size = 128
    if four_cc == b'DX10':
        header_raw_size = 148
    
    # Obliczanie paddingu (wyrównanie do 16 bajtów)
    padding = 0
    remainder = header_raw_size % 16
    if remainder != 0:
        padding = 16 - remainder
    
    print(f"[*] Nagłówek: {header_raw_size} bajtów. Padding gry: {padding} bajtów.")
    return header_raw_size, padding, width, height

def process_texture(args):
    print(f"--- MWC XD FINAL TILE OPS: {args.mode.upper()} ---")

    try:
        with open(args.input_file, "rb") as f:
            full_data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[!] Brak pliku {args.input_file}")
        sys.exit(1)

    header_size, padding, dds_w, dds_h = parse_dds_header(full_data)
    
    width = args.width if args.width else dds_w
    height = args.height if args.height else dds_h
    
    # LOGIKA PADDINGU
    if args.mode == "unswizzle":
        # Czytamy z gry: Omijamy padding, żeby naprawić kolory dla GIMP
        data_start_offset = header_size + padding
        texture_data = full_data[data_start_offset:]
        header_data = full_data[:header_size]
    else:
        # Czytamy z GIMP: Zakładamy, że plik jest czysty (bez paddingu)
        data_start_offset = header_size
        texture_data = full_data[data_start_offset:]
        header_data = full_data[:header_size] 
    
    img_w_blocks = width // BLOCK_W
    img_h_blocks = height // BLOCK_H
    
    # Weryfikacja długości danych
    expected_len = img_w_blocks * img_h_blocks * BYTES_PER_BLOCK
    if len(texture_data) < expected_len:
        print(f"[!] Dane za krótkie! Jest {len(texture_data)}, wymagane {expected_len}. Kontynuuję...")

    output_data = bytearray(len(texture_data))
    
    tile_w_blocks = args.tile // BLOCK_W
    tile_h_blocks = args.tile // BLOCK_H
    tiles_per_row = img_w_blocks // tile_w_blocks
    
    print(f"[*] Przetwarzanie: {width}x{height}, Padding usunięty/dodany: {padding}")
    
    # PĘTLA SWIZZLINGU
    for by in range(img_h_blocks):
        for bx in range(img_w_blocks):
            linear_idx = (by * img_w_blocks + bx) * BYTES_PER_BLOCK
            
            tile_x = bx // tile_w_blocks
            tile_y = by // tile_h_blocks
            local_bx = bx % tile_w_blocks
            local_by = by % tile_h_blocks
            
            tile_idx = tile_y * tiles_per_row + tile_x
            local_idx = local_by * tile_w_blocks + local_bx
            
            tile_size_bytes = tile_w_blocks * tile_h_blocks * BYTES_PER_BLOCK
            swizzled_idx = (tile_idx * tile_size_bytes) + (local_idx * BYTES_PER_BLOCK)
            
            if linear_idx + BYTES_PER_BLOCK <= len(output_data) and swizzled_idx + BYTES_PER_BLOCK <= len(texture_data):
                 if args.mode == "unswizzle":
                    chunk = texture_data[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK]
                    output_data[linear_idx : linear_idx + BYTES_PER_BLOCK] = chunk
                 else:
                    chunk = texture_data[linear_idx : linear_idx + BYTES_PER_BLOCK]
                    output_data[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK] = chunk

    # ZAPIS
    with open(args.output_file, "wb") as f:
        f.write(header_data)
        if args.mode == "reswizzle":
            f.write(b'\x00' * padding) # Przywracamy padding dla silnika gry
        f.write(output_data)
        
    print(f"[+] Gotowe: {args.output_file}")

if __name__ == "__main__":
    process_texture(get_params())
