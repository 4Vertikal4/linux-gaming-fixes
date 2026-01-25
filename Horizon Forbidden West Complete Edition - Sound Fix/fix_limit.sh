#!/bin/bash

# 1. Wymuszenie limitu plików
ulimit -n 524288

# 2. Ustawienie logów (PRZYWRÓCONE)
export PROTON_LOG=1
export PROTON_LOG_DIR="$HOME/Games/Heroic/HorizonForbiddenWestCE"
export VKD3D_DEBUG=warn

# Znacznik nowej sesji w naszym prywatnym logu statusu
echo "--- SESJA: $(date) ---" >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"

# 3. Uruchomienie gry (Skrypt czeka aż gra się zamknie)
"$@"

# 4. INTELIGENTNA NAPRAWA CACHE (Wersja Ochronna)
echo "Gra zakończona. Sprawdzam pliki cache..." >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"

if [ -f "vkd3d-proton.cache.write" ]; then
    
    if [ -f "vkd3d-proton.cache" ]; then
        # Pobieramy rozmiary plików w bajtach
        SIZE_OLD=$(stat -c%s "vkd3d-proton.cache")
        SIZE_NEW=$(stat -c%s "vkd3d-proton.cache.write")
        
        echo "Rozmiar STARY: $SIZE_OLD | Rozmiar NOWY: $SIZE_NEW" >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"

        # DECYZJA: Aktualizujemy TYLKO jeśli nowy cache jest większy
        if [ $SIZE_NEW -gt $SIZE_OLD ]; then
            mv -f "vkd3d-proton.cache.write" "vkd3d-proton.cache"
            echo "SUKCES: Nowy cache jest większy (Progres). Zaktualizowano." >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"
        else
            # Jeśli nowy jest mniejszy, usuwamy go. Chronimy stary, duży plik.
            rm "vkd3d-proton.cache.write"
            echo "IGNOROWANIE: Nowy cache jest mniejszy (Krótka sesja lub błąd). Zachowano stary, duży plik." >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"
        fi
    else
        # Jeśli nie ma starego pliku, po prostu bierzemy nowy
        mv -f "vkd3d-proton.cache.write" "vkd3d-proton.cache"
        echo "START: Utworzono pierwszy plik cache." >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"
    fi
    
    # Dla pewności nadajemy uprawnienia odczytu/zapisu dla wszystkich (żeby gra nie miała problemu z odczytem)
    chmod 666 "vkd3d-proton.cache" 2>/dev/null

else
    echo "INFO: Brak pliku .write. Gra nic nie zapisała." >> "$HOME/Games/Heroic/HorizonForbiddenWestCE/fix_status.txt"
fi
