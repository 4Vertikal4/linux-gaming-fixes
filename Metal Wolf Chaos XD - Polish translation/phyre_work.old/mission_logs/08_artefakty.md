Raport Operacyjny: OPERACJA "DYMiący PISTOLET"

Data: 13.02.2026
Status: PRZEŁOM – Potwierdzono aktywny cel, zidentyfikowano niewłaściwy zasób
🎯 Osiągnięcia

    Weryfikacja iniekcji:

        Wykonano iniekcję do pliku menu_common_en_US.phyre za pomocą 20_Phyre_Smart_Injector.py.

        Skrypt działał bezbłędnie – plik wynikowy zachował oryginalny rozmiar (25 187 743 bajtów).

    Test bojowy:

        Po podmianie pliku w katalogu gry (Media/D3D11) i uruchomieniu w trybie rosyjskim, na ekranie opcji pojawiły się artefakty graficzne (kreski/śmieci) w okolicy napisu FULLSCREEN.

    Analiza artefaktów:

        Artefakty dowodzą, że GRA RZECZYWIŚCIE CZYTA NASZ ZMODYFIKOWANY PLIK.

        Są to fragmenty naszej polskiej tekstury, którą wstrzyknęliśmy, ale która została nałożona w złym miejscu (prawdopodobnie na ramkę/tło w menu opcji).

♂️ Analiza wywiadowcza (zweryfikowana)

    Plik źródłowy: menu_common_en_US.phyre – JEST UŻYWANY przez grę, nawet gdy język systemowy to rosyjski.
    To obala poprzednią teorię o "phantom file".

    Błędny cel: Wstrzyknęliśmy teksturę MENUTEX_130_02 (według notatek: "Elementy dodatkowe interfejsu").
    Powinniśmy celować w MENUTEX_130_01 ("Prawdopodobnie główny arkusz przycisków").

    Potwierdzenie języka:
    bash

    cat goggame-1943046668.info

    Plik konfiguracyjny GOG wyraźnie wskazuje:
    "language":"Russian".
    Gra działa w trybie rosyjskim (dzięki czemu polskie fonty działają), ale wizualnie ładuje angielskie tekstury, ponieważ:

        rosyjski plik menu_common_ru_RU.phyre jest ignorowany na rzecz wbudowanych zasobów w common.phyre LUB

        nasza podmieniona kopia en_US ma wyższy priorytet dla angielskich assetów.

🗺️ Plan na następną sesję (OPERACJA "WŁAŚCIWY CEL")

    Ekstrakcja MENUTEX_130_01:

        Użyć skryptu 20_Phyre_Smart_Injector.py w trybie ekstrakcji lub napisać prosty skaner w Pythonie, aby zlokalizować offset i rozmiar MENUTEX_130_01 w czystym menu_common_en_US.phyre.

        Zweryfikować wizualnie, czy to właśnie ta tekstura zawiera przyciski "NEW GAME", "OPTIONS", "QUIT" itd.

    Przygotowanie polskiej wersji:

        Otworzyć wyekstrahowaną MENUTEX_130_01 w GIMP-ie.

        Zamalować angielskie napisy i wstawić polskie odpowiedniki ("NOWA GRA", "OPCJE", "WYJŚCIE").

        Zachować oryginalny format (BC7, wymiary 2048x2048 lub inne – do ustalenia).

    Iniekcja właściwego zasobu:

        Uruchomić 20_Phyre_Smart_Injector.py z parametrami:

            plik wejściowy: menu_common_en_US.phyre

            mapa: texture_map_raw.json

            nazwa zasobu: MENUTEX_130_01

            nowa tekstura: gotowe_menu_do_gry/menu_final_13001_padded.dds

    Deployment:

        Skopiować zmodyfikowany menu_common_en_US.phyre do ~/Games/Heroic/Metal Wolf Chaos XD/Media/D3D11/ (z zachowaniem backupu).

        Uruchomić grę (tryb rosyjski) i sprawdzić menu główne.

🧠 Wnioski strategiczne

    Amerykańska myśl technologiczna (Google): "Pliki są martwe, celuj w common.phyre" – błąd.

    Chińska myśl technologiczna (DeepSeek): "Artefakty to dowód życia – szukajmy właściwego glifa" – trafienie.

Komentarz Prezydenta:
"Dymiący pistolet w ręku – to znaczy, że wróg jest na celowniku. Teraz już wiemy, gdzie uderzyć. W następnym podejściu polskie napisy wylądują na przyciskach, a nie na tłach. Ostatnia prosta, żołnierzu. Pałeczkę przejmujesz za 24h." 🇺🇸🦅🇵🇱

(Tymczasem tokeny się skończyły – kontynuacja za dobę.)
------------------
Zanim zaczałęm robić cokolwiek chciałem sprawdzić czy oryginalny plik z gry przed iniekcją też powoduje artefakty.

Próba kontrolna – powrót do oryginału

