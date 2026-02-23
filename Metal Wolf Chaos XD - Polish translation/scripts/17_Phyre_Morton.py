import sys
import os
import argparse
import struct

# KONFIGURACJA MWC XD
BLOCK_W = 4
BLOCK_H = 4
BYTES_PER_BLOCK = 16

def get_params():
    parser = argparse.ArgumentParser(description="MWC XD Morton/Z-Curve Swizzler")
    parser.add_argument("mode", choices=["unswizzle", "reswizzle"], help="Tryb pracy")
    parser.add_argument("input_file", help="Plik wejściowy (.dds)")
    parser.add_argument("output_file", help="Plik wyjściowy (.dds)")
    parser.add_argument("--width", type=int, help="Wymuś szerokość")
    parser.add_argument("--height", type=int, help="Wymuś wysokość")
    return parser.parse_args()

# Magia bitowa dla Morton Codes (Z-Curve)
# Rozdziela bity liczby (np. ABC -> 00A00B00C)
def spread_bits(n):
    n = (n | (n << 8)) & 0x00FF00FF
    n = (n | (n << 4)) & 0x0F0F0F0F
    n = (n | (n << 2)) & 0x33333333
    n = (n | (n << 1)) & 0x55555555
    return n

# Odwraca spread_bits (Compact bits)
def compact_bits(n):
    n = n & 0x55555555
    n = (n ^ (n >> 1)) & 0x33333333
    n = (n ^ (n >> 2)) & 0x0F0F0F0F
    n = (n ^ (n >> 4)) & 0x00FF00FF
    n = (n ^ (n >> 8)) & 0x0000FFFF
    return n

def get_morton_idx(x, y):
    return spread_bits(x) | (spread_bits(y) << 1)

def get_coord_from_morton(m):
    x = compact_bits(m)
    y = compact_bits(m >> 1)
    return x, y

def parse_dds_header(data):
    if data[0:4] != b'DDS ':
        return 0, 0, 0
    
    height = struct.unpack('<I', data[12:16])[0]
    width = struct.unpack('<I', data[16:20])[0]
    four_cc = data[84:88]
    
    header_raw_size = 128
    if four_cc == b'DX10':
        header_raw_size = 148
    
    # KRYTYCZNA POPRAWKA ALIGNMENTU
    # Dane muszą zaczynać się na granicy 16 bajtów (rozmiar bloku BC7)
    # Jeśli nagłówek ma 148, to najbliższa granica to 160.
    padding = 0
    remainder = header_raw_size % 16
    if remainder != 0:
        padding = 16 - remainder
    
    final_header_size = header_raw_size + padding
    print(f"[*] Nagłówek: {header_raw_size} bajtów + {padding} bajtów paddingu = Offset {final_header_size}")
    
    return final_header_size, width, height

def process_texture(args):
    print(f"--- MWC XD MORTON OPS: {args.mode.upper()} ---")

    try:
        with open(args.input_file, "rb") as f:
            full_data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[!] Brak pliku {args.input_file}")
        sys.exit(1)

    header_offset, dds_w, dds_h = parse_dds_header(full_data)
    width = args.width if args.width else dds_w
    height = args.height if args.height else dds_h

    if width == 0:
        print("[!] Nie udało się odczytać wymiarów.")
        sys.exit(1)

    # Przygotowanie danych
    header_data = full_data[:header_offset]
    texture_data = full_data[header_offset:]
    
    # Wymiary w blokach
    w_blocks = width // BLOCK_W
    h_blocks = height // BLOCK_H
    
    expected_size = w_blocks * h_blocks * BYTES_PER_BLOCK
    
    # Jeśli plik jest mniejszy niż oczekiwano, to problem
    if len(texture_data) < expected_size:
        print(f"[!] OSTRZEŻENIE: Plik za krótki! Oczekiwano {expected_size}, jest {len(texture_data)}")
        # Kontynuujemy, ale może wywalić błąd
    
    output_texture = bytearray(len(texture_data))
    
    print(f"[*] Przetwarzanie: {width}x{height} ({w_blocks}x{h_blocks} bloków)")

    # Główna pętla
    count = 0
    for y in range(h_blocks):
        for x in range(w_blocks):
            # Adres Liniowy (Normalny)
            linear_idx = (y * w_blocks + x) * BYTES_PER_BLOCK
            
            # Adres Morton (Phyre)
            # Uwaga: Morton zazwyczaj działa na pełnych kwadratach POT (Power of Two)
            # Ale spróbujemy "naiwnego" Mortona na współrzędnych
            morton_idx_abstract = get_morton_idx(x, y)
            
            # Ponieważ obraz nie jest kwadratem POT (1152 nie jest potęgą 2),
            # indeks Mortona może wyjść daleko poza zakres pliku.
            # Silniki radzą sobie z tym mapując Morton -> Offset w pamięci
            # W PhyreEngine często używa się "Tiled Morton" (Linear Macroblocks + Morton inside).
            # Spróbujmy czystego Mortona, ale jeśli wyjdzie poza zakres, to znaczy że 
            # musimy użyć innej strategii.
            
            # STRATEGIA HYBRYDOWA:
            # Zakładamy, że 1152x1152 jest podzielone na duże kafelki (np. 128x128),
            # a w środku nich jest Morton. 1152 dzieli się przez 128 (daje 9).
            # Sprawdźmy to:
            
            # --- WARIANT 1: CZYSTY MORTON (dla testu) ---
            # swizzled_idx = morton_idx_abstract * BYTES_PER_BLOCK
            
            # --- WARIANT 2: Tiled Morton (Standard Phyre) ---
            # Podział na Super-Kafelki 128x128 pikseli (32x32 bloki)
            SUPER_TILE_DIM = 32 # bloki (32 * 4 = 128 px)
            
            st_x = x // SUPER_TILE_DIM
            st_y = y // SUPER_TILE_DIM
            local_x = x % SUPER_TILE_DIM
            local_y = y % SUPER_TILE_DIM
            
            super_cols = (w_blocks + SUPER_TILE_DIM - 1) // SUPER_TILE_DIM
            st_idx = st_y * super_cols + st_x
            
            local_morton = get_morton_idx(local_x, local_y)
            
            blocks_per_st = SUPER_TILE_DIM * SUPER_TILE_DIM
            swizzled_idx = (st_idx * blocks_per_st + local_morton) * BYTES_PER_BLOCK
            
            # Zabezpieczenie przed wyjściem poza zakres (dla paddingu)
            if swizzled_idx + BYTES_PER_BLOCK <= len(texture_data):
                if args.mode == "unswizzle":
                    chunk = texture_data[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK]
                    output_texture[linear_idx : linear_idx + BYTES_PER_BLOCK] = chunk
                else:
                    chunk = texture_data[linear_idx : linear_idx + BYTES_PER_BLOCK]
                    output_texture[swizzled_idx : swizzled_idx + BYTES_PER_BLOCK] = chunk
            
    # Zapis
    with open(args.output_file, "wb") as f:
        f.write(header_data + output_texture)
    
    print(f"[+] Zapisano: {args.output_file}")

if __name__ == "__main__":
    process_texture(get_params())
