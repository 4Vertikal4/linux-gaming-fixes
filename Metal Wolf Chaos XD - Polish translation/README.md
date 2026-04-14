# 🇵🇱 Metal Wolf Chaos XD - Spolszczenie

**Aktualizacja:** Kwiecień 2026  
Spolszczenie obejmuje 100% tekstów w grze (odprawy, dialogi w trakcie misji, maile, opisy broni oraz interfejs HUD). Z przyczyn technicznych narzuconych przez silnik PhyreEngine, napisy w menu głównym (Nowa Gra, Opcje) pozostały w oryginalnej, angielskiej wersji językowej.

---

## ⚠️ UWAGA: Wymagania wstępne (Kluczowe dla działania!)

### 1. Wersja Wine (Bardzo ważne dla Linux/Steam Deck)
Gra na natywnym Wine często crashuje przy próbie odtwarzania filmów intro.
- **Rozwiązanie:** W ustawieniach Heroic Games Launcher dla tej gry, w zakładce "Wine", wybierz **GE-Proton-latest** jako wersję Wine.

### 2. Język gry
Aby polskie znaki diakrytyczne (ą, ć, ę, ł, ń, ó, ś, ż, ź) wyświetlały się poprawnie, **gra musi zostać uruchomiona w rosyjskiej wersji językowej**. Jest to zabieg techniczny mający na celu ominięcie blokady znaków ASCII zaimplementowanej przez twórców w angielskiej wersji gry.

**Jak ustawić język gry?**

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

## 🛡️ KROK 0: Backup (Zalecany!)

Przed instalacją **zdecydowanie zalecam** wykonanie kopii zapasowej oryginalnych plików gry. W razie problemów będziesz mógł łatwo przywrócić stan pierwotny.

```bash
# Przejdź do folderu z grą (przykład dla Heroic)
cd ~/Games/Heroic/Metal\ Wolf\ Chaos\ XD/

# Wykonaj kopię folderu z plikami językowymi
cp -r Media Media_backup_oryginal

# Lub jeśli wolisz backup tylko folderu D3D11 (mniejszy rozmiar)
cp -r Media/D3D11 Media/D3D11_backup_oryginal
```

Przywracanie oryginału (jeśli coś pójdzie nie tak):
```bash

rm -rf Media/D3D11
cp -r Media/D3D11_backup_oryginal Media/D3D11
```

📥 KROK 1: Pobieranie
Najnowszą wersję spolszczenia pobierz z zakładki Releases:

    Plik: MWC_XD_Spolszczenie_PL.tar.gz
    Rozmiar: ~28 MB

Alternatywnie, jeśli przeglądasz to repozytorium lokalnie, plik znajduje się w głównym katalogu.
🛠️ KROK 2: Instalacja Spolszczenia
2.1 Podstawowa instalacja

    Upewnij się, że gra jest zamknięta.
    Wypakuj zawartość archiwum MWC_XD_Spolszczenie_PL.tar.gz bezpośrednio do głównego folderu z grą (tam gdzie znajduje się plik wykonywalny gry).
    Potwierdź nadpisanie plików (tak, to bezpieczne - właśnie dlatego zrobiliśmy backup).

### 2.2 Instalacja menu angielskiego (Obejście PhyreEngine)
**Uwaga:** To już zostało zrobione za Ciebie! W paczce `MWC_XD_Spolszczenie_PL.tar.gz` znajdują się przygotowane pliki angielskiego menu z już zmienionymi nazwami na `_ru_RU.phyre`. 

Wystarczy, że wypakujesz całą zawartość archiwum do folderu z grą - pliki te automatycznie nadpiszą rosyjskie menu, zachowując przy tym wymagany przez silnik tryb "rosyjski".

**Weryfikacja:** Po wypakowaniu w folderze `Media/D3D11/` powinieneś zobaczyć pliki z końcówką `_ru_RU.phyre` (są to oryginalne angielskie pliki, tylko z nazwą sugerującą rosyjską wersję).
    
✅ KROK 3: Weryfikacja (Sprawdzenie czy działa)

    Uruchom grę przez Heroic (upewnij się, że masz wybrane GE-Proton-latest)
    W pierwszym ekranie (intro) lub w pierwszym dialogu z Prezydentem Wilsonem powinieneś zobaczyć polskie znaki (np. "Witaj, Michael" zamiast "Welcome, Michael")
    Jeśli widzisz krzaki zamiast polskich znaków (np. "Witaj, Michael" zamiast "Witaj, Michael"):
        Sprawdź czy masz ustawiony język Russian w pliku goggame-1943046668.info
        Sprawdź czy używasz GE-Proton-latest
    Jeśli menu jest po rosyjsku (cyrylica):
        Wróć do kroku 2.2 i upewnij się, że skopiowałeś pliki _en_US.phyre jako _ru_RU.phyre
        
🗑️ Jak usunąć spolszczenie?
Jeśli chcesz wrócić do wersji angielskiej:
Sposób 1 (jeśli robiłeś backup):

```
cd ~/Games/Heroic/Metal\ Wolf\ Chaos\ XD/
rm -rf Media
cp -r Media_backup_oryginal Media
```
# Pamiętaj też zmienić język z powrotem na English w pliku goggame-1943046668.info

Sposób 2 (reinstalacja gry):
W Heroic: Prawy przycisk na grze → Manage → Uninstall, a następnie zainstaluj ponownie wybierając język angielski.

📝 Informacje techniczne dla moderów
Spolszczenie wykorzystuje:

    Iniekcję bazy SQLite (teksty gry przechowywane są w bazie danych)
    Modyfikację atlasu czcionek bitmapowych (.dds) dla wyświetlania polskich znaków
    Podmianę plików językowych w locie (technika _en_US → _ru_RU)

Więcej narzędzi deweloperskich i skryptów (Text Sniper, Amputatory) znajdziesz w moim prywatnym repozytorium: My-AI-Gaming-Translator.

🆘 Troubleshooting (Rozwiązywanie problemów)

| Problem                          | Możliwa przyczyna                                        | Rozwiązanie                                            |
| -------------------------------- | -------------------------------------------------------- | ------------------------------------------------------ |
| Gra crashuje na intro            | Zły wybór wersji Wine                                    | Ustaw dokładnie **GE-Proton-latest** w Heroic          |
| Krzaki zamiast polskich znaków   | Brak ustawienia języka Russian                           | Edytuj plik `goggame-1943046668.info` jak w instrukcji |
| Menu jest po rosyjsku (cyrylica) | Nie skopiowano plików `_en_US.phyre` jako `_ru_RU.phyre` | Wróć do kroku 2.2 i wykonaj kopiowanie plików          |
| Gra nie uruchamia się po modzie  | Uszkodzone pliki                                         | Przywróć backup lub przeinstaluj grę                   |


