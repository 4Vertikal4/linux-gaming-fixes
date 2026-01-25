📋 Horizon Forbidden West Complete Edition - Stan Diagnostyki (Herioc/Epic)

Data aktualizacji: Styczeń 2026
Obecny Status

Użytkownicy na systemach takich jak Fedora (Rawhide/42) korzystający z Heroic Games Launcher (Flatpak) doświadczają następujących problemów:

    Brak wzrostu cache shaderów (DX12/VKD3D): Gra nie zapisuje na dysk nowo skompilowanych shaderów, przez co każdy start wiąże się z długą kompilacją od zera. Plik vkd3d-proton.cache.write nie jest tworzony po wyjściu z gry.

    Losowa awaria dźwięku: Dźwięk może nie działać przy starcie gry lub zanikać podczas szybkiej podróży (Fast Travel), prawdopodobnie z powodu wyczerpania zasobów CPU podczas kompilacji shaderów.

Co zostało przetestowane i uznane za NIEROZWIĄZANIE

Poniższa konfiguracja nie doprowadziła do trwałego rozwiązania problemu z cache'owaniem shaderów. Stanowi jedynie zapis podjętych prób.
1. Skrypt opakowujący ("Smart Wrapper")

Aby zapobiec utracie danych i wymusić wyższy limit deskryptorów plików, używany był skrypt uruchamiany jako "Wrapper Command" w Heroic.

    Skrypt tylko chronił istniejący plik cache, ale nie wymuszał jego zapisu przez VKD3D.

2. Zmienne środowiskowe (bezskuteczne)

Poniższe zmienne, mimo szczegółowego testowania, nie sprawiły, że gra zaczęła zapisywać cache shaderów:

    VKD3D_CONFIG=no_upload_hvv,pipeline_library_app_cache

    PULSE_LATENCY_MSEC=300

    WINE_FD_LIMIT=524288

    __GL_SHADER_DISK_CACHE=1

    __GL_SHADER_DISK_CACHE_SIZE=10000

    WINE_RT_AUDIO=1

3. Inne działania

    Wyłączenie GameMode i EAC w ustawieniach Heroic.

    Ręczne zarządzanie plikami cache (vkd3d-proton.cache, .write).

Wnioski i przyszłe kierunki

Podstawowy problem pozostaje nierozwiązany: VKD3D-Proton w konfiguracji Flatpak nie inicjuje zapisu cache shaderów na dysk dla gry Horizon Forbidden West. Obecny stan to impas (stalemate).

Potrzebne dalsze badania nad:

    Głębszą analizą logów VKD3D (VKD3D_DEBUG=all) w kontekście Flatpaka.

    Testowaniem innych flag VKD3D_CONFIG. Na przykład, w przypadku gry Starfield dla użytkowników kart AMD kluczową dla stabilności okazała się flaga force_host_cached. Warto sprawdzić, czy ta lub podobna flaga (np. force_host_cached,pipeline_library_app_cache) nie wymusi w końcu zapisu cache w HFW.
