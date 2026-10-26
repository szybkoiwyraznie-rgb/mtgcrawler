# PROŚBA — dane, które nazywają mówców cytatów bitewnych

## Po co to

Tabela `battle_voice` ma **34 317 kwestii w 39 grupach** i żadnej kolumny z mówcą.
Wiemy, że gra jakoś je łączy — inaczej nie wiedziałaby, czyj głos puścić. To
połączenie siedzi w **danych gry**, nie w tabelach tekstowych, które już mamy:

- `high` klucza wiersza (`01999dc9:…`) jest **ten sam dla wszystkich kwestii jednej
  postaci**, a `low>>22` jest ten sam dla wszystkich kwestii jednej sytuacji. Czyli
  klucz to `(id zestawu głosu) : (sytuacja)` — brakuje nam tylko, do kogo należy
  `id zestawu głosu`.
- Unity trzyma **klucze tekstowe** wpisów obok ich id w obiekcie
  `battle_voice Shared Data.asset`. Jeśli autorzy nadali im nazwy (np. `AMRO_012`),
  ten jeden plik rozwiąże zagadkę.
- `PilotBasicDatas` to dane bazowe pilotów — tam gra trzyma m.in. przypisanie
  pilota do zestawu głosu.

Poprzednia próba (26.10) przeszła przez: hashe nazw (crc32, fnv1a, murmur3, md5,
sha1 — 0 trafień na 398 kodach postaci) i dopasowanie cytatów do linii fabuły
(0 z 34 317). Dlatego prosimy o pliki danych — to jedyna droga do **pewnego**
przypisania, a nie do zgadywania.

## Co uruchomić

1. Skopiuj na pulpit `collect_voice_speaker_data.ps1` (jest w `tools/`).
2. Kliknij prawym → **Uruchom z PowerShell** (albo w PowerShell:
   `powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Desktop\collect_voice_speaker_data.ps1"`).
3. Skrypt niczego nie zmienia w grze — tylko **kopiuje 17 plików**
   (razem **3,076,247 B**, poniżej 2 MB) i pakuje je do
   `srw_y_voice_data.zip` na pulpicie.
4. Wrzuć ten zip na Drive (folder projektu) i napisz, że jest.

Skrypt wypisuje na końcu liczbę skopiowanych plików, sumę bajtów i SHA-256 zipa.
Jeśli czegoś nie znajdzie, wypisze `BRAKUJE:` z listą — wtedy wyślij sam log
(`srw_y_voice_log.txt` na pulpicie), a my poprawimy ścieżki.

## Co przyjdzie

| co | plik | rozmiar |
|---|---|---|
| battle_voice Shared Data (podstawka) | `ba1da373064fa4257af70cd3741c3b0e.bundle` | 496,100 B |
| battle_voice-DLC1 Shared Data | `2180d4f65e1ee3ac2fb4497c015b0395.bundle` | 20,174 B |
| battle_voice-DLC2 Shared Data | `8fb5468b8f0e3e65eadb980949553186.bundle` | 15,289 B |
| battle_voice-DLC3 Shared Data | `f2c0027f39ba80ee8ec5510fde91ee60.bundle` | 24,058 B |
| battle_voice-DLC4 Shared Data | `4e2c02efe3bd247bee95c6ba792b0c9c.bundle` | 28,151 B |
| PilotBasicDatas | `a0ae82c7bcb2df2b2ea1cd705dd968f6.bundle` | 279,321 B |
| PilotBasicDatas_DlcOf1 | `9a86251607bab7f2a3258f2709bee213.bundle` | 22,849 B |
| PilotBasicDatas_DlcOf2 | `7a7c55b8f1d1c991651d30333ce771c4.bundle` | 22,853 B |
| PilotBasicDatas_DlcOfEXP | `892215ddbcdf52f2ebf8a0bd6fec0466.bundle` | 40,192 B |
| PilotBasicDatas_DlcOfEXP2 | `3f065218ced59059a0908b505b0a9609.bundle` | 35,681 B |
| DicDetail_Pilot | `1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle` | 1,690,486 B |
| RobotBasicDatas | `862c7887d89b02dc5798436613f93586.bundle` | 228,926 B |
| RobotBasicDatas_DlcOfEXP | `fffb4d79945d10628c55ab13356efdfd.bundle` | 57,119 B |
| RobotBasicDatas_DlcOfEXP2 | `102a157887ff8b2acf824cc6c9d110e2.bundle` | 92,099 B |
| SystemBasicDatas | `9f2339313950b822bb0ffe0353ce1d10.bundle` | 15,480 B |
| SystemBasicDatas_DlcOfEXP | `09b2858b77e9d4103345dd38fae7c781.bundle` | 3,983 B |
| SystemBasicDatas_DlcOfEXP2 | `4723fcb4c6dcb838cef5b3c69a661554.bundle` | 3,486 B |

## Co z tego zrobimy

1. Z `Shared Data` odczytamy klucze wpisów i porównamy z id, które już mamy — jeśli
   klucze są nazwane, mapa `grupa → postać` powstanie natychmiast.
2. Z `PilotBasicDatas` odczytamy id zestawu głosu per pilot i połączymy je z 39
   grupami `battle_voice` (oraz z kodami postaci z katalogu assetów, np. `AMRO`,
   `ECHIKA`, `CHISE`).
3. Każde przypisanie sprawdzimy **na treści**: w grupie `00000411` cytaty mówią
   „ブライガー" (Braiger), w `0001168c` — „ジーグ" i zwracają się do „宙さん" (pilot
   Jeega). Jeśli odczytane id nie zgadza się z treścią, szukamy dalej — nie
   publikujemy zgadywania.
4. Wynik: `local/s6/voice_banks.json` + nowa etykieta w paczce tłumacza,
   `[Cytat bitewny - アムロ (Amuro)]` zamiast `[głos 7/39]`.

## Czego NIE trzeba wysyłać

- **Plików audio** (klipy `AMRO_001_A` itd.). Ich **nazwy** już mamy z katalogu
  assetów (6 627 klipów, 398 kodów postaci) — to one naprowadziły nas na trop.
  Samego dźwięku nie potrzebujemy, a to właśnie on waży gigabajty.
- Całego folderu gry, katalogów, `GameAssembly.dll` — mamy je z poprzednich rund.