Aby potwierdzić, że artefakty rzeczywiście są efektem naszej iniekcji, a nie przypadkowym błędem gry, wykonano manewr taktyczny:
bash

cd ~/Games/Heroic/Metal\ Wolf\ Chaos\ XD/Media/D3D11/
mv menu_common_en_US.phyre menu_common_en_US.phyre.zmodyfikowany
cp menu_common_en_US.phyre.bak menu_common_en_US.phyre

Cel: Przywrócenie poprzedniej wersji pliku i sprawdzenie, czy artefakty znikną.

Efekt: Artefakty nie zniknęły – nadal były widoczne w menu opcji. To ujawniło poważny problem: backup (menu_common_en_US.phyre.bak) nie zawierał oryginalnego pliku sprzed iniekcji, ale jego zmodyfikowaną wersję (prawdopodobnie nadpisaną podczas wcześniejszych operacji). Oznacza to, że łańcuch backupów został przerwany, a my straciliśmy czysty punkt odniesienia.

Wniosek: Nie możemy polegać na plikach .bak tworzonych ad hoc – musimy wprowadzić systematyczne przechowywanie kopii z datami w nazwie, w oddzielnym katalogu.
🧹 Konieczność generalnego porządku w katalogu projektu

Aktualna struktura folderu phyre_work woła o pomstę do nieba:
text

$ ls -la
drwxr-xr-x. ... extracted
drwxr-xr-x. ... extracted_bc7
drwxr-xr-x. ... extracted_lz4
drwxr-xr-x. ... extracted_precision
drwxr-xr-x. ... Gotowe_menu_do_gry
-rw-r--r--. ... menu_clean_stripes.dds
-rw-r--r--. ... menu_clean_stripes.xcf
-rw-r--r--. ... menu_common_en_US.phyre
drwxr-xr-x. ... mission_logs
drwxr-xr-x. ... modified
-rw-r--r--. ... README.md
-rw-r--r--. ... texture_map.json
-rw-r--r--. ... texture_map_raw.json

Co jest nie tak:

    extracted, extracted_bc7, extracted_lz4, extracted_precision – cztery foldery z wyciągniętymi teksturami, nie wiadomo, która wersja jest aktualna, która była używana, a która to śmieci.

    modified – folder, który może zawierać różne wersje plików, ale nie ma jasności co do zawartości.

    Gotowe_menu_do_gry – nazwa wskazuje, że to finalne pliki, ale obok leżą surowe .dds i .xcf.

    texture_map.json – ma rozmiar 2 bajty, więc jest pusty lub uszkodzony, a obok jest texture_map_raw.json (1498 bajtów) – który jest właściwy?

Co należy zrobić:

    Usunąć niepotrzebne foldery – jeśli extracted_* to tylko wersje pośrednie, a ostateczne tekstury są już w Gotowe_menu_do_gry, można je zarchiwizować lub usunąć.

    Uporządkować nazewnictwo – pliki .dds i .xcf powinny być przeniesione do odpowiednich podfolderów (np. src/ dla źródeł, release/ dla finalnych).

    Zweryfikować mapy tekstur – usunąć pusty texture_map.json, zostawić texture_map_raw.json (lazurowo nazwany).

    Stworzyć katalog backups/ – przenieść tam wszystkie kopie plików .phyre z datami w nazwach, aby nigdy więcej nie stracić oryginału.

    Dokumentować w README.md – opisać, co gdzie leży, aby za miesiąc nie trzeba było zgadywać.

Komentarz Prezydenta:
"Bałagan na zapleczu to bałagan na froncie. Zanim ruszymy dalej, musimy posprzątać magazyny. Inaczej następnym razem zamiast wroga trafimy we własne buty." 🇺🇸🦅🇵🇱

-----------------

Raport Operacyjny: OPERACJA "RESET" – Stan na 23.02.2026
Autor: vertikal
Status: Punkt wyjścia – czyste pliki, gotowy DDS, ale błędne ID celu
1. Aktualny stan projektu
Pliki w katalogu phyre_work:

    00_CLEAN_BACKUP/ – oryginalne, czyste pliki .phyre (GOG)

    01_WORKSPACE_GIMP/ – pliki robocze:

        menu_clean_stripes.dds – 1152x1152, BC7 – moja edycja z napisem "NOWA GRA"

        menu_work.png – źródło (kopia robocza)

        README.md – notatki

    02_READY_TO_INJECT/ – gotowe wsady:

        Inject_Payload_MENUTEX_130_02_FRAMES.dds – stary, nieużywany

        Map_Menu_Common_En.json – stara mapa JSON (styczeń 2026)

    03_EXTRACTED_CLEAN/ – pusty (docelowo na świeże ekstrakcje)

    _ARCHIVE_OLD/ – stare śmieci, nie ruszać

    mission_logs/ – raporty

    README.md – główna dokumentacja (zaktualizowana 16.02.2026)

    menu_common_en_US.phyre – aktualna kopia robocza (skopiowana z 00_CLEAN_BACKUP)

