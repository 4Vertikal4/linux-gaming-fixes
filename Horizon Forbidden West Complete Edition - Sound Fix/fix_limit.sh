#!/bin/bash
# Wymuszenie Hard Limit dla deskryptorów plików
ulimit -n 524288

# Uruchomienie oryginalnej komendy gry (przekazanie wszystkich argumentów)
exec "$@"
