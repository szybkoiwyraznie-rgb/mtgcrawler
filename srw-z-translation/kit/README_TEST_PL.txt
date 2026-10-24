SRW Z (PL) — TEST CZCIONKI P3
=============================

Co to robi
----------
PATCH_TEST.bat tworzy KOPIE Twojego ISO (plik *_PLTEST.iso obok
oryginalu; oryginal NIE jest ruszany) i wstrzykuje do niej:
  * polska czcionke polszeroka (ta sama szerokosc co angielska,
    polskie znaki narysowane na literach lacinskich),
  * jedna probna kwestie dialogowa z polskim pangramem
    ("Zazolc gesla jazn!" + wszystkie polskie znaki) w pierwszej
    scenie gry (kwestia Henkena).

Wymagania
---------
  * Windows, Python 3.10+ w PATH (jak przy kitach SRW OE),
  * Twoje ISO SRW Z (SLPS-25887) — patcher sam sprawdzi hashe;
    inny obraz = stop, bez zadnych zmian,
  * miejsce na dysku na kopie obrazu (~dodatkowe 3,7 GB),
  * PCSX2 (testowane zalozenie: v2.9.144).

Kroki
-----
1. Rozpakuj caly folder, uruchom PATCH_TEST.bat.
2. Wskaz swoje ISO (okno wyboru pliku albo przeciagnij ISO na bata).
3. Poczekaj (kopiowanie obrazu + patchowanie; pare minut).
4. Uruchom *_PLTEST.iso w PCSX2, zacznij NOWA gre i dojdz do
   pierwszej sceny dialogowej (pangram jest na poczatku).
5. Zrob screenshoty:
   - okno dialogowe z pangramem (najwazniejsze),
   - dla pewnosci: jakis ekran menu (czy nic sie nie wysypalo).
6. Odeślij screenshoty + plik srwz_patch_log.txt (powstaje w tym
   folderze).

Na co patrzec na screenie
-------------------------
  * czy wszystkie polskie znaki sa (ĄĆĘŁŃÓŚŹŻ + male),
  * czytelność ogonkow (ą, ę) i kresek (ć, ń, ó, ś, ź),
  * czy litery sie nie dubluja / nie ma "duchow",
  * czy tekst nie wychodzi za ramke i nie łamie sie w polowie slowa,
  * czy wielkie litery z kreska nie dotykaja gornej krawedzi ramki.

Po tescie obraz *_PLTEST.iso mozesz usunac.
