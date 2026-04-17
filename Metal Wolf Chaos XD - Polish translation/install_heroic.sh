#!/bin/bash
# Automatyczny skrypt instalujący dla Heroic Games Launcher
# URUCHOM TEN SKRYPT Z FOLDERU GDZIE ZNAJDUJE SIĘ PLIK MWC_XD_Spolszczenie_PL.tar.gz

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

GAME_PATH="${1:-~/Games/Heroic/Metal Wolf Chaos XD}"

echo -e "${YELLOW}=== Instalator Spolszczenia Metal Wolf Chaos XD ===${NC}"
echo "Ścieżka gry: $GAME_PATH"
echo ""

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

echo -e "${YELLOW}[1/4] Wypakowywanie archiwum...${NC}"
tar -xzf MWC_XD_Spolszczenie_PL.tar.gz -C "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Błąd podczas wypakowywania archiwum${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

PACZKA_DIR="$TEMP_DIR/MWC_XD_Spolszczenie_PL"

if [ ! -d "$PACZKA_DIR" ]; then
    echo -e "${RED}❌ Błąd: Nieprawidłowa struktura archiwum${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${YELLOW}[2/4] Instalowanie bazy tekstów...${NC}"
if [ -f "$PACZKA_DIR/Media/Texts/texts_may30.db" ]; then
    mkdir -p "$GAME_PATH/Media/Texts/"
    cp "$PACZKA_DIR/Media/Texts/texts_may30.db" "$GAME_PATH/Media/Texts/"
    if [ $? -eq 0 ]; then
        echo "  ✅ texts_may30.db"
    else
        echo -e "${RED}  ❌ Błąd kopiowania bazy tekstów${NC}"
    fi
else
    echo -e "${RED}  ❌ Nie znaleziono texts_may30.db w paczce!${NC}"
fi

echo -e "${YELLOW}[3/4] Instalowanie czcionek...${NC}"
KOPIOWANE_CZCIONKI=0
for plik in MWC_Font_ru_RU.ccm MWC_Font_ru_RU.dds; do
    if [ -f "$PACZKA_DIR/rom/font/$plik" ]; then
        cp "$PACZKA_DIR/rom/font/$plik" "$GAME_PATH/rom/font/"
        if [ $? -eq 0 ]; then
            echo "  ✅ $plik"
            ((KOPIOWANE_CZCIONKI++))
        else
            echo -e "${RED}  ❌ Błąd kopiowania $plik${NC}"
        fi
    else
        echo -e "${RED}  ❌ Nie znaleziono $plik w paczce!${NC}"
    fi
done

echo -e "${YELLOW}[4/4] Instalowanie plików menu...${NC}"
KOPIOWANE_MENU=0
for plik in "$PACZKA_DIR"/Media/D3D11/*_ru_RU.phyre; do
    if [ -f "$plik" ]; then
        nazwa=$(basename "$plik")
        cp "$plik" "$GAME_PATH/Media/D3D11/"
        if [ $? -eq 0 ]; then
            echo "  ✅ $nazwa"
            ((KOPIOWANE_MENU++))
        else
            echo -e "${RED}  ❌ Błąd kopiowania $nazwa${NC}"
        fi
    fi
done

rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}=== Instalacja zakończona ===${NC}"
echo "Zainstalowane elementy:"
echo "  • Baza tekstów: texts_may30.db"
echo "  • Czcionki: $KOPIOWANE_CZCIONKI/2"
echo "  • Pliki menu: $KOPIOWANE_MENU"
echo ""
echo "Następne kroki:"
echo "1. Upewnij się, że w Heroic masz wybrane: GE-Proton-latest"
echo "2. Sprawdź czy język gry jest ustawiony na Russian (plik goggame-1943046668.info)"
echo "3. Uruchom grę i sprawdź czy w pierwszym dialogu widzisz polskie znaki"
echo ""
echo "Jeśli chcesz usunąć spolszczenie, przywróć folder Media z backupu."