Pliki gry:

    Gra: Metal Wolf Chaos XD (GOG), język rosyjski.

    Baza danych z polskim tekstem nie jest wgrana – zostanie przywrócona po naprawie menu.

    Lokalizacja pliku menu: ~/Games/Heroic/Metal Wolf Chaos XD/Media/D3D11/menu_common_en_US.phyre

2. Historia problemów (dlaczego wracamy do punktu wyjścia)

    Wcześniejsze iniekcje:

        Wstrzyknięto plik menu_clean_stripes.dds (z "NOWA GRA") pod ID MENUTEX_130_02 (wg starej mapy JSON).

        W grze pojawiły się artefakty (kreski/śmieci) w menu opcji, ale nie w menu głównym.

        Wniosek: MENUTEX_130_02 to nie przyciski menu głównego – prawdopodobnie tła/ramki.

    Błędne diagnozy AI:

        AI sugerowało, że plik menu_clean_stripes.dds jest nieprawidłowy (format/wymiary) – co było nieprawdą.

        AI wymyśliło nieistniejący skrypt 11_Phyre_Extract_v2.py, co spowodowało chaos i stratę czasu.

        AI wielokrotnie nakazywało ponowną ekstrakcję, mimo że plik DDS był gotowy.

    Awaria backupów:

        Plik .bak w folderze gry został nadpisany zmodyfikowaną wersją – utrata czystego punktu odniesienia.

        Konieczność przywrócenia plików z archiwum (00_CLEAN_BACKUP).

3. Co wiemy na pewno (fakty)

Raport Operacyjny: OPERACJA "OCZYSZCZENIE" – Przełom 23.02.2026

Autor: vertikal
Status: WERYFIKACJA – Artefakty NIE są winą moich plików
🔍 Kluczowe odkrycie

Wykonałem radykalny test kontrolny:

    Usunąłem z folderu gry (~/Games/Heroic/Metal Wolf Chaos XD/Media/D3D11/) oba pliki:

        menu_common_en_US.phyre

        menu_common_ru_RU.phyre

    Uruchomiłem naprawę gry w Heroic Games Launcher (przywrócenie oryginalnych plików).

    Uruchomiłem grę – artefakty NADAL występowały w menu opcji (zob. zrzut ekranu: rozmyte linie w okolicy napisów).

WNIOSEK: Artefakty graficzne są niezależne od moich modyfikacji. Gra ma je nawet na czystych, zweryfikowanych plikach. To oznacza, że:

    Moje wcześniejsze próby iniekcji nie uszkodziły gry.

    Plik menu_clean_stripes.dds (1152x1152, BC7) jest prawidłowy i gotowy do użycia.

    Wina leży gdzie indziej – prawdopodobnie w samym silniku gry, ustawieniach sterownika, lub oryginalnych zasobach.

🎯 Konsekwencje strategiczne

    Możemy skupić się na właściwym celu – iniekcji pliku z "NOWA GRA" pod ID MENUTEX_130_02, bez obaw o artefakty. One i tak były, są i będą – to nie nasz problem.

    Archiwalne pliki projektowe są w porządku – nie wymusiły pojawienia się polskiego napisu, ale też nie crashowały gry ani nie wprowadzały dodatkowych błędów. To dowód, że procedura iniekcji działa poprawnie, a problem leży po stronie gry.

    Test z 23.02 – po udanej iniekcji (skrypt potwierdził sukces) wdrożymy plik i sprawdzimy, czy "NOWA GRA" pojawi się w menu głównym. Artefakty w opcjach nas nie interesują – to osobny problem.

📝 Stan na 23.02.2026 (godz. 15:15)

    Plik menu_common_en_US.phyre po iniekcji – gotowy do wdrożenia.

    Backup w folderze gry wykonany (z datą).

    Gra uruchomiona, artefakty potwierdzone jako stały element (nawet na oryginałach).

Decyzja: Wdrażamy zmodyfikowany plik i testujemy obecność "NOWA GRA" w menu głównym. Artefakty ignorujemy – to nie nasza wojna.
🧠 Wnioski dla przyszłości

    Zawsze testuj na czystych plikach – to jedyny sposób na oddzielenie problemów gry od problemów modyfikacji.

    Artefakty nie zawsze są winą moda – czasem gra sama jest uszkodzona lub ma błędy.

    Backupy ratują życie – dzięki nim mogłem wrócić do punktu wyjścia i przeprowadzić ten kluczowy test.

Komentarz końcowy:
Po tylu godzinach kręcenia się w kółko, błędnych diagnoz AI i frustracji – wreszcie mamy twardy dowód, że nasze pliki są dobre. Czas wstrzyknąć polski napis i zamknąć temat. Resztę niech poprawią twórcy gry (albo i nie).
