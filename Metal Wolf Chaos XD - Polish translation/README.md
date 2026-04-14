# 🇵🇱 Metal Wolf Chaos XD - Spolszczenie

**Aktualizacja:** Kwiecień 2026  
Spolszczenie obejmuje 100% tekstów w grze (odprawy, dialogi w trakcie misji, maile, opisy broni oraz interfejs HUD). Z przyczyn technicznych narzuconych przez silnik PhyreEngine, napisy w menu głównym (Nowa Gra, Opcje) pozostały w oryginalnej, angielskiej wersji językowej.

---

## ⚠️ UWAGA: Wymagania wstępne (Kluczowe dla działania!)

### 1. Wersja Wine (Bardzo ważne dla Linux/Steam Deck)
Gra na natywnym Wine często crashuje przy próbie odtwarzania filmów intro.
- **Rozwiązanie:** W ustawieniach Heroic Games Launcher dla tej gry, w zakładce "Wine", wybierz **GE-Proton-Latest** jako wersję Wine.

### 2. Język gry
Aby polskie znaki diakrytyczne (ą, ć, ę, ł, ń, ó, ś, ż, ź) wyświetlały się poprawnie, **gra musi zostać uruchomiona w rosyjskiej wersji językowej**. Jest to zabieg techniczny mający na celu ominięcie blokady znaków ASCII zaimplementowanej przez twórców w angielskiej wersji gry.
- **Heroic/GOG/Steam:** W ustawieniach gry zmień język na **Russian**.

### Jak ustawić język gry?

**Opcja A (Podczas instalacji):**
Jeśli instalujesz grę przez Heroic/GOG, wybierz "Russian" w opcjach instalacji języka.

**Opcja B (Zmiana po instalacji - metoda edycji pliku):**
Jeśli gra jest już zainstalowana, możesz przełączyć język bez jej usuwania:
1. Przejdź do folderu z zainstalowaną grą.
2. Znajdź plik o nazwie `goggame-1943046668.info`.
3. Otwórz go edytorem tekstu.
4. Zmień linię `"language": "English"` na `"language": "Russian"`.
5. W linii `"languages": ["en-US"]` zmień `en-US` na `ru-RU.UTF-8`.
6. Zapisz plik. Gra przy następnym uruchomieniu wymusi tryb rosyjski, aktywując polskie znaki.

---

## 3. Pobieranie
Najnowszą wersję spolszczenia pobierzesz w formacie archiwum:
**[MWC_XD_Spolszczenie_PL.tar.gz](MWC_XD_Spolszczenie_PL.tar.gz)** 

*(Alternatywnie, najnowsze wydania znajdziesz zawsze w zakładce **Releases** po prawej stronie).*

---

## 4. Instrukcja Instalacji

1. Pobierz plik `MWC_XD_Spolszczenie_PL.tar.gz` z zakładki **Releases**.
2. Wypakuj zawartość paczki do głównego folderu z zainstalowaną grą (nadpisując oryginały).
3. **KROK INSTALACJI MENU (Obejście PhyreEngine):**
   Aby uzyskać amerykańskie menu w trybie rosyjskim, wejdź do katalogu `Media/D3D11/`, skopiuj 5 oryginalnych plików z końcówką `_en_US.phyre` i zmień ich nazwy na `_ru_RU.phyre`, nadpisując istniejące tam pliki.
4. Uruchom grę w trybie rosyjskim przy użyciu GE-Proton.

---

## 📝 Informacje techniczne dla moderów
Spolszczenie wykorzystuje iniekcję bazy SQLite oraz modyfikację atlasu czcionek bitmapowych (`.dds`). Więcej narzędzi deweloperskich i skryptów (Text Sniper, Amputatory) znajdziesz w moim prywatnym repozytorium: `My-AI-Gaming-Translator`.
