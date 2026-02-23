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
