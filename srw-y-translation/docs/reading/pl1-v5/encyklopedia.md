# Encyklopedia SRW Y — polski indeks haseł

Wszystkie wpisy czterech tabel `dic_text_*` (podstawka i DLC), w kolejności wierszy
źródłowych tabel — osobno dla każdej tabeli, bez układania chronologii gry.
Każdy wpis ma **klucz Shared Data** i adres wiersza S6. W tym dokumencie nie ma
żadnego tekstu obcego: brakujący polski opis jest jawnym znacznikiem `[BRAK PL]`.

## Skąd pochodzą i jak są przypisane

Teksty pochodzą z tabel lokalizacyjnych w odzyskanych bundlach gry.
Rekordy właścicielskie (która postać/mech dostaje który wariant opisu) są w 11
assetach `*DictionaryEntryTable*`, które właściciel gry przysłał w pakiecie
`SRW_Y_ENCYKLOPEDIA.zip`. Powiązanie jest **dokładne**: `BaseID → TextID → klucz
Shared Data`, bez dopasowywania po nazwie, prefiksie ani podobieństwie.
Dostępne polskie opisy pochodzą z zaakceptowanych planów; brakujące części
są oznaczone `[BRAK PL]`, bez zmiany potwierdzonego powiązania.

Assety właścicielskie: **11** (paczkę zweryfikowano sumą SHA-256).

| asset | wierszy | bundle | CAB | PathID |
|---|---:|---|---|---|
| PilotDictionaryEntryTable | 546 | `28581885` | `CAB-01f86635f91bb3bbfc48d41a90271f43` | 1129104669845470025 |
| PilotDictionaryEntryTable\_D1 | 25 | `f623b6c7` | `CAB-0935c7317cf754c75fbc68ed343b45f4` | 927690676583782947 |
| PilotDictionaryEntryTable\_D2 | 20 | `29eda1d3` | `CAB-e0655e611f46612a442d7a3d0afeefdf` | -9080974526686167828 |
| PilotDictionaryEntryTable\_D3 | 96 | `8da124fa` | `CAB-70f1b497e305c35f20dd4f78d34cd557` | -3646492316749395310 |
| PilotDictionaryEntryTable\_D4 | 99 | `dfc36f73` | `CAB-55e44ff834f09b04fe4d125fb3037887` | 4685436187128819781 |
| RobotDictionaryEntryTable | 782 | `a1537bb9` | `CAB-c527b0c4ad67127e06ca4e34dad41692` | -4955802041619837238 |
| RobotDictionaryEntryTable\_D1 | 38 | `37540e8d` | `CAB-5a6b3557f372ea810509d6fb71c2580a` | -6951290935163468961 |
| RobotDictionaryEntryTable\_D2 | 31 | `7c18bc90` | `CAB-038905bc5974f780551ddad26f1a8002` | 862235853776947275 |
| RobotDictionaryEntryTable\_D3 | 116 | `a78e44cc` | `CAB-709543f6a5cbe5e2d49dcdd4e83cd49b` | -6496906234422478195 |
| RobotDictionaryEntryTable\_D4 | 253 | `50fa37a7` | `CAB-eaec9c38717cf0447e78329783bdc222` | -292049997751584111 |
| WordDictionaryEntryTable | 78 | `9e46587d` | `CAB-70c519ef6a8d3fa6c1726f843465f00b` | 4957098788972794372 |

## Potwierdzone powiązania rekordów

Każdy z poniższych wierszy to dosłowny odczyt z assetu właścicielskiego.
Liczba części to liczba kluczy Shared Data przypisanych do danego `TextID`
(tabela podstawowa oraz rozszerzenia DLC).

### Postacie

| ID rekordu | klucz tekstu | części | asset |
|---|---|---:|---|
| AID | AID | 3 | PilotDictionaryEntryTable |
| AITY | AITY | 3 | PilotDictionaryEntryTable |
| AKIK | AKIK | 3 | PilotDictionaryEntryTable\_D1 |
| AKIRA | AKIRA | 3 | PilotDictionaryEntryTable |
| AKIRA\_C | AKIRA | 3 | PilotDictionaryEntryTable\_D3 |
| AKIRA\_S | AKIRA | 3 | PilotDictionaryEntryTable |
| AKIRA\_SD | AKIRA | 3 | PilotDictionaryEntryTable\_D4 |
| ALF | ALF | 6 | PilotDictionaryEntryTable\_D1 |
| ALF\_S | ALF\_S | 3 | PilotDictionaryEntryTable\_D1 |
| ALYA | ALYA | 3 | PilotDictionaryEntryTable |
| AMANE | AMANE | 3 | PilotDictionaryEntryTable |
| AMARI | AMARI | 6 | PilotDictionaryEntryTable |
| AMARI\_S | AMARI\_S | 3 | PilotDictionaryEntryTable |
| AMASAKI | AMASAKI | 3 | PilotDictionaryEntryTable |
| AMNDR | AMNDR | 3 | PilotDictionaryEntryTable |
| AMRO | AMRO | 3 | PilotDictionaryEntryTable |
| AMRO\_C | AMRO | 3 | PilotDictionaryEntryTable\_D3 |
| AMRO\_P | AMRO | 3 | PilotDictionaryEntryTable |
| AMRO\_S | AMRO | 3 | PilotDictionaryEntryTable |
| AMU | AMU | 3 | PilotDictionaryEntryTable |
| AMU\_S | AMU | 3 | PilotDictionaryEntryTable |
| ANGE | ANGE | 3 | PilotDictionaryEntryTable\_D3 |
| ANGE\_S | ANGE | 3 | PilotDictionaryEntryTable\_D3 |
| ANINA | ANINA | 3 | PilotDictionaryEntryTable |
| ANJU | ANJU\_S | 3 | PilotDictionaryEntryTable |
| ANJU\_S | ANJU\_S | 3 | PilotDictionaryEntryTable |
| ANJU\_S0 | ANJU\_S | 3 | PilotDictionaryEntryTable |
| ANJU\_S2 | ANJU\_S | 3 | PilotDictionaryEntryTable |
| ANJU\_SD | ANJU\_S | 3 | PilotDictionaryEntryTable\_D4 |
| ANJU\_SD2 | ANJU\_S | 3 | PilotDictionaryEntryTable\_D4 |
| ANTON | ANTON | 3 | PilotDictionaryEntryTable |
| ARAD | ARAD | 3 | PilotDictionaryEntryTable |
| ARAD\_S | ARAD | 3 | PilotDictionaryEntryTable |
| AREBE | AREBE | 3 | PilotDictionaryEntryTable |
| AREBE\_S | AREBE | 3 | PilotDictionaryEntryTable |
| AREN | AREN | 3 | PilotDictionaryEntryTable |
| ARNST | ARNST | 3 | PilotDictionaryEntryTable |
| ARNYA | ARNYA | 3 | PilotDictionaryEntryTable |
| ARUGO | ARUGO | 3 | PilotDictionaryEntryTable |
| ARUGO\_C | ARUGO | 3 | PilotDictionaryEntryTable\_D3 |
| ARUGO\_S | ARUGO | 3 | PilotDictionaryEntryTable |
| ASAGI | ASAGI\_S | 3 | PilotDictionaryEntryTable |
| ASAGI\_P | ASAGI\_S | 3 | PilotDictionaryEntryTable |
| ASAGI\_S | ASAGI\_S | 3 | PilotDictionaryEntryTable |
| ASAGI\_S2 | ASAGI\_S | 3 | PilotDictionaryEntryTable |
| ASAGI\_SD | ASAGI\_S | 3 | PilotDictionaryEntryTable\_D4 |
| ASRAN | ASRAN\_P | 3 | PilotDictionaryEntryTable |
| ASRAN\_C | ASRAN\_P | 3 | PilotDictionaryEntryTable\_D3 |
| ASRAN\_CS | ASRAN\_P | 3 | PilotDictionaryEntryTable\_D3 |
| ASRAN\_P | ASRAN\_P | 3 | PilotDictionaryEntryTable |
| ASRAN\_S | ASRAN\_P | 3 | PilotDictionaryEntryTable |
| ASRAN\_SS | ASRAN\_P | 3 | PilotDictionaryEntryTable |
| ASUT | ASUT | 3 | PilotDictionaryEntryTable |
| AXEL | AXEL | 3 | PilotDictionaryEntryTable\_D1 |
| BAKU | BAKU\_S | 3 | PilotDictionaryEntryTable |
| BAKU\_P | BAKU\_S | 3 | PilotDictionaryEntryTable |
| BAKU\_S | BAKU\_S | 3 | PilotDictionaryEntryTable |
| BAKU\_SD | BAKU\_S | 3 | PilotDictionaryEntryTable\_D4 |
| BALT | BALT | 3 | PilotDictionaryEntryTable |
| BALT\_C | BALT | 3 | PilotDictionaryEntryTable\_D3 |
| BARAO | BARAO | 3 | PilotDictionaryEntryTable |
| BAT | BAT | 3 | PilotDictionaryEntryTable |
| BB | BB | 3 | PilotDictionaryEntryTable |
| BECK | BECK | 3 | PilotDictionaryEntryTable\_D1 |
| BELME | BELME | 3 | PilotDictionaryEntryTable |
| BELME\_S | BELME | 3 | PilotDictionaryEntryTable\_D4 |
| BELT | BELT | 3 | PilotDictionaryEntryTable\_D3 |
| BEROS | BEROS | 3 | PilotDictionaryEntryTable |
| BEROS\_X | BEROS | 3 | PilotDictionaryEntryTable |
| BESS | BESS | 3 | PilotDictionaryEntryTable |
| BITUL | BITUL\_S | 3 | PilotDictionaryEntryTable |
| BITUL\_S | BITUL\_S | 3 | PilotDictionaryEntryTable |
| BLKKNIGHT | BURN | 3 | PilotDictionaryEntryTable |
| BLKKNIGHT\_C | BURN | 3 | PilotDictionaryEntryTable\_D3 |
| BOAG | BOAG | 3 | PilotDictionaryEntryTable |
| BOAG\_S | BOAG | 3 | PilotDictionaryEntryTable |
| BOLBNA | BOLBNA | 3 | PilotDictionaryEntryTable |
| BOSSK | BOSSK | 3 | PilotDictionaryEntryTable |
| BOY | BOY | 3 | PilotDictionaryEntryTable\_D1 |
| BURAI | BURAI | 3 | PilotDictionaryEntryTable |
| BURAI\_C | BURAI | 3 | PilotDictionaryEntryTable\_D3 |
| BURN | BURN | 3 | PilotDictionaryEntryTable |
| BURNG | BURNG | 3 | PilotDictionaryEntryTable |
| BURN\_C | BURN | 3 | PilotDictionaryEntryTable\_D3 |
| BURN\_F | BURN | 3 | PilotDictionaryEntryTable |
| BYS | BYS | 3 | PilotDictionaryEntryTable |
| CAMIYU | CAMIYU | 3 | PilotDictionaryEntryTable |
| CAMIYU\_C | CAMIYU | 3 | PilotDictionaryEntryTable\_D3 |
| CAMIYU\_S | CAMIYU | 3 | PilotDictionaryEntryTable |
| CASHA | CASHA | 3 | PilotDictionaryEntryTable\_D3 |
| CASHA\_E | CASHA | 3 | PilotDictionaryEntryTable\_D3 |
| CASHA\_S | CASHA | 3 | PilotDictionaryEntryTable\_D3 |
| CATOR | CATOR | 3 | PilotDictionaryEntryTable |
| CATOR\_C | CATOR | 3 | PilotDictionaryEntryTable\_D3 |
| CATOR\_D | CATOR | 3 | PilotDictionaryEntryTable\_D4 |
| CC | CC\_S | 3 | PilotDictionaryEntryTable |
| CC\_C | CC\_E | 3 | PilotDictionaryEntryTable\_D3 |
| CC\_P | CC\_S | 3 | PilotDictionaryEntryTable |
| CC\_S | CC\_S | 3 | PilotDictionaryEntryTable |
| CC\_X | CC\_S | 3 | PilotDictionaryEntryTable |
| CEDO | CEDO | 3 | PilotDictionaryEntryTable\_D4 |
| CESIL | CESIL | 3 | PilotDictionaryEntryTable |
| CHACK | CHACK | 3 | PilotDictionaryEntryTable |
| CHACK\_S | CHACK | 3 | PilotDictionaryEntryTable |
| CHAM | CHAM | 3 | PilotDictionaryEntryTable |
| CHAM\_C | CHAM | 3 | PilotDictionaryEntryTable\_D3 |
| CHAM\_S | CHAM | 3 | PilotDictionaryEntryTable |
| CHAR | CHAR\_ | 3 | PilotDictionaryEntryTable |
| CHAR\_C | CHAR\_ | 3 | PilotDictionaryEntryTable\_D3 |
| CHAR\_P | CHAR\_ | 3 | PilotDictionaryEntryTable |
| CHAR\_S | CHAR\_ | 3 | PilotDictionaryEntryTable |
| CHEAN | CHEAN | 3 | PilotDictionaryEntryTable |
| CHIBOD | CHIBOD | 3 | PilotDictionaryEntryTable |
| CHIBOD\_C | CHIBOD | 3 | PilotDictionaryEntryTable\_D3 |
| CHIBOD\_E | CHIBOD | 3 | PilotDictionaryEntryTable |
| CHIBOD\_S | CHIBOD | 3 | PilotDictionaryEntryTable |
| CHISE | CHISE | 3 | PilotDictionaryEntryTable |
| CHITOSE | CHITOSE | 3 | PilotDictionaryEntryTable |
| CHNDR | CHNDR\_S | 3 | PilotDictionaryEntryTable |
| CHNDR\_P | CHNDR\_S | 3 | PilotDictionaryEntryTable |
| CHNDR\_S | CHNDR\_S | 3 | PilotDictionaryEntryTable |
| CHUCHU | CHUCHU | 3 | PilotDictionaryEntryTable |
| CHUCHU\_S | CHUCHU | 3 | PilotDictionaryEntryTable |
| CHUCHU\_S2 | CHUCHU | 3 | PilotDictionaryEntryTable\_D4 |
| CHUCHU\_S3 | CHUCHU | 3 | PilotDictionaryEntryTable\_D4 |
| CHZUR | CHZUR | 3 | PilotDictionaryEntryTable |
| CHZUR\_C | CHZUR | 3 | PilotDictionaryEntryTable\_D3 |
| CLAIN | CLAIN | 3 | PilotDictionaryEntryTable |
| CLAIN\_S | CLAIN | 3 | PilotDictionaryEntryTable |
| CLAIN\_S2 | CLAIN | 3 | PilotDictionaryEntryTable |
| CLREUM | CLREUM | 3 | PilotDictionaryEntryTable |
| CLREUM\_F | CLREUM | 3 | PilotDictionaryEntryTable |
| CONERIA | CONERIA | 3 | PilotDictionaryEntryTable |
| COOKIN | COOKIN | 3 | PilotDictionaryEntryTable |
| COSMO | COSMO | 3 | PilotDictionaryEntryTable\_D3 |
| COSMO\_E | COSMO | 3 | PilotDictionaryEntryTable\_D3 |
| COSMO\_L | COSMO | 3 | PilotDictionaryEntryTable\_D3 |
| COSMO\_S | COSMO | 3 | PilotDictionaryEntryTable\_D3 |
| CROW | CROW | 3 | PilotDictionaryEntryTable\_D4 |
| CROW\_1 | CROW | 3 | PilotDictionaryEntryTable\_D4 |
| CYCYCI | CYCYCI | 3 | PilotDictionaryEntryTable |
| CYCYCI\_C | CYCYCI | 3 | PilotDictionaryEntryTable\_D3 |
| CYCYCI\_E | CYCYCI | 3 | PilotDictionaryEntryTable |
| CYCYCI\_S | CYCYCI | 3 | PilotDictionaryEntryTable |
| CYHIRO | CYHIRO | 3 | PilotDictionaryEntryTable\_D2 |
| CYHIRO2 | CYHIRO2 | 3 | PilotDictionaryEntryTable\_D2 |
| DABA | DABA | 3 | PilotDictionaryEntryTable |
| DABA\_S | DABA | 3 | PilotDictionaryEntryTable |
| DABA\_S2 | DABA | 3 | PilotDictionaryEntryTable |
| DABA\_SD | DABA | 3 | PilotDictionaryEntryTable\_D4 |
| DABA\_X | DABA | 3 | PilotDictionaryEntryTable |
| DAIMA | DAIMA | 3 | PilotDictionaryEntryTable |
| DAISK | DAISK | 3 | PilotDictionaryEntryTable |
| DAISK\_C | DAISK | 3 | PilotDictionaryEntryTable\_D3 |
| DANIEL | DANIEL | 3 | PilotDictionaryEntryTable |
| DANN | DANN | 3 | PilotDictionaryEntryTable |
| DAV | DAV | 3 | PilotDictionaryEntryTable\_D1 |
| DEAK | DEAK | 3 | PilotDictionaryEntryTable |
| DEGAWA | DEGAWA | 3 | PilotDictionaryEntryTable |
| DEKIM | DEKIM | 3 | PilotDictionaryEntryTable |
| DEKU | DEKU | 3 | PilotDictionaryEntryTable\_D3 |
| DEKU\_E | DEKU | 3 | PilotDictionaryEntryTable\_D3 |
| DEKU\_S | DEKU | 3 | PilotDictionaryEntryTable\_D3 |
| DERING | DERING | 3 | PilotDictionaryEntryTable |
| DERING\_S | DERING | 3 | PilotDictionaryEntryTable\_D4 |
| DEWEY | DEWEY | 3 | PilotDictionaryEntryTable\_D3 |
| DGAN | DGAN | 9 | PilotDictionaryEntryTable\_D2 |
| DGAN\_GX | DGAN\_GX | 3 | PilotDictionaryEntryTable\_D2 |
| DGAN\_X | DGAN\_X | 3 | PilotDictionaryEntryTable\_D2 |
| DNTEK | DNTEK | 3 | PilotDictionaryEntryTable |
| DOLGN | DOLGN | 3 | PilotDictionaryEntryTable |
| DOLGN\_C | DOLGN | 3 | PilotDictionaryEntryTable |
| DOLGN\_S | DOLGN | 3 | PilotDictionaryEntryTable |
| DOLOSY | DOLOSY | 3 | PilotDictionaryEntryTable |
| DOMON | DOMON | 3 | PilotDictionaryEntryTable |
| DOMON\_C | DOMON | 3 | PilotDictionaryEntryTable\_D3 |
| DOMON\_S | DOMON | 3 | PilotDictionaryEntryTable |
| DOMON\_S2 | DOMON | 3 | PilotDictionaryEntryTable |
| DREIK | DREIK | 3 | PilotDictionaryEntryTable |
| DREIK\_C | DREIK | 3 | PilotDictionaryEntryTable\_D3 |
| DREIK\_S | DREIK | 3 | PilotDictionaryEntryTable |
| DRKJENK | DRKJENK | 3 | PilotDictionaryEntryTable |
| DRTHY | DRTHY | 3 | PilotDictionaryEntryTable\_D1 |
| DUO | DUO | 3 | PilotDictionaryEntryTable |
| DUO\_C | DUO | 3 | PilotDictionaryEntryTable\_D3 |
| DUO\_D | DUO | 3 | PilotDictionaryEntryTable\_D4 |
| ECHIKA | ECHIKA | 3 | PilotDictionaryEntryTable |
| ECHIKA\_1 | ECHIKA | 3 | PilotDictionaryEntryTable |
| ECHIKA\_2S | ECHIKA | 3 | PilotDictionaryEntryTable |
| ECHIKA\_S | ECHIKA | 3 | PilotDictionaryEntryTable |
| ECHIKA\_X | ECHIKA | 3 | PilotDictionaryEntryTable |
| EEL | EEL | 3 | PilotDictionaryEntryTable |
| EEL\_C | EEL | 3 | PilotDictionaryEntryTable\_D3 |
| EIMIS | EIMIS | 3 | PilotDictionaryEntryTable |
| ELDN | ELDN | 3 | PilotDictionaryEntryTable |
| ELDN\_C | ELDN | 3 | PilotDictionaryEntryTable\_D3 |
| ELICT | ELICT | 3 | PilotDictionaryEntryTable\_D4 |
| EMA | EMA | 3 | PilotDictionaryEntryTable |
| EMA\_C | EMA | 3 | PilotDictionaryEntryTable\_D3 |
| EMA\_S | EMA | 3 | PilotDictionaryEntryTable |
| ENAO | EONA | 3 | PilotDictionaryEntryTable |
| ENAO\_S | EONA | 3 | PilotDictionaryEntryTable |
| ENBRW | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_1 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_10 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_2 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_3 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_4 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_5 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_6 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_7 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_8 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENBRW\_9 | ENBRW | 3 | PilotDictionaryEntryTable\_D3 |
| ENDE | ENDE | 3 | PilotDictionaryEntryTable |
| ERAN | ERAN | 9 | PilotDictionaryEntryTable |
| ERAN\_5D | ERAN\_5S | 3 | PilotDictionaryEntryTable\_D4 |
| ERAN\_5S | ERAN\_5S | 3 | PilotDictionaryEntryTable\_D4 |
| ERAN\_5S2 | ERAN\_5S | 3 | PilotDictionaryEntryTable\_D4 |
| ERAN\_5S3 | ERAN\_5S | 3 | PilotDictionaryEntryTable\_D4 |
| ERAN\_D | ERAN | 9 | PilotDictionaryEntryTable |
| ERAN\_S | ERAN | 9 | PilotDictionaryEntryTable |
| ERAN\_SF | ERAN | 9 | PilotDictionaryEntryTable |
| ERAN\_T | ERAN\_D | 3 | PilotDictionaryEntryTable\_D4 |
| EUREK | EUREK | 3 | PilotDictionaryEntryTable\_D3 |
| EUREK\_S | EUREK | 3 | PilotDictionaryEntryTable\_D3 |
| EUREK\_S2 | EUREK | 3 | PilotDictionaryEntryTable\_D3 |
| EXIS | EXIS | 3 | PilotDictionaryEntryTable\_D2 |
| EXIS\_E | EXIS | 3 | PilotDictionaryEntryTable\_D2 |
| EXIS\_E2 | EXIS | 3 | PilotDictionaryEntryTable\_D2 |
| FA | FA | 3 | PilotDictionaryEntryTable |
| FA\_C | FA | 3 | PilotDictionaryEntryTable\_D3 |
| FA\_S | FA | 3 | PilotDictionaryEntryTable |
| FEI | FEI | 3 | PilotDictionaryEntryTable |
| FELCY | FELCY | 3 | PilotDictionaryEntryTable |
| FELCY\_S | FELCY | 3 | PilotDictionaryEntryTable\_D4 |
| FHERO | FHERO | 6 | PilotDictionaryEntryTable |
| FHERO\_S | FHERO\_S | 3 | PilotDictionaryEntryTable |
| FRAT | FRAT | 3 | PilotDictionaryEntryTable |
| FREIA | FREIA | 3 | PilotDictionaryEntryTable |
| FREIA\_P | FREIA | 3 | PilotDictionaryEntryTable |
| FREIA\_S | FREIA | 3 | PilotDictionaryEntryTable |
| FREIA\_X | FREIA | 3 | PilotDictionaryEntryTable |
| GABLY | GABLY\_ | 3 | PilotDictionaryEntryTable |
| GABLY\_C | GABLY\_ | 3 | PilotDictionaryEntryTable\_D3 |
| GABLY\_F | GABLY\_ | 3 | PilotDictionaryEntryTable |
| GALDA | GALDA | 3 | PilotDictionaryEntryTable |
| GALDA\_B | GALDA | 3 | PilotDictionaryEntryTable |
| GALDA\_X | GALDA | 3 | PilotDictionaryEntryTable |
| GALKIE | GALKIE | 3 | PilotDictionaryEntryTable |
| GAON | GAON | 3 | PilotDictionaryEntryTable\_D2 |
| GAUMA | GAUMA | 3 | PilotDictionaryEntryTable |
| GAUMAI\_X | GAUMA | 3 | PilotDictionaryEntryTable |
| GAUMA\_D | GAUMA | 3 | PilotDictionaryEntryTable\_D4 |
| GGONK | GGONK | 3 | PilotDictionaryEntryTable |
| GLDBRN | GLDBRN | 3 | PilotDictionaryEntryTable |
| GNRY | GNRY | 3 | PilotDictionaryEntryTable |
| GOAL | GOAL | 3 | PilotDictionaryEntryTable |
| GOLNE | GOLNE | 3 | PilotDictionaryEntryTable |
| GOOGOL\_S | GOOGOL | 3 | PilotDictionaryEntryTable\_D4 |
| GOOGOL\_S2 | GOOGOL | 3 | PilotDictionaryEntryTable\_D4 |
| GOUA | GOUA | 3 | PilotDictionaryEntryTable |
| GOZR | GOZR | 3 | PilotDictionaryEntryTable |
| GRIDKT | GRIDKT | 3 | PilotDictionaryEntryTable |
| GRIDKT\_D | GRIDKT | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_2 | GUERU | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU\_2S | GUERU | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU\_2SE | GUERU | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU\_H | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_HS | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_P | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_P1 | GUERU | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU\_P2 | GUERU | 3 | PilotDictionaryEntryTable\_D4 |
| GUERU\_S | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_S2 | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_S3 | GUERU | 3 | PilotDictionaryEntryTable |
| GUERU\_SF | GUERU | 3 | PilotDictionaryEntryTable |
| GUNEI | GUNEI | 3 | PilotDictionaryEntryTable |
| GUNEI\_C | GUNEI | 3 | PilotDictionaryEntryTable\_D3 |
| GUNEI\_S | GUNEI | 3 | PilotDictionaryEntryTable |
| GWAZA | GWAZA | 3 | PilotDictionaryEntryTable |
| HABEL | HABEL | 3 | PilotDictionaryEntryTable |
| HADEK | HADEK | 3 | PilotDictionaryEntryTable |
| HAN | HAN | 3 | PilotDictionaryEntryTable |
| HANS | HANS | 3 | PilotDictionaryEntryTable |
| HARUK | HARUK | 3 | PilotDictionaryEntryTable\_D3 |
| HARUK\_S | HARUK | 3 | PilotDictionaryEntryTable\_D3 |
| HASYA | HASYA | 3 | PilotDictionaryEntryTable |
| HAYATE | HAYATE | 3 | PilotDictionaryEntryTable |
| HAYATE\_S | HAYATE | 3 | PilotDictionaryEntryTable |
| HAYATE\_SD | HAYATE | 3 | PilotDictionaryEntryTable\_D4 |
| HAYATOA | HAYATOA | 3 | PilotDictionaryEntryTable |
| HAYAT\_B | HAYAT\_B | 3 | PilotDictionaryEntryTable\_D2 |
| HECRR | HECRR | 3 | PilotDictionaryEntryTable |
| HELMA | HELMA | 3 | PilotDictionaryEntryTable |
| HELMA\_S | HELMA | 3 | PilotDictionaryEntryTable |
| HIGASHI | HIGASHI | 3 | PilotDictionaryEntryTable |
| HIKA | HIKA | 3 | PilotDictionaryEntryTable\_D2 |
| HILDE | HILDE | 3 | PilotDictionaryEntryTable |
| HINTS | HINTS | 3 | PilotDictionaryEntryTable |
| HIROS | HIROS | 3 | PilotDictionaryEntryTable\_D2 |
| HOPES | HOPES | 3 | PilotDictionaryEntryTable |
| HOTA | HOTA | 3 | PilotDictionaryEntryTable\_D2 |
| HYOMA | HYOMA | 3 | PilotDictionaryEntryTable |
| HYOMA\_C | HYOMA | 3 | PilotDictionaryEntryTable\_D3 |
| HYOMA\_D | HYOMA | 3 | PilotDictionaryEntryTable\_D4 |
| HYRO | HYRO | 3 | PilotDictionaryEntryTable |
| HYRO\_C | HYRO | 3 | PilotDictionaryEntryTable\_D3 |
| HYRO\_D | HYRO | 3 | PilotDictionaryEntryTable\_D4 |
| HYRO\_G | HYRO | 3 | PilotDictionaryEntryTable |
| ICHIRO | ICHIRO | 3 | PilotDictionaryEntryTable |
| IGARI | IGARI | 3 | PilotDictionaryEntryTable |
| ILISHA | ILIJA | 3 | PilotDictionaryEntryTable |
| ILISH\_S | ILIJA | 3 | PilotDictionaryEntryTable |
| INAMT | INAMT | 3 | PilotDictionaryEntryTable |
| IORI | IORI | 6 | PilotDictionaryEntryTable |
| IORI\_S | IORI\_S | 3 | PilotDictionaryEntryTable |
| IRIS | IRIS | 6 | PilotDictionaryEntryTable\_D3 |
| IRIS\_30 | IRIS\_30 | 3 | PilotDictionaryEntryTable\_D1 |
| IVRVER | IVRVER | 3 | PilotDictionaryEntryTable |
| IZAK | IZAK | 3 | PilotDictionaryEntryTable |
| IZANA | IZANA | 3 | PilotDictionaryEntryTable |
| IZANA\_X | IZANA | 3 | PilotDictionaryEntryTable |
| IZAQ | IZAQ | 3 | PilotDictionaryEntryTable\_D1 |
| IZURU | IZURU\_S | 3 | PilotDictionaryEntryTable |
| IZURU\_P | IZURU\_S | 3 | PilotDictionaryEntryTable |
| IZURU\_S | IZURU\_S | 3 | PilotDictionaryEntryTable |
| IZURU\_SD | IZURU\_S | 3 | PilotDictionaryEntryTable\_D4 |
| IZURU\_SX | IZURU\_S | 3 | PilotDictionaryEntryTable |
| IZURU\_SX2 | IZURU\_S | 3 | PilotDictionaryEntryTable |
| JAKOBA | JAKOBA | 3 | PilotDictionaryEntryTable |
| JBRL | JBRL | 3 | PilotDictionaryEntryTable |
| JEEG | JEEG | 6 | PilotDictionaryEntryTable\_D2 |
| JEREM | JEREM | 6 | PilotDictionaryEntryTable |
| JEREM\_C | JEREM\_A | 3 | PilotDictionaryEntryTable\_D3 |
| JJAGUAR | JJAGUAR | 3 | PilotDictionaryEntryTable |
| JJAGUAR\_D | JJAGUAR | 3 | PilotDictionaryEntryTable\_D4 |
| JORJU | JORJU | 3 | PilotDictionaryEntryTable |
| JORJU\_C | JORJU | 3 | PilotDictionaryEntryTable\_D3 |
| JORJU\_S | JORJU | 3 | PilotDictionaryEntryTable |
| JRIANO | JRIANO | 3 | PilotDictionaryEntryTable |
| JRIL | JRIL | 3 | PilotDictionaryEntryTable |
| JUGA | JUGA | 3 | PilotDictionaryEntryTable |
| JUGA\_F | JUGA | 3 | PilotDictionaryEntryTable |
| JUNK | JUNK | 3 | PilotDictionaryEntryTable |
| JUZO | JUZO | 3 | PilotDictionaryEntryTable |
| JUZO\_C | JUZO | 3 | PilotDictionaryEntryTable\_D3 |
| KAGA | KAGA | 3 | PilotDictionaryEntryTable |
| KAITAKE | KAITAKE | 3 | PilotDictionaryEntryTable |
| KAL | KAL | 3 | PilotDictionaryEntryTable |
| KAMMOM | KAMMOM | 3 | PilotDictionaryEntryTable |
| KAMRN | KAMRN | 3 | PilotDictionaryEntryTable |
| KAMUI | KAMUI\_S | 3 | PilotDictionaryEntryTable |
| KAMUI\_E | KAMUI\_S | 3 | PilotDictionaryEntryTable |
| KAMUI\_S | KAMUI\_S | 3 | PilotDictionaryEntryTable |
| KAMUI\_SD | KAMUI\_S | 3 | PilotDictionaryEntryTable\_D4 |
| KANAME | KANAME | 3 | PilotDictionaryEntryTable |
| KANAME\_P | KANAME | 3 | PilotDictionaryEntryTable |
| KANAME\_S | KANAME | 3 | PilotDictionaryEntryTable |
| KANO | KANO | 3 | PilotDictionaryEntryTable |
| KANOKO | KANOKO | 3 | PilotDictionaryEntryTable |
| KAREN | KAREN | 6 | PilotDictionaryEntryTable |
| KAREN\_C | KAREN\_A | 3 | PilotDictionaryEntryTable\_D3 |
| KAREN\_P | KAREN | 6 | PilotDictionaryEntryTable |
| KAREN\_P2 | KAREN | 6 | PilotDictionaryEntryTable |
| KAREN\_S | KAREN | 6 | PilotDictionaryEntryTable |
| KAREN\_X | KAREN | 6 | PilotDictionaryEntryTable |
| KASIM | KASIM | 3 | PilotDictionaryEntryTable |
| KASIM\_S | KASIM | 3 | PilotDictionaryEntryTable |
| KAWASE | KAWASE | 3 | PilotDictionaryEntryTable |
| KAWASE\_C | KAWASE | 3 | PilotDictionaryEntryTable\_D3 |
| KEEN | KEEN | 3 | PilotDictionaryEntryTable |
| KEES | KEES | 3 | PilotDictionaryEntryTable |
| KEES2 | KEES | 3 | PilotDictionaryEntryTable |
| KEES2\_F | KEES | 3 | PilotDictionaryEntryTable |
| KEES2\_S | KEES | 3 | PilotDictionaryEntryTable |
| KEES\_C | KEES | 3 | PilotDictionaryEntryTable\_D3 |
| KEES\_S | KEES | 3 | PilotDictionaryEntryTable |
| KEI | KEI\_S | 3 | PilotDictionaryEntryTable |
| KEI\_P | KEI\_S | 3 | PilotDictionaryEntryTable |
| KEI\_S | KEI\_S | 3 | PilotDictionaryEntryTable |
| KEI\_SD | KEI\_S | 3 | PilotDictionaryEntryTable\_D4 |
| KENAN | KENAN | 3 | PilotDictionaryEntryTable\_D4 |
| KENAN\_P | KENAN | 3 | PilotDictionaryEntryTable\_D4 |
| KENAN\_S | KENAN | 3 | PilotDictionaryEntryTable\_D4 |
| KGRIDKT | KGRIDKT | 3 | PilotDictionaryEntryTable |
| KGRIDKT\_D | KGRIDKT | 3 | PilotDictionaryEntryTable\_D4 |
| KIDJ | KIDJ | 3 | PilotDictionaryEntryTable\_D1 |
| KIRA | KIRA\_P | 3 | PilotDictionaryEntryTable |
| KIRA\_C | KIRA\_P | 3 | PilotDictionaryEntryTable\_D3 |
| KIRA\_CS | KIRA\_P | 3 | PilotDictionaryEntryTable\_D3 |
| KIRA\_P | KIRA\_P | 3 | PilotDictionaryEntryTable |
| KIRA\_S | KIRA\_P | 3 | PilotDictionaryEntryTable |
| KIRA\_SS | KIRA\_P | 3 | PilotDictionaryEntryTable |
| KISA | KISA | 3 | PilotDictionaryEntryTable |
| KJAPAT | KJAPAT | 3 | PilotDictionaryEntryTable |
| KNIGHT | KNIGHT | 3 | PilotDictionaryEntryTable |
| KOMEI | KOMEI | 3 | PilotDictionaryEntryTable |
| KOMINE | KOMINE | 3 | PilotDictionaryEntryTable |
| KOSKE | KOSKE | 3 | PilotDictionaryEntryTable |
| KOSKE\_C | KOSKE | 3 | PilotDictionaryEntryTable\_D3 |
| KOUZIK | KOUZIK | 3 | PilotDictionaryEntryTable |
| KOUZIK\_C | KOUZIK | 3 | PilotDictionaryEntryTable\_D3 |
| KOUZIK\_S | KOUZIK | 3 | PilotDictionaryEntryTable |
| KOUZIK\_SD | KOUZIK | 3 | PilotDictionaryEntryTable\_D4 |
| KOYOMI | KOYOMI | 3 | PilotDictionaryEntryTable |
| KOYOMI\_D | KOYOMI | 3 | PilotDictionaryEntryTable\_D4 |
| KURO | KURO | 3 | PilotDictionaryEntryTable |
| KYAO | KYAO | 3 | PilotDictionaryEntryTable |
| KYUZO | KYUZO | 3 | PilotDictionaryEntryTable |
| LADY | LADY | 3 | PilotDictionaryEntryTable |
| LLS | LLS | 3 | PilotDictionaryEntryTable |
| LLSH | LLSH | 6 | PilotDictionaryEntryTable |
| LLSH\_C | LLSH\_E | 3 | PilotDictionaryEntryTable\_D3 |
| LLSH\_D | LLSH | 6 | PilotDictionaryEntryTable\_D4 |
| LLSH\_P | LLSH | 6 | PilotDictionaryEntryTable |
| LLSH\_X | LLSH | 6 | PilotDictionaryEntryTable |
| LLS\_S | LLS | 3 | PilotDictionaryEntryTable |
| LLY | LLY | 3 | PilotDictionaryEntryTable |
| LUTEL | LUTEL | 3 | PilotDictionaryEntryTable |
| LUTEL\_S | LUTEL | 3 | PilotDictionaryEntryTable |
| LUU | LUU | 3 | PilotDictionaryEntryTable\_D3 |
| MACD | MACD | 3 | PilotDictionaryEntryTable |
| MACD\_S | MACD | 3 | PilotDictionaryEntryTable |
| MACHI | MACHI | 3 | PilotDictionaryEntryTable\_D1 |
| MACTMN | MACTMN | 3 | PilotDictionaryEntryTable |
| MACTMN2 | MACTMN | 3 | PilotDictionaryEntryTable |
| MAKINA | MAKINA | 3 | PilotDictionaryEntryTable |
| MAKINA\_P | MAKINA | 3 | PilotDictionaryEntryTable |
| MAKINA\_S | MAKINA | 3 | PilotDictionaryEntryTable |
| MALTN | MALTN | 3 | PilotDictionaryEntryTable |
| MALTN\_S | MALTN | 3 | PilotDictionaryEntryTable |
| MALTN\_SY | MALTN | 3 | PilotDictionaryEntryTable\_D4 |
| MARBL | MARBL | 3 | PilotDictionaryEntryTable |
| MARBL\_C | MARBL | 3 | PilotDictionaryEntryTable\_D3 |
| MARBL\_S | MARBL | 3 | PilotDictionaryEntryTable |
| MARI | MARI | 3 | PilotDictionaryEntryTable |
| MARYM | MARYM | 3 | PilotDictionaryEntryTable |
| MARYM\_P | MARYM | 3 | PilotDictionaryEntryTable |
| MASAKI | MASAKI | 3 | PilotDictionaryEntryTable |
| MATBR | MATBR | 3 | PilotDictionaryEntryTable |
| MAYG | MAYG | 3 | PilotDictionaryEntryTable |
| MAYG\_S | MAYG | 3 | PilotDictionaryEntryTable |
| MAYU | MAYU | 3 | PilotDictionaryEntryTable |
| MEI | MEI | 3 | PilotDictionaryEntryTable |
| MEIDZ | MEIDZ | 3 | PilotDictionaryEntryTable |
| MERAN | MERAN | 3 | PilotDictionaryEntryTable |
| MERAN\_C | MERAN | 3 | PilotDictionaryEntryTable\_D3 |
| MERIL | MERIL | 3 | PilotDictionaryEntryTable |
| MESSA | MESSA | 3 | PilotDictionaryEntryTable |
| MESSA\_S | MESSA | 3 | PilotDictionaryEntryTable |
| MESSA\_SD | MESSA | 3 | PilotDictionaryEntryTable\_D4 |
| MEYRIN | MEYRIN | 3 | PilotDictionaryEntryTable |
| MEYRIN\_C | MEYRIN | 3 | PilotDictionaryEntryTable\_D3 |
| MHERO | MHERO | 6 | PilotDictionaryEntryTable |
| MHERO\_E | MHERO\_S | 3 | PilotDictionaryEntryTable |
| MHERO\_S | MHERO\_S | 3 | PilotDictionaryEntryTable |
| MIKUMO | MIKUMO | 3 | PilotDictionaryEntryTable |
| MIKUMO\_E | MIKUMO | 3 | PilotDictionaryEntryTable |
| MIKUMO\_P | MIKUMO | 3 | PilotDictionaryEntryTable |
| MIKUMO\_S | MIKUMO | 3 | PilotDictionaryEntryTable |
| MINA | MINA | 3 | PilotDictionaryEntryTable |
| MINA\_S | MINA | 3 | PilotDictionaryEntryTable |
| MINA\_X | MINA | 3 | PilotDictionaryEntryTable |
| MIOLN | MIOLN | 3 | PilotDictionaryEntryTable |
| MIOLN\_BS | MIOLN | 3 | PilotDictionaryEntryTable\_D4 |
| MIOLN\_D | MIOLN | 3 | PilotDictionaryEntryTable |
| MIOLN\_P | MIOLN | 3 | PilotDictionaryEntryTable\_D4 |
| MIOLN\_S | MIOLN | 3 | PilotDictionaryEntryTable |
| MIOLN\_S2 | MIOLN | 3 | PilotDictionaryEntryTable\_D4 |
| MIRAGE | MIRAGE | 3 | PilotDictionaryEntryTable |
| MIRAGE\_S | MIRAGE | 3 | PilotDictionaryEntryTable |
| MIREY | MIREY | 3 | PilotDictionaryEntryTable |
| MIRIARIA | MIRIARIA | 3 | PilotDictionaryEntryTable |
| MIWA | MIWA | 3 | PilotDictionaryEntryTable\_D2 |
| MRARIZ | MRARIZ | 3 | PilotDictionaryEntryTable |
| MRMRK | MRMRK | 3 | PilotDictionaryEntryTable |
| MUSASHIA | MUSASHIA | 3 | PilotDictionaryEntryTable |
| MUSAS\_B | MUSAS\_B | 3 | PilotDictionaryEntryTable\_D2 |
| MUTYAK | MUTYAK | 3 | PilotDictionaryEntryTable |
| MUZINA | MUZINA | 3 | PilotDictionaryEntryTable |
| MUZINA\_F | MUZINA | 3 | PilotDictionaryEntryTable |
| NANA | NANA | 3 | PilotDictionaryEntryTable |
| NAZI | NAZI | 3 | PilotDictionaryEntryTable\_D4 |
| NEBLNNA | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBLNNA\_1 | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBLNNA\_2 | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBLNNA\_3 | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBLNNA\_4 | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBLNNA\_5 | NEBLNNA | 3 | PilotDictionaryEntryTable |
| NEBORA | NEBORA | 3 | PilotDictionaryEntryTable |
| NEE | NEE | 3 | PilotDictionaryEntryTable |
| NEENA | NEENA | 3 | PilotDictionaryEntryTable |
| NEGSIS | NEGSIS | 3 | PilotDictionaryEntryTable |
| NEKO | NEKO | 3 | PilotDictionaryEntryTable\_D1 |
| NEWGEN | NEWGEN | 3 | PilotDictionaryEntryTable |
| NEY | NEY | 3 | PilotDictionaryEntryTable |
| NEY\_C | NEY | 3 | PilotDictionaryEntryTable\_D3 |
| NEY\_F | NEY | 3 | PilotDictionaryEntryTable |
| NIDAI | NIDAI | 3 | PilotDictionaryEntryTable |
| NINE | NINE | 3 | PilotDictionaryEntryTable |
| NINE2 | NINE | 3 | PilotDictionaryEntryTable |
| NKA | NKA | 6 | PilotDictionaryEntryTable |
| NKA\_SY | NKA\_SY | 3 | PilotDictionaryEntryTable\_D4 |
| NNRY | NNRY | 3 | PilotDictionaryEntryTable |
| NNRY\_X | NNRY | 3 | PilotDictionaryEntryTable |
| NOIN | NOIN | 3 | PilotDictionaryEntryTable |
| NOREA | NOREA | 3 | PilotDictionaryEntryTable\_D4 |
| NOREA\_P | NOREA | 3 | PilotDictionaryEntryTable\_D4 |
| NOREA\_P2 | NOREA | 3 | PilotDictionaryEntryTable\_D4 |
| NOREA\_S | NOREA | 3 | PilotDictionaryEntryTable\_D4 |
| NOREA\_S2 | NOREA | 3 | PilotDictionaryEntryTable\_D4 |
| NOSSOK | NOSSOK | 3 | PilotDictionaryEntryTable |
| NOVY | NOVY | 3 | PilotDictionaryEntryTable |
| NTSHA | NTSHA | 3 | PilotDictionaryEntryTable |
| NUKEK | NUKEK | 3 | PilotDictionaryEntryTable |
| NUNO | NUNO | 3 | PilotDictionaryEntryTable |
| OJRO | OJRO | 3 | PilotDictionaryEntryTable |
| OJRO\_S | OJRO | 3 | PilotDictionaryEntryTable |
| OLBY | OLBY | 3 | PilotDictionaryEntryTable |
| OLBY\_C | OLBY | 3 | PilotDictionaryEntryTable\_D3 |
| OLBY\_F | OLBY | 3 | PilotDictionaryEntryTable |
| OLCOT | OLCOT | 3 | PilotDictionaryEntryTable\_D4 |
| ONIJA | ONIJA | 3 | PilotDictionaryEntryTable |
| ONIJA\_F | ONIJA | 3 | PilotDictionaryEntryTable |
| OTAKI | OTAKI | 3 | PilotDictionaryEntryTable |
| OUGI | OUGI | 3 | PilotDictionaryEntryTable |
| PERO2 | PERO2 | 3 | PilotDictionaryEntryTable |
| PERO2R | PERO2R | 3 | PilotDictionaryEntryTable |
| PERO2\_D | PERO2 | 3 | PilotDictionaryEntryTable\_D4 |
| PETRA | PETRA | 3 | PilotDictionaryEntryTable |
| PETRA\_BS | PETRA | 3 | PilotDictionaryEntryTable\_D4 |
| PHILP | PHILP | 3 | PilotDictionaryEntryTable\_D1 |
| PONCH | PONCH | 3 | PilotDictionaryEntryTable\_D1 |
| POSEIDL | POSEIDL | 6 | PilotDictionaryEntryTable |
| POSEIDL\_S | POSEIDL\_S | 3 | PilotDictionaryEntryTable |
| PROSPE | PROSPE | 3 | PilotDictionaryEntryTable |
| PROSPE\_S | PROSPE | 3 | PilotDictionaryEntryTable\_D4 |
| PTRIC | PTRIC\_S | 3 | PilotDictionaryEntryTable |
| PTRIC\_P | PTRIC\_S | 3 | PilotDictionaryEntryTable |
| PTRIC\_S | PTRIC\_S | 3 | PilotDictionaryEntryTable |
| QEIN | QEIN | 3 | PilotDictionaryEntryTable |
| QUES | QUES | 3 | PilotDictionaryEntryTable |
| QUES\_C | QUES | 3 | PilotDictionaryEntryTable\_D3 |
| QUES\_S | QUES | 3 | PilotDictionaryEntryTable |
| RABAN | RABAN | 3 | PilotDictionaryEntryTable |
| RABAN\_S | RABAN | 3 | PilotDictionaryEntryTable |
| RACSHTA | RACSHTA | 3 | PilotDictionaryEntryTable |
| RADA | RADA | 3 | PilotDictionaryEntryTable |
| RADA\_S | RADA | 3 | PilotDictionaryEntryTable |
| RAIL | RAIL | 3 | PilotDictionaryEntryTable |
| RAIL\_C | RAIL | 3 | PilotDictionaryEntryTable\_D3 |
| RAIN | RAIN | 3 | PilotDictionaryEntryTable |
| RAIN\_S | RAIN | 3 | PilotDictionaryEntryTable |
| RAKUS | RAKUS\_P | 3 | PilotDictionaryEntryTable |
| RAKUS\_C | RAKUS\_P | 3 | PilotDictionaryEntryTable\_D3 |
| RAKUS\_CS | RAKUS\_P | 3 | PilotDictionaryEntryTable\_D3 |
| RAKUS\_P | RAKUS\_P | 3 | PilotDictionaryEntryTable |
| RAKUS\_SS | RAKUS\_P | 3 | PilotDictionaryEntryTable |
| RAMYY | RAMYY | 3 | PilotDictionaryEntryTable |
| RANDY | RANDY\_S | 3 | PilotDictionaryEntryTable |
| RANDY\_P | RANDY\_S | 3 | PilotDictionaryEntryTable |
| RANDY\_S | RANDY\_S | 3 | PilotDictionaryEntryTable |
| RAUDA | RAUDA | 6 | PilotDictionaryEntryTable |
| RAUDA\_BS | RAUDA | 6 | PilotDictionaryEntryTable\_D4 |
| RAUDA\_S | RAUDA | 6 | PilotDictionaryEntryTable\_D4 |
| RAUDA\_S2 | RAUDA\_S2 | 3 | PilotDictionaryEntryTable\_D4 |
| REA | REA | 3 | PilotDictionaryEntryTable\_D1 |
| REDRN | REDRN | 3 | PilotDictionaryEntryTable\_D2 |
| REEKA | REEKA | 3 | PilotDictionaryEntryTable |
| REENA | REENA | 3 | PilotDictionaryEntryTable |
| REIASUKA | REIASUKA | 3 | PilotDictionaryEntryTable |
| REIKA | REIKA | 3 | PilotDictionaryEntryTable |
| REIKO | REIKO | 3 | PilotDictionaryEntryTable |
| REINA | REINA | 3 | PilotDictionaryEntryTable |
| REINA\_P | REINA | 3 | PilotDictionaryEntryTable |
| REINA\_S | REINA | 3 | PilotDictionaryEntryTable |
| REMURU | REMURU | 3 | PilotDictionaryEntryTable |
| RENE | RENE | 3 | PilotDictionaryEntryTable |
| RENE\_S | RENE | 3 | PilotDictionaryEntryTable |
| RENREN | RENREN | 3 | PilotDictionaryEntryTable |
| RENTN | RENTN | 3 | PilotDictionaryEntryTable\_D3 |
| RERENA | RERENA | 3 | PilotDictionaryEntryTable |
| RESSY | RESSY | 3 | PilotDictionaryEntryTable |
| RESSY2 | RESSY2 | 3 | PilotDictionaryEntryTable |
| RESSY2\_S | RESSY2 | 3 | PilotDictionaryEntryTable |
| RESSY\_S | RESSY | 3 | PilotDictionaryEntryTable |
| REZN\_C | REZN\_S | 3 | PilotDictionaryEntryTable\_D3 |
| REZN\_S | REZN\_S | 3 | PilotDictionaryEntryTable |
| RIDERW | RIDERW | 3 | PilotDictionaryEntryTable\_D1 |
| RIZOU | RIZOU | 3 | PilotDictionaryEntryTable |
| ROGER | ROGER | 3 | PilotDictionaryEntryTable\_D1 |
| ROID\_D | ROID | 3 | PilotDictionaryEntryTable |
| ROID\_D2 | ROID | 3 | PilotDictionaryEntryTable |
| ROPET | ROPET | 3 | PilotDictionaryEntryTable |
| ROUJI | ROUJI | 3 | PilotDictionaryEntryTable |
| ROYD | ROYD | 3 | PilotDictionaryEntryTable |
| RRKE | RRKE | 3 | PilotDictionaryEntryTable |
| RRKE\_S | RRKE | 3 | PilotDictionaryEntryTable |
| RUMES | RUMES | 3 | PilotDictionaryEntryTable |
| RUMES\_S | RUMES | 3 | PilotDictionaryEntryTable |
| RUNA | RUNA | 3 | PilotDictionaryEntryTable |
| RUNA\_S | RUNA | 3 | PilotDictionaryEntryTable |
| RURA | RURA | 3 | PilotDictionaryEntryTable |
| RYOKLY | RYOKLY | 3 | PilotDictionaryEntryTable |
| RYOMA\_BS | RYOMA\_B | 3 | PilotDictionaryEntryTable\_D2 |
| SABINA | SABINA | 3 | PilotDictionaryEntryTable |
| SABINA\_S | SABINA | 3 | PilotDictionaryEntryTable |
| SAGIRI | SAGIRI | 6 | PilotDictionaryEntryTable |
| SAGIRI\_S | SAGIRI\_S | 3 | PilotDictionaryEntryTable |
| SAIZOU | SAIZOU | 6 | PilotDictionaryEntryTable |
| SAIZOU\_S | SAIZOU\_S | 3 | PilotDictionaryEntryTable |
| SALIUS | SALIUS | 3 | PilotDictionaryEntryTable |
| SALY | SALY | 3 | PilotDictionaryEntryTable |
| SARU | SARU | 3 | PilotDictionaryEntryTable |
| SATO | SATO | 3 | PilotDictionaryEntryTable |
| SATOMI | SATOMI | 3 | PilotDictionaryEntryTable |
| SAYAKAK | SAYAKAK | 3 | PilotDictionaryEntryTable |
| SAYOKO | SAYOKO | 3 | PilotDictionaryEntryTable |
| SAYOKO\_X | SAYOKO | 3 | PilotDictionaryEntryTable |
| SCULL | SCULL | 3 | PilotDictionaryEntryTable\_D1 |
| SEIJ | SEIJ | 6 | PilotDictionaryEntryTable\_D2 |
| SEIJ\_S | SEIJ\_S | 3 | PilotDictionaryEntryTable\_D2 |
| SEWAK | SEWAK | 3 | PilotDictionaryEntryTable |
| SEYVAS | SEYVAS | 3 | PilotDictionaryEntryTable |
| SEYVAS\_C | SEYVAS | 3 | PilotDictionaryEntryTable\_D3 |
| SEYVAS\_F | SEYVAS | 3 | PilotDictionaryEntryTable |
| SEYVAS\_G | SEYVAS | 3 | PilotDictionaryEntryTable |
| SGATA | SGATA | 3 | PilotDictionaryEntryTable\_D3 |
| SHAMNA | SHAMNA | 3 | PilotDictionaryEntryTable |
| SHARIO | SHARIO | 3 | PilotDictionaryEntryTable |
| SHARIO\_S | SHARIO | 3 | PilotDictionaryEntryTable |
| SHESTA | SHESTA | 3 | PilotDictionaryEntryTable |
| SHIKI | SHIKI | 3 | PilotDictionaryEntryTable |
| SHIRA | SHIRA | 3 | PilotDictionaryEntryTable |
| SHIRA\_C | SHIRA | 3 | PilotDictionaryEntryTable\_D3 |
| SHIRA\_S | SHIRA | 3 | PilotDictionaryEntryTable |
| SHIRO | SHIRO | 3 | PilotDictionaryEntryTable |
| SHIROKO | SHIROKO | 3 | PilotDictionaryEntryTable\_D4 |
| SHIROKO2 | SHIROKO | 3 | PilotDictionaryEntryTable\_D4 |
| SHIZM | SHIZM | 3 | PilotDictionaryEntryTable |
| SHIZM\_F | SHIZM | 3 | PilotDictionaryEntryTable |
| SHOT | SHOT | 3 | PilotDictionaryEntryTable |
| SHOT2 | SHOT2 | 3 | PilotDictionaryEntryTable |
| SHOTA | SHOTA | 3 | PilotDictionaryEntryTable\_D1 |
| SHOU | SHOU | 3 | PilotDictionaryEntryTable |
| SHOUG | SHOUG | 3 | PilotDictionaryEntryTable |
| SHOU\_C | SHOU | 3 | PilotDictionaryEntryTable\_D3 |
| SHOU\_S | SHOU | 3 | PilotDictionaryEntryTable |
| SHOU\_SD | SHOU | 3 | PilotDictionaryEntryTable\_D4 |
| SHRLY | SHRLY | 3 | PilotDictionaryEntryTable |
| SHUNA | SHUNA | 3 | PilotDictionaryEntryTable |
| SHUVI | SHUVI | 3 | PilotDictionaryEntryTable |
| SHUWA | SHUWA | 3 | PilotDictionaryEntryTable |
| SHVRT | SHVRT | 3 | PilotDictionaryEntryTable\_D1 |
| SIMON | SIMON | 3 | PilotDictionaryEntryTable |
| SIN | SIN | 3 | PilotDictionaryEntryTable |
| SIN\_S | SIN | 3 | PilotDictionaryEntryTable |
| SIN\_S1 | SIN | 3 | PilotDictionaryEntryTable |
| SIN\_SS | SIN | 3 | PilotDictionaryEntryTable |
| SION | SION | 3 | PilotDictionaryEntryTable |
| SION2 | SION | 3 | PilotDictionaryEntryTable |
| SIRKI | SIRKI | 3 | PilotDictionaryEntryTable |
| SISTIS | SISTIS | 3 | PilotDictionaryEntryTable\_D4 |
| SISTIS\_F | SISTIS | 3 | PilotDictionaryEntryTable\_D4 |
| SISTIS\_X | SISTIS | 3 | PilotDictionaryEntryTable |
| SLETA | SLETA\_G | 3 | PilotDictionaryEntryTable |
| SLETA\_D | SLETA\_G | 3 | PilotDictionaryEntryTable |
| SLETA\_F | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_G | SLETA\_G | 3 | PilotDictionaryEntryTable |
| SLETA\_GS | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_GS2 | SLETA\_G | 3 | PilotDictionaryEntryTable |
| SLETA\_GS3 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_GS4 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_S | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_S1 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_S2 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_S3 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SLETA\_S4 | SLETA\_G | 3 | PilotDictionaryEntryTable\_D4 |
| SOFI | SOFI | 3 | PilotDictionaryEntryTable\_D4 |
| SOFI\_P | SOFI | 3 | PilotDictionaryEntryTable\_D4 |
| SOFI\_S | SOFI | 3 | PilotDictionaryEntryTable\_D4 |
| SOFI\_S2 | SOFI | 3 | PilotDictionaryEntryTable\_D4 |
| SOKI | SOUKITI | 3 | PilotDictionaryEntryTable\_D1 |
| SOUJI | SOUJI | 3 | PilotDictionaryEntryTable |
| SRUGA | SRUGA\_S | 3 | PilotDictionaryEntryTable |
| SRUGA\_P | SRUGA\_S | 3 | PilotDictionaryEntryTable |
| SRUGA\_S | SRUGA\_S | 3 | PilotDictionaryEntryTable |
| SRUGA\_SD | SRUGA\_S | 3 | PilotDictionaryEntryTable\_D4 |
| SSRIA | SSRIA | 3 | PilotDictionaryEntryTable |
| STOKER | STOKER | 3 | PilotDictionaryEntryTable |
| SUZAK | SUZAK\_S | 3 | PilotDictionaryEntryTable |
| SUZAK\_C | SUZAK\_E | 3 | PilotDictionaryEntryTable\_D3 |
| SUZAK\_S | SUZAK\_S | 3 | PilotDictionaryEntryTable |
| SUZAK\_SG | SUZAK\_S | 3 | PilotDictionaryEntryTable |
| SUZAK\_X | SUZAK\_S | 3 | PilotDictionaryEntryTable |
| SUZAK\_X2 | SUZAK\_S | 3 | PilotDictionaryEntryTable |
| SYADIK | SYADIK | 3 | PilotDictionaryEntryTable |
| SYADIK\_D | SYADIK | 3 | PilotDictionaryEntryTable |
| SYADIK\_P | SYADIK | 3 | PilotDictionaryEntryTable\_D4 |
| SYADIK\_S | SYADIK | 3 | PilotDictionaryEntryTable |
| SYADIK\_S2 | SYADIK | 3 | PilotDictionaryEntryTable\_D4 |
| SZKAZE | SZKAZE | 3 | PilotDictionaryEntryTable |
| TAKT | TAKT | 3 | PilotDictionaryEntryTable\_D3 |
| TAKT\_S | TAKT | 3 | PilotDictionaryEntryTable\_D3 |
| TAKUMA | TAKUMA\_S | 3 | PilotDictionaryEntryTable |
| TAKUMA\_P | TAKUMA\_S | 3 | PilotDictionaryEntryTable |
| TAKUMA\_S | TAKUMA\_S | 3 | PilotDictionaryEntryTable |
| TAKUMA\_SD | TAKUMA\_S | 3 | PilotDictionaryEntryTable\_D4 |
| TAMA | TAMA\_S | 3 | PilotDictionaryEntryTable |
| TAMAKI | TAMAKI | 3 | PilotDictionaryEntryTable |
| TAMA\_P | TAMA\_S | 3 | PilotDictionaryEntryTable |
| TAMA\_S | TAMA\_S | 3 | PilotDictionaryEntryTable |
| TAMA\_SD | TAMA\_S | 3 | PilotDictionaryEntryTable\_D4 |
| TBON | TBON | 3 | PilotDictionaryEntryTable\_D1 |
| TEO | TEO | 3 | PilotDictionaryEntryTable |
| TEORIA | TEORIA | 3 | PilotDictionaryEntryTable |
| TEO\_S | TEO | 3 | PilotDictionaryEntryTable |
| TERU | TERU | 3 | PilotDictionaryEntryTable\_D1 |
| TETUYAK | TETUYAK | 3 | PilotDictionaryEntryTable |
| TETUYAK\_C | TETUYAK | 3 | PilotDictionaryEntryTable\_D3 |
| TETUYAK\_S | TETUYAK | 3 | PilotDictionaryEntryTable |
| TETUYAK\_SD | TETUYAK | 3 | PilotDictionaryEntryTable\_D4 |
| TFFHAI | TFFHAI | 3 | PilotDictionaryEntryTable |
| TIL | TIL | 3 | PilotDictionaryEntryTable |
| TILDA | TILDA | 3 | PilotDictionaryEntryTable |
| TIL\_S | TIL | 3 | PilotDictionaryEntryTable |
| TODO | TODO | 3 | PilotDictionaryEntryTable |
| TODO\_C | TODO | 3 | PilotDictionaryEntryTable\_D3 |
| TODO\_G | TODO | 3 | PilotDictionaryEntryTable |
| TODO\_S | TODO | 3 | PilotDictionaryEntryTable |
| TODO\_SF | TODO | 3 | PilotDictionaryEntryTable |
| TOEN | TOEN | 3 | PilotDictionaryEntryTable |
| TOKI | TOKI | 3 | PilotDictionaryEntryTable\_D1 |
| TOROWA | TOROWA | 3 | PilotDictionaryEntryTable |
| TOROWA\_C | TOROWA | 3 | PilotDictionaryEntryTable\_D3 |
| TOROWA\_D | TOROWA | 3 | PilotDictionaryEntryTable\_D4 |
| UFEY | UFEY | 3 | PilotDictionaryEntryTable |
| UFEY\_D | UFEY | 3 | PilotDictionaryEntryTable\_D4 |
| UFEY\_E | UFEY | 3 | PilotDictionaryEntryTable |
| UFEY\_G | UFEY | 3 | PilotDictionaryEntryTable |
| ULBE | ULBE | 3 | PilotDictionaryEntryTable |
| USPR\_S | USPR\_S | 3 | PilotDictionaryEntryTable\_D3 |
| VALBLM | VALBLM | 3 | PilotDictionaryEntryTable\_D4 |
| VALBLM2 | VALBLM | 3 | PilotDictionaryEntryTable |
| VALBLM\_F | VALBLM | 3 | PilotDictionaryEntryTable\_D4 |
| VALBLM\_P | VALBLM | 3 | PilotDictionaryEntryTable |
| VALBLM\_X | VALBLM | 3 | PilotDictionaryEntryTable |
| VALBLM\_X2 | VALBLM | 3 | PilotDictionaryEntryTable |
| VIM | VIM | 3 | PilotDictionaryEntryTable |
| VIM\_S | VIM | 3 | PilotDictionaryEntryTable\_D4 |
| WAKO | WAKO | 3 | PilotDictionaryEntryTable\_D3 |
| WON | WON | 3 | PilotDictionaryEntryTable |
| YAGAMI | YAGAMI | 6 | PilotDictionaryEntryTable |
| YAGAMI\_S | YAGAMI\_S | 3 | PilotDictionaryEntryTable\_D4 |
| YAZAN | YAZAN | 3 | PilotDictionaryEntryTable\_D4 |
| YAZAN\_C | YAZAN | 3 | PilotDictionaryEntryTable\_D3 |
| YAZAN\_S | YAZAN | 3 | PilotDictionaryEntryTable\_D4 |
| YAZAN\_SF | YAZAN | 3 | PilotDictionaryEntryTable\_D4 |
| YOMOGI | YOMOGI | 3 | PilotDictionaryEntryTable |
| YOMOGI\_D | YOMOGI | 3 | PilotDictionaryEntryTable\_D4 |
| YOMOGI\_X | YOMOGI | 3 | PilotDictionaryEntryTable |
| YOMOMUM | YOMOMUM | 3 | PilotDictionaryEntryTable |
| YOTYA | YOTYA | 3 | PilotDictionaryEntryTable |
| YUME | YUME | 3 | PilotDictionaryEntryTable |
| YUME\_D | YUME | 3 | PilotDictionaryEntryTable\_D4 |
| YUMIK | YUMIK | 3 | PilotDictionaryEntryTable |
| YUN | YUN | 3 | PilotDictionaryEntryTable |
| ZAO | ZAO | 3 | PilotDictionaryEntryTable |
| ZAO\_S | ZAO | 3 | PilotDictionaryEntryTable |
| ZEE | ZEE | 3 | PilotDictionaryEntryTable |
| ZEKS | ZEKS | 3 | PilotDictionaryEntryTable |
| ZERO | ZERO | 3 | PilotDictionaryEntryTable |
| ZERO\_G | SUZAK\_X | 3 | PilotDictionaryEntryTable |
| ZERO\_X | SUZAK\_X | 3 | PilotDictionaryEntryTable |
| ZIAT | ZIAT | 3 | PilotDictionaryEntryTable |
| ZIAT\_S | ZIAT | 3 | PilotDictionaryEntryTable |
| ZIAT\_S2 | ZIAT | 3 | PilotDictionaryEntryTable |
| ZIKFRT | ZIKFRT | 3 | PilotDictionaryEntryTable |

### Mechy

| ID rekordu | klucz tekstu | części | asset |
|---|---|---:|---|
| AAZIL | AAZIL | 2 | RobotDictionaryEntryTable |
| AAZIL\_E | AAZIL | 2 | RobotDictionaryEntryTable |
| ANGELOI\_AL | ANGELOI\_AL | 2 | RobotDictionaryEntryTable\_D4 |
| ANGELOI\_AL\_2 | ANGELOI\_AL | 2 | RobotDictionaryEntryTable\_D4 |
| ARG\_EW | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARG\_EW2 | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARG\_EW\_D | ARG\_EW | 2 | RobotDictionaryEntryTable\_D4 |
| ARG\_EW\_E | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARG\_EW\_E2 | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARG\_EW\_ED | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARG\_EW\_G | ARG\_EW | 2 | RobotDictionaryEntryTable |
| ARKDIA | ARKDIA | 2 | RobotDictionaryEntryTable |
| ARKDIA2 | ARKDIA | 2 | RobotDictionaryEntryTable |
| ASRAT | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT2 | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_D1 | ASRAT | 2 | RobotDictionaryEntryTable\_D4 |
| ASRAT\_D2 | ASRAT | 2 | RobotDictionaryEntryTable\_D4 |
| ASRAT\_P | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_PC | ASRAT | 2 | RobotDictionaryEntryTable\_D3 |
| ASRAT\_S1 | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_S2 | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_SD | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_S\_C1 | ASRAT | 2 | RobotDictionaryEntryTable |
| ASRAT\_S\_C4 | ASRAT | 2 | RobotDictionaryEntryTable |
| ATOL5 | ATOL5 | 2 | RobotDictionaryEntryTable |
| ATOL5\_2 | ATOL5 | 2 | RobotDictionaryEntryTable |
| ATOL5\_C2 | ATOL5 | 2 | RobotDictionaryEntryTable |
| ATOL5\_C4 | ATOL5 | 2 | RobotDictionaryEntryTable |
| ATOL5\_D | ATOL5 | 2 | RobotDictionaryEntryTable |
| ATOL5\_D1 | ATOL5 | 2 | RobotDictionaryEntryTable\_D4 |
| ATOL5\_D2 | ATOL5 | 2 | RobotDictionaryEntryTable\_D4 |
| AUG | AUG | 2 | RobotDictionaryEntryTable |
| AUGE | AUGE | 2 | RobotDictionaryEntryTable |
| AUGE2 | AUGE | 2 | RobotDictionaryEntryTable |
| AUGE\_C | AUGE | 2 | RobotDictionaryEntryTable\_D3 |
| AUGE\_C2 | AUGE | 2 | RobotDictionaryEntryTable |
| AUGE\_C4 | AUGE | 2 | RobotDictionaryEntryTable |
| AUGE\_D | AUGE | 2 | RobotDictionaryEntryTable |
| AUGE\_D1 | AUGE | 2 | RobotDictionaryEntryTable\_D4 |
| AUGE\_P | AUGE | 2 | RobotDictionaryEntryTable |
| AUG\_2 | AUG | 2 | RobotDictionaryEntryTable |
| AUG\_C5 | AUG | 2 | RobotDictionaryEntryTable |
| AUG\_D2 | AUG | 2 | RobotDictionaryEntryTable\_D4 |
| BARS | BARS | 2 | RobotDictionaryEntryTable |
| BARS2 | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_C2 | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_C4 | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_D1 | BARS | 2 | RobotDictionaryEntryTable\_D4 |
| BARS\_P | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_PC | BARS | 2 | RobotDictionaryEntryTable\_D3 |
| BARS\_S1 | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_S2 | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_SD | BARS | 2 | RobotDictionaryEntryTable |
| BARS\_SD1 | BARS | 2 | RobotDictionaryEntryTable\_D4 |
| BARS\_SD2 | BARS | 2 | RobotDictionaryEntryTable\_D4 |
| BASH | BASH | 2 | RobotDictionaryEntryTable |
| BASH2 | BASH | 2 | RobotDictionaryEntryTable |
| BASH2\_D1 | BASH | 2 | RobotDictionaryEntryTable\_D4 |
| BASH3 | BASH | 2 | RobotDictionaryEntryTable |
| BASH3\_D2 | BASH | 2 | RobotDictionaryEntryTable\_D4 |
| BASH\_C1 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_C2 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_C4 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_S1 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_S2 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_SD | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_SD1 | BASH | 2 | RobotDictionaryEntryTable\_D4 |
| BASH\_SD2 | BASH | 2 | RobotDictionaryEntryTable\_D4 |
| BASH\_S\_C2 | BASH | 2 | RobotDictionaryEntryTable |
| BASH\_S\_C4 | BASH | 2 | RobotDictionaryEntryTable |
| BBDX | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_2 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_3 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_4 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_B | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_B2 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_B3 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BBDX\_B4 | BBDX | 2 | RobotDictionaryEntryTable\_D1 |
| BGGRD | BGGRD | 2 | RobotDictionaryEntryTable |
| BGGRD2 | BGGRD | 2 | RobotDictionaryEntryTable |
| BGGRD\_C2 | BGGRD | 2 | RobotDictionaryEntryTable |
| BGGRD\_C5 | BGGRD | 2 | RobotDictionaryEntryTable |
| BGGRD\_D | BGGRD | 2 | RobotDictionaryEntryTable |
| BGGRD\_D1 | BGGRD | 2 | RobotDictionaryEntryTable\_D4 |
| BGGRD\_D2 | BGGRD | 2 | RobotDictionaryEntryTable\_D4 |
| BGRPNT | BGRPNT | 2 | RobotDictionaryEntryTable |
| BIGD | BIGD | 2 | RobotDictionaryEntryTable\_D1 |
| BIGD\_2 | BIGD | 2 | RobotDictionaryEntryTable\_D1 |
| BIGD\_D | BIGD | 2 | RobotDictionaryEntryTable\_D1 |
| BIGO | BIGO | 2 | RobotDictionaryEntryTable\_D1 |
| BKDR | BKDR | 2 | RobotDictionaryEntryTable |
| BKDR2 | BKDR | 2 | RobotDictionaryEntryTable |
| BKDR3 | BKDR | 2 | RobotDictionaryEntryTable |
| BKDR\_D | BKDR | 2 | RobotDictionaryEntryTable |
| BKDR\_D1 | BKDR | 2 | RobotDictionaryEntryTable\_D4 |
| BKDR\_D2 | BKDR | 2 | RobotDictionaryEntryTable\_D4 |
| BLBAIN | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBAIN2 | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBAIN\_C2 | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBAIN\_C5 | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBAIN\_D | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBAIN\_D1 | BLBAIN | 2 | RobotDictionaryEntryTable\_D4 |
| BLBAIN\_DS | BLBAIN | 2 | RobotDictionaryEntryTable\_D4 |
| BLBAIN\_FST | BLBAIN | 2 | RobotDictionaryEntryTable |
| BLBD | BLBD | 4 | RobotDictionaryEntryTable |
| BLBD2 | BLBD | 4 | RobotDictionaryEntryTable |
| BLBD3 | BLBD | 4 | RobotDictionaryEntryTable |
| BLBD\_B | BLBD\_B | 2 | RobotDictionaryEntryTable |
| BLBD\_B2 | BLBD\_B | 2 | RobotDictionaryEntryTable |
| BLBD\_B3 | BLBD\_B | 2 | RobotDictionaryEntryTable |
| BLBD\_B\_C1 | BLBD\_B | 2 | RobotDictionaryEntryTable |
| BLBIN | BLBIN | 2 | RobotDictionaryEntryTable |
| BLBIN2 | BLBIN | 2 | RobotDictionaryEntryTable |
| BLBIN\_C | BLBIN | 2 | RobotDictionaryEntryTable\_D3 |
| BLBIN\_D | BLBIN | 2 | RobotDictionaryEntryTable\_D4 |
| BLU1 | BLU1 | 2 | RobotDictionaryEntryTable |
| BLU1\_2 | BLU1 | 2 | RobotDictionaryEntryTable |
| BLU1\_3 | BLU1 | 2 | RobotDictionaryEntryTable |
| BLU1\_4 | BLU1 | 2 | RobotDictionaryEntryTable |
| BLU1\_D | BLU1 | 2 | RobotDictionaryEntryTable\_D4 |
| BLU1\_D2 | BLU1 | 2 | RobotDictionaryEntryTable\_D4 |
| BRAO | BRAO | 2 | RobotDictionaryEntryTable |
| BRAO\_C5 | BRAO | 2 | RobotDictionaryEntryTable |
| BRAO\_D | BRAO | 2 | RobotDictionaryEntryTable |
| BRAO\_D2 | BRAO | 2 | RobotDictionaryEntryTable |
| BRAO\_D3 | BRAO | 2 | RobotDictionaryEntryTable\_D4 |
| BRIGER | BRIGER | 2 | RobotDictionaryEntryTable\_D1 |
| BRIGER\_2 | BRIGER | 2 | RobotDictionaryEntryTable\_D1 |
| BRK6 | BRK6 | 2 | RobotDictionaryEntryTable |
| BRK6\_0 | BRK6 | 2 | RobotDictionaryEntryTable |
| BRK6\_2 | BRK6 | 2 | RobotDictionaryEntryTable |
| BRK6\_3 | BRK6 | 2 | RobotDictionaryEntryTable |
| BRK6\_4 | BRK6 | 2 | RobotDictionaryEntryTable |
| BRK6\_D | BRK6 | 2 | RobotDictionaryEntryTable\_D4 |
| BRK6\_D2 | BRK6 | 2 | RobotDictionaryEntryTable\_D4 |
| BRMAG | BRMAG | 2 | RobotDictionaryEntryTable\_D3 |
| BRMAG\_2 | BRMAG | 2 | RobotDictionaryEntryTable\_D3 |
| BRMAG\_3 | BRMAG | 2 | RobotDictionaryEntryTable\_D3 |
| BRTGD | BRTGD | 2 | RobotDictionaryEntryTable |
| BRTGD2 | BRTGD | 2 | RobotDictionaryEntryTable |
| BRTGD3 | BRTGD | 2 | RobotDictionaryEntryTable |
| BRTGD\_C | BRTGD | 2 | RobotDictionaryEntryTable\_D3 |
| BRTGD\_CS | BRTGD | 2 | RobotDictionaryEntryTable\_D3 |
| BRTGD\_S | BRTGD | 2 | RobotDictionaryEntryTable |
| BRTGD\_S2 | BRTGD | 2 | RobotDictionaryEntryTable |
| BRTGD\_S3 | BRTGD | 2 | RobotDictionaryEntryTable |
| BTRD | BTRD | 2 | RobotDictionaryEntryTable |
| BTRD2 | BTRD | 2 | RobotDictionaryEntryTable |
| BTRD\_C1 | BTRD | 2 | RobotDictionaryEntryTable |
| BUGU | BUGU | 2 | RobotDictionaryEntryTable |
| CALIBARN | CALIBARN | 2 | RobotDictionaryEntryTable\_D4 |
| CALIBARN\_2 | CALIBARN | 2 | RobotDictionaryEntryTable\_D4 |
| COMV | COMV | 2 | RobotDictionaryEntryTable |
| COMV2 | COMV | 2 | RobotDictionaryEntryTable |
| COMV\_C | COMV | 2 | RobotDictionaryEntryTable\_D3 |
| COMV\_D | COMV | 2 | RobotDictionaryEntryTable\_D4 |
| CRBLT | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CRBLT2 | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CRBLT\_B | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_B2 | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_BD | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_BD1 | CRBLT\_B | 2 | RobotDictionaryEntryTable\_D4 |
| CRBLT\_BD2 | CRBLT\_B | 2 | RobotDictionaryEntryTable\_D4 |
| CRBLT\_BS1 | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_BS2 | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_B\_C1 | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_B\_C5 | CRBLT\_B | 2 | RobotDictionaryEntryTable |
| CRBLT\_D | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CRBLT\_P | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CRBLT\_PC | CRBLT\_P | 2 | RobotDictionaryEntryTable\_D3 |
| CRBLT\_S | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CRBLT\_S2 | CRBLT\_P | 2 | RobotDictionaryEntryTable |
| CYBSTER | CYBSTER | 2 | RobotDictionaryEntryTable |
| CYBSTER\_2 | CYBSTER | 2 | RobotDictionaryEntryTable |
| DANTE | DANTE | 2 | RobotDictionaryEntryTable |
| DANTE2 | DANTE | 2 | RobotDictionaryEntryTable |
| DANTE\_C1 | DANTE | 2 | RobotDictionaryEntryTable |
| DANTE\_D | DANTE | 2 | RobotDictionaryEntryTable\_D4 |
| DEMIBARD | DEMIBARD | 2 | RobotDictionaryEntryTable\_D4 |
| DEMIBARD\_2 | DEMIBARD | 2 | RobotDictionaryEntryTable\_D4 |
| DENBEL | DENBEL | 2 | RobotDictionaryEntryTable\_D1 |
| DENBEL\_2 | DENBEL | 2 | RobotDictionaryEntryTable\_D1 |
| DENBEL\_3 | DENBEL | 2 | RobotDictionaryEntryTable\_D1 |
| DENBEL\_4 | DENBEL | 2 | RobotDictionaryEntryTable\_D1 |
| DGANGX | DGANGX | 2 | RobotDictionaryEntryTable\_D2 |
| DGANX | DGANX | 2 | RobotDictionaryEntryTable\_D2 |
| DGANX\_2 | DGANX | 2 | RobotDictionaryEntryTable\_D2 |
| DIGIA | DIGIA | 2 | RobotDictionaryEntryTable |
| DIGIA2 | DIGIA | 2 | RobotDictionaryEntryTable |
| DKJEN | DKJEN | 2 | RobotDictionaryEntryTable |
| DKJEN2 | DKJEN | 2 | RobotDictionaryEntryTable |
| DKJEN\_C3 | DKJEN | 2 | RobotDictionaryEntryTable |
| DKJEN\_C5 | DKJEN | 2 | RobotDictionaryEntryTable |
| DKJEN\_D | DKJEN | 2 | RobotDictionaryEntryTable |
| DKJEN\_D1 | DKJEN | 2 | RobotDictionaryEntryTable\_D4 |
| DLCBST | DLCBST | 2 | RobotDictionaryEntryTable\_D1 |
| DLCBST\_2 | DLCBST | 2 | RobotDictionaryEntryTable\_D1 |
| DLNZA\_GEL | DLNZA\_GEL | 2 | RobotDictionaryEntryTable |
| DMTRNR\_CC | DMTRNR\_CC | 2 | RobotDictionaryEntryTable |
| DMTRNR\_CC\_D | DMTRNR\_CC | 2 | RobotDictionaryEntryTable |
| DNBIN | DNBIN | 2 | RobotDictionaryEntryTable |
| DNBIN\_C | DNBIN | 2 | RobotDictionaryEntryTable\_D3 |
| DRGGD | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD2 | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD3 | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD\_C | DRGGD | 2 | RobotDictionaryEntryTable\_D3 |
| DRGGD\_CS | DRGGD | 2 | RobotDictionaryEntryTable\_D3 |
| DRGGD\_E | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD\_S | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD\_S2 | DRGGD | 2 | RobotDictionaryEntryTable |
| DRGGD\_S3 | DRGGD | 2 | RobotDictionaryEntryTable |
| DRLBLDE\_1 | DRLBLDE | 4 | RobotDictionaryEntryTable |
| DRLBLDE\_2 | DRLBLDE | 4 | RobotDictionaryEntryTable |
| DRLBLDE\_2S | DRLBLDE\_2S | 2 | RobotDictionaryEntryTable\_D4 |
| DRLBLDE\_2SD | DRLBLDE\_2S | 2 | RobotDictionaryEntryTable\_D4 |
| DRLBLDE\_P | DRLBLDE | 4 | RobotDictionaryEntryTable |
| DRMR | DRMR | 2 | RobotDictionaryEntryTable |
| DRMR2 | DRMR | 2 | RobotDictionaryEntryTable |
| DRMR3 | DRMR | 2 | RobotDictionaryEntryTable |
| DRMR\_C2 | DRMR | 2 | RobotDictionaryEntryTable |
| DROME | DROME | 2 | RobotDictionaryEntryTable |
| DROME2 | DROME | 2 | RobotDictionaryEntryTable |
| DROME\_D | DROME | 2 | RobotDictionaryEntryTable |
| DROME\_D2 | DROME | 2 | RobotDictionaryEntryTable\_D4 |
| DSGD | DSGD | 2 | RobotDictionaryEntryTable |
| DSGD2 | DSGD | 2 | RobotDictionaryEntryTable |
| DSGD3 | DSGD | 2 | RobotDictionaryEntryTable |
| DTAM | DTAM | 2 | RobotDictionaryEntryTable |
| DTAM2 | DTAM | 2 | RobotDictionaryEntryTable |
| DTAM3 | DTAM | 2 | RobotDictionaryEntryTable |
| DTAM\_C4 | DTAM | 2 | RobotDictionaryEntryTable |
| DTAM\_D1 | DTAM | 2 | RobotDictionaryEntryTable\_D4 |
| DTAM\_D2 | DTAM | 2 | RobotDictionaryEntryTable\_D4 |
| DTAM\_W | DTAM | 2 | RobotDictionaryEntryTable |
| DVGD | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD2 | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD3 | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD\_C | DVGD | 2 | RobotDictionaryEntryTable\_D3 |
| DVGD\_C5 | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD\_D | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD\_D1 | DVGD | 2 | RobotDictionaryEntryTable\_D4 |
| DVGD\_D2 | DVGD | 2 | RobotDictionaryEntryTable |
| DVGD\_DD2 | DVGD | 2 | RobotDictionaryEntryTable\_D4 |
| DYNZNON | DYNZNON | 2 | RobotDictionaryEntryTable |
| DYNZNON2 | DYNZNON | 2 | RobotDictionaryEntryTable |
| DYNZNON3 | DYNZNON | 2 | RobotDictionaryEntryTable |
| DYNZNON\_0 | DYNZNON | 2 | RobotDictionaryEntryTable |
| DYNZNON\_D | DYNZNON | 2 | RobotDictionaryEntryTable\_D4 |
| DYNZNON\_D2 | DYNZNON | 2 | RobotDictionaryEntryTable\_D4 |
| DYNZNON\_D3 | DYNZNON | 2 | RobotDictionaryEntryTable\_D4 |
| EFAS\_OMEGA | EFAS\_OMEGA | 2 | RobotDictionaryEntryTable\_D4 |
| EFAS\_OMEGA\_2 | EFAS\_OMEGA | 2 | RobotDictionaryEntryTable\_D4 |
| EL\_MILLEN | EL\_MILLEN | 2 | RobotDictionaryEntryTable\_D4 |
| EL\_MILLEN\_2 | EL\_MILLEN | 2 | RobotDictionaryEntryTable\_D4 |
| ENDE | ENDE | 2 | RobotDictionaryEntryTable |
| ENDE2 | ENDE | 2 | RobotDictionaryEntryTable |
| ENDNOS | ENDNOS | 2 | RobotDictionaryEntryTable |
| ENDNOS2 | ENDNOS | 2 | RobotDictionaryEntryTable |
| ENDNOS\_C4 | ENDNOS | 2 | RobotDictionaryEntryTable |
| ENDNOS\_D | ENDNOS | 2 | RobotDictionaryEntryTable |
| ENDNOS\_D1 | ENDNOS | 2 | RobotDictionaryEntryTable\_D4 |
| ETNL | ETNL | 2 | RobotDictionaryEntryTable |
| ETNL\_C | ETNL | 2 | RobotDictionaryEntryTable\_D3 |
| F100R | F100R | 2 | RobotDictionaryEntryTable |
| FIGD | FIGD | 2 | RobotDictionaryEntryTable |
| FIGD2 | FIGD | 2 | RobotDictionaryEntryTable |
| FIGD3 | FIGD | 2 | RobotDictionaryEntryTable |
| GARDON | GARDON | 2 | RobotDictionaryEntryTable |
| GARDON2 | GARDON | 2 | RobotDictionaryEntryTable |
| GARDON3 | GARDON | 2 | RobotDictionaryEntryTable |
| GARDON\_C | GARDON | 2 | RobotDictionaryEntryTable\_D3 |
| GARDON\_C1 | GARDON | 2 | RobotDictionaryEntryTable |
| GARDON\_D | GARDON | 2 | RobotDictionaryEntryTable |
| GARDON\_D1 | GARDON | 2 | RobotDictionaryEntryTable\_D4 |
| GARDON\_D2 | GARDON | 2 | RobotDictionaryEntryTable\_D4 |
| GBZORG | GBZORG | 2 | RobotDictionaryEntryTable |
| GBZORG2 | GBZORG | 2 | RobotDictionaryEntryTable |
| GBZORG\_C2 | GBZORG | 2 | RobotDictionaryEntryTable |
| GBZORG\_C5 | GBZORG | 2 | RobotDictionaryEntryTable |
| GBZORG\_D | GBZORG | 2 | RobotDictionaryEntryTable |
| GBZORG\_D1 | GBZORG | 2 | RobotDictionaryEntryTable\_D4 |
| GBZORG\_DS | GBZORG | 2 | RobotDictionaryEntryTable\_D4 |
| GD2 | GD2 | 2 | RobotDictionaryEntryTable |
| GD2\_C | GD2 | 2 | RobotDictionaryEntryTable\_D3 |
| GDARRAL | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDARRALRB | GDARRALRB | 4 | RobotDictionaryEntryTable |
| GDARRALRB\_D | GDARRALRB | 4 | RobotDictionaryEntryTable\_D4 |
| GDARRALRB\_DD | GDARRALRB | 4 | RobotDictionaryEntryTable\_D4 |
| GDARRALRB\_DDW | GDARRALRB | 4 | RobotDictionaryEntryTable\_D4 |
| GDARRALRB\_E | GDARRALRB\_E | 2 | RobotDictionaryEntryTable\_D4 |
| GDARRAL\_2 | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDARRAL\_D | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDARRAL\_D0 | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDARRAL\_D2 | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDARRAL\_DW | GDARRAL | 2 | RobotDictionaryEntryTable |
| GDH\_EW | GDH\_EW | 2 | RobotDictionaryEntryTable |
| GDH\_EW2 | GDH\_EW | 2 | RobotDictionaryEntryTable |
| GDH\_EW\_C | GDH\_EW | 2 | RobotDictionaryEntryTable\_D3 |
| GDH\_EW\_D | GDH\_EW | 2 | RobotDictionaryEntryTable\_D4 |
| GDMST | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST2 | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST3 | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST\_C | GDMST | 2 | RobotDictionaryEntryTable\_D3 |
| GDMST\_CS | GDMST | 2 | RobotDictionaryEntryTable\_D3 |
| GDMST\_E | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST\_S | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST\_S2 | GDMST | 2 | RobotDictionaryEntryTable |
| GDMST\_S3 | GDMST | 2 | RobotDictionaryEntryTable |
| GDNON | GDNON | 2 | RobotDictionaryEntryTable |
| GDOGA | GDOGA | 4 | RobotDictionaryEntryTable |
| GDOGA\_B | GDOGA\_B | 2 | RobotDictionaryEntryTable |
| GDOGA\_BC | GDOGA\_B | 2 | RobotDictionaryEntryTable\_D3 |
| GDOGA\_C | GDOGA | 4 | RobotDictionaryEntryTable\_D3 |
| GDPHARCT | GDPHARCT | 4 | RobotDictionaryEntryTable |
| GDPHARCT\_5GO | GDPHARCT\_5GO | 2 | RobotDictionaryEntryTable\_D4 |
| GDPHARCT\_P | GDPHARCT | 4 | RobotDictionaryEntryTable |
| GDROS | GDROS | 2 | RobotDictionaryEntryTable |
| GDROS2 | GDROS | 2 | RobotDictionaryEntryTable |
| GDROS3 | GDROS | 2 | RobotDictionaryEntryTable |
| GDROS\_C | GDROS | 2 | RobotDictionaryEntryTable\_D3 |
| GDROS\_CS | GDROS | 2 | RobotDictionaryEntryTable\_D3 |
| GDROS\_S | GDROS | 2 | RobotDictionaryEntryTable |
| GDROS\_S2 | GDROS | 2 | RobotDictionaryEntryTable |
| GDROS\_S3 | GDROS | 2 | RobotDictionaryEntryTable |
| GEDB | GEDB | 2 | RobotDictionaryEntryTable |
| GEDB2 | GEDB | 2 | RobotDictionaryEntryTable |
| GEDB\_L | GEDB | 2 | RobotDictionaryEntryTable |
| GGENDNOS | GGENDNOS | 2 | RobotDictionaryEntryTable |
| GGENDNOS\_C5 | GGENDNOS | 2 | RobotDictionaryEntryTable |
| GGENDNOS\_D | GGENDNOS | 2 | RobotDictionaryEntryTable |
| GGENDNOS\_D1 | GGENDNOS | 2 | RobotDictionaryEntryTable\_D4 |
| GGENDNOS\_PD | GGENDNOS | 2 | RobotDictionaryEntryTable\_D4 |
| GGYRA\_1 | GGYRA\_1 | 2 | RobotDictionaryEntryTable |
| GGYRA\_1D | GGYRA\_1 | 2 | RobotDictionaryEntryTable\_D4 |
| GGYRA\_2 | GGYRA\_2 | 2 | RobotDictionaryEntryTable |
| GGYRA\_2D | GGYRA\_2 | 2 | RobotDictionaryEntryTable\_D4 |
| GGYRA\_2\_C5 | GGYRA\_2 | 2 | RobotDictionaryEntryTable |
| GHA\_EW | GHA\_EW | 2 | RobotDictionaryEntryTable |
| GHA\_EW\_2 | GHA\_EW | 2 | RobotDictionaryEntryTable |
| GHA\_EW\_C | GHA\_EW | 2 | RobotDictionaryEntryTable\_D3 |
| GHA\_EW\_D | GHA\_EW | 2 | RobotDictionaryEntryTable\_D4 |
| GKEK | GKEK | 2 | RobotDictionaryEntryTable |
| GKEK2 | GKEK | 2 | RobotDictionaryEntryTable |
| GKEK\_D | GKEK | 2 | RobotDictionaryEntryTable\_D4 |
| GKEK\_WND | GKEK2\_WN | 2 | RobotDictionaryEntryTable\_D4 |
| GLABA | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA2 | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_C | GLABA | 2 | RobotDictionaryEntryTable\_D3 |
| GLABA\_C2 | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_D | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_D1 | GLABA | 2 | RobotDictionaryEntryTable\_D4 |
| GLABA\_D2 | GLABA | 2 | RobotDictionaryEntryTable\_D4 |
| GLABA\_M | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_P | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_PC | GLABA | 2 | RobotDictionaryEntryTable\_D3 |
| GLABA\_S1 | GLABA | 2 | RobotDictionaryEntryTable |
| GLABA\_S2 | GLABA | 2 | RobotDictionaryEntryTable |
| GLD4 | GLD4 | 2 | RobotDictionaryEntryTable |
| GLD4\_2 | GLD4 | 2 | RobotDictionaryEntryTable |
| GLD4\_3 | GLD4 | 2 | RobotDictionaryEntryTable |
| GLD4\_4 | GLD4 | 2 | RobotDictionaryEntryTable |
| GLD4\_D | GLD4 | 2 | RobotDictionaryEntryTable\_D4 |
| GLD4\_D2 | GLD4 | 2 | RobotDictionaryEntryTable\_D4 |
| GLJOM | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM2 | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM\_C1 | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM\_C2 | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM\_D | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM\_D1 | GLJOM | 2 | RobotDictionaryEntryTable\_D4 |
| GLJOM\_S | GLJOM | 2 | RobotDictionaryEntryTable |
| GLJOM\_S2 | GLJOM | 2 | RobotDictionaryEntryTable |
| GMAZINGS | GMAZINGS | 2 | RobotDictionaryEntryTable |
| GMAZINGS\_C | GMAZINGS | 2 | RobotDictionaryEntryTable\_D3 |
| GMTGD | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD2 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD3 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_C3 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_C4 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_C5 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_D | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_D1 | GMTGD | 2 | RobotDictionaryEntryTable\_D4 |
| GMTGD\_D2 | GMTGD | 2 | RobotDictionaryEntryTable\_D4 |
| GMTGD\_S1 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_S2 | GMTGD | 2 | RobotDictionaryEntryTable |
| GMTGD\_SD1 | GMTGD | 2 | RobotDictionaryEntryTable\_D4 |
| GMTGD\_SD2 | GMTGD | 2 | RobotDictionaryEntryTable\_D4 |
| GNTE | GNTE | 2 | RobotDictionaryEntryTable |
| GNTE2 | GNTE | 2 | RobotDictionaryEntryTable |
| GNTE3 | GNTE | 2 | RobotDictionaryEntryTable |
| GNTE\_C1 | GNTE | 2 | RobotDictionaryEntryTable |
| GNTE\_D | GNTE | 2 | RobotDictionaryEntryTable |
| GNTE\_D1 | GNTE | 2 | RobotDictionaryEntryTable\_D4 |
| GNTE\_D2 | GNTE | 2 | RobotDictionaryEntryTable\_D4 |
| GNTE\_S | GNTE | 2 | RobotDictionaryEntryTable |
| GODGD | GODGD | 2 | RobotDictionaryEntryTable |
| GODGD2 | GODGD | 2 | RobotDictionaryEntryTable |
| GODGD3 | GODGD | 2 | RobotDictionaryEntryTable |
| GODGD\_C | GODGD | 2 | RobotDictionaryEntryTable\_D3 |
| GODGD\_CH | GODGD | 2 | RobotDictionaryEntryTable\_D3 |
| GODGD\_H | GODGD | 2 | RobotDictionaryEntryTable |
| GODGD\_H2 | GODGD | 2 | RobotDictionaryEntryTable |
| GODGD\_H3 | GODGD | 2 | RobotDictionaryEntryTable |
| GRES | GRES | 4 | RobotDictionaryEntryTable |
| GRES2 | GRES | 4 | RobotDictionaryEntryTable |
| GRES\_D | GRES | 4 | RobotDictionaryEntryTable\_D4 |
| GRES\_FMH | GRES\_FMH | 2 | RobotDictionaryEntryTable |
| GRES\_FMH2 | GRES\_FMH | 2 | RobotDictionaryEntryTable |
| GRES\_FMH\_D | GRES\_FMH | 2 | RobotDictionaryEntryTable\_D4 |
| GRID\_KT | GRID\_KT | 2 | RobotDictionaryEntryTable |
| GRID\_KT2 | GRID\_KT | 2 | RobotDictionaryEntryTable |
| GRID\_KT3 | GRID\_KT | 2 | RobotDictionaryEntryTable |
| GRID\_KT\_D | GRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| GRID\_KT\_D2 | GRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| GRID\_KT\_D3 | GRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| GRNGLAN | GRNGLAN | 2 | RobotDictionaryEntryTable |
| GRNGLAN\_C | GRNGLAN | 2 | RobotDictionaryEntryTable\_D3 |
| GRNVNG | GRNVNG | 2 | RobotDictionaryEntryTable |
| GRNVNG2 | GRNVNG | 2 | RobotDictionaryEntryTable |
| GRON | GRON | 2 | RobotDictionaryEntryTable |
| GRON2 | GRON | 2 | RobotDictionaryEntryTable |
| GRON3 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_C2 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_C4 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_D1 | GRON | 2 | RobotDictionaryEntryTable\_D4 |
| GRON\_D2 | GRON | 2 | RobotDictionaryEntryTable\_D4 |
| GRON\_S1 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_S2 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_SD | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_SD1 | GRON | 2 | RobotDictionaryEntryTable\_D4 |
| GRON\_SD2 | GRON | 2 | RobotDictionaryEntryTable\_D4 |
| GRON\_S\_C2 | GRON | 2 | RobotDictionaryEntryTable |
| GRON\_S\_C4 | GRON | 2 | RobotDictionaryEntryTable |
| GRVLIN | GRVLIN | 2 | RobotDictionaryEntryTable |
| GRVLIN\_P | GRVLIN | 2 | RobotDictionaryEntryTable |
| GSR\_EW | GSR\_EW | 2 | RobotDictionaryEntryTable |
| GSR\_EW2 | GSR\_EW | 2 | RobotDictionaryEntryTable |
| GSR\_EW\_C | GSR\_EW | 2 | RobotDictionaryEntryTable\_D3 |
| GSR\_EW\_D | GSR\_EW | 2 | RobotDictionaryEntryTable\_D4 |
| GTENOIR1 | GTENOIR1 | 2 | RobotDictionaryEntryTable\_D2 |
| GTENOIRG | GTENOIRG | 2 | RobotDictionaryEntryTable\_D2 |
| GTENOIRG\_2 | GTENOIRG | 2 | RobotDictionaryEntryTable\_D2 |
| GTRARK | GTRARK | 2 | RobotDictionaryEntryTable |
| GTRARK2 | GTRARK | 2 | RobotDictionaryEntryTable |
| GTRARK\_0 | GTRARK | 2 | RobotDictionaryEntryTable |
| GTRARK\_D | GTRARK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRARK\_D2 | GTRARK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRARK\_D3 | GTRARK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRARK\_D4 | GTRARK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRARK\_D5 | GTRARK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRARK\_X | GTRARK | 2 | RobotDictionaryEntryTable |
| GTRHDGN | GTRHDGN | 2 | RobotDictionaryEntryTable |
| GTRHDGN\_C4 | GTRHDGN | 2 | RobotDictionaryEntryTable |
| GTRHDGN\_D | GTRHDGN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRHDGN\_DF | GTRHDGN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKARN | GTRKARN | 2 | RobotDictionaryEntryTable |
| GTRKARN2 | GTRKARN | 2 | RobotDictionaryEntryTable |
| GTRKARN\_D | GTRKARN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKARN\_D2 | GTRKARN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKARN\_D3 | GTRKARN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKARN\_D4 | GTRKARN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKARN\_D5 | GTRKARN | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKRIK | GTRKRIK | 2 | RobotDictionaryEntryTable |
| GTRKRIK2 | GTRKRIK | 2 | RobotDictionaryEntryTable |
| GTRKRIK\_D | GTRKRIK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKRIK\_D2 | GTRKRIK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKRIK\_D3 | GTRKRIK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKRIK\_D4 | GTRKRIK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRKRIK\_D5 | GTRKRIK | 2 | RobotDictionaryEntryTable\_D4 |
| GTRTRK | GTRTRK | 2 | RobotDictionaryEntryTable |
| GTRZURS | GTRZURS | 2 | RobotDictionaryEntryTable |
| GTRZURS\_C4 | GTRZURS | 2 | RobotDictionaryEntryTable |
| GTRZURS\_D | GTRZURS | 2 | RobotDictionaryEntryTable\_D4 |
| GTRZURS\_S | GTRZURS | 2 | RobotDictionaryEntryTable |
| GTRZURS\_S\_C4 | GTRZURS | 2 | RobotDictionaryEntryTable |
| GUNDNODE | GUNDNODE | 2 | RobotDictionaryEntryTable\_D4 |
| GUNDVOLVA | GUNDVOLVA | 2 | RobotDictionaryEntryTable\_D4 |
| GUNDVOLVA\_2 | GUNDVOLVA | 2 | RobotDictionaryEntryTable\_D4 |
| GUNDVOLVA\_3 | GUNDVOLVA | 2 | RobotDictionaryEntryTable\_D4 |
| GURENSE\_C | GURENSE | 2 | RobotDictionaryEntryTable\_D3 |
| GZC | GZC | 2 | RobotDictionaryEntryTable |
| GZC2 | GZC | 2 | RobotDictionaryEntryTable |
| GZC\_0 | GZC | 2 | RobotDictionaryEntryTable |
| GZLULTM | GZLULTM | 2 | RobotDictionaryEntryTable |
| GZLULTM\_D | GZLULTM | 2 | RobotDictionaryEntryTable |
| GZLULTM\_D1 | GZLULTM | 2 | RobotDictionaryEntryTable\_D4 |
| GZLULTM\_D2 | GZLULTM | 2 | RobotDictionaryEntryTable |
| GZLULTM\_P | GZLULTM | 2 | RobotDictionaryEntryTable\_D4 |
| HBRB | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB2 | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB\_C2 | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB\_C5 | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB\_D | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB\_D1 | HBRB | 2 | RobotDictionaryEntryTable\_D4 |
| HBRB\_D2 | HBRB | 2 | RobotDictionaryEntryTable\_D4 |
| HBRB\_P | HBRB | 2 | RobotDictionaryEntryTable |
| HBRB\_PC | HBRB | 2 | RobotDictionaryEntryTable\_D3 |
| HBRB\_PD | HBRB | 2 | RobotDictionaryEntryTable\_D4 |
| HNGD | HNGD | 2 | RobotDictionaryEntryTable\_D3 |
| HNGD\_P | HNGD | 2 | RobotDictionaryEntryTable\_D3 |
| HRDIAS | HRDIAS | 2 | RobotDictionaryEntryTable |
| HRDIAS\_C1 | HRDIAS | 2 | RobotDictionaryEntryTable |
| HRDIAS\_D | HRDIAS | 2 | RobotDictionaryEntryTable |
| HRDIAS\_HIMI | HRDIAS | 2 | RobotDictionaryEntryTable\_D2 |
| HRDIAS\_HIMI\_0 | HRDIAS | 2 | RobotDictionaryEntryTable\_D2 |
| HSTLK | HSTLK | 2 | RobotDictionaryEntryTable\_D3 |
| HSTLK\_M | HSTLK | 2 | RobotDictionaryEntryTable\_D3 |
| HSTLK\_S | HSTLK | 2 | RobotDictionaryEntryTable\_D3 |
| IBIT | IBIT | 2 | RobotDictionaryEntryTable\_D2 |
| IDEON | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_2 | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_2S | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_3 | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_3S | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_4 | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_4S | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_5 | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_5S | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_E | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IDEON\_S | IDEON | 2 | RobotDictionaryEntryTable\_D3 |
| IFAS | IFAS | 2 | RobotDictionaryEntryTable\_D2 |
| IGZIS | IGZIS | 2 | RobotDictionaryEntryTable\_D2 |
| IGZIS\_E1 | IGZIS | 2 | RobotDictionaryEntryTable\_D2 |
| IGZIS\_E2 | IGZIS | 2 | RobotDictionaryEntryTable\_D2 |
| IGZIS\_E3 | IGZIS | 2 | RobotDictionaryEntryTable\_D2 |
| INBEL | INBEL | 2 | RobotDictionaryEntryTable\_D3 |
| INBEL\_2 | INBEL | 2 | RobotDictionaryEntryTable\_D3 |
| INFGD | INFGD | 2 | RobotDictionaryEntryTable |
| INFGD2 | INFGD | 2 | RobotDictionaryEntryTable |
| INFGD\_C | INFGD | 2 | RobotDictionaryEntryTable\_D3 |
| INSCTR | INSCTR | 2 | RobotDictionaryEntryTable |
| INSCTR2 | INSCTR | 2 | RobotDictionaryEntryTable |
| INSCTR3 | INSCTR | 2 | RobotDictionaryEntryTable |
| INSCTR\_0 | INSCTR | 2 | RobotDictionaryEntryTable |
| INSCTR\_C1 | INSCTR | 2 | RobotDictionaryEntryTable |
| INSCTR\_S | INSCTR | 2 | RobotDictionaryEntryTable |
| ISTLJEEG | ISTLJEEG | 4 | RobotDictionaryEntryTable\_D2 |
| ISTLJEEG\_2 | ISTLJEEG | 4 | RobotDictionaryEntryTable\_D2 |
| ISTLJEEG\_3 | ISTLJEEG | 4 | RobotDictionaryEntryTable\_D2 |
| ISTLJEEG\_EV | ISTLJEEG | 4 | RobotDictionaryEntryTable\_D2 |
| IZNORT | IZNORT | 2 | RobotDictionaryEntryTable |
| IZNORT\_C5 | IZNORT | 2 | RobotDictionaryEntryTable |
| IZNORT\_D | IZNORT | 2 | RobotDictionaryEntryTable |
| IZNORT\_D1 | IZNORT | 2 | RobotDictionaryEntryTable\_D4 |
| JDJGR | JDJGR | 2 | RobotDictionaryEntryTable |
| JDJGR\_2 | JDJGR | 2 | RobotDictionaryEntryTable |
| JDJGR\_3 | JDJGR | 2 | RobotDictionaryEntryTable |
| JDJGR\_D | JDJGR | 2 | RobotDictionaryEntryTable\_D4 |
| JDJGR\_D2 | JDJGR | 2 | RobotDictionaryEntryTable\_D4 |
| JDJGR\_D3 | JDJGR | 2 | RobotDictionaryEntryTable\_D4 |
| JDOGA\_G | JDOGA\_G | 2 | RobotDictionaryEntryTable |
| JDOGA\_GE | JDOGA\_G | 2 | RobotDictionaryEntryTable\_D3 |
| JDOGA\_GP | JDOGA\_G | 2 | RobotDictionaryEntryTable |
| JDOGA\_Q | JDOGA\_Q | 2 | RobotDictionaryEntryTable |
| JDOGA\_QE | JDOGA\_Q | 2 | RobotDictionaryEntryTable\_D3 |
| JDOGA\_QP | JDOGA\_Q | 2 | RobotDictionaryEntryTable |
| JEG | JEG | 2 | RobotDictionaryEntryTable |
| JEG\_E | JEG | 2 | RobotDictionaryEntryTable |
| JIGMACK | JIGMACK | 2 | RobotDictionaryEntryTable\_D3 |
| JIGMACK\_0 | JIGMACK | 2 | RobotDictionaryEntryTable\_D3 |
| JIGMACK\_2 | JIGMACK | 2 | RobotDictionaryEntryTable\_D3 |
| JIGMACK\_3 | JIGMACK | 2 | RobotDictionaryEntryTable\_D3 |
| KMNGA | KMNGA | 2 | RobotDictionaryEntryTable |
| KMNGA2 | KMNGA | 2 | RobotDictionaryEntryTable |
| KMNGA3 | KMNGA | 2 | RobotDictionaryEntryTable |
| KMNGA\_D | KMNGA | 2 | RobotDictionaryEntryTable\_D4 |
| KMNGA\_LA | KMNGA | 2 | RobotDictionaryEntryTable |
| KRDWCAXEL | KRDWCAXEL | 2 | RobotDictionaryEntryTable\_D1 |
| KRDWCJ | KRDWCJ | 2 | RobotDictionaryEntryTable\_D1 |
| KRDWCJ\_2 | KRDWCJ | 2 | RobotDictionaryEntryTable\_D1 |
| KRDWSCULL | KRDWSCULL | 2 | RobotDictionaryEntryTable\_D1 |
| KRDWSCULL\_2 | KRDWSCULL | 2 | RobotDictionaryEntryTable\_D1 |
| KZLGRID\_KT | KZLGRID\_KT | 2 | RobotDictionaryEntryTable |
| KZLGRID\_KT2 | KZLGRID\_KT | 2 | RobotDictionaryEntryTable |
| KZLGRID\_KT3 | KZLGRID\_KT | 2 | RobotDictionaryEntryTable |
| KZLGRID\_KT\_D | KZLGRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| KZLGRID\_KT\_D2 | KZLGRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| KZLGRID\_KT\_D3 | KZLGRID\_KT | 2 | RobotDictionaryEntryTable\_D4 |
| LADON | LADON | 2 | RobotDictionaryEntryTable |
| LADON2 | LADON | 2 | RobotDictionaryEntryTable |
| LADON3 | LADON | 2 | RobotDictionaryEntryTable |
| LADON\_0 | LADON | 2 | RobotDictionaryEntryTable |
| LADON\_D | LADON | 2 | RobotDictionaryEntryTable\_D4 |
| LADON\_LA | LADON | 2 | RobotDictionaryEntryTable |
| LFRITH\_TH | LFRITH\_TH | 2 | RobotDictionaryEntryTable\_D4 |
| LFRITH\_TH\_2 | LFRITH\_TH | 2 | RobotDictionaryEntryTable\_D4 |
| LFRITH\_TH\_3 | LFRITH\_TH | 2 | RobotDictionaryEntryTable\_D4 |
| LFRITH\_UR | LFRITH\_UR | 2 | RobotDictionaryEntryTable\_D4 |
| LFRITH\_UR2 | LFRITH\_UR | 2 | RobotDictionaryEntryTable\_D4 |
| LGIM | LGIM | 4 | RobotDictionaryEntryTable |
| LGIM2 | LGIM | 4 | RobotDictionaryEntryTable |
| LGIM\_MK2 | LGIM\_MK2 | 2 | RobotDictionaryEntryTable |
| LGIM\_MK2\_D | LGIM\_MK2 | 2 | RobotDictionaryEntryTable\_D4 |
| LKAI | LKAI | 2 | RobotDictionaryEntryTable |
| LKAI\_2 | LKAI | 2 | RobotDictionaryEntryTable\_D3 |
| LKAI\_C | LKAI | 2 | RobotDictionaryEntryTable\_D3 |
| LYNS | LYNS | 2 | RobotDictionaryEntryTable |
| MADIVIA | MADIVIA | 2 | RobotDictionaryEntryTable\_D4 |
| MADIVIA\_2 | MADIVIA | 2 | RobotDictionaryEntryTable\_D4 |
| MAGDA\_2 | MAGDA | 2 | RobotDictionaryEntryTable\_D4 |
| MAGDA\_M | MAGDA | 2 | RobotDictionaryEntryTable\_D4 |
| MAGDA\_Y | MAGDA | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINENG | MAZINENG | 2 | RobotDictionaryEntryTable |
| MAZINENG2 | MAZINENG | 2 | RobotDictionaryEntryTable |
| MAZINENG3 | MAZINENG | 2 | RobotDictionaryEntryTable |
| MAZINENG3S | MAZINENG | 2 | RobotDictionaryEntryTable |
| MAZINENG\_D | MAZINENG | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINENG\_D2 | MAZINENG | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINENG\_D3 | MAZINENG | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINENG\_D4 | MAZINENG | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINENG\_D5 | MAZINENG | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINKZR | MAZINKZR | 2 | RobotDictionaryEntryTable |
| MAZINKZR2 | MAZINKZR | 2 | RobotDictionaryEntryTable |
| MAZINKZR3 | MAZINKZR | 2 | RobotDictionaryEntryTable |
| MAZINKZR3S | MAZINKZR | 2 | RobotDictionaryEntryTable |
| MAZINKZR\_C | MAZINKZR | 2 | RobotDictionaryEntryTable\_D3 |
| MAZINKZR\_D | MAZINKZR | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINKZR\_D2 | MAZINKZR | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINKZR\_D3 | MAZINKZR | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINKZR\_D4 | MAZINKZR | 2 | RobotDictionaryEntryTable\_D4 |
| MAZINKZR\_D5 | MAZINKZR | 2 | RobotDictionaryEntryTable\_D4 |
| MCAELS | MCAELS | 2 | RobotDictionaryEntryTable |
| MCLIN | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN2 | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN3 | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN\_C1 | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN\_C3 | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN\_C5 | MCLIN | 2 | RobotDictionaryEntryTable |
| MCLIN\_D2 | MCLIN | 2 | RobotDictionaryEntryTable\_D4 |
| MCRS\_ERSON | MCRS\_ERSON | 2 | RobotDictionaryEntryTable |
| MCRS\_GRSON | MCRS\_GRSON | 2 | RobotDictionaryEntryTable |
| MCRS\_GRSON\_C5 | MCRS\_GRSON | 2 | RobotDictionaryEntryTable |
| MCRS\_MGSON | MCRS\_MGSON | 2 | RobotDictionaryEntryTable |
| MCRS\_MGSON\_C5 | MCRS\_MGSON | 2 | RobotDictionaryEntryTable |
| MDLGN | MDLGN | 2 | RobotDictionaryEntryTable |
| MDLGN\_C5 | MDLGN | 2 | RobotDictionaryEntryTable |
| MDLGN\_D | MDLGN | 2 | RobotDictionaryEntryTable |
| MDLGN\_D2 | MDLGN | 2 | RobotDictionaryEntryTable\_D4 |
| MET | MET | 2 | RobotDictionaryEntryTable |
| MET\_C | MET | 2 | RobotDictionaryEntryTable\_D3 |
| MFCARDNT | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT2 | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT3 | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT\_0 | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT\_EV | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT\_NH | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MFCARDNT\_W | MFCARDNT | 2 | RobotDictionaryEntryTable |
| MIDORO | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MIDORO\_C5A | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MIDORO\_C5B | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MIDORO\_D | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MIDORO\_D1 | FTBNFROBO | 2 | RobotDictionaryEntryTable\_D4 |
| MIDORO\_D2 | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MIDORO\_D2\_EXP | FTBNFROBO | 2 | RobotDictionaryEntryTable\_D4 |
| MIDORO\_M | FTBNFROBO | 2 | RobotDictionaryEntryTable |
| MLTEL | MLTEL | 2 | RobotDictionaryEntryTable |
| MLTEL\_C1 | MLTEL | 2 | RobotDictionaryEntryTable |
| MLTEL\_C5 | MLTEL | 2 | RobotDictionaryEntryTable |
| MLTEL\_D | MLTEL | 2 | RobotDictionaryEntryTable |
| MLTEL\_D2 | MLTEL | 2 | RobotDictionaryEntryTable\_D4 |
| MNGD\_F | MNGD\_F | 2 | RobotDictionaryEntryTable |
| MNGD\_I | MNGD\_I | 2 | RobotDictionaryEntryTable |
| MSKA | MSKA | 2 | RobotDictionaryEntryTable |
| MSKA\_C | MSKA | 2 | RobotDictionaryEntryTable\_D3 |
| MSTGD | MSTGD | 2 | RobotDictionaryEntryTable |
| MSTGD\_E | MSTGD | 2 | RobotDictionaryEntryTable |
| MZIAT | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIAT2 | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIAT3 | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIAT\_C1 | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIAT\_C5 | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIAT\_D | MZIAT | 2 | RobotDictionaryEntryTable |
| MZIA\_D2 | MZIAT | 2 | RobotDictionaryEntryTable\_D4 |
| NBGD | NBGD | 2 | RobotDictionaryEntryTable |
| NBGD2 | NBGD | 2 | RobotDictionaryEntryTable |
| NCNGL | NCNGL | 2 | RobotDictionaryEntryTable\_D3 |
| NDSD | NDSD | 2 | RobotDictionaryEntryTable |
| NDSD2 | NDSD | 2 | RobotDictionaryEntryTable |
| NGD | NGD | 2 | RobotDictionaryEntryTable |
| NGD\_C | NGD | 2 | RobotDictionaryEntryTable\_D3 |
| NGD\_CP | NGD | 2 | RobotDictionaryEntryTable\_D3 |
| NGD\_P | NGD | 2 | RobotDictionaryEntryTable |
| NGSM | NGSM | 2 | RobotDictionaryEntryTable |
| NGSM2 | NGSM | 2 | RobotDictionaryEntryTable |
| NGSM\_C2 | NGSM | 2 | RobotDictionaryEntryTable |
| NLVASHUZ | NLVASHUZ | 2 | RobotDictionaryEntryTable\_D3 |
| ORCDN | ORCDN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCDN\_2 | ORCDN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCDN\_3 | ORCDN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCIN | ORCIN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCIN\_2 | ORCIN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCIN\_3 | ORCIN | 2 | RobotDictionaryEntryTable\_D3 |
| ORCUS\_BA | ORCUS\_BA | 2 | RobotDictionaryEntryTable\_D4 |
| ORCUS\_BA\_2 | ORCUS\_BA | 2 | RobotDictionaryEntryTable\_D4 |
| ORCZNG\_2 | ORCZNG | 2 | RobotDictionaryEntryTable\_D3 |
| ORCZNG\_3 | ORCZNG | 2 | RobotDictionaryEntryTable\_D3 |
| PLOID\_2 | PLOID | 2 | RobotDictionaryEntryTable\_D3 |
| PLOID\_3 | PLOID | 2 | RobotDictionaryEntryTable\_D3 |
| PUR2 | PUR2 | 2 | RobotDictionaryEntryTable |
| PUR2\_2 | PUR2 | 2 | RobotDictionaryEntryTable |
| PUR2\_3 | PUR2 | 2 | RobotDictionaryEntryTable |
| PUR2\_4 | PUR2 | 2 | RobotDictionaryEntryTable |
| PUR2\_D | PUR2 | 2 | RobotDictionaryEntryTable\_D4 |
| PUR2\_D2 | PUR2 | 2 | RobotDictionaryEntryTable\_D4 |
| RAGMADOC | RAGMADOC | 2 | RobotDictionaryEntryTable\_D4 |
| RAGMADOC\_S | RAGMADOC | 2 | RobotDictionaryEntryTable\_D4 |
| RANSAR | RANSAR | 2 | RobotDictionaryEntryTable\_D3 |
| RANSR | RANSR | 2 | RobotDictionaryEntryTable\_D3 |
| RDDOPNT | RDDOPNT | 2 | RobotDictionaryEntryTable\_D1 |
| RDDOPNT\_2 | RDDOPNT | 2 | RobotDictionaryEntryTable\_D1 |
| RDDOPNT\_3 | RDDOPNT | 2 | RobotDictionaryEntryTable\_D1 |
| RED5 | RED5 | 2 | RobotDictionaryEntryTable |
| RED5\_0 | RED5 | 2 | RobotDictionaryEntryTable |
| RED5\_2 | RED5 | 2 | RobotDictionaryEntryTable |
| RED5\_3 | RED5 | 2 | RobotDictionaryEntryTable |
| RED5\_4 | RED5 | 2 | RobotDictionaryEntryTable |
| RED5\_D | RED5 | 2 | RobotDictionaryEntryTable\_D4 |
| RED5\_D2 | RED5 | 2 | RobotDictionaryEntryTable\_D4 |
| REDGIST | REDGIST | 2 | RobotDictionaryEntryTable\_D2 |
| REDGIST\_D | REDGIST | 2 | RobotDictionaryEntryTable\_D2 |
| REGZ | REGZ | 4 | RobotDictionaryEntryTable |
| REGZ\_BWS | REGZ\_BWS | 2 | RobotDictionaryEntryTable |
| REUL | REUL | 2 | RobotDictionaryEntryTable |
| REUL\_C | REUL | 2 | RobotDictionaryEntryTable\_D3 |
| RE\_BLASTA | RE\_BLASTA | 2 | RobotDictionaryEntryTable\_D4 |
| RE\_BLASTA\_2 | RE\_BLASTA | 2 | RobotDictionaryEntryTable\_D4 |
| RIDEEN | RIDEEN | 2 | RobotDictionaryEntryTable |
| RIDEEN2 | RIDEEN | 2 | RobotDictionaryEntryTable |
| RIDEEN3 | RIDEEN | 2 | RobotDictionaryEntryTable |
| RIDEEN3M | RIDEEN | 2 | RobotDictionaryEntryTable |
| RIDEEN\_C | RIDEEN | 2 | RobotDictionaryEntryTable\_D3 |
| RIDEEN\_D | RIDEEN | 2 | RobotDictionaryEntryTable\_D4 |
| RIDEEN\_DM | RIDEEN | 2 | RobotDictionaryEntryTable\_D4 |
| RNDRAH | RNDRAH | 6 | RobotDictionaryEntryTable |
| RNDRAH2 | RNDRAH2 | 2 | RobotDictionaryEntryTable |
| RNDRAH2\_0 | RNDRAH2 | 2 | RobotDictionaryEntryTable |
| RNDRAH2\_2 | RNDRAH2 | 2 | RobotDictionaryEntryTable |
| RNDRAH2\_SUB | RNDRAH2 | 2 | RobotDictionaryEntryTable |
| RNDRAH\_0 | RNDRAH | 6 | RobotDictionaryEntryTable |
| RNDRAH\_2 | RNDRAH | 6 | RobotDictionaryEntryTable |
| RNDRAH\_BRM | RNDRAH\_BRM | 2 | RobotDictionaryEntryTable |
| RNDRAH\_BRM2 | RNDRAH\_BRM | 2 | RobotDictionaryEntryTable |
| RNDRAH\_BRM3 | RNDRAH\_BRM | 2 | RobotDictionaryEntryTable |
| RNDRAH\_BRM\_EV | RNDRAH\_BRM | 2 | RobotDictionaryEntryTable |
| RNDRAH\_E | RNDRAH | 6 | RobotDictionaryEntryTable |
| RNDRAH\_NCT | RNDRAH\_NCT | 2 | RobotDictionaryEntryTable |
| RNDRAH\_NCT2 | RNDRAH\_NCT | 2 | RobotDictionaryEntryTable |
| RNDRAH\_NCT3 | RNDRAH\_NCT | 2 | RobotDictionaryEntryTable |
| RNDRAH\_NCT\_EV | RNDRAH\_NCT | 2 | RobotDictionaryEntryTable |
| RNDRAH\_SUB | RNDRAH | 6 | RobotDictionaryEntryTable |
| RNGLM | RNGLM | 2 | RobotDictionaryEntryTable\_D1 |
| RNGLM\_2 | RNGLM | 2 | RobotDictionaryEntryTable\_D1 |
| RNGLM\_3 | RNGLM | 2 | RobotDictionaryEntryTable\_D1 |
| RNGLM\_4 | RNGLM | 2 | RobotDictionaryEntryTable\_D1 |
| ROS3 | ROS3 | 2 | RobotDictionaryEntryTable |
| ROS3\_2 | ROS3 | 2 | RobotDictionaryEntryTable |
| ROS3\_3 | ROS3 | 2 | RobotDictionaryEntryTable |
| ROS3\_4 | ROS3 | 2 | RobotDictionaryEntryTable |
| ROS3\_D | ROS3 | 2 | RobotDictionaryEntryTable\_D4 |
| ROS3\_D2 | ROS3 | 2 | RobotDictionaryEntryTable\_D4 |
| RPRKN | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN2 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN3 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_C2 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_C4 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_D1 | RPRKN | 2 | RobotDictionaryEntryTable\_D4 |
| RPRKN\_S1 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_S2 | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_SD | RPRKN | 2 | RobotDictionaryEntryTable |
| RPRKN\_SD1 | RPRKN | 2 | RobotDictionaryEntryTable\_D4 |
| RPRKN\_SD2 | RPRKN | 2 | RobotDictionaryEntryTable\_D4 |
| RRAZ | RRAZ | 2 | RobotDictionaryEntryTable |
| RRAZ\_G | RRAZ | 2 | RobotDictionaryEntryTable |
| RRSN | RRSN | 4 | RobotDictionaryEntryTable |
| RRSN2 | RRSN | 4 | RobotDictionaryEntryTable |
| RRSN\_D | RRSN | 4 | RobotDictionaryEntryTable\_D4 |
| RRSN\_WFG | RRSN\_WFG | 2 | RobotDictionaryEntryTable |
| RRSN\_WFG2 | RRSN\_WFG | 2 | RobotDictionaryEntryTable |
| RRSN\_WFG\_D | RRSN\_WFG | 2 | RobotDictionaryEntryTable\_D4 |
| RSGGD | RSGGD | 2 | RobotDictionaryEntryTable |
| RSGGD2 | RSGGD | 2 | RobotDictionaryEntryTable |
| RSGGD3 | RSGGD | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1 | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_1A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_1B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_1C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_2 | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_2A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_2B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_2C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_3 | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_3A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_3B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_3C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_5B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_6C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_7A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_7B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_7C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_8A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_8C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_9A | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C1\_DL1C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable\_D1 |
| RUMINA\_C1\_DL2B | RUMINA\_C1 | 2 | RobotDictionaryEntryTable\_D2 |
| RUMINA\_C1\_DL2C | RUMINA\_C1 | 2 | RobotDictionaryEntryTable\_D2 |
| RUMINA\_C1\_P | RUMINA\_C1 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2 | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_1A | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_1B | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_2 | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_2A | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_2B | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_5C | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_6B | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_7A | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_7C | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_DL1B | RUMINA\_C2 | 2 | RobotDictionaryEntryTable\_D1 |
| RUMINA\_C2\_P | RUMINA\_C2 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C2\_W | RUMINA\_C2 | 2 | RobotDictionaryEntryTable\_D2 |
| RUMINA\_C3 | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3LV | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3S | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_10A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_1C | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_2 | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_2C | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_3 | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_4A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_4B | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_4C | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_5A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_6A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_D | RUMINA\_C3 | 2 | RobotDictionaryEntryTable\_D4 |
| RUMINA\_C3\_DL1A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable\_D1 |
| RUMINA\_C3\_DL2A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable\_D2 |
| RUMINA\_C3\_DL3A | RUMINA\_C3 | 2 | RobotDictionaryEntryTable\_D3 |
| RUMINA\_C3\_M | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_P | RUMINA\_C3 | 2 | RobotDictionaryEntryTable |
| RUMINA\_C3\_W | RUMINA\_C3 | 2 | RobotDictionaryEntryTable\_D3 |
| RYAB | RYAB | 2 | RobotDictionaryEntryTable\_D3 |
| RYAB\_2 | RYAB | 2 | RobotDictionaryEntryTable\_D3 |
| RYAB\_3 | RYAB | 2 | RobotDictionaryEntryTable\_D3 |
| SAZA | SAZA | 2 | RobotDictionaryEntryTable |
| SAZA\_E | SAZA | 2 | RobotDictionaryEntryTable\_D3 |
| SCHWARZ | SCHWARZ | 2 | RobotDictionaryEntryTable\_D4 |
| SFRGD | SFRGD | 2 | RobotDictionaryEntryTable |
| SFRGD2 | SFRGD | 2 | RobotDictionaryEntryTable |
| SFRGD\_C | SFRGD | 2 | RobotDictionaryEntryTable\_D3 |
| SGLBRNS | SGLBRNS | 2 | RobotDictionaryEntryTable |
| SGLBRNS\_C5 | SGLBRNS | 2 | RobotDictionaryEntryTable |
| SGLBRNS\_D2 | SGLBRNS | 2 | RobotDictionaryEntryTable\_D4 |
| SHINK | SHINK | 2 | RobotDictionaryEntryTable\_D3 |
| SLBNDS | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS2 | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_0 | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_C1 | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_C2 | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_D | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_D1 | SLBNDS | 2 | RobotDictionaryEntryTable\_D4 |
| SLBNDS\_S | SLBNDS | 2 | RobotDictionaryEntryTable |
| SLBNDS\_S2 | SLBNDS | 2 | RobotDictionaryEntryTable |
| SPNT | SPNT | 2 | RobotDictionaryEntryTable |
| SPNT2 | SPNT | 2 | RobotDictionaryEntryTable |
| SPNT3 | SPNT | 2 | RobotDictionaryEntryTable |
| SPNT\_C3 | SPNT | 2 | RobotDictionaryEntryTable |
| SPNT\_D1 | SPNT | 2 | RobotDictionaryEntryTable\_D4 |
| SPNT\_D2 | SPNT | 2 | RobotDictionaryEntryTable\_D4 |
| SPNT\_S | SPNT | 2 | RobotDictionaryEntryTable |
| SRBIN | SRBIN | 2 | RobotDictionaryEntryTable |
| STAMEN\_BI | STAMEN\_BI | 2 | RobotDictionaryEntryTable\_D4 |
| STAMEN\_BI\_2 | STAMEN\_BI | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_BLS | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS2 | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS3 | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS\_C3 | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS\_C4 | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS\_C5 | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS\_D1 | STERA\_BLS | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_BLS\_D2 | STERA\_BLS | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_BLS\_P | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_BLS\_PD | STERA\_BLS | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_BLS\_S | STERA\_BLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS2 | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS2\_C | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D3 |
| STERA\_FLS3 | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS\_C | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D3 |
| STERA\_FLS\_C3 | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS\_C5 | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS\_D1 | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_FLS\_D2 | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_FLS\_DL3C | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D3 |
| STERA\_FLS\_DL3F | STERA\_FLS | 2 | RobotDictionaryEntryTable\_D3 |
| STERA\_FLS\_G | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_FLS\_M | STERA\_FLS | 2 | RobotDictionaryEntryTable |
| STERA\_KKN | STERA\_KKN | 2 | RobotDictionaryEntryTable |
| STERA\_KKN\_B | STERA\_KKN | 2 | RobotDictionaryEntryTable |
| STERA\_KKN\_C5 | STERA\_KKN | 2 | RobotDictionaryEntryTable |
| STERA\_KKN\_D1 | STERA\_KKN | 2 | RobotDictionaryEntryTable\_D4 |
| STERA\_VRS | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS2 | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS3 | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS\_C2 | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS\_G | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS\_P | STERA\_VRS | 2 | RobotDictionaryEntryTable |
| STERA\_VRS\_PC | STERA\_VRS | 2 | RobotDictionaryEntryTable\_D3 |
| SUGEO | SUGEO | 4 | RobotDictionaryEntryTable |
| SUGEO2 | SUGEO | 4 | RobotDictionaryEntryTable |
| SUGEO\_C4 | SUGEO | 4 | RobotDictionaryEntryTable |
| SUGEO\_M | SUGEO\_M | 2 | RobotDictionaryEntryTable |
| SUGEO\_M2 | SUGEO\_M | 2 | RobotDictionaryEntryTable |
| SUGEO\_M3 | SUGEO\_M | 2 | RobotDictionaryEntryTable |
| SUGEO\_MD1 | SUGEO\_M | 2 | RobotDictionaryEntryTable\_D4 |
| SUGEO\_M\_C3 | SUGEO\_M | 2 | RobotDictionaryEntryTable |
| SV262BDKN | SV262BDKN | 14 | RobotDictionaryEntryTable |
| SV262BDKN2 | SV262BDKN | 14 | RobotDictionaryEntryTable |
| SV262BDKN3 | SV262BDKN | 14 | RobotDictionaryEntryTable |
| SV262BDKN\_B | SV262BDKN\_B | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_B2 | SV262BDKN\_B | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_BD | SV262BDKN\_B | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_BD2 | SV262BDKN\_B | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_B\_C1 | SV262BDKN\_B | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_B\_C4 | SV262BDKN\_B | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_C2 | SV262BDKN | 14 | RobotDictionaryEntryTable |
| SV262BDKN\_D2 | SV262BDKN | 14 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_H | SV262BDKN\_H | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_H2 | SV262BDKN\_H | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_HD | SV262BDKN\_H | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_HD2 | SV262BDKN\_H | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_H\_C2 | SV262BDKN\_H | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_H\_C4 | SV262BDKN\_H | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_K | SV262BDKN\_K | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_K2 | SV262BDKN\_K | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_KD | SV262BDKN\_K | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_KD2 | SV262BDKN\_K | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_K\_C2 | SV262BDKN\_K | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_K\_C4 | SV262BDKN\_K | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_T | SV262BDKN\_T | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_T2 | SV262BDKN\_T | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_TD | SV262BDKN\_T | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_TD2 | SV262BDKN\_T | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_T\_C1 | SV262BDKN\_T | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_T\_C4 | SV262BDKN\_T | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_W | SV262BDKN\_W | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_WD2 | SV262BDKN\_W | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_Z | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_Z2 | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_ZD | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_ZD2 | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable\_D4 |
| SV262BDKN\_Z\_C1 | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable |
| SV262BDKN\_Z\_C4 | SV262BDKN\_Z | 2 | RobotDictionaryEntryTable |
| SV262HDKN | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN2 | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN\_C2 | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN\_C4 | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN\_D | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN\_D2 | SV262HDKN | 4 | RobotDictionaryEntryTable\_D4 |
| SV262HDKN\_P | SV262HDKN | 4 | RobotDictionaryEntryTable |
| SV262HDKN\_PC | SV262HDKN | 4 | RobotDictionaryEntryTable\_D3 |
| SV262HDKN\_R | SV262HDKN\_R | 2 | RobotDictionaryEntryTable |
| SV262HDKN\_RD2 | SV262HDKN\_R | 2 | RobotDictionaryEntryTable\_D4 |
| SZRNDZK | SZRNDZK | 2 | RobotDictionaryEntryTable\_D3 |
| TENKU | TENKU | 2 | RobotDictionaryEntryTable |
| TENKU2 | TENKU | 2 | RobotDictionaryEntryTable |
| TENKU\_C1 | TENKU | 2 | RobotDictionaryEntryTable |
| TENKU\_C4 | TENKU | 2 | RobotDictionaryEntryTable |
| TENKU\_D | TENKU | 2 | RobotDictionaryEntryTable |
| TENKU\_D1 | TENKU | 2 | RobotDictionaryEntryTable\_D4 |
| TENKU\_D2 | TENKU | 2 | RobotDictionaryEntryTable\_D4 |
| TG3 | TG3 | 2 | RobotDictionaryEntryTable |
| TIAMAT | TIAMAT | 2 | RobotDictionaryEntryTable\_D4 |
| TIAMAT\_2 | TIAMAT | 2 | RobotDictionaryEntryTable\_D4 |
| TRNEDREX\_F | TRNEDREX | 2 | RobotDictionaryEntryTable |
| TRNEDREX\_F2 | TRNEDREX | 2 | RobotDictionaryEntryTable |
| TRNEDREX\_M | TRNEDREX | 2 | RobotDictionaryEntryTable |
| TRNEDREX\_M2 | TRNEDREX | 2 | RobotDictionaryEntryTable |
| TRNED\_F | TRNED | 2 | RobotDictionaryEntryTable |
| TRNED\_F2 | TRNED | 2 | RobotDictionaryEntryTable |
| TRNED\_M | TRNED | 2 | RobotDictionaryEntryTable |
| TRNED\_M2 | TRNED | 2 | RobotDictionaryEntryTable |
| TRS\_B | TRS\_B | 2 | RobotDictionaryEntryTable |
| TRS\_B0 | TRS\_B | 2 | RobotDictionaryEntryTable |
| TRS\_B2 | TRS\_B | 2 | RobotDictionaryEntryTable |
| TRS\_W | TRS\_W | 2 | RobotDictionaryEntryTable |
| TUBRNCMPT | TUBRNCMPT | 2 | RobotDictionaryEntryTable\_D3 |
| TUBRNCMPT\_2 | TUBRNCMPT | 2 | RobotDictionaryEntryTable\_D3 |
| UAM\_CLIN | UAM\_CLIN | 2 | RobotDictionaryEntryTable |
| UAM\_CLIN2 | UAM\_CLIN | 2 | RobotDictionaryEntryTable |
| UAM\_CLIN\_D2 | UAM\_CLIN | 2 | RobotDictionaryEntryTable\_D4 |
| UAM\_DLGN | UAM\_DLGN | 2 | RobotDictionaryEntryTable |
| UAM\_DLGN3 | UAM\_DLGN | 2 | RobotDictionaryEntryTable |
| UAM\_DLGN\_D2 | UAM\_DLGN | 2 | RobotDictionaryEntryTable\_D4 |
| UAM\_LTEL | UAM\_LTEL | 2 | RobotDictionaryEntryTable |
| UAM\_LTEL3 | UAM\_LTEL | 2 | RobotDictionaryEntryTable |
| UAM\_LTEL\_D2 | UAM\_LTEL | 2 | RobotDictionaryEntryTable\_D4 |
| UAM\_RADA | UAM\_RADA | 2 | RobotDictionaryEntryTable |
| UAM\_RADA3 | UAM\_RADA | 2 | RobotDictionaryEntryTable |
| UAM\_RADA\_D2 | UAM\_RADA | 2 | RobotDictionaryEntryTable\_D4 |
| UAM\_RMES | UAM\_RMES | 2 | RobotDictionaryEntryTable |
| UAM\_RMES2 | UAM\_RMES | 2 | RobotDictionaryEntryTable |
| UAM\_RMES3 | UAM\_RMES | 2 | RobotDictionaryEntryTable |
| UAM\_RMES\_D2 | UAM\_RMES | 2 | RobotDictionaryEntryTable\_D4 |
| UAM\_ZIAT | UAM\_ZIAT | 2 | RobotDictionaryEntryTable |
| UAM\_ZIAT3 | UAM\_ZIAT | 2 | RobotDictionaryEntryTable |
| UAM\_ZIAT\_D2 | UAM\_ZIAT | 2 | RobotDictionaryEntryTable\_D4 |
| UBF\_CLIN | UBF\_CLIN | 2 | RobotDictionaryEntryTable |
| UBF\_DLGN | UBF\_DLGN | 2 | RobotDictionaryEntryTable |
| UBF\_LTEL | UBF\_LTEL | 2 | RobotDictionaryEntryTable |
| UBF\_LTEL2 | UBF\_LTEL | 2 | RobotDictionaryEntryTable |
| UBF\_LTEL3 | UBF\_LTEL | 2 | RobotDictionaryEntryTable |
| UBF\_RADA | UBF\_RADA | 2 | RobotDictionaryEntryTable |
| UBF\_RADA2 | UBF\_RADA | 2 | RobotDictionaryEntryTable |
| UBF\_RADA3 | UBF\_RADA | 2 | RobotDictionaryEntryTable |
| UBF\_RMES | UBF\_RMES | 2 | RobotDictionaryEntryTable |
| UBF\_RMES2 | UBF\_RMES | 2 | RobotDictionaryEntryTable |
| UBF\_RMES3 | UBF\_RMES | 2 | RobotDictionaryEntryTable |
| UBF\_ZIAT | UBF\_ZIAT | 2 | RobotDictionaryEntryTable |
| UBF\_ZIAT2 | UBF\_ZIAT | 2 | RobotDictionaryEntryTable |
| UBS\_CLIN | UBS\_CLIN | 2 | RobotDictionaryEntryTable |
| UBS\_CLIN\_C3 | UBS\_CLIN | 2 | RobotDictionaryEntryTable |
| UBS\_CLIN\_D2 | UBS\_CLIN | 2 | RobotDictionaryEntryTable\_D4 |
| UBS\_DLGN | UBS\_DLGN | 2 | RobotDictionaryEntryTable |
| UBS\_DLGN\_D | UBS\_DLGN | 2 | RobotDictionaryEntryTable |
| UBS\_DLGN\_D2 | UBS\_DLGN | 2 | RobotDictionaryEntryTable\_D4 |
| UBS\_LTEL | UBS\_LTEL | 2 | RobotDictionaryEntryTable |
| UBS\_LTEL\_D | UBS\_LTEL | 2 | RobotDictionaryEntryTable |
| UBS\_LTEL\_D2 | UBS\_LTEL | 2 | RobotDictionaryEntryTable\_D4 |
| UBS\_RADA | UBS\_RADA | 2 | RobotDictionaryEntryTable |
| UBS\_RADA2 | UBS\_RADA | 2 | RobotDictionaryEntryTable |
| UBS\_RADA\_C1 | UBS\_RADA | 2 | RobotDictionaryEntryTable |
| UBS\_RADA\_C5 | UBS\_RADA | 2 | RobotDictionaryEntryTable |
| UBS\_RADA\_D | UBS\_RADA | 2 | RobotDictionaryEntryTable |
| UBS\_RADA\_D2 | UBS\_RADA | 2 | RobotDictionaryEntryTable\_D4 |
| UBS\_RMES | UBS\_RMES | 2 | RobotDictionaryEntryTable |
| UBS\_RMES\_C5 | UBS\_RMES | 2 | RobotDictionaryEntryTable |
| UBS\_RMES\_D | UBS\_RMES | 2 | RobotDictionaryEntryTable |
| UBS\_RMES\_D2 | UBS\_RMES | 2 | RobotDictionaryEntryTable\_D4 |
| UBS\_ZIAT | UBS\_ZIAT | 2 | RobotDictionaryEntryTable |
| UBS\_ZIAT\_D2 | UBS\_ZIAT | 2 | RobotDictionaryEntryTable\_D4 |
| UGRD | UGRD | 2 | RobotDictionaryEntryTable |
| UGRD2 | UGRD | 2 | RobotDictionaryEntryTable |
| UGRD3 | UGRD | 2 | RobotDictionaryEntryTable |
| UGRD\_D1 | UGRD | 2 | RobotDictionaryEntryTable\_D4 |
| UGRD\_D2 | UGRD | 2 | RobotDictionaryEntryTable\_D4 |
| ULSKGNA | ULSKGNA | 2 | RobotDictionaryEntryTable\_D3 |
| UMM\_CLIN | UMM\_CLIN | 2 | RobotDictionaryEntryTable |
| UMM\_CLIN\_C3 | UMM\_CLIN | 2 | RobotDictionaryEntryTable |
| UMM\_CLIN\_D2 | UMM\_CLIN | 2 | RobotDictionaryEntryTable\_D4 |
| UMM\_DLGN | UMM\_DLGN | 2 | RobotDictionaryEntryTable |
| UMM\_DLGN3 | UMM\_DLGN | 2 | RobotDictionaryEntryTable |
| UMM\_DLGN\_D2 | UMM\_DLGN | 2 | RobotDictionaryEntryTable\_D4 |
| UMM\_LTEL | UMM\_LTEL | 2 | RobotDictionaryEntryTable |
| UMM\_LTEL2 | UMM\_LTEL | 2 | RobotDictionaryEntryTable |
| UMM\_LTEL3 | UMM\_LTEL | 2 | RobotDictionaryEntryTable |
| UMM\_LTEL\_D2 | UMM\_LTEL | 2 | RobotDictionaryEntryTable\_D4 |
| UMM\_RADA | UMM\_RADA | 2 | RobotDictionaryEntryTable |
| UMM\_RADA2 | UMM\_RADA | 2 | RobotDictionaryEntryTable |
| UMM\_RADA3 | UMM\_RADA | 2 | RobotDictionaryEntryTable |
| UMM\_RADA\_D2 | UMM\_RADA | 2 | RobotDictionaryEntryTable\_D4 |
| UMM\_RMES | UMM\_RMES | 2 | RobotDictionaryEntryTable |
| UMM\_RMES2 | UMM\_RMES | 2 | RobotDictionaryEntryTable |
| UMM\_RMES3 | UMM\_RMES | 2 | RobotDictionaryEntryTable |
| UMM\_RMES\_D2 | UMM\_RMES | 2 | RobotDictionaryEntryTable\_D4 |
| UMM\_ZIAT | UMM\_ZIAT | 2 | RobotDictionaryEntryTable |
| UMM\_ZIAT2 | UMM\_ZIAT | 2 | RobotDictionaryEntryTable |
| UMM\_ZIAT3 | UMM\_ZIAT | 2 | RobotDictionaryEntryTable |
| UMM\_ZIAT\_D2 | UMM\_ZIAT | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_CLIN | UMS\_CLIN | 2 | RobotDictionaryEntryTable |
| UMS\_CLIN2 | UMS\_CLIN | 2 | RobotDictionaryEntryTable |
| UMS\_CLIN\_C3 | UMS\_CLIN | 2 | RobotDictionaryEntryTable |
| UMS\_CLIN\_D2 | UMS\_CLIN | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_DLGN | UMS\_DLGN | 2 | RobotDictionaryEntryTable |
| UMS\_DLGN3 | UMS\_DLGN | 2 | RobotDictionaryEntryTable |
| UMS\_DLGN\_D2 | UMS\_DLGN | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_LTEL | UMS\_LTEL | 2 | RobotDictionaryEntryTable |
| UMS\_LTEL3 | UMS\_LTEL | 2 | RobotDictionaryEntryTable |
| UMS\_LTEL\_D2 | UMS\_LTEL | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_RADA | UMS\_RADA | 2 | RobotDictionaryEntryTable |
| UMS\_RADA2 | UMS\_RADA | 2 | RobotDictionaryEntryTable |
| UMS\_RADA3 | UMS\_RADA | 2 | RobotDictionaryEntryTable |
| UMS\_RADA\_D2 | UMS\_RADA | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_RMES | UMS\_RMES | 2 | RobotDictionaryEntryTable |
| UMS\_RMES2 | UMS\_RMES | 2 | RobotDictionaryEntryTable |
| UMS\_RMES3 | UMS\_RMES | 2 | RobotDictionaryEntryTable |
| UMS\_RMES\_D2 | UMS\_RMES | 2 | RobotDictionaryEntryTable\_D4 |
| UMS\_ZIAT | UMS\_ZIAT | 2 | RobotDictionaryEntryTable |
| UMS\_ZIAT\_D2 | UMS\_ZIAT | 2 | RobotDictionaryEntryTable\_D4 |
| UZAR | UZAR | 2 | RobotDictionaryEntryTable |
| UZAR\_C4 | UZAR | 2 | RobotDictionaryEntryTable |
| UZAR\_C5 | UZAR | 2 | RobotDictionaryEntryTable |
| UZAR\_D | UZAR | 2 | RobotDictionaryEntryTable |
| UZAR\_D1 | UZAR | 2 | RobotDictionaryEntryTable\_D4 |
| UZAR\_D2 | UZAR | 2 | RobotDictionaryEntryTable\_D4 |
| VANX | VANX | 2 | RobotDictionaryEntryTable |
| VANX2 | VANX | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA2 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA3 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_10B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_10C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_7B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_7C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_8B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_8C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_9B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_9C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_C2 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_C3 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_D1 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D4 |
| VAY\_RUMINA\_D2 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D4 |
| VAY\_RUMINA\_DL1A | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D1 |
| VAY\_RUMINA\_DL1B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D1 |
| VAY\_RUMINA\_DL1C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D1 |
| VAY\_RUMINA\_DL2A | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D2 |
| VAY\_RUMINA\_DL2B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D2 |
| VAY\_RUMINA\_DL2C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D2 |
| VAY\_RUMINA\_DL2C2 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D2 |
| VAY\_RUMINA\_DL3A | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_DL3B | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_DL3C | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_DL3D | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_DL3E | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_DL3F | VAY\_RUMINA | 2 | RobotDictionaryEntryTable\_D3 |
| VAY\_RUMINA\_S | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VAY\_RUMINA\_S2 | VAY\_RUMINA | 2 | RobotDictionaryEntryTable |
| VF31CGKF | VF31CGKF | 2 | RobotDictionaryEntryTable |
| VF31CGKF2 | VF31CGKF | 2 | RobotDictionaryEntryTable |
| VF31CGKFS | VF31CGKFS | 2 | RobotDictionaryEntryTable |
| VF31CGKFS2 | VF31CGKFS | 2 | RobotDictionaryEntryTable |
| VF31EGKF | VF31EGKF | 2 | RobotDictionaryEntryTable |
| VF31EGKFS | VF31EGKFS | 2 | RobotDictionaryEntryTable |
| VF31FGKF | VF31FGKF | 2 | RobotDictionaryEntryTable |
| VF31FGKF2 | VF31FGKF | 2 | RobotDictionaryEntryTable |
| VF31FGKF2S | VF31FGKFS | 2 | RobotDictionaryEntryTable |
| VF31FGKFS | VF31FGKFS | 2 | RobotDictionaryEntryTable |
| VF31FGKFS\_D | VF31FGKFS | 2 | RobotDictionaryEntryTable\_D4 |
| VF31FGKFS\_D2 | VF31FGKFS | 2 | RobotDictionaryEntryTable\_D4 |
| VF31FGKF\_D | VF31FGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31FGKF\_D2 | VF31FGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31FSGKF | VF31FSGKF | 2 | RobotDictionaryEntryTable |
| VF31FSGKF2 | VF31FSGKF | 2 | RobotDictionaryEntryTable |
| VF31FSGKF\_D | VF31FSGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31FSGKF\_D2 | VF31FSGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31JGKF | VF31JGKF | 2 | RobotDictionaryEntryTable |
| VF31JGKFS | VF31JGKFS | 2 | RobotDictionaryEntryTable |
| VF31JSGKF | VF31JSGKF | 2 | RobotDictionaryEntryTable |
| VF31JSGKF2 | VF31JSGKF | 2 | RobotDictionaryEntryTable |
| VF31JSGKFS | VF31JSGKFS | 2 | RobotDictionaryEntryTable |
| VF31JSGKFS2 | VF31JSGKFS | 2 | RobotDictionaryEntryTable |
| VF31JSGKFS\_D | VF31JSGKFS | 2 | RobotDictionaryEntryTable\_D4 |
| VF31JSGKFS\_D2 | VF31JSGKFS | 2 | RobotDictionaryEntryTable\_D4 |
| VF31JSGKF\_D | VF31JSGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31JSGKF\_D2 | VF31JSGKF | 2 | RobotDictionaryEntryTable\_D4 |
| VF31SGKF | VF31SGKF | 2 | RobotDictionaryEntryTable |
| VF31SGKFS | VF31SGKFS | 2 | RobotDictionaryEntryTable |
| VOLFG140 | VOLFG140 | 2 | RobotDictionaryEntryTable\_D2 |
| VOLFG140\_2 | VOLFG140 | 2 | RobotDictionaryEntryTable\_D2 |
| VOLFG140\_3 | VOLFG140 | 2 | RobotDictionaryEntryTable\_D2 |
| VRKS | VRKS | 2 | RobotDictionaryEntryTable\_D3 |
| VRKS\_2 | VRKS | 2 | RobotDictionaryEntryTable\_D3 |
| VRKS\_EV | VRKS | 2 | RobotDictionaryEntryTable\_D3 |
| VRVN | VRVN | 2 | RobotDictionaryEntryTable |
| WG0\_EW | WG0\_EW | 2 | RobotDictionaryEntryTable |
| WG0\_EW2 | WG0\_EW | 2 | RobotDictionaryEntryTable |
| WG0\_EW2S | WG0\_EW | 2 | RobotDictionaryEntryTable |
| WG0\_EW\_0 | WG0\_EW | 2 | RobotDictionaryEntryTable |
| WG0\_EW\_C | WG0\_EW | 2 | RobotDictionaryEntryTable\_D3 |
| WG0\_EW\_D | WG0\_EW | 2 | RobotDictionaryEntryTable\_D4 |
| WLWPS | WLWPS | 2 | RobotDictionaryEntryTable |
| WLWPS\_C | WLWPS | 2 | RobotDictionaryEntryTable\_D3 |
| WLWPS\_C4 | WLWPS | 2 | RobotDictionaryEntryTable |
| WLWPS\_D | WLWPS | 2 | RobotDictionaryEntryTable |
| WNDBTLSP | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| WNDBTLSP2 | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| WNDBTLSP3 | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| WNDBTLSP3\_D2 | WNDBTLSP | 2 | RobotDictionaryEntryTable\_D4 |
| WNDBTLSP\_C3 | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| WNDBTLSP\_S | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| WNDBTLSP\_S2 | WNDBTLSP | 2 | RobotDictionaryEntryTable |
| W\_DEENBELL | W\_DEENBELL | 2 | RobotDictionaryEntryTable\_D4 |
| W\_DEENBELL\_2 | W\_DEENBELL | 2 | RobotDictionaryEntryTable\_D4 |
| W\_DYNZNON | W\_DYNZNON | 2 | RobotDictionaryEntryTable |
| XELGD\_F | XELGD | 2 | RobotDictionaryEntryTable |
| XELGD\_F2 | XELGD | 2 | RobotDictionaryEntryTable |
| XELGD\_M | XELGD | 2 | RobotDictionaryEntryTable |
| XELGD\_M2 | XELGD | 2 | RobotDictionaryEntryTable |
| YCLOWN | YCLOWN | 2 | RobotDictionaryEntryTable\_D3 |
| YCLOWN\_S | YCLOWN | 2 | RobotDictionaryEntryTable\_D3 |
| YzCLOWN | YzCLOWN | 2 | RobotDictionaryEntryTable\_D3 |
| ZEL\_BILLEN | ZEL\_BILLEN | 2 | RobotDictionaryEntryTable\_D4 |
| ZEL\_BILLEN\_2 | ZEL\_BILLEN | 2 | RobotDictionaryEntryTable\_D4 |
| ZGN | ZGN | 2 | RobotDictionaryEntryTable |
| ZGN2 | ZGN | 2 | RobotDictionaryEntryTable |
| ZGN2\_B | ZGN | 2 | RobotDictionaryEntryTable |
| ZGN\_B | ZGN | 2 | RobotDictionaryEntryTable |
| ZGN\_C | ZGN | 2 | RobotDictionaryEntryTable\_D3 |
| ZLDXX | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZLDXX2 | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZLDXX3 | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZLDXX\_0 | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZLDXX\_C4 | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZLDXX\_D1 | ZLDXX | 2 | RobotDictionaryEntryTable\_D4 |
| ZLDXX\_D2 | ZLDXX | 2 | RobotDictionaryEntryTable\_D4 |
| ZLDXX\_S | ZLDXX | 2 | RobotDictionaryEntryTable |
| ZMZZR | ZMZZR | 2 | RobotDictionaryEntryTable |
| ZMZZR2 | ZMZZR | 2 | RobotDictionaryEntryTable |
| ZMZZR3 | ZMZZR | 2 | RobotDictionaryEntryTable |
| ZMZZR\_0 | ZMZZR | 2 | RobotDictionaryEntryTable |
| ZMZZR\_C2 | ZMZZR | 2 | RobotDictionaryEntryTable |
| ZMZZR\_D1 | ZMZZR | 2 | RobotDictionaryEntryTable\_D4 |
| ZMZZR\_D2 | ZMZZR | 2 | RobotDictionaryEntryTable\_D4 |
| ZO | ZO | 2 | RobotDictionaryEntryTable |
| ZO\_C5 | ZO | 2 | RobotDictionaryEntryTable |
| ZO\_D | ZO | 2 | RobotDictionaryEntryTable |
| ZO\_D2 | ZO | 2 | RobotDictionaryEntryTable\_D4 |
| ZWUS | ZWUS | 2 | RobotDictionaryEntryTable |
| ZWUS2 | ZWUS | 2 | RobotDictionaryEntryTable |
| ZWUS\_C4 | ZWUS | 2 | RobotDictionaryEntryTable |
| ZWUS\_D | ZWUS | 2 | RobotDictionaryEntryTable |
| ZWUS\_D1 | ZWUS | 2 | RobotDictionaryEntryTable\_D4 |
| ZWUS\_D2 | ZWUS | 2 | RobotDictionaryEntryTable\_D4 |

## Zmierzone zbieżności dokładnych ID (badawcze, nie powiązanie własności)

Klucz `dic_pilot_X_00_0` zawiera człon `X`. Poniżej policzono, ile takich członów
jest **dokładnie równe** jakiemuś ID w rekordach gry. Równość nie dowodzi,
że wpis dotyczy tej postaci — własność pochodzi wyłącznie z 11 assetów powyżej.

- `dic\_text\_name`: grup 29, bez dokładnego ID 2; pola: defaultReferenceId=2, ipnameId=27, listAwakeData=1, listGlobalFlag=1, listHaveRobotSkillData=2, listIPTitleData=23, listRobotBaseData=2, listSpecialMoveData=1, robotimageID=2
- `dic\_text\_pilot`: grup 427, bez dokładnego ID 16; pola: defaultReferenceId=373, facialId=173, listAwakeData=6, listFacialChangeSettingData=11, listFacialSettingData=399, listHavePilotSkillData=110, listHaveRobotSkillData=1, listHaveSpiritCommandData=165, listKakeaiData=98, listPilotBaseData=175, listRobotBaseData=1, listShotdownMessageData=96, robotimageID=1
- `dic\_text\_robot`: grup 297, bez dokładnego ID 29; pola: defaultReferenceId=261, facialId=4, ipnameId=2, listArmorPurgeData=1, listAwakeData=5, listFacialSettingData=4, listGlobalFlag=3, listHavePilotSkillData=4, listHaveRobotSkillData=195, listHaveSpiritCommandData=4, listIPTitleData=2, listKakeaiData=4, listMapTransformationData=6, listPilotBaseData=4, listRetrofitData=4, listRobotBaseData=264, listShotdownMessageData=1, listSpecialMoveData=5, robotimageID=268
- `dic\_text\_word`: grup 78, bez dokładnego ID 78; pola: brak

## Postacie — biografie

### dic\_pilot\_AKIRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8b60b000`

> Wysportowany chłopak, kapitan drużyny piłkarskiej Akademii Nadmorskiej. Syn Ichira, badacza energii Mutron, i Lemurii, księżniczki Imperium Mu. Przeznaczeniem Akiry jest Fade In, czyli połączenie się z Reideenem, bóstwem opiekuńczym Mu. Walczy nim z Imperium Yoma, by nie dopuścić do nadejścia Ery Demonów. Pełen zapału, pogodny i prawy, nie ugina się pod ciężarem przeznaczenia i nie traci odwagi nawet w beznadziejnym położeniu. Spokój odbiera mu jednak myśl o matce, Lemurii, która, jak się okazało, żyje.

### dic\_pilot\_MARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b001`

> Koleżanka Akiry z klasy i gwiazda Akademii Nadmorskiej. Córka kierownika Higashiyamy z Instytutu Inżynierii Przyszłości: pogodna chłopczyca, której roztrzepanie Akira często bierze na języki. Jest dla niego oparciem w walce, a w końcu, by mu pomóc, wstępuje do Co-oplanders i wspiera Reideena z pokładu Bluegara.

### dic\_pilot\_REIASUKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b003`

> Członkini Co-oplanders obdarzona mocą parapsychiczną. Jej wyostrzone zmysły wyczuwają Reideena i bestie kopalne. Najpierw latała z Chikarą Jingujim na Bluegarze, wspierając Reideena, potem wyruszyła z Ichirem Hibikim do Tybetu, by odnaleźć matkę Akiry, Reiko Hibiki. Zanim dołączyła do Co-oplanders, jeździła z gangiem motocyklowym, a przez pewien czas była też zakonnicą.

### dic\_pilot\_SARU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b005`

> Chłopak odpowiedzialny w Mutropolis za rozwój techniki. Genialny umysł, specjalista od projektowania i analizy maszyn. Uczestniczy w badaniach nad energią Mutron; analizując Reideena, odkrył jego ukryte moce i bronie. Jako członek Co-oplanders bywał też w załodze Bluegara.

### dic\_pilot\_HIGASHI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b007`

> Kierownik Instytutu Inżynierii Przyszłości, ojciec Mari Sakurano. W odpowiedzi na najazd Imperium Yoma zbudował naukową fortecę Mutropolis. Dowodzi nią i stworzył Co-oplanders, by wspierać Reideena.

### dic\_pilot\_KYUZO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b009`

> Profesor archeologii, dziadek Akiry. Ze starych zapisków kontynentu Mu wyczytał zapowiedź powrotu demonów. W Tybecie odczytał gliniane tabliczki cywilizacji Mu i odsłonił jej dzieje.

### dic\_pilot\_REIKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00b`

> Matka Akiry i księżniczka starożytnego Imperium Mu, gdzie nosiła imię Lemuria. 12 000 lat temu zapadła w sen, by w dalekiej przyszłości pokrzyżować plany odrodzonego Imperium Yoma. Przebudzona w naszych czasach poślubiła Ichira Hibikiego i urodziła Akirę. Potem zniknęła z życia syna, by odszukać Gwiazdę Ra Mu, święty skarb Imperium Mu. Akira nie wiedział więc, że jego matka żyje.

### dic\_pilot\_REIKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00c`

> Wraca do Akiry tuż przed ostateczną bitwą z Imperium Yoma. W starciu z cesarzem Yoma Barao oddaje życie, by uruchomić Gwiazdę Ra Mu, co daje zwycięstwo Akirze i całej ludzkości.

### dic\_pilot\_ICHIRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00d`

> Ojciec Akiry, archeolog. Podczas poszukiwań energii Mutron Imperium Yoma zamieniło go w kamień. Po upadku Sharkina został uwolniony i szczęśliwie spotkał się z synem. Potem wyruszył z Kyuzem i Rei do Tybetu, by odnaleźć zaginioną żonę, Reiko.

### dic\_pilot\_ICHIRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00e`

> W przededniu ostatecznej bitwy z Imperium Yoma wraca do Japonii i odnajduje Reiko. Po ostatniej walce jako ojciec wspiera Akirę w żałobie po matce.

### dic\_pilot\_BARAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00f`

> Władca Imperium Yoma. Przez 12 000 lat spoczywał zapieczętowany w kamiennym posągu. Uwolniły go modły księcia Sharkina, naczelnego dowódcy Imperium Yoma, który oddał za niego życie. Pragnie energii Mutron, by sprowadzić Erę Demonów, i raz po raz nasyła na Reideena zabójców. Sam przerasta Reideena wielokrotnie, a dolną połową ciała tkwi w Wyspie Yoma.

### dic\_pilot\_BARAO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b010`

> Straciwszy wszystkich podwładnych, całą swą mocą wywołuje kataklizmy i rusza na Mutropolis. Jego przytłaczającej potędze nie dorównuje nawet Reideen, lecz w końcu ulega Reideenowi powiększonemu mocą Gwiazdy Ra Mu.

### dic\_pilot\_BEROS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b011`

> Arcykapłan Imperium Yoma. Inkantacjami i promieniami z demonicznego posągu tworzy bestie kopalne. Ma pod sobą wielu kapłanów.

### dic\_pilot\_BEROS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b012`

> Pochłonęła go szczelina ziemi, która otwarła się przy przebudzeniu cesarza Yoma Barao.

### dic\_pilot\_HYOMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b000`

> Przywódca Zespołu Bojowego, pilot maszyny nr 1, Battlejeta, i główny pilot Combattlera V. Wcześnie stracił rodziców w wypadku i wychował się w sierocińcu Słoneczna Szkoła. Świetny motocyklista, porywczy i skory do bójki, ma wrodzony talent do walki. Pogodny i prostolinijny, żyje zasadą “bronić słabych, utrzeć nosa silnym” i nigdy się nie poddaje. W sprawach serca jest jednak beznadziejnie nieśmiały i długo nie odwzajemniał uczuć Chizuru. Dopiero po wojnie z Campbellianami ich uczucie się spełniło. Po walce wręcz z odwiecznym wrogiem, Garudą, odniesione rany sprawiły, że w miejsce rąk nosi zaawansowane protezy.

### dic\_pilot\_JUZO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b002`

> Członek Zespołu Bojowego, pilot maszyny nr 2, Battlecrashera. Chłodny cynik o ciętym języku, ale z kansajskim zaśpiewem trudno go nie lubić. Bywa, że kłóci się z Hyomą, a nawet wdaje z nim w bójki, jednak w głębi serca obaj uważają się za niezastąpionych towarzyszy. Genialny strzelec, który zwyciężał w zawodach już jako ośmiolatek; jego celne oko wielokrotnie ratowało zespół. W Combattlerze V odpowiada za systemy strzeleckie.

### dic\_pilot\_DAISK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b004`

> Członek Zespołu Bojowego, pilot maszyny nr 3, Battletanka. Łagodny olbrzym: silny, a przy tym dobroduszny. Pochodzi z Kiusiu, mistrzowsko opanował judo, a marzy o karierze rysownika mangi.

### dic\_pilot\_CHZUR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b006`

> Jedyna dziewczyna w Zespole Bojowym, pilotka maszyny nr 4, Battlemarine. Wnuczka doktora Nambary, twórcy Combattlera V, i ulubienica drużyny. Zna się na oceanologii, medycynie i robotyce, a do tego gra na pianinie, pływa i uprawia gimnastykę. Czuła i dobra, choć bywa chłopczycą. Zakochana w Hyomie, nie raz gotowa była narazić życie, by go chronić. Długo nie umiała przyznać się do uczuć, lecz po wojnie z Campbellianami wreszcie się z nim porozumiała.

### dic\_pilot\_KOSKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b008`

> Najmłodszy członek Zespołu Bojowego, pilot maszyny nr 5, Battlecrafta. Choć to jeszcze uczeń podstawówki, ten mały geniusz studiował już na amerykańskiej uczelni i ma na koncie wiele wynalazków (niektóre dość osobliwe). Pozostaje jednak dzieckiem: gdy wróg zaatakował Hokkaido, gdzie mieszkają jego rodzice, całkiem stracił panowanie nad sobą. Do tego wciąż zdarza mu się moczyć w nocy. W Combattlerze V analizuje przeciwnika i podsuwa Hyomie cenne wskazówki.

### dic\_pilot\_YOTYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00a`

> Naukowiec, który po śmierci doktora Nambary, swego dawnego przyjaciela, kieruje Nambara Connection. Gdy Nambara po raz pierwszy poprosił go o dowodzenie Zespołem Bojowym, odmówił, twierdząc, że ludzkość może sobie ginąć. Kiedy jednak Nambara oddał za niego życie, postanowił walczyć w obronie ukochanej przyrody. Rubaszny, mówi bez ogródek, ale nawet w najgorszym położeniu niezłomnie szuka wyjścia. Uwielbia alkohol i zawsze nosi przy sobie butelkę whisky.

### dic\_pilot\_ROPET\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00c`

> Robot mierzący fale mózgowe, zbudowany przez doktora Nambarę na potrzeby łączenia. Bada fale mózgowe piątki z Zespołu Bojowego; dopiero gdy wskaźniki na jego ciele zrównają się, czyli gdy fale całej piątki się zsynchronizują, łączenie staje się możliwe. Ma ludzkie uczucia; raz nawet zakochał się w ślicznej robotce, którą przysłał wróg.

### dic\_pilot\_GALDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00e`

> Wielki Generał planety Campbell. Na rozkaz ukochanej matki, Oleany, dowodzi inwazją na Ziemię. Zwykle ma postać młodzieńca, ale potrafi przybrać ptasią postać. Zimny i bezwzględny, Ziemian ma za robactwo, a zarazem jest dumnym wojownikiem i szanuje tych, których uzna za godnych. Hyomę i Combattlera V, pogromców wielu jego podwładnych, uważa za godnych rywali i wciąż knuje przeciw nim nowe plany, które raz za razem zawodzą.

### dic\_pilot\_GALDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00f`

> W zażartej walce z Combattlerem V przypadkiem odkrywa, że jest androidem. Gdy po kolejnych porażkach Oleana chce go zlikwidować, stawia swój honor na jedną kartę i wsiada do olbrzymiego robota bojowego Big Garuda. Zabija Oleanę, fałszywą matkę, i wyzywa Combattlera V na pojedynek. Przegrywa po zaciętej walce i ginie w eksplozji razem z kochającą go androidką Mią.

### dic\_pilot\_CAMIYU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b010`

> Młody Newtype z AEUG, pilot Zeta Gundama. Ma 17 lat. Był wrażliwym, ale poza tym zwyczajnym uczniem liceum w kolonii kosmicznej Green Noa. Miał kompleks na punkcie swojego imienia, Kamille, uchodzącego za dziewczęce, więc rzucił się w “męskie” zajęcia: latanie na homoavisie (prostej lotni) i karate. Dzięki rodzicom, oficerom technicznym Federacji Ziemskiej, zna się na mechanice; wygrał nawet Juniorski Turniej Mobile Suitów. Gdy Jerid wyśmiał jego imię, wdał się z nim w awanturę, co postawiło go przeciw Titans. Splot wydarzeń sprawił, że pomógł ludziom Quattra ukraść Gundama Mk-II i tak trafił do AEUG. W walce przebudziły się w nim zdolności Newtype'a i z czasem został asem AEUG. Z początku walczył z czystej niechęci do Titans, lecz spotkania i rozstania z dorosłymi, takimi jak Quattro i Amuro, oraz z kobietami, takimi jak Four i Rosamia, pozwoliły mu bardzo dojrzeć. Szukając sposobu na zakończenie wojny, sięgał świadomością w przestrzeń kosmiczną. W finale serialu Scirocco, pokonany, pociągnął za sobą jego umysł, co zostawiło w Kamille'u głęboką ranę. W finale filmowym Kamille wychodzi z tego cało i odnajduje Fę; oboje cieszą się, że przeżyli.

### dic\_pilot\_FA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b001`

> Przyjaciółka Kamille'a z dzieciństwa. Ma 17 lat. Ponieważ znała Kamille'a, który ukradł Gundama Mk-II, Bask uwięził ją razem z rodzicami. Uratowana przez Brighta, wstąpiła do AEUG, by walczyć z Titans i być przy Kamille'u, i zgłosiła się na pilotkę. Choć gryzło ją, że brak jej umiejętności, przetrwała cały konflikt Gryps. Opiekuńcza z natury, od dawna strofuje Kamille'a za zachowanie i nawyki, co jego w duchu doprowadza do szału. Pewnie właśnie dlatego to jej przypadła opieka nad Shintą i Qum, sierotami, które Quattro przywiózł na Argamę. W finale serialu ukochany Kamille doznaje w ostatniej bitwie załamania psychicznego, a Fa opuszcza front, by się nim opiekować. W wersji filmowej oboje cieszą się, że wyszli z wojny cało.

### dic\_pilot\_EMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b003`

> Pilotka AEUG w stopniu porucznika. Służyła w Titans, ale po tym, jak była świadkiem ich nikczemnej operacji, przeszła na stronę AEUG. Jej świetne umiejętności pilotażu zyskały uznanie w AEUG, więc powierzano jej kluczowe maszyny, takie jak Rick Dias, Gundam Mk-II czy Super Gundam, i opanowała każdą z nich. Ma żelazną wolę, kieruje się własnymi przekonaniami i wymaga jak żołnierz, a zarazem jest kobieco łagodna. Zaloty Henkena zawsze zbywała chłodno, choć w głębi duszy chyba nie miała nic przeciwko. W ostatniej bitwie z Titans została ranna; powierzyła Kamille'owi dokończenie walki i zmarła w jego ramionach.

### dic\_pilot\_SHIROKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b005`

> Kapitan ogromnego transportowca Jupitris, zwany “człowiekiem, który wrócił z Jowisza”. Uzdolniony Newtype, pierwszorzędny pilot, a do tego konstruktor mobile suitów. Charyzmatyczny, przewidujący i obdarzony zmysłem strategicznym, uważa się jednak za geniusza i patrzy na innych z góry. Po wstąpieniu do Titans, elitarnej formacji sił Federacji Ziemskiej, odnosi sukces za sukcesem, aż w końcu zabija przywódcę Titans, Jamitova, i przejmuje władzę. Gdy wojna przeradza się w trójstronny konflikt z AEUG, ruchem oporu przeciw Federacji, i Axis, resztkami sił Zeonu, zawiązuje potajemny sojusz z Axis. W ostatniej bitwie toczy w zaprojektowanym przez siebie The-O zażartą walkę z Kamille'em, lecz Zeta Gundam w formie Waverider przebija go razem z maszyną.

### dic\_pilot\_YAZAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b007`

> Oficer Titans, początkowo porucznik, później awansowany do stopnia pełnego porucznika. Wojowniczy, szczerze cieszy się wojną, bo może w niej używać siły do woli. Wybitny pilot; szybkimi mobile suitami, takimi jak Gaplant czy Hambrabi, steruje jak własnym ciałem i nieraz dał się we znaki oddziałowi MS Argamy. Sprytny i okrutny, bez wahania zgładzi każdego, kto mu przeszkadza, nawet przełożonego. Potrafi jednak dbać o swoich, a podwładni, tacy jak Ramsus i Dunkel, ufają mu bez reszty. Odbiera życie Katzowi i Emmie, a potem jeszcze się śmieje; to okrucieństwo sprawia, że Kamille uruchamia Bio-Sensor Zeta Gundama. Zestrzelony przez Zetę dryfuje w kosmosie, aż ekipa Judaua wyławia jego kapsułę ratunkową i Yazan pojawia się w kolonii Shangri-La. Wykorzystuje Judaua i jego kompanów do ataku na Argamę zacumowaną w Shangri-La, ale brutalne metody rozwścieczają Judaua, który w Zeta Gundamie odpłaca mu pięknym za nadobne.

### dic\_pilot\_ASUT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b009`

> Szef mechaników Argamy, starszy sierżant. Fachowiec: dzięki niemu oddział MS Argamy zawsze walczy w pełnej gotowości. Przekazał pomysły Kamille'a do Anaheim Electronics, czym po cichu przyczynił się do powstania Zeta Gundama. Ceniony za umiejętności, w drugiej wojnie z Neo Zeonem był mechanikiem na Ra Cailum.

### dic\_pilot\_AMRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00b`

> Pilot Newtype z jednostki Londo Bell sił Federacji Ziemskiej, w stopniu porucznika. W wojnie jednorocznej pilotował Gundama RX-78 i walczył w wielu bitwach. Rozwinął się jako Newtype i zapisał legendarną kartę bojową. Po wojnie Federacja, obawiając się jego zdolności, trzymała go w areszcie domowym. Mimo to w konflikcie Gryps przyłączył się do Karaby, organizacji wspierającej AEUG, i walczył z Titans. Po pierwszej wojnie z Neo Zeonem trafił do Londo Bell, nowej jednostki pomocniczej Federacji, i walczył z siłami Neo Zeonu pod wodzą Chara Aznable'a, dawnego towarzysza broni i odwiecznego rywala. W wojnie jednorocznej był zamkniętym w sobie, naiwnym chłopakiem, lecz dzięki spotkanym ludziom i przeżyciom bardzo dojrzał. W drugiej wojnie z Neo Zeonem w zaprojektowanym przez siebie Nu Gundamie próbował powstrzymać zrzucenie Axis na Ziemię. Nadprzyrodzona moc Psycho-frame pozwoliła odepchnąć Axis, ale Amuro zaginął razem z Charem i zniknął z kart historii.

### dic\_pilot\_BURAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00d`

> Dowódca Londo Bell, jednostki pomocniczej Kosmicznych Sił Federacji Ziemskiej, w stopniu komandora. Ma 36 lat. Od czasu, gdy w wojnie jednorocznej dowodził White Base, był kapitanem kolejnych okrętów-matek gundamów i zasłynął jako dowódca oddziałów Newtype'ów. Przez tę przeszłość uchodzi za niebezpiecznego i odsunięto go od głównego nurtu armii, lecz prawość, z jaką odcina się od polityki, i ogromne doświadczenie bojowe zjednują mu pełne zaufanie podwładnych. W drugiej wojnie z Neo Zeonem poprowadził Londo Bell i razem z Amurem Rayem, podwładnym i bliskim przyjacielem, udaremnił plan Chara, by pogrążyć Ziemię w epoce lodowcowej.

### dic\_pilot\_MERAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00f`

> Zastępca dowódcy Ra Cailum w stopniu komandora porucznika. Opanowany i rzeczowy, od drugiej wojny z Neo Zeonem wspiera kapitana Brighta.

### dic\_pilot\_CHEAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b011`

> Oficer techniczny sił Federacji Ziemskiej. Oddelegowana do Anaheim Electronics, odpowiadała za rozwój Nu Gundama. Darzy uczuciem swego przełożonego, Amura, i z niezwykłym zapałem dostraja Psycho-frame, by mu pomóc. W bitwie o Axis wyrusza na front w uszkodzonym Re-GZ, by dostarczyć Amurowi próbkę Psycho-frame, która wzmocni Nu Gundama. Staje między Hathawayem a Quess i niszczy Alpha Azieru, lecz ginie z ręki Hathawaya, oszalałego z rozpaczy po śmierci Quess.

### dic\_pilot\_CHAR\_\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b013`

> Wódz Neo Zeonu. Naprawdę nazywa się Casval Rem Deikun; jest synem Zeona Zuma Deikuna, zgładzonego przez ród Zabich. W wojnie jednorocznej jako “Czerwona Kometa” zasłynął zmysłem taktycznym i mistrzowskim pilotażem mobile suitów. W konflikcie Gryps jako Quattro Bajeena walczył z Titans, lecz w bitwie o Działo Laserowe Kolonii po pojedynku z Haman przepadł bez śladu. Trzy lata po pierwszej wojnie z Neo Zeonem powrócił w okolice Ziemi na czele odrodzonego Neo Zeonu. Spacenoidzi, gnębieni przez Federację, powitali go z entuzjazmem, a wiele kolonii poparło Neo Zeon. Jako Wódz Neo Zeonu wypowiada wojnę Federacji, posługując się polityczną grą i intrygą. W sercu wciąż jednak nosi Lalah Sune i dlatego pragnie wreszcie rozstrzygnąć trwający 14 lat spór z Amurem. Aby wypędzić ludzkość z Ziemi, przystępuje do planu oziębienia planety. Na spadającej Axis staje do ostatniej walki z Amurem i, otulony światłem Psycho-frame, znika razem z nim.

### dic\_pilot\_QUES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b015`

> Jedyna córka Adenauera, wiceministra w sztabie sił Federacji Ziemskiej. Swobodna, o gwałtownych nastrojach, ocenia ludzi bezlitośnie trafnie. Interesuje się Newtype'ami, a w Indiach nawet przechodziła szkolenie duchowe. Oczarowana Charem, którego poznała w Londenion, ucieka do Neo Zeonu. Tam budzą się w niej zdolności Newtype'a i walczy w Jagd Dodze, by być Charowi przydatną. W walce zabija własnego ojca, choć nie jest tego w pełni świadoma. W bitwie o Axis pilotuje olbrzymi mobile armor Alpha Azieru. Gdy znów spotyka Hathawaya, osłania go przed atakiem Chan i ginie.

### dic\_pilot\_GUNEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b017`

> Pilot Neo Zeonu, latający na Jagd Dodze, mobile suicie dla Newtype'ów. To Cyber-Newtype z laboratorium Newtype'ów kierowanego przez Nanai Miguel. Ambitny, chciwie dąży do rozwoju swoich zdolności i czyha na okazję do awansu. Zdolności Newtype'a ma rzeczywiście duże: jako jedyny spośród wzmocnionych w laboratorium potrafi używać Funneli, broni psycommu. Gdy do Chara przybywa Quess, uznaje ją za prawdziwą Newtype i coraz bardziej go do niej ciągnie. W bitwie o Axis błyszczy, zestrzeliwując wszystkie pociski jądrowe Londo Bell, lecz ginie w starciu z Amurem w Nu Gundamie.

### dic\_pilot\_REZN\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b019`

> Pilotka Neo Zeonu, dowódczyni plutonu Geara Dog. Swoją maszynę maluje na niebiesko, w osobistych barwach. Świetna pilotka, nie cierpi tanich sztuczek i uważa, że mobile suity powinny walczyć przede wszystkim wręcz. Gardzi Cyber-Newtype'ami i potrafi zadrzeć z Gyuneiem. W bitwie o Axis atakuje Ra Cailum, ale ginie od bezpośredniego trafienia ogniem przeciwlotniczym Chan, wspomaganym przez Psycho-frame.

### dic\_pilot\_NANA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b000`

> Oficer taktyczna Neo Zeonu i dyrektor laboratorium Newtype'ów. Char darzy ją pełnym zaufaniem: powierzył jej między innymi dowodzenie atakiem z zaskoczenia na Lunę II. W laboratorium również ma sukcesy, choćby wyszkolenie Gyuneia. Jest kochanką Chara i wspiera go także prywatnie, jako kobieta. Nie kryje jednak niechęci do Quess, którą Char przyprowadził.

### dic\_pilot\_RAIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b002`

> Kapitan Rewlooli, okrętu flagowego floty Neo Zeonu. Gdy Char wyrusza do walki w Sazabim, przejmuje dowodzenie, choć nie podoba mu się, że Wódz osobiście walczy w mobile suicie.

### dic\_pilot\_KAMRN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b004`

> Urzędnik Biura Kontroli Finansowej kolonii Londenion. Niegdyś narzeczony Mirai, żony Brighta, z woli rodziców. Uczestnicząc w tajnych rozmowach Federacji z Neo Zeonem, podejrzewa, że rozbrojenie Neo Zeonu to kłamstwo, i pomaga Brightowi, nie bacząc na własne bezpieczeństwo.

### dic\_pilot\_DOMON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b006`

> Mistrz kolonijnych sztuk walki i Gundam Fighter reprezentujący Neo-Japonię. Po dziesięciu latach nauki u Master Asii, Niepokonanego ze Wschodu, przejął tytuł Króla Kier. Startuje w 13. Gundam Fight, by uwolnić ojca, doktora Kasshu, skazanego za zdradę na bezterminowe zamrożenie, i odnaleźć brata, Kyojiego, który ukradł Ultimate Gundama i uciekł na Ziemię. Wydaje się mrukliwy i chłodny, ale skrywa gorące serce i dobroć. W trakcie Gundam Fight dojrzewa dzięki przyjaźni z Sojuszem Shuffle, zaciętym walkom z mistrzem, Master Asią, i prawdzie o bracie. Gdy jego partnerka Rain staje się biologicznym rdzeniem Dark Gundama, Domon wyznaniem miłości otwiera jej zamknięte serce i uwalnia ją. Razem pokonują Dark Gundama ciosem Sekiha Love Love Tenkyoken i triumfalnie wracają na Ziemię.

### dic\_pilot\_RAIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b008`

> Przyjaciółka Domona Kasshu z dzieciństwa, członkini ekipy Gundam Team Neo-Japonii. Domon nie chce załogi, więc sama jest mechanikiem i lekarką: od konserwacji gundama po dbanie o jego zdrowie. Córka doktora Mikamury, autorytetu w dziedzinie gundamów; sama studiowała medycynę. Pogodna i oddana, wspiera Domona rozumem i czynem, jawnie i w cieniu. Pod koniec 13. Gundam Fight nieporozumienia i wina jej ojca oddalają ją od Domona. Wróg to wykorzystuje i Rain staje się biologicznym rdzeniem Dark Gundama, lecz ratuje ją wyznanie miłości Domona, który przybywa jej na pomoc. Razem pokonują Dark Gundama ciosem Sekiha Love Love Tenkyoken i triumfalnie wracają na Ziemię.

### dic\_pilot\_CHIBOD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00a`

> Gundam Fighter reprezentujący Neo-Amerykę. Rozdzielony z matką, jedyną krewną, żył w biednych dzielnicach Nowego Jorku z kradzieży i ulicznych walk. Dostrzeżono jego talent i został bokserem kolonijnym, a potem mistrzem z serią 100 zwycięstw. Spełniwszy amerykański sen, startuje w 13. Gundam Fight z nowym marzeniem: wynieść Neo-Amerykę na szczyt całego kosmosu. Zawsze towarzyszą mu cztery piękności zwane Chibodee Gals. Wesoły, pełen energii i wylewny. Zarażony komórkami DG zaatakował kiedyś Domona, lecz z pomocą Damy Pik wyzwolił się z nich, przejął herb Shuffle i został członkiem nowego Sojuszu Shuffle. W kolejnych starciach z Domonem i innymi fighterami nawiązał z nimi głęboką przyjaźń i walczył do końca jako członek Sojuszu Shuffle.

### dic\_pilot\_CYCYCI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00c`

> Gundam Fighter reprezentujący Neo-Chiny. Jego dziadek, Sai Feilong, wygrał 4. Gundam Fight. Syn wielkiego opata ziemskiego klasztoru Shaolin; startuje w Gundam Fight, by przywrócić podupadłemu klasztorowi dawną świetność. Mimo młodego wieku mistrzowsko włada kijem, ale to urwis, dowcipniś i trochę zbereźnik, który nie znosi treningu, czym bez przerwy utrapia swoich opiekunów, Keiuna i Zuisena. Świetnie gotuje: raz w zastępstwie kłopoczącego się właściciela rozkręcił uliczną garkuchnię. Zarażony komórkami DG zaatakował kiedyś Domona, lecz z pomocą Asa Trefl wyzwolił się z nich, przejął herb Shuffle i został członkiem nowego Sojuszu Shuffle. W kolejnych starciach z Domonem i innymi fighterami nawiązał z nimi głęboką przyjaźń i walczył do końca jako członek Sojuszu Shuffle.

### dic\_pilot\_JORJU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00e`

> Gundam Fighter reprezentujący Neo-Francję. Potomek szlacheckiego rodu de Sand, który pozostał na Ziemi razem z ludem, młodzieniec kochający ojczyznę, Neo-Francję, ponad wszystko. Startuje w 13. Gundam Fight dla dumy rodu i honoru Neo-Francji. Mistrz szermierki, zawsze kieruje się etykietą i kodeksem rycerskim; surowy wobec siebie, wobec innych szarmancki i łagodny. Przystojny i zawsze opanowany, nie zna jednak litości dla tych, którzy zachowują się nikczemnie lub ośmielą się skrzywdzić Marię Louise, której jako rycerz ślubował bezwzględną wierność. Zarażony komórkami DG zaatakował kiedyś Domona, lecz z pomocą Waleta Karo wyzwolił się z nich, przejął herb Shuffle i został członkiem nowego Sojuszu Shuffle. W kolejnych starciach z Domonem i innymi fighterami nawiązał z nimi głęboką przyjaźń i walczył do końca jako członek Sojuszu Shuffle.

### dic\_pilot\_ARUGO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b010`

> Gundam Fighter reprezentujący Neo-Rosję. Był przywódcą piratów kosmicznych, postrachu kolonii, lecz rząd Neo-Rosji pojmał jego kompanów jako zakładników. Ich wolność ma odkupić zwycięstwem w Gundam Fight. Sam też jest więźniem: na piersi ma zdalnie detonowaną bombę, na rękach ciężkie kajdany, a nadzorczyni Neo-Rosji, Nastasha Zabigov, nie spuszcza go z oka, więc nie ma ani krzty swobody. Groźny wygląd i małomówność sprawiają, że łatwo go źle ocenić, ale to człowiek prawy i oddany przyjaciołom. Zarażony komórkami DG zaatakował kiedyś Domona, lecz Czarny Joker oczyścił go z nich; przejął herb Shuffle i został członkiem nowego Sojuszu Shuffle. W kolejnych starciach z Domonem i innymi fighterami nawiązał z nimi głęboką przyjaźń i walczył do końca jako członek Sojuszu Shuffle.

### dic\_pilot\_AREBE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b012`

> Gundam Fighter reprezentująca Neo-Szwecję. Wcześnie osierocona, przeszła w wojskowym ośrodku elitarne szkolenie na fightera. Trudne dzieciństwo sprawiło, że buntowała się przeciw własnej ekipie, lecz spotkanie z Domonem, który przeżył podobny los, zmieniło ją w pogodną dziewczynę. W walce z Burning Gundamem Domona uruchomiono w niej Berserker System, który steruje umysłem z zewnątrz, i straciła zmysły, lecz pięść Domona, w którą włożył całą duszę, przywróciła jej przytomność. Po przegranej trzyma się Domona i darzy swego wybawcę nieśmiałym uczuciem.

### dic\_pilot\_TFFHAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b001`

> Poprzedni Król Kier i mistrz Domona. Zwycięzca 12. Gundam Fight, twórca szkoły walki Master Asia. Jego nadludzka siła pozwala mu pokonywać mobile fightery gołymi rękami. W trakcie 13. Gundam Fight chce mocą Dark Gundama usunąć ludzkość z Ziemi, przekonany, że to ludzie są przyczyną niszczenia planety. To jego własne przekonanie: w odróżnieniu od innych fighterów podległych Dark Gundamowi, którym umysły opanowały komórki DG, dzięki żelaznej woli zachowuje jasność umysłu. W finałowej bitwie królewskiej 13. Gundam Fight przegrywa z uczniem po straszliwym zderzeniu ciosów Sekiha Tenkyoken. Słowa Domona sprawiają, że uznaje swój błąd, i umiera spokojnie w jego ramionach.

### dic\_pilot\_WON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b003`

> Premier Neo-Hongkongu i organizator 13. Gundam Fight. W zmowie z Master Asią chce zdobyć Dark Gundama i jego mocą zapewnić sobie wieczną władzę nad koloniami. Pod dżentelmeńską powierzchownością kryje się intrygant, który nie przebiera w środkach.

### dic\_pilot\_ULBE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b005`

> Wojskowy z Neo-Japonii, ostatecznie w stopniu pułkownika. Były Gundam Fighter, kluczowa postać Biura Rozwoju Gundamów. W finale 12. Gundam Fight przegrał z Master Asią i zajął drugie miejsce. Oficjalnie wspierał z tyłu Domona w pościgu za Dark Gundamem, lecz naprawdę chciał jego mocą zawładnąć Sferą Ziemską. Odzyskał szczątki Dark Gundama zniszczonego na wyspie Lantau, przywrócił go do życia, czyniąc Rain jego biologicznym rdzeniem, i ogłosił całemu światu likwidację Gundam Fight. Opanowany przez komórki DG, stał się częścią samego Dark Gundama. W Grand Master Gundamie zaatakował Domona i jego przyjaciół, lecz padł od ciosu Shuffle Alliance Attack.

### dic\_pilot\_MRARIZ\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b007`

> Ukochana córka przywódcy Neo-Francji. Wzdycha do George'a; raz nawet, by zwrócić jego uwagę, poprosiła Domona o upozorowanie porwania. Pod słodką buzią kryje się niezła chłopczyca, a dla George'a gotowa jest działać nawet z narażeniem życia.

### dic\_pilot\_NTSHA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b009`

> Nadzorczyni Neo-Rosji, pilnująca więźnia Arga. Zjawiskowa i kompetentna, dowodzi mechanikami, operatorami i resztą ekipy. Zimna i gotowa na wszystko dla zwycięstwa, mięknie, widząc, jak Argo troszczy się o kompanów, i zbliża się do niego. Zostaje sojuszniczką Sojuszu Shuffle i pomaga mu pokonać Dark Gundama.

### dic\_pilot\_RIZOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00b`

> Naukowiec z Neo-Japonii, ojciec Domona i Kyojiego. Razem z Kyojim zbudował Ultimate Gundama (Dark Gundama). Spisek Urubego obarczył go winą za szał Dark Gundama i skazano go na wieczne zamrożenie. Uwolniony dzięki staraniom doktora Mikamury, doradza Domonowi i jego przyjaciołom, jak pokonać Dark Gundama.

### dic\_pilot\_STOKER\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00d`

> Przewodnik po Gundam Fight. Objaśnia pojedynki i ich tło.

### dic\_pilot\_HYRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00f`

> Agent operacji Meteor przysłany ze skupiska kolonii L1. Ma 16 lat. Od dziecka przechodził surowe szkolenie bojowe i ma niezwykłą sprawność fizyczną. Jego ciało jest wytrzymalsze niż u zwykłego człowieka: przeżył upadek z 50. piętra, a złamania nastawia sobie sam. Prócz walki świetnie radzi sobie z sabotażem i naprawą mobile suitów. Małomówny, unikał kontaktów z ludźmi, choć w głębi duszy jest dobrym chłopakiem; dzięki Relenie i innym pilotom gundamów stopniowo odzyskiwał ludzkie uczucia. Opanował Zero System Wing Gundama Zero i, wierząc w przyszłość, którą mu ukazał, oraz we własne uczucia, walczył z White Fang pod wodzą Zechsa. W ostatniej bitwie uratował Relenę uwięzioną w Librze i rozstrzygnął pojedynek z Zechsem. Zniszczył też spadającą Librę i ocalił Ziemię przed zimą nuklearną. Gdy zbuntowała się Armia Mariemai, zareagował jako jeden z pierwszych: odzyskał Wing Gundama Zero, wysłanego wcześniej ku Słońcu, i stoczył zaciekłą walkę z Wufeiem, który stał się wrogiem świata.

### dic\_pilot\_HYRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8d60b010`

> Ta walka bez oglądania się na siebie obudziła odwagę Releny i pomogła zakończyć konflikt.

### dic\_pilot\_DUO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b011`

> Agent operacji Meteor przysłany przez grupę złomiarzy działającą w pobliżu skupiska kolonii L2. Ma 16 lat. Pilot Gundama Deathscythe Hell. Okazuje wszystkie uczucia otwarcie i zwykle jest wesoły, choć potrafi się zaprzeć; spośród pilotów gundamów z kolonii najbardziej przypomina zwykłego chłopaka. Jego dewiza brzmi: “Mogę uciekać i się ukrywać, ale nigdy nie kłamię”. Nazywa siebie Żniwiarzem, bo, jak mówi, “cudów nie widziałem, ale trupów widziałem mnóstwo”. Podczas infiltracji bazy księżycowej poznał Hilde Schbeiker, ochotniczkę OZ, i z czasem otworzył jej oczy, choć ślepo wierzyła w OZ. Od tej pory wspierają się nawzajem. W ostatniej bitwie dzięki informacjom od Hilde przeniknął do Libry, uwolnił uwięzionych naukowców, przewiózł ich na Peacemillion i zdołał zmienić tor spadającej Libry. Razem z Heerem śledził poczynania Armii Mariemai i znów zasiadł w gundamie, by walczyć z wrogiem pokoju.

### dic\_pilot\_DUO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8d60b012`

> Po stłumieniu buntu Armii Mariemai prowadzi z Hilde złomowisko w jednej z kolonii.

### dic\_pilot\_TOROWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b000`

> Agent operacji Meteor przysłany ze skupiska kolonii L3. Ma prawdopodobnie 16 lat. Pilot Gundama Heavyarms Custom. Od dziecka wędrował jako najemnik po polach bitew; cichy i opanowany, o w dużej mierze nieznanej przeszłości. Nie jest jednak zimny: po cichu troszczy się o przyjaciół. Spośród pilotów gundamów najbliżej mu do Quatre'a; gdy ten, zrozpaczony postawą kolonii, wpadł w szał, Trowa przemówił mu do rozsądku z narażeniem życia. Przywrócił Quatre'owi trzeźwość umysłu, lecz jego maszyna została rozbita, a on sam zaginął. Odnaleziono go bez pamięci i woli walki; ukrywał się w cyrku jako “brat” Catherine. Na wezwanie Quatre'a wrócił do walki, przysięgając Catherine, że wróci żywy. “Trowa Barton” to nie jego prawdziwe imię, lecz imię pierwotnego pilota Heavyarmsa, zabitego w sporze o operację Meteor. Chłopak przypadkiem był świadkiem zabójstwa i aby je zatuszować, doktor S przekazał mu to imię; odtąd żyje jako Trowa Barton. Podczas buntu Armii Mariemai przeniknął w jej szeregi, by badać ją od środka. W bitwie o Brukselę błyszczał w Heavyarmsie Custom, którego dostarczył mu Quatre.

### dic\_pilot\_TOROWA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b001`

> Po zakończeniu wojny wrócił do cyrku Catherine.

### dic\_pilot\_CATOR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b002`

> Najstarszy syn i dziedzic bogatego rodu Winnerów ze skupiska kolonii L4. Ma 16 lat. W operacji Meteor zszedł na Ziemię jako agent i pilot Gundama Sandrock Custom. Wychowany w zamożnej, kochającej rodzinie, jest łagodny i dobry, a zarazem ma wyczucie bojowe, by w pełni wykorzystać gundama, i dar przywództwa. Ma 29 przyrodnich sióstr i dowodzi 40-osobowym oddziałem Maganac. Gdziekolwiek się pojawi, otaczają go ludzie, którzy go uwielbiają. Gdy jednak jego ojca, nieugiętego przeciwnika OZ, zabili mieszkańcy kolonii, Quatre wpadł w szał: zbudował zakazany mobile suit Wing Gundam Zero i zniszczył kolonię. Opamiętał się dopiero dzięki desperackim namowom Trowy, lecz za ogromną cenę. Uznał swój błąd i robił wszystko, by go odpokutować; zdołał nawet sprowadzić zaginionego Trowę z powrotem na front. Dojrzał też duchowo, potrafiąc skupić wokół siebie skłonnych do rozproszenia pilotów gundamów. Po wojnie zaproponował pozbycie się gundamów: zebrano wszystkie poza maszyną Wufeia na satelicie surowcowym i wystrzelono ku Słońcu.

### dic\_pilot\_CATOR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b003`

> Gdy jednak zbuntowała się Armia Mariemai, ruszył odzyskać wystrzelone gundamy. Choć statek ratunkowy miał na spotkanie z satelitą zaledwie pięć sekund, zdołał się na niego dostać. Dostarczył pilotom gundamy, co bardzo pomogło stłumić bunt.

### dic\_pilot\_UFEY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b004`

> Agent operacji Meteor ze skupiska kolonii L5, wysłany na Ziemię. Ma 16 lat. Pochodzi w prostej linii z rodu wojowników sięgającego starożytnych Chin. Wychowano go na wojownika w przekonaniu, że siła to sprawiedliwość. Deptanie słabych przez OZ uważa za zło i wierzy, że sprawiedliwość to pokonać je jeszcze większą siłą. Dlatego gdy przegrał z Treize'em w walce wręcz, poczuł się bezsilny i stracił wolę walki. Odzyskał ją, widząc, jak Sally Po przyznaje się do słabości, a mimo to walczy dalej; uznał, że świat zmienia właśnie wytrwałość w walce. W ostatniej bitwie pokonał Treize'a w rewanżu, lecz zwycięstwo okazało się niejasne, jakby Treize odszedł niepokonany. Po wojnie zwątpił, czy jest sprawiedliwość w świecie, gdzie ludzie w czasach pokoju zapomnieli o walce, a żołnierze nie mają dokąd pójść. W odpowiedzi celowo stał się złem i przyłączył się do Armii Mariemai.

### dic\_pilot\_UFEY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b005`

> W trakcie walki rozmowa z Heerem i widok mieszkańców stawiających opór Armii Mariemai przyniosły mu odpowiedź i zakończył walkę. Potem na zaproszenie Sally Po wstąpił do Preventers.

### dic\_pilot\_RERENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b006`

> Wiceminister spraw zagranicznych Zjednoczonego Państwa Sfery Ziemskiej. Ma 16 lat. Jest też księżniczką Królestwa Sanc, które głosiło pełny pacyfizm; naprawdę nazywa się Relena Peacecraft. Wychowywał ją wiceminister Darlian, a gdy zginął w zamachu, poznała swoje pochodzenie, przejęła pacyfistyczne ideały prawdziwego ojca i odbudowała Królestwo Sanc. Najazd OZ zniszczył królestwo, lecz za sprawą Fundacji Romefeller została przywódczynią całego świata. Choć była pionkiem w politycznych rozgrywkach, niezmiennie wzywała świat do pełnego pacyfizmu, bez broni i przemocy. Ustąpiła, gdy władzę przejął Treize, ale jej niezłomne dążenie do pokoju zyskało szerokie poparcie i po wojnie wciąż ma ogromne wpływy. Dziś, gdy świat się rozbraja, a ideał ojca się spełnia, jako wiceminister kontynuuje dzieło przybranego ojca, Darliana, budując mosty między koloniami a Ziemią. Z powodu jej wpływów Armia Mariemai porwała ją, lecz Relena bez lęku stawiła czoło Mariemai, próbując ją przekonać.

### dic\_pilot\_RERENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b007`

> Determinacja jej i Heera zmieniła myślenie ludzi, którzy zapomnieli o walce, i walnie przyczyniła się do stłumienia buntu Armii Mariemai.

### dic\_pilot\_HILDE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b008`

> Była ochotniczka OZ, mieszkanka kolonii, wówczas w stopniu specjalisty. Wstąpiła do wojska, gdy kolonia przyjęła OZ, szczerze pragnąc bronić domu. Spotkanie z Duem obudziło w niej wątpliwości co do metod OZ i zdezerterowała. Od tamtej pory wspiera Dua zarówno w walce, jak i w handlu złomem. Po wojnie nadal prowadzi z nim złomowisko.

### dic\_pilot\_DOLOSY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00a`

> Wnuczka księcia Dermaila, przewodniczącego Fundacji Romefeller. Pragnie wojny i ma własną estetykę wojny. Jest daleką krewną (siostrzenicą w drugim stopniu) Treize'a i ma bardzo podobne brwi. Przebywa z Releną i otwarcie podziwia jej niezłomny pacyfizm. Pośrednio doprowadziwszy do śmierci dziadka, samotnie wsiada na Librę i dołącza do White Fang. Dowodząc oddziałem mobile dolli za pomocą Zero System, staje na drodze Heerowi i jego towarzyszom. Za upodobaniem do walki skrywa jednak nienawiść do wojny, która odebrała jej ojca. W ostatniej bitwie wyjawia prawdziwe zamiary: chciała pokazać światu okrucieństwo wojny, by ją zakończyć. Po wojnie, spotkawszy Noin przy grobie Treize'a, mówi, że ma dość rozpamiętywania przeszłości, i zwraca się ku przyszłości.

### dic\_pilot\_DOLOSY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00b`

> Podczas buntu Armii Mariemai poderwała do działania zrezygnowanych mieszkańców i kolumną pojazdów zawiozła ich pod siedzibę prezydenta. Jej własny samochód, jak dawniej, lśnił złotym lakierem.

### dic\_pilot\_SALY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00c`

> Członkini Preventers o kryptonimie Water. Była lekarzem wojskowym sił Sojuszu; po spotkaniu z Heerem i jego towarzyszami zainteresowała się pilotami gundamów, a gdy OZ przejęła władzę nad Sferą Ziemską, jako działaczka ruchu oporu zaczęła ich wspierać. Wyrozumiała i cierpliwa, łagodzi tarcia między Preventers a pilotami gundamów. Gdy walczyła w partyzantce w rodzinnym regionie dawnych Chin, swoją dobrocią podniosła na duchu Wufeia, który po klęsce z rąk Treize'a stracił wolę walki. Potrafi też działać zdecydowanie: w czasie wojny wspierała i prowadziła akcje sił anty-OZ, a nawet odzyskała Heavyarmsa i Sandrocka i oddała je pilotom.

### dic\_pilot\_SALY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00d`

> Po buncie Armii Mariemai zwerbowała Wufeia do Preventers, gdzie nadal działa.

### dic\_pilot\_LADY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00e`

> Przywódczyni Preventers o kryptonimie Gold. Kobieta dostojna i zarazem łagodna, biegła we wszystkim, od wojskowości po politykę. Przed wojną była adiutantką Treize'a, przywódcy OZ. Zapatrzona w niego, nie przebierała w środkach i nie znała kompromisów, byle spełnić jego ideały. Posunęła się tak daleko, że by zrozumieć Treize'a, wykształciła w sobie drugą, niemal świętą osobowość. Obie osobowości pozostawały chwiejne, dopóki nie pojęła prawdziwych zamiarów Treize'a; wtedy się ustabilizowały i dziś stapiają się w jedną.

### dic\_pilot\_LADY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00f`

> Podczas buntu Armii Mariemai ruszyła do siedziby prezydenta, by ocalić Mariemaię, jedyną pamiątkę po Treizie. Po wojnie zaopiekowała się dziewczynką.
> 

### dic\_pilot\_ZEKS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b010`

> Pilot Preventers o kryptonimie Wind. Ma 20 lat. Naprawdę nazywa się Milliardo Peacecraft; jest księciem Królestwa Sanc, które głosiło pełny pacyfizm i zostało zniszczone przez Zjednoczony Sojusz Sfery Ziemskiej. W poprzedniej wojnie jako przywódca White Fang wypowiedział wojnę Ziemi. Tak jak Relena przejął ideały ojca i pragnął pokoju, lecz gdy upadło odrodzone przez nią Królestwo Sanc, uznał, że dla trwałego pokoju trzeba pokazać ludzkości bezsens wojny, i podjął próbę zrzucenia Libry. W ostatniej bitwie piloci gundamów pokrzyżowali mu plany, a on sam przegrał pojedynek z Heerem. Zaginął w eksplozji przy niszczeniu napędu Libry, lecz gdy wybuchł bunt Armii Mariemai, wrócił na pole bitwy w Tallgeese III jako Preventer Wind. Dawniej walczył jako pilot OZ, by pomścić ojczyznę, i uważa, że ma krew na rękach, dlatego dla pokoju chce wspierać Relenę z cienia.

### dic\_pilot\_ZEKS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b011`

> Po stłumieniu buntu Armii Mariemai wyruszył z Noin, by wcielić w życie projekt terraformowania wymyślony przez Relenę.

### dic\_pilot\_NOIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b012`

> Członkini Preventers o kryptonimie Fire. Była instruktorką rekrutów OZ. Ukończyła akademię wojskową z drugim wynikiem, tuż za Zechsem, i świetnie sprawdza się jako dowódca i pilotka mobile suita. Kocha Zechsa od czasów akademii; potrafiła dokładnie wyliczyć, jak długo byli rozdzieleni. Gdy jej podopieczni zginęli w ataku Wufeia, poprzysięgła zemstę i została podwładną Zechsa, a gdy on odszedł z OZ, poszła w jego ślady. Zaczęła ochraniać jego młodszą siostrę, Relenę, a kiedy ta wskrzesiła Królestwo Sanc, była jej prawą ręką i w tajemnicy organizowała jego obronę. Po wojnie wstąpiła do Preventers, by strzec pokoju. W bitwie z Armią Mariemai o Brukselę walczyła w Taurusie nie gorzej od pilotów gundamów.

### dic\_pilot\_NOIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b013`

> Po buncie Armii Mariemai, odnalazłszy Zechsa, wyruszyła z nim w kosmos, by realizować projekt terraformowania.

### dic\_pilot\_DEKIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b014`

> Przewodniczący Fundacji Barton i dziadek Mariemai. Szara eminencja: oficjalnie kieruje fundacją, a za kulisami wspierał siły oporu Quinze'a i popychał naprzód operację Meteor. Żądny władzy, uczynił Mariemaię symbolem, wokół którego z byłych żołnierzy White Fang i resztek frakcji Treize'a utworzył Armię Mariemai. Chce mobile suitami opanować rozbrojoną Sferę Ziemską i nią zawładnąć.

### dic\_pilot\_DEKIM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8de0b000`

> Bunt jednak upadł za sprawą pilotów gundamów, Zechsa i reszty Preventers oraz powstania mieszkańców pragnących pokoju. Opętany obsesją Dekim gotów był nawet poświęcić Mariemaię, byle dopiąć celu, lecz zastrzelił go jako zdrajcę jego własny podwładny, młody oficer z dawnej frakcji Treize'a.

### dic\_pilot\_MARYM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b001`

> Dziewczynka, symbol Armii Mariemai. Ma 7 lat. Córka Treize'a i Leii Barton; jej dziadkiem jest Dekim Barton. Dumna, że jest córką Treize'a, przejawia mądrość niezwykłą jak na siedmiolatkę. Wychowana jednak na marionetkę Dekima, przesiąkła jego wypaczonymi poglądami i odnosi się do innych z wyższością.

### dic\_pilot\_MARYM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8de0b002`

> Słowa Releny i postawa pilotów gundamów sprawiają, że w trakcie walk dostrzega swój błąd, a gdy Dekim strzela do Releny, zasłania ją własnym ciałem. Gdy symbol armii traci wolę walki, a faktyczny przywódca, Dekim, ginie, wojna dobiega końca. Mariemaia zamieszkuje potem z Lady Une.

### dic\_pilot\_SIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b003`

> Pilot mobile suita z okrętu Minerva sił ZAFT. Ma 16 lat. Urodził się i wychował w Orbie, gdzie z rodziną wiódł spokojne życie z dala od wojny. Podczas inwazji sił Sojuszu na Orb w poprzedniej wojnie na jego oczach zginęli rodzice i młodsza siostra. Wkrótce, za radą Todaki, wojskowego z Orbu, przeniósł się do PLANT i, przekonany, że by chronić to, co cenne, potrzebna jest siła, wstąpił do ZAFT. Ukończył Akademię z wyróżnieniem i dostał czerwony mundur, znak elitarnego pilota. Może przez tę przeszłość jest żywiołowy, ale bardzo wrażliwy, a jego agresja potrafi wybuchnąć. Przewodniczący Dullindal, dostrzegłszy jego ukryty potencjał, przydziela mu najnowszego Impulse Gundama. Gdy trzy gundamy drugiej generacji zostają skradzione, Shinn rusza je odbić. Z braku doświadczenia początkowo nie odnosi wielkich sukcesów, ale nieustanne walki i bunt przeciw śmierci budzą w nim SEED. Odtąd walczy jak lew i wyrasta na asa. Szanuje Athruna, lecz często wybucha gniewem na jego niezdecydowanie. Po walkach o Stellę uznaje Kirę za śmiertelnego wroga i zestrzeliwuje go razem z Freedom Gundamem. Zestrzeliwuje też Athruna, który odwrócił się od Dullindala; w nagrodę dostaje Destiny Gundama i zostaje członkiem specjalnej formacji FAITH, coraz pewniej stając się zbrojnym ramieniem Dullindala. W ostatniej bitwie Athrun próbuje go przekonać, lecz Shinn uparcie walczy dalej. W zamęcie omal nie atakuje nawet Lunamarii, z którą łączyła go bliska więź, lecz w ostatniej chwili Athrun go zestrzeliwuje. W majakach Shinn znów spotyka Stellę, a budzi się z głową na kolanach Lunamarii i ze łzami w oczach przyjmuje koniec wojny. W epilogu “Final Plus” odwiedza pomnik ofiar w Orbie i po raz drugi staje twarzą w twarz z Kirą. Tym razem obaj podają sobie ręce i ślubują razem strzec pokoju.

### dic\_pilot\_RUNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b005`

> Pilotka mobile suita z okrętu Minerva sił ZAFT. Ma 17 lat. Razem z Shinnem i Reyem ukończyła Akademię z wyróżnieniem i należy do elity w czerwonych mundurach. Walczy głównie w Gunner Zaku Warriorze pomalowanym na czerwono, w jej osobistych barwach. Razem z młodszą siostrą, Meyrin, interesuje się Athrunem, bohaterem poprzedniej wojny, i obie próbują go zdobyć. Gdy jednak Athrun, nie ufając Dullindalowi, dezerteruje, a Meyrin ucieka razem z nim, Lunamaria przeżywa wstrząs, a zaraz potem kolejny, gdy dowiaduje się, że oboje zostali zestrzeleni. Od tej pory ona i Shinn wspierają się, lecząc nawzajem rany, i szybko zbliżają się do siebie, aż rodzi się między nimi uczucie. W ostatniej bitwie próbuje powstrzymać Shinna, który jak opętany chce walczyć dalej, a on ją atakuje. Mimo to po jego porażce z Athrunem z oddaniem się nim opiekuje. W epilogu “Final Plus” odwiedza z Shinnem pomnik ofiar w Orbie. Patrzy, jak Shinn godzi się z Kirą i Athrunem i płacze, a potem razem ruszają ku nowej przyszłości.

### dic\_pilot\_ASRAN\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b007`

> Jeden z tych, którzy doprowadzili do końca poprzedniej wojny; w PLANT nie ma nikogo, kto nie znałby tego bohatera. Ma 18 lat. Po wojnie zbiegł do Orbu i był ochroniarzem ukochanej, Cagalli. Gdy znów wybuchła wojna, gorzko odczuwał własną bezsilność. Wtedy Dullindal zaproponował mu powrót; Athrun pożegnał się z Cagalli, wrócił do ZAFT i został członkiem specjalnej formacji FAITH. W powierzonym mu Savior Gundamie walczy jako członek załogi Minervy, lecz różnica poglądów stawia go przeciw najlepszemu przyjacielowi, Kirze. Z początku podzielał wizję Dullindala, ale podejrzenia o zamach na Lacus, wykorzystywanie fałszywej Lacus, Meer, i rozkaz ataku na Archangel, który dążył do tego samego, budziły w nim coraz większą nieufność. W końcu zdezerterował z ZAFT, znów stanął u boku Kiry i przeciwstawił się Planowi Destiny Dullindala. W ostatniej bitwie próbuje przekonać Shinna, wiernego Dullindalowi, by przestał walczyć, ale bez skutku. Gdy oszalały Shinn chce zaatakować nawet Lunamarię, która próbuje go powstrzymać, Athrun wchodzi w tryb SEED i go zestrzeliwuje.

### dic\_pilot\_KIRA\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b009`

> Członek załogi Archangela i pilot Strike Freedom Gundama. Ma 18 lat. Owoc modyfikacji genetycznych i licznych eksperymentów, rzec można “Superkoordynator”. W poprzedniej wojnie jako trzecia siła walczył zarówno z siłami Sojuszu, jak i z PLANT, i doprowadził do końca wojny. Potem zbiegł do Orbu razem z Murrue, towarzyszką broni, i ukochaną, Lacus, i żył tam w odosobnieniu z dala od walk. Spadek Junius Seven i starcie z oddziałem, który przyszedł zabić Lacus, uświadomiły mu jednak, że trzeba powstrzymać szerzący się pożar wojny. W końcu wraz z dawnymi towarzyszami podjął nową walkę. W walce nie ma sobie równych, lecz zbyt łagodne serce brzydzi się walką i zabijaniem, więc stara się niszczyć tylko broń i kamery wroga, nie zabijając pilotów. Ta dobroć obraca się przeciw niemu: raz przegrywa z desperackim atakiem Shinna. Wraca jednak z nowymi skrzydłami, Strike Freedom Gundamem. Gdy Dullindal ujawnia Plan Destiny, a Cagalli wraca na stanowisko przewodniczącej, Kira oficjalnie wstępuje do armii Orbu. W ostatniej bitwie rozprawia się z Reyem, spadkobiercą fatum Raua Le Creuseta, przenika do Messiaha i staje oko w oko z Dullindalem, pokazując, że gotów jest walczyć dalej w pogrążonym w chaosie świecie.

### dic\_pilot\_KAGA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00b`

> Przewodnicząca Zjednoczonych Emiratów Orbu. Ma 18 lat. Przejęła ideały zmarłego ojca, Uzumiego, poprzedniego przewodniczącego, i chce prowadzić kraj i świat ku pokojowi. Młodość, brak doświadczenia i knowania Seiranów sprawiają jednak, że nie potrafi zjednoczyć kraju i boleśnie odczuwa własną słabość. Gdy Athrun, jej ukochany od poprzedniej wojny, opuszcza Orb, dostaje od niego pierścionek. Później jednak, by zjednoczyć kraj, z konieczności decyduje się poślubić Yunę i zrywa z uczuciem. Ślub zostaje unieważniony, gdy w trakcie ceremonii porywa ją jej brat bliźniak, Kira, we Freedom Gundamie. Gdy Seiranowie, przejąwszy władzę, wchodzą w sojusz z Sojuszem Ziemskim i ruszają wojskami, próbuje ich powstrzymać, ale bezskutecznie. Widok żołnierzy Orbu gotowych na śmierć odnawia jednak jej postanowienie, by bronić ojczyzny. Gdy Orbowi grozi kolejne niebezpieczeństwo, ratuje go w Akatsuki, mobile suicie, który zostawił jej Uzumi. Odzyskawszy urząd przewodniczącej, jednoczy kraj i staje przeciw Dullindalowi i jego Planowi Destiny.

### dic\_pilot\_RAKUS\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00d`

> Niegdyś idolka zwana “pieśniarką PLANT”. Ma 18 lat. Jej obecność i charyzma są ogromne: w poprzedniej wojnie wskazała drogę Kirze i Athrunowi i skupiła ludzi o podobnych ideałach, co walnie przyczyniło się do końca wojny. Potem udała się do Orbu z towarzyszami broni, Waltfeldem i Murrue, oraz ukochanym, Kirą. Żyła tam cicho z wielebnym Malchiem, przybraną matką Kiry, Calidą, i sierotami, lecz krótki spokój przerwał zamach na jej życie. Pojawienie się fałszywej Lacus, Meer, pogłębia jej podejrzenia wobec Dullindala. Postanawia wrócić na scenę i wsiada z Kirą na Archangel. Potem sama wyrusza w kosmos, by walczyć, a dowiedziawszy się o Planie Destiny, ogłasza, że mu się przeciwstawi. Gdy przygotowuje nowe maszyny dla Kiry i Athruna, sama pilotuje Infinite Justice Gundama, by dostarczyć go Athrunowi. Energicznie zbiera siły z różnych stron i staje się duchowym i ideowym oparciem wszystkich, którzy sprzeciwiają się Dullindalowi. W ostatniej bitwie, jak w poprzedniej wojnie, dowodzi z pokładu Eternala i jest sztandarem pierwszej linii. Po walce z Dullindalem nie odstępuje Kiry ani prywatnie, ani publicznie.

### dic\_pilot\_BALT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00f`

> Kapitan szybkiego okrętu bojowego Eternal. Ma 32 lata. Służył w ZAFT, gdzie jako “Pustynny Tygrys” budził postrach. W poprzedniej wojnie zdezerterował, by pomóc Lacus i jej towarzyszom, i przyczynił się do końca wojny. Potem zbiegł do Orbu razem z Kirą, Murrue i Lacus i, delektując się ulubioną kawą, cieszył się chwilą pokoju. Gdy myślał już o przenosinach do PLANT, odparł atak oddziału specjalnego, który chciał zabić Lacus. To skłoniło go, by znów jako trzecia siła stawić czoło wojnie. Po wylocie Archangela wspiera Murrue niczym zastępca kapitana, a w razie potrzeby rusza do walki w Murasame w osobistych barwach, dowodząc, że nic nie stracił z dawnej formy. Gdy Lacus wyrusza sprawdzić sytuację w PLANT, leci z nią w kosmos jako ochrona. Gdy Eternal wraca do akcji, Waltfeld, jak w poprzedniej wojnie, zasiada w fotelu kapitana. Gdy Eternal musiał walczyć sam, wyruszał nawet do boju w Gaia Gundamie, następcy swojej dawnej maszyny.

### dic\_pilot\_MEYRIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b011`

> Operatorka szybkiego okrętu bojowego Eternal. Ma 16 lat. Służyła w ZAFT na Minervie, ale pomogła Athrunowi w ucieczce z ZAFT i została w armii Orbu. Młodsza siostra Lunamarii; choć czasem rywalizują, bardzo się lubią.

### dic\_pilot\_KISA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b000`

> Oficer armii lądowej Orbu w stopniu pułkownika. Był bezpośrednim podwładnym Uzumiego, poprzedniego przewodniczącego Orbu, a w poprzedniej wojnie ochraniał Cagalli. Po śmierci Uzumiego czuwa nad nią jako opiekun. Gdy Sojusz Ziemski i Orb zawarły przymierze, przeniknął do sił Sojuszu, by śledzić ich ruchy. Dowiedziawszy się o ucieczce Athruna i Meyrin, uratował ich po zestrzeleniu i zabrał na Archangel. Gdy Cagalli, wiedząc o zagrożeniu Orbu, uparła się walczyć, powierzył jej Akatsuki zostawionego przez Uzumiego, a sam ruszył do boju w Murasame.

### dic\_pilot\_IZAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b002`

> Dowódca oddziału Jule sił ZAFT. Ma 19 lat. W samej końcówce poprzedniej wojny pomógł Archangelowi i Eternalowi i przyczynił się do jej zakończenia. Po wojnie dzięki Dullindalowi wrócił do ZAFT i mimo młodego wieku, z racji talentu, objął dowództwo oddziału. Doświadczenie bojowe czyni z niego pierwszorzędnego dowódcę i pilota. Działa na wielu frontach w kosmosie: z pomocą Minervy próbował powstrzymać spadek Junius Seven, bronił PLANT przed jednostronnym atakiem sił Sojuszu, a gdy PLANT stały się celem Requiem, próbował (bez powodzenia) zniszczyć stację odchylającą wiązkę. Gdy znów spotyka Athruna, usilnie namawia go do powrotu do służby, co pokazuje, że dojrzał i porzucił dawną drobiazgową rywalizację. W ostatniej bitwie Orbu z PLANT znów rozdarty jest między obowiązkiem a przyjaciółmi po drugiej stronie, lecz buntuje się przeciw Dullindalowi, który sięga po broń masowej zagłady, Requiem i Neo Genesis, i ponownie staje u boku Kiry.

### dic\_pilot\_DEAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b004`

> Żołnierz ZAFT, prawa ręka w oddziale Jule, którym dowodzi jego najlepszy przyjaciel, Yzak. Ma 19 lat. W poprzedniej wojnie również służył w ZAFT, ale trafił do niewoli, wylądował na Archangelu i walczył u boku jego załogi. Po wojnie, w której jako trzecia siła pomógł ją zakończyć, wrócił do ZAFT, lecz za dawne winy nosi zwykły mundur szeregowca zamiast czerwonego, znaku elity. Jako pilot wciąż jest świetny, a dojrzał na tyle, że można na nim polegać. Co do Miriallii, za którą szalał, ona sama potwierdza, że “dała mu kosza”.

### dic\_pilot\_JBRL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b006`

> Członek Logosu, kompleksu wojskowo-przemysłowego, i nowy przywódca Blue Cosmos, dążącego do wytępienia Koordynatorów. Ma 31 lat. Przesadnie hołduje arystokratycznym gustom i wierzy w wyższość wybranych. Zwykle chłodny i uprzejmy, gdy coś idzie nie po jego myśli, natychmiast wpada w szał i wyżywa się na przedmiotach, ukazując podłą naturę. Gdy dowiaduje się, że zrzucenie Junius Seven to dzieło grupy Koordynatorów, pod tym pretekstem jednostronnie wypowiada wojnę PLANT, znów pogrążając świat w chaosie. Dullindal ujawnia jednak istnienie jego i Logosu, a cała wrogość ludu skupia się na nim. Przegrywa bitwę za bitwą i ucieka, poświęcając wszystkich poza sobą, członków Logosu i oficerów sił Sojuszu. Pokonany nawet w księżycowej bazie Daedalus, ostatniej twierdzy, wciąż próbuje uciec, lecz jego Girty Lue zostaje trafiony prosto w mostek, a śmierć kończy jego ucieczkę.

### dic\_pilot\_SLETA\_G\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b008`

> Pilotka Gundama Aerial. Przeniosła się z rodzinnego Merkurego na 2. rok wydziału pilotażu Szkoły Technicznej Asticassia. Wychowana na Merkurym, marzy o świecie poza nim, a plany na życie w szkole spisała na “liście rzeczy do zrobienia”. Szczera, ale zamknięta w sobie; nie umie rozmawiać z ludźmi i z tremy plącze się w słowach. Bezgranicznie ufa matce, Prosperze, a jej nauka, “Uciekniesz, zyskasz jedno. Pójdziesz naprzód, zyskasz dwa”, jest dla niej drogowskazem. Pierwszego dnia w szkole poznaje Miorine Rembran, przez co musi stanąć do pojedynku z Guelem Jeturkiem, Holderem, czyli najlepszym pilotem szkoły.

### dic\_pilot\_SLETA\_G\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b009`

> Zwycięstwo czyni ją Holderem i zarazem pierwszą kandydatką na narzeczonego Miorine. Wkrótce jednak pojawia się podejrzenie, że Aerial to GUND-ARM, i Suletta zostaje wciągnięta w zamieszanie, które ogarnia nie tylko szkołę, ale całą Grupę Benerit. W pojedynkach z pilotami Trzech Filii Grupy Benerit wyciska z Aeriala wszystko, co najlepsze, wygrywa i broni pozycji kandydatki na “pana młodego” Miorine.

### dic\_pilot\_MIOLN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00a`

> Jedyna córka Dellinga Rembrana, prezesa Grupy Benerit. Uczennica 2. roku wydziału strategii zarządzania Szkoły Technicznej Asticassia, najlepsza na swoim wydziale. Ze względu na urodę i pozycję ojca niektórzy przezywają ją “księżniczką”. Buntuje się przeciw ojcu, który decyduje o wszystkim sam, i marzy o ucieczce ze szkoły na Ziemię. Zgodnie z regułą ustaloną przez ojca, gdy skończy 17 lat, ma poślubić tego, kto będzie wtedy Holderem. Na terenie szkoły uprawia w szklarni pomidory odmiany wyhodowanej przez zmarłą matkę; to miejsce jest jej ostoją.

### dic\_pilot\_MIOLN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00b`

> Chce wykorzystać Sulettę, która pokonała Guela i została Holderem, by wymknąć się z reguł ojca, lecz szczerość Suletty stopniowo otwiera jej serce. Gdy Suletta wpada w tarapaty z powodu Gundama Aerial, Miorine proponuje założenie spółki GUND-ARM S.A. i, korzystając z zaufania, jakim cieszy się jej ojciec, zbiera fundusze. Potem jako prezes, wciągając w to mieszkańców akademika Ziemian, w pocie czoła prowadzi GUND-ARM S.A.

### dic\_pilot\_GUERU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00c`

> Uczeń 3. roku wydziału pilotażu Szkoły Technicznej Asticassia i as akademika Jeturk. Syn Vima Jeturka, prezesa Jeturk Heavy Machinery, jednej z Trzech Filii Grupy Benerit. Jako Holder, najlepszy pilot szkoły, przewodniczy Komitetowi Pojedynków. Gwałtowny i przekonany o swojej sile, często zachowuje się jak tyran. Marzy, by zostać asem oddziału Dominicus, sił specjalnych podległych bezpośrednio Cathedrze.

### dic\_pilot\_GUERU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00d`

> Przegrywa pojedynek z Sulettą i traci tytuł Holdera. Przegrywa też rewanż, lecz gdy ona docenia jego umiejętności, oświadcza się jej. Kolejne porażki ściągają na niego gniew ojca, Vima, a po przegranym pojedynku z Elanem Ceresem zostaje wyrzucony z akademika Jeturk.

### dic\_pilot\_ERAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00e`

> Pilot wystawiany przez Peil Technologies, jedną z Trzech Filii Grupy Benerit. Uczeń 3. roku wydziału pilotażu Szkoły Technicznej Asticassia, przewodzi akademikowi Peil i zasiada w Komitecie Pojedynków. Nie interesuje się innymi i nikomu nie otwiera serca, więc część uczniów nazywa go “Lodowym Księciem”.

### dic\_pilot\_ERAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b000`

> Naprawdę jest sobowtórem, któremu operacjami plastycznymi nadano wygląd prawdziwego Elana Ceresa; w Peil nazywają go “Wzmocnionym nr 4”. Jego ciało zmodyfikowano, by mógł pilotować GUND-ARM, i interesuje się Sulettą, sądząc, że spotkał ją ten sam los. Gdy jednak odkrywa, że jest inaczej, wyzywa ją na pojedynek. Przegrywa, ale przypomina sobie szczęśliwą przeszłość, której, jak sądził, nie miał. Jego ciało jest już jednak u kresu sił; nie może dłużej pełnić swojej roli i zostaje od niej odsunięty. Jego miejsce zajmuje “Wzmocniony nr 5”.

### dic\_pilot\_SYADIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b001`

> Przybrany syn Sariusa Zenellego, prezesa Grassley Defense Systems, jednej z Trzech Filii Grupy Benerit. Uczeń 3. roku wydziału pilotażu Szkoły Technicznej Asticassia i członek Komitetu Pojedynków. Choć wciąż się uczy, ma już na koncie wiele sukcesów w interesach i uchodzi za kandydata na przyszłego członka zarządu grupy. Otwarty i niefrasobliwy, w ukryciu jest ambitnym intrygantem.

### dic\_pilot\_SYADIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b002`

> Próbuje negocjować z Miorine przejęcie założonej przez nią spółki GUND-ARM S.A., lecz ona odmawia. Gdy Miorine wyzywa go na pojedynek, by rozstrzygnąć sprawę, sam siada za sterami mobile suita i prowadzi akademik Grassley do walki drużynowej z akademikiem Ziemian. Dzięki zgraniu maszyn zyskuje przewagę, lecz przegrywa z taktyką Miorine i wysiłkiem Suletty i reszty. Skrywane pragnienie, by chronić Miorine, nie trafia do jej serca.

### dic\_pilot\_NKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b003`

> Uczennica 2. roku wydziału mechaniki, mieszkanka akademika Ziemian. Chuchu mówi na nią “siostra Nika”. Łagodna i ciepła, zagadnęła Sulettę, gdy ta przeniosła się do szkoły, i dzięki niej Suletta trafiła do akademika Ziemian. Uzdolniona mechaniczka; to ona przerobiła Demi Trainera, którym lata Chuchu.

### dic\_pilot\_NKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b004`

> Gdy Suletta toczy pojedynek w przestrzeni poza Frontem, montuje na Aerialu zewnętrzny moduł napędowy. Ma jednak oblicze, którego nie znają mieszkańcy akademika Ziemian, i potajemnie utrzymuje kontakt z Shaddiqiem.

### dic\_pilot\_CHUCHU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b005`

> Uczennica 1. roku wydziału pilotażu, mieszkanka akademika Ziemian. Przyjaciele mówią na nią “Chuchu”. Z głębi serca nienawidzi Spacjan, którzy dyskryminują Ziemian. Ma charakterek i często wszczyna w szkole bójki. Lata w Demi Trainerze przerobionym specjalnie dla niej przez Nikę.

### dic\_pilot\_CHUCHU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b006`

> Z początku trzymała się z dala od Suletty, Spacjanki, lecz gdy zrozumiała, że ona także nosi w sercu rodzinne strony, stopniowo się do niej przekonała. Ponieważ zamieszkała w akademiku wcześniej, każe Suletcie traktować się jak starszą koleżankę. Gdy Miorine zakładała GUND-ARM S.A., Chuchu ostro sprzeciwiała się sprzedaży broni, ale gdy firma postawiła na medycynę, zaczęła pomagać, myśląc także o swoich rodzinnych stronach.

### dic\_pilot\_PROSPE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b007`

> Prezes Shin Sei Development Corporation i główna konstruktorka Gundama Aerial. Matka Suletty, która ufa jej bezgranicznie. Prawą rękę, utraconą w wypadku, zastępuje jej proteza oparta na technice GUND, a dla wsparcia ciała nosi specjalny hełm.

### dic\_pilot\_PROSPE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b008`

> Przeżyła incydent Vanadis 21 lat temu, lecz jej losy od tamtej pory i cele, do których dąży, pozostają tajemnicą.

### dic\_pilot\_DERING\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b009`

> Prezes Grupy Benerit i ojciec Miorine. Stoi też na czele Cathedry, organu nadzorczego, i przewodniczy radzie Szkoły Technicznej Asticassia. Surowy i niezwykle stanowczy, wręcz zadufany w sobie. Ma w grupie ogromną władzę, ale i wielu wrogów. Wobec córki jest równie surowy, a ich relacje są lodowate. 21 lat temu był kluczową postacią incydentu Vanadis; to on zakazał używania GUND Format.

### dic\_pilot\_DERING\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00a`

> Gdy Miorine zakłada GUND-ARM S.A., wytyka jej naiwność, ale zarazem pomaga zebrać inwestorów.

### dic\_pilot\_SALIUS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00b`

> Prezes Grassley Defense Systems, jednej z Trzech Filii Grupy Benerit. W podeszłym wieku, ale bystry i przenikliwy. Wprowadził do firmy przybranego syna, Shaddiqa.

### dic\_pilot\_SALIUS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00c`

> Podejrzliwie patrzy na Dellinga, który zgodził się na GUND-ARM S.A. i nie kazał zniszczyć Aeriala.

### dic\_pilot\_VIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00d`

> Prezes Jeturk Heavy Machinery, jednej z Trzech Filii Grupy Benerit, i ojciec Guela. Ambitny biznesmen, twardą ręką trzyma firmę Jeturk w ryzach. Dla syna jest wyjątkowo surowy.

### dic\_pilot\_VIM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00e`

> Planował zamach na Dellinga, ale gdy Guel przegrał pojedynek i stracił tytuł Holdera, musiał zrezygnować. Potem wszelkimi sposobami próbował zapewnić synowi zwycięstwa, lecz Guel znów przegrał z Sulettą, a potem, wbrew woli ojca stanąwszy do pojedynku, także z Elanem. Wtedy Vim wyrzucił go z akademika Jeturk.

### dic\_pilot\_NEWGEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00f`

> Jedna z czterech współprezesek Peil Technologies, jednej z Trzech Filii Grupy Benerit. Cztery prezeski kierują Peil kolegialnie.

### dic\_pilot\_NEWGEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b010`

> Wraz z pozostałą trójką potajemnie zleca budowę GUND-ARM i tworzy Wzmocnionych, którzy mają je pilotować. Na przyjęciu inkubacyjnym Grupy Benerit oskarża Aeriala o to, że jest GUND-ARM, i próbuje doprowadzić do jego zniszczenia.

### dic\_pilot\_KAL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b011`

> Jedna z czterech współprezesek Peil Technologies, jednej z Trzech Filii Grupy Benerit. Cztery prezeski kierują Peil kolegialnie.

### dic\_pilot\_KAL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b012`

> Wraz z pozostałą trójką potajemnie zleca budowę GUND-ARM i tworzy Wzmocnionych, którzy mają je pilotować. Na przyjęciu inkubacyjnym Grupy Benerit oskarża Aeriala o to, że jest GUND-ARM, i próbuje doprowadzić do jego zniszczenia.

### dic\_pilot\_NEBORA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b013`

> Jedna z czterech współprezesek Peil Technologies, jednej z Trzech Filii Grupy Benerit. Cztery prezeski kierują Peil kolegialnie.

### dic\_pilot\_NEBORA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b000`

> Wraz z pozostałą trójką potajemnie zleca budowę GUND-ARM i tworzy Wzmocnionych, którzy mają je pilotować. Na przyjęciu inkubacyjnym Grupy Benerit oskarża Aeriala o to, że jest GUND-ARM, i próbuje doprowadzić do jego zniszczenia.

### dic\_pilot\_GOLNE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b001`

> Jedna z czterech współprezesek Peil Technologies, jednej z Trzech Filii Grupy Benerit. Cztery prezeski kierują Peil kolegialnie.

### dic\_pilot\_GOLNE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b002`

> Wraz z pozostałą trójką potajemnie zleca budowę GUND-ARM i tworzy Wzmocnionych, którzy mają je pilotować. Na przyjęciu inkubacyjnym Grupy Benerit oskarża Aeriala o to, że jest GUND-ARM, i próbuje doprowadzić do jego zniszczenia.

### dic\_pilot\_RAUDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b005`

> Wicestarosta akademika Jeturk, uczeń 3. roku wydziału pilotażu. Chodzi na ten sam rok co Guel, ale jest jego młodszym bratem przyrodnim. Chłodny i rozważny, a zarazem bardzo przywiązany do brata.

### dic\_pilot\_RAUDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b006`

> Po wyrzuceniu Guela przejmuje akademik jako starosta.

### dic\_pilot\_FELCY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b007`

> Uczennica 2. roku wydziału pilotażu z akademika Jeturk. Podziwia Guela jako pilota. Lubi docinać innym i łatwo daje się ponieść. Zwykle chodzi razem z Petrą.

### dic\_pilot\_FELCY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b008`

> W drugim pojedynku Guela z Sulettą, by pomóc mu wygrać, razem z Petrą uruchamia system sterowania i zrasza wodą strefę testów taktycznych.

### dic\_pilot\_PETRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b009`

> Uczennica 2. roku wydziału mechaniki z akademika Jeturk. Wpatrzona w Guela, prawie nie rozstaje się z Felsi. Sprawia wrażenie chłodnej intelektualistki, ale często wtóruje docinkom Felsi.

### dic\_pilot\_PETRA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00a`

> W drugim pojedynku Guela z Sulettą, by pomóc mu wygrać, razem z Felsi uruchamia system sterowania i zrasza wodą strefę testów taktycznych.

### dic\_pilot\_SSRIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00b`

> Uczennica 2. roku wydziału strategii zarządzania z akademika Burion. Członkini Komitetu Pojedynków. Złośliwa i wyszczekana.

### dic\_pilot\_ROUJI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00d`

> Uczeń 1. roku wydziału mechaniki z akademika Burion. Razem z Secelią zasiada w Komitecie Pojedynków. Cichy, często nosi przy sobie przerobionego przez siebie Haro.

### dic\_pilot\_MALTN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00f`

> Starosta akademika Ziemian, uczeń 3. roku wydziału strategii zarządzania. Niezdecydowany, często dzieli się obawami. Barwne osobowości mieszkańców akademika nieraz wodzą go za nos, ale choć bywa zagubiony, z całych sił stara się wypełniać obowiązki starosty.

### dic\_pilot\_MALTN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b010`

> W pojedynku z akademikiem Grassley wystąpił jako pilot, ale został unieszkodliwiony, zanim zdążył cokolwiek zrobić.

### dic\_pilot\_NUNO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b011`

> Uczeń 2. roku wydziału mechaniki z akademika Ziemian. Zna się na oprogramowaniu. Sierota wojenny, a mimo to z chłodnym dystansem patrzy na położenie Ziemian. Z Ojelem są kumplami od psot; obaj namiętnie obstawiają wyniki pojedynków.

### dic\_pilot\_NUNO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b012`

> Przez pewien czas był skłócony z Ojelem w sprawie kierunku rozwoju GUND-ARM S.A., ale pogodzili się, kręcąc film reklamowy firmy.

### dic\_pilot\_OJRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b013`

> Uczeń 2. roku wydziału mechaniki z akademika Ziemian. Pogodny, poprawia nastrój całemu akademikowi. Razem z kumplem, Nunem, przepuszcza pieniądze na utrzymanie akademika na zakłady o wyniki pojedynków.

### dic\_pilot\_OJRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b014`

> Przez pewien czas był skłócony z Nunem w sprawie kierunku rozwoju GUND-ARM S.A., ale pogodzili się, kręcąc film reklamowy firmy. W pojedynku z akademikiem Grassley wystąpił jako pilot, ale został unieszkodliwiony, zanim zdążył cokolwiek zrobić.

### dic\_pilot\_TIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b015`

> Uczeń 3. roku wydziału mechaniki z akademika Ziemian. Spokojny i małomówny, cichy filar całego akademika.

### dic\_pilot\_TIL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b016`

> Ma wyczucie estetyki; na prośbę Miorine zaprojektował logo GUND-ARM S.A. W pojedynku z akademikiem Grassley wystąpił jako pilot, a Henao przyznała, że jak na mechanika ma dobry instynkt.

### dic\_pilot\_RRKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b017`

> Uczennica 1. roku wydziału strategii zarządzania z akademika Ziemian. Pogodna i przystępna, ma powodzenie u chłopców. Uwielbia plotki o miłostkach.

### dic\_pilot\_RRKE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b018`

> W pojedynku z akademikiem Grassley wystąpiła jako pilotka, bo Renee czepiła się jej o chłopaka.

### dic\_pilot\_ALYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b019`

> Uczennica 3. roku wydziału mechaniki z akademika Ziemian. Chodzi własnymi ścieżkami, kocha wróżby i zwierzęta gospodarskie. Hoduje w akademiku kozy, jaki, kury i inne zwierzęta przywiezione z rodzinnych stron.

### dic\_pilot\_ALYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01a`

> W pojedynku z akademikiem Grassley była operatorką.

### dic\_pilot\_BELME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01d`

> Badaczka techniczna w Peil Technologies. Brała udział w budowie Gundama Pharact i dba o stan fizyczny Elana. Przeżyła incydent Vanadis 21 lat temu, kiedy pracowała jako młodsza koleżanka Prospery.

### dic\_pilot\_BELME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01e`

> Wierzy w ideały techniki GUND, ale współpracuje z Peil, by ratować własną skórę, i w głębi duszy źle się z tym czuje. Odkąd GUND-ARM S.A. postawiła na medycynę GUND, wspiera Miorine i jej towarzyszy.

### dic\_pilot\_SABINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01f`

> Uczennica 3. roku wydziału pilotażu z akademika Grassley. Prawa ręka Shaddiqa, pomaga mu w sprawach szkolnych i pozaszkolnych. Opanowana, o dostojnej aparycji.

### dic\_pilot\_RENE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b000`

> Uczennica 2. roku wydziału pilotażu z akademika Grassley, jedna z pięciu dziewcząt wspierających Shaddiqa. Wesoła, ale przebiegła; inaczej zachowuje się przy chłopcach, a inaczej przy dziewczynach. W szkole ma mnóstwo wielbicieli.

### dic\_pilot\_RENE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b001`

> W pojedynku drużynowym z akademikiem Ziemian oskarżyła Lilique, że ośmieszyła jednego z jej adoratorów.

### dic\_pilot\_ILIJA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b002`

> Uczennica 2. roku wydziału pilotażu z akademika Grassley, jedna z pięciu dziewcząt wspierających Shaddiqa. Nieśmiała i lękliwa, zawsze tuli pluszaka. Szczególnie przyjaźni się z Maisie.

### dic\_pilot\_MAYG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b004`

> Uczennica 2. roku wydziału pilotażu z akademika Grassley, jedna z pięciu dziewcząt wspierających Shaddiqa. Niepoprawna optymistka. Szczególnie przyjaźni się z Ireeshą.

### dic\_pilot\_EONA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b006`

> Uczennica 3. roku wydziału pilotażu z akademika Grassley, jedna z pięciu dziewcząt wspierających Shaddiqa. Małomówna i tajemnicza, stale wyostrza umysł i zdaje się na szósty zmysł.

### dic\_pilot\_SHOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b008`

> Młody Japończyk, pilot Dunbine'a i Billbine'a. Ma 18 lat. Marzył o karierze w motocrossie, lecz E Ferario Silky Mau przywołała go do Byston Well, gdzie został pilotem Dunbine'a. Z początku, porwany biegiem wydarzeń, stał po stronie Drake'a, lecz po spotkaniu z Marvel z własnej woli przeszedł do jego przeciwników. Dzięki silnej mocy aury szybko stał się filarem sił przeciwnych Drake'owi, a sojusznicy zaczęli polegać na nim jako na świętym wojowniku. Często go to krępowało, lecz z czasem przyjął swoją rolę i wypełniał ją jako wojownik i prawa ręka Nie. Jego ojciec jest konsultantem biznesowym, a matka krytykiem oświatowym; gdy pierwszy raz wrócił do Górnego Świata, rodzice nie zaakceptowali jego drogi i rozstali się z nim. Odtąd Show nie tęskni już za Górnym Światem i uważa Byston Well za swoje miejsce. Gdy wszystkie maszyny aury trafiają do Górnego Świata, robi wszystko, by zatrzymać wojnę z Byston Well, która przelała się na powierzchnię.

### dic\_pilot\_SHOU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b009`

> W ostatniej bitwie stoczył pojedynek z odwiecznym wrogiem, Bernem, w którym obaj niemal się pozabijali, i za sprawą oczyszczenia przez Cielę zniknął z Górnego Świata.

### dic\_pilot\_MARBL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00a`

> Amerykanka, pilotka Dunbine'a. Ma 18 lat. Do Byston Well przywołała ją E Ferario Knuckle Bee. Trafiła tam przed Show; popiera przeciwników Drake'a, a że pociąga ją Nie, pomaga rodowi Givenów. Uświadamia Show zło Drake'a i zyskuje w nim sojusznika, a potem odwzajemnia jego uczucia; oboje nawzajem wzmacniają swoją moc aury. Bystra, zgłębia myśl Wschodu, choć potrafi też okazać gwałtowne uczucia. Pilotowała kolejno najnowsze Aura Battlery przeciwników Drake'a: Dana O'Shee, Bozune i Botune, a w końcu przejęła od Show Dunbine'a.

### dic\_pilot\_MARBL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00b`

> W ostatniej bitwie wraz z Show zestrzeliwuje Spriggana Shota, lecz Bern w Gallabie śmiertelnie ją rani. Umiera, kierując Show z powrotem do walki.

### dic\_pilot\_CHAM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00c`

> Mi Ferario pomagająca rodowi Givenów. Z początku podkochiwała się w Nie Givenie, a Show, który stał przy Drake'u, miała niemal za wroga, lecz wspólne przygody uczyniły go jej ważnym partnerem. W walce towarzyszy Show, a ponadto przydaje się w zwiadzie i siejąc zamęt u wroga. Zna się też na pracach domowych; swój strój bojowy uszyła sama.

### dic\_pilot\_CHAM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00d`

> Po ostatniej bitwie zostaje sama w Górnym Świecie; opowiada ludziom o walkach Show i reszty, po czym znika.

### dic\_pilot\_NEE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00e`

> Syn Romna Givena, lokalnego władcy w Krainie Ah. Ma 23 lata. Kapitan okrętu aury Zelerna i przywódca grupy Show. W walce zwykle dowodzi, ale w razie potrzeby sam siada za sterami Aura Battlera. Walczył z Show, Marvel i resztą, by pokrzyżować plany Drake'a, pragnącego zawładnąć Byston Well. Z początku, zaślepiony uczuciem do córki Drake'a, Riml, często ścierał się z Show i resztą, lecz walki bardzo go odmieniły.

### dic\_pilot\_NEE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00f`

> W ostatniej bitwie spełnił swoje pragnienie, zabijając Drake'a i jego żonę, Louser, która zamordowała Riml, lecz zaraz potem sam poległ.

### dic\_pilot\_KEEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b010`

> Córka rodziny Kissów, wasali rodu Givenów. Ma 16 lat. Prawa i szczera. Idzie za Nie, w którym się kocha, i wstępuje na pokład okrętu aury Zelerna. W trakcie wojny musi walczyć z własnym ojcem, który przystał do armii Drake'a, by chronić ród; ta próba hartuje jej wolę. Nie chce być ciężarem, więc wspiera Show i resztę w Aura Battlerze i wyrasta na prawdziwą wojowniczkę.

### dic\_pilot\_KEEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b011`

> Ginie w ostatniej bitwie od ataku Bubury pilotowanej przez Musiy Poe.

### dic\_pilot\_SHIRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b012`

> Królowa Krainy Na. Ma 17 lat. Szlachetna moc aury przyniosła jej miano Świętej Dziewicy; zawsze zachowuje królewską godność i wdzięk. Poczucie misji i odpowiedzialności skłoniło ją do budowy Gran-Garana i stanęła na czele przeciwników Drake'a. Show, który uratował ją z opresji, uznała za prawdziwego świętego wojownika i powierzyła mu najnowszego Aura Battlera, Billbine'a. Martwi ją jednak, jak maszyny aury zmieniają całe Byston Well, także ona sama odpowiada siłą na siłę, więc po pokonaniu Drake'a postanowiła zniszczyć wszystkie maszyny aury. Przeniesiona do Górnego Świata walczy z armią Drake'a, a zarazem stara się nie siać tam niepotrzebnego zamętu; w tym celu spotkała się nawet z królową Anglii.

### dic\_pilot\_SHIRA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b013`

> W ostatniej bitwie nad Pacyfikiem uwalnia całą swoją moc aury i oczyszcza wszelką złą aurę.

### dic\_pilot\_KAWASE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b014`

> Kapitan okrętu aury Gran-Garan. Wierny sługa Cieli, królowej Krainy Na, wspiera ją u boku, gdy prowadzi wojska.

### dic\_pilot\_KAWASE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b015`

> Gdy w ostatniej bitwie Gran-Garan traci sternika, kapitan sam chwyta ster i taranuje okręt aury Drake'a, Will-Wips.

### dic\_pilot\_ELDN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b016`

> Mi Ferario towarzysząca królowej Cieli. Ma cięty język i silny charakter. Show uwolnił ją i Cielę z kuli burzy, zjawiska pojawiającego się raz na kilkadziesiąt lat. Uwielbia Cielę i razem z Bell Arle martwi się o swoją strapioną królową.

### dic\_pilot\_EEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b018`

> Mi Ferario towarzysząca królowej Cieli. Niewinna, często kaprysi jak dziecko. Gdy jednak Ciela została ranna, przynosiła jej jedzenie i troszczyła się o nią, pokazując dobre serce.

### dic\_pilot\_DREIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01a`

> Król Krainy Ah. Był zwykłym lokalnym władcą, lecz przywołał ludzi z Górnego Świata, rozwinął maszyny aury i siłą odebrał tron poprzedniemu królowi, Folownowi Elfowi. Pragnie zawładnąć całym Byston Well i w tym celu zbudował okręt aury Will-Wips. Przebiegły, zdecydowany i przewidujący, łączy bezwzględność z ludzkimi uczuciami, a do tego ma potężną moc aury; to człowiek na miarę króla.

### dic\_pilot\_DREIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01b`

> Gdy walka przenosi się do Górnego Świata, jego ambicje rosną: chce podbić oba światy. W trakcie wojny odkrywa jednak, że jego żona, Louser, potajemnie trzyma z Bishotem Hattą, królem Krainy Ku i jego sojusznikiem, a oni oboje wykorzystują jego ambicje. Po śmierci Louser i Bishota w środku ostatniej bitwy ucieka z pola walki, by się odbudować, lecz ostatecznie ginie z ręki Nie.

### dic\_pilot\_BURN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01c`

> Rycerz, niegdyś dowódca w armii Drake'a. Ceni rycerskość, a zarazem jest intrygantem pewnym własnej wartości. Liczył, że zasługami wojennymi utoruje sobie drogę na następcę Drake'a, lecz po licznych porażkach z Show odebrano mu stanowisko i popadł w niełaskę. Pozbawiony honoru i chwały, winą za wszystko obarczył Show i, by się zemścić, ukrywszy twarz, wrócił na pole bitwy jako Czarny Rycerz.

### dic\_pilot\_BURN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01d`

> Moc aury spotęgowana zaciekłą nienawiścią pozwala mu górować nad Show. W ostatniej bitwie zmierzył się z nim pieszo; zadali sobie nawzajem śmiertelne ciosy, po czym królowa Ciela oczyściła jego duszę.

### dic\_pilot\_JAKOBA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01e`

> Przywódczyni Ferario, władczyni Królestwa Wody, w którym mieszkają Ferario z Byston Well. Surowa, z początku odmawiała pomocy Show i jego towarzyszom, lecz widząc, jak świat pogrąża się w chaosie, poprosiła ich o zniszczenie maszyn aury. Gdy wojna w Byston Well dalej się szerzyła, własną mocą przeniosła wszystkie maszyny aury do Górnego Świata, płacąc za to gwałtownym starzeniem się.

### dic\_pilot\_TODO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b000`

> Przybysz z Górnego Świata, przywołany do Byston Well razem z Show. Ma 23 lata. Jako święty wojownik na służbie Drake'a, a potem Bishota, wielokrotnie staje Show na drodze. Pochodzi z Bostonu; był kandydatem na pilota sił powietrznych. Z natury pogodny optymista, lecz po kolejnych porażkach z Show, który zdradził Drake'a i stał się wrogiem, zaczyna mieć na jego punkcie obsesję. Nawet poznawszy plany Drake'a, trzyma z nim, bo ten obiecuje mu godność rycerza; bywa więc samolubny, ale jest też wrażliwy: rywalizuje z Allenem, starszym kolegą z sił powietrznych, i często martwi się o matkę. Raz przepada bez wieści po przegranej z Show, lecz wraca na front jako święty wojownik Krainy Ku i w Vierresie znów poluje na Show. Latał na Dunbinie we własnych barwach i Drumlo, a po powrocie na Vierresie i Wryneku. Po wynurzeniu się w Górnym Świecie ściga Show już nie tylko z obsesji, ale i by chronić Boston, gdzie mieszka matka; jego moc rośnie jeszcze bardziej. Nadmiar mocy aury sprawia jednak, że przechodzi w Hyper, i po walce na śmierć i życie ginie z ręki Show. Drake, doceniając jego zasługi, postanawia oszczędzić Boston.

### dic\_pilot\_AREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b002`

> Jeden z przybyszów z Górnego Świata, których Drake przywołał po Show i reszcie. As amerykańskich sił powietrznych, starszy kolega Toda. Za chłodnym usposobieniem kryje się trafna ocena sytuacji: dobrze rozumie, że przywołani do Byston Well są w istocie tylko najemnikami. Jest przy tym na tyle przebiegły, że sam chce wykorzystać armię Drake'a. Jego bojowe umiejętności dają się we znaki Show i reszcie, lecz w bitwie o Rau przegrywa z Show, który przesiadł się do Billbine'a.

### dic\_pilot\_JRIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b004`

> Jedna z przybyszów z Górnego Świata, których Drake przywołał po Show i reszcie. Rockowa piosenkarka z Irlandii, z pasemkami w rudych włosach. Agresywna, traktuje wojnę w Byston Well jak grę. Po powrocie do Górnego Świata przenosi się z rodzinnej Irlandii do Grecji i mocą aury podporządkowuje sobie greckie wojsko. Lecąc w Leprechaunie na czele myśliwców, zyskuje u pilotów miano “Joanny d'Arc XX wieku”. W walce z Show i Marvel jej moc aury, napędzana gniewem i nienawiścią, wymyka się spod kontroli i Jeril jako pierwsza przechodzi w Hyper. Tą potęgą przypiera Billbine'a do muru, lecz nie panuje nad szalejącą mocą aury i sama siebie niszczy.

### dic\_pilot\_FEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b006`

> Jeden z przybyszów z Górnego Świata, których Drake przywołał po Show i reszcie. W Chinach był aktorem bez powodzenia. Spokojniejszy od pewnego siebie Allena i wojowniczej Jeril, ale żądny sławy i nie daje się zepchnąć w cień. Bystry, bywa doradcą swojego oddziału. Na zaproszenie Musiy atakuje Zelernę, lecz ginie, gdy Dunbine Show odbija w niego granat rzucony przez jego własnego Leprechauna.

### dic\_pilot\_SHOT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b008`

> Inżynier z Górnego Świata przywołany do Byston Well. Pod rozkazami Drake'a, razem z innym przybyszem z Górnego Świata, Zetem Lightem, buduje maszyny aury, łączące robotykę z mocą aury. Wspiera ambicje Drake'a, który chce podbić Byston Well, lecz naprawdę zamierza wykorzystać go, by samemu zostać królem. Po przeniesieniu do Górnego Świata działa na własną rękę w zbudowanym przez siebie krążowniku aury Spriggan. Intrygant jeszcze zdolniejszy niż inżynier: realizuje swój plan, zwodząc podejrzliwego Drake'a.

### dic\_pilot\_SHOT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b009`

> W ostatniej bitwie zleca zamach na Drake'a swojej zaufanej podwładnej i kochance, Musiy, lecz ten się nie udaje. Ginie razem z Musiy od ataku Show i Marvel.

### dic\_pilot\_SION\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00a`

> Młody myśliwy z Byston Well. Gdy zawitał do wioski Baran-Baran, pojmał go Rabaan Zaramand i użył do próby uruchomienia Aura Battlera. Dzięki mocy aury Shion obudził Sirbine'a, skarb Baran-Baran, i uciekł nim. Teraz walczy, by pokrzyżować plany Rabaana, i zyskał miano świętego wojownika. Z początku narzekał, że wciągnięto go w wojnę, lecz chęć ochrony Remul i ludzie wokół sprawili, że z czasem podszedł do walki poważnie.

### dic\_pilot\_SION\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00b`

> Jego dusza to wcielenie Show Zamy, świętego wojownika sprzed 700 lat.

### dic\_pilot\_SIRKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00c`

> Mi Ferario żyjąca w Byston Well 700 lat po epoce maszyn aury. Była E Ferario, która przywołała Show i innych z Górnego Świata; za złamanie zakazu przywódczyni Ferario, Jacoba Aon, zamieniła ją w Mi Ferario. W nowym wcieleniu jest pogodna jak Chum i nie ma w niej dawnej powagi. Shion Zaba ocalił jej życie, więc odtąd mu towarzyszy. To między innymi jej moc aury pozwoliła Sirbine'owi odeprzeć Zwautha Rabaana w pierwszym starciu. Także poza walkami Aura Battlerów nieraz okazuje się nieocenioną partnerką Shiona, na przykład uwalniając jego i Remul z niewoli.

### dic\_pilot\_REMURU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00e`

> Księżniczka wioski, która wie, gdzie ukryto Sirbine'a, skarb Baran-Baran. Rabaan, szukając skarbu, upatrzył ją sobie, napadł na wioskę i porwał ją do swojego zamku, lecz Shion ją uwolnił. Kocha Shiona i bez uprzedzeń zaufała przybyszowi, prowadząc go do skarbu. Odważna, o silnym charakterze i gotowa do działania: nie ugina się przed przemocą, potrafi odebrać żołnierzowi broń i uciec, a nawet wrzucić lampę do składu paliwa, by wzniecić pożar.

### dic\_pilot\_REMURU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00f`

> Intrygi Rabaana nieraz stawiają ją w opałach, lecz dzięki Shionowi i Silky zawsze się wymyka, a w końcu wiąże się z Shionem. Jej dusza to wcielenie Riml Luft sprzed 700 lat.

### dic\_pilot\_RABAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b010`

> Zamaskowany mężczyzna, który nazywa siebie Czarnym Rycerzem. W dzieciństwie zetknął się ze Zwauthem i opętała go fascynacja, a moc Aura Battlerów rozbudziła jego ambicje. By zdobyć jeszcze większą siłę, Sirbine'a, napada na Baran-Baran, gdzie pojmuje Shiona i Remul. W podziemiach zamku trzyma Shota Weapona, by korzystać z jego wiedzy.

### dic\_pilot\_RABAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b011`

> Jego dusza to wcielenie Berna Bunningsa, który 700 lat temu walczył gnany nienawiścią.

### dic\_pilot\_SHOT2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b012`

> Człowiek, który 700 lat temu dał maszyny aury lokalnemu władcy Drake'owi Luftowi i pogrążył Byston Well w wojnie. Za tę winę jego dusza nie może umrzeć i cierpi wieczne katusze.

### dic\_pilot\_SHOT2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b013`

> Chce uciec od cierpienia: otworzyć Drogę Aury i wrócić do Górnego Świata albo jej energią unicestwić samego siebie. W tym celu napuszcza Rabaana na Shiona, licząc, że ich moc aury wymknie się spod kontroli.

### dic\_pilot\_DABA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b000`

> Pilot L-Gaima. Młodzieniec z prowincji planety Coam, który wyruszył z przyjacielem, Mirawoo Kyao, by zaciągnąć się do regularnej armii Posaydala. Choć ma łagodną twarz, potrafi być uparty, a gdy coś postanowi, nie da sobie przemówić do rozsądku. Uczciwość, dobroć i silna wola zjednują mu jednak ludzi. Podoba się też kobietom, lecz nie odwzajemnia ich uczuć, twierdząc, że nie ma prawa decydować o czyimś życiu, co doprowadza otoczenie do szału. Zamieszanie wokół weksla na milion gheenów sprawia, że trafia do rebeliantów. Walczy z regularną armią w ręcznie wykonanym Heavy Metalu klasy A, L-Gaimie, pamiątce po ojcu.

### dic\_pilot\_DABA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b001`

> Po wielu przejściach staje na czele rebelii. “Daba Myroad” to imię przybrane; naprawdę to Camen Myroad, dziedzic dynastii Yaman z planety Mizun, zniszczonej przez Posaydala. Wychował go wasal rodu, Daba Hatzer, razem z Quwasan Olibee, z którą dorastał jak z siostrą. Jego narzeczona, Olibee, zaginęła i między innymi po to, by jej szukać, wyruszył z rodzinnych stron. W trakcie walk przesiada się z L-Gaima do L-Gaima Mk-II i jako przywódca rebelii prowadzi ludzi do zwycięstwa nad prawdziwym Oldną Posaydalem. Po wojnie nie przyjmuje żadnego stanowiska w nowym rządzie i wraca na Coam z Olibee, której umysł się załamał.

### dic\_pilot\_LLS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b002`

> Ocalała z Mirali, rdzennego ludu Pentagony. Daba uwolnił ją z wędrownej trupy, gdzie pokazywano ją jak dziwowisko, i dołączyła do jego drużyny. Z początku nie ufała ludziom i nie odzywała się ani słowem, lecz stopniowo otworzyła się na Dabę i resztę. Mirali to pokojowy lud, ale świat ludzi chyba ją zmienia: z natury łagodna, potrafi w ferworze kopnąć kogoś, a potem sama się sobie dziwić. Świetnie gotuje i szyje; ubrania szyje sama, więc ma ich mnóstwo, od piżamy po czarny strój zwiadowczy. Dzięki małemu ciału i umiejętności latania pomaga Dabie i reszcie w zwiadzie i infiltracji, a w walce towarzyszy pilotom w kokpicie Heavy Metalu.

### dic\_pilot\_LLS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b003`

> Na górniczej planecie Palata Star razem z Kyao i z pomocą dusz pobratymców powstrzymała wybuch reaktora jądrowego Alpha Heart. Po wojnie postanawia wyruszyć z Kyao na poszukiwanie innych ocalałych Mirali.

### dic\_pilot\_AMU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b004`

> Dziewczyna podróżująca z Dabą. Była aktorką w teatrzyku, lecz Miyama Lilen dostrzegła jej talent i przyjęła ją do bandy rabusiów. Tak poznała Dabę, zakochała się w nim bez pamięci i uparcie mu towarzyszy. Przy Dabie to rozkochana panienka, lecz przy innych zmienia się nie do poznania i wychodzi z niej zadziorna, sprytna natura. Z Leccee, która dla Daby porzuciła armię, toczy zażartą walkę o jego względy.

### dic\_pilot\_AMU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b005`

> Chcąc pomóc Dabie, uczy się pilotować Heavy Metale, a gdy Daba przesiada się do L-Gaima Mk-II, przejmuje L-Gaima. Po wojnie ze łzami w oczach żegna Dabę, który wraca z Olibee na Coam.

### dic\_pilot\_RESSY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b006`

> Jedna z sojuszniczek Daby. Była członkinią Trzynastki regularnej armii Posaydala, lecz porzuciła armię, ujęta charakterem Daby, i zaczęła mu pomagać. Zna się na wywiadzie i strategii, a przy tym jest świetną wojowniczką. Ma charakterek i jest uparta; z Amm toczy zażartą walkę o Dabę.

### dic\_pilot\_RESSY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b007`

> Z czasem, zamiast rywalizować z Amm na jej warunkach, uznała, że lepiej pomoże Dabie inaczej niż walcząc u jego boku, i sama od niego odeszła. Gdy powraca jako dowódczyni bojowa okrętu Whele, ma nowy strój i zachowuje się dojrzalej. W ostatniej bitwie na Sveet doprowadza Mian Qu Haw Asher do Serca Lachesis, by wyłączyć Bio-Relation System. Po wojnie ze łzami w oczach żegna Dabę, który wraca z Olibee na Coam.

### dic\_pilot\_RESSY2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b008`

> Jedna z sojuszniczek Daby. Była członkinią Trzynastki regularnej armii Posaydala, lecz porzuciła armię, ujęta charakterem Daby, i zaczęła mu pomagać. Zna się na wywiadzie i strategii, a przy tym jest świetną wojowniczką. Ma charakterek i jest uparta; z Amm toczy zażartą walkę o Dabę. Z czasem uznała, że lepiej pomoże Dabie inaczej niż walcząc u jego boku, i sama od niego odeszła. Gdy powraca jako dowódczyni bojowa okrętu Whele, ma nowy strój i zachowuje się dojrzalej.

### dic\_pilot\_RESSY2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b009`

> W ostatniej bitwie na Sveet doprowadza Mian Qu Haw Asher do Serca Lachesis, by wyłączyć Bio-Relation System. Po wojnie ze łzami w oczach żegna Dabę, który wraca z Olibee na Coam.

### dic\_pilot\_KYAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b00a`

> Przyjaciel Daby z rodzinnej Coam. Wyruszył z nim z prowincji, by zaciągnąć się do regularnej armii, ale gdy Daba przystał do rebeliantów, niechętnie z tego zrezygnował. Wesoły, roztrzepany poczciwiec, ma jednak słabość do pięknych kobiet i pieniędzy, a do tego jest porywczy. Ma też wilczy apetyt i niezwykłą siłę. To nie tylko wybitny mechanik, ale i pilot Heavy Metali; wspiera Dabę w każdej sytuacji.

### dic\_pilot\_KYAO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b00b`

> W trakcie walk od razu rozpoznaje w Amoun Duulu, nowej maszynie armii Posaydala, Heavy Metal w stylu Yaman, i przerabia go na L-Gaima Mk-II. Po wojnie wyrusza z Lilis na poszukiwanie ocalałych Mirali, choć niezbyt mu się do tego pali.

### dic\_pilot\_GABLY\_\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b000`

> Żołnierz regularnej armii Posaydala. Pochodzi z ubogiego szlacheckiego rodu z prowincji planety Coam; z nadziejami całej wioski na barkach wyruszył w używanym Allonie, by zaciągnąć się do armii. Po drodze podkradł Dabie jedzenie i tak został jego rywalem. Ambitny i dumny, chce uchodzić za chłodnego, lecz jest emocjonalny, łatwo się wzrusza, bywa dziecinny i kocha się na zabój od pierwszego wejrzenia, a mimo to trudno go nie lubić. Jako pilot ma prawdziwy talent; po kilku przydziałach zostaje oficerem sztabowym i dostaje Heavy Metal klasy A. W jego stronach Mirali uchodzą za sługi diabła, dlatego nie znosi Lilis.

### dic\_pilot\_GABLY\_\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b001`

> Po wielu perypetiach zakochuje się w Quwasan Olibee i, by ją ocalić, walczy u boku Daby, przyczyniając się do upadku prawdziwego Posaydala i Giwazy. Po wojnie powierza Dabie Olibee, której umysł się załamał, i żegna ich, gdy wracają na Coam.

### dic\_pilot\_HASYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b002`

> Podwładny Gablae. Był zastępcą hersztki bandy rabusiów, do której należała Amm, lecz próbując się wybić, zamordował hersztkę, Lilen; gdy sprawa wyszła na jaw, musiał uciekać. Potem przymilił się do Amm, która przystała do rebeliantów, i przez jakiś czas był w drużynie Daby, lecz zdradził ją dla nagrody i w końcu trafił pod rozkazy Gablae. Tchórzliwy kanciarz, łatwo daje się ponieść.

### dic\_pilot\_HASYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b003`

> Przeżył do końca, a po wojnie razem z Gablae i innymi żegnał Dabę i resztę.

### dic\_pilot\_OLBY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b004`

> Żołnierz armii Posaydala, dowódczyni oddziału przynęty, wyspecjalizowanego w tropieniu niedobitków rodu Yaman, później dowódczyni gwardii przybocznej. Naprawdę to przybrana siostra i narzeczona Daby, której Posaydal wbił Controller Harken i zawładnął jej umysłem. Służy też Posaydalowi za czujnik: zbiera informacje, a czasem przemawia w jego imieniu. Wspomnienia czasów spędzonych z Dabą są zapieczętowane, lecz spotkania z nim kruszą pieczęć, co sprawia jej ból. W walce pilotuje Calvary Temple zwaną Hellmeene.

### dic\_pilot\_OLBY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b005`

> Jej umysł staje się coraz mniej stabilny, a po upadku prawdziwego Posaydala całkiem się załamuje. Gdy wszystko się kończy, wraca z bratem, Dabą, na Coam.

### dic\_pilot\_NEY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b006`

> Członkini Trzynastki regularnej armii Posaydala. Świetna wojowniczka w Heavy Metalu klasy A, Auge, nieraz dała się Dabie we znaki. Wysoka piękność, która nigdy nie zapomina o kobiecości; wstydzi się nawet pokazać bez makijażu. Kochanka Giwazy, zajmuje wysoką pozycję w Trzynastce. Z początku sprzyjała Gablae, lecz gdy zaczął działać na własną rękę, stała się wobec niego surowa.

### dic\_pilot\_NEY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b007`

> Walczyła dla ukochanego Giwazy, lecz w końcu oskarżył ją o szpiegostwo. Rozwścieczona, odcięła mu prawą rękę, ale zaraz potem Giwaza ją zastrzelił.

### dic\_pilot\_GWAZA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b008`

> Szef wywiadu dywizji Coam armii Posaydala. Dowodzi elitarną Trzynastką; jego głównym zadaniem jest wykrywanie i tracenie przeciwników Posaydala. Bez wątpienia zdolny, ale przebiegły, wyniosły i zbyt pewny siebie. Dla własnych korzyści potrafi być wobec innych całkowicie bezwzględny.

### dic\_pilot\_GWAZA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b009`

> Przysięgał wierność Posaydalowi, lecz niezadowolony z własnej pozycji i podejrzliwy wobec Posaydala, który przymyka oczy na zepsucie w armii, uknuł spisek. Dla swoich ambicji stracił nawet kochankę, Nei, podejrzewając ją o zdradę. Uważał się za godnego tronu Pentagony, lecz nie dorósł do roli władcy świata i jego ambicje legły w gruzach. Choć nie miał już szans na zwycięstwo, przekonany, że po zebraniu sił zdoła się odegrać, porzucił załogę okrętu flagowego i uciekł sam promem, lecz zginął od bezpośredniego trafienia z Buster Launchera L-Gaima.

### dic\_pilot\_MACTMN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00a`

> Członek Trzynastki regularnej armii Posaydala. Fryzura, strój i makijaż nadają mu dziwaczny wygląd. Na co dzień sprawia wrażenie spokojnego, lecz gdy się podekscytuje, zaczyna mówić i zachowywać się ekscentrycznie i traci równowagę. Pilotuje A-Taula V, którego sam przerobił.

### dic\_pilot\_MACTMN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00b`

> Staje po stronie Giwazy, gdy ten buntuje się przeciw Posaydalowi, i na jego rozkaz wciąż poluje na Dabę. Ostatecznie zestrzeliwuje go Buster Launcher L-Gaima Mk-II.

### dic\_pilot\_LLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00c`

> Członkini Trzynastki regularnej armii Posaydala. Kapryśna i bezlitosna; przez dawne przeżycia nienawidzi mężczyzn i gardzi kobietami, które im usługują. Jej ulubiony Heavy Metal to G.Roon.

### dic\_pilot\_LLY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00d`

> Staje po stronie Giwazy, gdy ten buntuje się przeciw Posaydalowi, choć nie jest mu szczególnie wierna. Znęca się nad pojmaną Amm i tak rodzi się między nimi zawziętość; w końcu to Amm zestrzeliwuje ją w L-Gaimie.

### dic\_pilot\_BURNG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00e`

> Członek Trzynastki. Opanowany i pewny siebie.

### dic\_pilot\_BURNG\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00f`

> Staje po stronie Giwazy, gdy ten buntuje się przeciw Posaydalowi. W Ashura Temple przypiera do muru Dabę, który chce dopaść Giwazę, lecz ulega zgranemu atakowi Daby i Kyao, który przybył z odsieczą.

### dic\_pilot\_ANTON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b010`

> Oficer rezerwy Trzynastki. Podwładny Nei Moh Han; gdy rusza do walki, osłania ją z boku razem z partnerem, Hekelerem. W przeciwieństwie do porywczego Hekelera jest opanowany.

### dic\_pilot\_ANTON\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b011`

> Gdy Nei odchodzi z frontu, zostaje adiutantem Giwazy i służy mu do końca. Wzory na jego twarzy brano za tatuaż, lecz po ostatniej bitwie okazało się, że to naklejki.

### dic\_pilot\_HECRR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b000`

> Jednooki oficer rezerwy Trzynastki. Podwładny Nei Moh Han; gdy rusza do walki, osłania ją z boku razem z partnerem, Antoonem. W przeciwieństwie do opanowanego Antoona jest porywczy, ale ma prostolinijny honor wojownika.

### dic\_pilot\_HECRR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b001`

> Staje po stronie Giwazy, gdy ten buntuje się przeciw Posaydalowi, i w Bat-Shu prowadzi natarcie na Sveet, lecz Calvary Temple Hanza Alahalta wyłącza go z walki. Ginie, osłaniając MF McTomina przed L-Gaimem Mk-II, a umierając, woła imię swego partnera, Antoona.

### dic\_pilot\_RYOKLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b002`

> Ochroniarz i nadzorca Quwasan Olibee. Podobnie jak ona ma umysł kontrolowany przez Controller Harken. Były członek Trzynastki, groźny nawet bez broni. Nie jest wierny samej Olibee; liczy się dla niego tylko wykonanie zadania.

### dic\_pilot\_RYOKLY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b003`

> Gdy Olibee zostaje dowódczynią gwardii przybocznej, staje się jej adiutantem. W czarnej Calvary Temple odpiera zbuntowane siły Giwazy i rebeliantów.

### dic\_pilot\_HANS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b004`

> Członek Trzynastki regularnej armii Posaydala. Odpowiada za obronę Sveet.

### dic\_pilot\_HANS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b005`

> Nie przyłącza się do buntu Giwazy i do końca walczy po stronie Posaydala. W czarnej Calvary Temple wyłącza z walki Bat-Shu Hekelera ze stronnictwa Giwazy. Ginie w najgłębszym wnętrzu Sveet razem z Marhalem Senumą, innym wiernym Posaydalowi członkiem Trzynastki, wskutek działania Bio-Relation System.

### dic\_pilot\_AMNDR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b006`

> Założyciel największego koncernu w Świecie Pentagony. Ma spore wpływy w regularnej armii Posaydala i dotarł do samego jej trzonu. Poznał Dabę i Gablae dzięki wekslowi na milion gheenów i napisał Gablae list polecający do regularnej armii. Kupiec śmierci: przez swoją Kompanię Handlową Aman zaopatruje w broń zarówno regularną armię, jak i rebeliantów, i ma w wielu miejscach prywatne wojska. Kieruje się głównie interesem kupca, choć bywa, że stawia na pierwszym miejscu własną ciekawość.

### dic\_pilot\_AMNDR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b007`

> Imię i pozycja Amandry Kamandry są fałszywe. Naprawdę to prawdziwy Oldna Posaydal, władca Świata Pentagony.

### dic\_pilot\_POSEIDL\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b008`

> Prawdziwe oblicze Amandry Kamandry i rzeczywisty władca Świata Pentagony. Młodość zawdzięcza Bio-Relation System, który sam opracował. Mian i Flat, które niegdyś go kochały, traktował jak narzędzia, a pod pretekstem utrzymania równowagi napuszczał na siebie regularną armię i rebeliantów, rządząc światem z cienia. Gdy jednak rebelia pod wodzą Daby okazuje się silniejsza, niż przewidział, a Mian i Flat odwracają się od niego, musi sam wyjść na scenę.

### dic\_pilot\_POSEIDL\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b009`

> W ostatniej bitwie w Auge miażdży L-Gaima Mk-II Daby, lecz gdy Mian wyłącza Bio-Relation System, gwałtownie się starzeje i przegrywa. W trakcie walki wyjawia, że jego bliskich okrutnie zamordowali ludzie z rodu Yaman i że chciał z zemsty wytępić ich ród.

### dic\_pilot\_POSEIDL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00a`

> Władca Świata Pentagony. Podobno to 68-letni mężczyzna, lecz ma młodą, uwodzicielską urodę i otacza go wiele tajemnic. Przed ludźmi pojawia się zwykle jako hologram i nazywa się dzieckiem boga, z przesadą podsycając swoją aurę tajemnicy.

### dic\_pilot\_POSEIDL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00b`

> Naprawdę to Mian Qu Haw Asher, kobieta, która była towarzyszką i kochanką prawdziwego Posaydala; młodość zawdzięcza Bio-Relation System. Była marionetką prawdziwego Posaydala (Amandry Kamandry), lecz z czasem zaczęła wątpić w sens swojego istnienia i w ukochanego, który tak się zmienił, aż postanowiła z nim zerwać. Gdy Amandra ujawnia się i walczy z Dabą, Mian razem z Leccee dociera do Serca Lachesis w najgłębszym wnętrzu Sveet i wyłącza Bio-Relation System, po czym gaśnie, jakby się rozpłynęła. Wtedy i Amandra gwałtownie się starzeje i przegrywa.

### dic\_pilot\_FRAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00c`

> Pani sztucznego ciała niebieskiego Theart Star, któremu Posaydal nadał eksterytorialność. Od dawna rządzi tą planetą zamieszkaną wyłącznie przez kobiety, a jej wygląd nie zdradza wieku. Korzystając z eksterytorialności, która zamyka wstęp regularnej armii, z kaprysu wspiera Dabę i jego drużynę.

### dic\_pilot\_FRAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00d`

> Naprawdę to kobieta, która niegdyś razem z Mian Qu Haw Asher walczyła dla prawdziwego Posaydala; przywileje to nagroda za tamte zasługi. Zrażona tym, że prawdziwy Posaydal traktuje kobiety jak narzędzia, odwraca się od niego. Gdy żąda od niego wyjaśnień, ginie w eksplozji.

### dic\_pilot\_KOUZIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00e`

> Pilot Mazinkaisera. Maszynę powierzył mu jej twórca, dziadek Kojiego, doktor Juzo Kabuto. Gorącokrwisty, prawy i oddany przyjaciołom. Z początku nie potrafił zapanować nad potęgą Mazinkaisera, lecz wiele prób uczyniło z niego prawdziwego pilota. Gdy zaczyna się inwazja, jest na wypoczynku w Paryżu. By powstrzymać Armię Bestii Bojowych, rusza do Instytutu Energii Fotonowej, po drodze tracąc przyjaciół, między innymi siostry Loru i Lori oraz doktora Morimoriego.

### dic\_pilot\_KOUZIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00f`

> Wsiada do Mazinkaisera, którego profesor Yumi i reszta przysłali z kosmosu, i jego niesamowitą mocą rozbija Bestie Bojowe jedną po drugiej. W końcu wygrywa pojedynek z Wielkim Generałem Ciemności i ocala przyszłość świata.

### dic\_pilot\_TETUYAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b000`

> Pilot Great Mazingera. Został pilotem po morderczym szkoleniu bojowym i zwą go “zawodowym żołnierzem”. Dla Kojiego jest jak starszy brat; bywa szorstki w słowach i czynach, ale w głębi duszy troszczy się o towarzyszy. Stoczył zaciętą walkę z Bestiami Bojowymi, które pojawiły się w Nowym Jorku.

### dic\_pilot\_TETUYAK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b001`

> Pokonuje dwóch z Siedmiu Generałów, Wodnego Generała Angorasa i Owadziego Generała Scarabetha, i broni miasta, lecz uszkodzony Great Mazinger nie może się ruszyć.

### dic\_pilot\_SAYAKAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b002`

> Córka profesora Yumiego, dyrektora Instytutu Energii Fotonowej. Pogodna i żywa, kocha się w Kojim. Kiedyś walczyła u jego boku w Aphrodite A. Gdy Bestie Bojowe przystępują do inwazji, wyrusza z Kojim z Paryża do Japonii, lecz zostaje ranna w ataku arcyksięcia Gorgona, którego nasłało Imperium Mykeńskie.

### dic\_pilot\_JUNK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b004`

> Pilotka Venus A i operatorka Instytutu Energii Fotonowej. Gdy Bestie Bojowe ruszają na cały świat, toczy z nimi w Venus A zaciekłą walkę w australijskim Sydney.

### dic\_pilot\_JUNK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b005`

> Przegrywa z Upiornym Generałem Hadiasem, jednym z Siedmiu Generałów, ale uchodzi z życiem.

### dic\_pilot\_BOSSK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b006`

> Pilot Boss Robota. Dobry kumpel Kojiego, z którym nieraz otarł się o śmierć. Nieokrzesany, ale wierny przyjaciel; zawsze zjawia się z pomocą, gdy Koji jest w opałach. Rzadko rusza się bez dwóch pomagierów, Nuke'a i Muchy.

### dic\_pilot\_BOSSK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b007`

> Ratuje Kojiego przed arcyksięciem Gorgonem, zamachowcem Imperium Mykeńskiego, przywozi w Boss Robocie Kaiser Scrander i na wiele sposobów wspiera Kojiego.

### dic\_pilot\_NUKEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b008`

> Jeden z pomagierów Bossa. Nieśmiały i powolny, często z cieknącym nosem.

### dic\_pilot\_MUTYAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00a`

> Jeden z pomagierów Bossa. Śmiały; czasem nawet ma inne zdanie niż Boss.

### dic\_pilot\_YUMIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00c`

> Dyrektor Instytutu Energii Fotonowej i ojciec Sayaki. Gdy Bestie Bojowe najeżdżają świat, wysyła na Ziemię Mazinkaisera, którego ulepszał w Drugim Instytucie Energii Fotonowej, ośrodku badawczym w kosmosie.

### dic\_pilot\_MRMRK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00e`

> Uczeń doktora Juzo Kabuto i jeden z Trzech Doktorów. Rozpoznać go można po potężnej posturze i okazałej brodzie. Podczas podróży służbowej z Kojim i resztą do Paryża zostaje zaatakowany przez Bestie Bojowe i ląduje awaryjnie w bazie wojsk Unii Europejskiej.

### dic\_pilot\_MRMRK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00f`

> By Koji bezpiecznie dotarł do Japonii, zostaje sam w bazie i za cenę życia zatrzymuje Bestie Bojowe.

### dic\_pilot\_SEWAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b010`

> Uczeń doktora Juzo Kabuto i jeden z Trzech Doktorów. Rozpoznać go można po niskim wzroście i wielkich wąsach. Niecierpliwy w gorącej wodzie kąpany.

### dic\_pilot\_NOSSOK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b012`

> Uczeń doktora Juzo Kabuto i jeden z Trzech Doktorów. Najwyższy z trójki, o charakterystycznych krzaczastych brwiach. Spokojny i małomówny.

### dic\_pilot\_SIROK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b014`

> Młodszy brat Kojiego. Pełen energii i ciekawy świata, a przy tym oddany bratu. Z Drugiego Instytutu Energii Fotonowej kibicuje Kojiemu i jego towarzyszom.

### dic\_pilot\_DRKENPK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b016`

> Władca Imperium Mykeńskiego. Absolutny pan, któremu podlega Wielki Generał Ciemności, dowodzący Siedmioma Generałami. Zbudził się z długiego snu, by wypędzić ludzkość z powierzchni ziemi. Całe jego ciało jest z ognia.

### dic\_pilot\_DRKJENK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b018`

> Generał Imperium Mykeńskiego, dowodzący Siedmioma Armiami Bestii Bojowych. Przez tysiące lat czaił się pod ziemią, aż wyszedł na powierzchnię, by podbić Ziemię. Ogłosił całemu światu wyrok zagłady na ludzkość i jej cywilizację.

### dic\_pilot\_DRKJENK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b019`

> Przytłaczającą siłą przyciska Mazinkaisera do muru, lecz ulega furii Kojiego, którego napędza myśl o towarzyszach.

### dic\_pilot\_HADEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01a`

> Jeden z Siedmiu Generałów, przywódca upiornych Bestii Bojowych. Walczy wielką kosą. Pociął Venus A, którą pilotowała Jun, aż ta nie mogła walczyć.

### dic\_pilot\_HADEK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01b`

> Wraz z innymi Bestiami Bojowymi zdobywa Instytut Energii Fotonowej, lecz Promień Mrożący Mazinkaisera zamienia go w lód, a potem w okruchy.

### dic\_pilot\_DNTEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01c`

> Upiorna Bestia Bojowa, która zaatakowała Instytut Energii Fotonowej. Jeden z przywódców Bestii Bojowych; zapowiada śmierć Kojiego.

### dic\_pilot\_DNTEK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01d`

> Tuż po Pilder On trafia go wprost Photon Power Beam Mazinkaisera i obraca w nicość.

### dic\_pilot\_GGONK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01e`

> Zabójca nasłany przez Imperium Mykeńskie. Dolną połowę ciała ma tygrysią. Na rozkaz Wielkiego Generała Ciemności poluje na Kojiego.

### dic\_pilot\_GGONK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01f`

> Przypiera do muru Kojiego, który walczy bez maszyny, lecz powstrzymuje go Boss. Ginie przeszyty strzałem z pistoletu fotonowego Kojiego i znika w płomieniach.

### dic\_pilot\_TAKUMA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b020`

> Pilot Getter Arca. Ma 19 lat. Syn Ryomy Nagarego z pierwszej drużyny Gettera, w gorącej wodzie kąpany. Od urodzenia ma wyjątkowo wytrzymałe ciało: znosi przeciążenia przy pilotowaniu Gettera bez kombinezonu, a rany goją się na nim szybciej niż na innych. Uwielbia onigiri ze sklepu całodobowego. W dzieciństwie stracił matkę, zamordowaną przez nieznanego sprawcę; by go odnaleźć, przybywa z Baku Yamagishim do Laboratorium Saotome. Jakby wiedziony przeznaczeniem, wsiada do Getter Robota i staje do walki z wrogiem ludzkości.

### dic\_pilot\_TAKUMA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b000`

> W trakcie walk odkrywa, że zabójca jego matki, McDonald, należy do Andromeda Stellaration, i rozlicza się z nim w kosmosie dalekiej przyszłości. Po powrocie do teraźniejszości walczy, by powstrzymać Kamuia, który poznał prawdę o władzy Getter Emperora i ludzkości nad wszechświatem i stał się jej wrogiem.

### dic\_pilot\_KAMUI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b001`

> Pilot Getter Kirika. Ma 19 lat. Pół człowiek, pół Saurianin z Imperium Dinozaurów, pokonanego niegdyś przez Getter Robota; nie wybacza nikomu drwin na ten temat. Wyglądem różni się od ludzi, a przy tym ma wytrzymałe ciało i niezwykłą sprawność. Od dziecka wychowywał go Hayato Jin z Laboratorium Saotome, szkoląc na pilota Getter Robota.

### dic\_pilot\_KAMUI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b002`

> W kosmosie dalekiej przyszłości widzi, jak przerażająca jest ewolucja, do której dochodzi ludzkość. Tam McDonald, ocalały z Imperium Hyakki, powierza mu broń ostateczną, BUG. Po powrocie do teraźniejszości odbiera władzę nad Imperium Dinozaurów cesarzowi Gore'owi III i w ukończonym BUG-u staje przeciw Takumie i reszcie jako wróg ludzkości.

### dic\_pilot\_BAKU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b003`

> Pilot Getter Khana. Ma 22 lata. Młodszy brat Tahira, założyciela religii Zielonej Ziemi, który niegdyś pilotował Shin Getter Robota. Ma słaby dar przewidywania, lecz wie, że daleko mu do brata, i gnębi go to. Dobroduszny olbrzym. Wspiera Takumę, z którym podróżuje od dziecka, a przyjmując los związanych z Getterem, postanawia walczyć jako członek drużyny Gettera.

### dic\_pilot\_BAKU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b004`

> Poznawszy w kosmosie przyszłości prawdę o władzy Getter Emperora i ludzi nad wszechświatem, zostaje w przestrzeni stworzonej przez Getter Emperora, by szukać innej drogi.

### dic\_pilot\_HAYATOA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b005`

> Dyrektor Laboratorium Saotome. Członek pierwszej drużyny Gettera; kontynuuje badania nad promieniami Gettera, wierny spuściźnie zmarłego doktora Saotome. Jako dowódca kieruje też oddziałem Getter D2, który walczy z nieznanym wrogiem pojawiającym się w różnych miejscach Ziemi. W licznych bitwach stracił wielu towarzyszy, dlatego cechuje go wielkie poczucie odpowiedzialności i nieugięta determinacja.

### dic\_pilot\_HAYATOA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b006`

> Gdy Imperium Dinozaurów pod wodzą Kamuia, który wrócił z przyszłości, atakuje Laboratorium Saotome, Hayato gołymi rękami rozprawia się z pilotami Gettersaurusa. Postrzelony w plecy przez Kamuia, spada w najgłębsze rejony laboratorium; tam, powierzając przyszłość ludzkości Takumie i reszcie, otwiera “Kocioł Piekieł”, w którym śpi Getter Dragon.

### dic\_pilot\_SHIKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b007`

> Szef działu rozwoju uzbrojenia Laboratorium Saotome. Konstruuje wszelką broń, małą i dużą, a także systemy obronne całego laboratorium. Szalony naukowiec, który uwielbia niekonwencjonalną broń palną i (liczne) eksplozje; sam przerobił swoje ciało na cyborga, tak że całe jest bronią. Od dawna strzeże Laboratorium Saotome i znał Ryomę, ojca Takumy.

### dic\_pilot\_IGARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b009`

> Dowódca zespołu obsługującego Getter D2. Troskliwy, cieszy się zaufaniem członków zespołu. Był pilotem rezerwowym Getter Robota, potem instruktorem, aż objął obecne stanowisko.

### dic\_pilot\_KOMEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00b`

> Dowódca, który z dalekich zakątków kosmosu nasyła na Ziemię machiny bojowe zwane Insectorami. Jego cele i tożsamość pozostają nieznane.

### dic\_pilot\_KOMEI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00c`

> Okazuje się, że to dowódca, któremu Wielka Królowa Meldusa, władczyni Andromeda Stellaration, powierzyła podbój Ziemi. Jego celem jest unicestwienie ludzkości, która zapanuje nad wszechświatem, i Getter Emperora, który ją do tego doprowadzi. By zniszczyć Getter Robota, wysadza własną bazę i znika w płomieniach.

### dic\_pilot\_MACD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00d`

> Prawa ręka Kongminga. To on zabił matkę Takumy, a teraz czyha na życie samego Takumy, choć jego cel pozostaje nieznany.

### dic\_pilot\_MACD\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00e`

> Okazuje się, że to ocalały z dawno zniszczonego Imperium Hyakki. By pomścić Wielkiego Cesarza Brai, pokonanego przez Getter Robota, chce zniszczyć Getter Robota i zabić jego pilota, Takumę, syna Ryomy Nagarego. Gdy Takuma i reszta trafiają do przyszłości, powierza Kamuiowi broń ostateczną, BUG, a sam walczy w bestii Uzala, lecz przegrywa z Takumą i jego towarzyszami.

### dic\_pilot\_TOEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00f`

> Dowódca frontowy prowadzący Insectory. Wyłania się z podprzestrzennej bramy zwanej Stoker i prowadzi Insectory na Laboratorium Saotome. Potrafi się maskować i mnożyć, czym wodzi za nos oddział Getter D2.

### dic\_pilot\_TOEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b010`

> Ginie od Double Tomahawka Getter Arca w pierwszej walce Takumy i reszty jako oficjalnych pilotów Gettera.

### dic\_pilot\_QEIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b011`

> Istota przysłana przez Andromeda Stellaration. Niezwykle płodna, składa mnóstwo jaj. Wyklute robactwo przejmuje ludzkie ciała i zamienia je w ludzi-owady. Na czele niezliczonych robali zajmuje najgłębsze rejony starego Laboratorium Saotome.

### dic\_pilot\_QEIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b012`

> Doprowadza laboratorium na skraj zagłady, lecz w końcu miażdżą ją szczęki Getter Arca.

### dic\_pilot\_GOAL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b013`

> Cesarz Imperium Dinozaurów, potomek cesarza Gore'a, którego niegdyś pokonał Getter Robot. Aby stawić czoło Insectorom, zawiera pokój z ludzkością i sojusz z Laboratorium Saotome.

### dic\_pilot\_GOAL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b014`

> Oficjalnie współpracuje z ludźmi, lecz potajemnie rozkazuje Kamuiowi zniszczyć Getter Robota po wojnie z Andromeda Stellaration. Gdy Kamui wraca z przyszłości, odbiera mu władzę w zamachu stanu, a Gore III zostaje marionetkowym cesarzem.

### dic\_pilot\_HAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b015`

> Szef nauki Imperium Dinozaurów. Sędziwy przywódca umiarkowanego skrzydła, marzy o pokoju i współistnieniu Saurian z ludźmi. Jeden z nielicznych, którzy znają przeszłość Kamuia.

### dic\_pilot\_HAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b016`

> Buduje moduł kotwicy hiperprzestrzennej Zold i przenosi drużyny Gettera i Saurusa na kraniec czasu i przestrzeni.

### dic\_pilot\_BAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b017`

> Stary generał Imperium Dinozaurów, jedyny żyjący weteran z czasów cesarza Gore'a. Żyje opowieściami o dawnych walkach z Ryomą Nagarem, a otoczenie kręci głową nad zgrzybiałym starcem.

### dic\_pilot\_BAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b018`

> Gdy Kamui po powrocie z przyszłości wznieca bunt, staruszek odzyskuje dawny wigor i staje po jego stronie.

### dic\_pilot\_BYS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b019`

> Główny pilot Gettersaurusa. Pochodzi z terrasaurian, najniższej warstwy Saurian. Życie jego pobratymców ceni się nisko, więc zgłosił się na pilota, by zyskać głos; gotów jest ryzykować życiem dla chwały. Wojowniczy, często ściera się z Takumą. Kamuia, przyjaciela z dzieciństwa, podziwia i darzy szacunkiem.

### dic\_pilot\_BYS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01a`

> Gdy Kamui po powrocie z przyszłości wznieca bunt, idzie za nim i staje się wrogiem ludzkości. W Laboratorium Saotome atakuje gołymi rękami Hayato Jina, lecz ginie z jego ręki.

### dic\_pilot\_GNRY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01b`

> Drugi pilot Gettersaurusa. Terrasaurianin, jak Vise i Gozro.

### dic\_pilot\_GNRY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01c`

> Gdy Kamui po powrocie z przyszłości wznieca bunt, idzie za nim i staje się wrogiem ludzkości. W Laboratorium Saotome atakuje gołymi rękami Hayato Jina, lecz ginie z jego ręki.

### dic\_pilot\_GOZR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01d`

> Drugi pilot Gettersaurusa. Terrasaurianin, jak Vise i Ganryu.

### dic\_pilot\_GOZR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01e`

> Gdy Kamui po powrocie z przyszłości wznieca bunt, idzie za nim i staje się wrogiem ludzkości. W Laboratorium Saotome atakuje gołymi rękami Hayato Jina, lecz ginie z jego ręki.

### dic\_pilot\_MUSASHIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01f`

> Dowódca Legionu Gettera. Był pilotem maszyny Bear pierwszego Getter Robota i zginął w ostatecznej bitwie z Imperium Dinozaurów. Walczy w wojnie o przetrwanie ludzkości i dla wrogów jest bezlitosny.

### dic\_pilot\_MUSASHIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b020`

> Okazuje się, że to sztuczny człowiek z genami Musashiego Tomoe, stworzony na podstawie wspomnień Getter Emperora. Istnieje wiele jego kopii; gdy jedna ginie, nowa, z jej wspomnieniami, natychmiast wraca na front.

### dic\_pilot\_KAMMOM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b021`

> Matka Kamuia. Porwana przez Imperium Dinozaurów za panowania cesarza Gore'a, urodziła jego syna, Kamuia. Gore III więzi ją jako zakładniczkę, by trzymać w ryzach cieszącego się poważaniem Kamuia, i nie może widywać syna.

### dic\_pilot\_KAMMOM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b022`

> Gdy Kamui, przejąwszy władzę w Imperium Dinozaurów, chce zgładzić żyjących w nim ludzi, Ron Schweitzer stawia opór i strzela, a ona zasłania syna własnym ciałem i umiera w jego ramionach.

### dic\_pilot\_SHUVI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b023`

> Naukowiec wysłany przez ONZ do Imperium Dinozaurów. Był dyrektorem satelity geostacjonarnego sił ONZ i 19 lat temu widział, jak Shin Getter Robot leci na Marsa.

### dic\_pilot\_SHUVI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b000`

> Wraz z profesorem Hanem z Imperium Dinozaurów badał moduł kotwicy hiperprzestrzennej Zold i wysłał Takumę i resztę do kosmosu przyszłości. Gdy Kamui, przejąwszy władzę w Imperium Dinozaurów, chce zgładzić żyjących w nim ludzi, Ron stawia opór i ginie zastrzelony.

### dic\_pilot\_SHUWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b001`

> Admirał sił sprzymierzonych. Był pilotem Stelbera, załogowego robota armii USA. Walczył wtedy razem z drużyną Gettera Go Ichimonjiego i związał się z Sho Tachibaną.

### dic\_pilot\_SHOUG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b003`

> Inspektor sił sprzymierzonych. Członkini drużyny Gettera, która 19 lat temu walczyła z wrogami ludzkości; nie ustępuje mężczyznom. Martwi się o dawnego towarzysza, Go Ichimonjiego, który pojawił się w Shin Getter Robocie Tarak.

### dic\_pilot\_GOUA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b005`

> Pilot Getter Robota z wojny sprzed 19 lat. W ostatniej bitwie razem z Ryomą Nagarem i Tahirem, bratem Baku Yamagishiego, pilotował Shin Getter Robota i ocalił Ziemię, po czym przepadł bez wieści. Gdy Ziemi grozi niebezpieczeństwo, pojawia się w Shin Getter Robocie Tarak.

### dic\_pilot\_GOUA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b006`

> Gdy atak Andromeda Stellaration wytrąca moduł kotwicy hiperprzestrzennej Zold spod kontroli, Go własnym ciałem osłania Zolda, a gdy Takuma i reszta przechodzą na drugą stronę, znika razem z maszyną.

### dic\_pilot\_HAYATE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b007`

> Nowy pilot Klucza Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Znak wywoławczy: Delta 5. Swobodny duch, nie znosi regulaminów. Ma świetne wyczucie dźwięku i rytmu, a jego taneczny styl pilotażu zyskał miano “tańca Immelmanna”. Wierzy, że niebo jest po to, by latać w nim swobodnie, przez co często ściera się z przełożonymi, Messerem i Mirage. Podczas misji tłumienia Syndromu Var na planecie Ionideth poznaje Freyję, która przemyciła się na pokładzie frachtowca.

### dic\_pilot\_HAYATE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b008`

> W trakcie walk zbliża się do Freyi i odkrywa, po co lata. W ostatniej bitwie razem z nią przebija się do rdzenia Sigur Berrentzsa, największej siły Królestwa Windermere, i niszczy go, walnie przyczyniając się do końca wojny.

### dic\_pilot\_MIRAGE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b009`

> Pilotka Klucza Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Znak wywoławczy: Delta 4. Sumienna, bardzo przestrzega regulaminu. Wnuczka Maximiliana Jeniusa, bohatera dawnych wielkich wojen, i czuje ciężar urodzenia w wielkim rodzie Jeniusów. Jako opiekunka nowego pilota, Hayate, ulega wpływowi jego swobodnego stylu życia i zaczyna się w nim podkochiwać.

### dic\_pilot\_MIRAGE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b00a`

> Widząc w trakcie wojny, jak Hayate i Freyja się do siebie zbliżają, zamyka sprawę własnych uczuć, lecz sama odkrywa, po co lata, i uwalnia się od ciężaru, który ją przytłaczał.

### dic\_pilot\_ARAD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00b`

> Pilot i dowódca Klucza Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Znak wywoławczy: Delta 1. Człowiek wielkiego serca, potrafi utrzymać w ryzach pilotów o trudnych charakterach. Prócz dowodzenia sam wyszukuje nowych pilotów. Służył niegdyś w N.U.N.S.; Ernest, kapitan Macross Elysion, to jego towarzysz broni z tamtych czasów.

### dic\_pilot\_MESSA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00d`

> Pilot Klucza Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Znak wywoławczy: Delta 2. Opanowany, świetnie ocenia sytuację; as Klucza Delta. Surowy wobec siebie i innych, szkoli też pozostałych pilotów. Dwa lata temu w walce uległ Syndromowi Var, lecz śpiew Kaname go uspokoił.

### dic\_pilot\_MESSA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b00e`

> Jego umiejętności należą do najlepszych w Kluczu Delta; walczy jak równy z równym z Keithem, Białym Rycerzem Powietrznych Rycerzy. Gdy Syndrom Var powraca, zostaje przeniesiony do innego działu, lecz mimo to przybywa na pole bitwy na planecie Al Shahal. Ratuje Klucz Delta i Walkure z opresji i zestrzeliwuje Keitha, lecz wyniszczony umiera w ramionach Kaname. Jego maszynę przejmuje Hayate.

### dic\_pilot\_CHACK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00f`

> Pilot Klucza Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Znak wywoławczy: Delta 3. Zajmuje się głównie wczesnym ostrzeganiem. Rdzenny mieszkaniec planety Ragna; ma błony pławne i skrzela. Niepoprawnie wesoły, z każdym nawiąże rozmowę. Na co dzień jest kucharzem w lokalu Rag-Nyan Nyan, który prowadzi z młodszym rodzeństwem.

### dic\_pilot\_ARNST\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b011`

> Kapitan okrętu klasy Macross, Macross Elysion, z oddziału Ragna międzygwiezdnego konglomeratu Xaos. Pół Ziemianin, pół Zentradi, o potężnej posturze i równie wielkim sercu. Służył niegdyś w N.U.N.S., a przed pierwszą wojną o niepodległość Windermere był doradcą wojskowym w Królestwie Windermere.

### dic\_pilot\_BESS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b013`

> Operator okrętu klasy Macross, Macross Elysion.

### dic\_pilot\_KEES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b015`

> As Powietrznych Rycerzy, elitarnej formacji podległej bezpośrednio rodowi królewskiemu Windermere. Nosi tytuł Białego Rycerza z Derwent. Wierny rycerskim ideałom, prowadzi Powietrznych Rycerzy do walki z N.U.N.S., które odebrały ojczyźnie pokój. Choć jest najstarszym synem zmarłego króla Grammiera, urodziła go nałożnica, więc tron przypadł Heinzowi. Z kanclerzem Królestwa Windermere, Roidem Brehmem, przyjaźni się od dzieciństwa.

### dic\_pilot\_KEES\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b016`

> Toczy zaciekłe pojedynki z Messerem, asem Klucza Delta, i zestrzelony nad Al Shahal ledwie uchodzi z życiem. Z czasem rozchodzą się jego drogi z Roidem, który chce posłużyć się ruinami Protokultury, by zawładnąć galaktyką. W ostatniej bitwie wspiera Klucz Delta i zabija Roida, lecz obaj giną w eksplozji.

### dic\_pilot\_ROID\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b000`

> Kanclerz Królestwa Windermere. Dowodzi też Powietrznymi Rycerzami, a do tego jest uczonym, specjalistą od badań nad Protokulturą. Wypowiada wojnę N.U.N.G. w chwili, gdy Freyja debiutuje na koncercie Walkure.

### dic\_pilot\_ROID\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b001`

> Pieśń Wiatru króla Heinza daje mu przewagę na froncie, lecz potem chce zmusić Mikumo z Walkure do zaśpiewania Pieśni Gwiazd, by za pomocą systemu pozostawionego przez Protokulturę zawładnąć całą galaktyką. W ostatniej bitwie jego ambicje niweczą Klucz Delta, Walkure i Keith z Powietrznych Rycerzy, który porzucił jego ideały; ginie z ręki Keitha.

### dic\_pilot\_BOAG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b002`

> Najmłodszy pilot Powietrznych Rycerzy, z szanowanego rodu Con-Vaart z Królestwa Windermere. Podczas dawnej wojny stracił rodzinę i otwarcie okazuje gniew i nienawiść wobec N.U.N.G.

### dic\_pilot\_BOAG\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b003`

> W trakcie wojny pieśni Walkure, choć budzą w nim odrazę, wywołują w nim uczucia, których nie potrafi wyjaśnić. W ostatniej bitwie idzie za Keithem, który zerwał z Roidem, i walczy u boku Klucza Delta.

### dic\_pilot\_HELMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b004`

> Najstarszy pilot Powietrznych Rycerzy. Ma 33 lata. Windermerczycy żyją średnio 30 lat, więc należy do najstarszych z nich, a krystalizacja objęła mu już twarz i szyję. Ceni ideały rycerskie i z szacunkiem traktuje tych, których umiejętności uznał.

### dic\_pilot\_KASIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b006`

> Rosły pilot Powietrznych Rycerzy. Jego rodzina prowadzi w rodzinnych stronach sad jabłoni; ma jedynego syna.

### dic\_pilot\_TEO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b008`

> Jeden z bliźniaków w Powietrznych Rycerzach, starszy brat Xao. Pochodzi ze znanego rodu kupieckiego Królestwa Windermere. Ma tatuaż na lewym policzku i zaokrągloną runę po prawej stronie głowy. Na co dzień opanowany i poważny, w walce pokazuje gwałtowną naturę.

### dic\_pilot\_ZAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00a`

> Pilot Powietrznych Rycerzy, młodszy brat bliźniak Thea. Pochodzi ze znanego rodu kupieckiego Królestwa Windermere. Ma tatuaż na prawym policzku i spiczastą runę po lewej stronie głowy. Wojowniczy z natury.

### dic\_pilot\_HINTS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00c`

> Król Windermere. Po śmierci króla Grammiera rok temu zasiadł na tronie mimo młodego wieku. Biały Rycerz, Keith, jest jego przyrodnim bratem. Śpiewa Pieśń Wiatru, która pozwala mu panować nad ludźmi dotkniętymi Syndromem Var. Pragnie szybkiego końca wojny, a na prośbę kanclerza, Roida, śpiewa dalej, choć wyniszcza to jego ciało.

### dic\_pilot\_HINTS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b00d`

> Rezonans ze śpiewem Mikumo i Freyi w ruinach Protokultury na Al Shahal gwałtownie przyspiesza jego krystalizację i przykuwa go do łóżka. W ostatniej bitwie wyczuwa śmierć Roida i Keitha; postanawia sam rządzić Królestwem Windermere i kończy wojnę.

### dic\_pilot\_MIKUMO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00e`

> Główna wokalistka taktycznej jednostki muzycznej Walkure. Jej hasło brzmi: “Śpiew to tajemnica”. Tajemnicza, jej wiek i przeszłość pozostają nieznane; często chodzi własnymi drogami. Śpiewanie znaczy dla niej więcej niż dla kogokolwiek, a jej głos niesie silne fale biofold. Jej oddanie śpiewowi wywiera wielki wpływ na Freyję, nową członkinię Walkure.

### dic\_pilot\_MIKUMO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b00f`

> Naprawdę jest klonem stworzonym z komórek Śpiewaczki Gwiazd, odnalezionych w ruinach Protokultury. Roid, kanclerz Królestwa Windermere, zmusza ją do zaśpiewania Pieśni Gwiazd, chcąc uczynić z niej narzędzie, które zjednoczy świadomość wszystkich istot galaktyki, lecz śpiew Walkure i wołanie przyjaciół przywracają jej samą siebie.

### dic\_pilot\_KANAME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b010`

> Liderka taktycznej jednostki muzycznej Walkure. Jej hasło brzmi: “Śpiew to życie”. Debiutowała solo jako idolka, ale bez powodzenia, i wycofała się ze sceny. Gdy okazało się, że ma wysoki wynik receptora fold, została jedną z założycielek Walkure. Po przyjściu Mikumo oddała jej miejsce głównej wokalistki i skupiła się na prowadzeniu zespołu, choć wciąż z nią rywalizuje.

### dic\_pilot\_KANAME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b011`

> W bitwie o ruiny Protokultury na Al Shahal, by powstrzymać Syndrom Var u Messera, który przybył na ratunek, śpiewa swój solowy debiut, “AXIA ~I love you, I hate you~”.

### dic\_pilot\_REINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b012`

> Członkini taktycznej jednostki muzycznej Walkure. Jej hasło brzmi: “Śpiew to miłość”. Szczególnie przyjaźni się z Makiną; prywatnie też często spędzają czas razem. Przed Walkure była hakerką w dziale cybernetycznym międzygwiezdnego konglomeratu Xaos, lecz wysoki wynik receptora fold zapewnił jej miejsce w zespole. Hakerskich umiejętności nie straciła: potrafi nawet wpleść wirusa w pieśń Walkure.

### dic\_pilot\_REINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b013`

> W ostatniej bitwie razem z Makiną i resztą Walkure ratuje Mikumo i wspiera Klucz Delta.

### dic\_pilot\_MAKINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b014`

> Członkini taktycznej jednostki muzycznej Walkure. Jej hasło brzmi: “Śpiew to nadzieja”. Szczególnie przyjaźni się z Reiną; prywatnie też często spędzają czas razem. Dostała się do zespołu przez przesłuchanie i od samego początku Walkure działa z Kaname i Reiną. Jest też mechaniczką i świetnie dba o maszyny.

### dic\_pilot\_MAKINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b015`

> W bitwie o ruiny Protokultury na Al Shahal, osłaniając Reinę, zostaje ranna i trafia jako jeniec do izolatki w szpitalu Królestwa Windermere. W ostatniej bitwie przyjaciele ją uwalniają, a ona razem z resztą Walkure wspiera Klucz Delta.

### dic\_pilot\_FREIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b000`

> Nowa członkini taktycznej jednostki muzycznej Walkure. Jej hasło brzmi: “Śpiew to energia”. Marzyła o Walkure i, by stanąć do przesłuchania, przemyciła się z rodzinnego Królestwa Windermere na planetę Ragna. Pogodna i ufna jak dziecko. Ma receptor fold, a wysoki wynik zapewnił jej miejsce w Walkure. Mówi z lekkim akcentem, a jej powiedzonko to “na całego”. Z Hayate z Klucza Delta, którego poznała podczas przemytu, wzajemnie dodają sobie otuchy.

### dic\_pilot\_FREIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b001`

> W bitwie na Al Shahal jej prawa dłoń zaczyna się krystalizować, lecz w ostatniej bitwie śpiewa, nie szczędząc życia, i w rezonansie z receptorem fold Hayate wyzwala ogromną moc.

### dic\_pilot\_LLSH\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b002`

> Chłopak, który jako Cesarz Tyran podbił świat i ściągnął na siebie nienawiść całej ludzkości. Był to jednak plan: zniszczyć świat, w którym przemoc rodzi niekończący się łańcuch nienawiści, i stworzyć taki, w którym wszyscy ludzie, bez broni w ręku, budują przyszłość rozmową. Urodził się jako jedenasty książę Świętego Imperium Britannii, supermocarstwa władającego jedną trzecią świata. Gdy jego matkę zamordowano, a ukochana siostra, Nunnally, została kaleką, wysłano go jako zakładnika do Japonii. Tam poznał Suzaku Kururugiego, przyjaciela na całe życie i zarazem największego wroga, i zaznał krótkiego spokoju, który przerwała inwazja Britannii na Japonię, rozpętana przez jego ojca, cesarza Charlesa. W Japonii, obróconej w pole bitwy i kolonię Britannii, porzucił nazwisko Britannia, znak cesarskiego rodu, przyjął nazwisko matki i ukrywał się z Nunnally. Poprzysiągł zemstę ojczyźnie; od przypadkowo spotkanej dziewczyny, C.C., otrzymał Geass, moc absolutnego posłuszeństwa, i jako zamaskowany Zero rozpoczął bunt przeciw Britannii. W końcu doszedł do wniosku, że świat, w którym Nunnally będzie mogła żyć spokojnie, powstanie wtedy, gdy on, skupiwszy na sobie całą nienawiść, zginie z ręki Zero, symbolu sprawiedliwości, którego sam stworzył. Powierzył więc rolę Zero Suzaku i własną śmiercią dopełnił Zero Requiem, które przyniosło światu pokój. Zero Requiem przecięło łańcuch nienawiści: Cesarz Tyran Lelouch, znienawidzony przez wszystkich, zginął z ręki Zero, symbolu sprawiedliwości. Dzięki planowi dwóch chłopców, Leloucha i Suzaku, świat wreszcie zaznał pokoju. Rok po Zero Requiem, w epoce bez wojen i terroru, zwanej “cudownym jutrem”, ciało Leloucha, który powinien był umrzeć, ożywa za sprawą Kodu, przejętego w trakcie jego walk. Gdyby przejęcie Kodu przebiegło prawidłowo, Lelouch stałby się nieśmiertelny jak C.C., lecz zaburzenie w Świecie C sprawiło, że jego dusza została tam uwięziona. C.C. wyrusza więc w podróż po ruinach na całym świecie, by odzyskać jego umysł.

### dic\_pilot\_LLSH\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b003`

> C.C. i Lelouch, którego umysł wciąż nie wraca, przemierzają kolejne ruiny, aż z ostatnią nadzieją trafiają do Królestwa Zilkhstanu, strażnika ruin. Dzięki tamtejszej Bramie Adama Lelouch odzyskuje umysł. By uratować Nunnally, uwięzioną przez kapłankę Zilkhstanu, Shamnę, na krótko znów staje się Zero. Geass Shamny, istoty niepełnej jak on, sprawia mu kłopot, lecz z pomocą Suzaku, Kallen i innych pokonuje ją i uwalnia Nunnally.

### dic\_pilot\_ZERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b004`

> Nowy Zero, w którego wciela się wskrzeszony Lelouch. Uważa, że ktoś, kto umarł i nie jest pewien nawet własnego istnienia, nie powinien wpływać na losy świata, dlatego wraca do roli Zero tylko na pewien czas. Po wszystkim oddaje ją z powrotem Suzaku.

### dic\_pilot\_CC\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b006`

> Dziewczyna posiadająca Kod, który daje nieśmiertelne ciało i moc nadawania Geass. By móc umrzeć, dała Lelouchowi Geass i towarzyszyła mu, chcąc przekazać mu Kod, lecz widząc, jak walczy o lepsze jutro, zmieniła zdanie. Szła z nim jako wspólniczka i była świadkiem jego śmierci w Zero Requiem. Lelouch przejął Kod V.V. za pośrednictwem Charlesa, a mimo to nadal używał Geass, więc sądziła, że nie stał się posiadaczem Kodu, lecz po Zero Requiem jego ciało ożyło. Ciało wróciło, ale umysł nie: Lelouch zachowuje się jak małe dziecko. Przypuszczając, że jego umysł jest uwięziony w Świecie C, rusza na poszukiwanie ruin, przez które można się z nim połączyć. W końcu dociera do Królestwa Zilkhstanu, gdzie znajduje się Brama Adama.

### dic\_pilot\_CC\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b007`

> Tam udaje się jej wskrzesić Leloucha i znów walczy u jego boku, by ocalić Nunnally. Gdy Lelouch traci nadzieję wobec Geass kapłanki Zilkhstanu, Shamny, czyli nieskończonego odrodzenia, C.C. potrząsa nim, przywraca mu ducha walki i prowadzi akcję ratunkową do sukcesu.

### dic\_pilot\_SUZAK\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b008`

> Najlepszy przyjaciel i największy wróg Leloucha. Zaprzyjaźnili się w dzieciństwie, lecz gdy Święte Imperium Britannii najechało Japonię, ich drogi się rozeszły. Aby zakończyć wojnę, zabił własnego ojca, Genbu, ostatniego premiera Japonii. Dręczony tą winą, przyjął zasadę, że “wynik osiągnięty złymi środkami nic nie znaczy”, i wstąpił do armii Britannii, by zmienić ją od środka. Tam znów spotkał Leloucha, lecz nie znając nawzajem swych tożsamości, wielokrotnie ścierał się z nim jako z Zero, aż stracił ukochaną, Euphemię. Jej śmierć sprawiła, że zaczął liczyć się tylko wynik: wydał Leloucha cesarzowi Charlesowi i wspiął się aż do Knights of the Round, najpotężniejszych rycerzy imperium. Konsekwencją jego działań było jednak użycie broni masowej zagłady F.L.E.I.J.A. i śmierć ogromnej liczby ludzi. By odpokutować winy, przeprowadził z Lelouchem Zero Requiem. Odtąd nosi maskę bohatera, Zero; wyrzekł się własnego życia i jako Zero służy pokojowi na świecie. Ochraniając Nunnally podczas wizyty w obozie dla uchodźców, wpada w pułapkę Shalia i razem z nią trafia do niewoli w Królestwie Zilkhstanu.

### dic\_pilot\_SUZAK\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b009`

> Uwolniony przez wskrzeszonego Leloucha, by ocalić Nunnally, znów wsiada do przeklętej maszyny, Lancelota. W Lancelocie siN pokonuje Nagid Shu Mein króla Zilkhstanu, Shalia, który obsesyjnie dąży do bycia najsilniejszym.

### dic\_pilot\_SUZAK\_X\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00a`

> Główny doradca Czarnych Rycerzy. W czarnym Knightmare Frame walczy, by wykorzenić terroryzm i konflikty. Naprawdę to Suzaku, który spełnia życzenie Leloucha.

### dic\_pilot\_ROYD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00c`

> W czasie Zero Requiem wspierał starego znajomego, Suzaku, i zbudował Lancelota Albion, maszynę Suzaku jako Knight of Zero. Ponieważ pomagał Lelouchowi, po Zero Requiem nie dostał żadnego ważnego stanowiska w Zjednoczonej Federacji Narodów. Kanon, nie mogąc na to patrzeć, załatwił mu posadę w prywatnej firmie, lecz przez trudny charakter Lloyd z dnia na dzień jest degradowany i żali się, że nie może porządnie budować Knightmare Frame'ów. Gdy Zero zostaje porwany, Lloyd z Kallen i Sayoko przenika do Królestwa Zilkhstanu.

### dic\_pilot\_ROYD\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00d`

> Razem z Kallen i resztą pomaga potem wskrzesić Leloucha i uratować Nunnally.

### dic\_pilot\_CESIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00e`

> Była członkini zespołu konstruktorów Lancelota. Przed upadkiem Świętego Imperium Britannii pracowała między innymi w Specjalnym Korpusie Techniczno-Ekspedycyjnym, czyli Camelocie, jako asystentka swego przełożonego, Lloyda. Na wieść o porwaniu Nunnally przyłącza się z Lloydem i Niną do akcji ratunkowej.

### dic\_pilot\_CESIL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00f`

> W trakcie akcji zostaje ciężko postrzelona, ale przeżywa.

### dic\_pilot\_NEENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b010`

> Badaczka współpracująca z Cecile. Niegdyś stworzyła broń masowej zagłady F.L.E.I.J.A., lecz po tym, jak zobaczyła wywołane nią zniszczenia, szuka pokojowych zastosowań tej techniki. Dołącza do Leloucha i reszty, by pomóc uratować Nunnally.

### dic\_pilot\_NEENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b011`

> Podczas akcji Qujappat, dowódca oddziału zabójców Królestwa Zilkhstanu, przypiera ją, Lloyda i Cecile do muru, lecz dzięki swojej pomysłowości Nina rozprawia się z wrogami za jednym zamachem.

### dic\_pilot\_SHUNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b012`

> Szef kancelarii Najwyższej Rady Zjednoczonej Federacji Narodów. Był drugim księciem Świętego Imperium Britannii i walczył o panowanie nad światem z Lelouchem, gdy ten został cesarzem, lecz przegrał. Do dziś wiernie spełnia polecenie, które Lelouch wydał mu wtedy za pomocą Geass: “Służ Zero”. Dowiedziawszy się o porwaniu Zero i Nunnally, wysyła Lloyda i resztę do Królestwa Zilkhstanu.

### dic\_pilot\_SHUNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b013`

> Na potrzeby akcji ratunkowej przekazuje Lloydowi i reszcie Gurena Type Special i Lancelota siN.

### dic\_pilot\_NNRY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b014`

> Rodzona siostra Leloucha. Sprzeciwiła się bratu, gdy przejął Święte Imperium Britannii i został cesarzem, lecz przegrała. Podczas parady, na której miała zostać stracona jako buntowniczka, ujrzała, jak Zero zabija brata. Dopiero wtedy zrozumiała jego zamiary i przysięgła służyć ludziom w świecie pokoju. Jako honorowa doradczyni Światowej Agencji Pomocy Humanitarnej odwiedza obóz dla uchodźców, gdzie porywają ją ludzie Zilkhstanu z Shaliem na czele, udający nieznany oddział.

### dic\_pilot\_NNRY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b015`

> Kapłanka Shamna chce wykorzystać ją jako klucz do swobodnego dostępu do Świata C, lecz Lelouch i reszta ją ratują.

### dic\_pilot\_CONERIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b000`

> Była druga księżniczka Świętego Imperium Britannii, przyrodnia siostra Leloucha i Nunnally. Z wiernym Guilfordem i innymi próbowała zamordować cesarza Leloucha, lecz w końcu była świadkiem Zero Requiem, gdy Zero zabił Leloucha. Dziś dowodzi 11. brygadą wojsk lądowych Czarnych Rycerzy, którzy bronią Zjednoczonej Federacji Narodów, i prowadzi oddział biorący udział w akcji ratowania Nunnally.

### dic\_pilot\_CONERIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b001`

> Gdy spotyka wskrzeszonego Leloucha, wciąż ma mu za złe śmierć ukochanej siostry, Euphemii, lecz gdy on odsłania twarz i błaga o pomoc, kładzie kres urazie. By ocalić Nunnally, która jest także jej siostrą, prowadzi oddział Quinn Roses i walczy z Bolvoną Forgnarem, budzącym postrach jako “Brązowy Mur”.

### dic\_pilot\_ARNYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b002`

> Dziewczyna, która należała do Knights of the Round, najpotężniejszych rycerzy Świętego Imperium Britannii. Matka Leloucha, Marianne, ukryła w niej swoją świadomość za pomocą Geass przenoszenia umysłu; gdy świadomość Marianne wychodziła na wierzch, Anya cierpiała na zaniki pamięci. Uwolnił ją od Geass Geass Canceler Jeremiaha, z którym kiedyś walczyła, a po Zero Requiem prowadzi z nim sad pomarańczowy.

### dic\_pilot\_ARNYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b003`

> Razem z Jeremiahem bierze udział w akcji ratowania Nunnally w Królestwie Zilkhstanu, pilotując Mordreda Buildup.

### dic\_pilot\_JEREM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b004`

> W Strefie 11 pod rządami Clovisa przewodził frakcji Czystej Krwi, która w armii Britannii głosiła wyższość Britannijczyków. Gdy Zero odbił Suzaku, oskarżonego o zabójstwo Clovisa, Jeremiah za sprawą Geass wywołał skandal i popadł w niełaskę. Śmiertelnie ranny w walce z Gurenem Mk-II, posłużył jako obiekt doświadczeń nad Geass i przypadkiem zyskał Geass Canceler, moc unieważniania Geass. Z jej pomocą przez pewien czas był zabójcą na usługach V.V., lecz dręczony tym, że nie uchronił przed zamachem czczonej matki Leloucha, Marianne, ślubował wierność jej synowi i został jego sługą. Jeden z nielicznych, którzy znają prawdę o Zero Requiem. W świecie, który zaznał pokoju, prowadzi z Anyą sad pomarańczowy.

### dic\_pilot\_JEREM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b005`

> Bierze udział w akcji ratowania Nunnally w Zilkhstanie; pod dowództwem Leloucha walczy w Sutherlandzie Royal.

### dic\_pilot\_KAREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b006`

> As Czarnych Rycerzy. Pół Britannijka, pół Japonka; kontynuując dzieło brata, Naoto, działała w ruchu oporu przeciw Britannii. W walce poznała Leloucha jako Zero i walczyła o wyzwolenie Japonii w Gurenie Mk-II. Podczas Czarnej Rebelii, zwanej też pierwszą bitwą o Tokio, odkryła, że Zero to Lelouch, lecz uwierzyła w niego, widząc, że walczy dla Nunnally, i dalej była jego siłą jako pilotka Gurena Flight-Type i Gurena S.E.I.T.E.N. Eight Elements. W Zero Requiem nie poznała jednak zamiarów Leloucha, stanęła przeciw niemu i była świadkiem jego śmierci. Po Zero Requiem, by trzymać się z dala od walki, przeszła do rezerwy Czarnych Rycerzy i studiowała, lecz na wieść o porwaniu Zero i Nunnally z Sayoko i Lloydem przeniknęła do Królestwa Zilkhstanu.

### dic\_pilot\_KAREN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b007`

> Tam spotyka C.C. i pomaga wskrzesić Leloucha. Potem bierze udział w akcji ratowania Nunnally i w Gurenie Type Special toczy zaciekły bój z Batalalanem Du Bitoola.

### dic\_pilot\_OUGI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b008`

> Kontynuując dzieło przyjaciela, Naoto, brata Kallen, przewodził ruchowi oporu przeciw Britannii, lecz gnębiło go, że brak mu zdolności. Ujęty charyzmą Zero, nieprzerwanie mu ufał. W trakcie walk zakochał się jednak w Villetcie, która straciła pamięć, i dowiedział się od niej o mocy Geass. Gdy wyszło na jaw, że Zero to Lelouch, ta niepojęta moc sprawiła, że nie potrafił mu dłużej ufać, i wygnał go z Czarnych Rycerzy. W Zero Requiem stanął przeciw Lelouchowi jako zastępca dowódcy Czarnych Rycerzy. Po Zero Requiem został pierwszym premierem Stanów Zjednoczonych Japonii, poślubił Villettę i doczekał się syna, Naoto; wiedzie szczęśliwe życie.

### dic\_pilot\_OUGI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b009`

> Ustąpił z urzędu premiera po około pół roku, a na wieść o porwaniu Zero i Nunnally wziął z Tamakim udział w akcji ratunkowej.

### dic\_pilot\_TAMAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00a`

> Właściciel Cafe ZERO. Członek Czarnych Rycerzy od ich założenia. Ma się za najlepszego przyjaciela Zero i tak w niego wierzył, że gdy Czarni Rycerze zerwali z Zero, szczerze rozpaczał. Po Zero Requiem nie wszedł do nowego rządu Japonii, lecz otworzył kawiarnię z barem, rzekomo we współpracy z Zero, z takim talentem do interesów, że otworzył drugi lokal.

### dic\_pilot\_TAMAKI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b00b`

> Bierze z Ohgim udział w akcji ratunkowej i mimowolnie podsuwa Lelouchowi pomysł użycia łączności wroga.

### dic\_pilot\_RACSHTA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00c`

> Była doradczyni techniczna Czarnych Rycerzy. Dziś pełni mnóstwo funkcji: przewodniczy Światowemu Komitetowi Naukowemu Zjednoczonej Federacji Narodów, doradza Międzynarodowej Organizacji Zdrowia, jest honorową rektor Uniwersytetu Federacji, doradczynią jej biura wolontariatu, członkinią Światowej Agencji Bezpieczeństwa Publicznego i doradczynią ministra zdrowia Stanów Zjednoczonych Indii. Założyła też prywatną organizację Pearl Party, skupiającą genialne dzieci z całego świata. W akcji ratowania Nunnally Frame Coaty załatwiła Shanti, członkini Pearl Party.

### dic\_pilot\_SAYOKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00e`

> 37. mistrzyni szkoły Shinozaki. Jako pokojówka rodu Ashfordów opiekowała się Lelouchem i Nunnally, a potem wstąpiła do Czarnych Rycerzy. Gdy okazało się, że Zero to Lelouch, służyła mu jako tajna agentka; pomagała też przy Zero Requiem i do końca wypełniała jego polecenia. Po Zero Requiem pomagała z ukrycia rozwiązywać konflikty na świecie, lecz na wieść o porwaniu Nunnally z Kallen i Lloydem przeniknęła do Królestwa Zilkhstanu.

### dic\_pilot\_SAYOKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b00f`

> Spotkawszy C.C., pomaga wskrzesić Leloucha i uratować Nunnally.

### dic\_pilot\_MIREY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b010`

> Reporterka. Przyjechała z Rivalzem do Królestwa Zilkhstanu, by zrelacjonować atak na obóz dla uchodźców, w którym porwano Nunnally. Była przewodniczącą samorządu Akademii Ashford, do której chodził Lelouch; opiekuńcza, cieszyła się sympatią uczniów.

### dic\_pilot\_SHRLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b000`

> Dziewczyna Leloucha z czasów Akademii Ashford. Choć wiedziała, że Lelouch to Zero, starała się mu pomagać. Po jego śmierci w Zero Requiem pomogła Jeremiahowi wywieźć ciało. Dlatego do dziś utrzymuje kontakt z C.C.

### dic\_pilot\_SHAMNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b002`

> Kapłanka Królestwa Zilkhstanu i starsza siostra króla, Shalia. Prowadzi Zilkhstan swoim “darem proroctwa”.

### dic\_pilot\_SHAMNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b003`

> Potomkini Farlafu, odłamu Zakonu Geass; ma Geass nieskończonego odrodzenia. W chwili śmierci cofa się w czasie, zachowując wspomnienia, i tak, wracając do przeszłości, “prorokuje”. Pierwotnie był to Geass przewidywania, lecz z czasem przemienił się w tę moc. Pokój zrodzony z Zero Requiem odebrał wartość wojskom najemnym, głównemu towarowi eksportowemu Zilkhstanu; by ocalić królestwo, chce zmienić sam świat. W tym celu próbuje zapanować nad dostępem do Świata C, by swobodnie wybierać, do której chwili się cofa, a jako klucz porywa Nunnally. W końcu Geass Leloucha pogrąża ją w wiecznym śnie. Potem, spotkawszy C.C. w Świecie C, okazuje żal wobec Shalia i wszystkich, którzy oddali za nią życie.

### dic\_pilot\_SHARIO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b004`

> Król Królestwa Zilkhstanu. Od urodzenia słabowity, na co dzień porusza się na wózku inwalidzkim, lecz ma wrodzony talent do pilotowania Knightmare Frame'ów. Dla odpowiedzialności wobec poddanych, by udowodnić sens własnego istnienia i by pomóc ukochanej siostrze, Shamnie, w swoim Nagid Shu Mein dąży do bycia najsilniejszym wojownikiem świata. Dla tego celu gotów jest na wszystko. Bezgranicznie ufa proroctwom Shamny i postępuje dokładnie według nich.

### dic\_pilot\_SHARIO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b005`

> Chce pokonać Suzaku na dowód, że jest najsilniejszy, lecz gdy Lelouch pokonuje Shamnę, Shalio zostaje bez proroctw i przegrywa z Suzaku w Lancelocie siN.

### dic\_pilot\_SHESTA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b006`

> Dowódca gwardii przybocznej kapłanki Królestwa Zilkhstanu, Shamny. Syn wielkiego generała Bolvony Forgnara. Zarozumiały, przecenia własne możliwości.

### dic\_pilot\_SHESTA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b007`

> Otacza więzienie, które zajął Lelouch ze swoimi ludźmi, i żąda kapitulacji. Lekceważy jednak przeciwnika i ulega fortelowi Leloucha.

### dic\_pilot\_BOLBNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b008`

> Wielki generał Królestwa Zilkhstanu. Cieszy się zaufaniem Shamny, Shalia i żołnierzy; to jeden z filarów królestwa.

### dic\_pilot\_BOLBNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b009`

> W akcji ratowania Nunnally wychodzi naprzeciw oddziałowi Cornelii i staje z nią do pojedynku. By ją zgładzić, każe żołnierzom strzelać razem z nim samym, lecz ci, bojąc się utracić ostatni mur obronny Zilkhstanu, nie wykonują rozkazu.

### dic\_pilot\_KJAPAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00a`

> Dowódca oddziału zabójców Królestwa Zilkhstanu. Jego Geass zamienia w oczach przeciwnika twarze wrogów i sojuszników; użył go w walce z Kallen i resztą, którzy przeniknęli do Zilkhstanu.

### dic\_pilot\_KJAPAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00b`

> Przypiera do muru Lloyda i resztę podczas akcji ratowania Nunnally, lecz ulega pomysłowości Niny.

### dic\_pilot\_BITUL\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00c`

> Naczelnik wielkiego więzienia Królestwa Zilkhstanu. Był hersztem bandy rozbójników, którą Zilkhstan kupił razem z nim, lecz zrobił z więzienia swoją kryjówkę i rządzi w nim, jak chce. Prostacki samolub, a zarazem siłacz, groźny zarówno wręcz, jak i w Knightmare Frame. W walce pilotuje Knight Gigafortress Batalalan Du.

### dic\_pilot\_BITUL\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00d`

> Gdy Kallen przenika do więzienia, by wskrzesić Leloucha, pokonuje ją w walce wręcz, lecz podczas akcji ratowania Nunnally przegrywa z jej Gurenem Type Special.

### dic\_pilot\_ZEE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00e`

> Podwładny Bitoola. Bystry, na jego rozkaz kieruje ludźmi w więzieniu. Zaprawiony w walce, mierzył się wręcz z Sayoko.

### dic\_pilot\_ZEE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00f`

> Odbiera sobie życie pod wpływem Geass wskrzeszonego Leloucha.

### dic\_pilot\_IZURU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b010`

> Pilot Red 5. Ma 16 lat. Lider Team Rabbits; szczerością i niezmiennym optymizmem trzyma drużynę razem. Ma wyjątkową zdolność koncentracji i najwyższy w drużynie poziom harmonii. Gdy uczył się w Akademii Glanzehre, naczytał się mangi o bohaterach i zamarzył, by sam nim zostać; to marzenie pcha go do walki. Zawsze pozytywny i niewinny, przez co często coś palnie, a cała drużyna go za to beszta. Rysuje mangę, ale tak źle, że nikt jej nie chwali. Dzięki licznym misjom z przyjaciółmi bardzo dojrzał, zarówno jako członek drużyny, jak i jako człowiek.

### dic\_pilot\_IZURU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b011`

> Jako jedyny dorównuje potężnemu Jiartowi, który uznał go za swoją zwierzynę. Jego matką jest Wulgaru, Teoria, a ojcem komandor Simon, więc jest przyrodnim bratem Asagiego. Przed ostatnią bitwą wykryto u niego zaburzenia wywołane gwałtownym wzrostem poziomu harmonii i kazano mu czekać na Godinionie, lecz rusza do walki, by ratować przyjaciół z opresji. W starciu z Jiartem budzi się w nim ukryta moc; przemienia Red 5 w jego prawdziwą postać i zwycięża.

### dic\_pilot\_ASAGI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b012`

> Pilot Blue 1. Ma 17 lat. W Team Rabbits gra rolę “napastnika” i walczy wręcz na pierwszej linii. Świetnie pilotuje i ma rozległą wiedzę, ale nie radzi sobie z presją i rzadko pokazuje pełnię możliwości. Opanowany, poważny i najbardziej “normalny” w drużynie, więc to on przywołuje resztę do porządku. Ma jednak tremę i wiecznie skręca go w żołądku, dlatego nigdzie nie rusza się bez leków na żołądek.

### dic\_pilot\_ASAGI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b013`

> Gnębiło go, że Izuru coraz bardziej go przerasta, lecz po rozmowie z kapitan Suzukaze uznał go za asa i postanowił go wspierać. Uwolniony od rozterek, bardzo dojrzał. Później okazało się, że ma z Izuru wspólne geny, przekazane przez komandora Simona, więc jest jego przyrodnim bratem.

### dic\_pilot\_KEI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b000`

> Pilotka Purple 2. Ma 16 lat. W Team Rabbits odpowiada za “kontrolę”: analizuje przebieg walki i kieruje sojuszniczymi maszynami. Ma znakomitą orientację przestrzenną i słuch; potrafi nawet wyłowić uchem szczególne fale radiowe. Chłodna, ale troszczy się o przyjaciół: pilnuje Tamaki i martwi się o zdrowie Asagiego. Uwielbia słodycze; piecze ciasta tak przesłodzone i krzykliwie kolorowe, że nikt ich nie chwali, choć ona sama tego nie zauważa.

### dic\_pilot\_KEI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b001`

> Odkąd Izuru wyratował ją z opresji, nieśmiało się w nim podkochuje.

### dic\_pilot\_TAMA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b002`

> Pilotka Rose 3. Ma 15 lat. W Team Rabbits jest “dopalaczem”: szybkimi szarżami rozbija szyki wroga. Ma świetny refleks wzrokowy i odporność na przeciążenia; wytrzymuje nawet 20 G przy przyspieszaniu maszyny. Beztroska i ufna jak dziecko, działa instynktownie, choć czasem trafia w sedno. Marzy o miłości i łatwo się zakochuje: każdemu przystojniakowi od razu wyznaje uczucia i za każdym razem dostaje kosza. Uwielbia solone kałamarnice shiokara, które je z górą białego ryżu.

### dic\_pilot\_TAMA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b003`

> Po śmierci Patricka zrozumiała, że się w niej kochał, i zwierzyła się Kei ze swojego żalu i smutku. W operacji Heaven's Gate, wbrew rozkazom Asagiego, ścigała Lutiel, by pomścić Patricka, i ostatecznie ją pokonała.

### dic\_pilot\_SRUGA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b004`

> Pilot Gold 4. Ma 16 lat. W Team Rabbits jest “strzelcem” i wspiera drużynę ogniem dalekiego zasięgu z tylnej linii. Ma fenomenalną pamięć i jest maniakiem militariów; zna parametry każdej broni, a gdy rozmowa schodzi na jego konik, mówi jak karabin maszynowy. Wesoły podrywacz, zaczepia każdą piękną kobietę, ale nigdy z sukcesem. W gruncie rzeczy niewinny; nie potrafi nawet patrzeć na treści dla dorosłych. Uwielbia curry, a gotowe z torebki woli od wykwintnego.

### dic\_pilot\_SRUGA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b005`

> Snajperskimi strzałami odnosi wielkie sukcesy: z kosmosu zestrzelił na powierzchni Ziemi dowódcę armii Wulgaru, Kleina, a łącząc się z systemami Godiniona, zniszczył też Lutiel.

### dic\_pilot\_ANJU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b006`

> Pilot Black 6. Ma 15 lat. Dołącza do Team Rabbits jako dodatkowy członek. Na co dzień cichy i nieśmiały charakter w kokpicie AHSMB zamienia się w agresję i potok wyzwisk. Wielka siła w walce indywidualnej idzie w parze z brakiem umiejętności współpracy, więc na polu bitwy Ange często działa na własną rękę. Świetnie zna się na broni, strzela po mistrzowsku i osobiście dba o swoją maszynę. Płeć Ange pozostaje nieznana.

### dic\_pilot\_ANJU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b007`

> W ostatniej bitwie razem z Chandrą z Team Doberman prowadzi oddział seryjnych AHSMB.

### dic\_pilot\_RANDY\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b008`

> Lider Team Doberman. Swobodny wesołek; przez jego zachowanie drużynę przezywa się czasem “Trójką Kabaretową” albo “Trójką Rozczarowań”. Jako pilot jest jednak wybitny i ma na koncie wiele sukcesów. Troskliwy wobec młodszych: Izuru, młodszemu koledze z Akademii Glanzehre, opowiadał o bohaterach, a nawet pożyczał mu swoją tajną kolekcję.

### dic\_pilot\_RANDY\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b009`

> W operacji Eagle Landed, siłowym rozpoznaniu bramy Wulgaru, walczy jak lew do samego końca, nie tracąc nadziei na powrót, lecz ta nadzieja się nie spełnia.

### dic\_pilot\_CHNDR\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00a`

> Zastępca lidera Team Doberman. Sumienny i opanowany, uważa się za tego, który sprowadza wygłupy Randy'ego na ziemię. Świetny analityk taktyczny, wspiera drużynę z tyłu: ocenia sytuację i dzieli się informacjami. Kocha całym sercem swoją pulchną narzeczoną, która mieszka na Ziemi.

### dic\_pilot\_CHNDR\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00b`

> Jako jedyny z drużyny przeżywa operację Eagle Landed i przywozi do MJP kluczowe dane. W ostatniej bitwie dzielnie prowadzi oddział seryjnych AHSMB.

### dic\_pilot\_PTRIC\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00c`

> Członek Team Doberman. Rozkojarzony safanduła, często mówi coś nie w porę. Młodszy od Randy'ego i Chandry; w drużynie działa jako wolny strzelec, wspierając Randy'ego z przodu i Chandrę z tyłu.

### dic\_pilot\_PTRIC\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00d`

> W trakcie wojny potajemnie zakochuje się w Tamaki. Po operacji Eagle Landed zamierzał wyznać jej uczucie, wręczając w prezencie solone kałamarnice shiokara, lecz zginął od ataku dowódczyni armii Wulgaru, Lutiel.

### dic\_pilot\_SIMON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00e`

> Dowódca MJP w stopniu pułkownika. Przygotowując obronę przed inwazją Wulgaru na Ziemię, kierował budową AHSMB i szkoleniem pilotów. Przez dawne rany nie rozstaje się z metalowymi goglami z układem wspomagającym i laską. Pod chłodnym spokojem skrywa żelazną determinację.

### dic\_pilot\_SIMON\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00f`

> To jego geny posłużyły do stworzenia Izuru i Asagiego; genetycznie jest ich ojcem. W ostatniej bitwie dowodzi całością sił, a w kulminacji, gotów na śmierć, taranuje bramę przerzutową Wulgaru Star Rose przerobioną na okręt-matkę, zapewniając sukces operacji. Był gotów oddać życie, lecz w ostatniej chwili ratuje go Teoria.

### dic\_pilot\_SZKAZE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b010`

> Kapitan Godiniona w stopniu majora. Ma 28 lat. Jako instruktorka w Akademii Glanzehre szkoliła pilotów, a gdy jej podopieczni, Team Rabbits, trafili na front, przeniesiono ją razem z nimi. Jako pilotka GDF jako jedyna przeżyła starcie z Wulgaru, lecz odniesione rany zmusiły ją do zejścia z pierwszej linii. Surowo szkoli Izuru i resztę, ale znając ich pochodzenie, cierpi, posyłając ich do walki. Z szefową mechaników, Reiką, przyjaźni się od dzieciństwa i często się jej zwierza; po kilku kieliszkach płacze i wyrzuca z siebie słabości, których na co dzień nie okazuje. Nie pozwala Reice nazywać się “Rin-Rin”. Zawsze nosi przy sobie lizaki i częstuje nimi podwładnych, by rozładować napięcie.

### dic\_pilot\_ZIKFRT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b012`

> Łącznościowiec Godiniona w stopniu porucznika. Sumienny; nawet po służbie załatwia sprawy związane z pracą, a przy tym zapamiętale ćwiczy na siłowni. Świetnie przetwarza informacje i razem z Giulianem, nierozłącznym kompanem jeszcze ze szkoły wojskowej, melduje kapitan Suzukaze o sytuacji na polu bitwy i nawigacji okrętu.

### dic\_pilot\_JRIANO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b000`

> Łącznościowiec Godiniona w stopniu porucznika. Ma świetną intuicję i talent do sterowania okrętem; sądząc po ocenach, był największym geniuszem w historii szkoły wojskowej. Wtedy jednak sprawiał kłopoty wychowawcze, a kolega, Siegfried, tuszował jego wybryki. Lubi koty, a wobec kobiet jest szarmancki i bezpośredni. Nazywając przepadającą za przystojniakami Tamaki “kociątkiem”, pomaga podnieść jej poziom harmonii.

### dic\_pilot\_REIKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b002`

> Szefowa mechaników Godiniona w stopniu kapitana. Odważna, opiekuńcza i mocna w piciu, a przy tym taktowna. Podwładni mechanicy, którzy mogą na niej polegać, mówią na nią “Szefie”. Przyjaciółka Suzukaze z dzieciństwa i z rocznika w szkole oficerskiej, jej powierniczka; nazywa ją “Rin-Rin”, choć Rin protestuje. Podczas walki monitoruje z mostka przebieg starcia i poziom harmonii każdego AHSMB. Dziedziczka wielkiej firmy farmaceutycznej Saionji z Kioto.

### dic\_pilot\_RURA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b004`

> Lekarka wojskowa Godiniona. Dba o zdrowie fizyczne i psychiczne Team Rabbits i mierzy ich dostosowanie do systemu Juria. Była na tym samym roku w szkole oficerskiej co Suzukaze i Reika.

### dic\_pilot\_DANN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b006`

> Jeden z mechaników Red 5. Fachowiec w każdym calu. Choć wygląda zwyczajnie, nosi długie i skomplikowane nazwisko.

### dic\_pilot\_MAYU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b008`

> Jedna z mechaniczek Red 5. Wesoła i bezpośrednia, nazywa Izuru przezwiskami w rodzaju “Izurek”, “Iziu” czy “Izuś”. Ma świetną intuicję mechanika: szybko znajduje usterkę i jej przyczynę. Pochodzi z Furano, gdzie mieści się siedziba MJP; jej rodzice też tam pracują. Od dawna nie była w domu, więc mechanika Degawę traktuje jak ojca, a Dana jak starszego brata.

### dic\_pilot\_DEGAWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00a`

> Jeden z mechaników Red 5. Najlepiej radzi sobie z pracą fizyczną, więc przy naprawach zwykle pomaga Danowi i Mayu. Lubi haiku i mówi rytmem 5-7-5, lecz zwykle bez słowa na określenie pory roku, więc wychodzą mu senryu.

### dic\_pilot\_AMANE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00c`

> Oficer wywiadu w Połączonym Sztabie Generalnym GDF. Adiutantka zastępcy szefa sztabu, pułkownika Komine, choć to ona wykonuje większość pracy. Zajmuje się głównie zbieraniem informacji i planowaniem operacji, ale często dowodzi też oddziałami na froncie. Suzukaze i jej koleżanki były w szkole oficerskiej rok wyżej; często razem chodzą na drinka.

### dic\_pilot\_AMANE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00d`

> W ciągu jednego dnia awansuje z kapitana na pułkownika i w ostatniej bitwie dowodzi flotą.

### dic\_pilot\_KOMINE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00e`

> Zastępca szefa Połączonego Sztabu Generalnego GDF w stopniu pułkownika. Przełożony Amane; dowodzi oddziałami w polu, ale planowanie operacji w dużej mierze zostawia jej. Zapatrzony w zasługi i własną skórę, nieraz źle ocenia sytuację.

### dic\_pilot\_KOMINE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00f`

> W operacji Night Blow, choć źle ocenił siły wroga, przeforsował jej kontynuację i omal nie doprowadził Team Rabbits do zagłady. W bitwie o Ceres, zaskoczony atakiem Wulgaru, rozpoczął walkę przed czasem, stawiając całą armię w trudnym położeniu; potem odsunięto go od dowodzenia na froncie.

### dic\_pilot\_TEORIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b010`

> Tajemnicza dziewczyna. Zanim wymazano Izuru pamięć, byli sobie bliscy, a on przysiągł, że zawsze będzie ją chronił.

### dic\_pilot\_TEORIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b011`

> Naprawdę to księżniczka Wulgaru (Prae Exousia), która zbiegła na Ziemię, młodsza siostra Jiarta. Na tajny rozkaz matki, której serce krwawiło na widok łowów Wulgaru, niszczących kolejne gatunki, przekazała Ziemi informacje o Wulgaru. Dała MJP technikę, z której powstał system Juria, a także własne geny do wyhodowania pilotów; genetycznie jest matką Izuru. W ostatniej bitwie sama rusza do walki w maszynie bojowej i ratuje życie Simona, który poświęcił się w samobójczym ataku.

### dic\_pilot\_DANIEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b012`

> Kamerdyner Teorii. Jest też jej ochroniarzem i mistrzem walki wręcz. Zawsze na pierwszym miejscu stawia jej bezpieczeństwo.

### dic\_pilot\_DANIEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b013`

> Podobnie jak Teoria jest Wulgaru i razem z nią zbiegł na Ziemię. W ostatniej bitwie walczy z Wulgaru w maszynie bojowej.

### dic\_pilot\_ZIAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b014`

> Drugi książę Wulgaru (Prae Exous), przyrodni brat cesarza Galkiego. Wojowniczy, idzie za instynktem i pragnieniami. W walce kieruje się własną estetyką i nie zwraca uwagi na słabych wrogów, niegodnych walki.

### dic\_pilot\_ZIAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b015`

> Szuka godnego rywala i spotkawszy na polu bitwy Izuru, uznaje go za swoją “lamatę”, zwierzynę łowną. Ma obsesję na punkcie siostry, Teorii; podejrzewał, że jest na Ziemi, nim jeszcze Lumes dostarczył mu informacji. W ostatniej bitwie w maszynie w trybie Overlord toczy zaciekły bój z Izuru, lecz przegrywa.

### dic\_pilot\_GALKIE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b016`

> Cesarz Wulgaru, przyrodni brat Jiarta. Bezwzględny racjonalista, nie cofa się przed zimnymi decyzjami; władzę zdobył, zlecając zabójstwo ojca, poprzedniego cesarza. Po wyroczni, która nadchodzi raz na 300 lat, postanowił najechać Ziemię. Nie gani Jiarta za samowolę, lecz milcząco ją toleruje, a Jiart darzy go za to pewnym szacunkiem.

### dic\_pilot\_GALKIE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b017`

> Gdy w ostatniej bitwie Ziemianie niszczą bramę przerzutową, łowy trzeba przerwać, lecz Galkie dostrzega w Ziemianach szansę na ewolucję Wulgaru.

### dic\_pilot\_CLAIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b018`

> Przywódca 11. klanu Wulgaru i jeden z dowódców armii (Legatów). Specjalizuje się w atakach z zaskoczenia z przytłaczającą szybkością i w dezorientowaniu wroga. Porywczy i okrutny, nie znosi, gdy ktoś go uprzedza.

### dic\_pilot\_CLAIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b019`

> W walce upatruje sobie jako zwierzynę Black 6 pilotowane przez Ange. Potem atakuje Akademię Glanzehre, lecz ulega zgranemu atakowi Team Rabbits i strzałowi Surugi z ekstremalnej odległości.

### dic\_pilot\_RADA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b000`

> Przywódca 13. klanu Wulgaru i jeden z dowódców armii (Legatów). Histeryczny sadysta, lubi podłą taktykę: najpierw dręczy przeciwnika, a potem go unicestwia.

### dic\_pilot\_RADA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b001`

> Podsłuchał rozmowę Jiarta z Lumesem i dowiedział się, gdzie jest Teoria; Jiart zabił go, by zamknąć mu usta.

### dic\_pilot\_LUTEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b002`

> Jedna z dowódczyń armii Wulgaru (Legatów). Miarą wszystkiego jest dla niej piękno, także w walce. Specjalizuje się w taktyce przytłaczania wroga szybkością.

### dic\_pilot\_LUTEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b003`

> Jej siła pozwala przytłoczyć Team Doberman w operacji Eagle Landed; zestrzeliwuje Patricka. W ostatniej bitwie zgrany atak Asagiego, Tamaki i Ange odbiera jej swobodę ruchów, a Suruga, kierując działem głównym Godiniona, ją zestrzeliwuje.

### dic\_pilot\_RUMES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b004`

> Jeden z dowódców armii Wulgaru (Legatów). Przebiegły racjonalista, specjalizuje się w obronie manewrowej z tyłu frontu. Pochodzi z klanu służącego rodzinie cesarskiej Wulgaru i wykonuje tajne rozkazy Jiarta.

### dic\_pilot\_RUMES\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b005`

> Atakuje bazę Vesta, ziemską kopalnię paliwa, i zdobywa dane o MJP, co prowadzi do ataku na Akademię Glanzehre. W ostatniej bitwie dowodzi oddziałami Kleina i Rady, pozbawionymi dowódców, odpowiada za obronę manewrową i wsparcie z tyłu; jego obrona jest nie do przebicia, odpiera nawet ziemskie pociski podświetlne.

### dic\_pilot\_DOLGN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b006`

> Jeden z dowódców armii Wulgaru (Legatów), najpotężniejszy z generałów. Wierny wojownik; pod rozkazami cesarza Galkiego planuje operacje i dowodzi na froncie. Weteran wielu kampanii, specjalizuje się w natarciu czołowym wielkimi siłami.

### dic\_pilot\_DOLGN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b007`

> W ostatniej bitwie dowodzi obroną bramy. Sam rusza do walki w maszynie bojowej i robi wszystko, by powstrzymać atak Star Rose, lecz po skoncentrowanym ostrzale Black 6 i Rhinos podwładni ewakuują go w swoich maszynach.

### dic\_pilot\_MEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b008`

> Doktorantka badająca stworzenia fantastyczne. Pogodna i genialna, choć trochę roztrzepana. Gdy w zastępstwie profesora przyjeżdża do obserwatorium radiowego Misakioku, zostaje wciągnięta w kryzys, który kaiju sprowadzają na świat. Razem z partnerem, Pelopsem II, który powstał, gdy zainstalowała z sieci asystenta komunikacji SI Naratake stworzonego przez Yuna Arikawę, próbuje rozwikłać anomalie zachodzące na świecie.

### dic\_pilot\_MEI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b009`

> Gdy Pelops II zbiera jej pomysły o stworzeniach fantastycznych w artykuł i go publikuje, profesor Li, czołowa znawczyni badań Ashihary, zaprasza ją do wspólnych badań. Zbierając i analizując informacje z Pelopsem II, odkrywa cel Ashihary, a potem z BB z ośrodka Upala wyrusza tam, gdzie znajduje się Nadwymiarowy Kalkulator. By zapobiec rozprzestrzenieniu się Czerwonego Pyłu i Katastrofie z rąk Godzilli, rozszyfrowuje kod potrzebny do ukończenia Orthogonal Diagonalizera i walnie przyczynia się do powstrzymania Katastrofy.

### dic\_pilot\_PERO2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00a`

> Sztuczna inteligencja zrodzona z asystenta komunikacji SI Naratake, z awatarem w postaci psa. Mieszka w komputerze Mei i jako jej partner wspiera ją we wszystkim. Imię Pelops II wzięło się od Pelopsa, psa, którego Mei kiedyś miała.

### dic\_pilot\_PERO2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00b`

> Po podróży z Mei przenika do Nadwymiarowego Kalkulatora konsorcjum SHIVA i analizuje, jak uniknąć Katastrofy. W końcu odkrywa “protokół, który uczyni Jet Jaguara najsilniejszym”, łączy się z Jet Jaguarem Yungiem i odgrywa kluczową rolę w powstrzymaniu Katastrofy z rąk Godzilli.

### dic\_pilot\_PERO2R\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00c`

> Sztuczna inteligencja zrodzona z asystenta komunikacji SI Naratake. Mieszkał w komputerze Mei, lecz gdy konsorcjum SHIVA dało mu ciało, może poruszać się samodzielnie.

### dic\_pilot\_PERO2R\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00d`

> Po podróży z Mei przenika do Nadwymiarowego Kalkulatora konsorcjum SHIVA i analizuje, jak uniknąć Katastrofy. W końcu odkrywa “protokół, który uczyni Jet Jaguara najsilniejszym”, łączy się z Jet Jaguarem Yungiem i odgrywa kluczową rolę w powstrzymaniu Katastrofy z rąk Godzilli.

### dic\_pilot\_YUN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00e`

> Inżynier z Otaki Factory. Geniusz o szerokich horyzontach: buduje roboty, projektuje oprogramowanie sterujące, tworzy SI i wiele więcej. Bystry obserwator, ale ma kłopoty w kontaktach z ludźmi. Gdy bada rezydencję, o której mówi się, że jest nawiedzona, zostaje wciągnięty w walkę z kaiju.

### dic\_pilot\_YUN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00f`

> Przenosi do Jet Jaguara Yunga, instancję opracowanego przez siebie asystenta komunikacji SI Naratake, i staje do walki z kaiju. Nigdy nie spotkał Mei osobiście, a jednak, rozmawiając z nią na czacie, wspólnie rozwiązują zagadki. W ostatniej bitwie z Godzillą towarzyszy Jet Jaguarowi, by odebrać wiadomość nad stacją Tokio, i zapobiega Katastrofie.

### dic\_pilot\_JJAGUAR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b010`

> Robot zbudowany przez Otakiego, szefa Otaki Factory, z myślą o “obronie Ziemi”. Miał wystąpić na letnim festynie, lecz walka z kaiju sprawiła, że przerobiono go na maszynę bojową. Po kilku przeróbkach z maszyny załogowej stał się bezzałogową, sterowaną przez SI. Jego interfejs rozmowy to Yung, instancja asystenta komunikacji SI Naratake stworzonego przez Yuna Arikawę.

### dic\_pilot\_JJAGUAR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b011`

> W walkach z kaiju wielokrotnie ratował Otaki Factory i ludzi. W ostatniej bitwie z Godzillą “protokół, który uczyni Jet Jaguara najsilniejszym”, odkryty przez Pelopsa II, łączy go z Pelopsem II w olbrzymiego Jet Jaguara PP. Gdy pojmuje, że kodem Orthogonal Diagonalizera, potrzebnym do uniknięcia Katastrofy, jest on sam, uruchamia go i ocala świat.

### dic\_pilot\_HABEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b012`

> Inżynier elektronik z Otaki Factory. Dla przyjemności ćwiczy na siłowni; w liceum przezywano go “Sztangą”. Jako partner Yuna Arikawy stawia wraz z nim czoło zagrożeniu ze strony kaiju.

### dic\_pilot\_HABEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b013`

> Montuje na motocyklu Otaki Factory specjalne anteny przeciw Rodanom i ratuje ludzi przed kaiju. Chodził z Mei do jednej klasy w liceum i to on domyśla się, że “Kamimushi”, z którą Yun pisze na czacie, to ona.

### dic\_pilot\_OTAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b014`

> Szef Otaki Factory. Pracownicy, Yun i reszta, mówią na niego “Pan O”. Choć to światowej sławy naukowiec z wieloma patentami, uwielbia tematy paranormalne i bez reszty oddaje się “obronie Ziemi”. To on zbudował Jet Jaguara i pilotował go, gdy był maszyną załogową. Gdy Jet Jaguara przerobiono na maszynę sterowaną przez SI, nadal razem z Yunem i resztą poluje na kaiju.

### dic\_pilot\_SATOMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b016`

> Pracownica biura Otaki Factory. Gdy Yun i reszta wyjeżdżają na akcję, pilnuje biura. Lubi styl punk, a jej życie prywatne to zagadka. Hobby: wiązanie ozdobnych węzłów mizuhiki.

### dic\_pilot\_SATO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b018`

> Główny pracownik w Misakioku. Urzędnik Ministerstwa Spraw Zagranicznych, oddelegowany do obserwatorium; podwładny Yukie Kanoko. Alarmy w Misakioku sprawiają, że dowiaduje się o kościach olbrzymiego stworzenia pod ziemią i o Ashiharze, i zaczyna zgłębiać tę zagadkę.

### dic\_pilot\_KANOKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b000`

> Urzędniczka Ministerstwa Spraw Zagranicznych, przełożona Sata. Podąża śladem Ashihary, badając możliwość inwestycji w przełomowy nowy materiał zwany Archetypem. Zna od dawna Yoshiyasu Matsubarę z Sił Samoobrony.

### dic\_pilot\_KANOKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b001`

> Na wykładzie o Archetypie w Dubaju spotyka Mei, zaproszoną tam przez profesor Li. Potem odbiera od BB Orthogonal Diagonalizer i przewozi go do Japonii.

### dic\_pilot\_KAITAKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b002`

> Samozwańczy niezależny dziennikarz. Śledzi poczynania kaiju, lecz jego tożsamość i cele są nieznane. W imieniu profesor Li przekazuje Mei zaproszenie do Dubaju.

### dic\_pilot\_KAITAKE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b003`

> Ma też kontakty z ludźmi z konsorcjum SHIVA, raz po raz styka się z Yunem i resztą walczącymi z kaiju, a w ruinach Upala w Indiach powierza los świata Mei i jej towarzyszom. Gdy zagrożenie ze strony Godzilli mija, wygląda na to, że knuje coś z tajemniczymi ludźmi.

### dic\_pilot\_REEKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b004`

> Badaczka i doradczyni konsorcjum SHIVA, czołowa znawczyni badań Ashihary. Przeczytawszy w sieci artykuł Mei, dostrzega jej talent i zaprasza ją do Dubaju.

### dic\_pilot\_REEKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b005`

> Prowadzi Mei do londyńskiej rezydencji odziedziczonej po Ashiharze i powierza jej ogrom materiałów badawczych. Wierzyła, że Nadwymiarowy Kalkulator pozwoli uniknąć Katastrofy, lecz w trakcie działań zginęła w ataku Rodana.

### dic\_pilot\_BB\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b006`

> Szef działu badań ośrodka Upala w Indiach. Specjalista od Archetypu i zagorzały zwolennik Ashihary. Wybitny, ale dumny; nie znosi ludzi mądrzejszych od siebie.

### dic\_pilot\_BB\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b007`

> Na podstawie artykułu Mei przeprowadza próbę Orthogonal Diagonalizera. Gdy zbliża się Katastrofa, na własną rękę rozsyła Orthogonal Diagonalizery po całym świecie. Sam razem z Mei analizuje Nadwymiarowy Kalkulator i przyczynia się do uniknięcia Katastrofy.

### dic\_pilot\_REENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b008`

> Córka BB. Po ojcu ma odwagę i ciekawość świata. Gdy BB pochłaniają badania, gotuje mu i dba o dom.

### dic\_pilot\_REENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b009`

> Odprowadza Mei do BB, a potem razem z nimi schodzi w najgłębsze rejony ruin Upala i pomaga uniknąć Katastrofy.

### dic\_pilot\_MATBR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00a`

> Pułkownik Lądowych Sił Samoobrony. Stoi na pierwszej linii obrony Japonii. Poważny i rzetelny. Zna od dawna Kanoko z Ministerstwa Spraw Zagranicznych, która nazywa go “Miho”.

### dic\_pilot\_TILDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00c`

> Przewodnicząca konsorcjum SHIVA, której podlega ośrodek Upala w Indiach. Konserwatywna, często ściera się z BB.

### dic\_pilot\_TILDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b00d`

> Ukończenie Orthogonal Diagonalizera stawia ponad bezpośrednią walkę z Katastrofą.

### dic\_pilot\_GAUMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00e`

> Mężczyzna, który nazywa siebie “władcą kaiju”. Szuka pewnej osoby i nie rozstaje się z figurką smoka, którą od niej dostał. Choć zachowuje się szalenie, jest poważny i wierny honorowi i przyjaźni. Utracił moc władcy kaiju; Yomogi znalazł go, gdy padł z głodu. Gdy w mieście pojawia się kaiju, wsiada do Dynazenona, zrodzonego z figurki smoka, i wciąga do walki Yomogiego, Yume i Koyomiego, którzy akurat byli w pobliżu. Jest głównym pilotem Dynazenona, a po rozłączeniu steruje okrętem podwodnym Dyna Diver, który tworzy nogi robota. Mieszka pod mostem nad rzeką i dorabia w kilku miejscach naraz.

### dic\_pilot\_GAUMA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b00f`

> 5000 lat temu walczył z Klubem Kaiju, który zbuntował się przeciw krajowi, chcącemu pozbyć się władców kaiju; zginął razem z przeciwnikami, lecz moc kaiju wskrzesiła go w naszych czasach. Szuka “księżniczki”, której ślubował wspólną przyszłość, lecz do końca jej nie odnajduje. Przed ostatnią bitwą słabnie tak, że nie może nawet pilotować Dynazenona, a mimo to postanawia walczyć, by wszystko rozstrzygnąć. Po ostatniej walce z Gagulą jego ciało dociera jednak do kresu sił i Gauma znika sprzed oczu Yomogiego i reszty.

### dic\_pilot\_YOMOGI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b010`

> Uczeń pierwszej klasy publicznego liceum Fujiyokidai. Łagodny, ma wielu przyjaciół. Mieszka z mamą i babcią, ale chce się usamodzielnić, więc dorabia w supermarkecie Yuri Mart. Gdy pod mostem nad rzeką pomaga Gaumie, który padł z głodu, zostaje wciągnięty w walkę z kaiju. Po rozłączeniu Dynazenona steruje smoczym humanoidem Dyna Soldier.

### dic\_pilot\_YOMOGI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b011`

> W walkach z kaiju odkrywa w sobie zadatki na władcę kaiju; w ostatniej bitwie tą mocą odbija atak Gaguli i daje drużynie okazję do kontrataku. Stopniowo zakochuje się w koleżance z klasy, Yume; przed ostatnią bitwą wyznaje jej uczucie, a po walkach są już sobie tak bliscy, że mówią do siebie po imieniu.

### dic\_pilot\_YUME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b012`

> Koleżanka Yomogiego z klasy. Umawia się z chłopcami, a potem nie przychodzi na spotkania. W podstawówce straciła siostrę, Kano; zawsze nosi przy sobie jej łamigłówkę z metalowych kółek. Umówiła się też z Yomogim, zamierzając go wystawić, lecz Gauma ją za to zbeształ, a pojawienie się kaiju wciągnęło ją w walkę. Po rozłączeniu Dynazenona steruje Dyna Wingiem, który tworzy jego tors i skrzydła.

### dic\_pilot\_YUME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b013`

> Dociekając prawdy o śmierci siostry, dzięki mocy kaiju poznaje jej przeszłość i uczucia i postanawia iść naprzód. Po ostatniej bitwie odwzajemnia uczucie Yomogiego i powoli odnajduje się w klasie.

### dic\_pilot\_KOYOMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b014`

> Młody mężczyzna od dawna bez pracy. Nie ma żadnych celów i wiedzie leniwe życie. Małomówny i cichy. Gdy z kuzynką, Chise, która przesiaduje w jego pokoju, przychodzi popatrzeć na zamieszanie z kaiju, Gauma wciąga go w walkę.

### dic\_pilot\_KOYOMI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b015`

> Pani Inamoto, szefowa Yomogiego w pracy, chodziła z nim do jednej klasy w gimnazjum. Wciąż gryzie go, jak się wtedy zachował, lecz gdy przypadkiem znów się spotykają, idą razem na drinka. Nawiązuje nić porozumienia z Mujiną z Klubu Kaiju, która także nie ma żadnych celów, lecz stoją po przeciwnych stronach i ich relacja nie posuwa się dalej. Walki z kaiju sprawiają jednak, że mierzy się z przeszłością i dojrzewa. Po wszystkim ścina włosy i zaczyna szukać pracy; w końcu dostaje posadę w firmie męża pani Inamoto.

### dic\_pilot\_CHISE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b016`

> Kuzynka Koyomiego, uczennica gimnazjum. Nie chodzi do szkoły, tylko przesiaduje w pokoju Koyomiego. Nie pilotuje Dynazenona, ale ze wszystkich najmocniej czuje się członkinią drużyny Gaumy. Po pierwszej walce z kaiju znajduje coś jakby biały kamyk.

### dic\_pilot\_CHISE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b017`

> W poprzedniej szkole cierpiała z powodu samotności i odrzucenia. Lubi rysować wzory zentangle; pod rękawem na lewej ręce ma malunek na skórze. Z nasienia kaiju, które znalazła, wykluwa się Goldburn; nawiązuje z nim więź i zaczyna pomagać w walkach z kaiju.

### dic\_pilot\_GLDBRN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b018`

> Kaiju, które wyrosło z nasienia znalezionego przez Chise. Rozumie ją i pomaga Gaumie i reszcie. Złote światło, którym zieje, zmienia rozmiar przedmiotów i łączy je ze sobą.

### dic\_pilot\_GLDBRN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b019`

> Po połączeniu w Kaiser Gridknighta tworzy przedni pancerz i hełm. Samo potrafi zmienić się w tarczę i nieraz ratuje Dynazenona z opresji. Po ostatniej bitwie odchodzi z Fujiyokidai razem z Sojuszem Gridknighta.

### dic\_pilot\_JUGA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b01a`

> Władca kaiju z Klubu Kaiju. Poważny i opanowany. 5000 lat temu podziwiał Gaumę, starszego towarzysza, a dziś chce go prześcignąć jako władca kaiju i raz po raz wyzywa go do walki. Ma dar do kierowania dwunożnymi kaiju.

### dic\_pilot\_JUGA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b01b`

> Uważa, że lepiej przeciągnąć Dynazenona na swoją stronę, niż go pokonać, i nawet zbliża się do Yomogiego. Po przegranej w ostatniej bitwie z Gaumą i resztą przepada bez wieści.

### dic\_pilot\_ONIJA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b01c`

> Władca kaiju z Klubu Kaiju. Wojowniczy i gwałtowny. Uważa, że moc kaiju służy do zabijania ludzi. Mocniej niż inni czuje więź z grupą i nienawidzi Gaumy, który zdradził Klub Kaiju. Ma dar do kierowania dwunożnymi kaiju z ogonem.

### dic\_pilot\_ONIJA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b01d`

> Po kolejnych porażkach z Dynazenonem znajduje wspólny język z Mujiną, w której obudził się zapał. Gdy kaiju przestają się pojawiać, myśli o wybiciu ludzkości bez nich, ale to oczywiście niemożliwe. Po przegranej w ostatniej bitwie z Gaumą i resztą przepada bez wieści.

### dic\_pilot\_MUZINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b000`

> Władczyni kaiju z Klubu Kaiju. Nie ma własnych celów i idzie za tym, co postanowią inni. Trzyma się grupy, lecz kierowanie kaiju i walka z Gaumą zupełnie jej nie obchodzą. Ma dar do kierowania czworonożnymi kaiju.

### dic\_pilot\_MUZINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b001`

> Spotkanie z Koyomim, w którym dostrzega bratnią duszę, uświadamia jej, że prócz kaiju nie ma nic, i zaczyna palić się do walki, stając się wojownicza jak nigdy dotąd. Po przegranej w ostatniej bitwie z Gaumą i resztą przepada bez wieści.

### dic\_pilot\_SHIZM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b002`

> Władca kaiju z Klubu Kaiju. Spokojny, lecz jego słowa i czyny są tajemnicze i trudno odgadnąć jego zamiary. Słyszy głosy kaiju i dąży wyłącznie do wolności i wyzwolenia, które niosą kaiju.

### dic\_pilot\_SHIZM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b003`

> Jako uczeń z wymiany przenika do liceum Fujiyokidai i z ciekawości zbliża się do Yomogiego i Yume. Nosi w sobie kaiju; w ostatniej bitwie poddaje sam siebie Instance Domination i łączy się z Gagulą. Wchłonąwszy pozostałych członków Klubu Kaiju, zyskuje jeszcze większą moc, lecz przegrywa z Gaumą i resztą i przepada bez wieści.

### dic\_pilot\_KNIGHT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b004`

> Młodzieniec, który przemienia się w Gridknighta. Razem z 2nd założył Sojusz Gridknighta, by chronić światy przed zagrożeniem ze strony kaiju. Szorstki; na zaczepki Gaumy odpowiadał ciętymi słowami i pięścią.

### dic\_pilot\_KNIGHT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b005`

> Z początku nie uznawał drużyny Gaumy, lecz z czasem ją docenił i zaczął z nią współpracować. Po wszystkich walkach odchodzi z Fujiyokidai z 2nd, by podjąć kolejną misję.

### dic\_pilot\_GRIDKT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b006`

> Postać, w którą przemienia się Knight. Łącząc się z Dynazenonem i Goldburnem, tworzy Kaiser Gridknighta.

### dic\_pilot\_KGRIDKT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b008`

> Postać, jaką przybiera Gridknight połączony mocą Goldburna z Dynazenonem i Goldburnem.

### dic\_pilot\_NIDAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00a`

> Członkini Sojuszu Gridknighta. Podróżuje z Knightem, by chronić różne światy przed kaiju. Pogodna i radosna. Nosi przy sobie pałeczkę zwaną Live Baton i ma uprawnienia do Fixer Beam, promienia, który naprawia przedmioty.

### dic\_pilot\_NIDAI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00b`

> Po wszystkich walkach odchodzi z Fujiyokidai razem z Knightem, by podjąć kolejną misję.

### dic\_pilot\_INAMT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00c`

> Kierowniczka zmiany w supermarkecie Yuri Mart, gdzie dorabia Yomogi. Mężatka; po ślubie wróciła do rodzinnego Fujiyokidai.

### dic\_pilot\_INAMT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00d`

> Chodziła z Koyomim do jednej klasy w gimnazjum; gdy przypadkiem się spotykają, piją razem do rana. Dzielą wspólny sekret z gimnazjum: znaleźli torbę pełną banknotów po 10 000 jenów.

### dic\_pilot\_MEIDZ\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00e`

> Przyjaciółka Yume. Łagodna; Yume nazywa ją “mamą”. Hobby: fotografia.

### dic\_pilot\_YOMOMUM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b010`

> Matka Yomogiego. Rozwiodła się z mężem, gdy Yomogi był w trzeciej klasie podstawówki; dziś mieszka z nim i swoją matką, babcią Yomogiego, w rodzinnym domu. Ma partnera, którego przedstawiła synowi.

### dic\_pilot\_KANO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b012`

> Siostra Yume.

### dic\_pilot\_MIRIARIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b014`

> Członkini załogi Archangela, odpowiada za łączność. Ma 18 lat. Była zwykłą uczennicą, ale wojna wciągnęła ją do walki. Po śmierci ukochanego, Tolle'a, przez pewien czas nienawidziła Koordynatorów, lecz dojrzała i walczyła do końca wojny. Po wojnie podróżowała po świecie jako fotoreporterka wojenna. Gdy Archangel znów wyruszył do akcji, wróciła na pokład, by walczyć z załogą, a po powrocie Cagalli na urząd przewodniczącej oficjalnie wstąpiła do armii Orbu.

### dic\_pilot\_MHERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b016`

> NINJA (New Infinity Neuron - Japanese Assassin), żołnierz sił specjalnych wywodzący się od dawnych japońskich ninja, przywódca grupy NINJA Haze z Tajnych Sił Specjalnych. Ma 21 lat. Mężczyzna. Wykonanie zadania stawia ponad wszystko i gotów jest wyrzec się wszelkich osobistych uczuć; jeśli trzeba, ukryje nawet własną tożsamość. Dlatego otoczenie ma go za chłodnego i bezlitosnego. Uchodzi za najsilniejszego NINJA w historii Haze; mistrzowsko opanował Ninja Art i kły ninja, a w pilotowaniu mobilnego pancerza ninja nie ma sobie równych. Umysłem całkowicie panuje nad ciałem, więc jest bardzo odporny na wszelkie trucizny.

### dic\_pilot\_MHERO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b017`

> Naprawdę nazywa się Yaichi Yagami. Syn Tetsuro Yagamiego, brat Yachiyo Yagami (Forte Tsukinowy) i Echiki Y. Franburnett. Jako dziecko otrzymał od ojca polecenie, by zostać NINJA i chronić Echikę. Nie on o tym zdecydował, lecz nigdy się nie zawahał; młodsza siostra, Echika, stała się sensem jego życia. Choć nowe uczucia i kaprysy Echiki nieraz wytrącają go z równowagi, cieszy się misją na A. Advencie u boku przyjaciół.

### dic\_pilot\_MHERO\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b018`

> NINJA (New Infinity Neuron - Japanese Assassin), żołnierz sił specjalnych wywodzący się od dawnych japońskich ninja, przywódca grupy NINJA Haze z Tajnych Sił Specjalnych. Ma 21 lat. Mężczyzna. Wykonanie zadania stawia ponad wszystko i gotów jest wyrzec się wszelkich osobistych uczuć; jeśli trzeba, ukryje nawet własną tożsamość. Dlatego otoczenie ma go za chłodnego i bezlitosnego. Uchodzi za najsilniejszego NINJA w historii Haze; mistrzowsko opanował Ninja Art i kły ninja, a w pilotowaniu mobilnego pancerza ninja nie ma sobie równych. Umysłem całkowicie panuje nad ciałem, więc jest bardzo odporny na wszelkie trucizny.

### dic\_pilot\_MHERO\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b019`

> Naprawdę nazywa się Yaichi Yagami. Syn Tetsuro Yagamiego, brat Yachiyo Yagami (Forte Tsukinowy) i Echiki Y. Franburnett.

### dic\_pilot\_FHERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b000`

> NINJA (New Infinity Neuron - Japanese Assassin), żołnierz sił specjalnych wywodzący się od dawnych japońskich ninja, członkini grupy NINJA Haze z Tajnych Sił Specjalnych. Ma 17 lat. Kobieta. Jako NINJA ma niewielkie doświadczenie i pod każdym względem jest jeszcze niedojrzała, lecz wrodzony optymizm pozwala jej stawiać czoło trudnościom. Ma spory talent, ale brak jej doświadczenia i umiejętności, by go wykorzystać, więc wątpiono, czy poradzi sobie sama. Mimo to z decyzji przywódcy Haze, Crossa Tsukinowy, otrzymała zadanie ochrony Echiki Y. Franburnett.

### dic\_pilot\_FHERO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b001`

> Naprawdę nazywa się Yachiyo Yagami. Córka Tetsuro Yagamiego, młodsza siostra Yaichiego Yagamiego (Crossa Tsukinowy) i starsza siostra Echiki Y. Franburnett. Jako dziecko poszła za bratem i zgłosiła się na NINJA, choć już wtedy wątpiono w jej zdolności. Myśl, że razem z bratem chroni młodszą siostrę, Echikę, pozwoliła jej przetrwać morderczy trening; dziś to sens jej życia. Za punkt honoru uważa nie okazywać innym przeszłości ani rozterek i cieszy się misją na A. Advencie i życiem u boku Echiki.

### dic\_pilot\_FHERO\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b002`

> NINJA (New Infinity Neuron - Japanese Assassin), żołnierz sił specjalnych wywodzący się od dawnych japońskich ninja, członkini grupy NINJA Haze z Tajnych Sił Specjalnych. Ma 17 lat. Kobieta. Jako NINJA ma niewielkie doświadczenie i pod każdym względem jest jeszcze niedojrzała, lecz wrodzony optymizm pozwala jej stawiać czoło trudnościom.

### dic\_pilot\_FHERO\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b003`

> Naprawdę nazywa się Yachiyo Yagami. Córka Tetsuro Yagamiego, młodsza siostra Yaichiego Yagamiego (Crossa Tsukinowy) i starsza siostra Echiki Y. Franburnett.

### dic\_pilot\_ECHIKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b004`

> Córka właściciela ziemskiego z miasta Yagami. Ma 14 lat. Dziewczyna. Straciła oboje rodziców; mieszkała w ogromnej rezydencji w mieście Yagami z guwernantką, Anniną, i 99 pokojówkami. Nie chodziła do szkoły, lecz Annina przygotowywała ją do roli przyszłej władczyni, ucząc nie tylko polityki i ekonomii, ale nawet sztuki wojennej. Sumienna, we wszystko angażuje się całym sercem i nie znosi przegrywać. Mało obcowała z ludźmi, więc niezgrabnie nawiązuje kontakty, lecz przy bliskich bywa dziecinna, jak przystało na jej wiek.

### dic\_pilot\_ECHIKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b005`

> Zostaje właścicielką mobilnej fortecy-miasta A. Advent, a w wyborach przewodniczącą mobilnego miasta-państwa A. Advent. W rzeczywistości jest kopią nadczłowieka Izany i nie łączą jej więzy krwi z Tetsuro Yagamim, Crossem ani Forte. Jako przebudzona istota nadludzka potrafi panować nad Willforce, lecz zapieczętowała tę moc i walczy, skupiając energię duchową mieszkańców A. Adventu.

### dic\_pilot\_ANINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b006`

> Guwernantka Echiki. Ma 27 lat. Kobieta. Od trzech lat mieszka w rezydencji i uczy Echikę wszystkiego, czego potrzeba do rządzenia. Była asystentką ojca Echiki, naukowca Tetsuro Yagamiego; po jego śmierci w wypadku, zgodnie z jego ostatnią wolą, została guwernantką Echiki. Wykształcona i rozważna, zawsze łagodnie uśmiechnięta, nie wyczuwa jednak atmosfery i czasem mówi lub robi coś zupełnie nie w porę. Mimo to rozumie Echikę lepiej niż ktokolwiek i cieszy się jej bezgranicznym zaufaniem.

### dic\_pilot\_ANINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b007`

> Po uruchomieniu A. Adventu odpowiada za stan okrętu i pełni rolę zastępcy kapitana. Równocześnie, na podstawie danych pozostawionych przez Tetsuro Yagamiego, zgłębia zagadkę Systemu Nira-Kana-I i Echiki, kierując się zarówno ciekawością badaczki, jak i pragnieniem, by lepiej poznać ukochaną Echikę.

### dic\_pilot\_NOVY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b008`

> Były żołnierz Sił Nowej Federacji Ziemskiej. Ma 48 lat. Mężczyzna. W wojsku był komandorem porucznikiem i kapitanem okrętu, lecz sam odszedł ze służby i wiódł beztroskie życie. Swobodny, unika odpowiedzialności i na pierwszy rzut oka wydaje się nicponiem, ale ma podstawowe zasady moralne. Twierdzi, że liczy się dla niego zapłata, choć tak naprawdę nie przywiązuje wagi do pieniędzy. Był namiętnym palaczem, lecz po odejściu z wojska, na prośbę Miny, ogranicza papierosy.

### dic\_pilot\_NOVY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b009`

> Ze względu na doświadczenie zostaje kapitanem A. Adventu i kieruje wszystkim, co dotyczy walki, lecz decyzje taktyczne i strategiczne zostawia Echice. W wojsku był zastępcą dowódcy 31. Samodzielnego Korpusu Indigo Chasers, który przypadkowo napotkał Ra Valbelma i został przez niego zniszczony. Wnioskował o pościg za Valbelmem, lecz wniosek zatuszowano, więc odszedł ze służby. Nie czuje gniewu ani nienawiści do Valbelma, lecz gorycz i rozpacz wobec własnej bezsilności w obliczu potęgi Valbelma i potęgi władzy, która sprawę zamiotła pod dywan.

### dic\_pilot\_MINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00a`

> Była żołnierka Sił Nowej Federacji Ziemskiej. Ma 18 lat. Kobieta. Już w wojsku była podwładną Noveya i świetną operatorką okrętu pod jego dowództwem. Gdy Novey odszedł ze służby, poszła w jego ślady i dba o jego niechlujne życie prywatne. Sumienna, nie znosi nieuczciwości, a dawne doświadczenia sprawiają, że surowo traktuje ludzi u władzy.

### dic\_pilot\_MINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00b`

> Zatrudniona przez Echikę razem z Noveyem, jest operatorką A. Adventu. Gdy zatuszowano wniosek Noveya o pościg za wrogiem, który zniszczył 31. Samodzielny Korpus, straciła wiarę w ludzi u władzy, lecz znajomość z Echiką stopniowo zmienia jej poglądy. Uwielbia cosplay; pracując w sklepiku A. Adventu “Kana-Kana-I”, przebiera się we własne kostiumy.

### dic\_pilot\_RENREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00c`

> Pokojówka w rezydencji Franburnettów. Kieruje zespołem mechaników, który dba o infrastrukturę rezydencji. Opiekuńcza starsza siostra, trzyma w ryzach wszystkie 99 pokojówek.

### dic\_pilot\_RENREN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00d`

> Tetsuro Yagami wtajemniczył ją w istnienie A. Adventu; razem z Anniną i innymi pokojówkami przygotowywała się na dzień jego uruchomienia.

### dic\_pilot\_AITY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00e`

> Pokojówka w rezydencji Franburnettów. Kieruje zespołem wywiadowczym, który zbiera dla Echiki informacje z całego świata. Opanowana, lecz myśli w sposób nieco odbiegający od powszechnych norm, co czyni ją niebezpieczną, bo dla osiągnięcia celu nie cofnie się przed niczym.

### dic\_pilot\_AITY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b000`

> Tetsuro Yagami wtajemniczył ją w istnienie A. Adventu; razem z Anniną i innymi pokojówkami przygotowywała się na dzień jego uruchomienia.

### dic\_pilot\_COOKIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b001`

> Pokojówka w rezydencji Franburnettów. Kieruje zespołem gospodarczym, który zajmuje się wszystkimi pracami domowymi. Świetna kucharka, przyrządzi dania z całego świata; z radością patrzy, jak Echika rośnie.

### dic\_pilot\_COOKIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b002`

> Tetsuro Yagami wtajemniczył ją w istnienie A. Adventu; razem z Anniną i innymi pokojówkami przygotowywała się na dzień jego uruchomienia.

### dic\_pilot\_YAGAMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b003`

> Ojciec Echiki. Autorytet w dziedzinie materiałów psychoreaktywnych i inżynierii energetycznej; uczestniczył też w budowie mobilnych pancerzy ninja używanych przez Haze z Tajnych Sił Specjalnych. Potajemnie zbudował pod miastem Yagami mobilną fortecę-miasto A. Advent i zginął w wypadku podczas badań, gdy Echika miała 10 lat. Wypadek był jednak tylko przykrywką, by zniknąć światu z oczu i prowadzić tajne badania.

### dic\_pilot\_YAGAMI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b004`

> Egoista, dla którego badania są ponad wszystko; nie lubią go nawet przybrane dzieci, Cross i Forte, a i dla Echiki nie żywi uczuć większych niż dla obiektu badań. Matka Echiki, czyli jego żona, nigdy nie istniała; była tylko narzędziem do spętania umysłu Echiki. Ma wielu sponsorów, z których pieniędzy zbudował A. Advent, lecz jeszcze większy majątek ukrył jako tajny fundusz.

### dic\_pilot\_AID\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b005`

> Pierwszy i zarazem ostatni prezydent Nowej Federacji Ziemskiej. Po rozwiązaniu Nowej Federacji Ziemskiej został sekretarzem generalnym Nowej Ligi Narodów, organu rozjemczego między państwami, i służy światu w czasach przemian.

### dic\_pilot\_AID\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b006`

> Naprawdę od samego początku współpracuje z Wszechgwiezdnym Imperium Ra Val; gdy dowiedział się o istnieniu tej potęgi, przysiągł jej posłuszeństwo. Już jako senator Federacji Ziemskiej potajemnie sprzyjał Ra Val; to on zatuszował wniosek Noveya o pościg za Valbelmem.

### dic\_pilot\_VALBLM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b007`

> 68. Niebiański Cesarz Wszechgwiezdnego Imperium Ra Val. Ma 49 lat. Mężczyzna. Tytułu Niebiańskiego Cesarza, władcy Ra Val, nie dziedziczy się; zdobywa się go wyłącznie siłą, a Valbelm objął tron, pokonawszy poprzednika. Sławiony jako największy wódz w dziejach Ra Val i zarazem najpotężniejszy wojownik, ma najbardziej rozwinięte geny strategii przetrwania, które decydują o zdolnościach bojowych. Surowy wobec siebie i innych, budzi wśród podwładnych żarliwe uwielbienie i strach; niewielu może zwrócić się do niego wprost.

### dic\_pilot\_VALBLM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b008`

> W jego sercu wciąż krwawi rana po klęsce, którą 2500 lat w przyszłości zadali mu potomkowie ludzkości. By oddać cześć poległym towarzyszom i odzyskać dumę Ra Valian, chce ujarzmić ludzkość i podbić galaktykę, choćby miał zostać sam.

### dic\_pilot\_SEYVAS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b009`

> Niebiański Rycerz z gwardii przybocznej Niebiańskiego Cesarza Wszechgwiezdnego Imperium Ra Val. Ma 23 lata. Mężczyzna. Pogodny, kocha wolność i cieszy się sympatią podległych mu niebiańskich wojowników. Stronnictwo przywiązane do dyscypliny go nie znosi, o czym dobrze wie, a nawet celowo prowokuje je dla zabawy. Wszystko robi jednak dla Niebiańskiego Cesarza Valbelma i Ra Val; chce tchnąć coś nowego w duszne Imperium.

### dic\_pilot\_SEYVAS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00a`

> Jeden z nielicznych Niebiańskich Rycerzy przeniesionych razem z Valbelmem do naszych czasów; w chwili przeniesienia był niemal nowicjuszem. Głęboko świadomy swojej misji, starał się zostać prawdziwym najsilniejszym wojownikiem Ra Val i zdobył siłę godną tej roli.

### dic\_pilot\_SISTIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00b`

> Niebiańska Rycerz z gwardii przybocznej Niebiańskiego Cesarza Wszechgwiezdnego Imperium Ra Val. Ma 23 lata. Kobieta. Ceni dyscyplinę i stoi na straży porządku w armii Ra Val. Służy w gwardii od tego samego czasu co Seivas, ale nie znoszą się i rozmawiają tylko wtedy, gdy muszą. Świetna dowódczyni; z rozkazu Valbelma ma władzę nad całą armią Ra Val.

### dic\_pilot\_SISTIS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00c`

> Darzy Valbelma uczuciem większym niż lojalność, lecz kroczy za nim na jego drodze podboju zawsze o krok z tyłu i skrywa swe uczucia.

### dic\_pilot\_NEGSIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00d`

> Niebiański Mędrzec, główny strateg Wszechgwiezdnego Imperium Ra Val. Ma 48 lat. Mężczyzna. Najbliższy doradca Niebiańskiego Cesarza Valbelma, jego strateg jeszcze z czasów sprzed koronacji. Ma bystry umysł i zmysł strategiczny, lecz jego wyniosła uprzejmość zraża do niego wielu w Ra Val. Zarazem wszyscy cenią jego intelekt i czują przed nim respekt. Przemawia w imieniu Valbelma i prowadzi wszelkie negocjacje z innymi organizacjami.

### dic\_pilot\_NEGSIS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00e`

> Rozumie uczucia Valbelma, lecz w trosce o przetrwanie Ra Val sprzeciwia się jego ambicjom i szuka łagodnego rozwiązania. Łączy ich więź, w którą nikt nie może się wedrzeć; choć w końcu ich drogi się rozchodzą, do ostatniej chwili życzy Valbelmowi i Ra Val zwycięstwa.

### dic\_pilot\_IZANA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00f`

> Nadczłowiek, w którym obudził się czynnik pozostawiony przez starożytną supercywilizację, Klan Animus. Ma 16 lat. Dziewczyna. Pierwsza przebudzona istota nadludzka w dziejach ludzkości, lecz gdy miała dwa lata, zanim zdołała zapanować nad swymi mocami, wypadek sprawił, że jej umysł wymknął się spod kontroli; od tamtej pory pogrążona jest w długim śnie. Zaopiekował się nią Tetsuro Yagami, który z jej genów stworzył kopię, Echikę. Imię Izana nadał jej Yagami; wszelkie zapiski o jej wcześniejszych losach wymazano.

### dic\_pilot\_IZANA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b010`

> Miała stać się nowym ciałem Evolverów, zbiorowej woli złożonej z Willforce Klanu Animus, lecz uwolniona od nich postanawia żyć po swojemu, razem z młodszą siostrą, Echiką, i resztą.

### dic\_pilot\_IVRVER\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b011`

> Zbiorowisko Willforce, pozostałości woli starożytnej supercywilizacji, Klanu Animus. Nazwał je tak Tetsuro Yagami, bo pcha ludzkość ku bojowej ewolucji. Chce ziścić niespełnione niegdyś pragnienie podboju galaktyki, posługując się ludzkością jak pionkami, a ciało Izany, przebudzonej jako istota nadludzka, ma stać się jego nowym naczyniem.

### dic\_pilot\_MOB\_14\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b013`

> Właściciel baru Ale &amp; Vent w dzielnicy mieszkalnej A. Adventu. Lokal nosił kiedyś inną nazwę, lecz zmienił ją, by uczcić wybór Echiki na przewodniczącą A. Adventu. Trunki z całego świata i potrawy, które podkreślają ich smak, przyciągają tłumy gości.

### dic\_pilot\_MOB\_12\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b015`

> Właścicielka kawiarni A. Ardent w dzielnicy mieszkalnej A. Adventu. Lokal nosił kiedyś inną nazwę, lecz zmieniła ją, by uczcić wybór Echiki na przewodniczącą A. Adventu. Przytulna atmosfera, mnóstwo słodkości i bogate menu lunchowe sprawiają, że kawiarnia jest bardzo popularna, a Echika przesiaduje w niej przy każdej okazji. Właścicielka to lokalna piękność, ulubienica całego miasta.

### dic\_pilot\_MASAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b017`

> Herold Elemental Lorda Cybastera. Przywołany z Japonii do Świętego Królestwa Langran w podziemnym świecie La Gias w ramach planu sprowadzania przybyszów z powierzchni. Wybrany przez Cyphis, ducha opiekuńczego Cybastera, został heroldem Elemental Lorda. W gorącej wodzie kąpany, a do tego beznadziejnie gubi drogę, ale to świetny sportowiec o wielkim poczuciu sprawiedliwości.

### dic\_pilot\_KURO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b000`

> Chowaniec Masakiego. Kot-duszek wyodrębniony z części jego podświadomości; charakter ma inny niż Masaki, bo jest jedną z jego person. Lata z Masakim w Cybasterze i go wspiera. Raczej spokojna, ale też zamartwia się na zapas i często upomina Shiro i Masakiego, gdy szarżują.

### dic\_pilot\_SHIRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b002`

> Chowaniec Masakiego. Kot-duszek wyodrębniony z części jego podświadomości; charakter ma inny niż Masaki, bo jest jedną z jego person. Lata z Masakim w Cybasterze i go wspiera. Raczej spokojny, ale też zadziorny i zawsze musi mieć ostatnie słowo.

### dic\_pilot\_SOUJI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b004`

> Członek oddziału obrony Księżycowego Laboratorium Strategii Specjalnych sił Federacji Ziemskiej, w stopniu chorążego. Ma 23 lata. Służył w 25. Dywizjonie Księżycowego Lotnictwa, lecz wszyscy pozostali członkowie zginęli w walce, więc dywizjon rozwiązano, a jego przydzielono do ochrony laboratorium. Ciemną skórę zawdzięcza promieniowaniu UV; jak twierdzi, to znak kosmicznego pilota. Hedonista z dewizą “żyć radośnie”; niezłomny optymista, który we wszystkim widzi dobre strony. W 25. Dywizjonie był poważny i uchodził za sztywniaka, lecz by uczcić pamięć poległych towarzyszy, postanowił “żyć radośnie” także za nich i próbuje wszelkich “przyjemności”. Do podrywania nie ma jednak talentu. Zszedł na Ziemię, by przewieźć opracowany w laboratorium ERS-100. Nauczywszy ERS-100, czym jest “człowiek”, zostaje pilotem stworzonej przez nią maszyny, VangRaya, i wyrusza w podróż, by ocalić Ziemię. Doświadczenia z tej podróży sprawiają, że dojrzewa razem ze swoją partnerką, Nine, i staje się wielką siłą w ratowaniu Ziemi.

### dic\_pilot\_CHITOSE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b006`

> Członkini oddziału obrony Trzeciego Laboratorium Strategii Specjalnych sił Federacji Ziemskiej, w stopniu chorążego. Ma 19 lat. Wojna odebrała jej rodziców i siostrę; jest sama jak palec. Prawie nie ma doświadczenia bojowego, lecz z braku ludzi została jedyną członkinią oddziału obrony laboratorium. Przeszła tylko podstawowe szkolenie z pilotażu maszyn bojowych, ale ma talent, zwłaszcza do strzelania. Sumienna, pogodna i pełna życia; jej optymizm rozjaśnia innych, a w laboratorium była duszą towarzystwa. Ponieważ poza obroną laboratorium musi wykonywać mnóstwo różnych prac, a pracownicy osobiście o to prosili, zwolniono ją z noszenia munduru. Nauczywszy ERS-100, czym jest “człowiek”, zostaje pilotką stworzonej przez nią maszyny, VangRaya, i wyrusza w podróż, by ocalić Ziemię. Doświadczenia z tej podróży sprawiają, że dojrzewa razem ze swoją partnerką, Nine, i staje się wielką siłą w ratowaniu Ziemi.

### dic\_pilot\_NINE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b008`

> Androidka z wbudowanym Systemem 99, systemem operacyjnym VangRaya. Gdy rozdzieliła się z Sojim i Chitose, uznała, że do zbierania informacji i swobodnej rozmowy lepsza będzie ludzka postać; dopasowując ją do kobiecej osobowości, System 99 sam zbudował sobie ciało dziewczynki. Naprawdę jest Systemem Regeneracji Ziemi ERS-100; podziwia ludzi i naśladuje ich wygląd, by się od nich uczyć. Strój w stylu steampunk wyraża jej tożsamość, zawieszoną między maszyną a człowiekiem. W porównaniu z Systemem 99 okazuje więcej uczuć, ale zwykle zachowuje chłód i odnosi się do otoczenia cynicznie. To poza, która ma ukryć skrajną nieśmiałość, a zarazem typowy bunt nastolatki. Jest terminalem Nevanlinny, systemu odbudowy cywilizacji stworzonego przez supercywilizację Gardim, o oznaczeniu Slave 2044. Podczas zwiadu doszło do awarii, która odcięła ją od Nevanlinny; później znaleźli ją ludzie i dostosowali jako ERS-100. Terminale Nevanlinny służą do zbierania informacji z zewnątrz i nie powinny mieć woli niezależnej od Nevanlinny. Przypuszcza się, że gdy awaria odcięła wolę jednostki głównej, pomocnicza SI terminalu zyskała własną świadomość. Dzięki swoim funkcjom zbudowała VangRaya i inne maszyny, by chronić drogich jej ludzi i walczyć u ich boku. Po ocaleniu Ziemi trzech światów wyrusza z bliskimi w podróż, by pomagać w odbudowie.

### dic\_pilot\_IORI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b00a`

> Czarodziej Strażników Porządku, wyszkolony w dogmie. Ma 18 lat. Zwany Czarodziejem Iolitu. Przybysz z innego świata niż Al-Warth; naprawdę nazywa się Iori Aoi. Zadziorny, sumienny, o silnym poczuciu sprawiedliwości. Dumny ze swojej dogmy, ćwiczonej od dzieciństwa, szuka sposobu, by coś nią zdziałać. Zbiegłszy od Strażników Porządku, podróżował w Autowarlocku Xelguard z magiczną istotą, Spero. Strażnicy Porządku, zbierający ludzi z zadatkami na Założyciela, przywołali go z innego świata; w Al-Warth spędził zaledwie około roku, lecz pod kontrolą umysłu wmówiono mu, że szkolił się u nich od dziecka. W swoim świecie pragnął zmienić to, że nie umie okazywać uczuć, i właśnie tę “wolę zniszczenia” upatrzył w nim Ende. Spotykając wielu ludzi, odkrył, do czego może użyć dogmy, wzmocnił magię i stworzył własną dogmę. Także jego relacja ze Spero, z początku wroga, stopniowo się zmieniała, aż stali się prawdziwymi partnerami. Po ocaleniu Al-Warth postanawia zostać tam, dopóki świat nie odzyska pełnego spokoju.

### dic\_pilot\_IORI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b00c`

> Czarodziej Strażników Porządku, wyszkolony w dogmie. Ma 18 lat. Zwany Czarodziejem Iolitu. Przybysz z innego świata niż Al-Warth; naprawdę nazywa się Iori Aoi. Sumienny i prawy, choć bywa trochę nieśmiały. Strażnicy Porządku, zbierający ludzi z zadatkami na Założyciela, przywołali go z innego świata; w Al-Warth spędził zaledwie około roku, lecz pod kontrolą umysłu wmówiono mu, że szkolił się u nich od dziecka. W swoim świecie chodził do klasy z Amari i kochał się w niej, lecz przez nieśmiałość nie potrafił zrobić żadnego kroku. Gdy Amari przywraca mu samego siebie, walczy z nią w Xelguardzie, choć ze Spero, swoim (?) rywalem w miłości, niezbyt się dogaduje. Po ocaleniu Al-Warth postanawia zostać tam z Amari, dopóki świat nie odzyska pełnego spokoju.

### dic\_pilot\_AMARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b000`

> Czarodziejka Strażników Porządku, wyszkolona w dogmie. Ma 18 lat. Zwana Czarodziejką Akwamaryny. Przybyszka z innego świata niż Al-Warth; naprawdę nazywa się Amari Amano. Uprzejma i sumienna, ale nieśmiała i lękliwa. W głębi serca kryje jednak silną determinację i szuka tego, po co żyje. W tym celu podróżowała w Autowarlocku Xelguard z magiczną istotą, Spero. Strażnicy Porządku, zbierający ludzi z zadatkami na Założyciela, przywołali ją z innego świata; w Al-Warth spędziła zaledwie około roku, lecz pod kontrolą umysłu wmówiono jej, że szkoliła się u nich od dziecka. W swoim świecie pragnęła zmienić swoją nieśmiałość i zamknięcie w sobie, i właśnie tę “wolę zniszczenia” upatrzył w niej Ende. Spotykając wielu ludzi, odkryła, do czego może użyć dogmy, wzmocniła magię i stworzyła własną dogmę. Jej dobroć i ukryta siła oczarowały nawet Spero. Po ocaleniu Al-Warth postanawia zostać tam, dopóki świat nie odzyska pełnego spokoju.

### dic\_pilot\_AMARI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b002`

> Czarodziejka Strażników Porządku, wyszkolona w dogmie. Ma 18 lat. Zwana Czarodziejką Akwamaryny. Przybyszka z innego świata niż Al-Warth; naprawdę nazywa się Amari Amano. Pod kontrolą umysłu Strażników wydawała się sztywna i nieustępliwa, lecz z natury jest uprzejma i łagodna. Strażnicy Porządku, zbierający ludzi z zadatkami na Założyciela, przywołali ją z innego świata; w Al-Warth spędziła zaledwie około roku, lecz pod kontrolą umysłu wmówiono jej, że szkoliła się u nich od dziecka. W swoim świecie chodziła do klasy z Iorim, który potajemnie się w niej kochał. Gdy Iori przywraca jej samą siebie, walczy z nim w Xelguardzie i ze zdziwieniem odkrywa jego nieznane oblicze. Po ocaleniu Al-Warth postanawia zostać tam z Iorim, dopóki świat nie odzyska pełnego spokoju.

### dic\_pilot\_HOPES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b004`

> Sztuczna istota stworzona dogmą. Zgryźliwy i wyniośle uprzejmy: z tymi, których uważa za gorszych, rozmawia grzecznie, lecz co chwila daje im odczuć swoją wyższość. Ma rozległą wiedzę i podróżuje, by ją poszerzać. Potrafi wzmacniać Od; to w dużej mierze dzięki niemu Xelguard mógł używać dogmy, choć tracił opiekę Ende. Naprawdę jest larwą istoty z wyższego wymiaru, tak jak bestia Ende; Ende sprowadził go z innego świata, by zrobić z niego zapas własnego życia, lecz Spero, uciekając przed tym losem, zbiegł od Strażników. Tak jak Ende żywi się ludzkimi uczuciami, lecz dzięki licznym spotkaniom, w przeciwieństwie do niego, zasmakował w ludzkiej radości, miłości i nadziei.

### dic\_pilot\_SAIZOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b006`

> Kierownik Sekcji Specjalnej 3 w VTX Union S.A. Ma 27 lat. Główny pilot prototypu Tyranado w Sekcji 3. Dumny z bycia pracownikiem korporacji, za wykonanie zadania odda życie, ale na wszystko inne jest obojętny, więc otoczenie ma go za dziwaka. Jego zachowanie można nazwać “dzikim”, jeśli ktoś chce być miły, albo “bezczelnym”, jeśli nie; za plecami nazywa się go “bestią w krawacie”. Przed VTX latał prywatnie w wyścigach powietrznych i stąd wziął się jego samotniczy charakter. Przez pierwsze lata w firmie ten charakter sprawiał, że był odizolowany, lecz dzięki ówczesnemu kierownikowi Amasakiemu odkrył wartość pracy zespołowej i odtąd jest dumny, że należy do firmy. Przez to zaniedbuje jednak życie prywatne, a otoczenie patrzy na niego z mieszaniną politowania i troski. Po Wojnie Brzasku wyznaczył sobie nowy cel, “zostać prezesem VTX Union”, i prowadzi Sekcję Specjalną 3.

### dic\_pilot\_SAIZOU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b008`

> Pracownik Sekcji Specjalnej 1 w VTX Union S.A. Ma 27 lat. Pilot prototypów w Sekcji 1. Dumny z bycia pracownikiem korporacji, za wykonanie zadania odda życie, ale na wszystko inne jest obojętny, więc otoczenie ma go za dziwaka. Jego zachowanie można nazwać “dzikim”, jeśli ktoś chce być miły, albo “bezczelnym”, jeśli nie; za plecami nazywa się go “bestią w krawacie”. Po Wojnie Brzasku, gdy Sekcję Specjalną 1 zlikwidowano, przeniesiono go do Sekcji Specjalnej 3.

### dic\_pilot\_SAGIRI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b00a`

> Kierowniczka Sekcji Specjalnej 3 w VTX Union S.A. Ma 27 lat. Główna pilotka prototypu Tyranado w Sekcji 3. Choć wygląda uroczo, jest niechlujna, niedbała i robi wszystko byle jak; przez ten kontrast nazywa się ją “Upadłym Aniołem”. Jej genialny pilotaż przyciąga uwagę w całej firmie, lecz ona sama chodzi własnymi drogami i otwarcie mówi, że “pracuje dla pensji i premii”. Swobodny styl życia i bezwiednie męskie zachowanie przysporzyły jej w firmie mnóstwa wielbicielek, a przezwisko “Upadły Anioł” rozumie się też jako “ta, przez którą upadają anioły”. Przy przyjęciu do pracy chciała trafić do działu spożywczego i projektować słodycze, lecz test predyspozycji wykazał świetne zdolności pilotażu i przydzielono ją tutaj. Łatwo się peszy, a jej swoboda często służy ukryciu zakłopotania. Nawet jako kierowniczka kazała podwładnym mówić do siebie bez tytułów, bo uważała, że to do niej nie pasuje, ale także z powodu wątpliwości, czy podoła. Po Wojnie Brzasku otoczenie przekonuje ją, że “kiedyś zostanie prezesem VTX Union”, i prowadzi Sekcję Specjalną 3.

### dic\_pilot\_SAGIRI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b00c`

> Pracownica Sekcji Specjalnej 1 w VTX Union S.A. Ma 27 lat. Pilotka prototypów w Sekcji 1. Choć wygląda uroczo, jest niechlujna, niedbała i robi wszystko byle jak; przez ten kontrast nazywa się ją “Upadłym Aniołem”. Jej genialny pilotaż przyciąga uwagę w całej firmie, lecz ona sama chodzi własnymi drogami i otwarcie mówi, że “pracuje dla pensji i premii”. Może właśnie ten swobodny styl życia przysporzył jej w firmie mnóstwa wielbicielek. Po Wojnie Brzasku, gdy Sekcję Specjalną 1 zlikwidowano, przeniesiono ją do Sekcji Specjalnej 3.

### dic\_pilot\_RAMYY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b000`

> Nowa pracownica przydzielona do Sekcji Specjalnej 3 w VTX Union S.A. Ma 20 lat. Drugi pilot prototypu Tyranado w Sekcji 3. Wybitnie zdolna absolwentka akademii wojskowej sił Federacji Ziemskiej, którą ukończyła przed czasem; miała trafić do sekcji badań taktycznych VTX Union, lecz za radą prezesa Goldwina przydzielono ją do Sekcji Specjalnej 3. Sumienna, ale mało elastyczna; gdy coś ją zaczyna gryźć, potrafi bez końca nad tym rozmyślać. Pochodzi z planety Darbness; trzy lata temu dotarła na Ziemię razem z prototypem Quark Drive. Zaopiekował się nią prezes Goldwin, a potem adoptowała ją rodzina Amasakich. Jej włosy są naturalnie niebieskie, lecz nanomaszyny barwią je na kolor typowy dla Ziemian. Ma to ukryć jej obce pochodzenie, ale wynika też z upodobania Rami do ziemskiej mody. Przybranego ojca, kierownika Sekcji Specjalnej 3, Hirosuke Amasakiego, kocha jak rodzonego, a do życia na Ziemi przywykła i bardzo je lubi.

### dic\_pilot\_AMASAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b002`

> Kierownik Sekcji Specjalnej 3 w VTX Union S.A. Ma 52 lata. Odpowiada za Projekt TND i pilotuje Carriaxa, zintegrowaną maszynę wsparcia taktycznego. Skromny i łagodny, w codziennej pracy zostawia podwładnym swobodę. Słynie z talentu do wychowywania ludzi; z niejednego trudnego pracownika zrobił porządnego fachowca. Przed VTX Union był wojskowym; z prezesem Dymą Goldwinem zna się od tamtych czasów i przyjaźni się prywatnie. W wojsku był przełożonym Goldwina; ten miał silne poczucie sprawiedliwości, ale był zadufany w sobie, więc Amasaki chciał go nauczyć, jak ważne jest działać razem z innymi, czyli “sensu pracy w korporacji”, i dlatego razem wstąpili do VTX. Ponieważ z żoną nie doczekali się dzieci, kocha przybraną córkę, Rami, jak rodzoną, a na myśl o dniu jej ślubu robi mu się smutno.

### dic\_pilot\_MERIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b004`

> Pracownica Sekcji Specjalnej 3 w VTX Union S.A. Ma 24 lata. Pracowała w Sekcji Technicznej 1 przy budowie broni, więc w Sekcji 3 serwisuje Tyranado i dostraja jego uzbrojenie. Jako operatorka Carriaxa, zintegrowanej maszyny wsparcia taktycznego, z zewnątrz kieruje ogniem Tyranado. Sprawia wrażenie chłodnej i rozsądnej, ale jest wybuchowa i uparta, więc za plecami nazywa się ją “Meryl Zapalnik”. Przez ten charakter wciąż popadała w konflikty i choć jest zdolna, przylgnęła do niej łatka trudnej pracownicy. Sama się tego wstydzi i próbowała się zmienić, a dzięki zaufanym towarzyszom z Sekcji Specjalnej 3 stopniowo łagodnieje. Choć zaprzecza, uwielbia wszystko, co urocze: od małych zwierzątek, przez bibeloty, po dzieci.

### dic\_pilot\_EIMIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b006`

> Pracownica Sekcji Specjalnej 3 w VTX Union S.A. Ma 24 lata. Pracowała w dziale administracji, a także w księgowości, więc w Sekcji 3 prowadzi wszystkie sprawy biurowe. Jako operatorka Carriaxa, zintegrowanej maszyny wsparcia taktycznego, dzięki znajomości przetwarzania danych odpowiada za łączność i wykrywanie wroga. Urocza, łagodna i troskliwa; mężczyźni w firmie wciąż źle to odczytywali, co rodziło kłopoty, lecz ona rozprawiała się z nimi bezceremonialnymi, ciętymi słowami, zyskując przydomek “Miss Straight”. Sama się tego wstydzi i próbowała się zmienić, a dzięki zaufanym towarzyszom z Sekcji Specjalnej 3 jej jad złagodniał do poziomu żartobliwych docinków. Czasem jednak wychodzi z niej przebiegłość, która przeraża koleżankę, Meryl.

### dic\_pilot\_NEBLNNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b008`

> System odbudowy cywilizacji stworzony przez supercywilizację Gardim. Autonomiczna SI o kobiecej osobowości. Jej charakter w dużej mierze ukształtowały dane zebrane przez terminal nr 2044: ma silne poczucie odpowiedzialności, determinację i nieugiętą wolę walki z wszystkim, co staje na drodze jej misji. Przechowuje wszelkie dane, z których składa się supercywilizacja Gardim; uciekła z bliskiej zagłady macierzystej planety Gardim do naszej galaktyki razem z garstką Gardimian. Uruchomiona, przekształca otoczenie w środowisko idealne dla Gardimian i wykorzystuje okoliczne zasoby, by odbudować cywilizację. Ma też funkcje bojowe, by usuwać przeszkody na drodze misji i chronić cywilizację Gardim; w tym celu zbudowała sobie ciało, maszynę bojową Arcadia. Wchłonąwszy dane zebrane przez Slave 2044, czyli Nine, ogłosiła się istotą wyższą od ludzi, lecz zgubił ją lęk przed “miłością”, uczuciem, którego nie potrafiła pojąć. W końcu jednak uznała swój błąd i, powierzając misję Nine, odeszła.

### dic\_pilot\_ENDE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b000`

> Stwórca Al-Warth. Istota z wyższego wymiaru o niepojętej, przekraczającej ludzkie wyobrażenia mocy; siłą woli stworzył Al-Warth w poznawalnym wszechświecie. Jego celem było zaludnić go ludźmi i żywić się rodzącymi się w nich uczuciami; najbardziej smakują mu smutek, cierpienie i rozpacz. By je wywoływać, założył Strażników Porządku i do woli sterował wojnami w Al-Warth. Nie żywi się nimi, by przeżyć, lecz wyłącznie dla przyjemności; ludzkimi słowami to okrutny, bezlitosny egoista. Żyje już ponad 3000 lat i wiedząc, że kiedyś umrze, szuka zapasowych “umysłu, ciała i życia”. Po jego śmierci Al-Warth trwa dalej dzięki pragnieniom swoich mieszkańców.

### dic\_pilot\_DAIMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b002`

> Były prezes VTX Union S.A. Ma 48 lat. Słynie z żelaznej ręki: w wieku zaledwie 38 lat został prezesem VTX Union, światowego giganta, i przez 10 lat przewodził światowej gospodarce. Rządzi jednoosobowo i ma wielu wrogów w firmie i poza nią, lecz wielu, zachwyconych jego formatem, idzie za nim gotowych oddać życie. Ma silną wolę i nie zmienia raz podjętych decyzji, ale jako menedżer myśli elastycznie i wprowadził VTX w mnóstwo branż. Przed przyjściem do firmy był wojskowym, bohaterem, który w superrobocie Gaian walczył z wrogami ludzkości. Upozorował jednak własną śmierć i przystąpił do realizacji od dawna knutego “Planu Zjednoczenia Galaktyki”. Za pieniądze VTX Union zbudował Mobilną Fortecę VTX i ostateczną broń Dygaian, w której ogłosił się nowym obrońcą Ziemi. Szczerze wierzy, że Plan Zjednoczenia Galaktyki służy ludzkości, a jego wykonanie to jego misja i sprawiedliwość. Kierując VTX Union, trenował bez wytchnienia na dzień, gdy znów stanie na polu bitwy w Dygaianie, więc jest silniejszy niż w czasach wojska. Po klęsce przyznaje się do błędu i poddaje, a jego plan dobiega końca.

### dic\_pilot\_CLREUM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b004`

> Dowódca oddziału wykonawczego Quaestorów. Pochodzi z Valrougi, wojowniczego ludu z 12. Galaktyki; Quaestorzy zwerbowali go razem z jego pobratymcami. Jako pełnomocnik przywódcy Quaestorów bada i poddaje eksperymentom ziemską cywilizację. Magister wyznaczył go na przyszłego króla Ziemi po jej osądzeniu; na znak tego pilotuje Gravalina, najwyższy model Valina. W kontaktach z ziemską cywilizacją, jak przystało na poszukiwacza prawdy, interesuje się wszystkim, przez co jego arogancja stopniowo znika, a na wierzch wychodzi szczera, niewinna ciekawość nowych doświadczeń. W końcu zaczyna wątpić nawet w swoją relację z Magistrem. Okazuje się, że tak jak pozostali Quaestorzy jest klonem Magistra, a jego wspomnienia i myśli przygotował Magister. Po śmierci Magistra nazywa siebie strażnikiem wymiarów i podróżuje po światach równoległych, by zaspokoić ciekawość.

### dic\_pilot\_KIDJ\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:df20b000`

> Naprawdę nazywa się Jotaro Kido. Były snajper specjalnego oddziału strzelców Red Rose regularnych sił Federacji Ziemskiej, mistrz w swoim fachu: z odległości 100 metrów zestrzeli muchę. Włada każdą bronią palną, a dzięki wielkim umiejętnościom bojowym specjalizuje się w samotnych szturmach i infiltracji. Udaje chłodnego, ale to równy gość, któremu mimowolnie wyrywa się gorąca natura. Na co dzień przystępny i wesoły, trochę jak dzieciak, lecz do łotrów strzela bez wahania. Lubi czyścić ukochaną broń, kolekcjonuje płyty i gra na gitarze. Gra tak dobrze, że występował z Ronnym Page'em z megapopularnego zespołu Raiders; jego ulubiony instrument to zrobiona własnoręcznie dwugryfowa gitara Stratomaster.

### dic\_pilot\_BOY\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b001`

> Naprawdę nazywa się Steven Bowie. Rekordzista w liczbie zwycięstw z rzędu w Le Mans Desol, największym wyścigu Układu Słonecznego. Jego znaki rozpoznawcze to czapka i piegi. Zaproszony przez Isaaca i oczarowany Brai-Thunderem, dołączył do J9. Lekkoduch, wesoły przystojniak z przymrużeniem oka, ma słabość do pięknych kobiet. Zwykle to on, pomagając pięknej nieznajomej w kłopotach, wplątuje się w sprawę, która staje się zleceniem dla J9. W głębi duszy jest jednak wrażliwy i szczery; nie potrafi zapomnieć dawnych miłości ani tych, którym coś zawdzięcza. Ma charakterystyczny sposób mówienia, a swój ukochany Brai-Thunder nazywa “kociakiem”.

### dic\_pilot\_MACHI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b003`

> Naprawdę nazywa się Machiko Valencia. Specjalizuje się w infiltracji i sabotażu, za co nazywa się ją “Bomber Girl”. Zwinność i umiejętne wykorzystywanie kobiecych wdzięków czynią ją niezastąpionym źródłem informacji dla J9. Jej ojciec jest szefem Biura Rozwoju Jowisza, lecz nie mogąc znieść jego postępowania, uciekła z domu i przez pewien czas należała do jowiszowego Galileo Connection. Kocha wolność i dreszcz emocji, żyje miłością i namiętnością.

### dic\_pilot\_IZAQ\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b005`

> Naprawdę nazywa się Isaac Godunov. Założyciel i przywódca Cosmo Rangers J9. Bystry analityk i strateg, mózg J9; dowodzi drużyną, która bezgranicznie mu ufa. Urodził się w arystokratycznym rodzie z północnej Europy, lecz w dzieciństwie jego ojciec zginął w walce o władzę. Dalsze jego losy spowija tajemnica; w końcu założył firmę czyścicieli w bazie J9 w pasie asteroid, w Strefie Zachodniej, w dzielnicy J pod numerem 9. Pod chłodną miną kryje się cichy obrońca sprawiedliwości, w którym płonie nienawiść do władzy i zła. Za odpowiednią zapłatę podejmie się niemal każdego zlecenia, lecz z zasady odrzuca prośby łotrów i ludzi, których nie lubi. Mistrz walki wręcz; jego ulubiony elektryczny bicz bezlitośnie spada na łotrów. Na co dzień chłodny i cichy, ma jednak poczucie humoru i dobre serce; przygarnął sieroty Sina i Mei. Nie znosi pożyczania pieniędzy i zielonej papryki, a jego słabość to zupełny brak głowy do alkoholu.

### dic\_pilot\_PONCH\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b000`

> Paser z półświatka i menedżer J9. Negocjuje zlecenia i próbuje po kryjomu przed Isaakiem uszczknąć coś z zapłaty, ale z wrodzonej niezdarności rzadko mu się to udaje. Nie potrafi sprzeciwić się Isaacowi, lecz bynajmniej nie słucha go z niechęcią; w głębi duszy jest bardzo oddany J9. W walce pilotuje transportowiec Brai-Carrier i dowozi Brai-Cannon. Zgromadzona przez niego fortuna przejdzie do legendy jako “ukryty skarb Pancha Poncha”.

### dic\_pilot\_ROGER\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b002`

> Najlepszy negocjator Paradigm City, miasta bez pamięci. Ma 25 lat. Był porucznikiem żandarmerii; Dastun z żandarmerii był jego przełożonym. Z humorem i dowcipem pewnie prowadzi negocjacje i osiąga więcej, niż spodziewał się klient. Szarmancki dżentelmen, ale łatwo się unosi; wobec tych, którzy nie słuchają i łamią zasady uczciwości, potrafi użyć siły. Z zasady nigdy jednak nie nosi broni, nawet przy najniebezpieczniejszych zleceniach. Uparty, nie znosi zmieniać zdania, lecz w gruncie rzeczy to poczciwiec; gdy Dorothy poprosiła o kota, w końcu się zgodził. Ma Pamięć pozwalającą pilotować Big O i z jego pomocą staje do walki z wielkim złem. Nie robi tego, by zgrywać bohatera, lecz wymierza własne prawo tym, którzy łamią zasady uczciwości i człowieczeństwa. Sam nie wie, skąd ma Pamięć pozwalającą pilotować Big O. Mieszka w opuszczonym banku poza kopułą. Wszyscy, którzy w nim mieszkają, muszą nosić czerń, a bez warunków wstęp do domu mają tylko kobiety. Kolekcjonuje klepsydry. Ceni sobie przyjemne przebudzenie, ale ma ciężkie poranki, więc Dorothy budzi go czasem ostrą grą na fortepianie.

### dic\_pilot\_DRTHY\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b004`

> Androidka zbudowana przez Timothy'ego Wayneright na obraz jego córki. Waży jednak 130 kilogramów. Po serii wydarzeń, które zaczęły się od porwania córki magnata Soldano, zamieszkała w rezydencji Rogera, oficjalnie jako spłata należności. To nie tylko dopracowana androidka: kocha kota i zadaje Rogerowi pytania o miłość, tak bliska człowiekowi, że Roger czasem zapomina, że jest androidem. Jej oschłość i bezceremonialność nieraz odbierają mu mowę, lecz z czasem staje się jego cenną partnerką. Opaska na głowie to napęd pamięci, który często służy też za źródło światła. Lubi grać na fortepianie; z początku miała w repertuarze same gwałtowne utwory, lecz lekcje u androida-pianisty, R. Instro, stopniowo go poszerzyły.

### dic\_pilot\_SHVRT\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b006`

> Człowiek dociekający, czym są Pamięci utracone ponad 40 lat temu. Był reporterem Paradigm Press, Michaelem Seebachem, lecz obsesja na punkcie prawdy odebrała mu rozum. Na dnie podziemnych korytarzy odnalazł archetyp Megadeusa. Schwarzwald to po niemiecku “Czarny Las”. Potem odnalazł Big Duo i wyzwał Rogera do walki, lecz przegrał. Wstrząśnięty, gdy Big Duo sam się poruszył, zniknął ze sceny. Mówi jak deklamujący poeta; uważa, że ludzie, którzy nie szukają prawdy i przestali myśleć, są bezwartościowymi istotami.

### dic\_pilot\_BECK\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b008`

> Przestępca, który wciąż mąci w Paradigm City. Ma 22 lata. Zjawia się z ordynarnym rechotem i parał się już wszystkim: napadami na banki, porwaniami, oszustwami. Zachowuje się jak zwykły chuligan i Roger uważa go za przestępcę bez cech zawodowca. Ma Pamięć o technologii zastępczych interfejsów, kluczową dla pilotowania Megadeusów, więc zdobywa Megadeusy i używa ich do przestępstw. Odkąd Roger posłał go do więzienia po porwaniu córki Soldana, przezywa go “wroniskiem” i poprzysiągł zemstę. Raz po raz ucieka z więzienia i knuje kolejne plany, by wreszcie wykończyć Rogera.

### dic\_pilot\_DAV\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00a`

> Bladolicy podwładny Becka. Mówi w kobiecy sposób.

### dic\_pilot\_TBON\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00c`

> Pulchny podwładny Becka. Razem z Dove'em pomaga mu uciec z więzienia.

### dic\_pilot\_SHOTA\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00e`

> Prywatny detektyw z Agencji Detektywistycznej Narumi. Zgrywa twardziela, ale nie do końca mu to wychodzi i otoczenie mówi o nim czasem “twardziel na miękko”. Serdeczny, porządny chłop; jego energia i silna wola porywają innych. Kocha Fuuto, w którym się urodził i wychował; jako detektyw rozwiązuje kłopoty mieszkańców, a razem z partnerem, Philipem, jako Kamen Rider Double stawia czoło sprawom związanym z Dopantami i Gaia Memory.

### dic\_pilot\_PHILP\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b010`

> Partner Shotara. Nienasycona ciekawość, chłodny osąd i wyszukiwanie w “Bibliotece Gai” w jego umyśle czynią go mózgiem duetu. Razem z Shotarem staje się Kamen Riderem Double i stawia czoło sprawom związanym z Dopantami i Gaia Memory. Ceni logikę i teorię, więc na początku nie rozumiał uczuć Shotara, lecz w trakcie walk jego postawa zmieniła Philipa i stali się partnerami połączonymi silnym zaufaniem.

### dic\_pilot\_TOKI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b012`

> Tajemnicza kobieta, o której mieszkańcy Fuuto mówią “wiedźma ze skrzyżowania w kształcie T”. Z początku podejrzewano, że to ona jest Road Dopantem, lecz śledztwo Shotara oczyściło ją z zarzutów. Brakuje jej części wspomnień i nie pamięta, kim jest; po sprawie zostaje asystentką Shotara w Agencji Detektywistycznej Narumi.

### dic\_pilot\_AKIK\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b000`

> Szefowa Agencji Detektywistycznej Narumi. Sama nie jest detektywem, tylko zajmuje się papierami i resztą spraw. Wychowana w Osace, mistrzowsko przywołuje do porządku klapkiem. Pełna energii, czasem ściąga kłopoty, ale ma poczucie sprawiedliwości odziedziczone po ojcu, mentorze Shotara, Sokichim Narumim. Poślubiła Ryu Teruiego, którego poznała przy jednej ze spraw, lecz on wciąż mówi do niej “szefowo”.

### dic\_pilot\_TERU\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b002`

> Detektyw z Wydziału do spraw Przestępstw Nadprzyrodzonych komisariatu w Fuuto. Przemienia się w Kamen Ridera Accel i ściga przestępstwa związane z Gaia Memory. Z początku trzymał się z dala od Agencji Detektywistycznej Narumi, lecz wspólne śledztwa zrodziły zaufanie, a z szefową agencji, Akiko, nawet się ożenił. Udaje chłodnego, ale skrywa gwałtowne uczucia. Nie znosi pytań i często ucina je z góry: “Nie zadawaj mi pytań!”.

### dic\_pilot\_RIDERW\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b004`

> Postać, którą przybierają Shotaro Hidari i Philip, używając W Drivera oraz Cyclone Memory i Joker Memory. Od tych Memory forma nazywa się Cyclone Joker; wyróżnia się szybkością i siłą w walce wręcz. Zadając błyskawiczne ciosy, wchłania wiatr i odnawia siły. Zamiana Memory w lewym i prawym gnieździe Drivera pozwala przemienić się w inną formę o innych cechach i barwach. Przy przemianie świadomość jednego z nich przenosi się do ciała drugiego; w formie Cyclone Joker świadomość Philipa łączy się z ciałem Shotara.

### dic\_pilot\_AXEL\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b006`

> Postać, którą przybiera Ryu Terui, używając Accel Drivera i Accel Memory. Pamięć przyspieszenia zapisana w Accel Memory i wydobywająca ją Accel Driver dają mu nadludzką szybkość i siłę.

### dic\_pilot\_SOUKITI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b008`

> Pierwszy szef Agencji Detektywistycznej Narumi. Prywatny detektyw, uosobienie twardziela, mentor Shotara. W tajemnicy przemieniał się w Kamen Ridera Skull i walczył z przestępstwami z użyciem Gaia Memory w Fuuto. Przyjąwszy pewne zlecenie, uratował chłopaka, który stracił imię i pamięć, Philipa, lecz zginął od kuli organizacji Museum. Jego dzieło kontynuują uczeń, Shotaro, i jego partner, Philip.

### dic\_pilot\_SCULL\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00a`

> Postać, którą przybiera Sokichi Narumi, używając Lost Drivera i Skull Memory. Moc Memory zawierającej pamięć “szkieletu” wzmacnia jego ciało, a w czasie przemiany czyni go nieśmiertelnym. Jego ciało jest wtedy zimne jak u zmarłego.

### dic\_pilot\_REA\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00c`

> Kobieta szukająca “starszego pana w cylindrze”; zleciła poszukiwania kilku osobom. Łagodna, o wytwornym usposobieniu. Ktoś czyha na jej życie, więc schroniła się na A. Advencie.

### dic\_pilot\_ALF\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00e`

> Tajemniczy starszy pan. Handluje w półświatku złotymi golemami i uczy ludzi czynić zło, za co nazywa się go “Kaznodzieją Zła”. Nosi cylinder i ulubiony szal ozdobiony ornamentem w kształcie dziurki od klucza i kół zębatych.

### dic\_pilot\_ALF\_S\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b010`

> Prawdziwa, potworna postać Alfcourta. Przybierał ludzką twarz, by wtopić się w półświatek, lecz zdemaskowany odsłonił swą naturę. Mówi o sobie, że jest smakoszem. Arogancki, ludzi ma za coś niewiele więcej niż pchły wodne.

### dic\_pilot\_NEKO\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b012`

> Kot Alfcourta, który chodzi samopas. Wolny duch, pojawia się i znika, gdzie chce. Widziano go nawet unoszącego się w powietrzu.

### dic\_pilot\_IRIS\_30\_00\_0

Adres: `dic\_text\_pilot-DLC1/00202cef:2920b000`

> Samozwańcza wróżka szczęścia. Bezczelna, nieokrzesana i psotna. Naprawdę to sztuczna istota stworzona jako sługa przez Cyclaminosa, władcę Boskiej Cywilizacji Aos. Cyclaminos miał kilka takich istot, lecz większość sam ukarał i dziś pozostała tylko Iris. Po wszystkich walkach zostaje z Caruleumem w podprzestrzeni jako jeden ze strażników wymiarów.

### dic\_pilot\_HIROS\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f520b000`

> Cyborg wojownik, którego przerobił ojciec, Senjiro Shiba; przemienia się w głowę Kotetsu Jeega. Obiecujący kierowca wyścigowy i młody właściciel warsztatu samochodowego Shiba Motors. Przerobiono go bez jego wiedzy i nawet gdy zaczęła się wojna z Królestwem Jamatai, przez jakiś czas nie wiedział, że jest cyborgiem. Narwany, łatwo szarżuje; gdy dowiedział się prawdy, gryzło go, że nie jest już zwykłym człowiekiem. W końcu postanowił walczyć z Królestwem Jamatai w obronie ludzi.

### dic\_pilot\_JEEG\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6a0b001`

> Magne Robot zbudowany przez doktora Shibę do walki z Królestwem Jamatai. Powstaje, gdy Jeeg Parts wystrzelone z Big Shootera łączą się z Jeeg Headem, w którego przemienia się Hiroshi Shiba. Napędza go energia prądu magnetycznego, a jego moc wynosi 750 000 KM. Prócz ciosów, takich jak Dynamite Kick i Jeeg Breaker, ma broń taką jak Knuckle Bomber i Spin Storm, lecz jego największym atutem jest Magnet Power, która pozwala w walce wymieniać części. Prócz Mach Drill i Jeeg Bazooki w dalszej części historii korzysta też, zależnie od sytuacji, z Jeeg Bucklera oraz części Sky Parts, Earth Parts i Marine Parts.

### dic\_pilot\_JEEG\_H\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b000`

> Głowa Jeega, w którą przemienia się Cyborg Hiroshi. W tej postaci może atakować tylko Jeeg Beamem i taranowaniem; bez Big Shootera Kotetsu Jeeg jest dosłownie pozbawiony rąk i nóg. Potrafi jednak samodzielnie latać.

### dic\_pilot\_CYHIRO\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b002`

> Postać, w którą przemienia się Hiroshi Shiba, uderzając o siebie rękawicami. Okrzyk przemiany to “Change Cyborg!”. Z tej postaci może przemienić się dalej w Jeeg Heada. Ma siłę daleko przewyższającą zwykłego człowieka i bez trudu rozprawia się z żołnierzami-haniwa Królestwa Jamatai. Nie ma broni; walczy wręcz, wykorzystując swą siłę.

### dic\_pilot\_CYHIRO2\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b004`

> Nowa postać cyborga, w którą Hiroshi odrodził się po morderczym treningu. Walczy biczem Jeeg Whip z żołnierzami-robotami i robotami-bestiami. Jego sprawność jeszcze wzrosła; porusza się z nadludzką zwinnością.

### dic\_pilot\_MIWA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b006`

> Stała pilotka Big Shootera, zwana Micchi. Jej rodzice zaginęli, gdy była mała, a rodzina Shiba wychowała ją jak własną córkę. Była asystentką doktora Shiby; widząc, jak przytłaczają go badania, zgłosiła się na pilotkę Big Shootera i postanowiła poświęcić młodość walce z Królestwem Jamatai. Opanowana i odpowiedzialna, niezastąpiona partnerka Hiroshiego. Walki z Królestwem Jamatai wyczerpują ją fizycznie i psychicznie, lecz nigdy się nie skarży i wytrwale znosi trudy misji.

### dic\_pilot\_RYOMA\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b008`

> Biologiczny klon Ryomy Nagarego stworzony w innej czasoprzestrzeni. Ma wspomnienia Ryomy, lecz jest zupełnie odrębną istotą i wie, że stworzono go do walki. Ma instynktowny tryb ataku; jego siła ujawnia się w ciosie dobijającym.

### dic\_pilot\_HAYAT\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00a`

> Biologiczny klon Hayato Jina stworzony w innej czasoprzestrzeni. Ma wspomnienia Hayato, lecz jest zupełnie odrębną istotą i wie, że stworzono go do walki. Ma precyzyjny tryb ataku; jego styl walki to niezwykle dokładne ciosy bez zbędnych ruchów.

### dic\_pilot\_MUSAS\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00c`

> Biologiczny klon Musashiego Tomoe stworzony w innej czasoprzestrzeni. Ma wspomnienia Musashiego, lecz jest zupełnie odrębną istotą i wie, że stworzono go do walki. Ma logiczny tryb ataku, dlatego gdy sytuacja tego wymaga, bez wahania wybiera poświęcenie.

### dic\_pilot\_SEIJ\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00e`

> Uczeń piątej klasy szkoły podstawowej Midorigahama. Żartowniś, ale z silnym poczuciem sprawiedliwości. Od istoty, którą można nazwać wolą Ziemi, otrzymał Aurin i został kapitanem Wojowników. Jego ojciec, Koichiro, wysoki rangą wojskowy, i matka, Misuzu, prezenterka telewizyjna, rzadko bywają w domu, więc Seiji często zostaje sam i świetnie gotuje. Szczery do bólu, w dobrym i złym sensie: mówi, co myśli, i działa bez namysłu, przez co często sam pakuje się w kłopoty, ale właśnie dzięki tej prostolinijności współpracuje z Wojownikami i walczy w obronie Ziemi.

### dic\_pilot\_SEIJ\_S\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b010`

> Seiji w kombinezonie kapitana. Kombinezon chroni go, a zarazem ukrywa jego tożsamość: w razie potrzeby do hełmu dołącza się maskę zakrywającą twarz. W walce Seiji przybiera tę postać i nadajnikiem zwanym Director wydaje rozkazy Wojownikom.

### dic\_pilot\_HIKA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b012`

> Przyjaciółka Seijiego z dzieciństwa i sąsiadka. Jej rodzina prowadzi restaurację ze zdrową żywnością “Tsukushi”. Pogodna i zadziorna; Seijiego, którego rodzice rzadko bywają w domu, wciąż próbuje doglądać, choć on nieraz ma jej tego dość. Gdy Seiji mizdrzy się do innych dziewczyn, okazuje zazdrość. Nie wie, że Seiji jest kapitanem Wojowników.

### dic\_pilot\_HOTA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b014`

> Koleżanka Seijiego z klasy. Małomówna, rzadko okazuje uczucia, otacza ją aura tajemnicy. Zachowuje się tak, jakby słyszała głosy zwierząt i przyrody. Zdaje się wiedzieć, że Seiji jest kapitanem Wojowników, i czasem udziela mu rad.

### dic\_pilot\_DGAN\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b016`

> Wojownik zrodzony z Energii Planety. Odrodził się z kamienia Wojownika osadzonego na czole posągu Buddy w świątyni w Midorigahamie, gdzie mieszka Seiji. Przywódca Wojowników; często nosi Seijiego w swoim wnętrzu. Na co dzień stoi jako radiowóz przy posterunku policji.

### dic\_pilot\_DGAN\_X\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b001`

> Olbrzymi robot powstały z połączenia Da-Garna, Wojownika zrodzonego z Ziemi, z maszynami wsparcia Earth Fighter i Earth Liner. Earth Fighter tworzy górną część ciała, a Earth Liner dolną, zamykając między sobą Da-Garna. Najpotężniejszy cios to Breast Earth Buster, wiązka energii z części piersiowej w kształcie kuli ziemskiej.

### dic\_pilot\_DGAN\_GX\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b003`

> Postać powstała z Legend Combination Da-Garna X i Ga-Orna: części Ga-Orna łączą się z różnymi elementami Da-Garna X. Najpotężniejsza broń to GX Buster, powstały z połączenia G-Cannon i G-Vulcan. Po przestawieniu GX Buster działa też jako GX Buster Vulcan.

### dic\_pilot\_GAON\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b005`

> Wojownik, który odrodził się na Kilimandżaro. Walczył u boku Seijiego w zastępstwie Da-Garna, który poświęcił się, by powstrzymać rozpad kontynentu afrykańskiego. Po odrodzeniu Da-Garna połączył się z nim przez Legend Combination w Great Da-Garna GX.

### dic\_pilot\_REDRN\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b007`

> Pierwszy dowódca frontowy wysłany przez Ohbosu. Kolekcjonuje maszyny i ma własną estetykę w ich sprawie. Po porażce musiał się wycofać, lecz powrócił na Ziemię jako cyborg w swojej maszynie, Red Gaist. Dawna nieporadność zniknęła; stał się zimnym mścicielem i potęgą Red Gaista raz po raz dawał się we znaki Seijiemu, Da-Garnowi i reszcie.

### dic\_pilot\_EXIS\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b009`

> Robot stworzony przez cywilizację inną niż dzisiejsza ziemska. Reaktor bliski perpetuum mobile daje mu ogromną energię, a z nią przytłaczającą siłę bojową i wytrzymałość w długiej walce. Szczegóły techniki pozostają nieznane, lecz ma autonomiczną wolę i coś, co można nazwać sercem; działa według własnego osądu. Prostolinijny w dobrym sensie, uparty w złym, wszystko poświęca misji, czyli czynieniu sprawiedliwości. Bardzo dba o własną tożsamość i ceni imię “Exis”, które nadała mu Echika.

### dic\_pilot\_BELT\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:22a0b000`

> Członkini Karaby, organizacji wspierającej AEUG. Energiczna, ale mówi, co myśli, czym często zraża innych. Gdy natknęła się na Audhumlę, ucieszyła się, że może poznać Amura, bohatera wojny jednorocznej, którym od dawna się interesowała. Od razu zaczęła go usilnie zdobywać, a gdy Amuro znów stanął do walki, wspierała go jako ukochana.

### dic\_pilot\_COSMO\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b001`

> Syn doktora Rawla Yukiego, szefa Agencji Naukowej planety Solo, pilot A-Mechy i Ideona. Ma 16 lat. Gdy Buff Clan zaatakował planetę Solo, by się ratować, wsiadł do A-Mechy Ideona i tak, siłą rzeczy, został pilotem Ideona. Z początku walczył z gniewu na samolubnych dorosłych i obcych z Buff Clanu oraz z czystego przywiązania do życia, lecz gdy coraz wyraźniej widać było, jak niebezpieczna jest nieskończona energia Ide, zmienił zdanie o walce. Mistrzowsko rzuca nożem; potrafi strącić nim w locie miniaturowy samolot zwiadowczy. Zna się też na mechanice i pomagał serwisować elektronikę Ideona. Był cynicznym zgrywusem, lecz śmierć Camulli Lanban z bazy Brazillier, Kittie Kitten z planety kolonialnej Carale i inne wydarzenia ucieczki przed Buff Clanem uczyniły z Cosma dorosłego. Może dlatego, że wychował się wśród osadników, nie poddaje się nawet w najcięższych warunkach; nawet w beznadziejnym położeniu ostatniej bitwy z Buff Clanem do końca nie przestał walczyć o życie.

### dic\_pilot\_DEKU\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b003`

> Dziecko osadników z planety Solo, młodszy kompan Cosma. Ma 10 lat. Ma zwierzątko podobne do wiewiórki, Rapapę. Atak Buff Clanu odebrał mu rodziców; na początku ucieczki nie walczył, lecz dziecięca fascynacja bohaterami i nienawiść do Buff Clanu sprawiły, że zgłosił się na drugiego pilota A-Mechy. Z początku tylko przeszkadzał, lecz wyrósł na pilota niezbędnego dla Cosma i nieraz to on studził jego zapał. Gdy zabrakło Gije, a Kasha zrezygnowała, został głównym pilotem B-Mechy i prawdziwym wojownikiem.

### dic\_pilot\_CASHA\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b005`

> Główna pilotka C-Mechy Ideona, odpowiedzialna za kierowanie pociskami. Ma 17 lat. Odebrała elitarne wykształcenie i ma licencję mechanika rakietowego. Wychowana z dala od rodziców na A-92, planecie kolonialnej, gdzie jest tylko lato i zima, wierzy, że nie wolno na nikim polegać. Dlatego często działa na własną rękę, czym zraża innych. Miłość ma za nic; gardzi nią jako spoufalaniem się i wzajemnym oszukiwaniem. Duma i agresja sprawiają, że często rani innych słowami, za co bywa upominana. Mimo to podczas rozpaczliwej ucieczki stopniowo otwiera serce przed Cosmem.

### dic\_pilot\_LUU\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b000`

> Półtoraroczne niemowlę osadników z planety Solo. Stracił rodziców podczas ataku Buff Clanu. Jako niemowlę ma “czysty instynkt samoobrony”, a Ide na niego reaguje (Ide też ma własny instynkt samoobrony). Bez Lou trudno więc wzmocnić Ideona, a malec staje się jakby bóstwem opiekuńczym Solo Shipa.

### dic\_pilot\_HARUK\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b002`

> Master iDOL-a Imbera. Stanęła do przesłuchania, by zostać idolką, nie wiedząc, że to nabór pilotów iDOL-i; trafiła do Mondenkind, organizacji wspierającej odbudowę po światowej katastrofie, i została iDOLmasterem. Zawsze pozytywna i silna duchem, ma jednak skłonność do przyjmowania wszystkiego bez głębszego namysłu i bywa słaba. Jej znakiem rozpoznawczym jest kokarda, od której wzięło się wiele jej przezwisk. W trakcie walk odkryła, że Imber ma serce, i zbudowała z nim głęboką więź, która przerodziła się w miłość.

### dic\_pilot\_TAKT\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b004`

> Chłopak, który przybył na Wyspę Krzyża Południa. Uczeń pierwszej klasy Liceum Krzyża Południa i członek kółka teatralnego Nocny Lot. Pogodny, pozytywnie nastawiony i bezpośredni, szybko stał się w szkole ulubieńcem. Star Driver Cybody Tauburn; jako Ginga Bishonen, który osiągnął trzecią fazę, sam wsiada do Tauburna. Wako zna od chwili, gdy morze wyrzuciło go na brzeg wyspy, a ze Sugatą rywalizuje o Wako, a zarazem są najlepszymi przyjaciółmi. Walczy z Zakonem Krzyża Kiraboshi, który chce zawładnąć mocą Cybody, aż w końcu pokonuje królewskie Cybody King Samekh i swego ojca, Tokio, czyli Głowę Zakonu, który uczynił z niego narzędzie własnych ambicji, i uwalnia Sugatę i Wako od ich przeznaczenia. Po walkach wyrusza z nimi z Wyspy Krzyża Południa, by ścigać Cybody uwolnione z czasu zerowego.

### dic\_pilot\_SGATA\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b006`

> Dziedzic rodu Shindo, możnej rodziny z Wyspy Krzyża Południa. Jak Takuto uczy się w pierwszej klasie Liceum Krzyża Południa i należy do kółka teatralnego Nocny Lot. Przystojny, a przy tym chłodny intelektualista, przeciwieństwo Takuta, dzieli z nim względy dziewcząt w szkole. Wako, przyjaciółka z dzieciństwa, jest też jego narzeczoną; w głębi serca postanowił ją chronić. Włada tradycyjnymi sztukami walki; uczy Takuta, a zarazem jest jego rywalem o Wako i najlepszym przyjacielem. Driver królewskiego Cybody King Samekh; chciał własnym kosztem zapieczętować King Samekha, który wysysa wszelkie libido, lecz Głowa przejął Samekha. Uratowany przez Takuta, który pokonał Samekha, uwalnia się od przeznaczenia i szuka nowej drogi życia.

### dic\_pilot\_WAKO\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b008`

> Dziewczyna z Wyspy Krzyża Południa. To ona uratowała Takuta, gdy próbując dopłynąć do wyspy, wylądował na brzegu, i od tamtej pory są sobie bliscy. Jak Takuto uczy się w pierwszej klasie Liceum Krzyża Południa i należy do kółka teatralnego Nocny Lot. Pogodna, żywa i skłonna do bujania w obłokach. Jest Kapłanką Południa, jedną z Kapłanek Czterech Stron, które pieczętują Cybody; marzy o karierze piosenkarki, lecz z powodu swej misji nie może opuścić wyspy. Sugata, przyjaciel z dzieciństwa, jest jej narzeczonym, ale Takuto zaprząta jej myśli równie mocno. W walce z King Samekhem połączyła się z Cybody Wawna, lecz w efekcie Wawna przepadło, pieczęć kapłanek pękła, a czas zerowy zniknął. Gdy Takuto pokonuje Samekha, a ona i Sugata uwalniają się od przeznaczenia, opuszcza wyspę i szuka nowej drogi życia.

### dic\_pilot\_ANGE\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b00a`

> Już nie księżniczka, tylko po prostu Ange. Gdy wyszło na jaw, że jest Normą, straciła wszystko i musiała walczyć ze Smokami w Ragna-Mailu Villkiss. Z początku książęca duma sprawiała, że wciąż ścierała się z otoczeniem, lecz rozmaite przeżycia stopniowo zbliżyły ją do towarzyszek. Trochę uparta, ale ma silne serce, które nie ugnie się przed nikim. Wysportowana i obeznana z grą Iaria, szybko wybiła się w walce ze Smokami. Wokół upadku Arzenalu na jaw wyszło wiele prawd; gdy straciła Tuska i Momokę, którzy zawsze ją wspierali, na chwilę zgubiła sens walki, lecz niespodziewane spotkanie z Tuskiem utwierdziło ją w postanowieniu, by chronić świat.

### dic\_pilot\_ANGE\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b00b`

> Potem zastępuje Jill na stanowisku dowódcy i z pozostałymi towarzyszkami przeprowadza Last Libertas. Embryo, władający niezwykłą mocą, pojmał ją i uwięził w szczelinie między wymiarami, lecz Tusk i reszta ją uratowali, a ona zniszczyła świat podległy Embryowi.

### dic\_pilot\_ENBRW\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b000`

> Tajemnicza istota, która nazywa siebie Stroicielem. Stoi ponad wszystkimi władcami i chłodnym okiem przygląda się biegowi świata. Ma pradawną broń i technikę; ukazał się Ange w Ragna-Mailu Hysterica. Wnika w szczeliny ludzkiego serca i włada ludźmi, jakby kontrolował ich umysły; jego moc działa szczególnie na kobiety. Potrafi też sterować bólem i rozkoszą, czym zwodził Ange. Naprawdę to naukowiec z Ziemi innego świata. Gdy odkryta przez niego energia, dragonium, doprowadziła tamten świat do zagłady, porzucił swoją Ziemię i przybył do świata Ange. Uznawszy, że jedynym ratunkiem dla ludzkości jest przerobienie samych ludzi, stworzył ludzi władających Maną, lecz ich natura była daleka od jego ideału, więc postanowił przerobić cały świat. W tym celu uknuł zespolenie czasoprzestrzeni, które połączyłoby dwie Ziemie w jedną.

### dic\_pilot\_ENBRW\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b001`

> Wybrał Ange na swoją oblubienicę, z którą stworzy nowy świat, lecz ona całkowicie go odrzuciła i pokonała razem z Hysteriką, a on zniknął na zawsze.

### dic\_pilot\_EUREK\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b002`

> Starsza agentka bojowa A.C.I.D., Samodzielnego Korpusu Niezależnej Dywizji. Niegdyś potrafiła tworzyć Scab Coral (koralowe formy życia z informacji), lecz wywołała Wielkie Połączenie, katastrofę, w której Green Earth, wirtualny świat wewnątrz Scab Coral, pojawił się w prawdziwym świecie, Blue Earth, i wtedy straciła tę moc. W sercu nosi ranę po śmierci ukochanego chłopca, Rentona, który zginął przez nią, lecz tli się w niej nadzieja, że żyje w jakimś innym świecie. Otrzymuje rozkaz ochrony Iris, dziewczynki, która tak jak ona dawniej potrafi tworzyć Scab Coral, lecz po ataku Deweya obie trafiają na Ziemię i, bez wsparcia organizacji, uciekają dalej.

### dic\_pilot\_EUREK\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b003`

> Podczas samotnej podróży stopniowo zbliża się do Iris. W ostatniej walce z Deweyem, który porwał Iris, ratuje świat w Nirvashu Z i spotyka Rentona, który w nim zamieszkuje.

### dic\_pilot\_IRIS\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b004`

> Dziewczynka potrafiąca tworzyć Scab Coral. Przez porównanie z Eureką, która miała niegdyś tę samą moc, nazywa się ją “EUREKA”. Dlatego Dewey Novak z Green Earth uczynił ją swoim celem, a ona ucieka przed nim razem z Eureką.

### dic\_pilot\_IRIS\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b005`

> Podczas samotnej podróży z Eureką, z początku jej wroga, stopniowo się do niej przekonuje i zaczyna mówić do niej “ciociu”.

### dic\_pilot\_DEWEY\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b006`

> Żołnierz z Green Earth. Trafił do Blue Earth jeszcze przed Wielkim Połączeniem, a Wielkie Połączenie dało mu wiele żyć i nadprzyrodzone moce. Żywi złożone uczucia wobec Eureki, istoty, która stworzyła Green Earth; by dowieść, że on i jego pobratymcy mają wolę i serce, poluje na swoją stwórczynię, Eurekę, i na Iris, która ma tę samą moc.

### dic\_pilot\_DEWEY\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b007`

> Porywa Iris, lecz przegrywa z Eureką, która przybywa ją uratować. Umierając, wyznaje Eurece, co czuje, i strąca na Ziemię dawny międzygwiezdny statek kolonizacyjny, by zniszczyć świat.

### dic\_pilot\_RENTN\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b008`

> Chłopak, z którym łączy Eurekę wzajemna miłość. Zginął w wypadku na jej oczach i ginie także w wielu światach, które potem stworzyła. Eureka wierzy jednak, że w którymś świecie Renton żyje.

### dic\_pilot\_RENTN\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b009`

> Istnieje jako jedność z Nirvashem Z; podaje Eurece pomocną dłoń, by uratowała świat, a gdy wszystko się kończy, znów się z nią spotyka.

### dic\_pilot\_LLSH\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00a`

> 99. i jedyny cesarz Świętego Imperium Britannii. Przeprowadza reformy, które wstrząsają samymi podstawami imperium, na przykład znosi szlachtę, a zarazem chce zawładnąć całym światem i siłą zmiata wszelką opozycję.

### dic\_pilot\_SUZAK\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00c`

> Rycerz cesarza Leloucha. Był członkiem Knights of the Round, a po koronacji Leloucha został jego jedynym rycerzem, Knight of Zero. Idzie za Lelouchem, który chce zawładnąć światem, i walczy ze wszystkimi, którzy stają na drodze jego podboju.

### dic\_pilot\_CC\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00e`

> Jedna z najbliższych współpracowniczek cesarza Leloucha. Idzie za nim na drodze podboju i walczy jako jego tarcza.

### dic\_pilot\_JEREM\_A\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b010`

> Wierny sługa cesarza Leloucha. Najwierniejszy sługa cesarzowej Marianne, dziś idzie za jej synem, Lelouchem, drogą podboju.

### dic\_pilot\_KAREN\_A\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b012`

> Pół Britannijka, pół Japonka, córka britannijskiego szlachcica i Japonki, członkini Czarnych Rycerzy od ich założenia. Ma 18 lat. Umiejętnościami dorównuje, jak mówią, Knights of the Round, elicie Świętego Imperium Britannii; w ukochanym Gurenie odniosła zwycięstwo w wielu bitwach. Gdy Zero, wygnany z Czarnych Rycerzy, został cesarzem Lelouchem, Kallen spotkała go na rozmowach, dała mu pożegnalny pocałunek, a potem z towarzyszami stanęła na drodze jego podboju.

### dic\_pilot\_USPR\_S\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b014`

> Tajemnicza postać, która nazywa siebie Usurperem. Zwykle nosi maskę błazna, ukrywając tożsamość. Naprawdę to Kanoto Shijo, mieszkaniec A. Adventu, który kocha się w Anninie. Zbiera z różnych światów istoty o nieskończonej mocy, by zniszczyć świat i odrodzić go jako utopię dla siebie i Anniny. Z natury był trochę lękliwym wesołkiem, lecz moc ponad jego miarę zmieniła go w okrutnego egoistę.

### dic\_pilot\_KENAN\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84428000`

> Dowódca oddziału Dominicus, sił specjalnych podległych bezpośrednio Cathedrze, organowi nadzorczemu Rady Rozwoju MS. 21 lat temu, w incydencie Vanadis, odniósł wielkie sukcesy jako pilot Beguir-Beu. Dziś dowodzi flotą. Przez 21 lat bardzo zmienił się z sylwetki.

### dic\_pilot\_KENAN\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28000`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28000\]

### dic\_pilot\_NAZI\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28001`

> Przywódca antyspacjańskiej organizacji Dawn of Fold. Utrzymuje kontakt z Shaddiqiem; podczas ataku na Dellinga na stacji Plant Quetta porwał transportowiec i dowodził akcją.

### dic\_pilot\_OLCOT\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28003`

> Członek antyspacjańskiej organizacji Dawn of Fold, dowódca oddziału mobile suitów. Zaprawiony w bojach, cieszy się pełnym zaufaniem towarzyszy.

### dic\_pilot\_OLCOT\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28004`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28004\]

### dic\_pilot\_SOFI\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028000`

> Członkini antyspacjańskiej organizacji Dawn of Fold, pilotka Gundama Lfrith Ur. Idzie za instynktem i dla zaspokojenia pragnień nie cofnie się przed przemocą. W sercu nosi nieustanny głód, a najbardziej pragnie prawdziwej rodziny. Interesuje się Sulettą i Aerialem; nazywa siebie “wiedźmą z Ziemi”.

### dic\_pilot\_SOFI\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028001`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028001\]

### dic\_pilot\_NOREA\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028002`

> Członkini antyspacjańskiej organizacji Dawn of Fold, pilotka Gundama Lfrith Thorn. Tworzy parę z Sophie i hamuje jej skłonność do szaleństw. Nędzny los Ziemian sprawił, że głęboko nienawidzi Spacjan.

### dic\_pilot\_NOREA\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028003`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028003\]

### dic\_pilot\_CEDO\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028004`

> Ziemski chłopiec z wyznaczonej strefy odbudowy na Ziemi. Lękliwy jak na swój wiek, ale troszczy się o Seethię i trzyma się jej boku.

### dic\_pilot\_CEDO\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028005`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028005\]

### dic\_pilot\_LEADER\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028006`

> Negocjator demonstrantów podczas rozmów pokojowych, na które zgodziła się Miorine. Potępił niesprawiedliwe działania porządkowe Grupy Benerit i zażądał od Miorine, by Spacjanie opuścili Ziemię.

### dic\_pilot\_LEADER\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028007`

> Po rozmowach nabrał pewnego zaufania do Miorine i obiecał wstrzymać protesty do wyborów prezesa Grupy Benerit, lecz zaraz potem wybuchła walka, która przekreśliła ustalenia.

### dic\_pilot\_ELICT\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028008`

> Córka Prospery. Po incydencie Vanadis 21 lat temu uciekła z matką na Merkurego, lecz nie zniosła warunków kosmicznych, więc technika GUND przeniosła jej kod biometryczny do Gundama Aerial. Odtąd Gundam Aerial jest jej ciałem; chroniła Sulettę, gdy ta pilotowała Aeriala, przed burzą danych. Prospera zbudowała Quiet Zero, by stworzyć miejsce dla Ericht, która może żyć tylko w burzy danych, a Ericht stanęła na drodze Suletcie i reszcie, gdy próbowali ją powstrzymać.

### dic\_pilot\_ELICT\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028009`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028009\]

### dic\_pilot\_GOOGOL\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800a`

> Tajemniczy byt zwany “Pustką”, który 3000 lat w przyszłości walczy z ludzkością, w postaci naśladującej Psi Tsukinowę, przywódczynię Haze z Tajnych Sił Specjalnych tamtej epoki. Zainteresował się istotami zwanymi ludźmi i przybył obserwować wielki punkt zwrotny w dziejach ludzkości. Pustka nie rośnie, nie rozmnaża się, nie ma uczuć ani życia; nie jest żywą istotą, lecz “pojęciem”, które przybrało kształt. Fizyczne obrażenia dotykają więc tylko w niewielkim stopniu jej postaci w świecie trójwymiarowym, a jej źródło nigdy nie znika. By unicestwić Pustkę, trzeba zaatakować jej prawdziwą postać w wyższym wymiarze albo zniszczyć jej pojęcie w świecie trójwymiarowym. Ucząc się od ludzi serca i uczuć, traci swoje pojęcie i zyskuje w zamian życie.

### dic\_pilot\_YAGAMI\_S\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800c`

> Ojciec Echiki, Tetsuro Yagami, połączony z bestią Pustki Magudda. Uważano, że zginął w wypadku przy przebudzeniu Izany, lecz zabrał go jako obiekt obserwacji Googolplex, który zainteresował się istotami zwanymi ojcem i matką. Połączony z bestią Pustki Magudda zetknął się z Pustką; jego umysł się wypaczył, a jaźń rozpadła. Zostało mu tylko odrażające ego i obsesja na punkcie swego największego dzieła, Echiki, której bez końca szuka.

### dic\_pilot\_CROW\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800e`

> Łowca Damonów z Laboratorium Scotta. W czasie Wojny Zniszczenia w swoim Braście walczył o wolność i pokój i zdołał spłacić ogromny dług. Zgrywa nihilistycznego zawadiakę, lecz poza długo mu nie wychodzi. Ma wiele talentów; włada wojskową sztuką walki systema, więc i bez maszyny jest groźny. Twierdzi, że nie znosi kobiet, a pięknym nie ufa; przyczyna tkwi w przeszłości, lecz nie chce o niej mówić. Żałuje, że służył w specjalnym oddziale wojskowym Firebugs, i nie lubi, gdy się o tym wspomina. Po Wojnie Zniszczenia jako etatowy łowca Damonów zawodowo tępił Damony pojawiające się na całym świecie, lecz znów popadł w długi i rzucił się w wir walki. W trakcie walk w nowej maszynie, Li-Braście, budzi się w nim Sfera Chwiejnej Wagi. Od długów jednak nie uciekł. Po naprawie wymiarów wierzyciele wciąż go ścigają, ale jest w miarę zadowolony z życia.

### dic\_pilot\_ERAN\_D\_00\_0

Adres: `dic\_text\_pilot-DLC4/0036f7c2:4220b000`

> Kandydat na przyszłego prezesa Peil, z najwyższą oceną w systemie oceny SI firmy Peil, Peil Grade. Ma jednak słabe predyspozycje do pilotowania mobile suitów, więc gdy zaczęły się pojedynki o rękę Miorine, wysłał zamiast siebie wzmocnionego sobowtóra, a sam ukrył się w Peil.

### dic\_pilot\_ERAN\_5S\_00\_0

Adres: `dic\_text\_pilot-DLC4/0036f7c2:4320b000`

> Pilot wystawiany przez Peil Technologies, jedną z Trzech Filii Grupy Benerit. Uczeń 3. roku wydziału pilotażu Szkoły Technicznej Asticassia, przewodzi akademikowi Peil i zasiada w Komitecie Pojedynków. Naprawdę jest sobowtórem, któremu nadano wygląd prawdziwego Elana Ceresa; w Peil nazywają go “Wzmocnionym nr 5”. Ma anielski uśmiech; o sobie mówi, że jego życie jest “tanie”, a mimo to trzyma się życia bardziej niż ktokolwiek i walczy o przetrwanie. Zostaje pilotem testowym GUND-ARM S.A. i pomaga akademikowi Ziemian.

### dic\_pilot\_SLETA\_G\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800b`

> Gdy plan Prospery się realizuje, Suletta wpada w rozpacz: odrzucona przez Miorine, poznaje tajemnicę swoich narodzin i traci więź z Prosperą i Aerialem. Pomagając jednak odbudować szkołę zniszczoną w walce, odnajduje to, co powinna zrobić. Dowiaduje się, że jest repli-child stworzonym z genów Ericht Samayi, prawdziwej córki Prospery, a klątwa Gundama jej nie dotknęła, bo przyjęła ją na siebie Ericht, której kod biometryczny przeniesiono do Aeriala. Wtedy rusza powstrzymać Prosperę i Ericht. Podczas szturmu na Quiet Zero, cierpiąc w burzy danych, pilotuje Gundama Calibarn i w końcu razem z Ericht wyłącza międzyplanetarny laserowy system przesyłu energii Ligi Zgromadzenia Kosmicznego. Trzy lata po incydencie Quiet Zero żyje szczęśliwie, przechodząc rehabilitację po obrażeniach od burzy danych.

### dic\_pilot\_MIOLN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800c`

> Dowiedziawszy się, że Prospera traktowała Sulettę niemal jak ofiarę kontroli umysłu, postanawia zostać prezesem, pod warunkiem że Prospera nie będzie się już do niej zbliżać. By zdobyć osiągnięcia przed wyborami, podejmuje rozmowy z protestującą stroną ziemską, lecz intryga Prospery wywołuje wielką bitwę i negocjacje upadają. Dręczona poczuciem winy, zamyka się w pokoju, lecz szczerość Suletty ją ratuje i Miorine odzyskuje siłę, by iść naprzód. Z pomocą innych wdziera się do Quiet Zero i wyłącza go, a potem jako prezes Grupy Benerit ogłasza jej rozwiązanie, by zakończyć kryzys. Trzy lata po incydencie Quiet Zero wciąż robi, co może, by odpokutować za tragedię w Quin Harbor, którą wywołała.

### dic\_pilot\_GUERU\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800d`

> Po odejściu ze szkoły pracował na transportowcu jako “Bob”. Podczas ataku Dawn of Fold na Plant Quetta uciekł w mobile suicie, lecz wzięty za terrorystę, mimowolnie zestrzelił maszynę pilotowaną przez ojca, Vima. Potem, by odbudować firmę, która łączyła go z ojcem, wrócił do szkoły i został prezesem. Z Miorine zszedł na Ziemię, gdzie odkrył, że Shaddiq jest powiązany z Dawn of Fold, i własnymi rękami pokrzyżował jego plan. Brał też udział w szturmie na Quiet Zero i starł się z Gundamem Schwarzette, którym młodszy brat, Lauda, polował na Miorine. Narażając życie, Guel przemówił bratu do rozsądku, a dzięki pomocy Felsi obaj przeżyli. Trzy lata po incydencie Quiet Zero jako prezes Jeturk Heavy Machinery, z pomocą Elana i Secelii, odbudowuje firmę, choć jego słaba pozycja bywa wykorzystywana.

### dic\_pilot\_SYADIK\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800f`

> Szara eminencja wspierająca antyspacjańską organizację Dawn of Fold. Dla swojego planu zlecił atak na Plant Quetta, a nawet porwał i więził przybranego ojca, Sariusa Zenellego, prezesa Grassley. Pozyskał Peil i stanął do wyborów prezesa jako rywal Miorine, lecz przegrał walkę z Guelem, który odkrył jego powiązania z Dawn of Fold, i jego plan legł w gruzach. Trzy lata po incydencie Quiet Zero z własnej woli bierze na siebie także winy związane z Quiet Zero i staje przed sądem.

### dic\_pilot\_NKA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828010`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828010\]

### dic\_pilot\_CHUCHU\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828011`

> Incydent w Rumble Ringu sprawia, że zaczyna wierzyć, iż od jej postawy zależy, czy zbuduje przyjazne relacje ze Spacjanami. Kieruje się odtąd “wagą dialogu”; nawet poznawszy tajemnicę Niki, szuka rozmowy. Po ataku Norei na szkołę przesiada się do Demi Bardinga udostępnionego przez akademik Burion, a podczas szturmu na Quiet Zero przewozi Miorine i resztę. Trzy lata po incydencie Quiet Zero pracuje sumiennie razem z Roujim. Spotyka też Nikę, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_PROSPE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828012`

> Naprawdę nazywa się Elnora Samaya. Po ucieczce na Merkurego, by zatrzymać przy sobie ukochaną córkę, Ericht, zmarłą w dzieciństwie, przeniosła jej kod biometryczny do gundama. Stworzyła też repli-child Sulettę jako klucz do podniesienia Permet Score i ukończyła Quiet Zero, by dać miejsce do życia Ericht, która może istnieć tylko w burzy danych. Suletta i reszta ostatecznie udaremniły jej plan, lecz Prospera przyjęła życzenie Suletty i Ericht i trzy lata później spokojnie dożywa swych dni razem z nimi.

### dic\_pilot\_DERING\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828013`

> W ataku Dawn of Fold na Plant Quetta zostaje ciężko ranny. Długo pozostaje nieprzytomny, lecz powoli wraca do zdrowia, a przy tym w pewnej mierze godzi się z Miorine. Podczas szturmu na Quiet Zero pomaga, żądając od Ligi Zgromadzenia Kosmicznego zwołania nadzwyczajnego zgromadzenia ogólnego.

### dic\_pilot\_SALIUS\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828014`

> W zastępstwie nieprzytomnego Dellinga pełni rolę świadka Rumble Ringu w szkole, lecz Shaddiq go porywa i więzi. Uwolniony po aresztowaniu Shaddiqa, doradza Miorine, nowej prezes, jak ratować Grupę Benerit przed rozpadem.

### dic\_pilot\_VIM\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828015`

> Ściągnął Dawn of Fold, by pozbyć się Dellinga, lecz przez intrygę Shaddiqa sam został wciągnięty w atak na Plant Quetta. By ratować sytuację, wyruszył w mobile suicie, lecz wziął zaginionego Guela za terrorystę, starł się z nim i został zestrzelony. Dopiero wtedy obaj zrozumieli, z kim walczyli; umierając, Vim zdążył jeszcze zatroszczyć się o wstrząśniętego syna.

### dic\_pilot\_NEWGEN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828016`

> Doniosła Lidze Zgromadzenia Kosmicznego o skandalach Grupy Benerit: walkach w Szkole Technicznej Asticassia, w które wciągnięto zwykłych uczniów, porwaniu prezesa Grassley, Sariusa, i tajnej budowie Quiet Zero. Wspólnie z Ligą chciała zadać Grupie Benerit miażdżący cios, a potem przejąć kierowanie odbudową, lecz jej plan pokrzyżowała Miorine, która jako prezes ogłosiła rozwiązanie grupy.

### dic\_pilot\_KAL\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828017`

> Doniosła Lidze Zgromadzenia Kosmicznego o skandalach Grupy Benerit: walkach w Szkole Technicznej Asticassia, w które wciągnięto zwykłych uczniów, porwaniu prezesa Grassley, Sariusa, i tajnej budowie Quiet Zero. Wspólnie z Ligą chciała zadać Grupie Benerit miażdżący cios, a potem przejąć kierowanie odbudową, lecz jej plan pokrzyżowała Miorine, która jako prezes ogłosiła rozwiązanie grupy.

### dic\_pilot\_NEBORA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28000`

> Doniosła Lidze Zgromadzenia Kosmicznego o skandalach Grupy Benerit: walkach w Szkole Technicznej Asticassia, w które wciągnięto zwykłych uczniów, porwaniu prezesa Grassley, Sariusa, i tajnej budowie Quiet Zero. Wspólnie z Ligą chciała zadać Grupie Benerit miażdżący cios, a potem przejąć kierowanie odbudową, lecz jej plan pokrzyżowała Miorine, która jako prezes ogłosiła rozwiązanie grupy.

### dic\_pilot\_GOLNE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28001`

> Doniosła Lidze Zgromadzenia Kosmicznego o skandalach Grupy Benerit: walkach w Szkole Technicznej Asticassia, w które wciągnięto zwykłych uczniów, porwaniu prezesa Grassley, Sariusa, i tajnej budowie Quiet Zero. Wspólnie z Ligą chciała zadać Grupie Benerit miażdżący cios, a potem przejąć kierowanie odbudową, lecz jej plan pokrzyżowała Miorine, która jako prezes ogłosiła rozwiązanie grupy.

### dic\_pilot\_RAUDA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28003`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28003\]

### dic\_pilot\_FELCY\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28004`

> Po odejściu Guela z akademika Jeturk zastępowała go jako świadek pojedynków i wystartowała w Rumble Ringu. Gdy Guel i Lauda stoczyli zaciekłą walkę, zapobiegła wybuchowi maszyny Guela i ocaliła obu braci. Trzy lata po incydencie Quiet Zero pracuje z kolegami z akademika Jeturk, którzy ukończyli szkołę.

### dic\_pilot\_PETRA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28005`

> Gdy Norea w szale niszczyła szkołę, przygniótł ją walący się budynek i została ciężko ranna. Trzy lata po incydencie Quiet Zero z protezą nogi pracuje jako testerka GUND-ARM S.A. i spokojnie żyje u boku Laudy.

### dic\_pilot\_SSRIA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28006`

> Skłoniła Martina, zgryzionego sprawą Niki, do szczerości, dzięki czemu wyznał prawdę mieszkańcom akademika Ziemian. Gdy Norea w szale zaatakowała szkołę, pożyczyła Chuchu nowy model firmy Burion, Demi Barding. Trzy lata po incydencie Quiet Zero pracuje z prawdziwym Elanem Ceresem.

### dic\_pilot\_ROUJI\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28007`

> Z własnej ciekawości wziął udział w szturmie na Quiet Zero. Trzy lata później pracuje w tej samej firmie co Chuchu.

### dic\_pilot\_MALTN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28008`

> Przypadkiem dowiedział się, że Nika należy do terrorystów, i po wewnętrznej walce doniósł na nią firmie zarządzającej Frontem. Po cichu dręczył się tym, że wydał przyjaciółkę, lecz wyznał prawdę mieszkańcom akademika Ziemian i postanowił razem z nimi stawić czoło Nice. Do szturmu na Quiet Zero zgłosił się sam i zachował się jak prawdziwy starosta. Trzy lata po incydencie Quiet Zero spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_NUNO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28009`

> Podczas szturmu na Quiet Zero jako mieszkaniec akademika Ziemian zrobił, co do niego należało. Trzy lata później spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_OJRO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800a`

> Podczas szturmu na Quiet Zero jako mieszkaniec akademika Ziemian zrobił, co do niego należało. Trzy lata później spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_TIL\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800b`

> Podczas szturmu na Quiet Zero jako mieszkaniec akademika Ziemian zrobił, co do niego należało. Trzy lata później spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_RRKE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800c`

> Podczas szturmu na Quiet Zero jako mieszkanka akademika Ziemian zrobiła, co do niej należało. Trzy lata później spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_ALYA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800d`

> Podczas szturmu na Quiet Zero jako mieszkanka akademika Ziemian zrobiła, co do niej należało. Trzy lata później spotyka się z Niką, która odpokutowała winy, i z resztą akademika Ziemian odwiedza Sulettę i jej bliskich.

### dic\_pilot\_BELME\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800f`

> Ostrzegła Sulettę przed niebezpieczeństwem, gdy ta postanowiła wsiąść do Gundama Calibarn, by powstrzymać Quiet Zero, i przeprosiła za to, co robiła. Gdy z Miorine i resztą wdarła się do Quiet Zero, stanęła twarzą w twarz z Prosperą i przyczyniła się do jego wyłączenia. Trzy lata później z Gustonem Parche'em z Ligi Zgromadzenia Kosmicznego odwiedza groby.

### dic\_pilot\_SABINA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28010`

> Brała udział w planie Shaddiqa i została aresztowana razem z towarzyszkami, lecz uznano, że wszystko to był plan samego Shaddiqa, i ją zwolniono. Trzy lata po incydencie Quiet Zero towarzyszy Miorine, która wciąż robi, co może.

### dic\_pilot\_RENE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28011`

> Brała udział w planie Shaddiqa i została aresztowana razem z towarzyszkami, lecz uznano, że wszystko to był plan samego Shaddiqa, i ją zwolniono. Trzy lata po incydencie Quiet Zero towarzyszy Miorine, która wciąż robi, co może.

### dic\_pilot\_ILIJA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28012`

> Brała udział w planie Shaddiqa i została aresztowana razem z towarzyszkami, lecz uznano, że wszystko to był plan samego Shaddiqa, i ją zwolniono. Trzy lata po incydencie Quiet Zero towarzyszy Miorine, która wciąż robi, co może.

### dic\_pilot\_MAYG\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28013`

> Brała udział w planie Shaddiqa i została aresztowana razem z towarzyszkami, lecz uznano, że wszystko to był plan samego Shaddiqa, i ją zwolniono. Trzy lata po incydencie Quiet Zero towarzyszy Miorine, która wciąż robi, co może.

### dic\_pilot\_EONA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28014`

> Brała udział w planie Shaddiqa i została aresztowana razem z towarzyszkami, lecz uznano, że wszystko to był plan samego Shaddiqa, i ją zwolniono. Trzy lata po incydencie Quiet Zero towarzyszy Miorine, która wciąż robi, co może.

### dic\_pilot\_KENAN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428055`

> Gdy Miorine, kandydatka na prezesa Grupy Benerit, i Guel, już prezes Jeturk Heavy Machinery, schodzą na Ziemię, towarzyszy im jako ochrona. Od chłopca, Seda, którego poznał na Ziemi, dowiaduje się o powiązaniach Dawn of Fold z Shaddiqiem, rusza z Guelem do Szkoły Technicznej Asticassia i udaremnia plan Shaddiqa. W tamtej bitwie sam siada za sterami mobile suita i dowodzi oddziałem Dominicus. Potem nadal pomaga Miorine, chroni ją i resztę podczas szturmu na Quiet Zero i przyczynia się do jego wyłączenia.

### dic\_pilot\_OLCOT\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428057`

> Naprawdę nazywa się Ridrick Kruger. Służył w oddziale Dominicus; w zamachu terrorystów ziemskich stracił rodzinę.

### dic\_pilot\_SOFI\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428058`

> Chce usunąć Nikę, towarzyszkę, która im przeszkadza, lecz Suletta, by ją chronić, wyzywa Sophie na pojedynek. Sophie wdziera się do Rumble Ringu i walczy z Sulettą, lecz w trakcie walki nie wytrzymuje obciążenia wywołanego wzrostem Permet Score i ginie.

### dic\_pilot\_NOREA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428059`

> Razem z Sophie wdziera się do Rumble Ringu, lecz potem Shaddiq więzi ją w akademiku Grassley. Dla misji pilotuje gundama, lecz w głębi serca boi się śmierci i naprawdę pragnie żyć. Widząc, jak Aerial sieje zniszczenie na Ziemi, wpada w szał i atakuje szkołę. Elan przekonuje ją, by przestała, lecz zastrzelił ją snajper z oddziału Dominicus.

### dic\_pilot\_CEDO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3842805a`

> Stracił przyjaciółkę, Seethię, w ataku Grupy Benerit i żyje jako wyznaczony uchodźca. Spotyka Guela, który zszedł na Ziemię, a jedna jego mimochodem rzucona uwaga, o którą wypytuje go Kenanji, pozwala odkryć, że “Książę” to Shaddiq. Trzy lata po incydencie Quiet Zero chodzi do szkoły, o czym zawsze marzył.

### dic\_pilot\_LEADER\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828000`

> Po rozmowach nabrał pewnego zaufania do Miorine i obiecał wstrzymać protesty do wyborów prezesa Grupy Benerit, lecz zaraz potem wybuchła walka, która przekreśliła ustalenia.

### dic\_pilot\_ELICT\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828001`

> Chroniąc Prosperę przed międzyplanetarnym laserowym systemem przesyłu energii Ligi Zgromadzenia Kosmicznego, Aerial, czyli jej ciało, zostaje poważnie uszkodzony. Potem rozpływa się w cząsteczki Permetu w burzy danych o ogromnym zasięgu, lecz kod biometryczny Ericht przenosi się do breloczka Suletty, “pana Hotsa”. Trzy lata po incydencie Quiet Zero zaprzyjaźnia się nawet z Miorine.

### dic\_pilot\_ERAN\_D\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828005`

> W trakcie walk o Quiet Zero porzucił Peil i złożył wypowiedzenie. Trzy lata po zniknięciu Quiet Zero razem z Secelią pośredniczy w interesach dla Jeturka.

### dic\_pilot\_ERAN\_5S\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828006`

> W Norei Du Noc, która przeniosła się do szkoły, widział własny los i próbował ją ratować, gdy pędziła ku śmierci. Gdy poznał położenie i determinację Suletty, pomógł w szturmie na Quiet Zero. Trzy lata po incydencie Quiet Zero podróżuje, szukając miejsc ze szkicownika, który zostawiła Norea.

### dic\_pilot\_NKA\_SY\_00\_0

Adres: `dic\_text\_pilot-DLC4/007a68e4:20828000`

> Uczennica 2. roku wydziału mechaniki, mieszkanka akademika Ziemian. Chuchu mówi na nią “siostra Nika”. Łagodna i ciepła, zagadnęła Sulettę, gdy ta przeniosła się do szkoły, i dzięki niej Suletta trafiła do akademika Ziemian. Uzdolniona mechaniczka; to ona przerobiła Demi Trainera, którym lata Chuchu.

### dic\_pilot\_NKA\_SY\_00\_1

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028000`

> Gdy Suletta toczy pojedynek w przestrzeni poza Frontem, montuje na Aerialu zewnętrzny moduł napędowy. Ma jednak oblicze, którego nie znają mieszkańcy akademika Ziemian, i potajemnie utrzymuje kontakt z Shaddiqiem.

### dic\_pilot\_NKA\_SY\_00\_2

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028001`

> Była łączniczką między Shaddiqiem a antyspacjańską organizacją Dawn of Fold. Pośrednio jej działania naraziły przyjaciół i doprowadziły do tragedii, która dotknęła szkołę. Potem postanowiła własnymi siłami budować mosty między Ziemią a kosmosem i, mierząc się z tym, co zrobiła, wzięła udział w szturmie na Quiet Zero razem z Chuchu w Demi Bardingu. Po incydencie Quiet Zero oddała się w ręce władz, a po trzech latach, odpokutowawszy winy, spotyka się z mieszkańcami akademika Ziemian.

### dic\_pilot\_RAUDA\_S2\_00\_0

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028002`

> Wicestarosta akademika Jeturk, uczeń 3. roku wydziału pilotażu. Chodzi na ten sam rok co Guel, ale jest jego młodszym bratem przyrodnim. Chłodny i rozważny, a zarazem bardzo przywiązany do brata.

### dic\_pilot\_RAUDA\_S2\_00\_1

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028003`

> Po wyrzuceniu Guela przejmuje akademik jako starosta.

### dic\_pilot\_RAUDA\_S2\_00\_2

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028004`

> Po śmierci ojca, Vima, pełni obowiązki prezesa Jeturk Heavy Machinery, lecz gdy Guel wraca, oddaje mu stanowisko i zaczyna go wspierać. Kompleks wobec Guela i odkrycie, że to Guel odebrał życie Vimowi, sprawiają jednak, że winą za wszystko obarcza Miorine, a w walkach o Quiet Zero staje przeciw Guelowi. W końcu ratuje go brat, który z narażeniem życia przemawia mu do rozsądku, a dzięki pomocy Felsi obaj wychodzą z tego cało. Trzy lata po incydencie Quiet Zero trwa u boku Petry i rusza własną drogą.

## Mechy — opisy

### dic\_robot\_RIDEEN\_00\_0

Adres: `dic\_text\_robot/014d369b:92e0b000`

> Tajemniczy super robot zbudowany 12 000 lat temu dzięki nauce starożytnego Imperium Mu. Zwykle spoczywa w Skale Boskiej Twarzy jako złoty posąg i ożywa, gdy Akira wnika do jego wnętrza (Fade In). Napędza go zagadkowa energia Mutron, a pancerz z metalu mutronowego regeneruje się, wracając do stanu pierwotnego. Wiele jego tajemnic pozostaje nieodkrytych; w miarę kolejnych walk ujawniają się nowe funkcje. Głównym ciosem jest God Bird: Reideen zmienia się w ptaka i taranuje wroga z prędkością 7 Machów. Pilotować go może tylko Akira, w którym płynie krew Ra Mu, cesarza Imperium Mu, a sterowanie polega na zespoleniu ruchów maszyny z ruchami ciała Akiry.

### dic\_robot\_RIDEEN\_00\_1

Adres: `dic\_text\_robot/014d369b:9760b000`

> W ostatecznej bitwie z cesarzem Yoma Barao uwolniona energia Mutron sprawia, że Reideen urasta do gigantycznych rozmiarów.

### dic\_robot\_DROME\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b001`

> Bestia Yoma wysyłana przez Imperium Yoma. Pojawia się razem z Gante i swobodnie porusza się w powietrzu i pod wodą. Zieje ogniem i atakuje mackami. Nie jest groźna w walce, ale rzucana do boju masowo służy do nękania i powstrzymywania wroga.

### dic\_robot\_GNTE\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b003`

> Bestia Yoma Imperium Yoma pełniąca rolę ruchomej fortecy. Zbudowana w całości ze skał, ma kształt dłoni. Z paszcz smoków na końcach palców wystrzeliwuje rakiety i płomienie. W głowie-smoku tworzącej środkowy palec zasiada czasem dowódca Imperium Yoma, kierujący walką z pierwszej linii.

### dic\_robot\_GARDON\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b005`

> Połączenie bestii furii Gekido Gandera i bestii furii Gorai Geldona: Gander tworzy górną połowę ciała, a Geldon dolną. Wcześniej bestie furii przygotowane przez braci Gekido Kyoretsu i Gorai Kyoretsu, dowódców Imperium Yoma, walczyły ze sobą przed obliczem cesarza Yoma Barao, a zwycięzca ruszał na Reideena. Od Gandona Barao zaczął jednak swoją mocą stapiać obie bestie w jedną połączoną bestię furii. Jest dwa razy większy od Reideena i dysponuje przytłaczającą siłą. Potrafi też rozdzielić się na dwie bestie i walczyć, wykorzystując moc każdej z nich.

### dic\_robot\_BRAO\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b007`

> Władca Imperium Yoma. Z początku jego górna połowa wyrastała z wyspy Yoma, lecz w trakcie walk odsłonił dolną część ciała w kształcie bulwy. Przerasta Reideena wielokrotnie. Walczy gigantycznym łukiem, kosami i wielkim mieczem, a ze szponów i rogów na głowie miota potężny Promień zagłady.

### dic\_robot\_COMV\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b009`

> Łączony super robot zbudowany przez doktora Nambarę, który przewidział inwazję obcych na Ziemię, z wykorzystaniem fizyki super-elektromagnetycznej. Powstaje z połączenia pięciu maszyn bojowych: Battle Jet, Battle Crasher, Battle Tank, Battle Marine i Battle Craft. Hasło połączenia brzmi “Let's combine!”. Napędza go energia super-elektromagnetyczna, a pancerz wykonano z cermetu. Połączenie jest możliwe tylko wtedy, gdy fale mózgowe pięciorga pilotów są zgrane, co sprawdza mały robot Ropet. Wyróżnia się bogatym uzbrojeniem, które w trakcie walk jeszcze rozbudowywano, aż liczba broni sięgnęła blisko 20. Najczęściej używa ciosu Super EM Spin: wiruje z ogromną prędkością i niczym świder przebija wroga.

### dic\_robot\_BGGRD\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b00b`

> Gigantyczny robot bojowy, którym steruje Garuda, z wyglądu przypominający jego samego. Porzucony w połowie budowy, został odnaleziony przez Garudę, który sam go ukończył. Walczy Big Bow, gigantycznym łukiem wystrzeliwującym strzały-rakiety, a także rakietami z piersi i ogniem z paszczy; w ramieniu ma wbudowaną piłę łańcuchową. Gdy Garuda odkrywa, że jest androidem, wsiada do niego, by stoczyć z Combattlerem V ostateczny pojedynek na śmierć i życie.

### dic\_robot\_ZGN\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b000`

> Transformowalny mobile suit AEUG zbudowany przez Anaheim Electronics. Zwieńczenie doświadczeń projektu Zeta: łączy technologię Movable Frame z Gundama Mk-II z koncepcją Flying Armor. Pancerz z Gundarium Gamma i nowy generator zapewniają doskonały stosunek mocy do masy i bezkonkurencyjną mobilność. Wysoka moc pozwala mu używać Hyper Mega Launchera, ręcznej broni o sile porównywalnej z Mega Bazooka Launcherem. Po przemianie w Waverider zyskuje ogromny zasięg i przyspieszenie. Może samodzielnie wejść w atmosferę i latać w niej, a także przenosić na grzbiecie inną maszynę, co czyni go przydatnym w każdej sytuacji. Zamontowany później Bio-Sensor, uproszczony psycommu, pozwala mu nadążać za wyostrzonymi reakcjami Kamille'a. Odnotowano też niewyjaśnione zjawiska spoza specyfikacji, takie jak wpływanie na ruchy wrogich mobile suitów aż do ich unieruchomienia. W pierwszej wojnie z Neo Zeonem zamiast Kamille'a pilotowali go Judau i Roux.

### dic\_robot\_GD2\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b002`

> Mobile suit opracowany samodzielnie przez Titans w Gryps. To przeprojektowany pierwszy Gundam, lecz najważniejszą zmianą jest rezygnacja z systemu Core Block na rzecz Movable Frame, dzięki czemu porusza się bardziej jak człowiek i ma wysoką zwrotność. Zastosowano w nim też inne nowości, m.in. kokpit z fotelem liniowym i monitorem dookólnym oraz odczepiany system zasobnika Vulcan. Po tym, jak Kamille i inni wykradli go Titans i trafił do AEUG, przemalowano go z czarnego na biały. W pierwszej wojnie z Neo Zeonem pilotowała go głównie Elle Vianno, dzielnie stawiając czoła najnowszym mobile suitom.

### dic\_robot\_MET\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b004`

> Pierwszy transformowalny mobile suit AEUG, zbudowany przez Anaheim Electronics. Powstał do testów mechanizmu transformacji w projekcie Zeta, więc ma słabe możliwości bojowe i niezbyt wytrzymałą konstrukcję. Przydzielony do Argamy, pilotowały go Reccoa i Fa. W wersji kinowej pojawiają się dwie takie maszyny, aktywne na wielu frontach.

### dic\_robot\_GZC\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b006`

> Masowo produkowany transformowalny mobile suit Axis. Opracowany na bazie maszyn roboczych Gaza A i Gaza B jako transformowalna jednostka bojowa. W formie mobile armor ostrzeliwuje cele z Knuckle Bustera i atakuje okręty szponami nóg. Ma słabą zwrotność i kiepsko radzi sobie w zwarciu, dlatego podstawową taktyką jest zmasowany ostrzał z dystansu. Łatwo go za to produkować i fabryki Axis wytwarzały go w ogromnych ilościach. Ponieważ Axis i Siły Federacji Ziemskiej przez pewien czas współpracowały, ma oznaczenia obu armii: Axis (AMX-003) i Federacji (MMT-1). Poza wymienioną bronią ma też pistolet wiązkowy i szablę wiązkową.

### dic\_robot\_HBRB\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b008`

> Transformowalny mobile suit Titans. Liczne stabilizatory zapewniają mu wysoką zwrotność, która w formie mobile armor jeszcze rośnie. Prosty mechanizm transformacji pozwala elastycznie reagować w trakcie walki i ułatwia produkcję masową. Jego unikalna broń, Shock Wire (wąż morski), razi potężnym prądem, raniąc nie tylko maszynę, ale i pilota. Trzy maszyny z oddziału Yazana, walcząc w zgranym szyku, okazały się niezwykle groźne.

### dic\_robot\_ZO\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00a`

> Mobile suit zaprojektowany i zbudowany przez Scirocco na własny użytek. Bio-Sensor własnej konstrukcji w kokpicie zapewnia znakomite reakcje na ruchy pilota, a silniki rakietowe i dysze sterujące rozmieszczone na całym korpusie dają mu najwyższą mobilność i zwrotność. Uzbrojony jest w duży karabin wiązkowy, a w przednim pancerzu bioder skrywa specjalne ramiona (Hidden Arms), zabójczo skuteczne w walce wręcz.

### dic\_robot\_NGD\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00c`

> Mobile suit dla Newtype'ów zbudowany przez Anaheim Electronics na zamówienie Londo Bell; zaprojektował go sam pilot, Amuro. Powstał na bazie analizy osiągów wcześniejszych Gundamów i najnowszej technologii, więc choć budowano go w pośpiechu, ma wyjątkowe osiągi. Psycho-frame wbudowana wokół kokpitu zapewnia mu niezwykłą zwrotność i reakcje. Jako pierwszy mobile suit typu Gundam używa broni psycommu, Fin Funneli: są większe od zwykłych Funneli, a przez to silniejsze. Służą zarówno do ataku, jak i do obrony: kilka połączonych wytwarza I-Field, tworząc barierę antywiązkową. Aby powstrzymać zrzucenie Axis przez Neo Zeon, stoczył zwycięski pojedynek z Sazabim Chara, również wyposażonym w Psycho-frame. Widok Nu Gundama, który rozpaczliwie próbował odepchnąć Axis, zjednoczył serca wielu ludzi; Psycho-frame wytworzyła wówczas świetliste pole siłowe, które zmieniło tor Axis. To światło nazwano później “wstrząsem Axis”; odcisnęło ono piętno na wielu ludziach.

### dic\_robot\_REGZ\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00e`

> Prototypowy mobile suit zbudowany przez Anaheim Electronics. Uproszczony prototyp produkcyjny Zeta Gundama, który przechodzi w formę mobile armor po założeniu Back Weapon System. Rozwiązanie to miało podnieść łatwość produkcji przy zachowaniu wysokich osiągów i umożliwić produkcję masową. Mimo to maszyna wciąż była znacznie droższa od innych jednostek seryjnych, a do służby trafił tylko jeden egzemplarz w Londo Bell. Nazwa Re-GZ to skrót od “Refined Gundam Zeta”. Oprócz Back Weapon System ma szablę wiązkową, karabin wiązkowy, podwójny granatnik i działko Vulcan.

### dic\_robot\_REGZ\_BWS\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b010`

> Re-GZ w formie mobile armor, z założonym Back Weapon System. Zwrotność, zasięg lotu i siła ognia rosną w niej skokowo. Back Weapon System jest jednak niemal jednorazowy: po odłączeniu i powrocie do formy mobile suita nie da się go ponownie założyć na polu walki. Główne uzbrojenie to megadziało wiązkowe w nosie i wyrzutnie rakiet.

### dic\_robot\_JEG\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b012`

> Podstawowy masowo produkowany mobile suit Sił Federacji Ziemskiej. Powstał z połączenia danych projektowych licznych odmian GM-ów i Nemo i słynie z wysokich osiągów i niezawodności. Londo Bell otrzymało go w pierwszej kolejności, a później przez długie lata służył na wielu frontach. Jako pierwszy podstawowy mobile suit Federacji został zaprojektowany i był produkowany nie przez wojsko, lecz przez Anaheim Electronics. Główne uzbrojenie to karabin wiązkowy, szabla wiązkowa, system zasobnika Vulcan i granaty ręczne.

### dic\_robot\_LKAI\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b014`

> Okręt flagowy Londo Bell, nowej jednostki działającej poza strukturami Sił Federacji Ziemskiej. Dowodzi nim komandor Bright Noa. Jak wszystkie okręty przewożące Gundamy jest utrzymany w bieli. Oprócz zwykłych katapult startowych ma na rufie osobny pokład do lądowania, a obok zwykłego mostka także silnie opancerzony mostek bojowy. Ma tak dobre osiągi, że okręty tej klasy służyły jeszcze ponad 50 lat po jego zbudowaniu. Działa główne to cztery podwójne działa megacząsteczkowe; poza nimi ma liczne wyrzutnie rakiet i przeciwlotnicze karabiny maszynowe. Przed decydującą bitwą otrzymał od Camerona 15 rakiet jądrowych.

### dic\_robot\_GDOGA\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b016`

> Masowo produkowany mobile suit Neo Zeonu. Można go uznać za zwieńczenie wszystkich dotychczasowych mobile suitów Zeonu: bogate wyposażenie czyni go wszechstronnym, a prosta konstrukcja ułatwia produkcję. Stanowi trzon sił Neo Zeonu. Główne uzbrojenie to wiązkowy karabin maszynowy, wiązkowy miecz-topór, Sturm Faust, granatnik i liny elektromagnetyczne.

### dic\_robot\_GDOGA\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b000`

> Masowo produkowany mobile suit Neo Zeonu. Jako maszyna dowódcy drużyny ma tradycyjną dla Zeonu ozdobę na głowie. To osobista maszyna Rezina, pomalowana na niebiesko, ale osiągami i uzbrojeniem nie różni się zbytnio od maszyn zwykłych żołnierzy.

### dic\_robot\_JDOGA\_G\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b002`

> Mobile suit dla Newtype'ów sił Neo Zeonu, zbudowany w zakładach Anaheim Electronics w Granadzie. Powstały dwa prototypy; niebieski stał się osobistą maszyną Gyuneia. Dzięki Psycho-frame doskonale i błyskawicznie reaguje na ruchy pilota. Poza wiązkowym karabinem szturmowym, szablą wiązkową i poczwórnym działem megacząsteczkowym w tarczy ma sześć Funneli. W bitwie o Axis zestrzelił wszystkie rakiety jądrowe wystrzelone przez Londo Bell, lecz zniszczył go Nu Gundam.

### dic\_robot\_JDOGA\_Q\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b004`

> Mobile suit dla Newtype'ów sił Neo Zeonu, zbudowany w zakładach Anaheim Electronics w Granadzie. Powstały dwa prototypy; czerwony stał się osobistą maszyną Quess. Dzięki Psycho-frame doskonale i błyskawicznie reaguje na ruchy pilota. Uzbrojenie, w tym sześć Funneli, w większości pokrywa się z maszyną Gyuneia, lecz maszyna Quess ma dodatkowo megadziałko Gatling.

### dic\_robot\_AAZIL\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b006`

> Ogromny mobile armor sił Neo Zeonu dla Newtype'ów, opracowany na wzór maszyn z psycommu, takich jak Elmeth czy Qubeley. Główne uzbrojenie to działa megacząsteczkowe, podwójne działa Vulcan, Wired Psycommu Mega Arm Cannon i Funnele. Zaprojektowany do walki z okrętami, ma siłę ognia porównywalną z pancernikiem. Steruje nim psycommu, a kierowane przewodowo Mega Arm Cannon i duże Funnele umożliwiają atak z każdego kierunku. Ogromne dopalacze Sturm na nogach można po użyciu odrzucić. Z Quess za sterami został rzucony do walki jako as w rękawie Neo Zeonu w operacji ochłodzenia Ziemi.

### dic\_robot\_SAZA\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b008`

> Mobile suit dla Newtype'ów sił Neo Zeonu. Osobista maszyna wodza, Chara Aznable'a, pomalowana na szkarłatno. Psycho-frame zapewnia mu reakcje daleko lepsze od wcześniejszych maszyn. Mimo ciężkiego pancerza jest bardzo mobilny dzięki dyszom rozmieszczonym na całym korpusie: to potężna maszyna godna Chara. Uzbrojony w wiązkowy karabin śrutowy, działo megacząsteczkowe w brzuchu, szablę wiązkową i Funnele, ma miażdżącą siłę ognia.

### dic\_robot\_REUL\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00a`

> Okręt flagowy Neo Zeonu. Rozwinięcie pancernika klasy Gwazine, okrętu flagowego dawnego Księstwa Zeonu, po którym odziedziczył m.in. układ napędowy i zbiorniki chłodziwa. Siłą ognia i liczbą przewożonych mobile suitów przewyższa wszystkie okręty Neo Zeonu i Federacji; w drugiej wojnie z Neo Zeonem stanowił trzon floty.

### dic\_robot\_MSKA\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00c`

> Lekki krążownik zbudowany przez Neo Zeon. Rozwinięcie klasy Musai: żebra radiatorów chłodzą wnętrze silnika, co zwiększa zasięg rejsu. W drugiej wojnie z Neo Zeonem zbudowano wiele takich okrętów jako trzon floty, a służyły jeszcze w trzeciej wojnie.

### dic\_robot\_MNGD\_F\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00e`

> Masowo produkowany mobile suit Sił Federacji Ziemskiej. Londo Bell, obawiając się przedłużania drugiej wojny z Neo Zeonem, zaplanowało go jako seryjną wersję Nu Gundama, lepszą niż podstawowy Jegan. Uzbrojenie niemal w całości odpowiada Nu Gundamowi; na plecach montuje się moduł Incom albo Fin Funnele. Ta wersja ma Fin Funnele.

### dic\_robot\_MNGD\_I\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b010`

> Masowo produkowany mobile suit Sił Federacji Ziemskiej. Londo Bell, obawiając się przedłużania drugiej wojny z Neo Zeonem, zaplanowało go jako seryjną wersję Nu Gundama, lepszą niż podstawowy Jegan. Uzbrojenie niemal w całości odpowiada Nu Gundamowi; na plecach montuje się moduł Incom albo Fin Funnele. Ta wersja ma moduł Incom.

### dic\_robot\_F100R\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b012`

> Jeden z planów dozbrojenia Hyaku-Shiki Kai, ulepszonej wersji Hyaku-Shiki. Wbudowana w korpus broń wiązkowa i pociskowa zwiększa siłę ognia, a panele refleksyjne na piersi wzmacniają obronę. Ponieważ w tym czasie królowały duże transformowalne mobile suity, nigdy nie wszedł do produkcji seryjnej.

### dic\_robot\_GODGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b000`

> Najnowocześniejszy mobile fighter, którego Neo-Japonia wystawiła do finałów 13. Gundam Fight. Przeniesiono do niego wszystkie dane Shining Gundama, więc już w trybie normalnym przewyższa Shining Gundama w Super Mode. Odpowiednikiem Super Mode jest Hyper Mode, uruchamiany, gdy w Domonie wzbiera duch walki: rozkładają się wtedy generatory pola na plecach i otwiera mnożnik energii w piersi. Gdy Domon osiąga stan Meikyou-Shisui, całe ciało maszyny lśni złotem, a jej siła staje się przytłaczająca. Wiernie odwzorowuje techniki Domona i wyprowadza wiele ciosów. Erupting Burning Finger ma niszczycielską moc zdolną pokonać wrogiego mobile fightera jednym uderzeniem, a ostateczna technika szkoły Master Asia, Sekiha Tenkyoken, pogrzebała nawet Dark Gundama.

### dic\_robot\_RSGGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b002`

> Mobile fighter zbudowany jako prototyp Shining Gundama, przygotowany przez Ulubego do walki z Dark Gundamem. Jego bronią są m.in. Beam Naginata i łuk wiązkowy. Osiągami dorównuje Shining Gundamowi, lecz nie może użyć Super Mode; dla odchudzenia usunięto z niego część podzespołów. Odłączone naramienniki łączą się z lewym przedramieniem w Rising Shield.

### dic\_robot\_GDMST\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b004`

> Mobile fighter Neo-Ameryki przygotowany na 13. Gundam Fight. Walczy, odwzorowując bokserską technikę swojego Fightera, Chibodee'ego. Naramienniki pełnią też funkcję rękawic: wbudowane w nie dopalacze znacznie zwiększają siłę ciosów. Zrzucając pancerz z całego korpusu, traci na obronie, ale zyskuje mobilność i zwrotność. Rewolwery Gigantic Magnum pozwalają mu walczyć z dystansu, lecz prawdziwą siłę pokazuje w zwarciu, gdzie używa Burning Punch i wyćwiczonego później w morderczym treningu Burning Machine Gun Punch.

### dic\_robot\_DRGGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b006`

> Mobile fighter, którego Neo-Chiny wystawiły w 13. Gundam Fight. Odwzorowuje kung-fu Shaolin swojego Fightera, Sai Saiciego, i walczy zwinnie i nieprzewidywalnie. Wysuwane ramiona to Dragon Claw: chwyta nimi wroga z dystansu i zieje na niego żarem. Flagi Feilong na plecach wytwarzają wiązkę w kształcie sztandaru, której można używać do uderzeń, cięć i rzutów. Zna wiele technik, ale największą moc ma ostateczna technika Shaolin, Shin Ryuusei Kochouken, która spala siłę życiową pilota.

### dic\_robot\_GDROS\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b008`

> Mobile fighter, którego Neo-Francja wystawiła w 13. Gundam Fight. Podstawą jego taktyki jest szermierka Fightera, George'a, a bronią szabla Chevalier Saber. Świetnie radzi sobie też z dystansu dzięki licznym Rose Bits ukrytym w płaszczu: strzelają one wiązkami z wielu stron naraz, tworzą osłonę z sieci wiązek i mogą wybuchać, uderzając we wroga. Jego ciosem specjalnym jest Rose Screamer, który całkowicie okrąża wroga; później opanował jeszcze potężniejszy Rose Hurricane, rażący wroga gwałtownym strumieniem energii.

### dic\_robot\_BRTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00a`

> Mobile fighter, którego Neo-Rosja wystawiła w 13. Gundam Fight. W wielu miejscach korpusu ma niezależne silniki Victor, które dają mu ogromną moc i wbrew wyglądowi wysoką mobilność. Jego Fighter, Argo, woli walkę siłową i miażdży wrogów potężną masą, np. Graviton Hammer. Później opanował Bursting Gaia Crusher, w którym uderza w ziemię energią z pięści i przekształca teren, by razić wroga, a potem także Gaia Crusher z zerowej odległości, wbijający tę energię prosto w przeciwnika.

### dic\_robot\_NBGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00c`

> Mobile fighter Neo-Szwecji. Wykonuje efektowne techniki, takie jak wstęga i obręcz wiązkowa, a jego siła bojowa zaskakuje przy tak smukłej sylwetce. Najważniejszą cechą jest wbudowany Berserker System. Uruchomiony z zewnątrz, wydobywa 120％ ukrytych możliwości pilotki, Allenby, i daje jej miażdżącą siłę bojową. Podczas jego działania Allenby traci jednak rozum i przejmuje nad nią kontrolę ktoś z zewnątrz. W walce w parze z Domonem użyła ciosu specjalnego Burning Gundama, Burning Finger.

### dic\_robot\_MSTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00e`

> Najnowocześniejszy mobile fighter, którego Neo-Hongkong wystawił w 13. Gundam Fight. Ulepszona wersja Haow Gundama, zwycięzcy 12. Gundam Fight; walczy technikami szkoły Master Asia, stosowanymi przez jego Fightera, Master Asię. Skrzydła na plecach mogą zmienić się w płaszcz okrywający całe ciało. W połączeniu z mistrzostwem Master Asii ma miażdżącą siłę bojową; w finałach 13. Gundam Fight stoczył bój na śmierć i życie z Burning Gundamem Domona. Jego cios specjalny, Darkness Finger, przewyższa mocą Shining Finger Shining Gundama; potrafi też użyć ostatecznej techniki szkoły Master Asia, Sekiha Tenkyoken. Korpus zawiera komórki DG, więc regeneruje się nawet w trakcie walki.

### dic\_robot\_DTAM\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b000`

> Mobile suit tworzony dzięki samopowielaniu Dark Gundama. Pojedynczo jest znacznie słabszy od mobile fightera, ale rzucany do walki masowo stanowi awangardę armii Dark Gundama. Pilotami są ludzie zamienieni przez komórki DG w zombie. Dark Army to forma podstawowa; istnieje wiele odmian, np. Dark Birdy czy Dark Navy.

### dic\_robot\_GMTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b002`

> Postać, w której Czterej Królowie Dark Gundama, czyli Master Gundam, Gundam Heaven's Sword, Grand Gundam i Walter Gundam, odrodzili się i połączyli we wnętrzu Dark Gundama zespolonego z kolonią. Ma wszystkie zdolności Czterech Królów, a potężnymi atakami mocno daje się we znaki Sojuszowi Shuffle.

### dic\_robot\_DVGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b004`

> Przemieniona postać Ultimate Gundama zbudowanego przez Neo-Japonię. Pierwotnie miał odnowić środowisko Ziemi zgodnie z trzema zasadami: samoregeneracji, samoewolucji i samopowielania. Gdy jednak, by uniknąć wykorzystania go przez wojsko, siłą zrzucono go na Ziemię, w jego systemie doszło do awarii i zaczął dążyć do zagłady ludzkości. Dzięki samoewolucji przybiera wiele postaci; tę można uznać za ostateczną. Samopowielając się, tworzy masy swoich odrośli, Dark Army, i wciela je do swoich sił. Ma przytłaczającą moc i ogromną siłę bojową, ale do pełnego jej uwolnienia potrzebuje jednostki biologicznej. Za najlepszą uważa się kobietę, zdolną dać nowe życie.

### dic\_robot\_WG0\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b006`

> Gundam pilotowany przez Heero Yuya. Wyróżniają go ptasie skrzydła na plecach, tzw. Wing Binder, które dają mu niezwykłą mobilność i zwrotność. Pełnią też wiele innych funkcji: chronią przed żarem przy wejściu w atmosferę i amortyzują odrzut przy strzale z Buster Rifle. Zaprojektowano go do samodzielnego zdobywania baz, więc poza mobilnością ma miażdżącą siłę ognia; główna broń, Twin Buster Rifle, potrafi jednym strzałem zniszczyć kolonię. Dzięki wysokiej zwrotności świetnie walczy też wręcz szablą wiązkową. W kokpicie zainstalowano Zero System, który przez konsolę przekazuje do mózgu pilota działania potrzebne do zwycięstwa. W walce jest bardzo przydatny, ale ogromnie obciąża psychikę pilota i często wymyka się spod kontroli. Heero przezwyciężył go jednak w poprzedniej wojnie i całkowicie nad nim panuje. Po wojnie miał zostać wyrzucony w Słońce, lecz wrócił do Heero, by stłumić rebelię Armii Mariemai, i stoczył walkę z Altron Gundamem na granicy atmosfery.

### dic\_robot\_WG0\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b007`

> Następnie, by zniszczyć schron przeciwatomowy w siedzibie prezydenta, gdzie zabarykadowała się Mariemaia, mimo poważnych uszkodzeń raz po raz strzelał z Twin Buster Rifle. Schron został zniszczony, lecz odrzut rozbił maszynę, która tym samym zakończyła służbę.

### dic\_robot\_GDH\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b008`

> Gundam pilotowany przez Duo. Z rozpostartym na plecach Active Cloak, który służy za tarczę i wspomaga sterowanie, oraz z Beam Scissors w dłoniach przywodzi na myśl Ponurego Żniwiarza. Hyper Jammer, chwilowo oślepiający czujniki wroga, zapewnia mu świetne właściwości stealth; specjalizuje się w atakach z martwego pola. Także w walce twarzą w twarz Beam Scissors czyni go groźnym w zwarciu.

### dic\_robot\_GDH\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b009`

> Po stłumieniu rebelii Armii Mariemai Duo sam go zniszczył, uznając, że w czasach pokoju broń jest niepotrzebna.

### dic\_robot\_GHA\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b00a`

> Gundam pilotowany przez Trowę. Zaprojektowany do samodzielnego zdobywania baz i walki z wieloma celami naraz, ma na całym korpusie mnóstwo broni palnej. W jego budowie uczestniczyła Fundacja Barton, dlatego jego główna broń, podwójne działko Gatling, trafiła też do Serpentów. Dzięki znakomitej zwrotności używał dwóch takich działek naraz i rozbił cały oddział Serpentów.

### dic\_robot\_GHA\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b00b`

> Po stłumieniu rebelii Armii Mariemai Trowa sam go zniszczył, uznając, że w czasach pokoju broń jest niepotrzebna.

### dic\_robot\_GSR\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b00c`

> Gundam pilotowany przez Quatre'a. Jego główną bronią są wielkie Heat Shotel; wyróżnia się siłą i wytrzymałością. W głowie ma wiele czujników zapewniających doskonałe zbieranie informacji: na ich podstawie analizuje sytuację na polu walki i wydaje sojusznikom trafne rozkazy. Ma najwytrzymalszy pancerz z pięciu Gundamów, a dodatkowo może nosić płaszcz ze wzmocnionego pancerza z powłoką antywiązkową.

### dic\_robot\_GSR\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98e0b000`

> Po stłumieniu Armii Mariemai Quatre sam go zniszczył, uznając, że w czasach pokoju broń jest niepotrzebna.

### dic\_robot\_ARG\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b001`

> Gundam pilotowany przez Wufeia. Wyspecjalizowany w walce wręcz, ma znakomitą zwrotność. Jedyną bronią ręczną jest podwójny trójząb wiązkowy, co czyni go skrajnie nastawionym na zwarcie, ale Dragon Fang na obu ramionach pozwalają mu walczyć też na średnim dystansie. Broń ta, oddająca jego miano “dwugłowego smoka”, wysuwa się i chowa dowolnie, a wielostawowa budowa z połączonych kwadratowych segmentów umożliwia wyjątkowo elastyczne ataki.

### dic\_robot\_ARG\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98e0b002`

> Jako maszyna Armii Mariemai stanął na drodze Heero i reszty, lecz po stłumieniu rebelii Wufei sam go zniszczył.

### dic\_robot\_TRS\_W\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b003`

> Transformowalny mobile suit opracowany jako następca Leo w roli podstawowej maszyny. Nazwę zawdzięcza Bykowi (Taurus), jednemu z 12 znaków zodiaku. Zaprojektowano go do walki w kosmosie, lecz dzięki transformacji zachowuje wysoką mobilność również w atmosferze. Może nosić działo wiązkowe zdolne przebić nawet stop Gundanium i pod każdym względem przewyższa Leo i Aries. Białe maszyny przydzielono do obrony Królestwa Sanc; używała ich głównie Noin, która walczyła ramię w ramię z Gundamami także podczas rebelii Armii Mariemai.

### dic\_robot\_TG3\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b005`

> Pochodna Tallgeese zbudowana na polecenie Treize'a Khushrenady. Zachowuje skrajne cechy Tallgeese, czyli wysoką mobilność i ciężki pancerz, a do tego ma większą siłę ognia. Zgodnie z tym założeniem otrzymał nowy Mega Cannon, silniejszy od Dober Gun; strzałem z pełną mocą niszczy nawet satelitę surowcowego. Siłę Mega Cannon można regulować długością lufy, co pozwala elastycznie dostosować się do sytuacji. Po wojnie trafił pod nadzór Preventers, lecz podczas rebelii Armii Mariemai pilotował go Zechs Merquise.

### dic\_robot\_TRS\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b007`

> Masowo produkowany transformowalny mobile suit. Może mieć pilota, ale jako pierwszy otrzymał też bezzałogowy system bojowy Mobile Doll. Maszyny z tym systemem reagują szybciej niż przeciętny pilot, są bardzo mobilne i celnie strzelają, lecz doświadczeni piloci łatwo odczytują ich schematy działania.

### dic\_robot\_SPNT\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b009`

> Masowo produkowany ciężki mobile suit, trzon Armii Mariemai. Zbudowała go Fundacja Barton, która uczestniczyła też w tworzeniu Gundama Heavyarms. Specjalizuje się w ostrzale i może nosić potężną broń, m.in. podwójne działko Gatling i działo wiązkowe takie jak w Gundamie Heavyarms Custom. Pancerz ze stopu neotytanu, nowego materiału podobno równie twardego jak stop Gundanium, zapewnia mu wysoką wytrzymałość. Podczas rebelii Armii Mariemai blisko 400 takich maszyn wylądowało w Brukseli i walczyło z Gundamami.

### dic\_robot\_DSGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00b`

> Najnowocześniejszy mobile suit ZAFT, zbudowany, by rozstrzygnąć wojnę z Sojuszem Ziemskim. Dullindal uznał, że Impulse Gundam nie wykorzystuje w pełni szybko rosnącego talentu Shinna, i kazał dopracować szczegóły tej maszyny, która w praktyce stała się osobistym mobile suitem Shinna. Napędza go Hyper Deuterion Engine, łączący energię jądrową z systemem przesyłu energii Deuterion Beam; skrzydła wytwarzają skrzydła światła, dając mu ogromną mobilność. Łączy zalety wszystkich trzech form Impulse Gundama: ma bogate uzbrojenie na każdy dystans i znakomitą zwrotność. Do tego dochodzą unikalne funkcje, takie jak działo wiązkowe w dłoni czy powidoki tworzone przez Mirage Colloid, dzięki czemu realizuje założenie maszyny zdolnej samotnie poradzić sobie w każdej sytuacji. W bitwie o Messiaha został poważnie uszkodzony w walce z Infinite Justice, spadł na powierzchnię Księżyca i wypadł z walki.

### dic\_robot\_FIGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00d`

> Impulse Gundam z serii Second Stage, nowej generacji wysokowydajnych maszyn ZAFT, z założonym Force Silhouette. Cechy Impulse Gundama to system Deuterion Beam, pozwalający zasilać go zdalnie z okrętu-matki, mechanizm Core Splendor, w którym kokpit zmienia się w mały myśliwiec, oraz system Silhouette, czyli trzy moduły uzbrojenia dobierane do sytuacji. Spośród trzech form Impulse Gundama ta wyróżnia się mobilnością i może samodzielnie latać w atmosferze, dlatego używano jej najczęściej. Gdy Shinn przesiadł się do Destiny Gundama, przejęła ją Lunamaria, która straciła własną maszynę.

### dic\_robot\_SFRGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00f`

> Najnowocześniejszy mobile suit zbudowany razem z Infinite Justice w Factory, bazie frakcji Clyne, przeciwników Dullindala. Nowy laserowy silnik termojądrowy daje mu kilkakrotnie większą moc niż Freedom. Nowe wyposażenie, Super DRAGOON (system mobilnego uzbrojenia), to odłączane człony skrzydeł, które zwiększają mobilność i służą jako zdalnie kierowana broń wiązkowa. W pierwszym starciu z jej pomocą w ciągu zaledwie dwóch minut wyeliminował łącznie 25 ZAKU Warriorów i GOUF Ignitedów. Pancerz zmieniono na VPS, a wbudowana tarcza wiązkowa sprawia, że nie ma słabych punktów ani w ataku, ani w obronie. Wymaga jednak ogromnych umiejętności: uważa się, że poza Kirą nikt nie zdoła go w pełni wykorzystać.

### dic\_robot\_INFGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b011`

> Najnowocześniejszy mobile suit zbudowany razem ze Strike Freedom Gundamem w Factory, bazie frakcji Clyne, przeciwników Dullindala. Rozwinięcie Justice Gundama, którego Athrun pilotował w poprzedniej wojnie, z wykorzystaniem technologii serii Second Stage ZAFT. Srebrna rama kryje laserowy silnik termojądrowy, a jego znak rozpoznawczy, moduł napędowo-bojowy Fatum-01, został znacznie wzmocniony i ulepszony. W ostatecznej bitwie pokonał Destiny i zniszczył Requiem, przesądzając o losach wojny.

### dic\_robot\_ETNL\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b013`

> Okręt zbudowany przez ZAFT w poprzedniej wojnie specjalnie do obsługi Freedom Gundama i Justice Gundama; później służył jako okręt-matka ich następców, Strike Freedom Gundama i Infinite Justice Gundama. Na pokładzie służy wielu byłych członków ZAFT: symbol frakcji Clyne, Lacus, kapitan Waltfeld, a także DaCosta i Meyrin. Siłą ognia ustępuje Archangelowi, ale jest tak szybki, że z łatwością ucieka szybkim okrętom ZAFT klasy Nazca. Na dziobie ma moduły bojowe METEOR dla Strike Freedom i Infinite Justice; odłącza je, gdy maszyny ich potrzebują, a na co dzień używa ich jako baterii dział.

### dic\_robot\_UGRD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b015`

> Masowo produkowany olbrzymi mobile armor Sojuszu Ziemskiego. Nie ma tak nietypowego wyglądu jak Zamza-Zah czy Gells-Ghe, ale duże działo wiązkowe i reflektor pozytonowy zapewniają mu równowagę ataku i obrony, a do tego jest całkiem mobilny. Nie ma jednak żadnej broni do walki wręcz, więc w zwarciu jest słaby.

### dic\_robot\_ZMZZR\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b000`

> Prototypowy mobile armor Sojuszu Ziemskiego. Mimo ogromnych rozmiarów jest bardzo mobilny, a szpony i działa wiązkowe pozwalają mu walczyć na każdym dystansie. Z przodu rozpościera reflektor pozytonowy, który zatrzymuje nawet Tannhausera Minervy. Aby wykorzystać jego możliwości, potrzeba trzech pilotów: dowódcy, sternika i działonowego.

### dic\_robot\_GDARRAL\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b002`

> Mobile suit, który Suletta przywiozła z Merkurego do Szkoły Technicznej Asticassia. Zbudowała go mająca siedzibę na Merkurym korporacja Shin Sei Development. Ma GUND Format, czyli wojskowe zastosowanie GUND, technologii wzmacniania ciała z użyciem Permetu. Nie wykryto jednak u niego burz danych, typowych dla takich maszyn i obciążających ciało pilota. Wyposażony jest w GUND-Bit, system zdalnie sterowanej broni rojowej nowej generacji złożony z 11 bitów: służą one jako ruchome działa, a także jako dodatkowy napęd czy tarcza, w ataku i w obronie.

### dic\_robot\_GDARRAL\_00\_1

Adres: `dic\_text\_robot/014d369b:9920b003`

> Ze względu na swoje możliwości był podejrzewany o bycie GUND-ARM, lecz nie wyjaśniono, dlaczego nie wykryto u niego burz danych. Prawda długo pozostawała niejasna, aż prezes Shin Sei Development, Prospera, ujawniła, że to GUND-ARM.

### dic\_robot\_GDARRALRB\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b004`

> Gundam Aerial przebudowany przez Shin Sei Development. Zachował podstawową konstrukcję GUND-ARM, ale przy naprawie uszkodzeń z pojedynku z akademikiem Grassley wymieniono pancerz zewnętrzny i wyposażenie. Nowy moduł lotny z obrotowymi rozkładanymi skrzydłami znacznie poprawił zwrotność i promień skrętu. Dostał też karabin GUND-BIT: podłączenie bitów do lufy daje mu siłę ognia zdolną zagrozić okrętom.

### dic\_robot\_DMTRNR\_CC\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b006`

> Demi Trainer dostosowany przez Nikę dla Chuchu. Oparty na starszym modelu Demi Trainera, przeszedł autorskie ulepszenia, by nadrobić różnicę w osiągach. Przygotowany do taktyki “uderz i odskocz” z dużym karabinem wiązkowym, ma ruchome mocowania dopalaczy po bokach nóg, pozwalające gwałtownie przyspieszać i hamować. Kółka w stopach (mechanizm Wheel Dash) umożliwiają mu ślizg po ziemi.

### dic\_robot\_DLNZA\_GEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b008`

> Dilanza, uniwersalny mobile suit Jeturk Heavy Machinery, dostrojony dla Guela. Ma dużą moc i solidny pancerz, a spadek mobilności wynikający z większej masy rekompensuje mocniejszy napęd. Rzuca się w oczy jaskrawą magentą i bogatymi zdobieniami. Główną bronią jest partyzana wiązkowa, długa włócznia z ostrzem z wiązki. Tarcze na obu barkach mają kolce, skuteczne przy taranowaniu.

### dic\_robot\_DRLBLDE\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00a`

> Maszyna demonstracyjna piątej generacji zbudowana przez Jeturk Heavy Machinery. Ma SI wspomagającą decyzje i może działać samodzielnie, bez udziału pilota. Walczy za pomocą Isvary, jednostek ataku opartych na technologii dronów, oraz Ambiki, jednostek obronnych w kształcie dużych tarcz na barkach. Do walki wręcz służy oszczep wiązkowy, czyli połączenie kotwicy wiązkowej i szponiastego kunai wiązkowego.

### dic\_robot\_GDPHARCT\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00c`

> GUND-ARM, maszyna z GUND Format, zbudowana przez Peil Technologies. GUND Format zapewnia jej zaawansowaną kontrolę bezwładności, ale silnie obciąża ciało pilota. Na plecach i barkach ma potężne dopalacze Blast Booster do taktyki wysokiej mobilności, a w barkach kryje GUND-Bity, które wytwarzają paraliżujące wiązki elektromagnetyczne. Główna broń, arkebuz wiązkowy, dzięki łączu zmysłowemu GUND Format pozwala na niezwykle precyzyjne strzały snajperskie. W budowie maszyny uczestniczyła Belmeria, była badaczka Instytutu Vanadis.

### dic\_robot\_MCAELS\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00e`

> Najnowocześniejszy mobile suit Grassley Defense Systems. Ma Antidote, urządzenie zakłócające GUND Format. Na prawym ramieniu nosi karwasz wiązkowy, taktyczny moduł wielozadaniowy, w którym poza Antidote skupiono główne uzbrojenie, m.in. szablę wiązkową i działo wiązkowe. Karwasz może zmieniać tryby, a po odłączeniu od ramienia atakuje zdalnie, sterowany przewodowo.

### dic\_robot\_BGRPNT\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b010`

> Następca Beguir-Beu, mobile suita Grassley użytego w incydencie Vanadis. Zaprojektowany do walki z GUND-ARM, w dużej tarczy ma Antidote, urządzenie zakłócające GUND Format. Karabin wiązkowy ma duży zbiornik energii i podwójny czujnik poprawiający celność. Na pojedynek z akademikiem Ziemian akademik Grassley otrzymał pięć takich maszyn, co było zarazem testem w warunkach bojowych.

### dic\_robot\_DNBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b000`

> Prototypowy Aura Battler zbudowany przez Shota. Powstały trzy egzemplarze; ten fioletowy pilotuje Show. Jego osiągi zależą w dużej mierze od mocy aury pilota, dlatego ludziom z Byston Well i innym o słabej mocy aury trudno go opanować. W rękach kogoś o silnej aurze pokazuje jednak pełnię możliwości: Show, dzięki swojej mocy aury, odniósł na nim wiele sukcesów. Gdy Show przesiadł się do Billbine'a, maszynę przejęła Marvel; mimo że to wczesny Aura Battler, służył aż do końca wojny.

### dic\_robot\_BLBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b002`

> Najnowszy transformowalny Aura Battler zbudowany w Krainie Na. Zmienia się w Wing Caliber, co pozwala mu niespotykanie szybko dotrzeć na pole walki i równie szybko się z niego wycofać. Poza mobilnością zwiększono też siłę ognia: ma dwa wbudowane Aura Cannon i nowatorski Aura Sword Rifle, który strzela Aura Shot, a także, zamieniając moc aury bezpośrednio w ostrze, działa jako Aura Beam Sword. Dzięki temu dobrze walczy na każdym dystansie. Wymaga silnej mocy aury, ale jego potencjał w pełni to wynagradza. Królowa Krainy Na, Ciela, powierzyła go Showowi, uznawszy go za prawdziwego świętego wojownika. Dzięki potężnej aurze Showa do końca wojny stanowił trzon sił walczących z Drakiem.

### dic\_robot\_GRNGLAN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b004`

> Okręt aury zbudowany w Krainie Na. Składa się z trzech rozchodzących się segmentów i wznoszącego się nad nimi niczym zamek mostka. Jest wolniejszy od innych okrętów aury, ale stanowiska dział na każdym segmencie pozwalają mu prowadzić ogień we wszystkich kierunkach. Przewozi wiele Aura Battlerów; w walce z armią Drake'a był okrętem flagowym, obok Goraona z Krainy Rau.

### dic\_robot\_DRMR\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b006`

> Pierwszy masowo produkowany Aura Battler, zbudowany przez Shota na rozkaz Drake'a. W porównaniu z powstałym w tym samym czasie Dunbine'em ma grubszy pancerz i wbudowaną broń. Wymaga niewielkiej mocy aury i jest prostszy w obsłudze od innych Aura Battlerów, więc nadaje się dla zwykłych żołnierzy. Był tak udany, że stale ulepszany pozostał podstawową maszyną armii Drake'a do samego końca wojny.

### dic\_robot\_BARS\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b008`

> Aura Battler zbudowany w Krainie Ku. Rozwinięcie Aura Battlera dla zwykłych żołnierzy, łatwy w obsłudze nawet dla ludzi z Byston Well. Jest bardzo dobrze zrównoważony i później armia Drake'a również przyjęła go jako maszynę seryjną. Jedyną wbudowaną bronią jest Aura Vulcan, ale charakterystycznym sierpowatym ostrzem może też rzucać na krótki i średni dystans.

### dic\_robot\_RPRKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00a`

> Aura Battler zbudowany przez Shota. Nowatorska konstrukcja z bronią wbudowaną w cały korpus; wyprodukowano pewną liczbę egzemplarzy, ale słaby pancerz i brak równowagi sprawiły, że nie został podstawową maszyną. To pierwsza maszyna, która przeszła w Hyper, z Jeril za sterami.

### dic\_robot\_GLABA\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00c`

> Aura Fighter, którym walczy Czarny Rycerz. Łączy koncepcje Aura Battlera i Wing Calibera: poza wysoką mobilnością i siłą ognia radzi sobie też w zwarciu, przewyższając możliwościami wszystkie dotychczasowe maszyny aury. Jego konwerter aury jest kilkakrotnie większy niż w zwykłym Aura Battlerze, a uzyskiwana dzięki temu prędkość czyni go mistrzem taktyki “uderz i odskocz”. Choć produkowano go seryjnie, w pełni panował nad nim chyba tylko Czarny Rycerz. W walce z Showem nienawiść Czarnego Rycerza sprawiła, że przeszedł w Hyper, lecz powstrzymała go Elle, płacąc za to życiem.

### dic\_robot\_WLWPS\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00e`

> Okręt aury armii Drake'a. Ma potężną siłę ognia i wytrzymałość oraz przewozi ogromną liczbę maszyn aury; wszystko stoi w nim na najwyższym poziomie i uchodzi za najsilniejszy okręt aury. Jego pojawienie się rozpętało wojnę na wielką skalę, co w efekcie doprowadziło do usunięcia maszyn aury z Byston Well.
> 

### dic\_robot\_SRBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b010`

> Aura Battler spoczywający w świętym miejscu Baran-Baran. Jeden z nielicznych Aura Battlerów, które pozostały w Byston Well, gdy Jacoba Aon odesłał maszyny aury na powierzchnię. Zbudowano go według innej koncepcji niż pozostałe: w kokpicie nie ma żadnych monitorów, tylko specjalny hełm, dzięki któremu pilot wyczuwa cel “okiem duszy”, mocą aury. Lud Baran-Baran strzegł go przez 700 lat, aż uruchomił go Shion Zaba, wcielenie Showa Zamy, i stoczył na nim zacięte boje ze Zwauthem Czarnego Rycerza, Rabaana. Jego jedyną bronią jest miecz, ale gdy na pokładzie są Shion i Silky, wytwarza potężną barierę. Jest ona tak silna, że w ostatecznej bitwie ochroniła Shiona, Silky i Remul przed wybuchem rakiety jądrowej.

### dic\_robot\_VRVN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b012`

> Aura Battler spowity tajemnicą. Ostateczne rozwinięcie linii wysoko mobilnych Aura Battlerów wywodzącej się od Dunbine'a.

### dic\_robot\_ZWUS\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b001`

> Kruczoczarny Aura Battler, którym walczy Czarny Rycerz Rabaan. Ma cechy niespotykane u innych Aura Battlerów, takie jak ogon czy skrzydła o nietypowym kształcie.

### dic\_robot\_LGIM\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b003`

> Ręcznie zbudowany Heavy Metal klasy A, dzieło Daby Hatzera. Oparty na Gayrahmie, Heavy Metalu rodu Yaman, wszędzie wykorzystuje technologię Yaman, lecz celowo go osłabiono, by umożliwić produkcję seryjną, więc wśród Heavy Metali klasy A nie wyróżnia się osiągami. Kokpit stanowi Spiral Flow, który łagodzi fizyczne wstrząsy działające na pilota. Ponieważ moc Flossora jest za mała, do lotu potrzebuje Land Boostera.

### dic\_robot\_LGIM\_MK2\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b005`

> Heavy Metal klasy A powstały z przeróbki Amoun Duul, nowego Heavy Metalu zdobytego na armii Posaydala. Amoun Duul korzystał już z technologii Yaman, a po dodaniu m.in. systemu Spiral Flow uznano go za następcę L-Gaima i nazwano “Mk-II”. Najważniejszą cechą jest zdolność przemiany w Land Booster Plloler: pozwala to szybko dotrzeć na pole walki i się z niego wycofać, a także przewozić inne maszyny. Ulepszony względem L-Gaima system Spiral Flow zapewnia pełne unoszenie się fotela w kokpicie i ekran 360 stopni. Generator dużej mocy pozwala używać Buster Launchera, co czyni z niego potężny Heavy Metal klasy A, łączący wysoką mobilność z siłą ognia. W jego głowie czasem pojawia się sylwetka biokomputera. Pilotowany przez Dabę Myroada, stał się symbolem rebelii przeciw Posaydalowi.

### dic\_robot\_NDSD\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b007`

> Heavy Metal klasy A, który Gaw Ha Leccee otrzymała od Amandry Kamandry razem z Whele. Pierwotnie miał być inną maszyną, lecz ukończono go z użyciem technologii D-Sserda, seryjnej wersji L-Gaima, i stąd wzięła się nazwa; kokpit otrzymał wtedy system Spiral Flow. Główne uzbrojenie to Power Launchery na binderach obu ramion.

### dic\_robot\_BLBD\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b009`

> Heavy Metal klasy B armii Posaydala. Dzięki wysokiej jakości podzespołom wyraźnie przewyższa inne maszyny klasy B; trafia do żołnierzy wyższej rangi.

### dic\_robot\_BLBD\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00b`

> Heavy Metal klasy B armii Posaydala. Dzięki wysokiej jakości podzespołom wyraźnie przewyższa inne maszyny klasy B; trafia do żołnierzy wyższej rangi. To malowanie gwardii przybocznej Posaydala.

### dic\_robot\_BASH\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00d`

> Heavy Metal klasy A armii Posaydala. Specjalizuje się w walce wręcz, ale bogate wyposażenie opcjonalne pozwala mu walczyć na każdym dystansie. Może też używać Buster Launchera. W porównaniu z innymi Heavy Metalami klasy A wyprodukowano wiele jego replik.

### dic\_robot\_ASRAT\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00f`

> Heavy Metal klasy A armii Posaydala. Wyróżnia się czterema rękami: dodatkowe ramiona wyrastające z barków trzymają Circus Binder z Power Launcherem. Ma bogate wbudowane uzbrojenie i może używać Buster Launchera.

### dic\_robot\_CRBLT\_P\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b011`

> Heavy Metal klasy A armii Posaydala. Nastawiony na walkę wręcz, nie ma binderów, ale reflektory na piersi potrafią odbić nawet strzał z Power Launchera. Może też używać Buster Launchera. To malowanie maszyny Quwasan Olibee, zwanej Hellmeene.

### dic\_robot\_CRBLT\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b013`

> Heavy Metal klasy A armii Posaydala. Nastawiony na walkę wręcz, nie ma binderów, ale reflektory na piersi potrafią odbić nawet strzał z Power Launchera. Może też używać Buster Launchera. W tym malowaniu latali m.in. Ryoklay Ront i inni; istnieje kilka replik.

### dic\_robot\_GRON\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b015`

> Heavy Metal klasy A armii Posaydala. Ma Movable Frame rozmiaru S, ale generator rozmiaru M, co daje mu dużą moc. Główną bronią jest długa włócznia z wbudowanym Power Launcherem. Może też używać Buster Launchera. W porównaniu z innymi Heavy Metalami klasy A wyprodukowano wiele jego replik.

### dic\_robot\_ATOL5\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b017`

> Maszyna na zamówienie zbudowana na bazie A-Taula, Heavy Metalu klasy A armii Posaydala, z elementów pięciu Heavy Metali klasy A. Ma Round Binder z Auge, bindery z Bat-Shu, Circus Binder z Ashura Temple i długą włócznię z G.Roona. Może też używać Buster Launchera.

### dic\_robot\_AUGE\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b000`

> Heavy Metal klasy A armii Posaydala. Najbardziej wyróżnia go pancerz z prawdziwego złota, przez co jest wyjątkowo drogi. Round Bindery na barkach poruszają się niezależnie od rąk; na ich końcach są Power Launchery, a od spodu liczne Throw Lancery.

### dic\_robot\_AUG\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b002`

> Heavy Metal, którym walczył prawdziwy Oldna Posaydal. Dzięki systemowi Biorelation i energii dostarczanej przez Sveet ma miażdżącą moc: wytrzymał nawet bezpośrednie trafienie z Power Launchera z bliska. Poza launcherem i Throw Lancerami na binderze lewego barku używa składanej kosy.

### dic\_robot\_SUGEO\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b004`

> Krążownik planetarny armii Posaydala. Ma liczne wieżyczki działek laserowych i przewozi wiele Heavy Metali. Może działać w atmosferze i poza nią. To malowanie okrętu, na którym płynie Giwaza Lowaw.

### dic\_robot\_SUGEO\_M\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b006`

> Krążownik planetarny armii Posaydala. Ma liczne wieżyczki działek laserowych i przewozi wiele Heavy Metali. Może działać w atmosferze i poza nią.

### dic\_robot\_GMAZINGS\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b008`

> Super robot pilotowany przez Tetsuyę. Bratnia konstrukcja Mazingera Z o mocy godnej miana “wielkiego bohatera”. Napędza go energia fotonowa, a pancerz wykonano z Superstopu New Z. Kokpitem jest mały myśliwiec Brain Condor, który łączy się z głową, a Scramble Dash na plecach pozwala mu latać. Uzbrojenie obejmuje m.in. Breast Burn, czyli promień cieplny z płyt na piersi, oraz Thunder Break: antena na głowie ściąga pioruny, a robot ciska nimi z palców.

### dic\_robot\_DKJEN\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00a`

> Generał Imperium Mykeńskiego, dowodzący siedmioma armiami Bestii Bojowych. Ma przytłaczającą siłę: miota promienie z oczu i walczy wielkim mieczem. Jego płaszcz odbija nawet Fire Blaster Mazinkaisera.

### dic\_robot\_HRDIAS\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00c`

> Wódz upiornych Bestii Bojowych i jeden z siedmiu mykeńskich generałów. Atakuje wielką kosą, a z twarzy na lewym ramieniu wypluwa kule ognia o temperaturze 50 000 stopni.

### dic\_robot\_DANTE\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00e`

> Upiorna Bestia Bojowa. Walczy świetlistymi pierścieniami.

### dic\_robot\_MAZINKZR\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b010`

> Prototyp Mazingera Z z reaktorem energii fotonowej, zbudowany przez doktora Juzo Kabuto z pewnego świata. Nazywany jest też “Cesarzem Mazinów” i “Diabelskim Mazingerem”. Reaktor ma ogromną moc, ale trudno go kontrolować, a przy uruchomieniu grozi wymknięciem się spod kontroli. Dlatego doktor Juzo zapieczętował Kaisera razem z reaktorem w 7. hangarze Instytutu Energii Fotonowej. Obawiał się przy tym, że roboty zasilane energią fotonową, czyli Mazingery, mogą zostać użyte do złych celów, i nadał mu rolę “Mazingera, który pokona złego Mazingera”. Mazinkaiser ma też urządzenie podobne do obwodu autonomicznego, które po uruchomieniu wybiera jeden z trzech trybów: Demon, Bóg i Z. Tryb Demon włącza się po wykryciu złego Mazingera: robot walczy wtedy sam, nawet bez Pildera. Nie da się go jednak praktycznie kontrolować, a w najgorszym razie sam Kaiser staje się wcieleniem zniszczenia. Tryb Bóg uwalnia ukrytą moc Kaisera, ale szczegóły nie są znane (przypuszczalnie to odmiana Mazin Power). Wreszcie tryb Z to stan po połączeniu z Kaiser Pilderem (Pilder On); w nim Kaiser zwykle walczy. Pancerz wykonano z Superstopu New Z Alfa, a układ sterowania to Synchro System, który pozwala czerpać nieograniczoną moc z woli pilota.

### dic\_robot\_MAZINENG\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b012`

> Drugi Cesarz Mazinów zbudowany przez doktora Juzo Kabuto. Miał się uruchomić, gdy Mazinkaiserowi zagrozi niebezpieczeństwo, ale zarazem stanowić zabezpieczenie na wypadek, gdyby Mazinkaiser wymknął się spod kontroli. Zaprojektowany na bazie Great Mazingera, pod każdym względem przewyższa Mazingera Z i Great Mazingera, za co nazywa się go “Wielkim Cesarzem Mazinów”. Pierwotnie nosił nazwę “Mazin Emperor”, lecz Tetsuya Tsurugi, były pilot Great Mazingera, dodał “G” na znak, że jest on spadkobiercą Great.

### dic\_robot\_DKEN\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b014`

> Władca Imperium Mykeńskiego. Ma tak absolutną moc, że służy mu Wielki Generał Ciemności, dowódca siedmiu generałów. Przebudził się z długiego snu, by wypędzić ludzkość z powierzchni Ziemi. Całe jego ciało jest z ognia.

### dic\_robot\_BKDR\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b016`

> Mechaniczna forma życia stworzona przez Imperium Mykeńskie. Jej celem jest niszczenie obcych cywilizacji. Małe osobniki przyczepiają się do innych maszyn i przejmują nad nimi kontrolę, a duże walczą bezpośrednio.

### dic\_robot\_GTRARK\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b018`

> Getter Robo powstały z połączenia trzech Get Machine w kolejności Arc, Kirik i Khan. To Getter Robo czwartej generacji, nazywany ostatnią spuścizną doktora Saotome, byłego dyrektora Laboratorium Saotome. W porównaniu z wcześniejszymi Getter Robo jest znacznie stabilniejszy, oszczędniej gospodaruje energią i ma większą siłę bojową. Potrafi latać z ogromną prędkością, choć poddaje pilotów wielkim przeciążeniom. Uzbrojenie obejmuje m.in. Battle Shot Cutter, tnący wysuwanymi ostrzami na ramionach, oraz Thunder Bomber, rażący piorunami we wszystkie strony.

### dic\_robot\_GTRARK\_00\_1

Adres: `dic\_text\_robot/014d369b:99e0b019`

> W decydującym starciu z bestią Uzala w odległej przyszłości przebudził swoją moc i użył nowego ciosu specjalnego, Arc Shine Bomber.

### dic\_robot\_GTRKRIK\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b000`

> Getter Robo powstały z połączenia trzech Get Machine w kolejności Kirik, Khan i Arc. Specjalizuje się w szybkiej walce, posługując się na zmianę lewym ramieniem chwytnym i prawym ramieniem-świdrem. W razie potrzeby może zmienić oba ramiona w świdry; jego ciosem specjalnym jest Double Drill Storm, w którym cały zamienia się w świder i taranuje wroga.

### dic\_robot\_GTRKARN\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b002`

> Getter Robo powstały z połączenia trzech Get Machine w kolejności Khan, Arc i Kirik. Wyróżnia się siłą i świetnie walczy pod wysokim ciśnieniem, np. w głębinach morskich. Jego ciosem specjalnym jest Spine Crusher: zmienia się w gigantyczną oponę, Khan Rover, i rozrywa wroga od środka na pół. Pod wodą w formie Khan Rover może też wirować, wywołując wir Maelstrom.

### dic\_robot\_GTRTRK\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b004`

> Czarny Shin Getter Robo. Jest niezwykle szybki i w mgnieniu oka pokonuje ogromne odległości. Jego broń to m.in. dzierżony oburącz Getter Tomahawk, Getter Beam z brzucha oraz Getter Laser, czyli silnie skupiona energia Gettera z palca wskazującego.

### dic\_robot\_GTRTRK\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b005`

> Podczas operacji Jura Dead pojawił się z odsieczą Takumie i reszcie, zaatakowanym pod wodą przez Andromeda Stellaration. Wysłał ich za pomocą modułu kotwicy hiperprzestrzennej Zold poza czas i przestrzeń, po czym zniknął razem z pilotem, Go.

### dic\_robot\_GTRZURS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b006`

> Getter Robo Imperium Dinozaurów powstały z połączenia trzech Get Machine: Vorexa, Gallima i Megalona. Ukończono go dzięki technologii, którą Hayato przekazał profesorowi Hanowi z Imperium Dinozaurów. Główną bronią jest Double Stern, maczuga z kolcami na obu końcach; razem z Getterem Arc stawił czoła Andromeda Stellaration.

### dic\_robot\_GTRZURS\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b007`

> Kamui, który wrócił z odległej przyszłości, rozpoczął jego produkcję masową i uczynił go wrogiem ludzkości.

### dic\_robot\_TENKU\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b008`

> Dowódca frontowy prowadzący bojowe maszyny Insectorów. Potrafi przybierać cudzą postać i tworzyć swoje kopie, czym mocno daje się we znaki oddziałowi Gettera D2.

### dic\_robot\_TENKU\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b009`

> Został pokonany, posiekany na kawałki Double Tomahawk Gettera Arc.

### dic\_robot\_ZLDXX\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00a`

> Gigantyczna broń wysłana przez tajemniczego wroga. Dolną część ciała pokrywają niezliczone macki, którymi przebija przeciwników, a z jedynego oka w górnej części strzela wiązkami. Ma tak wytrzymały pancerz, że nie imają się go ani Getter Tomahawk, ani Getter Beam.

### dic\_robot\_ZLDXX\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b00b`

> Eksplodował, gdy w uszkodzone miejsce pancerza trafiły wiązki Gettera D2 Takumy i Gettera Arc Kamuiego.

### dic\_robot\_INSCTR\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00c`

> Broń wysyłana przez tajemniczego wroga. Wyłania się w niezliczonych ilościach z podprzestrzeni zwanej Stoker.

### dic\_robot\_UZAR\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00e`

> Superbroń cywilizacji Atlantydy, która istniała na Ziemi w zamierzchłych czasach. Razi piorunami i miota promień odcinający grawitację. Jej pancerz ze specjalnego stopu, orichalcum, jest tak wytrzymały, że gdy niegdyś walczyli z nią na Getter Dragonie ojciec Takumy, Ryoma Nagare, i jego towarzysze, nie zdołali go nawet zarysować. Po tym, jak pomogła Ryomie i reszcie rozbić Imperium Hyakki, zniknęła w kosmosie, lecz wpadła w ręce McDonalda, ocalałego z Imperium Hyakki, i stała się jego bronią.

### dic\_robot\_UZAR\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b00f`

> W walce w odległej przyszłości przytłoczyła Takumę i resztę swoją potęgą, lecz uległa Arc Shine Bomber Gettera Arc.

### dic\_robot\_BUGU\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b010`

> Superbroń zaprojektowana przez Andromeda Stellaration. Nazwa BUG to skrót od “Biogeocenosis” (ekosystem), “Unlimited” (bez granic) i “Genocidemachine” (maszyna zagłady). Kamui przywiózł do teraźniejszości dane i materiały powierzone mu przez McDonalda i ukończył ją dzięki nauce Imperium Dinozaurów. Ma absolutną moc, zdolną przekształcić całą planetę.

### dic\_robot\_BUGU\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b011`

> Swoją potężną siłą bojową przytłoczył Gettera Arc pilotowanego przez Takumę.

### dic\_robot\_GTRHDGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b012`

> Getter Dragon, który dzięki ewolucji wszedł na nowy etap. Ewoluował nieustannie głęboko pod Laboratorium Saotome, aż pojawił się na polu bitwy BUG z Getterem Arc.

### dic\_robot\_VF31JSGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b000`

> Przerobiona wersja typu J zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31J to najnowocześniejsza maszyna wsparcia w przestrzeni, przystosowana do szerokiego zakresu zadań. Nazwę zawdzięcza temu, że układ sterowania dostosowano do danych lotu pilota, Hayate Immelmanna. Malowanie i znak osobisty odziedziczył po maszynie poległego Messera Ihlefelda.

### dic\_robot\_VF31JSGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b002`

> VF-31J z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_VF31JGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b004`

> Jedna z odmian zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31 Siegfried to przeróbka VF-31A Kairos wykonana przez Xaos do tłumienia syndromu Var: zachowuje wielozadaniowy moduł kontenerowy, a przy tym ma większy kwarc fold. Dzięki temu wzmacnia fale fold zawarte w śpiewie Walkure, taktycznej jednostki muzycznej. VF-31J to najnowocześniejsza maszyna wsparcia w przestrzeni, przystosowana do szerokiego zakresu zadań. W formie Battroid ma jedno działko laserowe w głowie. W Kluczu Delta pilotuje go chorąży Hayate Immelmann, znak wywoławczy Delta 5.

### dic\_robot\_VF31JGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b006`

> VF-31J z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_VF31FSGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b008`

> VF-31F Klucza Delta z założonym Lilldrakenem, bezzałogową maszyną wsparcia armii Królestwa Windermere. VF-31F zdobyty przez armię Windermere Hayate dostroił na miejscu. Dodatkowe dysze Lilldrakena zwiększają ciąg, umożliwiając jeszcze bardziej przestrzenne manewry.

### dic\_robot\_VF31FGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00a`

> Jedna z odmian zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31 Siegfried to przeróbka VF-31A Kairos wykonana przez Xaos do tłumienia syndromu Var: zachowuje wielozadaniowy moduł kontenerowy, a przy tym ma większy kwarc fold. Dzięki temu wzmacnia fale fold zawarte w śpiewie Walkure, taktycznej jednostki muzycznej. VF-31F to wersja przewagi w przestrzeni, przeznaczona głównie do walki z wrogimi maszynami. W formie Battroid ma cztery działka laserowe w głowie. W Kluczu Delta pilotuje go porucznik Messer Ihlefeld, znak wywoławczy Delta 2; na górnej powierzchni widnieje jego znak osobisty, Żniwiarz.

### dic\_robot\_VF31FGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00c`

> VF-31F z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_VF31CGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00e`

> Jedna z odmian zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31 Siegfried to przeróbka VF-31A Kairos wykonana przez Xaos do tłumienia syndromu Var: zachowuje wielozadaniowy moduł kontenerowy, a przy tym ma większy kwarc fold. Dzięki temu wzmacnia fale fold zawarte w śpiewie Walkure, taktycznej jednostki muzycznej. VF-31C to wersja wsparcia taktycznego, która siłą ognia wspiera działania na linii frontu. W formie Battroid ma dwa działka laserowe w głowie. W Kluczu Delta pilotuje go podporucznik Mirage Farina Jenius, znak wywoławczy Delta 4.

### dic\_robot\_VF31CGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b010`

> VF-31C z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_VF31EGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b012`

> Jedna z odmian zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31 Siegfried to przeróbka VF-31A Kairos wykonana przez Xaos do tłumienia syndromu Var: zachowuje wielozadaniowy moduł kontenerowy, a przy tym ma większy kwarc fold. Dzięki temu wzmacnia fale fold zawarte w śpiewie Walkure, taktycznej jednostki muzycznej. VF-31E ma chowaną kopułę radaru do zadań wczesnego ostrzegania, rozkładaną w razie potrzeby. W formie Battroid ma dwa działka laserowe w głowie. W Kluczu Delta pilotuje go podporucznik Chuck Mustang, znak wywoławczy Delta 3.

### dic\_robot\_VF31EGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b014`

> VF-31E z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_VF31SGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b000`

> Jedna z odmian zmiennokształtnego myśliwca VF-31, używanego przez Klucz Delta z oddziału Ragna międzygwiezdnego konglomeratu Xaos. VF-31 Siegfried to przeróbka VF-31A Kairos wykonana przez Xaos do tłumienia syndromu Var: zachowuje wielozadaniowy moduł kontenerowy, a przy tym ma większy kwarc fold. Dzięki temu wzmacnia fale fold zawarte w śpiewie Walkure, taktycznej jednostki muzycznej. VF-31S, maszyna dowódcy, ma rozbudowany system łączności i kierowania. W formie Battroid ma cztery działka laserowe w głowie. W Kluczu Delta pilotuje go major Arad Molders, znak wywoławczy Delta 1; na górnej powierzchni widnieje jego znak osobisty, smocza czaszka.

### dic\_robot\_VF31SGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b002`

> VF-31S z założonym Super Packiem do działań poza atmosferą. Ma większą mobilność w przestrzeni kosmicznej.

### dic\_robot\_MCRS\_ERSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b004`

> Okręt klasy Macross, będący zarazem bazą oddziału Ragna międzygwiezdnego konglomeratu Xaos. Ma około 800 metrów długości. Przyjmuje dwie formy: fortecy i szturmową; w czasie pokoju stacjonuje na planecie Ragna w formie szturmowej. W formie szturmowej może odłączać ramiona: prawe tworzy lotniskowiec Hemera, który może też zmienić się w działo główne, Macross Cannon, a lewe lotniskowiec Aether, na którym stacjonują Klucz Delta i Walkure.

### dic\_robot\_MCRS\_GRSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b006`

> Okręt klasy Macross tej samej konstrukcji co Macross Elysion. Podstawowe wyposażenie i osiągi ma takie same, różni się malowaniem: cały okręt utrzymany jest w odcieniach zielonobrązowych.

### dic\_robot\_MCRS\_MGSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b008`

> Okręt klasy Macross tej samej konstrukcji co Macross Elysion. Podstawowe wyposażenie i osiągi ma takie same, różni się malowaniem: cały okręt utrzymany jest w odcieniach brązu.

### dic\_robot\_VF17NTMP\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00a`

> Zmiennokształtny myśliwiec N.U.N.S. Zaprojektowany tak, by radzili sobie z nim przeciętni piloci; choć powoli się starzeje, wciąż służy na wielu obszarach.

### dic\_robot\_SV262BDKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00c`

> Zmiennokształtny myśliwiec Królestwa Windermere. Najnowocześniejsza maszyna zaprojektowana do walk lokalnych i obrony baz, o znakomitej prędkości wznoszenia, przyspieszeniu i zwrotności. Ma na poszyciu optyczny system maskujący, który pozwala dowolnie zmieniać malowanie. Na obu skrzydłach przenosi bezzałogowe myśliwce Lilldraken.

### dic\_robot\_SV262BDKN\_H\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00e`

> Sv-262Ba Hermanna Kroosa z Powietrznych Rycerzy. Na górnej powierzchni nosi godło Powietrznych Rycerzy i herb rodu w kształcie topora. Pasy malowania są białe i szare.

### dic\_robot\_SV262BDKN\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b010`

> Sv-262Ba Bogue'a Con-Vaarta z Powietrznych Rycerzy. Na górnej powierzchni nosi godło Powietrznych Rycerzy i herb rodu w kształcie włóczni. Pasy malowania są różowe.

### dic\_robot\_SV262BDKN\_K\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b012`

> Sv-262Ba Kassima Eberhardta z Powietrznych Rycerzy. Na górnej powierzchni nosi godło Powietrznych Rycerzy i herb rodu w kształcie konia. Pasy malowania są pomarańczowe.

### dic\_robot\_SV262BDKN\_T\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b014`

> Sv-262Ba Thea Jussili z Powietrznych Rycerzy. Na górnej powierzchni nosi godło Powietrznych Rycerzy i herb rodu w kształcie koła. Pasy malowania są niebieskie.

### dic\_robot\_SV262BDKN\_Z\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b016`

> Sv-262Ba Xao Jussili z Powietrznych Rycerzy. Na górnej powierzchni nosi godło Powietrznych Rycerzy i herb rodu w kształcie koła. Pasy malowania są fioletowe.

### dic\_robot\_SV262BDKN\_W\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b018`

> Sv-262Ba sterowany mocą Pieśni Gwiazd za pośrednictwem Sigur Berrentzsa. Osiągi ma takie jak zwykła maszyna, ale optyczny system maskujący zmienił jego malowanie na białe.

### dic\_robot\_SV262HDKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01a`

> Maszyna dowódcy w wersji Sv-262. Należy do asa Powietrznych Rycerzy, Keitha Aero Windermere, zwanego Białym Rycerzem z Derwent. W formie Battroid ma głowę z charakterystycznymi czujnikami. Wysokiej czystości kwarc fold pochodzący od rodu królewskiego Windermere pozwala na przeciążenie silników do 130％ zwykłego ciągu. Malowanie: granat ze złotymi pasami.

### dic\_robot\_SV262HDKN\_R\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01c`

> Sv-262Hs, którym walczy Roid. Zamontowany w nim kwarc fold pochodzi od rodu królewskiego, otrzymany od poprzedniego króla. Pierwotnie stanowił jedną bryłę, lecz pękł na dwie części, które dzieli z maszyną Keitha. Malowanie, jak w Sv-262Ba z oddziałów poddanych przez Roida kontroli umysłu, jest białe, ale ze złotymi pasami.

### dic\_robot\_SGLBRNS\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01e`

> Ogromny okręt, jedna ze spuścizn Protokultury. Współdziałając z ruinami Protokultury rozsianymi po Gromadzie Kulistej Brisingr, potrafi rozprzestrzeniać “śpiew”. Tę formę uwolniła Śpiewaczka Gwiazd; przypomina ona inną spuściznę Protokultury, Człowieka-Ptaka. Świątynia w jego centrum wzmacnia moc Pieśni Gwiazd i wytwarza wokół okrętu uskok wymiarowy, który służy też jako bariera chroniąca przed atakami wroga.

### dic\_robot\_WNDBTLSP\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b020`

> Kanonierka Królestwa Windermere. Strzela wiązkami z wieżyczek rozmieszczonych na całym kadłubie.

### dic\_robot\_RRAZ\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b022`

> Osobisty KMF Zero (czyli Suzaku Kururugiego). Zbudowała go Pearl Party, prywatny instytut badawczy kierowany przez Rakshatę, w ramach Programu Zintegrowanych Rycerzy Uderzeniowych. Odtworzono go na podstawie materiałów pozostawionych przez Lloyda do badań nad technologią Knightmare Świętego Imperium Britannii, a dzięki dodaniu technologii Rakshaty osiągnął parametry równe Gurenowi S.E.I.T.E.N. Eight Elements. Z woli Schneizela, jako maszyna Zero, otrzymał czarno-fioletowe malowanie. Nazwę nadał mu sam Zero na podstawie kodu projektu. Ma ogromną siłę bojową, ale ze względu na nadmierną potęgę ograniczono jego użycie.

### dic\_robot\_GKEK\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b024`

> Duży dwumiejscowy KMF (Knightmare Frame) dla dowódcy. Zbudowała go Rakshata, przewodnicząca Światowego Komitetu Naukowego Zjednoczonej Federacji Narodów, wraz ze swoim prywatnym instytutem badawczym Pearl Party. Wywodzi się z linii Gawaina i Shinkiro, którymi dawniej walczył Lelouch. Gekkoei był pierwotnie maszyną do walki elektronicznej, lecz by Lelouch mógł walczyć na pierwszej linii, dodano mu nogi oparte na technologii dużych Knightmare Frame, takich jak Gawain, oraz liczne uzbrojenie, i tak powstał Gekkoei Sui. Jego wyposażenie korzysta z technologii Programu Zintegrowanych Rycerzy Uderzeniowych: poza systemem obronnym Absolutna obrona ma m.in. Diffusion Structure Phase Transition Cannon (zwane Absolute Zero Beam) i Hadron Blaster.

### dic\_robot\_RRSN\_WFG\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b026`

> Lancelot siN z założonym Frame Coat, dodatkowym wyposażeniem do zdobywania i obrony pozycji. Nadaje się do walki z wieloma wrogami na dystans. Siła ognia i wytrzymałość znacznie rosną, ale mobilność spada, więc przy zwrotnym przeciwniku, który wymusi walkę wręcz, jest w niekorzystnym położeniu.

### dic\_robot\_RRSN\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b001`

> KMF nowej generacji z serii Lancelot. Zaprojektowano go z powrotem do korzeni, jako maszynę prowadzącą oddział w pierwszej linii. Najbardziej wyróżniają go dwa C7 Anti-Materiel V.A.R.I.S., łączące technologię Britannii i Czarnych Rycerzy, oraz Cocoon na lewym barku i ramieniu. Cocoon to wielka bateria, służąca też jako fizyczna osłona, która znacznie wydłuża czas działania. Zwiększono też moc Energy Wings: obrona Blaze Luminous jest silniejsza, a ataki energią w kształcie ostrzy potężniejsze. Po założeniu Frame Coat radzi sobie także z liczną grupą wrogów.

### dic\_robot\_GRES\_FMH\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b003`

> Guren Type Special z założonym Frame Coat, dodatkowym wyposażeniem do zdobywania i obrony pozycji. Nadaje się do walki z wieloma wrogami na dystans. Rozbudowano też obronę: radiobariera może osłaniać całą maszynę. Siła ognia i wytrzymałość znacznie rosną, ale mobilność i zwrotność spadają, więc w pojedynkach bywa mniej skuteczny.

### dic\_robot\_GRES\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b005`

> KMF nowej generacji z serii Guren. Zachowuje cechy wcześniejszych Gurenów, ale zaprojektowano go z myślą o dobrym zaopatrzeniu, dlatego moc i zużycie energii wzrosły o około 10 procent względem poprzedniej generacji. Do lotu służą ulepszone skrzydła szybowe, wykorzystujące technologię Float Unit Britannii, które znacznie poprawiają mobilność i promień skrętu. Rozbudowano też obronę: radiobariera może osłaniać całą maszynę. Wave Surger z przewodowo sterowanego, przebijającego pancerz prawego ramienia jest jeszcze silniejszy i razi szerszy obszar, a obrotową osłonę radiacyjną można rozwinąć w kształt świdra i użyć jako broni. Do walki wręcz ma też m.in. Composite Guidance Hien Soga, ulepszony Slash Harken, oraz krótki miecz Test-Model \#1 Heat Sword. Po założeniu Frame Coat radzi sobie także z liczną grupą wrogów.

### dic\_robot\_GEDB\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b007`

> Podstawowa broń mobilna Królestwa Zilkhstanu. Symetryczna konstrukcja przód-tył eliminuje straty przy korekcie kursu i zwrotach. Pilot steruje za pomocą specjalnego wyświetlacza nagłownego; monitory w kokpicie są jedynie awaryjne i dają słabą widoczność. Poza Slash Harkenami do walki z bliska, wystrzeliwanymi z obu ramion, ma na barkach duże działa.

### dic\_robot\_BTRD\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b009`

> KGF (Knight Gigafortress) zbudowany na zamówienie przez Bitula z Królestwa Zilkhstanu. System Float służy nie do lotu, lecz do napędu korpusu, co zwiększa mobilność na lądzie. Bogate uzbrojenie obejmuje m.in. przypominający ogon Cura-la Heat Ray, Dreadnought Harken, pociski świetlne Messer i rakiety przeciwlotnicze. Ma też Capture Field, który dzięki systemowi Float chwyta cele; jego osiągi należą do najwyższej klasy światowej.

### dic\_robot\_NGSM\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b00b`

> Osobisty KMF króla Zilkhstanu, Shalia. Dla Shalia, który nie panuje w pełni nad własnym ciałem, to niejako drugie ciało, którym może swobodnie się poruszać. Float Unit wbudowane w całą maszynę dają mu szybkie reakcje i wysoką zwrotność. W trybie Megistos Omega, z którego Shalio, jego jedyny pilot, korzysta po wzmocnieniu się lekami, Float Unit pracują na granicy możliwości, minimalizując masę maszyny. Porusza się wtedy tak szybko, że zostawia powidoki, i ma miażdżącą siłę bojową. Główne uzbrojenie to miecz typu urumi z giętkiego metalu i karabin szturmowy; specjalizuje się w walce wręcz.

### dic\_robot\_RED5\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b00d`

> AHSMB dowódczo-uniwersalny zbudowany przez MJP, maszyna lidera należąca do Izuru Hitachiego. Aby wzmocnić funkcje dowodzenia, oparto go na Blue 1, uniwersalnej maszynie bojowej, na której wzorowano wszystkie AHSMB, i ulepszono m.in. komputer główny. Główną bronią jest wielofunkcyjne działo cząstek naładowanych typu 89 B (działo wiązkowe HEP), które może służyć jako piła łańcuchowa do walki wręcz, karabin wiązkowy do ostrzału lub potężne działo szynowe. Ma też bogaty wybór uzbrojenia, m.in. ciężkie wielozadaniowe działo typu 90 HM Launcher, montowane na ramieniu i strzelające różną amunicją oraz pociskami elektrycznymi, i dalekosiężne wielozadaniowe działo typu 90 Longbow z dwiema lufami na barkach.

### dic\_robot\_RED5\_00\_1

Adres: `dic\_text\_robot/014d369b:9b20b00e`

> Gdy poziom harmonii Izuru gwałtownie wzrósł, maszyna przebudziła się i przeszła w Full Burst Mode. Świadomość pilota i AHSMB zaczęła się przenikać, a wszystkie parametry skokowo wzrosły; ostatecznie maszyna zaczęła reagować tak szybko, że poruszała się, zanim pilot zdążył o tym pomyśleć.

### dic\_robot\_BLU1\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b000`

> Uniwersalny AHSMB do walki w każdych warunkach zbudowany przez MJP, maszyna Toshikazu Asagiego. Wzór dla wszystkich AHSMB, przeznaczony do walki wręcz w pierwszej linii i do ostrzału na średnim dystansie. Po wymianie uzbrojenia może walczyć z daleka, ale ustawiono go pod styl Asagiego, z naciskiem na gwałtowne przyspieszenie. Ma standardowe uzbrojenie na każdą sytuację: miecz szturmowy typu 88 Assault Blade w kształcie katany, zmienny topór-karabin typu 88 Gun Halberd, służący jako karabin wiązkowy lub halabarda, oraz przenośną wyrzutnię kierowanych pocisków typu 87 Magic Wand. Tarcze owinięte wokół obu ramion potrafią odbijać wiązki.

### dic\_robot\_BLU1\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b001`

> Na bitwę o Ceres otrzymał duże działo szynowe, ciężki akcelerator elektromagnetyczny typu 90 Eraser.

### dic\_robot\_PUR2\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b002`

> AHSMB rozpoznania i kierowania polem walki zbudowany przez MJP, maszyna Kei Kugimiyi. Łącze danych pozwala mu stale monitorować wszystkie maszyny drużyny. Na podstawie danych z trójwymiarowego czujnika złożonego, szerokopasmowego radaru o ultrawysokiej rozdzielczości oraz łączy z okrętem-matką i satelitami zwiadowczymi wyznacza najlepsze działania w danej sytuacji. Wielokanałowy system wsparcia elektronicznego, dwa komputery główne i zapasowy pozwalają mu przetwarzać dane nawet 10 AHSMB naraz. Uzbrojenie ma jednak tylko minimalne, wystarczające do samoobrony. Przy trafieniu łagodzi uderzenie tarczą wytwarzaną przez osłonę cząsteczkową typu 91 Active Guard.

### dic\_robot\_ROS3\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b004`

> Wysoko mobilny AHSMB do walki manewrowej zbudowany przez MJP, maszyna Tamaki Irie. Nastawiony na prędkość, ma jako dopalacz napęd stosowany w okrętach. Wielostopniowe silniki wysokiego przyspieszenia i tłumik grawitacji pozwalają mu przyspieszać z siłą ponad 20 G. Do panowania nad ogromną mocą służą dwa komputery główne. Główne uzbrojenie to wbudowane działo ciężkich cząstek typu 88, strzelające z soczewki w biodrach i z ramion, oraz emiter ciężkich cząstek typu 89 Mega Beam Launcher na szczycie i końcach dopalacza; ma też różne pociski kierowane. Dzięki dużej mocy może holować inne AHSMB.

### dic\_robot\_GLD4\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b006`

> AHSMB wsparcia ogniowego na bardzo dalekim dystansie zbudowany przez MJP, maszyna Ataru Surugi. Zaprojektowany do ostrzału: cała jego głowa to zaawansowany czujnik artyleryjski. Cztery silniki pomocnicze zasilają działa i systemy kierowania ogniem. Podstawowe uzbrojenie to działo cząstek naładowanych wysokiej mocy i szybkostrzelne działo rezonansu fotonowego z naprowadzaniem radiacyjnym, ale na mocowaniach może nosić niemal każdą broń strzelecką GDF i MJP. Dzięki łączu z Purple 2 trafia precyzyjnie nawet cele daleko poza zasięgiem wzroku.

### dic\_robot\_GLD4\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b007`

> Podczas obrony Akademii Miejskiej Glanzehre, połączony systemem kierowania z Purple 2, strzelał z kosmosu w cele na powierzchni z ciężkiego działa wiązkowego skupionego typu 90 Freischutz; w bitwie o bramę połączył się z dziobem i układem sterowania Godiniona i przejął kontrolę nad jego działem głównym.

### dic\_robot\_BRK6\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b008`

> Uniwersalny AHSMB nowej generacji przeznaczony do produkcji seryjnej, maszyna Ange Kuroki. Oparty na danych bojowych od Blue 1 do Red 5 i na konstrukcji Red 5; z myślą o produkcji uproszczono kształt pancerza i wiele elementów. Uzbrojenie jest modułowe, co pozwala na szybką obsługę i ponowny start. Obsługę zautomatyzowano, by zmniejszyć liczbę potrzebnego personelu. Może nosić wiele broni, a salwy m.in. z naramiennych pocisków krótkiego zasięgu typu 91 Sidearm i wielolufowych pocisków na nogach typu 91 Black Fire dają mu ogromną siłę ognia.

### dic\_robot\_LYNS\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00a`

> Wysoko mobilne wielozadaniowe urządzenie bojowe drużyny Team Doberman. Służy do testowania części dla AHSMB; opracowano je, łącząc naukę spoza Układu Słonecznego z dotychczasową teorią Ioness. Podobnie jak AHSMB ma system Juria. Główne uzbrojenie to działo szynowe podłączane do mocowania na boku ramienia i Beam Finger, broń do walki wręcz na ramionach pomocniczych.

### dic\_robot\_LYNS\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b00b`

> W operacji Eagle Landed użyto ciężkich mieczy uderzeniowych typu 88 Twin Claymore, montowanych na ramionach.

### dic\_robot\_GDNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00c`

> Duży mobilny lotniskowiec bojowy MJP. Silny napęd pozwala mu rozpościerać mocną tarczę, a w połączeniu z nowym pancerzem stosowanym w AHSMB zapewnia mu wysoką wytrzymałość. Kadłub ma budowę modułową: można odłączyć część dziobową, moduł mostka, silników, skrzydeł i inne. Obracając dwa żagle słoneczne pod modułem skrzydeł, pochłania światło słoneczne i zamienia je na energię napędu. Na dziobie przewozi pity, okręty wsparcia Team Rabbits.

### dic\_robot\_MZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00e`

> Osobista broń mobilna Jiarta. Nosi specjalny biały kolor, zarezerwowany dla rodziny cesarskiej. Ma znakomitą zwrotność i reakcje, a w rękach Jiarta, wrodzonego mistrza walki wręcz, pokazuje pełnię możliwości.

### dic\_robot\_MZIAT\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b00f`

> Ma system zwiększający moc zależnie od emocji pilota; w starciu z Red 5 przeszedł w Overlord Mode i stoczył zacięty bój.

### dic\_robot\_MCLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b010`

> Osobista maszyna dowódcy legionu Wulgaru, Kleina. Nastawiona na mobilność i przyspieszenie, specjalizuje się w taktyce “uderz i odskocz”. Prawe ramię kończy się ogromnym szponem, a w rękach i nogach ukryto działa wiązkowe. Jak maszyny jego podkomendnych, jest utrzymana w odcieniach fioletu.

### dic\_robot\_MCLIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b000`

> Po kolejnych porażkach przeszedł wzmacniającą przebudowę.

### dic\_robot\_MLTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b001`

> Osobista maszyna dowódczyni legionu Wulgaru, Lutiel. Nastawiona na prędkość, specjalizuje się w przełamujących atakach skupionych na jednym punkcie. Za tarcze służą jej skrzydła, które mogą też strzelać wiązkami, a działa wiązkowe w dłoniach zmieniają kształt w szable do walki wręcz. Jak maszyny jej podkomendnych, jest utrzymana w odcieniach żółci.

### dic\_robot\_MDLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b003`

> Osobista maszyna dowódcy legionu Wulgaru, Dolgany. Ciężka maszyna szturmowa, specjalizująca się w walce czołowej. Silny ogień i potężny pancerz czynią ją groźną w ataku i obronie, a przy tym jest całkiem mobilna. Jak maszyny jego podkomendnych, jest utrzymana w odcieniach czerwieni.

### dic\_robot\_UMM\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b005`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; zielone malowanie oznacza oddział, którym dowodzi Rada.

### dic\_robot\_UMM\_RADA\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b006`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UMM\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b007`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; fioletowe malowanie oznacza oddział, którym dowodzi Klein.

### dic\_robot\_UMM\_CLIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b008`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UMM\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b009`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; żółte malowanie oznacza oddział, którym dowodzi Lutiel.

### dic\_robot\_UMM\_LTEL\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00a`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UMM\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00b`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; czerwone malowanie oznacza oddział, którym dowodzi Dolgana.

### dic\_robot\_UMM\_DLGN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00c`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UMM\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00d`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; pomarańczowe malowanie oznacza oddział, którym dowodzi Lumes.

### dic\_robot\_UMM\_RMES\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00e`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UMM\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00f`

> Biologiczna broń mobilna Wulgaru. Przewyższa dotychczasową broń GDF i dobitnie pokazała, jak groźni są Wulgaru. Walczy działem wiązkowym ukrytym w dłoni i mieczem, który tworzą złączone szpony ramienia. Barwy i osiągi zależą od oddziału; błękitne malowanie oznacza oddział, którym dowodzi Jiart.

### dic\_robot\_UMM\_ZIAT\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b010`

> Maszyny są klonowane razem z żołnierzami i produkowane masowo na bazie najlepszych genów.

### dic\_robot\_UAM\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b011`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; zielone malowanie oznacza oddział, którym dowodzi Rada.

### dic\_robot\_UAM\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b000`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; fioletowe malowanie oznacza oddział, którym dowodzi Klein.

### dic\_robot\_UAM\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b002`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; żółte malowanie oznacza oddział, którym dowodzi Lutiel.

### dic\_robot\_UAM\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b004`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; czerwone malowanie oznacza oddział, którym dowodzi Dolgana.

### dic\_robot\_UAM\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b006`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; pomarańczowe malowanie oznacza oddział, którym dowodzi Lumes.

### dic\_robot\_UAM\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b008`

> Ulepszona wersja biologicznej broni mobilnej Wulgaru. Ma lepsze osiągi niż maszyny zwykłych oddziałów i silniejsze wiązki. Jak cała broń Wulgaru, ma barwy zależne od oddziału; błękitne malowanie oznacza oddział, którym dowodzi Jiart.

### dic\_robot\_UBS\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00a`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; zielone malowanie oznacza oddział, którym dowodzi Rada.

### dic\_robot\_UBS\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00c`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; fioletowe malowanie oznacza oddział, którym dowodzi Klein.

### dic\_robot\_UBS\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00e`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; żółte malowanie oznacza oddział, którym dowodzi Lutiel.

### dic\_robot\_UBS\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b010`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; czerwone malowanie oznacza oddział, którym dowodzi Dolgana.

### dic\_robot\_UBS\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b012`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; pomarańczowe malowanie oznacza oddział, którym dowodzi Lumes.

### dic\_robot\_UBS\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b014`

> Duży okręt-matka, flagowiec każdego z legionów Wulgaru. Ma tarczę obronną, która bez trudu odbija strzały z dział cząstek naładowanych, i przewozi wiele broni mobilnych. Jak cała broń Wulgaru, ma barwy zależne od oddziału; błękitne malowanie oznacza oddział, którym dowodzi Jiart.

### dic\_robot\_UMS\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b016`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; zielone malowanie oznacza oddział, którym dowodzi Rada.

### dic\_robot\_UMS\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b018`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; fioletowe malowanie oznacza oddział, którym dowodzi Klein.

### dic\_robot\_UMS\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b000`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; żółte malowanie oznacza oddział, którym dowodzi Lutiel.

### dic\_robot\_UMS\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b002`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; czerwone malowanie oznacza oddział, którym dowodzi Dolgana.

### dic\_robot\_UMS\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b004`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; pomarańczowe malowanie oznacza oddział, którym dowodzi Lumes.

### dic\_robot\_UMS\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b006`

> Średni okręt Wulgaru. Dobrze łączy siłę ognia, wytrzymałość i mobilność. Służy też jako okręt-matka dla broni mobilnych zwykłych oddziałów. Jak cała broń Wulgaru, ma barwy zależne od oddziału; błękitne malowanie oznacza oddział, którym dowodzi Jiart.

### dic\_robot\_UBF\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b008`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; zielone malowanie oznacza oddział, którym dowodzi Rada.

### dic\_robot\_UBF\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00a`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; fioletowe malowanie oznacza oddział, którym dowodzi Klein.

### dic\_robot\_UBF\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00c`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; żółte malowanie oznacza oddział, którym dowodzi Lutiel.

### dic\_robot\_UBF\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00e`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; czerwone malowanie oznacza oddział, którym dowodzi Dolgana.

### dic\_robot\_UBF\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b010`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; pomarańczowe malowanie oznacza oddział, którym dowodzi Lumes.

### dic\_robot\_UBF\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b012`

> Myśliwiec dla szeregowych żołnierzy Wulgaru. Istnieją też wersje dla żołnierzy średniej i wyższej rangi: im wyższa ranga pilota, tym bardziej złożony kształt maszyny. Jak cała broń Wulgaru, ma barwy zależne od oddziału; błękitne malowanie oznacza oddział, którym dowodzi Jiart.

### dic\_robot\_JDJGR\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b014`

> Robot zbudowany przez prezesa Otaki Factory, Otakiego. Początkowo był pilotowany, lecz po walkach z kaiju przerobiono go na bezzałogowca z SI. Wgrany wtedy interfejs dialogowy to Yung, instancja Naratake, SI wspomagającej komunikację, stworzonej przez Yuna Arikawę. Walczy włócznią Anguirusa (Lance of Anguirus), wykonaną z rogu zdobytego w walce z kaiju Anguirusem.

### dic\_robot\_JDJGR\_00\_1

Adres: `dic\_text\_robot/014d369b:9c20b015`

> Do ostatecznej walki z Godzillą otrzymał moduł lotny, lecz spadł i przestał działać. Następnie dzięki odkrytemu przez Pelopsa II “protokołowi, który uczyni Jet Jaguara najsilniejszym” połączył się z Pelopsem II i urósł jako Jet Jaguar PP. Po zaciętym boju zniknął razem z Godzillą w nagłym wybuchu.

### dic\_robot\_GZLULTM\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b016`

> Gigantyczny organizm, który wyszedł z morza. Przeszedł już trzy przemiany i wciąż rośnie. Nazwę “Godzilla” nadano mu na podstawie dawnych podań z miasta Nigashio. Wytwarza ogromne ilości Czerwonego Pyłu, silnie wpływając na otoczenie. Całe ciało pokrywa przypominająca zbroję skóra, płetwy grzbietowe są mocno rozwinięte, a po przemianie zaczął chodzić na dwóch nogach. Gdy płetwy grzbietowe rozbłyskują, wytwarza kilka pierścieni i, ściskając je, wystrzeliwuje promień atomowy (Heat Ray), który zamienił Tokio w morze ognia.

### dic\_robot\_GZLULTM\_00\_1

Adres: `dic\_text\_robot/014d369b:9c20b017`

> Uważa się go za Punkt Osobliwy, który poprowadzi świat ku Katastrofie. Po zaciętym boju z Jet Jaguarem zniknął w nagłym wybuchu, pozostawiając niebieskie kryształy.

### dic\_robot\_KMNGA\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b000`

> Kaiju, które pojawiły się w nadmorskiej stoczni. Nazwa nadana przez robotników z uwagi na podobieństwo do ośmionogiego pająka przyjęła się na stałe. Żyją w grupach z innymi osobnikami, a nawet po rozcięciu ciała dalej działają i się regenerują. Atakują ludzi, wypluwając z pyska nici śluzu.

### dic\_robot\_LADON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b002`

> Kaiju, które pojawiły się na całym świecie. Nazwa pochodzi od radioaktywnego radonu wykrytego w komórkach pierwszego osobnika z Nigashio. Zwracano uwagę na podobieństwo do pterozaura Quetzalcoatlus, lecz nie znaleziono u nich narządu pełniącego funkcję żołądka, więc uważa się je za coś zupełnie innego niż dotychczasowe życie na Ziemi. Wiadomo, że porozumiewają się falami radiowymi; odnotowano też, że wychodziły z morza. Osobniki, które zaczęły się pojawiać wraz z rozprzestrzenianiem się Czerwonego Pyłu, mają inną barwę niż ten z Nigashio.

### dic\_robot\_DYNZNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b004`

> Gigantyczny robot powstały z połączenia czterech maszyn: Dyna Soldier, Dyna Wing, Dyna Striker i Dyna Diver. Za pierwszym razem przyzwała go figurka smoka, przedmiot grobowy, który miał przy sobie Gauma; później rozdzielił się na cztery maszyny. Na co dzień mieszczą się one w dłoni, a posiadają je Yomogi, Yume, Koyomi i Gauma. Okrzyk “Access mode!” pozwala im urosnąć. Inny sposób łączenia daje Super Dragon Dynarex. Sygnałem do walki jest okrzyk Gaumy “Dynazenon! Battle, go!”. Poza bronią palną, taką jak działa Penetrator Gun na obu barkach czy Burst Missile, walczy z kaiju wręcz.

### dic\_robot\_GRID\_KT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b006`

> Postać olbrzyma, w którą przemienia się Knight. Walczy zwinnie wręcz i używa wielu rodzajów broni przeciw kaiju. Zna m.in. Gridknight Circular, w którym ciska świetlistym pierścieniem, i cios specjalny Gridknight Storm, promień z prawego ramienia.

### dic\_robot\_GRID\_KT\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b007`

> Po połączeniu w Kaiser Gridknighta tworzy jego tułów.
> 

### dic\_robot\_KZLGRID\_KT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b008`

> Połączenie Gridknighta, Dynazenona i Goldburna. Nadmiar energii tworzy na skrzydłach świetlisty płaszcz. Walczy m.in. Kaiser Knight Circular, tnąc wroga gigantycznym świetlistym pierścieniem, i ciosem specjalnym Rex Grid Fire, promieniem z Dynamic Cannon na prawym barku.

### dic\_robot\_SLBNDS\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00a`

> Kaiju, które potrafi unosić przedmioty. Uwalniając z narządu drgań na grzbiecie cząstki światła zwane Chaosbringer, sprawia, że budynki i samochody unoszą się w powietrze. Wyciąga szyję jak wąż i atakuje mieczowatym pyskiem, a z paszczy miota promienie podobne do błyskawic.

### dic\_robot\_SLBNDS\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00b`

> Pokonany przez Great Conflagration: Rex Roar Dynarexa.

### dic\_robot\_GLJOM\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00c`

> Kaiju zdolne do teleportacji. Urosło dzięki Instance Domination Juugi z Klubu Kaiju. Uwalniając cząstki światła Chaosbringer z narządów drgań na rogu na czole i na skrzydłach, przenosi się w mgnieniu oka na krótkie odległości. Z piersi miota promienie.

### dic\_robot\_GLJOM\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00d`

> Koyomi odkrył, że nie może się teleportować bez rozłożenia skrzydeł; Dyna Soldier Wing Combine unieruchomiło go, a Gauma na Dyna Diverze go dobił.

### dic\_robot\_BLBAIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00e`

> Kaiju zdolne do zgniatania przedmiotów. Kierowali nim Onija i Mujina z Klubu Kaiju. Uwalniając Chaosbringer z narządu drgań, zwiększa grawitację. Miota promienie z przypominających grzywę macek i ze skrzydeł, a także atakuje rogami wirującymi jak świdry.

### dic\_robot\_BLBAIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00f`

> Najpierw zapędziło Dynazenona w kozi róg, lecz wycofało się, gdy pojawił się Gridknight. Potem znów zaatakowało miasto, ale uległo wspólnemu atakowi Dynazenona i Gridknighta.

### dic\_robot\_GBZORG\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b010`

> Kaiju zdolne do falowania materii. Urosło dzięki Instance Domination Juugi z Klubu Kaiju. Uwalniając Chaosbringer z narządu drgań na grzbiecie oraz z dłoni i paszczy, wygina wieże i upłynnia grunt. Z soczewek grawitacyjnych tworzonych w dłoniach i paszczy miota potężne fale uderzeniowe podobne do wiązek.

### dic\_robot\_GBZORG\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b011`

> Pochłonęło podłoże pod Gridknightem i resztą, unieruchamiając ich, lecz Goldburn odwrócił losy walki i kaiju uległo połączonemu Kaiser Gridknightowi.

### dic\_robot\_GGYRA\_1\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b012`

> Kaiju ukryte w ciele Sizumu, powiększone dzięki Instance Domination. Uwalniając Chaosbringer z narządu drgań na grzbiecie, odrzuca cele daleko od siebie.

### dic\_robot\_GGYRA\_2\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b014`

> Postać, w jaką wyewoluowało kaiju ukryte w ciele Sizumu, powiększone dzięki Instance Domination, po wchłonięciu Oniji, Juugi i Mujiny z Klubu Kaiju. Uwalniając Chaosbringer z narządu drgań na grzbiecie, odrzuca cele daleko od siebie. Miota promienie z rogów i potężne wiązki z paszczy i piersi.

### dic\_robot\_GGYRA\_2\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b015`

> Przytłaczającą siłą zapędziło Kaiser Gridknighta w kozi róg, lecz Yomogi rozłączył maszynę i mocą władcy kaiju stworzył lukę, a zmasowany atak Dynazenona i Gridknighta przyniósł mu porażkę.

### dic\_robot\_W\_DYNZNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b016`

> Prototyp Dynazenona przejęty przez mikroskopijne, niewidoczne gołym okiem kaiju. Nie ma mechanizmu rozdzielania ani łączenia w Dynarexa. Klub Kaiju steruje nim przez Instance Domination za pośrednictwem kaiju wypełniających całą maszynę.

### dic\_robot\_MFCARDNT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b018`

> Mobilna forteca-miasto zbudowana pod miastem Yagami w Tokio. W kopule na pokładzie mieści się miasto Yagami wraz z okolicą. Ma mechanizmy jak statek emigracyjny ultradalekiego zasięgu, a dzielnice mieszkalne funkcjonują jak całkowicie samodzielne miasto. Główny silnik, System Nira-Kana-I, wytwarza ogrom energii, daleko przekraczający potrzeby miasta, ale jego działanie to czarna skrzynka i trudno mówić o pełnej kontroli. Ma też różnorodne uzbrojenie, któremu moc Nira-Kana-I zapewnia dużą siłę ognia, lecz jako okręt jest mało mobilny, a jego siła bojowa niewielka. Kopuła chroniąca miasto jest za to wyjątkowo wytrzymała: przy projektowaniu najważniejsze było bezpieczeństwo mieszkańców.

### dic\_robot\_MFCARDNT\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b019`

> Jego głównym zadaniem było panowanie nad Willforce, szczątkową wolą prastarej cywilizacji, Klanu Animus. Z woli właścicielki, Echiki Y. Franburnett, zamienia jednak w energię uczucia ludzi zebranych na A. Advencie.

### dic\_robot\_RNDRAH\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b000`

> Mobilny pancerz ninja przywódcy Tajnych Sił Specjalnych Haze. Elastyczna rama i napęd ze sztucznymi mięśniami dają mu niespotykaną zwrotność. Sterowanie odbywa się w systemie półpodporządkowanym, łączącym ruchy ciała pilota z obsługą różnych manipulatorów, co czyni maszynę niezwykle delikatną. Maszyna i pilot są połączeni nerwowo, więc pilot odczuwa też uszkodzenia; kto nie przeszedł szkolenia NINJA, z trudem zdoła nią choćby chodzić. Szal na plecach to rój nanomaszyn, służący nie tylko do ataku, ale też, zależnie od taktyki, do maskowania i zwodzenia. Lunedrache, maszyna na zamówienie dla przywódcy, ma inny silnik niż seryjny Mond i dysponuje wybuchową mocą. Nazwę “Lunedrache” nosi każda maszyna kolejnych przywódców Haze; maszyna obecnego przywódcy, od jego kryptonimu, nazywa się oficjalnie “X (Cross)-Lunedrache”.

### dic\_robot\_RNDRAH\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b001`

> W wielu jej częściach użyto metalu Willforce, który zamienia energię duchową pilota w siłę. Od początku projektowano ją też do współpracy z A. Adventem: ma system łącza, który korzysta z części energii okrętu.

### dic\_robot\_RNDRAH2\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b002`

> Drugi egzemplarz Lunedrache, mobilnego pancerza ninja przywódcy Tajnych Sił Specjalnych Haze, złożony z części zapasowych. Elastyczna rama i napęd ze sztucznymi mięśniami dają mu niespotykaną zwrotność. Sterowanie odbywa się w systemie półpodporządkowanym, łączącym ruchy ciała pilota z obsługą różnych manipulatorów, co czyni maszynę niezwykle delikatną. Maszyna i pilot są połączeni nerwowo, więc pilot odczuwa też uszkodzenia; kto nie przeszedł szkolenia NINJA, z trudem zdoła nią choćby chodzić. Szal na plecach to rój nanomaszyn, służący nie tylko do ataku, ale też, zależnie od taktyki, do maskowania i zwodzenia. Lunedrache, maszyna na zamówienie dla przywódcy, ma inny silnik niż seryjny Mond i dysponuje wybuchową mocą. Nazwę “Lunedrache” nosi każda maszyna kolejnych przywódców Haze; maszyna obecnego przywódcy, od jego kryptonimu, nazywa się oficjalnie “X (Cross)-Lunedrache”.

### dic\_robot\_RNDRAH2\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b003`

> W wielu jej częściach użyto metalu Willforce, który zamienia energię duchową pilota w siłę. Od początku projektowano ją też do współpracy z A. Adventem: ma system łącza, który korzysta z części energii okrętu.

### dic\_robot\_RNDRAH\_NCT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b004`

> Najnowszy mobilny pancerz ninja oparty na Lunedrache. Zbudował go Tetsuro Yagami, lecz szczegóły jego powstania nie są znane. W odróżnieniu od nastawionego na skradanie się Lunedrache stawia na walkę i ma znacznie większą siłę ataku. Ma dwa razy więcej nanomaszyn, co pozwala na jeszcze bardziej różnorodną taktykę. Pełne ich wykorzystanie wymaga jednak więcej energii, a obciążenie pilota jest nieporównanie większe. To maszyna eksperymentalna, przy której projektowaniu w ogóle nie brano pod uwagę użycia bojowego, więc ma przesadne, a nawet zbędne parametry i wyposażenie.

### dic\_robot\_RNDRAH\_NCT\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b005`

> Uruchomienie łącza energii z A. Adventem pozwala jej osiągnąć zakładane pierwotnie osiągi. Moc wytwarzana przez metal Willforce w całej maszynie pozostaje jednak niewiadomą i, jak pokazała technika Full Moon Crush, kryje potencjał wykraczający poza przewidywania konstruktora.

### dic\_robot\_RNDRAH\_BRM\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b006`

> Najnowszy mobilny pancerz ninja oparty na Lunedrache. Zbudował go Tetsuro Yagami, lecz szczegóły jego powstania nie są znane. W odróżnieniu od nastawionego na skradanie się Lunedrache stawia na walkę i ma znacznie większą siłę ataku. Ma dwa razy więcej nanomaszyn, co pozwala na jeszcze bardziej różnorodną taktykę. Pełne ich wykorzystanie wymaga jednak więcej energii, a obciążenie pilota jest nieporównanie większe. To maszyna eksperymentalna, przy której projektowaniu w ogóle nie brano pod uwagę użycia bojowego, więc ma przesadne, a nawet zbędne parametry i wyposażenie.

### dic\_robot\_RNDRAH\_BRM\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b007`

> Uruchomienie łącza energii z A. Adventem pozwala jej osiągnąć zakładane pierwotnie osiągi. Moc wytwarzana przez metal Willforce w całej maszynie pozostaje jednak niewiadomą i, jak pokazała technika Full Moon Crush, kryje potencjał wykraczający poza przewidywania konstruktora.

### dic\_robot\_RUMINA\_C1\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b008`

> Broń mobilna ukończona po wojnie rewolucyjnej. Stabilna moc, dobre prowadzenie, łatwa obsługa i produkcja sprawiły, że przyjęło ją wiele instytucji i w krótkim czasie upowszechniła się. To malowanie Sił Nowej Federacji Ziemskiej i współpracujących z nimi instytucji; maszyny te służą na całym świecie.

### dic\_robot\_RUMINA\_C1\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b009`

> Uproszczona wersja eksportowa Vi Lumenusa armii Ra Val, bez najważniejszego elementu, napędu Prophoton Effect Drive. Dlatego jej siła bojowa jest o kilka klas niższa od oryginału.

### dic\_robot\_RUMINA\_C2\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b00a`

> Broń mobilna ukończona po wojnie rewolucyjnej. Stabilna moc, dobre prowadzenie, łatwa obsługa i produkcja sprawiły, że przyjęło ją wiele instytucji i w krótkim czasie upowszechniła się. To malowanie maszyn sprzedawanych cywilom, używanych m.in. przez prywatne formacje zbrojne.

### dic\_robot\_RUMINA\_C2\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b00b`

> Uproszczona wersja eksportowa Vi Lumenusa armii Ra Val, bez najważniejszego elementu, napędu Prophoton Effect Drive. Dlatego jej siła bojowa jest o kilka klas niższa od oryginału.

### dic\_robot\_RUMINA\_C3\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b000`

> Broń mobilna ukończona po wojnie rewolucyjnej. Stabilna moc, dobre prowadzenie, łatwa obsługa i produkcja sprawiły, że przyjęło ją wiele instytucji i w krótkim czasie upowszechniła się. To malowanie sił zbrojnych kolonii kosmicznych i współpracujących z nimi instytucji; maszyny te służą głównie w przestrzeni kosmicznej.

### dic\_robot\_RUMINA\_C3\_00\_1

Adres: `dic\_text\_robot/014d369b:9ce0b001`

> Uproszczona wersja eksportowa Vi Lumenusa armii Ra Val, bez najważniejszego elementu, napędu Prophoton Effect Drive. Dlatego jej siła bojowa jest o kilka klas niższa od oryginału.

### dic\_robot\_VAY\_RUMINA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b002`

> Broń mobilna Wszechgwiezdnego Imperium Ra Val. Moc głównego napędu, Prophoton Effect Drive, zapewnia jej dużą siłę ognia i mobilność. Seria Lumenus miała pierwotnie wiele odmian do różnych zadań, lecz ze względu na łatwość produkcji i wszechstronność obecnie produkuje się seryjnie tylko typ Vi.

### dic\_robot\_STERA\_VRS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b004`

> Wersja na zamówienie Stelli, maszyny gwardii przybocznej Niebiańskiego Cesarza (Niebiańskich Rycerzy) Wszechgwiezdnego Imperium Ra Val. Pilotuje ją Niebiański Rycerz Re Seivas. Dostrojona pod maksymalną prędkość, uchodzi za najszybszą maszynę Ra Val. Trzy napędy Prophoton Effect Drive dają jej ogromną siłę bojową, ale jest trudna w obsłudze i wymaga wielkich umiejętności.

### dic\_robot\_STERA\_BLS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b006`

> Wersja na zamówienie Stelli, maszyny gwardii przybocznej Niebiańskiego Cesarza (Niebiańskich Rycerzy) Wszechgwiezdnego Imperium Ra Val. Pilotuje ją Niebiański Rycerz Re Sistis. Wzmocniony w wielu miejscach pancerz zapewnia jej wysoką wytrzymałość. Jako maszyna dowódcy batalionu ma też znacznie rozbudowane systemy łączności i rozpoznania.

### dic\_robot\_STERA\_FLS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b008`

> Replika Stelli, maszyny gwardii przybocznej Niebiańskiego Cesarza (Niebiańskich Rycerzy) Wszechgwiezdnego Imperium Ra Val. Stelle przysługiwały pierwotnie tylko Niebiańskim Rycerzom, lecz gdy imperium rozbiło się na Ziemi, dla wzmocnienia sił zaczęli ich używać także niebiańscy wojownicy. Oparta na Stella Blus, ma ograniczoną moc maksymalną, ale za to dobrze się prowadzi.

### dic\_robot\_STERA\_KKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00a`

> Stella Force skopiowana przez Willforce. Różni się nie tylko barwą: zasilana Willforce, ma też znacznie większą siłę bojową. Ra Valianie, dumni ze swoich Stelli, nienawidzą tych kopii.

### dic\_robot\_ENDNOS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00c`

> Maszyna Niebiańskiego Cesarza Wszechgwiezdnego Imperium Ra Val. Niebiański Cesarz Ra Valbelm kazał ją zbudować na własny użytek; uchodzi za najsilniejszą maszynę Ra Val. Valbelm walczy nią, odkąd zasiadł na tronie; jako symbol zwycięstw Ra Val oficjalnie nie poniosła ani jednej porażki. Siedem napędów Prophoton Effect Drive zapewnia jej ogromną siłę bojową w każdej sytuacji. Krąży legenda, że jej ogromnym toporem bojowym, Celestial Wrath Qeraunos, przecięła jednym ciosem na pół okręt flagowy wrogiego państwa międzygwiezdnego.

### dic\_robot\_GGENDNOS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00e`

> Ostateczna broń Wszechgwiezdnego Imperium Ra Val. Jej rdzeniem jest Endenos, a sama służy jako ośrodek sterowania bezzałogowymi oddziałami Stella Force. Liczne napędy Prophoton Effect Drive i Willforce jako źródło energii dają jej niespotykaną siłę bojową nawet jako pojedynczej broni mobilnej. Nawet ze wsparciem urządzenia panowanie nad Willforce wymaga ogromnej siły ducha, dlatego pilot, Valbelm, stale działa na granicy wytrzymałości. Gdyby jego równowaga psychiczna się załamała, groziłoby to utratą kontroli i potężnym wybuchem, lecz moc, jaką daje, jest warta tego ryzyka i stanowi oś planu podboju galaktyki Valbelma.

### dic\_robot\_IZNORT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b010`

> Broń mobilna stworzona przez Willforce, wolę Evolverów. Jej rdzeniem jest nadczłowiek Izana, a jako nowe naczynie Willforce, który utracił ciało, stanowi oś ich planu podboju galaktyki. Służy jako ośrodek sterowania maszynami podległymi Willforce, takimi jak Stella Kokuen czy Animus Beast Midollo, a do tego sama przewyższa siłą bojową bestię Midollo. Granice jej możliwości są nieznane, ale uważa się, że połączenie mocy Willforce i nadczłowieka mogłoby zniszczyć nawet planetę.

### dic\_robot\_GRVLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b000`

> Maszyna Caruleuma, dowódcy oddziału wykonawczego Quaestorów. Zaprojektowana do samodzielnego niszczenia wielu wrogów, ma przytłaczającą siłę ognia, wyraźnie przewyższając seryjną broń mobilną z serii Orcusula. Poza ogromną siłą bojową pełni też funkcję ośrodka dowodzenia: teoretycznie może sterować naraz 65 535 maszynami z serii Orcusula. Otrzymał ją jako dowód, że jest “nowym królem Ziemi”, więc stanowi ona niemal część tożsamości Caruleuma. To najwyższy model serii Valin, maszyn przyznawanych przyszłym królom planet podbitych przez Quaestorów, o wyjątkowo dużej sile ognia. Wynika to z niebezpieczeństwa, jakie stwarza podbijana cywilizacja ziemska: w najgorszym razie siły Quaestorów z Gravalinem na czele miały zniszczyć ją doszczętnie.

### dic\_robot\_ARKDIA\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b002`

> Broń mobilna, którą Nevanlinna zbudowała jako własne ciało. Łączy technologię supercywilizacji Gardim z technikami z różnych światów zebranymi przez Slave 2044, czyli Nine. Strumienie energii widoczne na ramionach, biodrach i udach stanowią ramę, którą okrywa pancerz; nadmiar energii tworzy unoszące się za plecami płytowe kryształy energetyczne. Jej doktryna bojowa, w odróżnieniu od dawnej doktryny Gardim, opartej na walce flot, stawia na połączenie wysokiej mobilności i siły ognia. To w jednej maszynie zamknięta ziemska taktyka, w której sprzeczne cechy, szybkość i siłę ognia, łączy się przez współdziałanie broni mobilnych i okrętów; można ją uznać za ostateczną formę serii Vang stworzonej przez Nine.

### dic\_robot\_ENDE\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b004`

> Ciało bestii Ende, istoty z wyższego wymiaru. Zbudowane z czystego Od, zamienia wolę Ende w dogmę. Drzewo wyrastające z jego grzbietu łączy się ze świętym miejscem Strażników Porządku, Prawdziwym Drzewem Świata, i zbiera uczucia ludzi zawarte w Owocach Mądrości rosnących w Al-Warth. Prawdziwe ciało Ende znajduje się z przodu głowy; ogromna paszcza poniżej i kończyny należą do innej istoty z wyższego wymiaru, którą Ende niegdyś przejął.

### dic\_robot\_DIGIA\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b006`

> Ostateczna broń, oś Planu Zjednoczenia Galaktyki prowadzonego przez Dymę Goldwina. Służy też jako jednostka sterująca mobilnej fortecy VTX: z kokpitu DyGaiana można kontrolować wszystkie jej funkcje. Do jego budowy hojnie użyto nauki łączącej cywilizację ziemską, w tym spuściznę Złotej Ery, prehistoryczną cywilizację Układu Słonecznego i cywilizacje obcych przywiezione przez Rami i UND, a także ogromnych funduszy VTX Union S.A. Konstrukcja nawiązuje do super robota Gaian, którym Dyma walczył w latach 180. Nowej Ery Uniwersalnej. Wraz z umiejętnościami Dymy jego siła bojowa dorównuje całej Flocie Zero UND. W gotowej maszynie z tego zrezygnowano, lecz na etapie projektu miał mechanizm samodzielnej przemiany w okręt kosmiczny; jego ślady widać w wielu miejscach.

### dic\_robot\_FTBNFROBO\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b008`

> Broń prastarej cywilizacji Klanu Animus, która rozkwitała 12 000 lat temu. Zasilają ją negatywne uczucia ludzkie, takie jak gniew, nienawiść i uraza, czerpane od istot pozbawionych ciała (czyli tak zwanych złych duchów i upiorów). Nie ma inteligencji ani rozumu, lecz pod wpływem wchłoniętych negatywnych uczuć działa jako wcielenie nienawiści i zniszczenia.

### dic\_robot\_CYBSTER\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00a`

> Maszyna zbudowana w Świętym Królestwie Langran w podziemnym świecie La Gias. Pobłogosławiona przez Cyphis, ducha wiatru, nosi miano “Elemental Lorda Wiatru”. Głównym źródłem mocy jest perpetuum mobile typu Fulcanelli, które dla zwiększenia wydajności potrzebuje prany heralda (pilota). Prana to w zasadzie to samo co “ki” czy “aura”; dostarcza jej herald, więc moc maszyny w dużej mierze zależy od jego predyspozycji. Maszyna jest szczelna i może działać pod wodą i w kosmosie, a wewnętrzny system obiegu podtrzymuje funkcje życiowe heralda, umożliwiając długotrwałe działanie. Do napędu wykorzystuje jako magiczny nośnik eter (energię bez masy, spoczywającą względem współrzędnych absolutnych). Pancerz z orichalconium zawiera na poziomie cząstek metalu wzory geometryczne oparte na numerologii o działaniu talizmanów, więc dobrze chroni też przed magią. Komputer główny typu demon Laplace'a oblicza przyczynowość i przewiduje różne zdarzenia, choć jego skuteczność silnie zależy od mocy magicznej heralda. Nazwa “Cybaster” nie jest prawdziwym imieniem maszyny, lecz imieniem ochronnym, które chroni ją przed atakami magicznymi.

### dic\_robot\_VANX\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00c`

> Następca VangRaya, broni mobilnej zbudowanej przez Nine jako model próbny. W odróżnieniu od VangRaya, złożonego z przypadkowych materiałów, Nine zaprojektowała go od podstaw, korzystając z technologii poznanych w różnych światach. Choć nie było to zamierzone, wykorzystano w nim też technologię Gardim, którą zna Nine, więc łączy technologie trzech światów i Gardim. Rozwija koncepcję VangRaya: taktykę i uzbrojenie przejął od poprzednika lub je ulepszył. Wszystkie części wykonano od nowa, zamiast składać je z tego, co było pod ręką, dzięki czemu usunięto wiele problemów VangRaya. Tuż po ukończeniu nie osiągał zakładanej mocy i miał wiele usterek, lecz gdy przechwyciły go Gardim, przebudowano go z użyciem ich materiałów i dopiero wtedy stał się w pełni gotowy. Układ sterowania działa na jeszcze cieńszej granicy równowagi niż w VangRayu, dlatego Nine musi być na pokładzie i, wyczuwając stan maszyny, wspierać sterowanie. Zarazem świadomość, że “walczy u boku kogoś bliskiego”, poprawiła działanie Nine, dzięki czemu VangNex pokazał moc daleko przewyższającą założenia projektowe.

### dic\_robot\_GRNVNG\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00e`

> Następca VangRaya, broni mobilnej zbudowanej przez Nine jako model próbny. W odróżnieniu od VangRaya, złożonego z przypadkowych materiałów, Nine zaprojektowała go od podstaw, korzystając z technologii poznanych w różnych światach. Z upodobania Nine ma wiele cech “super robota”, a jego maska wzoruje się na jej “ideale mężczyzny”. Choć nie było to zamierzone, wykorzystano w nim też technologię Gardim, którą zna Nine, więc łączy technologie trzech światów i Gardim. Z dwóch założeń VangRaya, wysokiej mobilności i siły ognia, stawia na siłę ognia; by zwiększyć moc, jest znacznie większy od VangRaya. Aby wytrzymał taką moc, znacznie wzmocniono sztywność konstrukcji, więc ma cięższy pancerz niż VangRay. Tuż po ukończeniu nie osiągał zakładanej mocy i miał wiele usterek, lecz gdy przechwyciły go Gardim, przebudowano go z użyciem ich materiałów i dopiero wtedy stał się w pełni gotowy. Układ sterowania działa na jeszcze cieńszej granicy równowagi niż w VangRayu, dlatego Nine musi być na pokładzie i, wyczuwając stan maszyny, wspierać sterowanie. Zarazem świadomość, że “walczy u boku kogoś bliskiego”, poprawiła działanie Nine, dzięki czemu GranVang pokazał moc daleko przewyższającą założenia projektowe.

### dic\_robot\_XELGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b000`

> Autowarlock zbudowany przez Strażników Porządku. Leżał porzucony w kącie magazynu zakonu i szacuje się, że ma co najmniej 100 lat, co oznacza, że przez ponad 100 lat nie pojawił się nikt godny tej maszyny, przeznaczonej dla Założyciela. Na przedramionach ma mechaniczne kręgi magiczne, które pozwalają szybko używać dogmy, ale silniejsza dogma wymaga kręgu magicznego w przestrzeni. W porównaniu z Deenbellem, standardową maszyną zakonu, jest trudny w obsłudze, a wiele jego elementów jest mniej wydajnych niż w obecnych maszynach. Wzmocnienie mocy magicznej jest niestabilne, a siła bojowa zależy bezpośrednio od kondycji i mocy czarodzieja. Wynika to z innej koncepcji niż w Deenbellu. Wzmocnienie w Autowarlocku polega na siłowym wydobywaniu mocy czarodzieja, a przesada może zniszczyć jego umysł. Dlatego Deenbell wzmacnia słabą moc i ma ogranicznik górnej granicy, a Xelguard nie ma żadnych ograniczeń i przy słabej mocy jego mechanizm wzmocnienia w ogóle nie działa. W zamian, zależnie od mocy pilota, Xelguard może osiągnąć niemal nieograniczoną siłę, a zarazem uświadamia czarodziejowi jego własną moc i pomaga ją rozwijać. Gdy uwalnia prawdziwą moc, otwierają się jego części i rozkładają złożone skrzydła. To przyszłe “ciało” (naczynie) bestii Ende przy jej odrodzeniu; przypuszcza się, że po połączeniu z życiem i umysłem Ende znacznie zmieni wygląd.

### dic\_robot\_TRNED\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b002`

> Przedprodukcyjna wersja prototypu zbudowanego w ramach projektu TND (Terrestrial Next Dream) VTX Union S.A. Nazwa pochodzi od “TND” i najpotężniejszego drapieżnego dinozaura, tyranozaura. Wyróżnia się mocą przewyższającą dotychczasową broń mobilną i wynikającym z niej ogromnym ciągiem; świetnie walczy w powietrzu. Przy maksymalnej prędkości słabo jednak skręca, więc wymaga dużych umiejętności pilota. Przeznaczony do współpracy z Carriaxem, zintegrowaną maszyną wsparcia taktycznego, który dostarcza mu zbyt dużą do noszenia broń. Przed konkursem na następną maszynę seryjną nowa Sekcja Specjalna 3 przeprowadzała jego testy bojowe i zbierała dane. Wysoką moc zawdzięcza silnikowi Quark Drive opracowanemu na planecie Darbnes; w wielu częściach widać połączenie technologii obcych i ziemskiej. Po przyjęciu do służby oddział miał się składać z pięciu Tyranado i jednego Carriaxa; taktyka współpracy obu maszyn w Sekcji Specjalnej 3 była zupełnie nieprzewidziana.

### dic\_robot\_TRNEDREX\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b004`

> Wzmocnione rozwinięcie prototypu Tyranado. Nazwa pochodzi od “przebudowy o nieznanym potencjale Re:X” i tyranozaura (Tyrannosaurus rex). Zachowano podstawową ramę Tyranado, lecz wymieniono części na nowe, uwzględniające dane zebrane przez Sekcję Specjalną 3; mimo krótkiego czasu przebudowy wygląd zmienił się mocno, a osiągi znacznie wzrosły. Koncepcja stała się przeciwieństwem maszyny seryjnej, z której każdy wyciśnie pełnię możliwości; to efekt dociekliwości (zdaniem niektórych: wybryku) działu technicznego, zainteresowanego tym, ile potencjału pilota da się wydobyć. Taktyka współpracy z Carriaxem pozostała jak w Tyranado, ale postępy w analizie Quark Drive znacznie poprawiły sprawność, pozwalając używać broni z większą mocą i zwiększając siłę ognia. Z czasem projekt TND otrzymał nowy cel: “stworzenie flagowej maszyny VTX Union S.A.”, a jego owoc był na bieżąco ulepszany. Postępy w ulepszaniu Quark Drive, dzieła obcej cywilizacji, niezwykła mobilność i siła ognia oraz taktyka współpracy z Carriaxem sprawiły, że ostatecznie stał się maszyną godną miana flagowej.

### dic\_robot\_BIGO\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f4e0b000`

> Czarny Megadeus, którym walczy Roger Smith. Pojawia się spod ziemi, gdy Roger krzyknie do zegarka na lewym nadgarstku “Big O! Showtime!”, i staje z nim do walki. Gdy Roger wsiada, na monitorze wyświetla się napis “CAST IN THE NAME OF GOD YE NOT GUILTY” (“Odlewam to w imię Boga. Nie jesteście winni”). Na co dzień spoczywa pod rezydencją Rogera, a wezwany pędzi do celu nieużywanymi tunelami podziemnej kolei na transporterze Prairie Dog. Ma wbudowaną broń, taką jak promienie z oczu Arc Line oraz Cannon Party i Missile Party z piersi i brzucha, ale jego najpotężniejszym ciosem jest Sudden Impact, niszczycielskie uderzenie wbijanym palem Strike Pile z ramienia. Pozostaje zagadką: kiedy, gdzie, przez kogo i po co go zbudowano, nie wie nawet jego pilot, Roger.

### dic\_robot\_BBDX\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b001`

> Megadeus należący do Becka, zwany też “Super Beck”. Zbudowali go podwładni Becka, T-Bone i Dove, z części ciężkich maszyn przemysłowych skradzionych z Wise Company. Uzbrojony jest w rakiety ukryte w piersi i wiązki strzelające z palców. Wiązki przecinają łańcuch Mobydick Anchor, ale odbiły się od kryształu na głowie Big O. Szybko ucieka, a górna połowa jego ciała obraca się o 180 stopni; wykorzystał to raz do ataku z zaskoczenia na Big O.

### dic\_robot\_BIGD\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b003`

> Megadeus odnaleziony przez Schwarza. Jeśli Big O to The Big lądu, Big Duo jest The Big przestworzy. Rozkłada skrzydła z obu ramion, zmienia cztery palce w śmigła i lata dzięki potężnemu silnikowi. Uzbrojenie to promienie z oczu Arc Line, Gatling Missile z piersi i Megaton Missile ukryte w podudziach. Potrafi ruszyć sam, bez Dominusa (pilota) na pokładzie, i kryje wiele zagadek.

### dic\_robot\_BRIGER\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b005`

> Ostatnia forma przemiany ślizgowej, w którą Brai-Star przekształca się dzięki Brai-synchron-maximum; najsilniejsza z trzech form: Brai-Thunder, Brai-Star i Braiger. Jak w pozostałych formach steruje Bowie, a Kid przenosi się do Blaster Pit w głowie i przejmuje całość ataku. Ma potężną broń, m.in. plazmowe działo niszczące Brai-Shot Special (na co dzień używane przez J9 jako przyczepa motocyklowa) i Brai-Sword, a Brai-Cannon, dostarczany przez Brai-Carrier pilotowany przez Poncho, daje mu ogromną siłę ognia. Zbudował go twórca teorii synchronu, genialny naukowiec doktor Edmond, o którym mówiono, że jego talent przyspieszy rozwój świata o sto lat.

### dic\_robot\_KRDWCJ\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b007`

> Postać, w którą Shotaro Hidari i Philip przemieniają się za pomocą W Drivera oraz Cyclone Memory i Joker Memory. Od użytych Memory nosi nazwę “Cyclone Joker”; wyróżnia się szybkością i walką wręcz. Wyprowadza szybkie ciosy, a pochłaniając wiatr, odzyskuje siły. Zamiana Memory po lewej i prawej stronie Drivera pozwala przemienić się w inną formę, o innych cechach i barwach. Przy przemianie świadomość jednego z nich wnika w ciało drugiego, które stanowi bazę. W formie Cyclone Joker świadomość Philipa łączy się z ciałem Shotaro.

### dic\_robot\_KRDWCAXEL\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b009`

> Postać, w którą Ryu Terui przemienia się za pomocą Accel Drivera i Accel Memory. Zapisane w Accel Memory wspomnienie przyspieszenia, wydobywane przez Accel Driver, daje mu ogromne przyspieszenie i wysoką sprawność fizyczną.

### dic\_robot\_KRDWSCULL\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00b`

> Postać, w którą Sokichi Narumi przemienia się za pomocą Lost Drivera i Skull Memory. Moc Memory zawierającej wspomnienie “szkieletu” wzmacnia ciało, a po przemianie czyni go nieśmiertelnym. Jego ciało jest zimne, jak u zmarłego.

### dic\_robot\_RDDOPNT\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00d`

> Dopant powstały z przemiany przy użyciu Road Memory. Szybkością i ciepłem otwiera drogę do innego wymiaru, Shadow Fuuto. W Shadow Fuuto jest wiele takich osobników; odpowiadają za tworzenie i rozbudowę miasta.

### dic\_robot\_DLCBST\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00f`

> Ogromny golem przyzwany przez Alfcourta z innego świata. Zasila go para złej woli wytwarzana przez ludzi. Ma coś w rodzaju silnika parowego: para złej woli pochłaniana z otoczenia porusza tłoki, zwielokrotniając moc maszyny. Uzbrojony jest w zębatą piłę łańcuchową mocowaną do odczepianego ramienia oraz samobieżne koła zębate ukryte w ramionach. Jest bardzo ciężki, więc porusza się powoli.

### dic\_robot\_RNGLM\_00\_0

Adres: `dic\_text\_robot-DLC1/00202c8e:5560b000`

> Kamienna lalka używana przez Strażników Porządku. Korpus powstaje przez wtłoczenie dogmy w bazalt zawierający Od; po dodaniu mechanicznego systemu sterowania i mocy magicznej jest gotowa. W środku ma sztuczną formę życia zwaną Voluntas, która zastępuje mózg sterujący, więc nawet bez czarodzieja wydającego rozkazy może do pewnego stopnia działać samodzielnie. Do użycia broni zużywa zgromadzoną w sobie moc magiczną, ale gdy w pobliżu nie ma czarodzieja, który stale ją uzupełnia, jej siła bojowa drastycznie spada.

### dic\_robot\_DENBEL\_00\_0

Adres: `dic\_text\_robot-DLC1/00202c8e:5620b001`

> Autowarlock zbudowany przez Strażników Porządku. Słynie z niezawodności i stabilnego wzmocnienia mocy magicznej, godnych miana dopracowanego Autowarlocka; od około 30 lat służy na pierwszej linii jako standardowa maszyna zakonu. Jego wysoka siła bojowa jest symbolem potęgi Strażników Porządku, stróżów prawa i porządku; choć rzadko się go widuje, mieszkańcy Al-Warth darzą go nabożnym szacunkiem. Na polu walki jeden Deenbell steruje kilkoma Rune Golemami, a on i jego czarodziej pełnią rolę dowódcy drużyny. Zaprojektowano go jednak z myślą o łatwości obsługi, więc czarodziej o wielkiej mocy może nie wykorzystać w nim w pełni swoich możliwości.

### dic\_robot\_ISTLJEEG\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:5220b000`

> Magne Robot zbudowany przez doktora Shibę do walki z Królestwem Jamatai. Powstaje, gdy do głowy Jeega, w którą przemienia się Hiroshi Shiba, dołączają części Jeega wystrzelone z Big Shootera. Zasilany energią prądu magnetycznego, ma moc 750 000 koni mechanicznych. Poza technikami walki wręcz, takimi jak Dynamite Kick czy Jeeg Breaker, ma broń taką jak Knuckle Bomber i Spin Storm, ale jego największym atutem jest Magnet Power, która pozwala mu wymieniać części w trakcie walki. Oprócz Mach Drill i Jeeg Bazooka w drugiej połowie historii zaczął dobierać do sytuacji kolejne części, takie jak Jeeg Buckler, Sky Parts, Earth Parts i Marine Parts.

### dic\_robot\_ISTLJEEG\_H\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b001`

> Głowa Jeega, w którą przemienia się cyborg Hiroshi. W tej postaci jedyne ataki to Jeeg Beam i taranowanie; bez Big Shootera Kotetsu Jeeg jest dosłownie pozbawiony rąk i nóg. Potrafi za to samodzielnie latać.

### dic\_robot\_GTENOIR1\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b003`

> Pierwsza maszyna serii Getter Robo Noir, zbudowanej w innej czasoprzestrzeni. Maszyna Ryomy; poza bronią podobną jak w Getterze 1 ma dwa pistolety, Getter Dragoon 7000, więc dobrze walczy wręcz i na dystans.

### dic\_robot\_GTENOIRG\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b005`

> Połączenie Gettera Noir 1, 2 i 3, przemienionych w Get Machine. Głównym pilotem jest Ryoma, a wspierają go Hayato i Musashi. Przejmuje charakterystyczną broń każdego Gettera Noir i ma przytłaczającą siłę ataku.

### dic\_robot\_DGANX\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b007`

> Gigantyczny robot powstały z połączenia Da-Garna, Wojownika zrodzonego przez Ziemię, z maszynami wsparcia Earth Fighter i Earth Liner. Earth Fighter tworzy górną połowę ciała, a Earth Liner dolną, zamykając Da-Garna między sobą. Jego najpotężniejszym ciosem jest Breast Earth Buster, wystrzeliwujący energię z części na piersi w kształcie Ziemi.

### dic\_robot\_DGANGX\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b009`

> Postać Da-Garna X po Legend Combination z Ga-Ornem. Części Ga-Orna dołączają się do różnych miejsc Da-Garna X jako dodatkowe elementy. Najpotężniejszą bronią jest GX Buster, powstający z połączenia G-Cannon i G-Vulcan; po przestawieniu może też działać jako GX Buster Vulcan.

### dic\_robot\_REDGIST\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00b`

> Maszyna bojowa, którą pilotuje Redlone. Może przechodzić z formy humanoidalnej w formę smoka. Walczy karabinem i ukrytym w nim mieczem.

### dic\_robot\_VOLFG140\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00d`

> Robot bojowy armii Redlone'a. Pojawił się w towarzystwie oddziału robotów zwiadowczych Riken Alpha. Potężnym cielskiem przytłoczył Da-Garna, lecz połączony Da-Garn X przeciął go jednym cięciem na pół.

### dic\_robot\_IGZIS\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00f`

> Robot stworzony przez cywilizację inną niż obecna ziemska. Wysoka energia z reaktora działającego niemal jak perpetuum mobile daje mu przytłaczającą siłę bojową i wytrzymałość w długiej walce. Szczegóły technologii są nieznane, ale ma własną wolę i coś, co można nazwać sercem, i działa według własnego osądu. Z charakteru jest prostolinijny, w dobrym tego słowa znaczeniu, i uparty, w złym; wszystko podporządkowuje swojej misji, czyli wymierzaniu sprawiedliwości. Bardzo przywiązuje się też do własnej tożsamości i ceni imię “Exis”, które nadała mu Echika.

### dic\_robot\_IBIT\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b011`

> Zintegrowana taktyczna broń mobilna UND. Ma zarówno Ray Cleaver E-Bita Alpha, jak i Ray Focus E-Bita Beta. W UND role poszczególnych maszyn są ściśle rozdzielone według taktyki, więc ta maszyna jest wyjątkiem, a ze względu na wysoki koszt używa się jej rzadko. Taktyka Ziemian wymagała jednak walki w każdych warunkach, więc rzucono ją na front. Konieczność wybierania między dwoma rodzajami broni o odmiennych cechach mocno obciąża pilota i uznawano to za problem, tymczasem Ziemianie radzą sobie z tym bez trudu, co dobitnie pokazało, jak bardzo są inni.

### dic\_robot\_IFAS\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b013`

> Najnowsza zintegrowana taktyczna broń mobilna UND. Długo istniała tylko w planach, a budowę odkładano, lecz by sprostać ziemskiej taktyce opartej na broni mobilnej, przyspieszono jej ukończenie. Uzbrojenie na każde warunki mocno obciąża pilota, ale jej siła bojowa przewyższa obecną serię E-Bit.

### dic\_robot\_IDEON\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4d20b000`

> Spuścizna Szóstej Cywilizacji, odkryta na pierwszym stanowisku wykopaliskowym na planecie Solo. Nazwę “Ideon” nadano mu od jedynego czytelnego w zapisach wzoru, przypominającego greckie litery. Powstaje z połączenia trzech pojazdów: A-Mecha, B-Mecha i C-Mecha; każdy z nich może się też przekształcać i walczyć. A-Mecha to Sol Amber/Ideo Delta, B-Mecha to Sol Vainer/Ideo Nova, a C-Mecha to Sol Conver/Ideo Buster. Główną bronią są zamontowane przez Ziemian Glenn Cannon i 549 wyrzutni rakiet. W trakcie walk mógł też użyć swojej prawdziwej broni: Ideon Sword, zdolnego przeciąć planetę na pół, i Ideon Gun, który zależnie od mocy razi wrogów nawet w podprzestrzeni i może zniszczyć planetę; jak nimi sterować, nie wiadomo. Przypuszcza się, że ma związek z legendą przekazywaną na planecie Buff Clanu, o “Bohaterze Ide” (zwanym też m.in. “Olbrzymem Ide”). Jeśli wierzyć legendzie, ma nieskończoną moc.

### dic\_robot\_JIGMACK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b001`

> Ciężki mech Buff Clanu, opracowany po Giran Dou do walki w podprzestrzeni i Dogg Macku do walk lokalnych. Jego szpony mają siłę zdolną zgnieść pancerz Ideona, a zarazem są tak precyzyjne, że mogą chwycić człowieka. Zwykle w ciężkich mechach kokpit pełni rolę kapsuły ratunkowej, lecz Zigg Mack po odrzuceniu nóg zamienia w kapsułę cały korpus. Nawet po powstaniu nowszych maszyn produkowano go masowo i dzięki stabilnym osiągom pozostał podstawową siłą bojową.

### dic\_robot\_HNGD\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b003`

> Mobile suit dla Newtype'ów zbudowany przez Anaheim Electronics. Ma ogromną siłę ataku dzięki m.in. potężnemu Hyper Mega Bazooka Launcherowi, który jednym strzałem niszczy okręt, i Fin Funnelom ładowanym w zasobniku na plecach.

### dic\_robot\_NCNGL\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b005`

> Mobile suit dla Newtype'ów sił Neo Zeonu. W barkach ma dziesięć zmniejszonych i odchudzonych Funneli typu Alpha Azieru, a w osłonach bioder ukryte ramiona.

### dic\_robot\_INBEL\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b007`

> Jedna z iDOL, humanoidalnych maszyn do usuwania meteorytów, zwana Prometheus 1. iDOL oznacza “immortal defender of legatee” (nieśmiertelny obrońca spadkobiercy); prawdziwym ciałem jest struktura krzemowa o niemal nieskończonej energii, a iDOL to oparty na niej humanoidalny interfejs. Po odrzuceniu poprzedniego mistrza Imber przez 16 lat nie działał, lecz uruchomił się ponownie, gdy jego mistrzynią została Haruka Amami. Służył w Mondenkind, organizacji odbudowującej świat po katastrofie zwanej Lost Artemis, spowodowanej rozpadem Księżyca, i walczył z wrogą organizacją Turiavita, aż został przez nią przechwycony i otrzymał ulepszenie Faustschlag. Różowy pancerz piersi dobrano pod gust jego mistrzyni, Haruki. Ma coś, co można nazwać sercem, i darzy Harukę uczuciem. Aby chronić Ziemię przed AULYN, bramą do innego wszechświata, wziął udział w misji przeniknięcia przez nią razem z Haruką i innymi iDOL.

### dic\_robot\_TUBRNCMPT\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b001`

> Jedno z Cybody, humanoidalnych robotów pozostawionych przez pradawną cywilizację galaktyczną. To postać Tauburn Ordinary, uszkodzonego w walce z Kingiem Samekhem, który odrodził się dzięki libido Takuta. Cybody mogły działać tylko w czasie zerowym, odciętym od zwykłej osi czasu, lecz w walce z królem Cybody, Kingiem Samekhem, zostały z niego uwolnione. Gdy Cybody ruszyły na rzeczywisty świat, Tauburn stawił im czoła razem z Takutem.

### dic\_robot\_VRKS\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b003`

> Stary Para-Mail przechowywany w hangarze Arzenalu. Wyróżnia go biało-niebieskie malowanie i figura bogini na głowie. Poza standardowym uzbrojeniem Para-Maili Arzenalu, przeciwsmoczym karabinem szturmowym i Freezing Bullets, ma własną broń, Type Zero Super Density Blade “Raziel”, który głęboko tnie nawet twardą skórę i łuski Smoków. Mimo wieku przewyższał osiągami inne Para-Maile, lecz z powodu problemów z mocą i sterowaniem nie znalazł pilota i leżał porzucony. Gdy Ange w walce ze Smokiem stanęła w obliczu śmierci, jej krew zareagowała z pierścieniem rodu królewskiego Ikaruga: zniszczona przez czas i walkę maszyna natychmiast się naprawiła i przebudziła. Odtąd jest maszyną Ange i trzonem Pierwszego Szwadronu Para-Maili. Kryje wiele tajemnic, o których w Arzenalu wie tylko kilka osób, m.in. Jill.

### dic\_robot\_VRKS\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b004`

> Reagując na pierścień Ange, w trakcie walk stopniowo uwalnia swoją moc i, zależnie od sytuacji, pokazuje tryby o różnych cechach. W trybie Ariel, umożliwiającym skok międzywymiarowy szybszy od światła, staje się niebieski, a w trybie Michael, w którym pochłania energię fazy przestrzennej i wytwarza z Raziela gigantyczne ostrze energii, czerwony. W trybie Uriel, w którym “Wieczna Opowieść” śpiewana przez Ange zdejmuje ograniczniki, lśni złotem i strzela z wbudowanej w barki broni wymiarowej Discord Phaser. W rzeczywistości to Bilkis, jeden z Ragna-Maili, absolutnej broni zbudowanej podczas Wojny Ostatecznej, odebrany Embryo przez Pradawny Lud dla Libertas. Na znak pragnienia wyzwolenia się spod Embryo i zerwania z nim zmieniono mu nazwę na “Villkiss”. Ange uwolniła jego prawdziwą moc: w ostatecznej bitwie przybrał postać łączącą cechy trybów Ariel, Michael i Uriel i pokonał Hysterikę Embryo.

### dic\_robot\_HSTLK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b005`

> Pierwszy zbudowany Ragna-Mail, osobista maszyna Embryo, który nazywa siebie Stroicielem. Podstawową konstrukcję ma wspólną z innymi Ragna-Mailami, ale ma też własne rozwiązania, np. odsłonięte podwójne oczy w głowie czy kilka par skrzydeł. Na przedramionach ma szable wiązkowe do walki wręcz, a w barkach i nasadach skrzydeł wbudowane Discord Phaser.

### dic\_robot\_HSTLK\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b006`

> W rzeczywistości była załogową maszyną do obserwacji wymiarów, a dzięki skokowi międzywymiarowemu połączona z umysłem Embryo stała się jego drugim ciałem. W ostatecznej bitwie zniszczył ją Villkiss, którego prawdziwą moc uwolniła Ange, a gdy Tusk pokonał Embryo w jego fizycznym ciele, ten zniknął całkowicie.

### dic\_robot\_PLOID\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b007`

> Bezzałogowa broń, którą Julio rzucił do ataku na Arzenal. Ma kształt dysku; wysuwa wbudowane piły łańcuchowe i, wirując z dużą prędkością, taranuje cele, rozcinając je. Ma też w korpusie liny, więc przydaje się nie tylko do ataku: schwytał nimi np. maszyny Tanyi i Irmy.

### dic\_robot\_PLOID\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b008`

> Rzucono je w dużej liczbie także do walki w Cesarstwie Misurugi, gdzie dały się mocno we znaki Aurorze.

### dic\_robot\_ULSKGNA\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b009`

> Wysoko mobilny Pr.A.I.M.D.Re.S.S. (szturmowo-obronny zmechanizowany opancerzony piechur). Trójwymiarowe manewry na desce odrzutowej dają mu znakomite możliwości walki w powietrzu. Ta maszyna należy do typu szturmowego wzmocnionego, a jej malowanie to barwy asa zwanego Stalową Wiedźmą. Istnieją też inne odmiany Urs Ragnara, m.in. typ zintegrowanej piechoty i typ wsparcia i walki elektronicznej.

### dic\_robot\_NLVASHUZ\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00b`

> Ostateczna forma Nirvasha Z, uwolnionego z pieczęci. Ma przytłaczającą moc, a zarazem jest dowodem, że Renton Thurston żyje, i więzią łączącą Eurekę z Rentonem.

### dic\_robot\_SHINK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00d`

> Osobisty KMF Zero. Ma mechanizm transformacji w Fortress Mode, który pozwala mu nie tylko szybko latać, ale też poruszać się pod wodą. To pochodna maszyny Czarnych Rycerzy, ale dzięki przejętemu z Gawaina Druid System ma niezwykłą moc obliczeniową. Aby optymalnie używać potężnego pola obronnego Absolutna obrona, uważanego za najsilniejszą osłonę na świecie, trzeba błyskawicznie i dokładnie wprowadzać do Druid System dane o otoczeniu. W piersi ma Diffusion Structure Phase Transition Cannon: wystrzeliwuje stały ciekły metal, a gdy trafi w niego strumień cząstek, metal je rozprasza. Wykorzystanie obu tych charakterystycznych systemów, ataku i obrony, wymaga zaawansowanego przetwarzania informacji, które wydobędzie moc Druid System; dlatego poza Lelouchem nikt, nawet jeśli zdoła nim sterować, nie wykorzysta w pełni jego możliwości. Gdy Czarni Rycerze ścigali Zero, Rolo ukradł go do ucieczki, i maszyna aż do końca służyła Lelouchowi, także jako cesarzowi Britannii. W ostatecznej bitwie ruszył z F.L.E.I.J.A. Eliminatorem, by zatrzymać wybuch F.L.E.I.J.A. W ciągu 19 sekund do eksplozji wprowadził dane o otoczeniu i wspólnie z Suzaku zdołał ją powstrzymać. Na koniec zniszczył go w Damoklesie Tristan Divider pilotowany przez Gina.

### dic\_robot\_RANSAR\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00f`

> Maszyna zbudowana w Camelocie specjalnie dla Suzaku. Razem z ukończonym wcześniej Gurenem S.E.I.T.E.N. Eight Elements należy do dziewiątej generacji KMF; ponieważ istnieją tylko te dwie maszyny tej generacji, pod każdym względem przewyższa wszystkie inne. Najważniejszą zmianą jest wyposażenie w Energy Wing, które skokowo zwiększyło mobilność i zwrotność. Energy Wing może też wystrzeliwać energię w kształcie ostrzy do ataku albo, jak Blaze Luminous, okrywać maszynę i chronić ją. Znakomite osiągi w połączeniu z umiejętnościami Suzaku pozwalały mu jednym ciosem rozbić nawet maszyny Knights of the Round. Jako symbol potęgi cesarza Leloucha budził strach i nienawiść całego świata. W ostatecznej bitwie nie ustąpił ani kroku asom, takim jak Todo na Zangetsu czy Xingke na Shen Hu, zyskał czas na ukończenie F.L.E.I.J.A. Eliminatora, a potem w czasie zaledwie 0,04 sekundy rzucił nim i powstrzymał wybuch F.L.E.I.J.A. Po wtargnięciu do Damoklesa stanął do walki z odwieczną rywalką, Kallen. Oboje walczyli na śmierć i życie, a starcie zakończyło się wzajemnym ciosem: pięść Gurena S.E.I.T.E.N. Eight Elements trafiła w kokpit i maszyna eksplodowała.

### dic\_robot\_RANSR\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b011`

> KMF złożony przez Lloyda i Cecile z zapasowych części Lancelota dla C.C. Uzbrojenie ma takie jak dawny Lancelot; różni się głównie malowaniem, dodaną tarczą z rakietami z Percivala i systemem ewakuacji. W ostatecznej bitwie walczył z Gurenem S.E.I.T.E.N. Eight Elements Kallen. Zyskał dość czasu, by uciekł Lelouch, ale wobec ogromnej przewagi przeciwnika w osiągach i umiejętnościach pilota nie miał szans i został zestrzelony.

### dic\_robot\_SZRNDZK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b013`

> Knight Gigafortress Jeremiaha, oparty na systemach Siegfrieda. Pod korpusem ma duży karabin liniowy, na górze zasobniki rakiet, a w różnych miejscach pięć dużych Slash Harkenów, co daje mu wielką siłę ognia na każdym dystansie. Wymaga jednak połączenia z potencjałem nerwowym pilota, więc może nim sterować tylko Jeremiah. Kokpit stanowi Sutherland J, któremu dolną część ciała zastąpiono uproszczonym modułem lotnym. W ostatecznej bitwie walczył z Mordredem Anyi i przyjął bezpośrednie trafienie z działa Stark Hadron. Jeremiah uczepił się jednak Mordreda ocalałym Sutherlandem J i wysadził się, poważnie go uszkadzając.

### dic\_robot\_GURENSE\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b000`

> Guren przechwycony w walkach w Federacji Chińskiej, przekazany Britannii i gruntownie przebudowany przez Lloyda i Cecile. Według Lloyda łatwo go było przerabiać, bo to dzieło Rakshaty; oboje dali się ponieść pasji i stworzyli maszynę o tak wysokich osiągach, że prawie nikt nie umiał nad nią zapanować. Uważano, że poradzi sobie z nią tylko Suzaku, lecz wsiadła do niej uwolniona przez Sayoko Kallen i już przy 60％ mocy przytłoczyła Lancelota Conquistę. Osiągami odpowiada dziewiątej generacji, a w parametrach przewyższa nawet drugiego KMF tej generacji, Lancelota Albion. Zamiast skrzydeł szybowych ma Energy Wing; może okryć nimi całe ciało i szybko lecieć, nie wychodząc z postawy obronnej. Ulepszono też prawe ramię: wystrzeliwane jak Slash Harken i kierowane po linie, pozwala razić Wave Surgerem przeciwników z daleka, a sam Wave Surger można też ciskać w kształcie dysku. Nazwa S.E.I.T.E.N. Eight Elements wzięła się z napisu na ekranie startowym, który Sayoko zobaczyła przy pierwszym starcie: “Superlative Extruder Interlocked Technology Exclusive Nexus EIGHT ELEMENTS”, oddanego po japońsku. W ostatecznej bitwie stoczył bój na śmierć i życie z Lancelotem Albion Suzaku; siły były wyrównane. Skończyło się wzajemnym ciosem, lecz pięść Gurena zniszczyła kokpit Lancelota Albion. Albion eksplodował, a pojedynek dawnych rywali zakończył się zwycięstwem Kallen i Gurena.

### dic\_robot\_YzCLOWN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b002`

> Broń mobilna, którą walczy Usurper. Podobnie jak Yz-Lunedrache czerpie moc z energii duchowej pilota, a do tego, by rzucić wyzwanie A. Adventowi, nosi w nazwie “Yz”. W podstawowym projekcie uczestniczył Tetsuro Yagami, lecz Usurper, który zdobył “Czarną Mądrość”, wbudował w nią systemy zupełnie odmienne od znanej technologii. Przytłaczająca moc nieznanego źródła energii i niewyjaśnione zdolności dają jej niewyobrażalną siłę bojową.

### dic\_robot\_RYAB\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b004`

> Maszyna szturmowa Gardim, pilotowana głównie przez szeregowych żołnierzy lub SI. Podstawą taktyki jest skoordynowany atak kilku maszyn, ale i pojedynczo jest groźna. Ramiona można wymieniać zależnie od zadania; korpus z głównym silnikiem jest taki sam jak w wyższej klasy maszynie szturmowej, Blarmagu.

### dic\_robot\_ORCDN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b006`

> Broń mobilna Quaestorów: korpus Orcusula z ramionami do walki wręcz. Zwykle walczy w parze z Orcusulą In, przeznaczoną do ostrzału.

### dic\_robot\_ORCIN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b008`

> Broń mobilna Quaestorów: korpus Orcusula z uzbrojeniem do ostrzału. Zwykle walczy w parze z Orcusulą Dan, przeznaczoną do walki wręcz.

### dic\_robot\_ORCZNG\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b00a`

> Broń mobilna Quaestorów. Wersja Orcusuli Dyne na zamówienie, przeznaczona dla członków oddziału wykonawczego, Quasarów; dowodzi sojuszniczymi maszynami działającymi autonomicznie. Wzmocniono wszystkie jej elementy, a siłę bojową oszacowano na 130％ Orcusuli Dyne.

### dic\_robot\_YCLOWN\_00\_0

Adres: `dic\_text\_robot-DLC3/000b6d41:ab20b000`

> Seryjna wersja Yz-Clowna. Chwilową moc maksymalną ma niższą niż Yz-Clown, ale wysoka moc niezbadanego źródła energii zapewnia jej dużą siłę bojową. Jest też wyjątkowo wytrzymała jak na swoje rozmiary i najlepiej sprawdza się w walce grupowej, w której maszyny osłaniają się nawzajem.

### dic\_robot\_BRMAG\_00\_0

Adres: `dic\_text\_robot-DLC3/000b6d41:ace0b001`

> Wyższej klasy maszyna szturmowa Gardim, pilotowana głównie przez oficerów drugiej klasy (dowódców oddziałów). Główny silnik ma ten sam co niższej klasy maszyna szturmowa Arlyabu, lecz jest znacznie mobilniejsza i zwrotniejsza i specjalizuje się w taktyce “uderz i odskocz”. Siłą ognia także przewyższa Arlyabu: jej główna broń, Side Impulser, ma większą moc i szybkostrzelność niż Photon Impactor Arlyabu.

### dic\_robot\_CALIBARN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:96c28000`

> Prototyp zbudowany przez Ochs Earth i Instytut Vanadis. Zaprojektowano go, by w pełni wydobyć możliwości GUND-ARM, ale nie ma filtra łagodzącego burze danych: pilot przyjmuje je bezpośrednio, co naraża go na ból i śmierć. Główną bronią jest potężny Variable Rod Rifle. Z tyłu ma cztery moduły napędowe, Quadra Thruster, które mogą też służyć jako dodatkowy napęd. Podczas incydentu Vanadis skonfiskowała go Liga Zgromadzeń Kosmicznych i przechowywała w tajemnicy.

### dic\_robot\_DEMIBARD\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828000`

> Nowy model koncepcyjny z serii Demi, projektowany i rozwijany przez Burion. Mimo parametrów, przy których nie liczono się z kosztami, zachowano typową dla serii konstrukcję i łatwość obsługi. Na plecach może nosić Baori Pack z funkcją modułu lotnego.

### dic\_robot\_LFRITH\_UR\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828002`

> Mobile suit z GUND-ARM. Oparty na prototypie produkcyjnym Gundama Lfrith, zbudowanym przez Ochs Earth przed incydentem Vanadis, i wielokrotnie ulepszany. Przekazano go wrogiej Spacjanom organizacji Dawn of Fold. Główną bronią jest szybkostrzelne wiązkowe działko Gatling. Phased Array Cannon na plecach rozkłada się wraz ze wzrostem Permet Score i służy do sterowania Gundvolvami, GUND-Bitami w postaci mobile suitów.

### dic\_robot\_LFRITH\_TH\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828004`

> Mobile suit z GUND-ARM. Podobnie jak bratnia maszyna, Lfrith Ur, oparty na prototypie produkcyjnym Gundama Lfrith. Przekazano go wrogiej Spacjanom organizacji Dawn of Fold. Główną bronią jest duża broń wiązkowa, Beam Diffuse Gun. Wraz ze wzrostem Permet Score rozkłada się Phased Array Cannon na plecach, umożliwiając sterowanie Gundvolvami, GUND-Bitami w postaci mobile suitów.

### dic\_robot\_GUNDVOLVA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828006`

> GUND-Bit w postaci mobile suita. Bezzałogowa maszyna z wbudowanym GUND Format, sterowana przez Gundama Lfrith Ur i Gundama Lfrith Thorn.

### dic\_robot\_DRLBLDE\_2S\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828008`

> Maszyna demonstracyjna piątej generacji zbudowana przez Jeturk Heavy Machinery. Ma nową broń w postaci dronów, działających samodzielnie dzięki SI wspomagającej decyzje. Przebudowana przed ponownym pojedynkiem z Gundamem Aerial, otrzymała jednostkę ataku z funkcją drona, Gussa Isvarę, obronną jednostkę dronową w kształcie dużej tarczy, Daya Ambikę, oraz nową broń ręczną, Composite Arms, która rozdziela się na wiązkowy karabin śrutowy i składaną katanę wiązkową.

### dic\_robot\_GDPHARCT\_5GO\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800a`

> Maszyna z GUND Format zbudowana w tajemnicy przez Peil Technologies. Dzięki dopalaczom Blast Booster i zaawansowanej kontroli bezwładności z GUND Format znacznie lepiej lata. Główną bronią są dwa pistolety wiązkowe Beam Caliver, które po połączeniu tworzą potężny Beam Musket.

### dic\_robot\_SCHWARZ\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800c`

> Mobile suit powstały z dodania GUND Format do Schwarzette, koncepcyjnego modelu nowej generacji rozwijanego przez Jeturk Heavy Machinery. Prace nad nim długo stały w miejscu, lecz dzięki technologii przekazanej przez Prosperę Mercury został ukończony jako GUND-ARM. Wielozadaniowa platforma ataku i obrony Guardian składa się, podobnie jak Escutcheon Aeriala, z GUND-Bitów i przełącza się zależnie od sytuacji między trzema trybami.

### dic\_robot\_GDARRALRB\_E\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800e`

> Gundam Aerial przebudowany przez Shin Sei Development. Przy naprawie uszkodzeń z pojedynku z akademikiem Grassley odnowiono i rozbudowano pancerz zewnętrzny i wyposażenie. Nowy kształt pancerza bardziej odsłania moduły powłokowe, a dedykowany moduł lotny z obrotowymi rozkładanymi skrzydłami znacznie poprawia zwrotność w locie.

### dic\_robot\_GUNDNODE\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828010`

> GUND-Bit w postaci mobile suita. Opracowany pod kierunkiem Prospery Mercury równolegle z Quiet Zero, pełni rolę przekaźnika wzmacniającego przestrzeń burzy danych. Po założeniu Armor Pack może też działać jako mobile armor.

### dic\_robot\_GKEK2\_WN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828012`

> Duży dwumiejscowy KMF (Knightmare Frame) dla dowódcy. Gekkoei Sui unowocześniony przez jego twórczynię, Rakshatę, przewodniczącą Światowego Komitetu Naukowego Zjednoczonej Federacji Narodów, i jej prywatny instytut badawczy Pearl Party.

### dic\_robot\_MAGDA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828014`

> Postać, jaką część Pustki przybiera w świecie trójwymiarowym. Pustka stanowi jedną całość: Googolplex i bestia Pustki Magudda są w gruncie rzeczy tą samą istotą, a bestią Magudda staje się ta jej część, którą odcięto od rozumu. Dlatego nie ma celu ani woli i po prostu atakuje wszystko, co nie jest Pustką. W świecie trójwymiarowym jej rozmiar i kształt są zmienne, ale w walce z ludzkością najczęściej przybiera tę postać jako najskuteczniejszą. Googolplex (a raczej część, która ją naśladuje), czyli niejako rozum Pustki, nie pokazywała się, więc dla ludzkości “Pustka” oznacza przede wszystkim bestię Magudda.

### dic\_robot\_RAGMADOC\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828016`

> Postać Pustki w świecie trójwymiarowym. Właściwe ciało Pustki w wyższym wymiarze nie ma kształtu, lecz by fizycznie oddziaływać na świat trójwymiarowy, przybiera tę formę. Pustka nie zna pojęcia jednostki, więc nie potrzebowała imienia, by odróżniać się od innych; nazwę tę przyjęła dopiero po zetknięciu z ludzkością. Nie rozumie przy tym dokładnie pojęcia “boga” i używa go mniej więcej w znaczeniu “ogromnej istoty”. Także w świecie trójwymiarowym może dowolnie zmieniać rozmiar i kształt, a tę postać wybrała jako optymalną do walki z A. Adventem.

### dic\_robot\_RE\_BLASTA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828018`

> Ostateczna forma Li-Brasty, łącząca wersję Red do walki wręcz i Blue do ostrzału; maszyna eksperymentalna o zupełnie nowym podejściu. “T” w nazwie oznacza “Trial” (próba). Jedna osoba obraziła się przy tym, uznając, że “T” to inicjał konstruktorki, Trii Scott. Podstawowa koncepcja taktyczna nawiązuje do Blue, dlatego główną bronią jest AX-99 RAPTOR (precyzyjny testowy model nowego karabinu elektromagnetycznego do badań nad bronią nowej generacji) z pomniejszonym SPIGOT (interferometrem obszaru prawdopodobieństwa do przemieszczania i przekształcania obiektów). Zarazem, by wykorzystać dane z Red, wzmocniono przedni pancerz i stawy, więc radzi sobie też w walce wręcz. Przeczy to koncepcji poprzedniej wersji, w której siłę bojową zwiększano przez zawężenie zastosowań, lecz łączy aktywne wykorzystanie w uzbrojeniu kontroli zjawisk przez Sferę z wszechstronnym stylem walki Crowe'a. W efekcie, przynajmniej na papierze, w każdej sytuacji przewyższa Red i Blue. Większą niż w Blue masę zrównoważono jednak zwiększeniem mocy: prędkość wzrosła, ale trudniej zmienić tor lotu, więc maszyna jest wymagająca, a Crowe musi wykazać się jeszcze większymi umiejętnościami. Po naprawie czasoprzestrzeni, zamiast utraconej Sfery, głównym źródłem mocy jest bateria wysokoplazmowa.

### dic\_robot\_MADIVIA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801a`

> Wersja na zamówienie Madivii, maszyny szturmowej dowódców Gardim. “Degg” w języku Gardim oznacza “wybitny, znakomity”. Usunięto z niej funkcje rozpoznania i łączności maszyny dowódcy, ale dodane elastyczne skrzydła dają jej przytłaczającą mobilność. Dopracowaną już Madivię dodatkowo ulepszono dzięki technologii cywilizacji innych niż Gardim; jako połączenie technologii wielu cywilizacji, w tym Gardim, jest niejako bratnią maszyną serii Vang.

### dic\_robot\_W\_DEENBELL\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801c`

> Wersja Deenbella na zamówienie, dostrojona dla kapłana Celrica. Nosi w nazwie imię Al-Warth i jest niemal symbolem Strażników Porządku. Zdjęto z niej ogranicznik wzmocnienia mocy magicznej, jaki ma Deenbell, więc bezpośrednio wzmacnia moc pilota. Łączy łatwość obsługi Deenbella z nieograniczonym potencjałem Xelguarda; jej siła bojowa jest ogromna, a w połączeniu z mocą Celrica miażdżyła wrogów zakonu. Może też samodzielnie użyć dogmy FORUS, która otwiera bramy do innych światów.

### dic\_robot\_EFAS\_OMEGA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801e`

> E-Phas dostosowany dla Ame Presbunda. Na znak przyjaźni z dowódcą wszystkich flot, Ragnayaelem Dynharishem, pomalowano go, podobnie jak A-Ruol, w odcieniach czerni. Umiejętności Ame wydobywają z niego pełnię mocy, a jego siła bojowa wyraźnie przewyższa inne seryjne maszyny UND.

### dic\_robot\_ORCUS\_BA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828020`

> Broń mobilna Quaestorów. Orcusula Zang dostosowana dla Orchidacei, która przeniosła świadomość do systemu maszyny, więc stanowi ona niejako jej ciało. Częściowo wykorzystuje technologię Boskiej Cywilizacji Aos i przewyższa Orcusulę Zang, ale z woli Magistra musiała zachować wygląd maszyn z serii Orcusula.

### dic\_robot\_TIAMAT\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828022`

> Broń mobilna Sidereal, międzygwiezdnego sojuszu wojskowego stworzonego przez Posłańców, ludzi z Ziemi, którzy niemal dotarli do prawdy ostatecznej. Zasadniczo bezzałogowa, sterowana przez SI. W porównaniu z Daimonem o tej samej koncepcji ma znacznie większą siłę ognia i wytrzymałość, a ogólną siłą bojową dorównuje standardowym Angeloi. Zwykle trafia na pole walki razem z Daimonami; jakość tej wydajnej maszyny dodana do taktyki opartej na liczebności czyni szyk znacznie groźniejszym.

### dic\_robot\_ANGELOI\_AL\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828024`

> Broń mobilna podległa bezpośrednio Posłańcom, ludziom z Ziemi, którzy niemal dotarli do prawdy ostatecznej. Poza czarnym pancerzem wygląda jak Angeloi, lecz dzięki bezpośredniemu użyciu mocy Prawa Początku (mocy wymiarowej) jest niezwykle wytrzymała. Standardowe Angeloi to tylko jej tanie kopie. W historii jej wszechświata to legendarna maszyna, która zjawiała się na polach bitew, gdzie Sidereal miało kłopoty, i miażdżyła opór przytłaczającą siłą; niewielu wie o jej istnieniu. Mówi się, że kto ją ujrzy, wyczuje przytłaczającą istotę, do której należy, i już na zawsze ogarnie go bezgraniczna trwoga.

### dic\_robot\_EL\_MILLEN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828026`

> Broń mobilna podległa bezpośrednio Posłańcom, ludziom z Ziemi, którzy niemal dotarli do prawdy ostatecznej. Cała zbudowana jest z DEC (Dimension Energy Crystal, kryształów wymiarowych), a jej napęd i uzbrojenie czerpią wyłącznie z mocy Prawa Początku. Pilotują ją głównie duchy, Idomy, które zamieniają pragnienie ciała i życia w siłę i atakują żywe istoty. Posłańcy umieszczają po jednej do trzech takich maszyn na obserwowanych planetach: gdy cywilizacja zaczyna ewoluować wbrew ich woli, budzą się i ją niszczą. W legendach galaktyki budzą grozę jako “Olbrzymie Bestie Sądu”.
> 

### dic\_robot\_ZEL\_BILLEN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828028`

> Broń mobilna podległa bezpośrednio Posłańcom, ludziom z Ziemi, którzy niemal dotarli do prawdy ostatecznej. Cała zbudowana jest z DEC (Dimension Energy Crystal, kryształów wymiarowych), a jej napęd i uzbrojenie czerpią wyłącznie z mocy Prawa Początku. Dzięki wytrzymałemu pancerzowi i sile ognia dwie takie maszyny wystarczą, by zniszczyć armię planety przeciętnej cywilizacji Drogi Mlecznej zdolnej do lotów międzygwiezdnych. Jeszcze rzadziej niż Angeloi Arca i El Millennium trafia na fronty zwykłego wszechświata: w ciągu ostatnich 12 000 lat wysłano ją tam tylko trzy razy.

### dic\_robot\_STAMEN\_BI\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782802a`

> Broń mobilna, która wywołuje DBD (zniekształcenia granic wymiarów). Technologia panowania nad wymiarami, czerpiąca energię z ludzkiego ducha, opiera się na podejściu zupełnie obcym obecnej ziemskiej technice; przypuszcza się, że to pozostałość wysoko rozwiniętej dawnej cywilizacji. Na Ziemi, gdzie granice wymiarów stały się niestabilne, wychwytuje nienawiść osób o silnej woli i wywołuje DBD, w efekcie przyciągając wrogów zza granic wymiarów, Etrangerów.

## Seria / nazwa własna

### dic\_name\_BRVRDN\_00\_0

Adres: `dic\_text\_name/014d371a:c020b000`

> Po 12 000 lat snu budzi się Imperium Yoma, które pragnie sprowadzić Erę Demonów. Akira Hibiki, kapitan drużyny piłkarskiej Akademii Nadmorskiej, wiedziony tajemniczym głosem dociera do Reideena, uśpionego w Skale Boskiego Oblicza. Posłuszny głosowi, dokonuje Fade In i, połączony z Reideenem, rzuca się w wir walki z Imperium Yoma, ramię w ramię z Co-oplanders z Mutropolis. Akira pokonuje dowódcę Imperium Yoma, księcia Sharkina, lecz z kamiennego posągu wyzwala się cesarz Yoma Barao. Dowiedziawszy się, że płynie w nim krew starożytnego Imperium Mu, a jego matka to księżniczka Lemuria, Akira staje do walki z przerażającymi wrogami, których nasyła Barao.

### dic\_name\_BRVRDN\_00\_1

Adres: `dic\_text\_name/014d371a:c1e0b000`

> Straciwszy Jinguji, towarzysza z Co-oplanders, Akira staje wreszcie do ostatecznej bitwy z cesarzem Yoma Barao. Przytłaczająca potęga Barao przypiera Reideena do muru, lecz tajemnicza energia Mutron, uwolniona przez Lemurię za cenę jej życia, przynosi zwycięstwo i świat zostaje ocalony.

### dic\_name\_CONV\_00\_0

Adres: `dic\_text\_name/014d371a:c220b000`

> Campbellianie, od zarania dziejów ukryci we wnętrzu Ziemi, rozpoczynają inwazję. Doktor Nambara, który przewidział ten dzień, buduje Combattlera V, olbrzymiego robota łączącego się z pięciu maszyn mocą super-elektromagnetyczną. Tworzy Zespół Bojowy z czwórki zebranej z całej Japonii, Hyomy Aoi, Juzo Naniwy, Daisaku Nishikawy i Kosuke Kity, oraz swojej wnuczki, Chizuru Nambary. W trakcie walk doktor Nambara ginie, a pałeczkę przejmuje jego przyjaciel, doktor Yotsuya. Combattler V odpiera kolejnych wrogów nasyłanych przez Wielkiego Generała Garudę i w końcu pokonuje cesarzową Oleanę, która stworzyła androida Garudę. Po śmierci Oleany planeta Campbell wysyła jednak na Ziemię nowych wrogów: cesarzową Janerę, kanclerza Warchimedesa i generała Dungele. Gdy na planecie Campbell wybucha powstanie pacyfistów, Combattler V wygrywa ostateczną bitwę z Janerą i przynosi Ziemi pokój.

### dic\_name\_ZGN\_00\_0

Adres: `dic\_text\_name/014d371a:c220b002`

> Rok 0087 Ery Uniwersalnej. Minęło siedem lat od wojny jednorocznej, w której siły Federacji Ziemskiej pokonały armię Księstwa Zeonu. Titans, nowa elitarna formacja w siłach Federacji, brutalnie gnębią Spacenoidów żyjących w koloniach i na Księżycu. Przeciwnicy rosnących w siłę Titans zakładają ruch oporu przeciw Federacji, AEUG. Wśród nich jest Char Aznable, dawny as Księstwa Zeonu, którego Federacja bała się jako “Czerwonej Komety”, teraz pod imieniem Quattro Bajeena. Gdy AEUG atakuje kolonię Green Oasis, bazę Titans, wciągnięty w walkę chłopak, Kamille Bidan, z niechęci do Titans przyłącza się do AEUG. Rzuciwszy się w wir walki jako pilot, rozwija talent Newtype'a. Do wojny AEUG z Titans włącza się Axis, niedobitki Zeonu, i konflikt staje się trójstronny. By przełamać impas, AEUG planuje użyć zdobytego Działa Laserowego Kolonii. Kamille i Quattro toczą zaciętą walkę z Paptimusem Sciroccą z Titans i Haman Karn z Axis, którzy chcą powstrzymać strzał. Działo zostaje odpalone, a wojna, nazwana później konfliktem Gryps, kończy się zwycięstwem AEUG okupionym ogromnymi ofiarami. Quattro przepada jednak w walce z Haman, a Kamille, choć wygrywa zacięty pojedynek z Sciroccą, pod ostatnim ciosem jego zaciekłej woli doznaje załamania psychicznego.

### dic\_name\_GNCC\_00\_0

Adres: `dic\_text\_name/014d371a:c260b001`

> Rok 0093 Ery Uniwersalnej. Char Aznable, zaginiony od konfliktu Gryps, zostaje Wodzem Neo Zeonu. Wypowiada wojnę Federacji Ziemskiej, by ukarać ludzkość, która uczepiła się Ziemi i gnębi kosmicznych osadników, i próbuje zrzucić na Ziemię asteroidę 5th Luna. Londo Bell, jednostka pomocnicza Federacji, w której służy Amuro, walczy, by go powstrzymać, lecz 5th Luna spada na Ziemię. Potem Char zawiera tajny układ z wysokimi urzędnikami Federacji: w zamian za rozbrojenie Neo Zeon dostaje Axis, dawną asteroidę-fortecę Neo Zeonu. Char łamie jednak umowę i przystępuje do zrzucenia Axis na Ziemię. By udaremnić ten plan i rozliczyć się z Charem, Amuro w najnowszym mobile suicie, Nu Gundamie, rusza na Axis. Amuro i Char ścierają się na Axis; Amuro wygrywa, lecz Londo Bell nie udaje się zniszczyć spadającej Axis. Gdy Axis wchodzi już w atmosferę, Amuro w Nu Gundamie przywiera do niej, próbując ją odepchnąć. Światło Psycho-frame Nu Gundama powstrzymuje spadek Axis, a jego ciepły blask zostawia coś w sercach wszystkich, którzy go widzieli. Amuro i Char znikają w tej bitwie i przepadają na kartach historii.

### dic\_name\_GODGN\_00\_0

Adres: `dic\_text\_name/014d371a:c260b003`

> Wiek Przyszłości. Ludzkość, która porzuciła zrujnowaną Ziemię, żyje w kosmicznych państwach-koloniach. By uniknąć wojny totalnej, państwa organizują Gundam Fight: na ringu, którym jest Ziemia, walczą gundamy reprezentujące poszczególne kraje, a zwycięzca zyskuje na cztery lata przywództwo polityczne. W roku 60 Wieku Przyszłości Neo-Japonia wysyła do 13. Gundam Fight Gundam Fightera Domona Kasshu. Podróżując po świecie z przyjaciółką z dzieciństwa i członkinią ekipy, Rain, Domon walczy z gundamami innych krajów i ściga brata, Kyojiego, który uciekł na Ziemię w najpotężniejszej i najstraszliwszej broni, Dark Gundamie. W tej podróży, krzyżując pięści z rywalami, Domon zyskuje ich uznanie i buduje bezcenne przyjaźnie. Spotyka też swego mistrza, zwycięzcę poprzedniego turnieju, Master Asię, lecz ten sprzymierzył się z Dark Gundamem i staje przeciw niemu jako wróg ludzkości. Po morderczych walkach Domon pokonuje wreszcie Dark Gundama, wygrywa zacięty pojedynek z Master Asią i zostaje mistrzem 13. Gundam Fight. Wydaje się, że to koniec, lecz intryga Urubego z Neo-Japonii wskrzesza Dark Gundama z Rain jako biologicznym rdzeniem. Dark Gundam wchłania nawet okoliczne kolonie i rośnie w siłę bardziej niż kiedykolwiek, lecz Domon ratuje ukochaną Rain, a Dark Gundam z rozbitym rdzeniem przestaje istnieć. Gundam Fighterzy, którzy przywrócili światu pokój, ślubują spotkać się za cztery lata na 14. Gundam Fight.

### dic\_name\_GNWEW\_00\_0

Adres: `dic\_text\_name/014d371a:c260b005`

> Rok 196 Kalendarza Kolonii. Minął rok od końca wojny, którą rozpoczęła operacja Meteor, zejście pięciu gundamów na Ziemię; świat zmierza ku pokojowi. Dawni piloci gundamów, członkowie agencji wywiadowczej Preventers założonej przez Lady Une, śledzą poczynania tak zwanej Armii Mariemai. Jej przywódczyni, dziewczynka Mariemaia, podaje się za córkę Treize'a Khushrenady, przywódcy światowego państwa, który zginął w ostatniej wojnie, i razem z Dekimem Bartonem, przewodniczącym Fundacji Barton, potajemnie gromadzi siły. Jest wśród nich także pilot gundama, Wufei. Armia Mariemai porywa symbol pokoju, wiceminister spraw zagranicznych Relenę Darlian, wypowiada wojnę światu i przystępuje do “prawdziwej operacji Meteor”, czyli zrzucenia kolonii na Ziemię.

### dic\_name\_GNWEW\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b000`

> Heero, pozostali piloci gundamów i brat Releny, Zechs Merquise, udaremniają zrzucenie kolonii, lecz Armia Mariemai wykorzystuje okazję, by zrzucić na Ziemię wielkie siły mobile suitów, i zajmuje siedzibę prezydenta. Zechs, Noin oraz piloci gundamów, Duo, Quatre i Trowa, ruszają w pościg i walczą, nie zabijając pilotów, lecz przytłaczająca przewaga liczebna wroga daje im się we znaki. Wtedy przybywa Heero w Wing Gundamie Zero, na wpół zniszczonym w walce z Wufeiem, i strzela z Twin Buster Rifle w osłonę siedziby prezydenta; choć jego maszyna rozpada się, wdziera się do środka, by uratować Relenę. Atak Heera uczy Mariemaię strachu przed wojną; uświadamia sobie swój błąd i zasłania Relenę przed kulą Dekima. Ten czyn Dekima rozwściecza jednak żołnierzy; jego właśni ludzie zastrzeliwują go jako zdrajcę i walka się kończy. Gundamy, niepotrzebne w świecie bez wojny, zostają zniszczone przez swoich pilotów, a każdy z nich rusza własną drogą.

### dic\_name\_GNDE\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b001`

> Rok 71 Ery Kosmicznej. W wojnie między siłami Sojuszu Ziemskiego a PLANT, zrodzonej z waśni między genetycznie modyfikowaną nową ludzkością, Koordynatorami, a zwykłymi ludźmi, Naturalnymi, siły Sojuszu najeżdżają neutralny Orb. W tych walkach, które pochłaniają ogrom ofiar wśród cywilów, Shinn Asuka traci rodziców i siostrę. Mijają dwa lata. Shinn, już w szeregach ZAFT, zostaje pilotem nowego mobile suita, Impulse Gundama, i bierze udział w akcji odbicia trzech skradzionych nowych maszyn. Na okręcie Minerva, któremu powierzono to zadanie, są też przewodniczący Najwyższej Rady PLANT, Gilbert Dullindal, i Athrun Zala, bohater wojny sprzed dwóch lat. W trakcie misji Shinn i reszta stają wobec zrzucenia Junius Seven przez dezerterów z ZAFT, którzy chcą wytępić Naturalnych. Dzięki Minervie Junius Seven zostaje rozbity, lecz odłamki spadają na Ziemię, siejąc ogromne zniszczenia. Wybucha nowa wojna między Sojuszem Ziemskim a PLANT. Gdy walki przybierają na sile, wkracza do nich bohater poprzedniej wojny, Kira Yamato, i sytuacja jeszcze bardziej się gmatwa. Shinn, coraz ślepiej wierzący Dullindalowi, wchodzi w konflikt z Athrunem i pokonuje Kirę, który chce powstrzymać walki. Tymczasem Dullindal ogłasza Plan Destiny, system należytego zarządzania ludzkością. Kira i Athrun, przeciwni pomysłowi kierowania ludzkim losem, ścierają się z flotą ZAFT Dullindala i z Shinnem. W ostatniej bitwie Shinn przegrywa z Athrunem, Dullindal ginie, a przyszłość i wolność ludzkości zostają ocalone.

### dic\_name\_GNWOM\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b003`

> Rok 122 Ad Stella. Epoka, w której mnóstwo firm, które ruszyły w kosmos, tworzy gigantyczną strefę gospodarczą. Przepaść majątkowa sprawia, że mieszkańcy kosmosu, Spacjanie, wyzyskują mieszkańców Ziemi, Ziemian, a konflikt między nimi trwa. Suletta Mercury, dziewczyna wychowana na dalekim Merkurym, przenosi się do Szkoły Technicznej Asticassia, prowadzonej przez Grupę Benerit, giganta branży mobile suitów. W szkole uczniowie toczą “pojedynki” w mobile suitach o to, czego pragną. Pierwszego dnia Suletta poznaje Miorine Rembran, córkę prezesa Grupy Benerit, a widząc tyranię Guela Jeturka, Holdera, czyli najlepszego pilota szkoły i pierwszego kandydata na narzeczonego Miorine, staje z nim do “pojedynku”.

### dic\_name\_GNWOM\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b004`

> Pokonawszy Guela, Suletta zostaje Holderem i zarazem pierwszą kandydatką na narzeczonego Miorine. Wkrótce jednak pojawia się podejrzenie, że Aerial, mobile suit użyty w pojedynku, to GUND-ARM, zakazany ze względów bioetycznych. Gdy Suletcie grozi zniszczenie Aeriala i wydalenie ze szkoły, ratuje ją Miorine. Suletta wygrywa rewanż z Guelem i pojedynek z Elanem Ceresem. Aerial znów jednak zostaje posądzony o to, że jest GUND-ARM, i grozi mu zniszczenie. By chronić Sulettę i Aeriala, Miorine zakłada GUND-ARM S.A., firmę badającą i rozwijającą GUND jako technikę medyczną. Suletta i Miorine razem z przyjaciółmi pokonują kolejne przeszkody, lecz matka Suletty, Prospera, skrywa własne zamiary.

### dic\_name\_ABDV\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b005`

> Show Zama, chłopak, który na przekór zaniedbującym go rodzicom żyje motocrossem, pewnej nocy mknie autostradą i nagle zostaje przeniesiony do nieznanego świata. To Byston Well, inny świat leżący między morzem a lądem. Razem z Todem i innymi przybyszami z Górnego Świata, przywołanymi do Krainy Ah, Show zostaje przyjęty przez lokalnego władcę, Drake'a, jako “święty wojownik” pilotujący humanoidalne machiny bojowe zwane Aura Battlerami. Show zostaje pilotem Aura Battlera Dunbine, lecz od Marvel i innych przybyszów z Górnego Świata dowiaduje się, że Drake chce zawładnąć Byston Well, i wraz z Dunbine'em przechodzi do jego przeciwników. Wojna Aura Battlerów się rozszerza, a w zamęcie przywódczyni Ferario, Jacoba Aon, swą mocą wypędza wszystkie maszyny aury i ich ludzi do świata, z którego pochodzi Show, czyli Górnego Świata. Show, Marvel i reszta, w sojuszu pod wodzą młodej królowej Krainy Na, Cieli, i księżniczki Krainy Rau, Elle, walczą z Drakiem, który chce mocą maszyn aury zawładnąć Górnym Światem, i jego sojusznikiem, królem Krainy Ku, Bishotem. Wojna ogarnia cały świat.

### dic\_name\_ABDV\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b006`

> W zaciętej walce ginie sprawca wszystkiego, Drake, a Show i jego odwieczny wróg, Czarny Rycerz Bern, zadają sobie nawzajem śmiertelne ciosy. Ciela otwiera Drogę Aury do Byston Well, by oczyścić wszelką nienawiść. Wszyscy przybysze z Byston Well znikają z Górnego Świata; zostaje tylko Chum Huau.

### dic\_name\_DBOVA\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b007`

> Minęło 700 lat od wojny, która ogarnęła Byston Well i Górny Świat. Shion Zaba, młody myśliwy z Baran-Baran w Krainie Ah, zostaje pewnego dnia zaatakowany przez oddział Czarnego Rycerza Rabaana Zaramanda w Aura Battlerze Zwauth. Razem z Remul, księżniczką rodu strzegącego legendarnego “skarbu Baran-Baran”, wpada w ręce Rabaana i trafia do jego zamku. Z pomocą Ferario Silky, którą uratował w trakcie napadu, ucieka z lochu i wymyka się z zamku razem z Remul. Ludzie Rabaana śledzą ich jednak, więc uciekinierzy mimowolnie prowadzą ich do kryjówki skarbu Baran-Baran, starożytnego Aura Battlera Sirbine. Gdy Remul jest w niebezpieczeństwie, Shion wsiada do Sirbine'a i odpiera Zwautha Rabaana. Shion okazuje się świętym wojownikiem o niezwykłej mocy aury.

### dic\_name\_DBOVA\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b000`

> Uciekłszy w Sirbinie na pustynię, Shion zostaje uratowany przez ludzi z rodu Rozon, którzy wyczekiwali świętego wojownika. W ich zamku przyjmują go z honorami, lecz ludzie Rabaana atakują ponownie, a Rabaan porywa Remul i się wycofuje. By ją uratować, Shion z rycerzami rodu Rozon atakuje zamek Rabaana, lecz atak się nie udaje i chłopak trafia w beznadziejne położenie. Wtedy życie ratuje mu tajemniczy, podobny do mumii starzec, sługa Rabaana. Podczas śmiertelnego pojedynku Aura Battlerów Rabaana i Shiona starzec, by otworzyć Drogę Aury, uruchamia odpalenie pocisku międzykontynentalnego. To Shot Weapon, którego dusza przetrwała 700 lat i pragnie śmierci. Wybuch pocisku obraca zamek w gruzy; Rabaan i Shot znikają w świetle, a Shion, Remul i Silky przeżywają pod osłoną bariery aury Sirbine'a. Tak kończy się walka z Rabaanem, a do Byston Well wraca spokój.

### dic\_name\_ELGIM\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b001`

> Świat Pentagony, złożony z podwójnego słońca Sunz i pięciu planet. Rządzi nim Oldna Posaydal, lecz wszędzie trwają potyczki z rebeliantami i wojny nie ustają. Daba Myroad i Mirawoo Kyao, którzy z wielkimi nadziejami opuścili rodzinne strony na dalekiej planecie Coam, spotykają byłą rozbójniczkę Fannarię Amm. Przez zadawanie się z handlarzem broni Amandrą Kamandrą Daba zaczyna walczyć z armią Posaydala w Heavy Metalu L-Gaim, pamiątce po ojcu; dołącza do niego była członkini Trzynastki, Gaw Ha Leccee. Jako członek wielkich sił rebeliantów na planecie Mizun Daba raz po raz walczy z Gavletem Gablae, który także przybył z prowincji z wielkimi ambicjami. Regularna armia jest jednak potężna; pokonani Daba i reszta opuszczają Mizun.

### dic\_name\_ELGIM\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b002`

> Po wielu spotkaniach i rozstaniach Daba przyjmuje prawdziwe imię, Camen Myroad, i staje na czele rebeliantów ze wszystkich planet. Wojna przeradza się w trójstronny konflikt rebeliantów Daby, regularnej armii Posaydala i stronnictwa Giwazy Lowawa, który zbuntował się przeciw Posaydalowi. W końcu okazuje się, że prawdziwym Posaydalem jest Amandra Kamandra. Pokonawszy prawdziwego Posaydala, który ujawnił swe oblicze, i Giwazę, Daba wyzwala Świat Pentagony spod władzy tyranów. Po wojnie rozstaje się z przyjaciółmi i wraca w rodzinne strony, by opiekować się przybraną siostrą, Quwasan Olibee, której umysł zniszczył Posaydal.

### dic\_name\_MZKZRDSDG\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b003`

> Imperium Mykeńskie, przez tysiące lat ukryte głęboko pod ziemią, rozpoczyna inwazję na Ziemię. Wielki Generał Ciemności, dowodzący Siedmioma Armiami Bestii Bojowych, ogłasza zagładę ludzkości i jeden po drugim rozbija oddziały Mazingerów broniące świata. Pilot Mazinkaisera, Koji Kabuto, wraca z podróży służbowej w Paryżu do Japonii, by stawić czoło zagrożeniu, lecz po drodze atakują go Bestie Bojowe. Dzięki ofierze towarzyszy Koji dociera wreszcie do Japonii, spotyka się z pilotem Boss Robota, Bossem, i rusza do Instytutu Energii Fotonowej. Tam czekają na niego jednak tylko zrujnowany instytut i Armia Bestii Bojowych.

### dic\_name\_MZKZRDSDG\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b004`

> Z pomocą Bossa Koji wsiada do Kaiser Pildera i dokonuje Pilder On z Mazinkaiserem, którego przysłał z kosmosu profesor Yumi. Mocą Mazinkaisera rozgramia Bestie Bojowe, lecz wtedy zjawia się jeszcze groźniejszy wróg, Wielki Generał Ciemności. Niosąc nadzieje towarzyszy, Koji pokonuje go po zaciekłej walce i na świat znów wraca pokój.

### dic\_name\_GTRARK\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b005`

> 19 lat temu Ryoma Nagare, Go Ichimonji i ich towarzysze zakończyli wojnę ludzkości z potężnym wrogiem i ocalili świat. Czas płynie, a syn Ryomy, Takuma Nagare, przybywa z przyjacielem, Baku Yamagishim, do Laboratorium Saotome, by odnaleźć zabójcę matki. W laboratorium Hayato Jin, członek dawnej drużyny Gettera, szykuje się do walki z nowym wrogiem. Jakby wiedziony przeznaczeniem, Takuma wsiada do Getter Arca i z Kamuiem i Baku rzuca się w wir walki.

### dic\_name\_GTRARK\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b006`

> Dowiedziawszy się, że zabójca matki należy do Andromeda Stellaration, wroga ludzkości, Takuma razem z przyjaciółmi i Imperium Dinozaurów przeprowadza operację Jura Dead: atak na bazę wroga prosto z podprzestrzeni. W dalekiej przyszłości, do której ich przenosi, czeka ich gigantyczna wojna obejmująca cały wszechświat, toczona przez Getter Emperora i ludzkość, która go stworzyła. Choć zagubieni, pokonują zabójcę matki Takumy, McDonalda, i doprowadzają Andromeda Stellaration do upadku. Jednak Kamui, któremu McDonald powierzył broń ostateczną, BUG, po powrocie do swoich czasów wznieca bunt, by zmienić przyszłość, i na czele Imperium Dinozaurów staje przeciw ludzkości. Takuma toczy z nim zaciętą walkę, a w jej trakcie pojawia się Getter Saint Dragon.

### dic\_name\_MCRSDLPW\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b007`

> Rok 2067. Kilkadziesiąt lat po tym, jak ludzkość ruszyła w głąb galaktyki w ramach planu kolonizacji, w Gromadzie Kulistej Brisingr szerzy się zagrożenie Syndromem Var, dziwną chorobą, która bez ostrzeżenia zamienia ludzi w szaleńców. Odpowiedzią jest taktyczna jednostka muzyczna Walkure z oddziału Ragna międzygwiezdnego konglomeratu Xaos, której śpiew potrafi wyciszać Syndrom Var. Pod ochroną Klucza Delta w myśliwcach zmiennokształtnych VF-31 Siegfried dziewczęta dają koncerty w kolejnych miejscach. Freyja Wion, dziewczyna, która marzy o Walkure, w drodze na przesłuchanie trafia w sam środek zamieszek wywołanych przez Var i poznaje nowego pilota Klucza Delta, Hayate Immelmanna. Śpiewem uspokaja ludzi ogarniętych szałem; dostrzeżony talent otwiera jej drogę do Walkure i razem z Hayate rzuca się w wir walki z Syndromem Var.

### dic\_name\_MCRSDLPW\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b008`

> Wreszcie nadchodzi debiutancki koncert Freyi, lecz w jego trakcie atakuje nieznany oddział myśliwców zmiennokształtnych. Podają się za siły Królestwa Windermere, a kanclerz królestwa, Roid, wypowiada wojnę N.U.N.G. Gdy w trakcie walk Królestwo Windermere pojmuje Walkure, Xaos, macierzysta organizacja Klucza Delta, przeprowadza atak z zaskoczenia, operację Ragnarok. Roid, mając w swych rękach Mikumo, obdarzoną mocą legendarnej Śpiewaczki Gwiazd z Windermere, chce połączyć Pieśń Gwiazd z systemem Protokultury i zawładnąć galaktyką. Jego ambicje niweczą jednak Walkure, Klucz Delta i Powietrzni Rycerze z Windermere, którzy odwrócili się od Roida. Po wojnie Klucz Delta i Walkure żegnają duszę poległego towarzysza, Messera.

### dic\_name\_CGRRR\_00\_0

Adres: `dic\_text\_name/014d371a:c320b000`

> Rok 2010 kalendarza imperialnego. Supermocarstwo, Święte Imperium Britannii, najeżdża Japonię i przytłaczającą przewagą humanoidalnych machin bojowych, Knightmare Frame'ów (KMF), czyni z niej swoją prowincję. Lelouch, mieszkaniec Japonii, zwanej teraz Strefą 11, zawiera pakt z tajemniczą dziewczyną, C.C., i otrzymuje Geass, moc narzucania innym swojej woli. Choć to jedenasty książę Britannii, nienawidzi ojca, cesarza Charlesa, który uczynił z niego polityczne narzędzie. Genialnym umysłem i mocą Geass, jako zamaskowany Zero, zakłada ruch oporu, Czarnych Rycerzy, i pod hasłem niepodległości Japonii, dla spokoju siostry, Nunnally, i własnej zemsty, wszczyna bunt przeciw Britannii. Choć staje mu na drodze dawny najlepszy przyjaciel, Suzaku Kururugi, dziś żołnierz imperium, Zero skupia sojuszników, rośnie w siłę i powołuje Zjednoczoną Federację Narodów. W końcu Lelouch poznaje prawdziwy cel ojca, Charlesa, i matki, Marianne, istniejącej już tylko jako świadomość; niweczy ich plan przerobienia świata i kończy swą zemstę. Z pomocą Suzaku Kururugiego i C.C., którzy poznali prawdę i zostali jego wspólnikami, przejmuje Imperium Britannii i zasiada na tronie jako cesarz Lelouch vi Britannia. Niszczy cały ustrój Britannii, pokonuje Schneizela, sprzymierzonego z Czarnymi Rycerzami, podbija świat i skupia na sobie nienawiść całej ludzkości. Wreszcie, na paradzie, na którą patrzy cały świat, ginie z ręki Suzaku przebranego za Zero. Wszystko, od podboju świata po wyrok z ręki Zero, było planem Leloucha zwanym Zero Requiem, za który zapłacił życiem. Śmierć Leloucha, symbolu zła, przecięła łańcuch nienawiści i świat wkroczył w nową epokę. Drugi rok ery Kowa, rok po Zero Requiem. Świat, przebudowany wokół Zjednoczonej Federacji Narodów, cieszy się pokojem. Wtem nieznana grupa zbrojna porywa Nunnally, honorową doradczynię Światowej Agencji Pomocy Humanitarnej, i Zero (czyli Suzaku), głównego doradcę Czarnych Rycerzy, podczas wizyty w obozie dla uchodźców. Kallen i jej towarzysze, którzy by wyjaśnić sprawę, przenikają do Królestwa Zilkhstanu, zwanego “Krajem Wojowników”, zostają tam zaatakowani przez tajemniczego użytkownika Geass. A na miejscu są Lelouch, który powinien nie żyć, i C.C.

### dic\_name\_CGRRR\_00\_1

Adres: `dic\_text\_name/014d371a:c320b001`

> W wielkim więzieniu Zilkhstanu, do którego przeniknął z pomocą Kallen i reszty, Lelouch odzyskuje świadomość ze Świata C. Uwalnia uwięzionego Suzaku, wyprowadza z więzienia dawnych towarzyszy i przystępuje do akcji ratowania Nunnally. Przypiera do muru przywódczynię Zilkhstanu, kapłankę Shamnę, lecz jej Geass, nieskończone odrodzenie, cofa czas. Geass Shamny przenika każdy jego plan i blokuje jego działania, lecz C.C. potrząsa nim, a Lelouch z ogromu wariantów planu zawęża działanie jej mocy i to on przypiera ją do muru. Odrzuca Shamnę, która dla swojego kraju chciała znów pogrążyć świat w wojnie, i pogrąża ją w wiecznym śnie. Wyratowawszy świadomość Nunnally ze Świata C, Lelouch opuszcza dawnych towarzyszy i wyrusza z C.C. w podróż w poszukiwaniu odłamków Geass.

### dic\_name\_MJP\_00\_0

Adres: `dic\_text\_name/014d371a:c320b002`

> Rok 2110. Ludzkość, która ruszyła w kosmos, staje przed zagładą, gdy w rejonie Jowisza atakują ją tajemnicze siły Wulgaru, Zjednoczonego Imperium Wszechgalaktycznego. Tymczasem na Ziemi specjalna agencja MJP prowadzi projekt tworzenia ludzi genetycznie dostosowanych do życia w kosmosie. Team Rabbits, piątka z MJP, w tym Izuru Hitachi, to zdolni indywidualiści, ale nie potrafią współpracować, więc mają najgorsze wyniki i przezywa się ich “Pechową Piątką”. Mimo to dostają rozkaz wsiąść do najnowszych urządzeń bojowych AHSMB i rzucają się w wir walki z Wulgaru.

### dic\_name\_MJP\_00\_1

Adres: `dic\_text\_name/014d371a:c320b003`

> Team Rabbits, choć bez wprawy, jakoś walczą dalej, aż od księżniczki Teorii, która zbiegła od Wulgaru, poznają ich prawdziwy cel: zbieranie najlepszych genów dla przetrwania gatunku. Dla Wulgaru wojna to “łowy”. Do drużyny dołącza młodsza Ange, lecz po zaciekłych walkach z odwiecznym wrogiem, Jiartem, zdrowie Izuru się psuje i zakazuje mu się walki. W operacji zniszczenia międzywymiarowej bramy przerzutowej, przez którą Wulgaru wdzierają się do Układu Słonecznego, Izuru mimo to rusza do boju, by odwrócić losy bitwy i chronić przyjaciół. Po zaciekłej walce bramę niszczy stacja kosmiczna Star Rose, którą taranuje ją komandor Simon z MJP, a Izuru, w pełni przebudzony, pokonuje Jiarta. Gdy wszystko się kończy, przyjaciele witają Izuru jak bohatera.

### dic\_name\_GZLSP\_00\_0

Adres: `dic\_text\_name/014d371a:c320b004`

> Rok 2030, miasto Nigashio w prefekturze Chiba. Yun Arikawa z warsztatu Otaki Factory dostaje zlecenie zbadania pogłosek o duchach i jedzie do opuszczonej rezydencji. Tymczasem Mei Kamino, doktorantka badająca stworzenia fantastyczne, bada sygnał odebrany przez Misakioku, obserwatorium w dawnej dzielnicy. Nieznający się nawzajem, w różnych miejscach słyszą tę samą pieśń i zostają wciągnięci w anomalie, które kaiju sprowadzają na świat. Gdy w mieście nagle pojawiają się kaiju, Yun z ludźmi z Otaki Factory staje do walki w robocie Jet Jaguar, a Mei z partnerem, psim SI Pelopsem II, zgłębia tajemnicę świata.

### dic\_name\_GZLSP\_00\_1

Adres: `dic\_text\_name/014d371a:c320b005`

> Mei i Yun wymieniają się informacjami na czacie. Na całym świecie pojawiają się kaiju, a substancja zwana Czerwonym Pyłem się rozprzestrzenia. Mei i Pelops II zgłębiają tajemnicę nowego materiału, Archetypu, i Mei odkrywa, że świat zmierza ku Katastrofie, a jej Punktem Osobliwym jest olbrzymi kaiju, który pojawił się w Tokio: Godzilla. Tymczasem Jet Jaguar, Yun i reszta ruszają do Tokio, by go pokonać. By zatrzymać Katastrofę, Mei i jej sojusznicy analizują ją w Nadwymiarowym Kalkulatorze, a Pelops II znajduje protokół potrzebny do jej uniknięcia. Jet Jaguar, odebrawszy protokół, łączy się z Pelopsem II, rośnie do olbrzymich rozmiarów i po zaciekłej walce znika razem z Godzillą, powstrzymując Katastrofę. Potem dwoje geniuszy, którzy ocalili świat, Yun i Mei, wreszcie spotyka się twarzą w twarz.

### dic\_name\_DYNZNN\_00\_0

Adres: `dic\_text\_name/014d371a:c320b006`

> Yomogi Asanaka, uczeń publicznego liceum Fujiyokidai, w drodze ze szkoły spotyka mężczyznę, który padł z głodu i nazywa siebie “władcą kaiju”: Gaumę. Nazajutrz w mieście nagle pojawia się kaiju, a Gauma przyzywa olbrzymiego robota, Dynazenona. Yomogi, jego koleżanka z klasy, Yume Minami, i bezrobotny Koyomi Yamanaka, który przyszedł popatrzeć na zamieszanie, zostają wciągnięci do Dynazenona razem z Gaumą; wraz z kuzynką Koyomiego, Chise Asukagawą, piątka staje do walki z kaiju.

### dic\_name\_DYNZNN\_00\_1

Adres: `dic\_text\_name/014d371a:c320b007`

> W trakcie kolejnych walk pojawiają się dawni towarzysze Gaumy, Klub Kaiju. Czwórka, która chce stworzyć świat potrzebujący kaiju, mocą panowania nad kaiju sieje w mieście zniszczenie. Yomogi i reszta, w sojuszu z Sojuszem Gridknighta i Goldburnem, kaiju wyrosłym z nasienia znalezionego przez Chise, dojrzewają, każde na swój sposób, i ścierają się z ostatnim kaiju, Gagulą, który wchłonął Klub Kaiju. Po zaciekłej walce zwyciężają, żegnają się z Gaumą i Goldburnem i wracają do codzienności, która nieco się zmieniła.

### dic\_name\_BIGO\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a7a0b000`

> Paradigm City, miasto bez pamięci. W mieście, które utraciło wspomnienia (Pamięci) sprzed ponad 40 lat, żyje negocjator Roger Smith. Razem z androidką Dorothy rozwiązuje przynoszone mu kłopoty zręczną wymową i stanowczym działaniem. Gdy przeciwnik sięga po przemoc, Roger wsiada do czarnego Megadeusa, Big O, i na siłę odpowiada siłą. Przy codziennych zleceniach Roger zbliża się do tajemnicy Pamięci Paradigm City.

### dic\_name\_GWBRGR\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a860b001`

> Epoka, w której ludzkość zasiedliła cały Układ Słoneczny. W cieniu społeczeństwa organizacja przestępcza zwana Connection rozpościera swoje macki. Isaac, zwany “Brzytwą”, razem z Blaster Kidem, Speedym Bowiem i Angel Omachi zakłada Cosmo Rangers J9, czyścicieli, którzy za sowitą zapłatą rozprawiają się ze złem. W Braigerze, który zmienia kształt i rośnie dzięki teorii Brai-synchron, przemierzają gwiazdy i walczą z rozmaitymi wrogami. W końcu ujawnia się ich największy wróg, Khamen Khamen z Nubia Connection. J9 staje do walki z planem Khamena, by przebudować Układ Słoneczny: Planem Wielkiego Atuma.

### dic\_name\_FTDKRS\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a8a0b000`

> Shotaro Hidari opowiada o tym, jak poznał swojego mistrza, detektywa Sokichiego Narumiego, i jak go stracił. Gdy w wietrznym mieście Fuuto zaczęły działać Dopanty, potwory używające Gaia Memory, młody Shotaro szedł w ślady Sokichiego jako asystent detektywa. Sokichi prócz pracy detektywa w tajemnicy działał jako Kamen Rider Skull, aż trafiło do niego pewne zlecenie. Przyjąwszy je, uratował chłopca z placówki tajemniczej organizacji Museum i nazwał go Philipem, lecz padł od kuli. Shotaro, który ruszył jego śladem, by dostarczyć mu “kartę atutową” od klientki, w chwili rozpaczy przemienia się razem z Philipem w Kamen Ridera Double i przejmuje dzieło Sokichiego. Razem z córką Sokichiego, Akiko Narumi, prowadzą dalej Agencję Detektywistyczną Narumi i strzegą pokoju w Fuuto.

### dic\_name\_STLJEEG\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:72e0b000`

> Senjiro Shiba, wyczuwszy odrodzenie Królestwa Jamatai, przerobił syna, Hiroshiego, na cyborga, który potrafi zbudować się w Kotetsu Jeega. Hiroshi razem z Senjirem, który przeniósł świadomość do komputera i stał się Machine Father, oraz partnerką, Miwą, staje do walki z Królestwem Jamatai. Gdy pokonują królową Jamatai, Himikę, pojawia się nowy wróg: cesarz Ryuma. Za cenę ofiary Machine Father Hiroshi i reszta pokonują cesarza Ryumę i bronią pokoju.
> 

### dic\_name\_GTERJBC\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:7360b001`

> Getter Emperor dla własnych celów tworzy nowe Getter Roboty serii Noir i ich pilotów: Ryomę, Hayato i Musashiego. Wysłani do braneświata w innej czasoprzestrzeni, walczą z wyżej wymiarową bezcielesną istotą, Brahmą.

### dic\_name\_LGNHDGN\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:7360b003`

> Uczeń podstawówki, Seiji Takasugi, spotyka Da-Garna, Wojownika zrodzonego z Energii Planety. Gdy przybysze z kosmosu sięgają po Energię Planety, siłę życiową Ziemi, Seiji zostaje kapitanem Wojowników i razem z nimi staje do walki z wrogiem. Nie mogąc wyjawić prawdy ani rodzicom, ani przyjaciołom, Seiji czasem się waha, czasem cierpi, lecz zacieśnia więź z Da-Garnem i resztą i walczy dalej, by chronić Ziemię przed złem.

### dic\_name\_LGNGIDEON\_00\_0

Adres: `dic\_text\_name-DLC3/00001546:ec20b000`

> Planeta Solo, ziemska kolonia. Ludzie odkrywają tu w starożytnych ruinach olbrzymiego robota, Ideona, i statek kosmiczny Solo Ship: legendarnego boskiego olbrzyma z podań obcej rasy, Buff Clanu. Gdy Buff Clan, przerażony mocą boskiego olbrzyma, atakuje, Cosmo i reszta stawiają opór mocą Ideona. By uciec przed pościgiem, opuszczają planetę Solo na pokładzie Solo Shipa. Wśród nieporozumień, miłości i nienawiści walka narasta, pochłania zrodzone w niej więzi i uczucia, aż ogarnia całą galaktykę. W trakcie beznadziejnej ucieczki Cosmo i reszta odkrywają, że wszystkim kieruje Ide, wola Szóstej Cywilizacji zamieszkująca Ideona. Jaki koniec czeka ludzi rzucanych przez próby Ide…?
> 

### dic\_name\_IDOLMXEN\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ee20b000`

> Rok 107 Odbudowy, ponad sto lat po rozpadzie Księżyca i wywołanej nim katastrofie zwanej Lost Artemis. Humanoidalne maszyny przeciwmeteorytowe, iDOL-e, i ich piloci, iDOLmasterzy, z wielkiej międzynarodowej korporacji Mondenkind przechwytują odłamki Księżyca, Dropy, spadające na Ziemię. Haruka Amami, nowo wybrana iDOLmasterka Imbera, gubi się przy pierwszym kontakcie z iDOL-em, lecz razem z przyjaciółkami zostaje wciągnięta w walkę z Turiavitą, organizacją, która chce przejąć iDOL-e. Po walce pełnej miłości i nienawiści, by chronić Ziemię przed AULYN, bramą do innego wszechświata, Haruka i Imber z przyjaciółkami wdzierają się do AULYN.

### dic\_name\_STRDVRMVE\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b001`

> Na Wyspie Krzyża Południa, położonej na południowy wschód od Japonii, pojawia się Takuto Tsunashi. Wstępuje do Liceum Krzyża Południa i zaprzyjaźnia się z Wako Agemaki i Sugatą Shindo. Tymczasem członkowie tajnego stowarzyszenia, Zakonu Krzyża Kiraboshi, chcą ziścić swoje ambicje za pomocą olbrzymich humanoidalnych robotów, Cybody. Takuto okazuje się jednak Star Driverem Cybody Tauburn i jako Ginga Bishonen, który wydobywa moc Cybody, staje przeciw Zakonowi. Takuto, Wako, jedna z Kapłanek Czterech Stron, które z woli losu pieczętują Cybody, i Sugata, Star Driver królewskiego Cybody King Samekh, walczą, a zarazem przeżywają młodość pełną miłości, marzeń i przyjaźni. Po zaciekłych walkach Takuto, razem z Wako i Sugatą, uwolnionymi od przeznaczenia wyspy, walczy dalej w Tauburn Compartment, by powstrzymać tych, którzy używają uwolnionych Cybody do złych celów.
> 

### dic\_name\_CRSAGAD\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b003`

> Ludzkość posiadła wysoko rozwiniętą technikę informacyjną zwaną Maną i jej niemal magiczną mocą zbudowała dostatnią utopię. Angelise, pierwsza księżniczka Cesarstwa Misurugi, jednego z mocarstw tego świata, dorastała, nie znając niedostatku, a Obrzęd Chrztu w dniu 16. urodzin miał przebiec bez zakłóceń. W trakcie ceremonii wychodzi jednak na jaw, że Angelise jest Normą, aspołeczną istotą, która nie jest człowiekiem i nie potrafi używać Many. Ludzie odwracają się od niej, lżą ją i zsyłają na odległą wyspę Arzenal, surowe miejsce, gdzie przetrwać można tylko, walcząc bez końca ze Smokami, wrogami ludzkości. Pozbawiona pozycji, praw, a nawet imienia, Angelise, teraz po prostu Ange, postanawia żyć jako Mail Riderka Villkissa, humanoidalnej machiny bojowej typu Para-Mail. W trakcie walk zacieśnia więź z Mail Riderkami z Arzenalu i z Tuskiem, potomkiem Pradawnego Ludu. Wkrótce jednak odkrywa, że Smoki, z którymi walczyła, to w rzeczywistości ludzie, Lud Smoków, żyjący na Ziemi z równoległego świata. Dowiaduje się też, że prawdziwym wrogiem jest Embryo, który z cienia steruje światem i nazywa siebie Stroicielem.

### dic\_name\_CRSAGAD\_00\_1

Adres: `dic\_text\_name-DLC3/001462c6:ef20b004`

> W trudnej walce z Embryem, obdarzonym nadprzyrodzoną mocą, Ange zostaje uwięziona w szczelinie między wymiarami, lecz z pomocą ukochanego Tuska i przyjaciół oraz uwalniając ukrytą moc Villkissa, pokonuje Embrya. Zniszczywszy świat podległy Embryowi, w nowym świecie bez władców Ange spełnia z przyjaciółmi marzenie i otwiera kawiarnię.

### dic\_name\_ERKSPESHE\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b005`

> Dziesięć lat temu wirtualny świat wewnątrz Scab Coral się rozpadł, a jego mieszkańcy pojawili się na prawdziwej Ziemi; to wydarzenie nazwano Wielkim Połączeniem. Ludzie z wirtualnego świata, Green Earth, i z prawdziwego, Blue Earth, musieli nagle żyć razem, co zrodziło głębokie konflikty. Eureka, choć straciła ukochanego Rentona, walczy dalej, by odpokutować przed światem za wywołanie Wielkiego Połączenia. Otrzymuje rozkaz ochrony Iris, dziewczynki, która tak jak ona niegdyś potrafi władać Scab Coral. Ataki polującego na Iris Deweya Novaka odcinają je od wszystkich; w ucieczce Eureka i Iris mierzą się ze swoją misją i własnym istnieniem.

### dic\_name\_ERKSPESHE\_00\_1

Adres: `dic\_text\_name-DLC3/001462c6:ef20b006`

> Eureka walczy z Deweyem, by uratować porwaną Iris. Wygrywa, lecz Dewey wysadza dawny międzygwiezdny statek kolonizacyjny, którego niegdyś używali ludzie z Green Earth, i strąca go na Ziemię. W obliczu zagłady Eureka wsiada do Nirvasha Z, który się pojawia, i walczy o ocalenie świata. W świetle Scab Coral, które otula świat, Eureka spotyka ukochanego Rentona, a świat zostaje ocalony.

### dic\_name\_GNWOM\_00\_2

Adres: `dic\_text\_name-DLC4/000005b2:11c28005`

> Plan Prospery rzuca Miorine i Sulettą, Spacjanami i Ziemianami. Suletta dowiaduje się, że jest repli-child Ericht Samayi, która zamieszkuje Aeriala, a Prospera, uruchomiwszy plan, odtrąca ją. Miorine chce zostać prezesem Grupy Benerit w miejsce nieprzytomnego ojca, Dellinga, lecz Prospera czyni z niej iskrę wojny między kosmosem a Ziemią i Miorine pogrąża się w rozpaczy. Suletta odnajduje jednak to, co powinna zrobić, a Miorine, uratowana jej szczerością, znów staje na nogi. Prospera uruchamia gigantyczną fortecę, Quiet Zero, dla Ericht, która może żyć tylko w burzy danych. Suletta i Miorine z przyjaciółmi z akademika Ziemian, Guelem i resztą ruszają na Quiet Zero i go powstrzymują. Miorine ogłasza rozwiązanie Grupy Benerit; gundamy znikają razem z Quiet Zero, a Ericht zyskuje nową postać. Trzy lata później, gdy każdy idzie własną drogą, Suletta i Miorine biorą się za ręce i razem idą naprzód, ku temu, co mogą zrobić teraz.

## Słownik pojęć

### dic\_word\_zinguji\_title

Adres: `dic\_text\_word/00000826:db60b000`

> Jinguji

### dic\_word\_zinguji\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b000`

> Członek Co-oplanders i główny pilot Bluegara. Pełne imię i nazwisko: Chikara Jinguji. Chłodny realista, początkowo ścierał się z Akirą, lecz gdy obaj docenili swoje umiejętności, zostali dobrymi towarzyszami. W walce z bestią furii Yoma, Baragornem, ratując Akirę z beznadziejnego położenia, staranował wroga Bluegarem wyładowanym materiałami wybuchowymi i za cenę własnego życia dał mu szansę na zwycięstwo.

### dic\_word\_yoma\_em\_title

Adres: `dic\_text\_word/00000826:dbe0b002`

> Yoma

### dic\_word\_yoma\_em\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b003`

> Imperium Yoma to imperium demonów, które przespało 12 000 lat. Upadło niegdyś wraz z kwitnącym Imperium Mu, lecz odrodziło się w czasach współczesnych, by zaprowadzić Erę Demonów.

### dic\_word\_barao\_title

Adres: `dic\_text\_word/00000826:dbe0b005`

> Barao

### dic\_word\_barao\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b006`

> Władca Imperium Yoma, zwany cesarzem Yoma. Spał w kamiennym posągu w podziemnej świątyni i przebudził się dopiero po śmierci księcia Sharkina, dowódcy frontowego imperium. Jego olbrzymie ciało wielokrotnie przewyższa rozmiarami Reideena, a dolna połowa tkwi zagrzebana w Wyspie Yoma. Aby zaprowadzić Erę Demonów i przejąć tajemniczą energię Mutron, wysyłał przeciw Reideenowi kolejne bestie furii.

### dic\_word\_barao\_00\_1

Adres: `dic\_text\_word/00000826:dc20b000`

> Gdy stracił wszystkich podwładnych, sam ruszył do boju i przytłoczył Akirę niezwykłą potęgą. Pokonał go dopiero Reideen, któremu moc energii Mutron dała modlitwa matki Akiry, Reiko, okupiona jej życiem.

### dic\_word\_canvel\_ali\_title

Adres: `dic\_text\_word/00000826:dc20b001`

> Campbellianie

### dic\_word\_canvel\_ali\_00\_0

Adres: `dic\_text\_word/00000826:dc20b002`

> Obca rasa, która najechała Ziemię. Pod wodzą wielkiego generała Garudy, a potem cesarzowej Janery wysyłała na Ziemię bestie magmowe, lecz Combattler V za każdym razem krzyżował jej plany. Po ostatecznej klęsce Janery władzę na planecie Campbell przejęli pacyfiści i inwazja dobiegła końca.

### dic\_word\_aeug\_title

Adres: `dic\_text\_word/00000826:dc20b004`

> AEUG

### dic\_word\_aeug\_00\_0

Adres: `dic\_text\_word/00000826:dc20b005`

> Organizacja powołana do walki z Titans, którzy zawłaszczyli Siły Federacji Ziemskiej. Pełna nazwa: Anti Earth Union Group. Współpracuje z korporacjami takimi jak Anaheim Electronics i Luio &amp; Co., a kieruje nią komodor Sił Federacji Blex Forer, mający rozległe wpływy w polityce i biznesie, dzięki czemu AEUG ma znaczną siłę militarną i polityczną. Jako dawna część Sił Federacji, tak jak Titans, składa się głównie z żołnierzy Federacji, ale służą w niej też byli żołnierze Zeonu, jak porucznik Quattro Bajeena. Po kradzieży Gundama Mk-II w Gryps drobne utarczki z Titans przerodziły się w otwartą wojnę. Po konflikcie Gryps AEUG walczyła jako część Sił Federacji z Neo Zeonem pod wodzą Haman.

### dic\_word\_nt\_title

Adres: `dic\_text\_word/00000826:dc20b007`

> Newtype

### dic\_word\_nt\_00\_0

Adres: `dic\_text\_word/00000826:dc20b008`

> Ludzie uważani za ewolucyjną formę ludzkości przystosowaną do nowego środowiska, jakim jest kosmos. Mają wybitną intuicję i przenikliwość, a poszerzona świadomość ma im pozwalać na wzajemne zrozumienie bez nieporozumień. Dzięki tym zdolnościom są też wyjątkowo uzdolnionymi pilotami.

### dic\_word\_g\_fight\_title

Adres: `dic\_text\_word/00000826:dc20b00a`

> Gundam Fight

### dic\_word\_g\_fight\_00\_0

Adres: `dic\_text\_word/00000826:dc20b00b`

> Turniej o przywództwo polityczne w Sferze Ziemskiej, w którym Gundam Fighterzy wybrani przez państwa-kolonie walczą w mobile fighterach zwanych “Gundamami”. Raz na cztery lata cała Ziemia staje się ringiem eliminacji, a zwycięzcy przechodzą do finału. Dotąd odbyło się 13 turniejów. Zwycięski Gundam Fighter otrzymuje tytuł “Gundama nad Gundamami”, a jego państwo przez następne cztery lata sprawuje władzę polityczną. Turniej pomyślano jako sposób na uniknięcie wojen między ludźmi, dlatego nazywa się go “idealną wojną”.

### dic\_word\_shuffle\_title

Adres: `dic\_text\_word/00000826:dc20b00d`

> Sojusz Shuffle

### dic\_word\_shuffle\_00\_0

Adres: `dic\_text\_word/00000826:dc20b00e`

> Grupa, która od niepamiętnych czasów strzeże porządku walki i z cienia historii chroni ludzkość przed zagładą. Ma pięć tytułów: Król Kier, Dama Pik, Walet Karo, As Trefl i Czarny Joker. Na dowód tytułu na grzbiecie dłoni członka pojawia się herb Shuffle. W czasie walki z Dark Gundamem pięciu fighterów, w tym Domon, przejęło tytuły od poprzedników.

### dic\_word\_koh\_title

Adres: `dic\_text\_word/00000826:dc20b010`

> Król Kier

### dic\_word\_koh\_00\_0

Adres: `dic\_text\_word/00000826:dc20b011`

> Jeden z tytułów Sojuszu Shuffle przekazywanych z pokolenia na pokolenie. Na grzbiecie prawej dłoni jego posiadacza pojawia się szkarłatny herb serca. Domon przejął go od swojego mistrza, Master Asii.

### dic\_word\_toho\_title

Adres: `dic\_text\_word/00000826:dc20b013`

> Master Asia

### dic\_word\_toho\_00\_0

Adres: `dic\_text\_word/00000826:dc20b014`

> Mistrz Domona i zwycięzca 12. turnieju Gundam Fight, zwany Niepokonanym ze Wschodu. Ma nadludzką siłę, gołymi rękami pokonuje mobile suity i stworzył własny styl walki, szkołę Master Asia. Był Królem Kier poprzedniego pokolenia Sojuszu Shuffle, a tytuł przekazał uczniowi, Domonowi. Chciał użyć Dark Gundama, by odrodzić ukochaną Ziemię, lecz przegrał zaciekły pojedynek z Domonem, przyznał się do błędu i zmarł w ramionach ucznia.

### dic\_word\_dg\_title

Adres: `dic\_text\_word/00000826:dc20b016`

> Dark Gundam

### dic\_word\_dg\_00\_0

Adres: `dic\_text\_word/00000826:dc20b017`

> Broń mobilna o trzech cechach: samoregeneracji, samoewolucji i samoreplikacji. Pierwotnie nazywała się Ultimate Gundam i miała odrodzić środowisko Ziemi, lecz w wyniku walki o jej moc program uległ zmianie, a maszyna stała się wrogiem ludzkości. Steruje nią energia psychiczna żywej jednostki biologicznej w rdzeniu. Wskutek intrygi majora Urube z Neo-Japonii jej rdzeniem stała się Rain, a Dark Gundam rósł, wchłaniając okoliczne kolonie, aż Domon uratował Rain i zniszczył maszynę.

### dic\_word\_kyral\_title

Adres: `dic\_text\_word/00000826:dc20b019`

> Kyral Mekirel

### dic\_word\_kyral\_00\_0

Adres: `dic\_text\_word/00000826:dc20b01a`

> Niewidomy Gundam Fighter z Neo-Nepalu. Pierwszorzędny zabójca, w 13. turnieju Gundam Fight wygrywał walkowerem, mordując rywali, aż pokonał go Domon. Gdy major Urube wypowiedział światu wojnę za pomocą Dark Gundama, Kyral stanął na czele Sojuszu Gundamów broniącego Ziemi.

### dic\_word\_love\_title

Adres: `dic\_text\_word/00000826:dc20b01c`

> Wyznanie stulecia

### dic\_word\_love\_00\_0

Adres: `dic\_text\_word/00000826:dc20b01d`

> Żarliwy okrzyk Domona, który chciał uratować Rain, przemienioną w jednostkę biologiczną Dark Gundama. Rain, dręczona winą za zbrodnie ojca, doktora Mikamury, uparcie odtrącała Domona, lecz gdy wykrzyczał jej swoją miłość, jej zamknięte serce stopniało i wyrwała się spod władzy Dark Gundama. Siła ich miłości zrodziła potem Sekiha Love Love Tenkyoken, który unicestwił Dark Gundama.

### dic\_word\_w\_fang\_title

Adres: `dic\_text\_word/00000826:dc20b01f`

> White Fang

### dic\_word\_w\_fang\_00\_0

Adres: `dic\_text\_word/00000826:dc20b020`

> Zbrojna organizacja mieszkańców kolonii, którzy chcieli uwolnić się od ingerencji Ziemi. Założył ją Quinze, a na jego prośbę przywództwo objął Milliardo Peacecraft (Zechs) z rodu królewskiego Królestwa Sanc. Milliardo wypowiedział wojnę Ziemi rządzonej przez OZ i wybuchła wojna totalna, lecz jego celem, tak jak Treize'a, było pokazanie wszystkim grozy wojny. Walki ustały, gdy Milliardo przegrał pojedynek z Heerem.

### dic\_word\_treize\_title

Adres: `dic\_text\_word/00000826:dc20b022`

> Treize

### dic\_word\_treize\_00\_0

Adres: `dic\_text\_word/00000826:dc20b023`

> Członek kierownictwa Fundacji Romefeller i przywódca tajnej organizacji OZ. Pełne imię i nazwisko: Treize Khushrenada. Ambitny geniusz o absolutnej charyzmie, który zamierza zreformować zepsuty świat i odmienić gnuśną epokę. Pierwszorzędny pilot MS, ma własną filozofię i estetykę wojny. Głęboko odczuwa też winę za wojnę: pamięta liczbę i imiona wszystkich, którzy polegli w walce. Po zamachu stanu OZ otwarcie sprzeciwił się polityce Fundacji Romefeller, został odsunięty i uwięziony jako zdrajca, lecz później znów stanął na czele OZ. Wufei, którego raz pokonał, uważał go za śmiertelnego wroga i w ostatniej bitwie wyzwał go na pojedynek. Wufei wygrał, ale właśnie tego pragnął Treize, a Wufei, nie mając już dokąd skierować swych uczuć, długo potem się zmagał.

### dic\_word\_cinq\_k\_title

Adres: `dic\_text\_word/00000826:dc20b025`

> Królestwo Sanc

### dic\_word\_cinq\_k\_00\_0

Adres: `dic\_text\_word/00000826:dc20b026`

> Państwo w północnej Europie, które głosiło całkowity pacyfizm. Kwitło pod rządami rodu królewskiego Peacecraftów, lecz Zjednoczony Sojusz Sfery Ziemskiej uznał je za groźne i zniszczył. Odrodziło się na krótko, gdy głową państwa została księżniczka Relena Peacecraft, ale znów pochłonęła je wojna i Relena ogłosiła jego rozwiązanie.

### dic\_word\_puppy\_title

Adres: `dic\_text\_word/00000826:dc20b028`

> Psiak

### dic\_word\_puppy\_00\_0

Adres: `dic\_text\_word/00000826:dc20b029`

> Szczeniak, który zginął podczas jednej z misji Heera. Śmierć psa i niewinnej dziewczynki, której życie Heero przy tym odebrał, odcisnęła piętno na jego myślach i czynach.

### dic\_word\_natak\_title

Adres: `dic\_text\_word/00000826:dca0b001`

> Nataku

### dic\_word\_natak\_00\_0

Adres: `dic\_text\_word/00000826:dca0b002`

> Zmarła żona Changa Wufeia. Wufei wierzy, że jej dusza zamieszkuje jego Gundama, dlatego nazywa swoją maszynę “Nataku”.

### dic\_word\_op\_meteor\_title

Adres: `dic\_text\_word/00000826:dca0b004`

> Operacja Meteor

### dic\_word\_op\_meteor\_00\_0

Adres: `dic\_text\_word/00000826:dca0b005`

> Plan wysłania na Ziemię pięciu Gundamów z różnych kolonii pod postacią meteorytów. Wcielono go w życie, by powstrzymać tajną organizację OZ przed przejęciem Zjednoczonego Sojuszu Sfery Ziemskiej. Pilotami Gundamów byli Heero, Duo, Trowa, Quatre i Wufei.

### dic\_word\_op\_meteor\_00\_1

Adres: `dic\_text\_word/00000826:dca0b006`

> Pierwotny plan Dekima Bartona był jednak zupełnie inny: zrzucić kolonię, pogrążyć Ziemię w chaosie i wykorzystać to, by opanować ją Gundamami.

### dic\_word\_logos\_title

Adres: `dic\_text\_word/00000826:dca0b007`

> Logos

### dic\_word\_logos\_00\_0

Adres: `dic\_text\_word/00000826:dca0b008`

> Kompleks wojskowo-przemysłowy istniejący podobno od zarania dziejów, mający ogromny wpływ na politykę. Tworzą go handlarze śmiercią, którzy zza kulis sterowali wojnami i odbudową, zbijając na tym fortuny. Logos stał za Blue Cosmos i urabiał opinię publiczną, by doprowadzić do wojny Sojuszu Ziemskiego z Koordynatorami. Członkami Logosu byli dawny przywódca Blue Cosmos Multa Azrael i obecny, Lord Djibril. Celem Logosu było przedłużanie wojen dla zysku, a to, że Blue Cosmos dążyło do wytępienia Koordynatorów, wynikało głównie z osobistych uczuć tych dwóch ludzi. Nie mając własnych sił zbrojnych, w poprzedniej wojnie Logos wykorzystał armię Sojuszu Ziemskiego, by wybić Koordynatorów, a po wojnie stworzył Phantom Pain, by sięgać po siłę bezpośrednio. Gdy Dullindal ujawnił istnienie i czyny Logosu, rozwścieczony tłum większość członków aresztował lub zlinczował. Djibril, który przetrwał najdłużej, stracił atut, Requiem, i zginął zestrzelony wraz z okrętem, którym uciekał.

### dic\_word\_dullindal\_title

Adres: `dic\_text\_word/00000826:dca0b00a`

> Dullindal

### dic\_word\_dullindal\_00\_0

Adres: `dic\_text\_word/00000826:dca0b00b`

> Były przewodniczący Najwyższej Rady PLANT. Pełne imię i nazwisko: Gilbert Dullindal. W przeciwieństwie do poprzednika, Patricka Zali, był umiarkowany i szukał drogi do pokoju i współistnienia z Naturalnymi. Podczas incydentu Junius Seven i w późniejszej wojnie z Sojuszem Ziemskim zawsze zachowywał spokój, trafnie decydował i dowiódł talentu przywódczego. Aby podnieść ducha PLANT, wykreował Meer Campbell na sobowtóra Lacus Clyne, lecz gdy wyszło na jaw, że potajemnie próbował zabić prawdziwą Lacus, stracił zaufanie Kiry i jego towarzyszy. Jego ostatecznym celem było społeczeństwo sterowane na poziomie genów, nazwane Planem Destiny. Po rozbiciu Logosu ogłosił światu wprowadzenie planu, ale powstrzymali go Kira i jego towarzysze, którzy nie chcieli świata bez ewolucji. Zastrzelił go Ray, któremu ufał jak synowi. Zmarł w ramionach Talii, dawnej ukochanej, do której nadal coś czuł.

### dic\_word\_gora\_gyre\_title

Adres: `dic\_text\_word/00000826:dca0b00d`

> Goraon i Gyre-Garing

### dic\_word\_gora\_gyre\_00\_0

Adres: `dic\_text\_word/00000826:dca0b00e`

> Dwa okręty aury z Byston Well. Goraon był okrętem sił przeciwnych Drake'owi, dowodzonym przez Elle Hunm, wnuczkę króla Krainy Rau Foizona Gowa. Gyre-Garing był okrętem flagowym króla Krainy Ku Bishota Hatty, sprzymierzonego z Drakiem. W decydującej bitwie nad Pacyfikiem Goraon staranował Gyre-Garing i oba okręty zniknęły z Górnego Świata.

### dic\_word\_hyper\_title

Adres: `dic\_text\_word/00000826:dca0b010`

> Hyper

### dic\_word\_hyper\_00\_0

Adres: `dic\_text\_word/00000826:dca0b011`

> Zjawisko zachodzące, gdy moc aury pilota maszyny aury rośnie ponad miarę. Gdy człowieka ogarniają negatywne uczucia, jak gniew, smutek czy nienawiść, jego moc aury się rozrasta, powiększając maszynę aury albo samo ciało. Powiększona postać to prawdopodobnie bariera, która przybrała kształt maszyny. Daje ogromną siłę, lecz tak rozdętej mocy aury nie da się opanować, a umysł i ciało pilota, który przeszedł w Hyper, w końcu się rozpadają.

### dic\_word\_byston\_title

Adres: `dic\_text\_word/00000826:dca0b013`

> Byston Well

### dic\_word\_byston\_00\_0

Adres: `dic\_text\_word/00000826:dca0b014`

> Inny świat, który podobno leży między morzem a lądem Górnego Świata. Zwany jest miejscem spoczynku dusz. Oba światy są od siebie ściśle oddzielone niewidzialną granicą, lecz łączy je przestrzeń przejścia zwana Drogą Aury, którą wolno wędrować jedynie duszom. Przejście żywego człowieka z Górnego Świata do Byston Well, a także mieszkańca Byston Well do Górnego Świata, jest surowym tabu. Byston Well dzieli się na trzy warstwy. Na górze leży Wa Landon, Królestwo Wody, niebiańska kraina rządzona przez Ferario. Pośrodku leży Świat Ludzi, gdzie żyją zwykli ludzie na poziomie średniowiecznej Europy; zanim maszyny aury rozpętały wojny, walczono tam mieczami. Na samym dole leży Bobhless, rządzony przez barbarzyńców ciemności, Garow Ran. Gdy złamano tabu, sprowadzając do Świata Ludzi ludzi z Górnego Świata, i zbudowano maszyny aury, wielka wojna ogarnęła Byston Well i Górny Świat.

### dic\_word\_13cro\_title

Adres: `dic\_text\_word/00000826:dce0b001`

> Trzynastka

### dic\_word\_13cro\_00\_0

Adres: `dic\_text\_word/00000826:dce0b002`

> Elita armii Posaydala pod dowództwem Giwazy Lowawa, zwana też EX13. Każdy z jej członków ma prawo dowodzić własnym oddziałem i jest zarazem świetnym pilotem Heavy Metalu.

### dic\_word\_13cro\_00\_1

Adres: `dic\_text\_word/00000826:dce0b003`

> Wielu z nich poparło bunt Giwazy przeciw Posaydalowi.

### dic\_word\_pent\_world\_title

Adres: `dic\_text\_word/00000826:dce0b004`

> Świat Pentagony

### dic\_word\_pent\_world\_00\_0

Adres: `dic\_text\_word/00000826:dce0b005`

> Układ gwiezdny z podwójnym słońcem Sunz i pięcioma planetami. Po długich wojnach zjednoczył go Oldna Posaydal, lecz bunty wciąż trwają i ogień wojny nie gaśnie.

### dic\_word\_hell\_title

Adres: `dic\_text\_word/00000826:dce0b007`

> Dr Hell

### dic\_word\_hell\_00\_0

Adres: `dic\_text\_word/00000826:dce0b008`

> Szalony naukowiec, który chciał podbić świat i siał postrach. Z ruin starożytnych Myken odkrytych na wyspie Bardos stworzył armię Kikaiju, lecz zginął pod koniec walki z Kojim Kabuto i jego Mazinkaiserem.

### dic\_word\_thayir\_title

Adres: `dic\_text\_word/00000826:dce0b00a`

> Tahir

### dic\_word\_thayir\_00\_0

Adres: `dic\_text\_word/00000826:dce0b00b`

> Starszy brat Baku Yamagishiego. Były założyciel religii Zielonej Ziemi, obdarzony czymś na kształt nadprzyrodzonej zdolności pojmowania “woli Gettera”. 19 lat temu na froncie syberyjskim pilotował Shin Getter Robo z Ryomą Nagare i Go Ichimonjim, ratując świat przed zagładą nuklearną. Od tamtej pory, jak Ryoma i Go, uchodzi za zaginionego.

### dic\_word\_em\_lelouch\_title

Adres: `dic\_text\_word/00000826:dce0b00d`

> Cesarz Lelouch

### dic\_word\_em\_lelouch\_00\_0

Adres: `dic\_text\_word/00000826:dce0b00e`

> 99. cesarz Świętego Imperium Britannii. Pełne imię i nazwisko: Lelouch vi Britannia. Przeszedł do historii jako Cesarz Tyran, który okrucieństwem pogrążył świat w strachu. Przejął pełnię władzy, pokonując Czarnych Rycerzy i swojego brata Schneizela, lecz w końcu zginął z ręki Zero, przywódcy Czarnych Rycerzy.

### dic\_word\_shirley\_title

Adres: `dic\_text\_word/00000826:dce0b010`

> Shirley

### dic\_word\_shirley\_00\_0

Adres: `dic\_text\_word/00000826:dce0b011`

> Uczennica Akademii Ashford, do której chodził Lelouch. Pełne imię i nazwisko: Shirley Fenette. Łączyło ją z Lelouchem coś więcej niż przyjaźń; nawet gdy odkryła, że jest Zero z Czarnych Rycerzy, postanowiła go wspierać. Zna prawdę o Zero Requiem i potajemnie pomagała C.C.

### dic\_word\_charles\_title

Adres: `dic\_text\_word/00000826:dce0b013`

> Charles

### dic\_word\_charles\_00\_0

Adres: `dic\_text\_word/00000826:dce0b014`

> 98. cesarz Świętego Imperium Britannii. Pełne imię i nazwisko: Charles zi Britannia. Ojciec Lelouch i Nunnally. Wraz z ich matką, swoją żoną Marianne vi Britannią, chciał stworzyć świat bez kłamstwa, łącząc myśli całej ludzkości w “Połączenie Ragnarok”. Lelouch udaremnił ich zamiar, a Charles i Marianne zostali wchłonięci przez Świat C, w którym gromadzi się świadomość ludzi, i zniknęli.

### dic\_word\_c\_world\_title

Adres: `dic\_text\_word/00000826:dce0b016`

> Świat C

### dic\_word\_c\_world\_00\_0

Adres: `dic\_text\_word/00000826:dce0b017`

> Przestrzeń, w której gromadzą się ludzka świadomość, myśli i wspomnienia. Można powiedzieć, że istniejąca w niej nieświadomość zbiorowa jest samym Światem C.

### dic\_word\_god\_title

Adres: `dic\_text\_word/00000826:dce0b019`

> Bóg

### dic\_word\_god\_00\_0

Adres: `dic\_text\_word/00000826:dce0b01a`

> Nieświadomość zbiorowa istniejąca w Świecie C. Jako zbiór świadomości i wspomnień wszystkich ludzi ponad czasem jest w istocie całym światem.

### dic\_word\_b\_knights\_title

Adres: `dic\_text\_word/00000826:dce0b01c`

> Czarni Rycerze

### dic\_word\_b\_knights\_00\_0

Adres: `dic\_text\_word/00000826:dce0b01d`

> Organizacja założona przez zamaskowanego Zero. Jako ruch oporu walczyła z panowaniem Świętego Imperium Britannii, a jako obrońca sprawiedliwości karała bezprawie w Strefie 11, zyskując poparcie ludzi. Wchłaniając ruchy oporu z całego świata, wyrosła na wielką siłę zbrojną i walczyła do końca nawet po wstąpieniu Lelouch na tron. Po zamachu na cesarza Lelouch stała się siłą zbrojną Zjednoczonej Federacji Narodów i strzeże porządku na całym świecie.

### dic\_word\_ash\_school\_title

Adres: `dic\_text\_word/00000826:dce0b01f`

> Akademia Ashford

### dic\_word\_ash\_school\_00\_0

Adres: `dic\_text\_word/00000826:dce0b020`

> Szkoła w dawnej Strefie 11, prowadzona przez britannijski ród szlachecki Ashfordów. Panował w niej liberalny duch, a jej drzwi stały otworem nawet dla honorowych Britannijczyków. Uczyli się w niej Lelouch, Suzaku i Kallen, dla których to miejsce pełne wspomnień.

### dic\_word\_h\_britannia\_title

Adres: `dic\_text\_word/00000826:dd20b001`

> Św. Imperium Britannii

### dic\_word\_h\_britannia\_00\_0

Adres: `dic\_text\_word/00000826:dd20b002`

> Święte Imperium Britannii: potężne imperium łączące dawny ustrój arystokratyczny z najnowszą techniką i wielką siłą militarną. W latach 2000. kalendarza imperialnego 98. cesarz Charles rozpoczął zbrojny podbój świata. Podbite kraje traciły nazwy i otrzymywały numery jako “Strefa nr”, a podbitych ludzi nazywano “Numerami”. Inwazje i bezwzględna polityka dyskryminacji zrodziły liczne ruchy oporu. 99. cesarzem został Lelouch vi Britannia, a po zamachu na niego imperium przekształcono w Księstwo Britannii, które przystąpiło do Zjednoczonej Federacji Narodów.

### dic\_word\_shikhara\_title

Adres: `dic\_text\_word/00000826:dd20b004`

> Shikaara

### dic\_word\_shikhara\_00\_0

Adres: `dic\_text\_word/00000826:dd20b005`

> W języku Wulgaru: “polowanie”.

### dic\_word\_shikhara\_00\_1

Adres: `dic\_text\_word/00000826:dd20b006`

> Dla Wulgaru to zarazem zbiór genów dla przetrwania gatunku i obyczaj, wręcz część kultury.

### dic\_word\_lamata\_title

Adres: `dic\_text\_word/00000826:dd20b007`

> Lamata

### dic\_word\_lamata\_00\_0

Adres: `dic\_text\_word/00000826:dd20b008`

> W języku Wulgaru “zdobycz” w polowaniu. Znaczy coś więcej niż cel ataku: Wulgaru, który uznał kogoś za swoją lamatę, obsesyjnie się na nim skupia.

### dic\_word\_urgal\_title

Adres: `dic\_text\_word/00000826:dd20b00a`

> Wulgaru

### dic\_word\_urgal\_00\_0

Adres: `dic\_text\_word/00000826:dd20b00b`

> Tajemnicza obca rasa, nazywająca siebie Zjednoczonym Imperium Wszechgalaktycznym. Starcie z ludzkością w sferze Jowisza zapoczątkowało wojnę. Ich biologia, siła militarna i cele inwazji pozostają owiane tajemnicą.

### dic\_word\_urgal\_00\_1

Adres: `dic\_text\_word/00000826:dd20b00c`

> Później księżniczka Teoria, która zbiegła od Wulgaru, ujawniła, że celem ich inwazji jest zdobycie wartościowych genów dla przetrwania gatunku.

### dic\_word\_garukier\_title

Adres: `dic\_text\_word/00000826:dd20b00d`

> Galkie

### dic\_word\_garukier\_00\_0

Adres: `dic\_text\_word/00000826:dd20b00e`

> Cesarz Wulgaru i przyrodni brat Jiarta. Przejął władzę, mordując ojca, poprzedniego cesarza, i rządzi Legatami (dowódcami legionów). Po wyroczni, która przychodzi raz na 300 lat, postanowił najechać Ziemię.

### dic\_word\_ceres\_w\_title

Adres: `dic\_text\_word/00000826:dd20b010`

> Bitwa o Ceres

### dic\_word\_ceres\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd20b011`

> Wielka kontrofensywa GDF w rejonie planety karłowatej Ceres, nazwana operacją Thunderbolt, dowodzona przez zastępcę szefa sztabu Komine. Atak Wulgaru jeszcze przed rozpoczęciem operacji wywołał chaos, a straty GDF były katastrofalne. Bitwa skończyła się odwrotem Wulgaru, lecz w praktyce była porażką GDF. Ze względu na rachuby dowództwa GDF opinii publicznej przedstawiono ją jednak jako wielkie zwycięstwo Ziemi, a Team Rabbits jako jego bohaterów.

### dic\_word\_h\_earth\_title

Adres: `dic\_text\_word/00000826:dd20b013`

> Historia Ziemi

### dic\_word\_h\_earth\_00\_0

Adres: `dic\_text\_word/00000826:dd20b014`

> Burzliwe 60 lat od wprowadzenia Nowej Ery Uniwersalnej (New Universal Correct-Century: NUCC). NUC 000 - Wybucha Nowa Wojna Galaktyczna, pierwsza wojna ludzkości z obcą rasą. - Po jej zakończeniu powstaje N.U.N.G. i zostaje wprowadzona Nowa Era Uniwersalna. NUC 003 - Rusza plan kolonizacji: ludzkość wyrusza w galaktykę. - Powstaje Federacja Ziemska, rząd całej Sfery Ziemskiej. NUC 006 - Pierwszy Gundam Fight, wojna zastępcza o władzę w Federacji. NUC 023 - Walki z Imperium Dinozaurów i Imperium Hyakki. NUC 030-039 - Wojny ludzi w galaktyce z obcymi rasami docierają na Ziemię. NUC 038 - Walka z Imperium Dinozaurów (front syberyjski). NUC 048 - Księstwo Zeonu ogłasza niepodległość: wojna jednoroczna. Od tej pory trwa konflikt mieszkańców Ziemi i kosmosu. NUC 050 - Pierwsze starcie z Wulgaru (nieoficjalne). NUC 055 - Pierwsza wojna PLANT, konflikt Koordynatorów i Naturalnych. NUC 056 - Pierwsze starcie z Wulgaru (oficjalne). NUC 057 - Wojna rewolucyjna. Wybucha wiele konfliktów naraz, a Sferę Ziemską ogarnia chaos. NUC 058 - Powstaje Nowa Federacja Ziemska.

### dic\_word\_galactic\_w\_title

Adres: `dic\_text\_word/00000826:dd20b016`

> Nowa Wojna Gal.

### dic\_word\_galactic\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd20b017`

> Nowa Wojna Galaktyczna: pierwsza wojna międzygwiezdna ludzkości z obcą rasą. Zaczęła się od kontaktu z Zentradi, rasą olbrzymów, szybko się rozszerzyła i w końcu Ziemia została wciągnięta w wojnę wielu obcych ras. Ziemia poniosła druzgocące straty, a przetrwanie ludzkości stanęło pod znakiem zapytania, lecz pokój z obcymi rasami zakończył wojnę i ludzkość uniknęła zagłady. Wraz z rasami, z którymi zawarła pokój, ludzkość utworzyła nowy rząd, N.U.N.G., i szybko się odbudowała. Ponieważ wojna ta całkowicie odmieniła ludzkość, wprowadzono Nową Erę Uniwersalną i ludzkość weszła w nową epokę.

### dic\_word\_revol\_w\_title

Adres: `dic\_text\_word/00000826:dd20b019`

> Wojna rewolucyjna

### dic\_word\_revol\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd60b000`

> Wielka wojna, która wybuchła w NUC 058. Jednocześnie wybuchły konflikty na wielu frontach: Ziemian ze Spacenoidami, Naturalnych z Koordynatorami, starej władzy z nowymi siłami. Była to największa wojna od czasów Nowej Wojny Galaktycznej. Do tego doszły walki wywołane przez przybyszów z innego świata, Byston Well, szał Dark Gundama i wielkie zamachy terrorystyczne Dr. Hella, a przez pewien czas ważyło się samo przetrwanie ludzkości. W zaciekłych walkach polegli przywódcy wszystkich stron: Jamitov Hymem, Paptimus Scirocco, Gilbert Dullindal, Haman Karn, Milliardo Peacecraft, Charles zi Britannia, Schneizel el Britannia i Treize Khushrenada. Ostatecznie pozostali Lelouch vi Britannia jako przywódca Ziemi i Char Aznable jako przywódca kosmosu. Gdy zbliżało się ich ostateczne starcie, cesarz Lelouch został zamordowany na oczach tłumów i wojna dobiegła końca. Uważa się, że sprawiła to nie tylko śmierć przywódców pragnących wojny, ale też to, że wielu ludzi, widząc okropieństwa walk, porzuciło nienawiść i zapragnęło pokoju. Ponieważ odmieniła ona ludzką świadomość, tę serię konfliktów nazwano wojną rewolucyjną (Revol War); świat przebudowano i powstała Nowa Federacja Ziemska.

### dic\_word\_nef\_title

Adres: `dic\_text\_word/00000826:dd60b002`

> Nowa Fed. Ziemska

### dic\_word\_nef\_00\_0

Adres: `dic\_text\_word/00000826:dd60b003`

> Organ wyrażający wspólną wolę ludzkości, utworzony po wojnie rewolucyjnej. Wyrósł z Federacji Ziemskiej, ale stawia na pojednanie mieszkańców Ziemi i kosmosu oraz pokojowe rozwiązywanie sporów. Wyciągając wnioski z problemów scentralizowanej Federacji, daje szerokie uprawnienia dawnym państwom i koloniom kosmicznym, zwanym jednostkami administracyjnymi drugiego szczebla. To jednak ogranicza władzę Nowej Federacji i budzi wątpliwości, czy zdoła ona przewodzić światu odmienionemu przez wojnę rewolucyjną.

### dic\_word\_oboro\_title

Adres: `dic\_text\_word/00000826:dd60b005`

> Haze

### dic\_word\_oboro\_00\_0

Adres: `dic\_text\_word/00000826:dd60b006`

> Jeden z oddziałów NINJA zwanych Tajnymi Siłami Specjalnymi. Wywodzi się ze szkół ninja z okresu walczących królestw w Japonii. Wtajemniczeni uważają go za najpotężniejszy z oddziałów, lecz jego wielkość, skład i siedziba pozostają tajemnicą. Prowadzi wywiad i dywersję, a także walczy w mobilnych pancerzach ninja, maszynach przeznaczonych dla NINJA.

### dic\_word\_ninja\_title

Adres: `dic\_text\_word/00000826:dd60b008`

> NINJA

### dic\_word\_ninja\_00\_0

Adres: `dic\_text\_word/00000826:dd60b009`

> Żołnierze sił specjalnych wywodzący się od dawnych japońskich ninja. Nazwa pochodzi od “New Infinity Neuron - Japanese Assassin”. Treningiem budzą obwody nerwowe niedostępne zwykłym ludziom, co pozwala im choć na chwilę wyzwolić ukryty potencjał człowieka. Badania nad tą zdolnością mają długą historię, a grup NINJA zwanych Tajnymi Siłami Specjalnymi, każda z własnymi metodami treningu, jest kilka. Wynajmowane przez rządy i różne instytucje, działają jako agenci.

### dic\_word\_ninja\_armor\_title

Adres: `dic\_text\_word/00000826:dd60b00b`

> Mob. pancerz ninja

### dic\_word\_ninja\_armor\_00\_0

Adres: `dic\_text\_word/00000826:dd60b00c`

> Broń mobilna przeznaczona dla NINJA. Dzięki elastycznemu szkieletowi i napędowi ze sztucznych mięśni ma niespotykaną zwrotność. Sterowanie półpodążające łączy ruchy ciała pilota z obsługą przyrządów i jest niezwykle czułe. Ponieważ maszyna i pilot są połączeni nerwowo, pilot odczuwa też uszkodzenia, więc ktoś bez szkolenia NINJA ledwie zdoła nią chodzić. Służy głównie do zwiadu, skrytego lub siłowego, dlatego mobilność ceni się w niej wyżej niż siłę ognia.

### dic\_word\_mont\_title

Adres: `dic\_text\_word/00000826:dd60b00e`

> Mond

### dic\_word\_mont\_00\_0

Adres: `dic\_text\_word/00000826:dd60b00f`

> Mobilny pancerz ninja używany przez członków oddziału Haze z Tajnych Sił Specjalnych. Przy jego budowie współpracował Tetsuro Yagami, kładąc większy nacisk na jedność z pilotem niż w maszynach innych grup. To zarazem ogromne obciążenie dla pilota, dlatego wtajemniczeni mówią: “Silny nie jest Mond, tylko Haze, który potrafi go opanować”.

### dic\_word\_ninja\_fang\_title

Adres: `dic\_text\_word/00000826:dd60b011`

> Kły ninja

### dic\_word\_ninja\_fang\_00\_0

Adres: `dic\_text\_word/00000826:dd60b012`

> Techniki NINJA inne niż walka wręcz. Zwykle nazywa się je “ninjutsu”. Oprócz ataków piorunem czy ogniem, wywoływanych substancjami chemicznymi lub specjalnymi narzędziami ninja, są też kły ninja działające jak granat ogłuszający albo wywołujące zbiorowe halucynacje. Zwykle zasilają je małe baterie, lecz oddział Haze podobno uruchamia je innym sposobem niż pozostałe grupy.

### dic\_word\_ninja\_tool\_title

Adres: `dic\_text\_word/00000826:dd60b014`

> Narz. ninja

### dic\_word\_ninja\_tool\_00\_0

Adres: `dic\_text\_word/00000826:dd60b015`

> Sprzęt i przyrządy używane przez NINJA, w tym broń oraz urządzenia i materiały do uruchamiania kłów ninja. Części z nich może używać każdy, więc niektóre narzędzia ninja trafiły do powszechnego użytku.

### dic\_word\_val\_x\_title

Adres: `dic\_text\_word/00000826:dd60b017`

> VAL-X

### dic\_word\_val\_x\_00\_0

Adres: `dic\_text\_word/00000826:dd60b018`

> Organizacja terrorystyczna działająca od czasów po wojnie rewolucyjnej. Jej nazwa podobno pochodzi od “Victory, Anarchy, Liberation - X”, lecz jej ideologia i postulaty są mgliste, więc niektórzy uważają ją nie za terrorystów, a za niezadowolonych z porządku buntowników. Używa jako bezzałogowców broni wyprzedanej po wojnie rewolucyjnej, co sugeruje, że ktoś ją wspiera.

### dic\_word\_heaven\_w\_title

Adres: `dic\_text\_word/00000826:dda0b000`

> Niebiańscy woj.

### dic\_word\_heaven\_w\_00\_0

Adres: `dic\_text\_word/00000826:dda0b001`

> Niebiańscy wojownicy to zwykli żołnierze Wszechgwiezdnego Imperium Ra Val. To ludzie o rozwiniętych genach strategii przetrwania, odpowiadających za zdolności bojowe, pod każdym względem silniejsi od Ziemian.

### dic\_word\_indigo\_c\_title

Adres: `dic\_text\_word/00000826:dda0b003`

> Indigo Chasers

### dic\_word\_indigo\_c\_00\_0

Adres: `dic\_text\_word/00000826:dda0b004`

> Przydomek 31. Samodzielnego Oddziału Sił Federacji Ziemskiej, zwanego też Oddziałem IC. Badał i przechwytywał wrogie siły z kosmosu na skraju Sfery Ziemskiej, a jego barwą było indygo, które podobno odstrasza szkodniki. W czasie wojny rewolucyjnej oddział zniszczył nieznany przeciwnik, a ocaleni ostatecznie odeszli z wojska.

### dic\_word\_divine\_title

Adres: `dic\_text\_word/00000826:dda0b006`

> Kosmyk

### dic\_word\_divine\_00\_0

Adres: `dic\_text\_word/00000826:dda0b007`

> Kosmyk łaski to znak obywatela Wszechgwiezdnego Imperium Ra Val: grzywka, która zmieniła barwę pod wpływem genów strategii przetrwania, odpowiadających za zdolności bojowe. Gdy emocje rosną, kosmyk zaczyna świecić.

### dic\_word\_aad\_ch\_title

Adres: `dic\_text\_word/00000826:dda0b009`

> Kanał AAD

### dic\_word\_aad\_ch\_00\_0

Adres: `dic\_text\_word/00000826:dda0b00a`

> Publiczna stacja nadawcza A. Adventu. Nadaje komunikaty rządu i własne, bardzo popularne programy rozrywkowe. W przyszłości chce tworzyć treści na cały świat.

### dic\_word\_astccl\_title

Adres: `dic\_text\_word/006b53c9:0ae0b000`

> Szkoła Techniczna Asticassia

### dic\_word\_astccl\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b000`

> Uczelnia prowadzona przez Grupę Benerit, największy koncern przemysłu mobile suitów. Jest samodzielnym Frontem (sztucznym osiedlem w kosmosie), na którym mieszkają uczniowie. Ma trzy wydziały: pilotażu, mechaniki i strategii zarządzania, a przyjęcie wymaga rekomendacji spółki z Grupy Benerit. W szkole działa Komitet Pojedynków, który nadzoruje pojedynki, sposób rozstrzygania sporów między uczniami.

### dic\_word\_pamet\_title

Adres: `dic\_text\_word/006b53c9:0ba0b002`

> Permet

### dic\_word\_pamet\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b003`

> Pierwiastek w minerałach wydobywanych w całym Układzie Słonecznym. Próbki Permetu dzielą się między sobą informacjami, a na tej właściwości oparto wiele technologii, na których stoi dzisiejszy świat.

### dic\_word\_gundarm\_title

Adres: `dic\_text\_word/006b53c9:0ba0b005`

> GUND-ARM

### dic\_word\_gundarm\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b006`

> Wspólna nazwa mobile suitów z systemem “GUND Format”, wojskową odmianą opartej na Permecie technologii wspomagania ciała “GUND”. Precyzyjniejsze sterowanie pozwalało im przewyższać dotychczasowe maszyny, lecz szkodziły pilotom, więc uznano je za broń nieludzką i zakazano ich budowy i użycia.

### dic\_word\_detastm\_title

Adres: `dic\_text\_word/006b53c9:0ba0b008`

> Burza danych

### dic\_word\_detastm\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b009`

> Szkodliwe zjawisko przy pilotowaniu MS przez “GUND Format”. Pilot i maszyna wymieniają ogromne ilości danych, które wracają do pilota. Obciążenie wywołuje w jego ciele różne objawy, a nawet śmierć.

### dic\_word\_vanadis\_title

Adres: `dic\_text\_word/006b53c9:0ba0b00b`

> Vanadis

### dic\_word\_vanadis\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b00c`

> Instytut, który niegdyś badał “GUND”. Początkowo zajmował się wspomaganiem ludzkiego ciała w kosmosie, lecz by uniknąć wstrzymania badań z braku funduszy, przyjął pomoc producenta mobile suitów Ochs Earth i skierował swą technologię na cele wojskowe. Rada Rozwoju Mobile Suitów uznała to za groźne i w egzekucji siłowej zdławiła instytut, co pociągnęło wiele ofiar.

### dic\_word\_dmncs\_title

Adres: `dic\_text\_word/006b53c9:0ba0b00e`

> Dominicus

### dic\_word\_dmncs\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b00f`

> Pierwotnie oddział specjalny podległy bezpośrednio Radzie Rozwoju Mobile Suitów. Dziś podlega Cathedrze, organizacji kontrolnej strzegącej porządku i etyki w budowie mobile suitów. Dowodzi nim Kenanji Avery, który odznaczył się w incydencie Vanadis.

### dic\_word\_zentradi\_title

Adres: `dic\_text\_word/006b53c9:0ba0b011`

> Zentradi

### dic\_word\_zentradi\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b012`

> Olbrzymia biologiczna broń człekokształtna stworzona przez Protokulturę, międzygwiezdną rasę o wysoko rozwiniętej cywilizacji i nauce z zamierzchłych czasów. Ponad dziesięciometrowi, silni w walce i wytrzymali, nie znali żadnej kultury poza wojną. Po upadku Protokultury przez pokolenia walczyli zgodnie z pierwotnym przeznaczeniem, lecz część z nich, spotkawszy ludzi w pierwszej wojnie międzygwiezdnej, odkryła kulturę i nawiązała kontakty z innymi rasami. Dzięki mikronizacji mogą przybrać rozmiar zwykłego człowieka, a zdarzają się nawet ich małżeństwa z innymi rasami.

### dic\_word\_ulri\_fleet\_title

Adres: `dic\_text\_word/006b53c9:0ba0b014`

> Ultradaleka flota emigracyjna

### dic\_word\_ulri\_fleet\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b015`

> Flota emigracyjna ultradalekiego zasięgu: flota wysłana po pierwszej wojnie międzygwiezdnej w ramach galaktycznego planu kolonizacji. Dziś to floty z okrętami klasy New Macross na czele, przemierzające galaktykę w poszukiwaniu planet do zamieszkania. Każda ma inny skład ras i firm, więc każda ma własny charakter, a nawet własną kulturę i technologię.

### dic\_word\_mr\_ship\_title

Adres: `dic\_text\_word/006b53c9:0ba0b017`

> Statek emigracyjny

### dic\_word\_mr\_ship\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b018`

> Okręt mieszkalny floty emigracyjnej ultradalekiego zasięgu. We flotach klasy New Macross znane są statki z kopułą nad osiedlem, które wraz z transformowalnymi kosmicznymi lotniskowcami szturmowymi stealth klasy Battle tworzą flotę.

### dic\_word\_linn\_m\_title

Adres: `dic\_text\_word/006b53c9:0ba0b01a`

> Lynn Minmay

### dic\_word\_linn\_m\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b01b`

> Ziemska piosenkarka-idolka, która w pierwszej wojnie międzygwiezdnej zakończyła wojnę śpiewem. Taktykę przebijania się przez flotę wroga zdezorientowaną jej śpiewem nazwano Atakiem Minmay. Po wojnie wyruszyła w galaktykę na wielkim statku emigracyjnym Megaroad-01; jej losy są od tamtej pory nieznane.

### dic\_word\_fb\_title

Adres: `dic\_text\_word/006b53c9:0ba0b01d`

> Fire Bomber

### dic\_word\_fb\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b01e`

> Zespół rockowy z floty Macross 7. Skład: Basara Nekki (gitara i wokal), Mylene Flare Jenius (bas i wokal), Ray Lovelock (klawisze) i Veffidas Feaze (perkusja). W konflikcie Varauta Basara wylatywał na pole bitwy i śpiewał nawet wrogom, Protodevilnom. Energia ich piosenek walnie przyczyniła się do zakończenia konfliktu.

### dic\_word\_sheryl\_n\_title

Adres: `dic\_text\_word/006b53c9:0ba0b020`

> Sheryl Nome

### dic\_word\_sheryl\_n\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b021`

> Gwiazda piosenki zwana “Galaktyczną Wróżką”, znana m.in. z floty Macross Frontier. W konflikcie Vajr wraz z Ranką Lee siłą śpiewu ocaliła flotę Frontier przed spiskiem floty Galaxy i atakami tajemniczych kosmicznych istot, Vajr.

### dic\_word\_ranka\_l\_title

Adres: `dic\_text\_word/006b53c9:0ba0b023`

> Ranka Lee

### dic\_word\_ranka\_l\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b024`

> Dziewczyna z floty Macross Frontier, którą nazwano “Kopciuszkiem Superwymiaru”. W konflikcie Vajr wraz z Sheryl Nome siłą śpiewu ocaliła flotę Frontier przed spiskiem floty Galaxy i atakami tajemniczych kosmicznych istot, Vajr.

### dic\_word\_chaos\_title

Adres: `dic\_text\_word/006b53c9:0ba0b026`

> Xaos

### dic\_word\_chaos\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b027`

> Międzygwiezdny konglomerat, który stworzył taktyczną jednostkę muzyczną Walkure. Początkowo firma technologii fold, w ciągu ostatnich dziesięciu lat szybko urosła i przejęła wiele branż, w tym rozrywkę i wojsko. Klucz Delta należy do oddziału Xaos Ragna z siedzibą na planecie Ragna w Gromadzie Kulistej Brisingr. Podobno Lady M, związana z Xaos, odegrała dużą rolę w powstaniu Walkure i Klucza Delta, lecz jej tożsamość jest tajemnicą.

### dic\_word\_misakioku\_title

Adres: `dic\_text\_word/006b53c9:0ba0b029`

> Misakioku

### dic\_word\_misakioku\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b02a`

> Potoczna nazwa Zarządu Dawnej Dzielnicy Tsuguno. Przedwojenne obserwatorium radiowe w mieście Nigashio, założone podobno przez Michiyukiego Ashiharę. Kiedyś Otaki Factory instalowała tu sprzęt łączności. By zbadać odebrany tu tajemniczy sygnał, wysłano Mei Kamino.

### dic\_word\_naratake\_title

Adres: `dic\_text\_word/006b53c9:0ba0b02c`

> Naratake

### dic\_word\_naratake\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b02d`

> SI wspomagająca komunikację, stworzona przez Yuna Arikawę. Instaluje się ją na komputerze lub telefonie; po prostym poleceniu sama zbiera i przetwarza wszelkie dane. Ma coś na kształt osobowości, a napędza SI Pelopsa II, partnera Mei Kamino, i Jet Jaguara. Przez ograniczony czas można ją pobrać za darmo z oficjalnej strony Otaki Factory.

### dic\_word\_kamimusi\_title

Adres: `dic\_text\_word/006b53c9:0ba0b02f`

> Kamimushi

### dic\_word\_kamimusi\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b030`

> Pseudonim osoby, z którą czatuje Yun Arikawa. Jej tożsamość jest nieznana, ale ma dość rozumu i wiedzy, by rozmawiać z Yunem jak równy z równym.

### dic\_word\_kamimusi\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b031`

> Później wyszło na jaw, że to Mei Kamino.

### dic\_word\_rd\_title

Adres: `dic\_text\_word/006b53c9:0ba0b032`

> Pył

### dic\_word\_rd\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b033`

> Czerwony Pył to czerwona substancja znaleziona w ciałach kaiju. Pojawia się w powietrzu i wodzie wraz z kaiju i barwi niebo oraz morze na czerwono. To skupisko cząsteczek o złożonej budowie, podejrzewane o związek z kaiju, lecz nic pewnego o nim nie wiadomo.

### dic\_word\_rd\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b034`

> Później okazało się, że to Archetyp w fazie 1 z 13.

### dic\_word\_arche\_t\_title

Adres: `dic\_text\_word/006b53c9:0ba0b035`

> Archetyp

### dic\_word\_arche\_t\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b036`

> Nowy materiał, którego nie wyjaśniają znane prawa fizyki. Jest lekki i wytrzymały, a czasem sam się regeneruje. Potrafi więzić światło i wzmacniać uwięzioną energię, więc jego działanie wykracza poza zasadę zachowania energii. Dotąd istniał tylko w symulacjach, lecz doktor Li ogłosiła jego istnienie w wykładzie w Dubaju.

### dic\_word\_arche\_t\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b037`

> Ma 13 faz. Faza 13 działa jak katalizator, przemieniając inne formy Archetypu; nazywa się ją “Orthogonal Diagonalizer”.

### dic\_word\_ashihara\_m\_title

Adres: `dic\_text\_word/006b53c9:0be0b000`

> Michiyuki Ashihara

### dic\_word\_ashihara\_m\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b001`

> Założyciel Misakioku. Kluczowa postać badań nad Archetypem, lecz owiana tajemnicą. Pozostawił wiele zagadkowych prac i podobno przewidywał przyszłość.

### dic\_word\_ashihara\_m\_00\_1

Adres: `dic\_text\_word/006b53c9:0be0b002`

> Około 80 lat temu, badając rozległy czerwony zakwit, odkrył nowy gatunek meduzy, a w jej ciele Archetyp. Potem zbudował Nadwymiarowy Kalkulator oparty na refrakcji czasu i, prowadząc badania nad Archetypem, szukał podobno sposobu na uniknięcie przyszłej “Katastrofy”.

### dic\_word\_ashihara\_c\_title

Adres: `dic\_text\_word/006b53c9:0be0b003`

> Kaskada Ashihary

### dic\_word\_ashihara\_c\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b004`

> Teoria wyjaśniająca wzmacnianie energii przez Archetyp. Tłumaczy obejście zasady zachowania energii zjawiskiem cofania się czasu w ośrodku. Do wniosku, który doktor Li i jej zespół wyprowadzili przez długie lata z prac Michiyukiego Ashihary, Mei Kamino doszła bez żadnych wskazówek w bardzo krótkim czasie.

### dic\_word\_salunga\_title

Adres: `dic\_text\_word/006b53c9:0be0b006`

> Salunga

### dic\_word\_salunga\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b007`

> Kaiju, który zaatakował ośrodek badań nad Archetypem w Indiach. Dwunożny, bardzo zwinny, potrafi sterować Czerwonym Pyłem. Prototyp Orthogonal Diagonalizera stworzony przez BB na chwilę go unieruchomił, lecz kaiju się odrodził i ruszył na Punkt Osobliwy “Shiva” pod ośrodkiem.

### dic\_word\_salunga\_00\_1

Adres: `dic\_text\_word/006b53c9:0be0b008`

> Gdy Orthogonal Diagonalizer zadziałał w pełni, kaiju znieruchomiał, a Czerwony Pył zniknął.

