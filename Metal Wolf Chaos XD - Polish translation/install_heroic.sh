#!/bin/bash
# Automatyczny skrypt instalujący dla Heroic Games Launcher
# URUCHOM TEN SKRYPT Z FOLDERU GDZIE ZNAJDUJE SIĘ PLIK MWC_XD_Spolszczenie_PL.tar.gz

# Kolory dla czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sprawdzenie czy paczka istnieje w obecnym katalogu
if [ ! -f "MWC_XD_Spolszczenie_PL.tar.gz" ]; then
    echo -e "${RED}❌ BŁĄD: Nie znaleziono pliku MWC_XD_Spolszczenie_PL.tar.gz${NC}"
    echo ""
    echo "Ten skrypt musi być uruchomiony z folderu gdzie znajduje się"
    echo "pobrana paczka ze spolszczeniem."
    echo ""
    echo "Przykład użycia:"
    echo "  cd ~/Pobrane"
    echo "  bash install_heroic.sh"
    exit 1
fi

# Ścieżka gry (domyślna dla Heroic, można nadpisać argumentem)
GAME_PATH="${1:-~/Games/Heroic/Metal Wolf Chaos XD}"

echo -e "${YELLOW}=== Instalator Spolszczenia Metal Wolf Chaos XD ===${NC}"
echo "Ścieżka gry: $GAME_PATH"
echo ""

# Sprawdzenie czy folder gry istnieje
if [ ! -d "$GAME_PATH" ]; then
    echo -e "${RED}❌ BŁĄD: Nie znaleziono folderu gry: $GAME_PATH${NC}"
    echo ""
    echo "Możliwe rozwiązania:"
    echo "1. Zainstaluj grę przez Heroic Games Launcher"
    echo "2. Podaj własną ścieżkę jako argument:"
    echo "   bash install_heroic.sh /ścieżka/do/gry"
    exit 1
fi

TEMP_DIR=$(mktemp -d)

# Wypakowanie
echo -e "${YELLOW}[1/3] Wypakowywanie plików...${NC}"
tar -xzf MWC_XD_Spolszczenie_PL.tar.gz -C "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Błąd podczas wypakowywania archiwum${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Kopiowanie tekstów
echo -e "${YELLOW}[2/3] Kopiowanie przetłumaczonych tekstów...${NC}"
cp -r "$TEMP_DIR/MWC_XD_Spolszczenie_PL/rom/"* "$GAME_PATH/rom/"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Błąd podczas kopiowania tekstów${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Kopiowanie menu
echo -e "${YELLOW}[3/3] Kopiowanie plików menu...${NC}"
cp "$TEMP_DIR/MWC_XD_Spolszczenie_PL/Media/D3D11/"*_ru_RU.phyre "$GAME_PATH/Media/D3D11/"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Błąd podczas kopiowania plików menu${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Sprzątanie
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}✅ Instalacja zakończona sukcesem!${NC}"
echo ""
echo "Następne kroki:"
echo "1. Upewnij się, że w Heroic masz wybrane: GE-Proton-latest"
echo "2. Sprawdź czy język gry jest ustawiony na Russian (plik goggame-1943046668.info)"
echo "3. Uruchom grę i sprawdź czy w pierwszym dialogu widzisz polskie znaki"
