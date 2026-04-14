# 🇵🇱 Metal Wolf Chaos XD - Spolszczenie

**Aktualizacja:** Kwiecień 2026  
Spolszczenie obejmuje 100% tekstów w grze (odprawy, dialogi w trakcie misji, maile, opisy broni oraz interfejs HUD). Z przyczyn technicznych narzuconych przez silnik PhyreEngine, napisy w menu głównym (Nowa Gra, Opcje) pozostały w oryginalnej, angielskiej wersji językowej, co jednak doskonale komponuje się z amerykańskim klimatem gry.

---

## ⚠️ UWAGA: Wymagania wstępne (Kluczowe dla działania!)

### 1. Wersja Wine (Bardzo ważne dla Linux/Steam Deck)
Gra na natywnym Wine często crashuje przy próbie odtwarzania filmów intro.
- **Rozwiązanie:** W ustawieniach Heroic Games Launcher dla tej gry, w zakładce "Wine", wybierz **GE-Proton-Latest** jako wersję Wine.

### 2. Język gry
Aby polskie znaki diakrytyczne (ą, ć, ę, ł, ń, ó, ś, ż, ź) wyświetlały się poprawnie, **gra musi zostać uruchomiona w rosyjskiej wersji językowej**. Jest to zabieg techniczny mający na celu ominięcie blokady znaków ASCII zaimplementowanej przez twórców w angielskiej wersji gry.
- **Heroic/GOG/Steam:** W ustawieniach gry zmień język na **Russian**.

---

## 🛠 Instrukcja Instalacji

1. Pobierz plik `MWC_XD_Spolszczenie_PL.tar.gz` z zakładki **Releases**.
2. Wypakuj zawartość paczki do głównego folderu z zainstalowaną grą (nadpisując oryginały).
3. **KROK INSTALACJI MENU (Obejście PhyreEngine):**
   Aby uzyskać estetyczne, amerykańskie menu w trybie rosyjskim, wejdź do katalogu `Media/D3D11/`, skopiuj 5 oryginalnych plików z końcówką `_en_US.phyre` i zmień ich nazwy na `_ru_RU.phyre`, nadpisując istniejące tam pliki.
4. Uruchom grę w trybie rosyjskim przy użyciu GE-Proton.

---

## 📝 Informacje techniczne dla moderów
Spolszczenie wykorzystuje iniekcję bazy SQLite oraz modyfikację atlasu czcionek bitmapowych (`.dds`). Więcej narzędzi deweloperskich i skryptów (Text Sniper, Amputatory) znajdziesz w moim prywatnym repozytorium: `My-AI-Gaming-Translator`.
