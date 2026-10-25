# Krok S2 — wynik analizy `GameAssembly.dll` (dla właściciela)

Krótko: **nic nie musisz teraz robić.** Plik dotarł, jest poprawny (74 865 152 B,
SHA-256 `d96e91f5…68bb`) i dał najwięcej jak dotąd — wiem już **jak** gra
szyfruje bundle, choć samego klucza nie mam.

## Co ustaliłem

Z nazw w kodzie gry (są w `global-metadata.dat`, nie w samym DLL):

- `Assets\Scripts\Addressable\SeekableAesStreamcs.cs` — własna klasa
  **strumienia AES, który można przewijać**, a jej pola to `password`, `salt`,
  `buffer`, `streamPos`, `aes`, `encryptor`;
- `Com.BBStudio.SRTeam.Encryption|EnctyptionInfo` z polami `KeySize`,
  `BlockSize`, `Mode`, `IV`, `Padding` — czyli konfiguracja AES;
- `Assets\Scripts\Addressable\CustomAssetBundleProvider.cs` — klasa, która
  podmienia standardowe ładowanie bundli.

Czyli: **klucz nie leży w grze jako gotowy napis — jest wyprowadzany z hasła i
soli.** Dlatego wszystkie wcześniejsze próby (6,1 mln kandydatów) nie mogły
trafić: one sprawdzały literały jako klucze, a literały to nie klucze.

## Czego jeszcze spróbowałem i co nie wyszło

- **61 201 575** okien 16/24/32-bajtowych — **każde przesunięcie** w danych
  `GameAssembly.dll` — jako gotowy klucz AES/RC4/ChaCha20. Zero trafień
  (15 minut 34 sekundy pracy).
- Klucz wyprowadzony z **nazwy samego bundla** (PBKDF2 i skróty MD5/SHA) × 12
  stałych projektu — 4712 kombinacji, zero trafień.

Uczciwie: statyczne szukanie klucza wyczerpałem w tym zakresie, który ma sens.

## Co dalej — i czego teraz NIE potrzebuję

Następny krok jest po mojej stronie: zamiast zgadywać hasło, **przechwycić tekst
w momencie, gdy gra już go odszyfruje** (gra musi to robić, żeby działać).
Technicznie: podpięcie się do działającej gry małym skryptem i zapisanie
odszyfrowanych danych — bez znajomości klucza.

To wymaga uruchomienia czegoś na Twoim komputerze, więc **dostaniesz osobną
instrukcję do wklejenia**, tak jak poprzednie, dopiero gdy sam sprawdzę, że
metoda jest realna. Nie chcę Ci wysyłać czegoś, czego nie przetestowałem.

**Nie wysyłaj już żadnych plików gry** — mam wszystko, co na tym etapie miało
sens (dwa bundle 6,5 MB, katalog, metadane, `GameAssembly.dll`).

## Jedno pytanie, które może przyspieszyć sprawę

Czy na Twoim komputerze jest zainstalowany **Python**? (Wcześniejsze kroki
zakładały PowerShell, więc nie wiem.) Jeśli tak — powiedz, którą wersję pokazuje

```powershell
python --version
```

To może skrócić drogę, ale nie jest warunkiem: jeśli Pythona nie ma, poszukam
wariantu, który go nie wymaga.
