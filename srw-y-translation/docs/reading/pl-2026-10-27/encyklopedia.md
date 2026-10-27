# Encyklopedia SRW Y — teksty źródłowe

Wszystkie wpisy czterech tabel `dic_text_*` (podstawka i DLC), w kolejności wierszy
źródłowych tabel — osobno dla każdej tabeli, bez układania chronologii gry.
Każdy wpis ma **klucz Shared Data**, adres wiersza S6 oraz tekst JP i EN.
To są dane źródłowe, nie polskie tłumaczenie: `PL:` pozostaje jawnie oznaczone jako brak.

## Skąd pochodzą i dlaczego nie są przypisane

Teksty pochodzą z tabel lokalizacyjnych w odzyskanych bundlach gry.
Rekordy właścicielskie (która postać/mech dostaje który wariant opisu) leżą w 11 assetach
`*DictionaryEntryTable*` wskazanych przez katalog Addressables — nie ma ich w żadnej
z dotychczasowych paczek źródłowych, więc **nie wolno łączyć opisu z postacią po
podobieństwie klucza ani po nazwie**. Poniższy indeks jest kompletny co do tekstu,
ale nie jest przypisaniem biografii przy pierwszym wystąpieniu.

Brakujące assety źródłowe: **11** (rozmiary z listingu właściciela).

| asset | bundle | rozmiar (B) |
|---|---|---:|
| PilotDictionaryEntryTable | `285818855b5de73d830691acc66152df.bundle` | 14394 |
| PilotDictionaryEntryTable\_D1 | `f623b6c79ecfcad1039e29cce87e8373.bundle` | 2617 |
| PilotDictionaryEntryTable\_D2 | `29eda1d3638745a1e3e0805db5933b86.bundle` | 2376 |
| PilotDictionaryEntryTable\_D3 | `8da124fa5a1a155373e562aed4ad403d.bundle` | 5315 |
| PilotDictionaryEntryTable\_D4 | `dfc36f738dca6ee278a43abf034fb04b.bundle` | 4872 |
| RobotDictionaryEntryTable | `a1537bb970d7f23aec670f2f54ff616b.bundle` | 11334 |
| RobotDictionaryEntryTable\_D1 | `37540e8d50756baf681c32a7eba5fdc1.bundle` | 2325 |
| RobotDictionaryEntryTable\_D2 | `7c18bc903c6f67a6a59ba8d807c22f2a.bundle` | 2340 |
| RobotDictionaryEntryTable\_D3 | `a78e44ccb19568678e44b9706e5982db.bundle` | 4086 |
| RobotDictionaryEntryTable\_D4 | `50fa37a7a150b36b8cce0103ad6a5ff3.bundle` | 6294 |
| WordDictionaryEntryTable | `9e46587dfa2b6e15792a39f4d40519ed.bundle` | 2508 |

## Zmierzone zbieżności dokładnych ID (badawcze, NIE powiązanie własności)

Klucz `dic_pilot_X_00_0` zawiera człon `X`. Poniżej policzono, ile takich członów
jest **dokładnie równe** jakiemuś ID w rekordach gry. Równość nie dowodzi,
że wpis dotyczy tej postaci — dlatego czytanki nadal mają jawny brak powiązania.

- `dic\_text\_name`: grup 29, bez dokładnego ID 2; pola: defaultReferenceId=2, ipnameId=27, listAwakeData=1, listGlobalFlag=1, listHaveRobotSkillData=2, listIPTitleData=23, listRobotBaseData=2, listSpecialMoveData=1, robotimageID=2
- `dic\_text\_pilot`: grup 427, bez dokładnego ID 16; pola: defaultReferenceId=373, facialId=173, listAwakeData=6, listFacialChangeSettingData=11, listFacialSettingData=399, listHavePilotSkillData=110, listHaveRobotSkillData=1, listHaveSpiritCommandData=165, listKakeaiData=98, listPilotBaseData=175, listRobotBaseData=1, listShotdownMessageData=96, robotimageID=1
- `dic\_text\_robot`: grup 297, bez dokładnego ID 29; pola: defaultReferenceId=261, facialId=4, ipnameId=2, listArmorPurgeData=1, listAwakeData=5, listFacialSettingData=4, listGlobalFlag=3, listHavePilotSkillData=4, listHaveRobotSkillData=195, listHaveSpiritCommandData=4, listIPTitleData=2, listKakeaiData=4, listMapTransformationData=6, listPilotBaseData=4, listRetrofitData=4, listRobotBaseData=264, listShotdownMessageData=1, listSpecialMoveData=5, robotimageID=268
- `dic\_text\_word`: grup 78, bez dokładnego ID 78; pola: brak

## Postacie — biografie

### dic\_pilot\_AKIRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8b60b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8b60b000\]
> JP (źródło tłumaczenia): 　臨海学園のサッカー部キャプテンを務めるスポーツ少年。 ⏎ 　ムートロンを研究していた父・一郎とムー帝国の皇女レムリアとの間に生まれ、ムー帝国の守護神であるライディーンにフェードインする事を運命づけられる。 ⏎ 　悪魔世紀の到来を防ぐため、ライディーンで妖魔帝国と戦う。 ⏎ 　熱血型の正義漢で性格も明るく、自らの宿命に負ける事のない強さと絶望的な状況にもひるまない勇気を持っている。 ⏎ 　しかし、生きていた母・レムリアへの想いから冷静さを欠く事もあった。
> EN (odniesienie oficjalne, NIE polski): An athletic young man, captain of the Seaside Academy soccer team. ⏎  ⏎ Born from the union of Ichiro, a Mutron researcher, and Princess Lemuria of the Empire of Mu, he is destined to fuse with the guardian deity of Mu—i.e. to Fade In to Reideen. ⏎ To protect the world against the coming of a new Age of Demons, he wields Reideen's power against the Yoma Empire's assaults. ⏎  ⏎ Energetic and hot-blooded, he has the strength of spirit to not falter under the weight of his destiny, and the courage to not flinch in the face of unbeatable odds. ⏎  ⏎ One of the few things to ever shake his poise is the revelation that his beloved mother, Lemuria, was alive.

### dic\_pilot\_MARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b001\]
> JP (źródło tłumaczenia): 　洸の同級生で、臨海学園のアイドル的存在。 ⏎ 　未来工学研究所の東山所長の娘で、性格は明るくおてんば。そのおっちょこちょいぶりを洸によくからかわれていた。 ⏎ 　戦う洸の心の支えとなり、ついには洸の力になりたい一心でコープランダー隊に入り、ブルーガーでライディーンを援護した。
> EN (odniesienie oficjalne, NIE polski): Akira's classmate and the idol of Seaside Academy. She is the daughter of Chief Higashiyama from the Future Engineering Research Institute, and has a bright, tomboyish personality. Her clumsiness often gets her teased by Akira.  ⏎  ⏎ She is one of the pillars that supports Akira's heart in his fight and, wishing to fight by his side, she joins the Co-oplanders and pilots the Bluegar to aid Reideen.

### dic\_pilot\_REIASUKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b003\]
> JP (źródło tłumaczenia): 　コープランダー隊の隊員で、超能力を持つ少女。 ⏎ 　鋭い霊感を持ち、ライディーンや化石獣を察知する事が出来る。 ⏎ 　かつては神宮寺力と共にブルーガーに乗り、ライディーンの戦いをサポートしていたが、洸の母・ひびき玲子の所在をつかむべく、ひびき一郎達と共にチベットへと向かった。 ⏎ 　コープランダー隊に入隊する以前は、暴走族に加わっていた時期がある他、シスターとして修道院に在籍していた過去も持つ。
> EN (odniesienie oficjalne, NIE polski): A girl with psychic powers who is a member of the Co-oplanders. With her sharp psychic senses she is able to pinpoint the locations of Reideen and any Fossil Beasts.  ⏎  ⏎ Though at first she rode on the Bluegar along with Chikara Shinguji to support Reideen, she later joined Ichiro Hibiki on his quest to Tibet to locate Akira's mother, Reiko Hibiki.  ⏎  ⏎ Before joining the Co-oplanders she spent some time as a member of a motorcycle gang, as well as a period as a nun in a nunnery.

### dic\_pilot\_SARU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b005\]
> JP (źródło tłumaczenia): 　ムトロポリスで技術開発を担当する少年。 ⏎ 　天才的な頭脳の持ち主で、メカの開発や解析を専門にしている。 ⏎ 　ムートロン研究にも携わり、ライディーンを解析する中でその秘められた力や武器等を発見した。 ⏎ 　コープランダー隊の一員として、ブルーガーに搭乗する事もあった。
> EN (odniesienie oficjalne, NIE polski): A young man in charge of technological development in Mutropolis. He is a genius, with a special talent for creating and analyzing robots.  ⏎  ⏎ His involvement with mutron research allowed him to analyze Reideen, discovering various hidden powers and weapons within the machine.  ⏎  ⏎ As a member of the Co-oplanders, he also helped crew the Bluegar.

### dic\_pilot\_HIGASHI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b007\]
> JP (źródło tłumaczenia): 　未来工学研究所の所長で、桜野マリの父。 ⏎ 　妖魔帝国の侵攻に対抗して、科学要塞ムトロポリスを建設。その指揮を執るかたわら、ライディーンをバックアップするため、コープランダー隊を結成した。
> EN (odniesienie oficjalne, NIE polski): The head of the Future Engineering Research Institute, and father of Mari Sakurano. He built Mutropolis, a scientific fortress, in response to the invasion of the Yoma Empire. ⏎  ⏎ While acting as commander of Mutropolis, he also formed the Co-oplanders to aid Reideen.

### dic\_pilot\_KYUZO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b009\]
> JP (źródło tłumaczenia): 　考古学の博士で、洸の祖父。 ⏎ 　ムー大陸の古い記録から、悪魔の復活を予想していた。 ⏎ 　チベットで発見した古代ムー文明の粘土板を解読し、その歴史を紐解いた。
> EN (odniesienie oficjalne, NIE polski): A professor of archeology and Akira's grandfather. He predicted the coming of the Yoma after reading ancient records from the continent of Mu.  ⏎  ⏎ While in Tibet he deciphered tablets from the ancient Mu culture, unraveling the secrets of their history.

### dic\_pilot\_REIKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b00b\]
> JP (źródło tłumaczenia): 　洸の母で古代ムー帝国の皇女。 ⏎ 　ムー帝国での名前はレムリア。 ⏎ 　１万２０００年前、遠い未来に復活する妖魔帝国の野望を阻止するため、眠りについた。 ⏎ 　現代に目覚め、ひびき一郎と結婚して洸を出産。その後、ムー帝国の秘宝「ラ・ムーの星」を探すために洸の前から姿を消した。 ⏎ 　そのため洸は、母が生きている事を知らなかった。
> EN (odniesienie oficjalne, NIE polski): Akira's mother and empress of the ancient Mu Empire. In the Mu Empire her name was Lemuria.  ⏎  ⏎ 12,000 years ago she put herself in a suspended sleep to stop the ambitions of the revived Yoma Empire in the far future.  ⏎  ⏎ She reawakened in the modern day, married Ichiro Hibiki and gave birth to Akira. Afterwards, she vanished from Akira's life as she went in search of the Star of Ra Mu, the Mu Empire's sacred treasure. Due to this, Akira was left unaware that his mother was still alive.

### dic\_pilot\_REIKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b00c\]
> JP (źródło tłumaczenia): 　妖魔帝国との最終決戦が迫る中、洸を助けるために現れる。 ⏎ 　妖魔大帝バラオとの戦いでは、その生命と引き換えに「ラ・ムーの星」を発動させ、洸と人類を勝利に導いた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She returns to Akira right before the final battle with the Yoma Empire.  ⏎  ⏎ In the final fight against Yoma Emperor Barao she offers her own life in exchange for activating the Star of Ra Mu, which guides Akira and all of mankind to victory.

### dic\_pilot\_ICHIRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b00d\]
> JP (źródło tłumaczenia): 　洸の父で考古学者。 ⏎ 　ムートロンの探索中、妖魔帝国によって石化されてしまう。 ⏎ 　シャーキンが倒れた後、石化から解放されて洸と無事再会を果たす。 ⏎ 　その後、行方不明の妻・玲子を探すため、久造と麗と共にチベットへと旅立った。
> EN (odniesienie oficjalne, NIE polski): Akira's father and an archaeologist. While researching mutron energy, he was turned to stone by the Yoma Empire. However, he was released and safely reunited with Akira when Sharkin was defeated.  ⏎  ⏎ Afterwards, he travels to Tibet with Kyuzo and Rei in search of his missing wife, Reiko.

### dic\_pilot\_ICHIRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b00e\]
> JP (źródło tłumaczenia): 　妖魔帝国との最終決戦が迫る中、日本に帰国し、玲子とも再会を果たす。 ⏎ 　最後の戦いの後、玲子を失った洸を父として励ました。
> EN (odniesienie oficjalne, NIE polski):  ⏎ With the final battle with the Yoma Empire looming, he returns to Japan and reunites with Reiko.  ⏎  ⏎ After the final battle, he comforts his son Akira, who is struggling with the loss of Reiko.

### dic\_pilot\_BARAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b00f\]
> JP (źródło tłumaczenia): 　妖魔帝国の支配者。 ⏎ 　１万２０００年の間、石像に封印されていたが、妖魔帝国最高司令官プリンス・シャーキンの生命を懸けた祈りによって復活を遂げた。 ⏎ 　悪魔世紀を実現するため、ムートロンを手に入れようとライディーンに幾度となく刺客を送る。 ⏎ 　ライディーンを遥かに凌ぐ巨体の持ち主で、下半身は妖魔島に埋もれている。
> EN (odniesienie oficjalne, NIE polski): The ruler of the Yoma Empire. ⏎  ⏎ He was sealed away in a statue for 12,000 years but was freed thanks to the prayers and life Prince Sharkin, commander of the Yoma Empire, offered up to him.  ⏎  ⏎ He desires mutron energy to usher in a new Age of Demons, so he sends countless assassins to destroy Reideen. He himself is far more massive than even Reideen, but his lower half is buried in Yoma Island.

### dic\_pilot\_BARAO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b010\]
> JP (źródło tłumaczenia): 　全ての配下を失った後、その全魔力を使って天変地異を引き起こし、ムトロポリスへ進撃を開始した。 ⏎ 　ライディーンを寄せ付けないほどの圧倒的な力を見せるが、最期はラ・ムーの星によって巨大化したライディーンの前に敗れ去った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Once all his underlings are crushed, he uses the full extent of his powers to bring about cataclysms and directly attack Mutropolis.  ⏎  ⏎ Though at first even Reideen couldn't keep up with his overwhelming power, he is ultimately defeated when Reideen is made gigantic thanks to the Star of Ra Mu.

### dic\_pilot\_BEROS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c20b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b011\]
> JP (źródło tłumaczenia): 　妖魔帝国の祭祀長。 ⏎ 　呪文を唱え、魔像から発せられる光線を利用して化石獣を生み出す。 ⏎ 　配下に複数の神官を抱えている。
> EN (odniesienie oficjalne, NIE polski): The master of rituals for the Yoma Empire. ⏎  ⏎ By chanting incantations and harnessing the light rays of an evil statue he is able to create Fossil Beasts. He has countless priests under his command.

### dic\_pilot\_BEROS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c20b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c20b012\]
> JP (źródło tłumaczenia): 　妖魔大帝バラオが復活した際、そこで生じた地割れに吞み込まれていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He was swallowed up by the earthquakes that heralded the awakening of Yoma Emperor Barao.

### dic\_pilot\_HYOMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b000\]
> JP (źródło tłumaczenia): 　バトルチームのリーダーで、１号機・バトルジェットのパイロットとコン・バトラーＶのメインパイロットを務める。 ⏎ 　両親を事故で失い、太陽学園という孤児院で育つ。 ⏎ 　オートバイの運転が得意でケンカっ早く激しい気性で、戦闘には天才的な才能を持っている。 ⏎ 　明るく単純であるが、「強きをくじき、弱きを助ける」の見本のような性格であり、ピンチに対しても諦めない闘志を持つ。しかし、女性に対しては全く奥手でちずるのアプローチになかなか反応しなかった。 ⏎ 　が、キャンベル星人との戦いが終わった後は気持ちを通わせ合うようになった。 ⏎ 　なお、その両腕は、宿敵ガルーダとの生身の戦いで撃たれた怪我により、高性能の義手を取り付けている。
> EN (odniesienie oficjalne, NIE polski): The leader of the Battle Team. He is the pilot of the Unit 1, the Battlejet, and the main pilot of Combattler V. ⏎  ⏎ Having lost his parents as a child, he grew up at the "Sunny School" orphanage. ⏎  ⏎ He is a talented biker with a very short fuse, but his fighting skills are undeniable.  ⏎  ⏎ His motto is "Help the weak and crush the strong". When faced with danger, he would rather die than give up the fight. However, he has a major shortcoming: he is incredibly dense when it comes to matters of the heart, and finds himself unable to fully understand his feelings for Chizuru until after the end of the war against the Campbellians. ⏎  ⏎ His arms were severely injured in combat against his archenemy Garuda, and had to be replaced with high-performance artificial limbs.

### dic\_pilot\_JUZO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b002\]
> JP (źródło tłumaczenia): 　バトルチームの一員で、２号機・バトルクラッシャーのパイロット。 ⏎ 　ニヒルでクールな性格で口も悪いが、関西弁で喋るため、あまり嫌味のない人物。 ⏎ 　豹馬とは時に意見をぶつけあい、殴りあいのケンカをすることもあるが、心の中では互いに仲間と認めあっている。 ⏎ 　８歳で大会に優勝する程の天才的な射撃の腕前を持ち、その力でチームの危機を何度も救ってきた。コン・バトラーＶでも射撃武器の制御を担当している。
> EN (odniesienie oficjalne, NIE polski): One of the members of the Battle Team. He is the pilot of Unit 2, the Battlecrasher. ⏎  ⏎ Calm and aloof, he always has a snarky remark for any given situation, though his Kansai accent makes him hard to really hate. ⏎  ⏎ He has a tendency to clash with Hyoma, both verbally and at times physically, but deep down they both consider each other irreplaceable comrades. ⏎  ⏎ He is a sharpshooting prodigy, winning tournaments since the age of 8; his skills saved the Battle Team on multiple occasions. He is also in charge of controlling Combattler V's firing systems.

### dic\_pilot\_DAISK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b004\]
> JP (źródło tłumaczenia): 　バトルチームの一員で、３号機・バトルタンクのパイロット。 ⏎ 　おっとりとしていて、気は優しくて力持ちタイプ。 ⏎ 　九州出身で漫画家を志望し、柔道の達人でもある。
> EN (odniesienie oficjalne, NIE polski): One of the members of the Battle Team. He is the pilot of Unit 3, the Battletank. ⏎  ⏎ He is a gentle giant: big, strong, and with a kind heart. ⏎  ⏎ A highly skilled judo practitioner born and raised in Kyushu, his dream is to become a professional manga artist.

### dic\_pilot\_CHZUR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b006\]
> JP (źródło tłumaczenia): 　バトルチームの紅一点で、４号機・バトルマリンのパイロット。 ⏎ 　コン・バトラーＶの開発者・南原博士の孫娘であり、チームのアイドル的存在。 ⏎ 　海洋学・医学・ロボット工学に通じている才女で、その他にもピアノ・水泳・体操等の特技を持つ。心優しい性格であるが、おてんばな所も持つ。 ⏎ 　豹馬に想いを寄せ、身を呈して彼を守ろうとする事もあった。普段は素直になれないため、なかなかその仲は進展しなかったが、キャンベル星人との戦いが終わった後、その想いは届き、心通じ合うようになった。
> EN (odniesienie oficjalne, NIE polski): One of the members of the Battle Team. She is the pilot of Unit 4, the Battlemarine. ⏎  ⏎ She is the granddaughter of Dr. Nambara, the developer of Combattler V, and the only girl of the team. ⏎  ⏎ She is an expert in oceanology, medical science, and robotics; additionally, she is also talented with the piano, swimming and gymnastics. Kind and compassionate, she can be a bit of a tomboy at times. ⏎  ⏎ She fell deeply in love with Hyoma during Combattler's struggles, and she's shown she is willing to give her life to protect him. Struggling at times to be honest with herself, she was unable to tell him how she felt until after the end of the war against the Campbellians.

### dic\_pilot\_KOSKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b008\]
> JP (źródło tłumaczenia): 　バトルチームの最年少メンバーで、５号機・バトルクラフトのパイロット。 ⏎ 　小学生でありながらアメリカの大学に留学していた天才少年で様々な名（迷？）発明をしていた。 ⏎ 　しかし、両親の住んでいる北海道が敵の攻撃のターゲットになった時は冷静さを失う等、子供としての一面も併せ持つ。 ⏎ 　なお、弱点としておねしょの癖がある。 ⏎ 　コン・バトラーＶでの戦闘中は敵を分析して、メインパイロットの豹馬に様々な助言を与える。
> EN (odniesienie oficjalne, NIE polski): The youngest member of the Battle Team. He is the pilot of Unit 5, the Battlecraft. ⏎  ⏎ Though he is a grade schooler, this prodigy has already attended a famous American university, and has multiple inventions to his name. ⏎  ⏎ While he is usually very mature, he is still fundamentally a child: when the enemy launched a raid in Hokkaido, where his parents live, he lost his composure and broke down crying. ⏎  ⏎ Additionally, he still wets his bed from time to time. ⏎  ⏎ During combat, he is tasked with analyzing Combattler's opponent, providing the main pilot with vital information.

### dic\_pilot\_YOTYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b00a\]
> JP (źródło tłumaczenia): 　南原博士亡き後、南原コネクションの所長を務める科学者。 ⏎ 　南原博士とは昔からの親友であった。 ⏎ 　博士が最初に彼をコネクションに呼び、バトルチームの指揮を頼んだ時は人類など滅べばいいと悲観的な考えを示し、申し出を拒否する。しかし、身を呈して自分を救った南原博士の姿を見て、愛する自然のために戦う事を決意する。 ⏎ 　性格は豪快で口は悪いが、どんな窮地でも諦めずに打開策を探す不屈の人物。 ⏎ 　酒が大好きで、普段からウイスキーのビンを持ち歩いている。
> EN (odniesienie oficjalne, NIE polski): The scientist in charge of the Nambara Connection after the death of Dr. Nambara, his longtime friend. ⏎  ⏎ When Dr. Nambara first asked him to lead the Battle Team, he firmly refused, claiming that mankind could go to hell for all he cared. But after Dr. Nambara gave his life to protect Yotsuya, he decided that he would fight, for the sake of his beloved Mother Nature. ⏎  ⏎ He is an energetic fellow, blunt and plain-spoken. When faced with a problem, he will relentlessly look for a solution. ⏎  ⏎ He is quite fond of his booze, and always carries a flask of whisky on his person.

### dic\_pilot\_ROPET\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b00c\]
> JP (źródło tłumaczenia): 　南原博士がコンバイン用に開発した脳波測定用ロボット。 ⏎ 　バトルチームの５人の脳波を測定し、身体各所についたメーターが揃った時、すなわち５人の脳波の同調が確認されてコンバインは初めて可能となる。 ⏎ 　人間と同じような感情を持っており、敵の送り込んだ美少女ロボットに恋をした事もあった。
> EN (odniesienie oficjalne, NIE polski): The brainwave-measuring robot developed by Dr. Nambara to perform the Combine sequence. ⏎  ⏎ Ropet measures the brainwaves of each member of the Battle Team; only when the five gauges on his body are maxed out—that is, when the brainwaves of the Battle Team are aligned—can the combination sequence be initiated. ⏎  ⏎ Despite his appearance, Ropet is capable of the same range of emotions of a human; for example, he once fell in love with a robot girl (who was, alas, a trap sent by the Campbellians).

### dic\_pilot\_GALDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b00e\]
> JP (źródło tłumaczenia): 　キャンベル星の大将軍。 ⏎ 　敬愛する母・オレアナの命令に従い、地球侵略の戦闘指揮を執る。 ⏎ 　普段は青年の姿をしているが、鳥人の姿へ変身する事も可能。 ⏎ 　冷徹な性格をしており、地球人を虫けらのように見下しているが、誇り高き精神の持ち主でもあり、自らの認めた者には敬意を払う。 ⏎ 　多くの配下を倒してきた豹馬とコン・バトラーＶは好敵手として捉えており、様々な作戦を講じるも敗北を重ねてきた。
> EN (odniesienie oficjalne, NIE polski): The general of the Campbellian forces. ⏎  ⏎ He leads the invasion of Earth under orders of his beloved mother, Oleana. ⏎  ⏎ Though he usually takes the form of a young man, he can also transform into a bird-like form. ⏎  ⏎ Cold and ruthless, he looks down on the Earthlings as if they were insects; however, he is a proud warrior and will show respect to those he acknowledges as strong. ⏎  ⏎ Hyoma and Combattler V have defeated many of his subordinates; for this reason, he has appointed them as his nemesis, devising many plans to take them down.

### dic\_pilot\_GALDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8c60b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b00f\]
> JP (źródło tłumaczenia): 　コン・バトラーＶとの激闘の中、偶然から自分自身がアンドロイドであるという事実を知る。度重なる失敗からオレアナに処分されそうになるが、自らの誇りを懸けて巨大戦闘ロボット・ビッグガルーダに乗り込む。 ⏎ 　偽りの母であったオレアナを討ち、コン・バトラーＶに一騎打ちを申し込むが、激闘の末に敗北。自らを愛してくれたアンドロイドのミーアと共に爆発の中に消えていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During a fierce battle with Combattler V, he accidentally discovers that he is an android. Before Oleana can punish him for his repeated failures, he gambles his pride on the giant fighting robot Big Garuda. ⏎  ⏎ After killing Oleana, who had been lying about being his mother, he challenges Combattler V to mortal combat. He is ultimately defeated, disappearing in a blazing explosion alongside Mia, the android who loved him.

### dic\_pilot\_CAMIYU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8c60b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8c60b010\]
> JP (źródło tłumaczenia): 　エゥーゴに参加するニュータイプの少年で、Ζガンダムのパイロット。１７歳。 ⏎ 　元もとはスペースコロニー「グリーン・ノア」のハイスクールに通っていた、やや多感ながらも普通の少年である。カミーユという女性的な名前にコンプレックスを抱いており、ホモ・アビス（簡易型グライダー）や空手といった男性的な趣味に傾倒していた。両親が地球連邦軍の技術将校という環境も手伝い、メカニックに精通しており、Ｊｒ．モビルスーツ大会では優勝するほどの腕前であった。 ⏎ 　しかし、その名前をジェリドに中傷され、彼といざこざを起こした事からティターンズと反目。なりゆきでクワトロらのガンダムＭｋ－Ⅱ強奪計画を手伝い、そのままエゥーゴに参加する。 ⏎ 　戦いの中でニュータイプとしての能力に目覚め、次第にエゥーゴのエースパイロットとして活躍するようになった。 ⏎ 　当初は単純にティターンズへの反感から戦っていたものの、クワトロやアムロといった大人達、そしてフォウやロザミアといった女性達との出会いと別れを経た事で、人間的に大きく成長する。そして、戦争を終わらせる道を模索しつつ、自らの意識を宇宙へと広げていった。 ⏎ 　テレビ版のラストでは、倒したシロッコに精神を道連れにされ、心に深い傷を負ったが、劇場版のラストではそれを跳ね除け、ファと互いの無事と身体を確かめ合った。
> EN (odniesienie oficjalne, NIE polski): A teenage Newtype and pilot of the Zeta Gundam with the AEUG. 17 years old. ⏎  ⏎ He started out as a somewhat sensitive but otherwise ordinary student going to high school on the space colony Green Noa. He had a complex about his name, Kamille, being traditionally a girl's name, so he threw himself into more "masculine" pursuits like flying homoavis (a simple type of glider) and karate. He has a familiarity with mechanics due to his parents (both Earth Federation tech officers), allowing him to win a Junior Mobile Suit Competition. ⏎  ⏎ After Jerid Messa mocked his name, he got into a series of fights and mishaps that radicalized him against the Titans. Over the course of these events, he helped Quattro's team in their theft of the Gundam Mk-II and ended up joining the AEUG. ⏎  ⏎ As he continued fighting for the AEUG, latent Newtype abilities awoke within him, and eventually, he rose to the position of the AEUG's top ace pilot.  ⏎  ⏎ At first he fought out of antipathy for the Titans, but he grew as a person over the course of his encounters with adult figures like Quattro and Amuro and women like Four Murasame and Rosamia Badam. As he sought a way to end the war, his consciousness reached out into space.  ⏎  ⏎ Accounts of his final fate differ: in the TV series finale, he kills Scirocco, only for Scirocco to launch a final mental assault as he dies, essentially "taking Kamille with him" and leaving Kamille with severe mental damage. This was changed in the finale of the movie edition, in which he and Fa both safely found each other.

### dic\_pilot\_FA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b001\]
> JP (źródło tłumaczenia): 　カミーユの幼馴染。１７歳。 ⏎ 　ガンダムＭｋ－Ⅱを強奪したカミーユと知り合いだったという理由から、両親共々バスクに捕らえられていた。ブライトによって助けられた後は、ティターンズへの反抗心とカミーユの側にいるためにエゥーゴに参加し、パイロットに志願する。自らの力量不足に苦悩しつつも、グリプス戦役を戦い抜いた。 ⏎ 　世話焼きな性格をしており、昔からカミーユの生活態度や癖などに注意をしていた。その口うるささに、カミーユは内心で辟易していた模様。その性格のためか、クワトロがアーガマに連れてきた孤児シンタやクムの世話係も彼女の役目となった。 ⏎ 　テレビ版では、最終決戦において最愛のカミーユが精神に異常をきたしたため、戦場を離れて彼の世話と看護に専念していた。しかし劇場版では、お互いの無事を喜び合う姿が見られた。
> EN (odniesienie oficjalne, NIE polski): Kamille's childhood friend. 17 years old.  ⏎  ⏎ She and her parents were arrested by Bask Om because they were acquainted with Kamille, who had stolen the Gundam Mk-II from the Titans. After Bright rescued her, she volunteered to be a pilot in the A.E.U.G. to fight the Titans and stay by Kamille's side. While she knew she wasn't the best pilot, she still made it through the entire Gryps Conflict alive.  ⏎  ⏎ She was always the type to look after others, and she had particularly kept on Kamille about his attitude and bad habits since they were young children, something which Kamille had no patience for. Because of this, she takes on the role of babysitter for Shinta and Qum, two orphans that Quattro brought on board the Argama.  ⏎  ⏎ In the TV series finale, her beloved Kamille suffers a mental breakdown in the final battle, and she ends up leaving the front lines to be his full-time nurse and caretaker. However, in the movie finale, she and Kamille safely come back together and rejoice.

### dic\_pilot\_EMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b003\]
> JP (źródło tłumaczenia): 　エゥーゴのパイロット。階級は中尉。 ⏎ 　元はティターンズに所属していたが、卑劣な作戦を目の当たりにしてエゥーゴに投降した。 ⏎ 　その高い操縦技術はエゥーゴでも高く評価され、リック・ディアス、ガンダムＭｋ－Ⅱ、スーパーガンダムなどの主力機を任され、それを乗りこなした。 ⏎ 　自らの信念に基づいて行動する強い意志と軍人としての厳しさを持つ。だがその一方で、女性的な優しさも併せ持っている。ヘンケンからのアプローチに対し、いつもつれない態度を取ってはいたが、その実はまんざらでもなかったようである。 ⏎ 　ティターンズとの最終決戦において負傷し、駆けつけたカミーユに後の事を託した後、彼の腕の中で息を引き取った。
> EN (odniesienie oficjalne, NIE polski): A lieutenant junior and pilot for the AEUG. who defected from the Titans after witnessing them carry out atrocities during an operation. Her advanced piloting skills made her an invaluable asset to the AEUG, which resulted in her being assigned key units such as a Rick Dias, a Gundam Mk-II, and the Super Gundam, all of which she mastered. ⏎  ⏎ She possesses ironclad determination to act in accordance with her convictions and the harshness of a soldier, yet also kindness and understanding. She always rebuffed Henken's passes with a frosty shoulder, yet never appeared entirely displeased by them, deep (deep) down. ⏎  ⏎ In the final battle with the Titans, she was mortally wounded and passed away in Kamille's arms after encouraging him to put an end to the war once and for all.

### dic\_pilot\_SHIROKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b005\]
> JP (źródło tłumaczenia): 　巨大輸送船ジュピトリスのキャプテン。 ⏎ 　「木星帰りの男」とも称される。 ⏎ 　優れたニュータイプの資質を持っており、一流のパイロットであると同時にモビルスーツの設計まで手掛ける。 ⏎ 　先を見通す洞察力と戦略眼を兼ね備えるカリスマである一方、自らを天才と認識しており、他人を見下している。 ⏎ 　地球連邦軍のエリート部隊・ティターンズに入隊して以降、次々と戦果を挙げていき、最終的には総帥ジャミトフを暗殺してティターンズの実権を握った。 ⏎ 　戦況が、反地球連邦組織・エゥーゴと旧ジオン軍残党・アクシズとの三つ巴の戦いへと変わりゆく中、アクシズと手を組み暗躍した。 ⏎ 　最終決戦では自らの開発したモビルスーツ、ジ・Oに乗り、カミーユと激戦を繰り広げるが、ウェイブ・ライダーの突撃に機体ごと身体を貫かれた。
> EN (odniesienie oficjalne, NIE polski): Captain of the Jupitris, a massive transport vessel. Known as "the man who returned from Jupiter", he is a gifted Newtype, a skilled pilot, and even a talented Mobile Suit designer. Though he's a charismatic figure with excellent foresight and an eye for tactics, he considers himself a genius and looks down on others. ⏎  ⏎ After joining the Titans, the EFF's elite force, he amassed power over the course of the war until he eventually assassinated the Titans' leader, Jamitov, and took over the group. As the war changed into a three-way conflict between the Titans, the anti-Earth Federation group known as the AEUG, and the remnants of Zeon known as Axis, he secretly allied himself with Axis. ⏎  ⏎ He and his Mobile Suit, The-O, engaged in a fierce fight against Kamille in the final battle of the war, only for he and his MS to be impaled by the Zeta Gundam's Waverider attack.

### dic\_pilot\_YAZAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b007\]
> JP (źródło tłumaczenia): 　ティターンズの士官。当初の階級は中尉だが、後に大尉に昇進する。 ⏎ 　好戦的な性格で、己の力を自在に振るえる戦争を心から楽しんでいる。パイロットとしては抜群の腕を持ち、ギャプランやハンブラビなどの高機動モビルスーツを手足のように操り、アーガマのモビルスーツ隊を何度も苦しめた。 ⏎ 　自分にとって不都合であれば、たとえ上官であってもためらう事なく謀殺する知略と残虐性を持つ。同時に面倒見の良い一面も持ち、ラムサスやダンケルを始めとする部下達からの信頼は厚かった。 ⏎ 　カツやエマの生命を奪った挙句、高笑いすらして見せたその非道さは、カミーユがＺガンダムのバイオセンサーを発動させるきっかけとなった。 ⏎ 　Ｚガンダムに撃墜されて宇宙を漂流し、後にジュドー達によって脱出ポッドを回収される形でスペースコロニー・シャングリラに姿を現す。 ⏎ 　ジュドー達を使いシャングリラに入港したアーガマを襲撃するが、乱暴なやりかたがジュドーの怒りを買い、Ｚガンダムに搭乗したジュドーに返り討ちに遭った。
> EN (odniesienie oficjalne, NIE polski): An officer with the Titans. He initially holds the rank of lieutenant junior grade, but is later promoted to lieutenant. ⏎  ⏎ Yazan is belligerent and enjoys the battlefield because he can fight freely, using his strength as he wishes. He has outstanding piloting skills, operating high-mobility Mobile Suits like the Gaplant and Hambrabi as if they were just extensions of his own body. He has caused the mobile fleet of the Argama much trouble. ⏎  ⏎ He has the brutality and resourcefulness to murder even his own superior officer should they stand in his way. At the same time, he does have a caring side, and he enjoys fierce loyalty from his subordinates Ramsus and Dunkel. ⏎  ⏎ He roars with laughter when he sees Katz and Emma's lives taken, and this cold cruelty is what drives Kamille to activate the Zeta Gundam's Biosensor. ⏎  ⏎ After being shot down by the Zeta Gundam, he drifts through space. Eventually, he appears at the Shangri-La space colony, discovered inside an escape pod collected by Judau and his team. ⏎  ⏎ Yazan attacks the Argama piloted by Judau, which is docked in Shangri-La. His violent methods enrage Judau, who boards the Zeta Gundam and gets his revenge on Yazan.

### dic\_pilot\_ASUT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b009\]
> JP (źródło tłumaczenia): 　アーガマのメカニックチーフ。階級は曹長。 ⏎ 　チーフを務めるだけあって腕は確かで、彼がいる事でアーガマのモビルスーツ隊は常に万全の態勢で戦う事が出来る。 ⏎ 　カミーユの考案したアイデアをアナハイム・エレクトロニクスに送り、Ζガンダムの完成に一役買った影の功労者でもある。 ⏎ 　その腕を見込まれ、後の第二次ネオ・ジオン抗争でもラー・カイラムでメカニックを務めた。
> EN (odniesienie oficjalne, NIE polski): The chief mechanic of the Argama. Rank: Master Sergeant.  ⏎  ⏎ A capable mechanic who kept the Argama's MS team up and running at all times.  ⏎  ⏎ He also played a key role in perfecting the Zeta Gundam when he passed Kamille's design ideas on to Anaheim Electronics.  ⏎  ⏎ Recognized for his skill, he went on to be a mechanic on the Ra Cailum in the Second Neo Zeon War.

### dic\_pilot\_AMRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b00b\]
> JP (źródło tłumaczenia): 　地球連邦軍のロンド・ベルに所属するニュータイプパイロット。階級は大尉。 ⏎ 　一年戦争では、ＲＸ－７８ ガンダムに搭乗し、数々の戦いに参加。ニュータイプとして成長を遂げ、伝説的な戦果を残す。 ⏎ 　だが、戦後はその能力を地球連邦に警戒され、軟禁状態の生活を強いられる。それでもグリプス戦役時には、エゥーゴの支援組織カラバに参加し、ティターンズと戦う。 ⏎ 　第一次ネオ・ジオン抗争後は連邦軍の外郭新興部隊ロンド・ベルに所属。かつての同志であり、宿敵でもあるシャア・アズナブル率いるネオ・ジオン軍と戦った。 ⏎ 　一年戦争当時は内向的でナイーブな少年であったが、戦争を通じて多くの人々と出会い、様々な経験をする中で、人間的にも大きく成長した。 ⏎ 　第二次ネオ・ジオン抗争では、自ら設計・開発に携わったνガンダムでアクシズの地球落下を阻止しようとする。サイコ・フレームの超常的な力により、アクシズの引き上げに成功するものの、その際にシャアと共に行方不明となり、歴史から姿を消した。
> EN (odniesienie oficjalne, NIE polski): A Newtype pilot with the Earth Federation Forces' Londo Bell unit.  ⏎  ⏎ Rank: Lieutenant.  ⏎  ⏎ He piloted the RX-78 Gundam in the One Year War and took part in numerous battles. He manifested as a Newtype during the conflict and left behind a field record which became the stuff of legend.  ⏎  ⏎ After the war, the Federation grew wary of his abilities and kept him under house arrest. When the Gryps Conflict broke out, he joined the AEUG. support organization Karaba and fought against the Titans.  ⏎  ⏎ After the First Neo Zeon War, he joined the newly formed Londo Bell, an autonomous Federation corps, and went on to fight against the Neo Zeon Forces led by Char Aznable—the man who had been both his ally and his arch-rival for a decade and a half.  ⏎  ⏎ At the outset of the One Year War, he was a naive, introverted teenager, but over the course of the various Earth Sphere conflicts, he encountered many people and went through experiences that shaped him into a far more well-rounded individual.  ⏎  ⏎ In the Second Neo Zeon War, he piloted the Nu Gundam, a model he designed and developed personally, to try and stop Neo Zeon from dropping Axis on Earth. He succeeded at forcing Axis back by virtue of a paranormal power exhibited by the Psychoframe, but he and Char both went missing in the incident and, at last, faded into history.

### dic\_pilot\_BURAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b00d\]
> JP (źródło tłumaczenia): 　地球連邦宇宙軍外郭新興部隊ロンド・ベル司令官。階級は大佐。３６歳。 ⏎ 　一年戦争時代にホワイトベースを率いて以降、ガンダムタイプのモビルスーツ搭載母艦の艦長を次々と務め上げ、ニュータイプ部隊の指揮官として知られている。 ⏎ 　その経歴が危険視され、軍の本流からは外されてしまっているものの、政治的な意向を遮断する実直さと豊富な実戦経験から、部下の信頼は厚い。 ⏎ 　第二次ネオ・ジオン抗争ではロンド・ベルを率い、部下であり盟友でもあるアムロ・レイと共にシャアの地球寒冷化作戦を阻止した。
> EN (odniesienie oficjalne, NIE polski): The commander of the Londo Bell, a unit independent of the Earth Federation Space Force. Rank: Captain. Age: 36. ⏎  ⏎ Ever since his time in command of the White Base during the One Year War, he has served as captain of multiple vessels carrying Gundam-type Mobile Suits. He was famous as a commander of Newtype teams.  ⏎  ⏎ His record marked him as dangerous to the military, and so was removed from the main military chain of command, but he had the integrity to eschew political compromises and an abundance of field experience, both of which made him highly trusted by his crew.  ⏎  ⏎ He led the Londo Bell during the Second Neo Zeon War and worked with his subordinate and dear friend Amuro Ray to put a stop to Char's plan to plunge the Earth into a new Ice Age.

### dic\_pilot\_MERAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b00f\]
> JP (źródło tłumaczenia): 　ラー・カイラム副長。階級は中佐。 ⏎ 　冷静沈着な性格で、第二次ネオ・ジオン抗争の頃から、艦長のブライトのサポートを行なってきた。
> EN (odniesienie oficjalne, NIE polski): Executive officer of the Ra Cailum. Holds the rank of commander. ⏎  ⏎ With his calm and collected disposition, he began serving in a support role for Captain Bright in the Second Neo Zeon War.

### dic\_pilot\_CHEAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b011\]
> JP (źródło tłumaczenia): 　地球連邦軍の技術士官。 ⏎ 　アナハイム・エレクトロニクスへ出向し、νガンダムの開発を担当する。上官のアムロに対して好意を抱いており、彼の力になろうとサイコ・フレームの調整に並々ならぬ意欲を燃やす。 ⏎ 　アクシズ攻防戦の最中には、νガンダムの能力向上の足しになるとしてサイコ・フレームのサンプルをアムロに届けようと、中破したリ・ガズィで戦場に出る。そして、ハサウェイとクェスの間に割って入り、α・アジールを撃墜。だが、クェスを殺されて逆上したハサウェイに撃たれて、生命を落とす。
> EN (odniesienie oficjalne, NIE polski): A technical officer in the Earth Federation Forces.  ⏎  ⏎ She transferred temporarily to Anaheim Electronics, where she oversaw development of the Nu Gundam. She had feelings for her commanding officer, Amuro Ray, and showed an extraordinary determination to fine-tune the Psychoframe of the Nu as her way of helping him.  ⏎  ⏎ During the fighting at Axis, she launched in a damaged Re-GZ to deliver a Psychoframe sample to Amuro in hopes of improving the Nu Gundam's performance. She came between Hathaway and Quess and managed to destroy the Alpha Azieru, only to die at the hands of Hathaway, who was furious at seeing Quess killed.

### dic\_pilot\_CHAR\_\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b013\]
> JP (źródło tłumaczenia): 　ネオ・ジオンの総帥。 ⏎ 　本名はキャスバル・レム・ダイクン。ザビ家によって謀殺されたジオン・ズム・ダイクンの忘れ形見である。一年戦争では「赤い彗星」として、その卓越した戦術眼やモビルスーツ操縦で勇名を馳せた。グリプス戦役ではクワトロ・バジーナと名乗り、ティターンズ打倒のために戦ったが、コロニーレーザーをめぐる戦いの中、ハマーンとの一騎討ちを最後に行方をくらませていた。 ⏎ 　しかし、第一次ネオ・ジオン抗争の終結から３年後、新生ネオ・ジオンを率いて再び地球圏へと現れる。地球連邦の圧政に苦しむスペースノイドは、圧倒的な歓喜をもって彼を迎え、多くのコロニーがネオ・ジオンに協力する事となった。 ⏎ 　ネオ・ジオン総帥として政治的な駆け引きや策謀を駆使して、地球連邦に戦いをしかける。だが、その胸中には今もなおララァ・スンが存在し、それゆえにアムロとの１４年越しの決着をつけたいと望む。 ⏎ 　そして、地球から人類を排除するべく地球寒冷化作戦を決行。落下するアクシズを舞台にアムロとの最後の戦いに臨み、戦いの中、サイコ・フレームの光に包まれ、アムロと共に行方不明となる。
> EN (odniesienie oficjalne, NIE polski): Commander of Neo Zeon. ⏎  ⏎ His full name is Char Aznable. His real name was Casval Rem Deikun, the child of the late Zeon Zum Deikun, who was assassinated by the Zabi family. Known as the Red Comet during the One Year War, he was famous for his strategic prowess and superior Mobile Suit piloting skills. In the Gryps Conflict, he used the alias "Quattro Bajeena" and fought to overcome the Titans, but in the struggle over the Colony Laser, he vanished following a one-on-one battle with Haman. ⏎  ⏎ However, he reappeared near Earth as leader of the revived Neo Zeon three years after the First Neo Zeon War. The Spacenoids, who were suffering under the oppressive Earth Federation, welcomed him enthusiastically and many colonies aided with Neo Zeon. ⏎  ⏎ As commander of Neo Zeon, he engaged in political negotiations and pilots in his struggle against the Earth Federation. However, he still had feelings for Lalah Sune and therefore hoped to bring his fourteen-year rivalry with Amuro to a conclusion. ⏎  ⏎ He decided upon military action to cause a nuclear winter that would remove humanity from Earth. The final showdown with Amuro took place on Axis, which was free-falling to Earth. However, they were both bathed in Psychoframe light and disappeared, never to be seen again.

### dic\_pilot\_QUES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b015\]
> JP (źródło tłumaczenia): 　地球連邦軍の参謀次官であるアデナウアーの一人娘。 ⏎ 　奔放な性格で感情の起伏が激しく、人間に対して鋭い見方をする。 ⏎ 　ニュータイプに興味があり、インドで修行をしていた事もある。 ⏎ 　ロンデニオンで出会ったシャアに惹かれ、ネオ・ジオンへと走る。そこで彼女は、ニュータイプとしての能力を覚醒させていき、ヤクト・ドーガに搭乗してシャアの役に立つために戦っていく。 ⏎ 　戦いの中、父アデナウアーをその手にかけるが、本人にははっきりとした自覚はなかった。 ⏎ 　アクシズ攻防戦では巨大モビルアーマー、α・アジールを駆って戦うが、再会したハサウェイをかばう形でチェーンの攻撃を受けて、命を落とす。
> EN (odniesienie oficjalne, NIE polski): The sole daughter to Adenauer, a vice-minister in the Earth Federation Forces. Wild and uninhibited with extreme moods, she views other people harshly. She has an interest in Newtypes and trained in India at one point. ⏎  ⏎ She became smitten with Char after meeting him at Londenion and escapes to Neo Zeon. There she awakens to her Newtype powers, and pilots the Jagd Doga into battle to be of aid to Char. She struck down her father Adenaur in battle, but wasn't fully aware she had even done so. ⏎  ⏎ In the battle against Axis, she piloted the large Mobile Armor Alpha Azieru. She reunited with Hathaway, and took the blow from Chan to defend him, eventually perishing.

### dic\_pilot\_GUNEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b017\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍のパイロット。 ⏎ 　乗機はニュータイプ用モビルスーツのヤクト・ドーガ。 ⏎ 　ナナイ・ミゲルが所長を務めるニュータイプ研究所出身の強化人間である。 ⏎ 　性格は野心的。貪欲なほどに自分の能力を向上させようと考えていて、出世の機会をうかがっている。実際、ニュータイプ的な能力は高く、研究所で強化を受けたメンバーの中で一人だけ、サイコミュ兵器のファンネルを使う事が出来た。 ⏎ 　シャアのもとにきたクェスを本物のニュータイプとして認めて、惹かれていく。 ⏎ 　アクシズ攻防戦では、ロンド・ベルが放った核ミサイルを全て撃ち落とすなど活躍を見せたが、νガンダムに乗ったアムロと戦い、撃墜される。
> EN (odniesienie oficjalne, NIE polski): A Neo Zeon pilot, he pilots the Newtype-specialized Mobile Suit, the Jagd Doga. He is an artificial Newtype hailing from the Newtype Laboratory led by Nanai Miguel. ⏎  ⏎ An ambitious man, he desires to improve his abilities to succeed in life. In reality, he has great Newtype abilities, and is the only artificially enhanced member at the Laboratory who can utilize the Fin Funnel, a Psycommu weapon. ⏎  ⏎ When Quess came to Char's side, Gyunei recognizes her abilities as a true Newtype, and admires them. ⏎  ⏎ In the battle against Axis, he performed spectacularly and destroyed all the nuclear missiles fired by Londo Bell. However, he exchanged blows with the Nu Gundam piloted by Amuro and was destroyed.

### dic\_pilot\_REZN\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ca0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ca0b019\]
> JP (źródło tłumaczenia): 　ネオ・ジオン所属のパイロット。 ⏎ 　ギラ・ドーガ部隊の小隊長を務め、搭乗する機体を青のパーソナルカラーで塗装している。高いモビルスーツ操縦技術を誇り、小細工を嫌い、モビルスーツは白兵戦がメインで運用されるべきだという考えを持っている。 ⏎ 　また、強化人間を嫌悪しており、ギュネイに突っかかる事もあった。 ⏎ 　アクシズ攻防戦ではラー・カイラムを攻撃するが、サイコ・フレームの補助を受けたチェーンが撃つ対空砲火の直撃で戦死する。
> EN (odniesienie oficjalne, NIE polski): A Neo Zeon pilot, and the Geara Doga platoon leader. ⏎  ⏎ Her Mobile Suit is personalized and painted blue. With excellent piloting skills, she detests petty tricks, and believes that MS should be utilized mainly in hand-to-hand combat. She also dislikes artificial Newtypes, and has gotten into fights with Gyunei. ⏎  ⏎ In the battle with Axis, she attacked the Ra Cailum but was in the direct line of fire of Chan's Psycho Frame-enhanced anti-air cannon, and perished.

### dic\_pilot\_NANA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b000\]
> JP (źródło tłumaczenia): 　ネオ・ジオンの戦術士官であり、ニュータイプ研究所の所長。 ⏎ 　戦術士官としては、ルナツー奇襲作戦の指揮を任されるなど、シャアからの信任も厚い。ニュータイプ研究所でもギュネイを育て上げるなど、実績を残している。 ⏎ 　シャアの愛人であり、プライベートでは女性として彼を支える。だが、シャアが連れてきたクェスに対しては不快さを露わにした。
> EN (odniesienie oficjalne, NIE polski): A Neo Zeon tactical officer and head of a Newtype research institute.  ⏎  ⏎ As a tactical officer, she had earned enough trust from Char to be placed in key roles such as commanding the operation to attack Luna II. She also left a solid track record of successes at the Newtype research institute, such as cultivating Gyunei Guss's talent.  ⏎  ⏎ She was Char's lover and supported him in private as well as in her official duties. However, her displeasure was plain to see when Char brought Quess Paraya on board.

### dic\_pilot\_RAIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b002\]
> JP (źródło tłumaczenia): 　ネオ・ジオン艦隊の旗艦レウルーラの艦長。 ⏎ 　シャアがサザビーで出撃した後は指揮を任されるが、総帥であるシャアがモビルスーツで戦場へ出ることを快く思っていない。
> EN (odniesienie oficjalne, NIE polski): Captain of the Neo Zeon forces flagship, the Rewloola. He took command after Char sortied in the Sazabi, and doesn't think well of Char for heading off to battle in a Mobile Suit despite being the Commander.

### dic\_pilot\_KAMRN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b004\]
> JP (źródło tłumaczenia): 　スペースコロニー「ロンデニオン」の会計監査局員。 ⏎ 　かつてはブライトの妻・ミライと親が決めた婚約者の関係だった。 ⏎ 　連邦政府とネオ・ジオンの秘密交渉に立ち会う中、ネオ・ジオンの武装解除が嘘であると疑い、自らの立場が危うくなる事を顧みず、ブライトに協力した。
> EN (odniesienie oficjalne, NIE polski): A member of the space colony Londenion's Audit Bureau. Was formerly engaged to Bright's wife Mirai as per their parents' decision. ⏎  ⏎ Suspected Neo Zeon of lying about their agreement to disarm during their secret talks with the Earth Federation, and consequently aided Bright despite the harm it could bring him and his career.

### dic\_pilot\_DOMON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b006\]
> JP (źródło tłumaczenia): 　コロニー格闘技のチャンピオンにしてネオジャパン代表のガンダムファイター。 ⏎ 　東方不敗マスター・アジアの下で１０年に及ぶ修行の末、キング・オブ・ハートの称号を受け継ぐ。 ⏎ 　第１３回ガンダムファイトには、国家反逆罪で無期冷凍刑に処された父カッシュ博士の釈放とアルティメットガンダムを奪って地球へ逃亡した兄キョウジの捜索のために参加した。 ⏎ 　一見すると無愛想で冷徹だが、激情を内に秘め、優しい一面も持つ。 ⏎ 　ガンダムファイトの旅を続ける中、シャッフル同盟との友情、師である東方不敗との激闘、兄キョウジの真実を経て、人間的にも大きく成長していく。 ⏎ 　パートナーであるレインがデビルガンダムの生体ユニットとなるも、愛を告白する事で閉ざされていた彼女の心を救い、デビルガンダムから解放する。 ⏎ 　その後、レインとの「石破ラブラブ天驚拳」でデビルガンダムを倒し、共に地球へと凱旋した。
> EN (odniesienie oficjalne, NIE polski): The Colony Martial Arts champion and representative Gundam Fighter of Neo Japan. ⏎ He inherited the title of King of Hearts after ten years of training under Master Asia, the Undefeated of the East. ⏎  ⏎ His father, Dr. Kasshu, was charged with treason and sentenced to cryogenic sleep, and his older brother, Kyoji, stole the Ultimate Gundam and fled to Earth. Domon joins the 13th Gundam Fight to clear his father's name and find his brother. ⏎  ⏎ Underneath his unsociable and cold demeanor is a passionate and kind heart. ⏎ As he continues his quest in the Gundam Fight, he grows as a person through his friendships with the Shuffle Alliance, his fierce fights with his master, and learning the truth behind Kyoji's actions. ⏎  ⏎ When his partner, Rain, becomes the Dark Gundam's bio-unit, his passionate declaration of love frees her from the Dark Gundam's shackles. Domon and Rain defeat the Dark Gundam with their Sekiha Love Love Tenkyoken and triumphantly return to Earth together.

### dic\_pilot\_RAIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b008\]
> JP (źródło tłumaczenia): 　ドモン・カッシュの幼なじみで、ネオジャパンのガンダムチームのスタッフ。 ⏎ 　クルー同伴を拒むドモンのためメカニック兼医師として、ガンダムのメンテナンスから彼の健康管理まで全てを一人でこなしている。 ⏎ 　ガンダム研究の権威ミカムラ博士を父に持ち、彼女自身は大学で医学を学んでいた。 ⏎ 　明るく献身的であり、時に理知的に、時に行動的にと陰に日向にパートナーであるドモンを支える。 ⏎ 　第１３回ガンダムファイトの終盤、気持ちのすれ違いや父であるミカムラ博士の罪からドモンと距離を置いてしまうこともあった。そこをつけ込まれ、デビルガンダムの生体ユニットとなるが、救出に来たドモンの愛の告白により救われる。 ⏎ 　その後、ドモンとの「石破ラブラブ天驚拳」でデビルガンダムを倒し、共に地球へと凱旋した。
> EN (odniesienie oficjalne, NIE polski): Domon Kasshu's childhood friend and Neo Japan's Gundam Team staff. ⏎  ⏎ Since Domon refuses to have an accompanying crew, she takes care of everything herself, acting both as both a mechanic and a doctor. ⏎  ⏎ The daughter of the influential Gundam researcher Dr. Mikamura, she studied medicine in university. ⏎  ⏎ Cheerful and devoted, she supports Domon with her actions and intellect both upfront and behind the scenes. ⏎  ⏎ In the final battle of the 13th Gundam Fight, she distances herself from Domon due to a mutual misunderstanding and the discovery of Dr. Mikamura's crimes. After a certain series of events, she becomes the Dark Gundam's bio-unit, but is freed by Domon's passionate declaration of love. ⏎  ⏎ Domon and Rain defeat the Dark Gundam with their Sekiha Love Love Tenkyoken and triumphantly return to Earth, together.

### dic\_pilot\_CHIBOD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b00a\]
> JP (źródło tłumaczenia): 　ネオアメリカ代表のガンダムファイター。 ⏎ 　唯一の肉親である母と生き別れになって以来、ニューヨークの下町で窃盗やストリートファイトをして生活していた。 ⏎ 　その腕が見込まれ、コロニーボクシングの選手となり、１００連勝を記録するチャンピオンとなった。 ⏎ 　アメリカンドリームを実現させたチボデーは、ネオアメリカを全宇宙の頂点にすることを次の夢として第１３回ガンダムファイトに参加する。その周囲には、チボデー・ギャルズと呼ばれる４人の美女が常に付き従っている。 ⏎ 　性格は陽気かつパワフルで、感情表現も豊か。 ⏎ 　一度はＤＧ細胞に感染してドモンを襲うが、クイーン・ザ・スペードに助けられ、シャッフルの紋章を受け継いで新シャッフル同盟の一員になる。 ⏎ 　戦いの中でドモンや他の国代表ファイターたちとぶつかる事で深く友情を結びつけていき、シャッフル同盟として戦い抜いた。
> EN (odniesienie oficjalne, NIE polski): The Gundam Fighter representing Neo America. ⏎  ⏎ After parting from his mother, his only living relative, he eked out a living in downtown New York by stealing and street fighting. ⏎  ⏎ His skills were recognized and he was scouted to be a Colony Boxer, becoming champion with a 100-win streak. ⏎  ⏎ Having achieved the American Dream, he joins the 13th Gundam Fight to realize his next dream: to make Neo America the greatest in the galaxy. ⏎  ⏎ Jovial and energetic, he is a very expressive person. He is always accompanied by the four beauties known as the Chibodee Gals. ⏎  ⏎ He once attacked Domon under the influence of the DG cells, but was cleansed by the Queen of Spades; he inherits the Shuffle Crest and becomes a member of the Shuffle Alliance. ⏎  ⏎ Throughout the tournament, he clashes with Domon and the other nation representatives, forming a deep bond of friendship with them and fighting together as the Shuffle Alliance.

### dic\_pilot\_CYCYCI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b00c\]
> JP (źródło tłumaczenia): 　ネオチャイナ代表のガンダムファイター。 ⏎ 　第４回大会優勝者サイ・フェイロンは、彼の祖父にあたる。 ⏎ 　地球の少林寺大僧正の息子で、荒廃した少林寺を再興するためにガンダムファイトに参加した。 ⏎ 　棒術を得意とし、若年ながら高い技能を持つが、お調子者でいたずら好きでスケベ、しかも修行は大嫌いという性格。そのため、お目付役の恵雲と瑞山をいつも困らせている。 ⏎ 　料理も得意で、出店で困っている男性の代わりに店を繁盛させたこともある。 ⏎ 　一度はＤＧ細胞に感染してドモンを襲うが、クラブ・エースに助けられ、シャッフルの紋章を受け継ぎ、新シャッフル同盟の一員となる。 ⏎ 　戦いの中でドモンや他の国代表ファイターたちとぶつかる事で深く友情を結びつけていき、シャッフル同盟として戦い抜いた。
> EN (odniesienie oficjalne, NIE polski): The Gundam Fighter representing Neo China. ⏎ His grandfather was Sai Feilong, winner of the 4th Gundam Fight. ⏎ His father is the current head priest of the Shaolin Temple on Earth. ⏎  ⏎ He participates in the Gundam Fight to restore the ruined Shaolin Temple to its former glory. Despite his young age, he is a master in the use of the staff. However, he has many shortcomings: he is undisciplined, a prankster, a bit of a pervert, and he hates training. His behavior always causes trouble for his attendants, Keiun and Zuisen. ⏎ He is also an incredibly talented chef: he once made a small restaurant flourish on behalf of another man, using only his cooking skills. ⏎  ⏎ He once attacked Domon under the influence of the DG cells, but was purified by the Ace of Clubs; he inherits the Shuffle Crest and becomes a member of the new Shuffle Alliance. ⏎ Throughout the tournament, he clashes with Domon and the other nation representatives, forming a deep bond of friendship with them and fighting together as the Shuffle Alliance.

### dic\_pilot\_JORJU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b00e\]
> JP (źródło tłumaczenia): 　ネオフランス代表のガンダムファイター。 ⏎ 　民衆とともに地球に残った名門貴族サンド家の末裔で、誰よりも地球の母国ネオフランスを愛している青年。第１３回ガンダムファイトには、一族の誇りとネオフランスの名誉のために参加を決意した。 ⏎ 　フェンシングを得意とし、常に礼儀と騎士道を重んじる、また、己には厳格だが、他人には紳士的で優しい。 ⏎ 　容姿端麗で常に涼しい表情をしているが、騎士として絶対の忠誠を誓っているマリアルイゼに危害が及んだり、相手が非礼であったりすれば、一切の容赦なく相手を斬り伏せる。 ⏎ 　一度はＤＧ細胞に感染してドモンを襲うが、ジャック・イン・ダイヤに助けられ、シャッフルの紋章を受け継ぎ、新シャッフル同盟の一員になる。 ⏎ 　戦いの中でドモンや他の国代表ファイターたちとぶつかる事で深く友情を結びつけていき、シャッフル同盟として戦い抜いた。
> EN (odniesienie oficjalne, NIE polski): The Gundam Fighter representing Neo France. ⏎  ⏎ Descendant of the prestigious and noble Sand family, who remained on Earth with the people, he is a young man who loves his homeland of Neo France more than anyone. He participates in the 13th Gundam Fight for the pride of his family and the honor of Neo France. ⏎  ⏎ His specialty is fencing, and he always conducts himself with courtesy and chivalry. He is strict with himself, but kind and gentle with others. ⏎  ⏎ He is a handsome man, calm and composed, but will show no mercy to those who disregard the rules of chivalry or who would dare to harm Maria Louise, to whom he has sworn absolute loyalty as a knight. ⏎  ⏎ He once attacked Domon under the influence of the DG cells, but was cleansed by the Jack of Diamonds; he inherits the Shuffle Crest and becomes a member of the new Shuffle Alliance. ⏎  ⏎ Throughout the tournament, he clashes with Domon and the other nation representatives, forming a deep bond of friendship with them and fighting together as the Shuffle Alliance.

### dic\_pilot\_ARUGO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b010\]
> JP (źródło tłumaczenia): 　ネオロシア代表のガンダムファイター。 ⏎ 　元はコロニー荒らしで有名な宇宙海賊のリーダーだったが、ネオロシア政府に海賊仲間を人質にとられてしまい、捕らえられた仲間の救出と引き換えに、ガンダムファイトで優勝することを命令される。 ⏎ 　彼自身も仲間同様に囚人で、胸には遠隔操作ができる爆弾が仕掛けられ、また腕には頑丈な手錠がはめられている。ネオロシア監督のナスターシャ・ザビコフに常に監視されているため、自由は存在しない。 ⏎ 　強面に加えて寡黙であるために誤解されがちだが、義に厚い人物。 ⏎ 　一度はＤＧ細胞に感染してドモンを襲うが、ブラック・ジョーカーに浄化されてシャッフルの紋章を受け継ぎ、新シャッフル同盟の一員となる ⏎ 　戦いの中でドモンや他の国代表ファイターたちとぶつかる事で深く友情を結びつけていき、シャッフル同盟として戦い抜いた。
> EN (odniesienie oficjalne, NIE polski): The Gundam Fighter representing Neo Russia. ⏎  ⏎ Formerly the leader of a group of infamous space pirates terrorizing the Colonies, his pirate comrades have been captured and are being held hostage by the Neo Russian government. In exchange for his friends' freedom, he has no choice but to enter the Gundam Fight and win. ⏎  ⏎ He himself is a prisoner, with a remote-controlled bomb strapped to his chest and heavy cuffs around his wrists. Neo Russia's prison warden, Nastasha Zabigov, monitors him constantly, to make sure he doesn't act on his own. ⏎  ⏎ With his fierce stare and few words, he is easily misunderstood, but he is an honorable man who deeply believes in doing what is right. ⏎  ⏎ He once attacked Domon under the influence of the DG cells, but was cleansed by the Black Joker; he inherits the Shuffle Crest and becomes a member of the new Shuffle Alliance. ⏎  ⏎ Throughout the tournament, he clashes with Domon and the other nation representatives, forming a deep bond of friendship with them and fighting together as the Shuffle Alliance.

### dic\_pilot\_AREBE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d20b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d20b012\]
> JP (źródło tłumaczenia): 　ネオスウェーデン代表のガンダムファイター。 ⏎ 　幼いころ両親を亡くして孤児となり、軍の施設でファイターとしての英才教育を受けてきた。 ⏎ 　不幸な生い立ちからクルーに対して反抗的だったが、同じような境遇のドモンと出会い、明朗な少女へと変化していく。 ⏎ 　ドモンのゴッドガンダムとのファイトでは、外部から精神を制御するバーサーカーシステムを発動されて正気を失うが、ドモンの魂の拳を受けて意識を取り戻す。 ⏎ 　敗れた後はドモンと行動を共にするようになり、恩人であるドモンに対してほのかな想いを抱いていた。
> EN (odniesienie oficjalne, NIE polski): The Gundam Fighter representing Neo Sweden. ⏎  ⏎ Orphaned at a young age, she received special combat training at a military facility. ⏎ Her unfortunate past made her rebellious towards her crew, but she turned into a cheerful girl after meeting Domon, who came from similar circumstances. ⏎  ⏎ In the fight against Domon's Burning Gundam, the activation of the Berserker System causes her to lose her sense of self, but Domon is able to restore her consciousness with the fists of his soul. ⏎ After losing to Domon, she decides to help him, harboring vague feelings for her benefactor.

### dic\_pilot\_TFFHAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b001\]
> JP (źródło tłumaczenia): 　先代キング・オブ・ハートにしてドモンの師匠。 ⏎ 　第１２回ガンダムファイトの優勝者であり、正統派格闘技の流派「東方不敗」を編み出し、素手でモビルファイターを倒すほどの超人的な強さを持つ。 ⏎ 　第１３回ガンダムファイトの最中、デビルガンダムの力を以て、人類を地球から排除しようとする。これは、地球の環境破壊の原因は人類の存在にあるという考えによるものである。 ⏎ 　この考えは東方不敗本人の思想であり、ＤＧ細胞に精神を支配されたデビルガンダム配下の他のファイターと異なり、強靱な精神力で正気を保っている。 ⏎ 　第１３回ガンダムファイト決勝大会のバトルロイヤルにおいて、弟子ドモンとの石破天驚拳の壮絶な撃ち合いの末、敗北する。さらにはドモンの言葉に自らのやってきた事の間違いを認め、ドモンの腕の中、安らかに死を迎えた。
> EN (odniesienie oficjalne, NIE polski): The former King of Hearts and Domon's master. ⏎  ⏎ He was the champion of the 12th Gundam Fight. He founded the martial arts School of Master Asia, the Undefeated of the East. His overwhelming, superhuman strength allows him to fight—and defeat—Mobile Fighters with his bare fists. ⏎  ⏎ Believing that human existence is the cause of the Earth's environmental degradation, he attempts to wipe humanity off the face of the Earth with the power of the Dark Gundam during the 13th Gundam Fight. ⏎  ⏎ Unlike other fighters infected by the DG cells and controlled by the Dark Gundam, he maintains his sanity through his unwavering mental strength. ⏎  ⏎ In the final round of the 13th Gundam Fight, the Battle Royale, he suffers defeat at the hands of Domon's Sekiha Tenkyoken. The words of his disciple make him realize the error of his ways, and he passes on peacefully in Domon's arms.

### dic\_pilot\_WON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b003\]
> JP (źródło tłumaczenia): 　ネオホンコンの首相であり、第１３回ガンダムファイトの主催者。 ⏎ 　マスター・アジアと結託してデビルガンダムを手中に収めることを画策し、その力により、永久的なコロニー国家の支配を目論んでいた。 ⏎ 　紳士的な外見や口調と裏腹に目的のためなら手段を選ばない策士。
> EN (odniesienie oficjalne, NIE polski): The Prime Minister of Neo Hong Kong. He is the organizer of the 13th Gundam Fight. ⏎  ⏎ He conspires with Master Asia to obtain the Dark Gundam. He intends to use its power to become the eternal ruler of the Colonies. ⏎  ⏎ Behind his gentlemanly appearance and speech, he is a schemer who will do anything to get what he wants.

### dic\_pilot\_ULBE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b005\]
> JP (źródło tłumaczenia): 　ネオジャパンの軍人。最終的な階級は大佐。 ⏎ 　ガンダム開発局の中心人物であり、元ガンダムファイター。 ⏎ 　第１２回ガンダムファイトの決勝戦では東方不敗に敗れ、準優勝となった。 ⏎ 　デビルガンダム捕獲のため、ドモンを後方からサポートしていたが、真の目的はデビルガンダムの力で地球圏を支配する事であった。 ⏎ 　ランタオ島で破壊されたデビルガンダムの残骸を回収した後、レインを生体ユニットにデビルガンダムを復活させ、ガンダムファイトの全面撤廃を全世界に宣言した。 ⏎ 　ＤＧ細胞に侵食された事でデビルガンダムそのものとなり、グランドマスターガンダムを駆ってドモン達を襲うが、シャッフル同盟の必殺技・シャッフル同盟拳によって倒された。
> EN (odniesienie oficjalne, NIE polski): A military officer from Neo Japan, promoted to the rank of Colonel. ⏎  ⏎ A former Gundam Fighter, he is now a central figure in the Gundam Development Bureau. ⏎  ⏎ He reached the final round of the 12th Gundam Fight tournament, where he placed second after being defeated by Master Asia. ⏎  ⏎ Though he has provided Domon with logistical support in his efforts to capture the Dark Gundam, his true goal is to use the power of the Dark Gundam to take over the Earth Sphere. ⏎  ⏎ After recovering the remains of the Dark Gundam, destroyed on Lantau Island, he restores it and forces Rain to act as its bio-unit. He then declares his intention to completely eliminate the Gundam Fight. ⏎  ⏎ He allows the DG cells to take over his body and mind, becoming an extension of the Dark Gundam itself. He fights against Domon and his friends with the Grand Master Gundam, but he ultimately falls before the power of the Shuffle Alliance Attack.

### dic\_pilot\_MRARIZ\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b007\]
> JP (źródło tłumaczenia): 　ネオフランス元首の愛娘。 ⏎ 　ジョルジュに憧れを抱いており、彼の気をひくためドモンに偽装誘拐を依頼したこともあった。 ⏎ 　可愛い外見だが相当なおてんばであり、ジョルジュのためならば、危険を侵してでも成し遂げる行動力を持っている。 
> EN (odniesienie oficjalne, NIE polski): The beloved daughter of the president of Neo France. ⏎  ⏎ She has feelings for George and once feigned being kidnapped by Domon to get his attention. ⏎  ⏎ Her cute appearance belies her inner tomboy, and she will take action even in dangerous situations for George's sake. 

### dic\_pilot\_NTSHA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b009\]
> JP (źródło tłumaczenia): 　ネオロシアの監督であり、囚人であるアルゴの監視者。 ⏎ 　メカニック、オペレーターなどのスタッフを指揮する有能な美女。 ⏎ 　勝利のためには手段を選ばない冷徹な性格だったが、アルゴの仲間を思いやる気持ちに触れ、彼との心の距離を縮めていく。 ⏎ 　シャッフル同盟の協力者となり、デビルガンダム打倒においても彼等をサポートして戦った。
> EN (odniesienie oficjalne, NIE polski): Neo Russia's prison warden and Argo's guardian. ⏎  ⏎ A striking woman who commands other personnel such as mechanics and operators. ⏎  ⏎ She is ruthless and would do anything for victory, but Argo's bond with his friends touched her and they grew closer. ⏎  ⏎ She cooperates with the Shuffle Alliance and helps them defeat the Dark Gundam.

### dic\_pilot\_RIZOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b00b\]
> JP (źródło tłumaczenia): 　ネオジャパンの科学者であり、ドモンとキョウジの父親。 ⏎ 　キョウジと共にアルティメットガンダム（デビルガンダム）を開発した。 ⏎ 　しかし、ウルベの陰謀でデビルガンダム暴走の罪を着せられ、永久冷凍刑にされていた。ミカムラ博士の計らいによって解放された後は、ドモン達にデビルガンダムを倒すアドバイスを送った。
> EN (odniesienie oficjalne, NIE polski): A scientist of Neo Japan and father of Domon and Kyoji. ⏎  ⏎ He developed the Ultimate Gundam (Dark Gundam) together with Kyoji. ⏎  ⏎ However, Urube framed him for the Dark Gundam's rampage and he was sentenced to cryogenic sleep. ⏎  ⏎ After being freed by Dr. Mikamura's plans, he advises Domon and his friends on how to defeat the Dark Gundam.

### dic\_pilot\_STOKER\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b00d\]
> JP (źródło tłumaczenia): 　ガンダムファイトの案内人。 ⏎ 　対戦カードの解説などを行う。
> EN (odniesienie oficjalne, NIE polski): The guide to the Gundam Fight. ⏎  ⏎ He provides explanations about the matches and other trivia.

### dic\_pilot\_HYRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b00f\]
> JP (źródło tłumaczenia): 　オペレーション・メテオでＬ１コロニー群から送り込まれたエージェント。１６歳。 ⏎ 　幼い頃から厳しい戦闘訓練を受けて育ったため、卓越した運動能力を持つ。５０階建てのビルから落下しても死なない、骨折を自力で治す等、肉体の強靭さも常人離れしたものがある。 ⏎ 　また、戦闘能力だけでなく、破壊工作やモビルスーツの修理といった技術にも非常に秀でている。 ⏎ 　無口で他人との係わり合いを極端に避ける傾向にあったが、本来は心優しい少年であり、リリーナや他のガンダムパイロット達との出会いを通して、次第に人間らしい感情を取り戻していった。 ⏎ 　ウイングガンダムゼロに搭乗してゼロシステムを使いこなし、そこで見た未来と自分の感情を信じて、ゼクス率いるホワイトファングと戦った。 ⏎ 　最終決戦ではリーブラ内に囚われていたリリーナを救い、ゼクスと決着をつける。 ⏎ さらに地球へと落下するリーブラを破壊して、地球を核の冬から救った。 ⏎ 　マリーメイア軍の反乱の際には、いち早く行動を開始。太陽に廃棄となったウイングガンダムゼロを回収し、世界の敵となった五飛と壮絶な戦闘を繰り広げた。
> EN (odniesienie oficjalne, NIE polski): An Operation Meteor agent sent from the L1 Colony Cluster. Age 16. ⏎  ⏎ He is extremely athletic, having been given rigorous combat training from an early age. His body is more resilient than the average human, allowing him to survive a 50-story fall with only a few broken bones that would heal on their own. ⏎  ⏎ In addition to combat, he excels in skills such as covert operations and Mobile Suit repair. ⏎  ⏎ A man of few words, he tended to avoid interacting with others, but at heart, he is ultimately kind. Through his encounters with Relena and the other Gundam pilots, he begins to regain the human emotions he had discarded in his upbringing. ⏎  ⏎ After mastering Wing Gundam Zero's Zero System, he fought against White Fang, led by Zechs, believing in the future Zero showed him as well as his own feelings. ⏎  ⏎ In the final battle, he rescued Relena, who was trapped inside Libra, and settled his score with Zechs. He then destroyed Libra before it could crash into Earth, saving the planet from nuclear winter. ⏎  ⏎ During the Mariemaia Army's rebellion, he was one of the first to take action. He recovered Wing Gundam Zero, which had been launched toward the sun, and engaged in a fierce battle with Wufei, who had decided to fight against a world he felt rejected soldiers like him.

### dic\_pilot\_HYRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8d60b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b010\]
> JP (źródło tłumaczenia): 　その我が身を顧みぬ戦いは、リリーナの勇気を呼び覚まし、戦いを終結させる力となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It was also a battle of reflection, and he recalled Relena's courage, which gave him the strength to end the fight.

### dic\_pilot\_DUO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8d60b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b011\]
> JP (źródło tłumaczenia): 　オペレーション・メテオでＬ２コロニー群付近に住むスイーパーグループから送り込まれたエージェント。１６歳。 ⏎ 　ガンダムデスサイズヘルのパイロットを務める。 ⏎ 　喜怒哀楽をハッキリと表に出す性格で、基本的には陽気に振る舞う。時には強情さを見せる事もあり、コロニー出身のガンダムパイロット達の中では最も少年らしい。「逃げも隠れもするが嘘はつかない」が信条で、事ある毎に死神と名乗るのは本人曰く「奇跡は見た事がないが、死人はいっぱい見たから」。 ⏎ 　月面基地潜入の際にＯＺの志願兵ヒルデ・シュバイカーと出会い、交流を重ねる内に妄信的にＯＺを信じていた彼女の目を覚まさせる事に成功。以後、互いに協力するようになっていった。 ⏎ 　最終決戦ではヒルデの情報を元にリーブラ内に潜入。捕らえられていたドクターらを解放。彼らをピースミリオンへと運び、落下するリーブラの軌道を変える事に成功している。 ⏎ 　ヒイロと共にマリーメイア軍の動向を探り、再びガンダムに搭乗して、平和の敵と戦った。
> EN (odniesienie oficjalne, NIE polski): A 16 year old Operation Meteor agent sent from L2 Colony Cluster by the Sweeper Group. ⏎  ⏎ He is tasked with piloting the Gundam Deathscythe Hell. ⏎  ⏎ His emotions show easily, and he is usually cheerful, but can be occasionally obstinate. He seems to be the youngest among the Gundam pilots who were born in the colonies. "I may run and I may hide, but I will never lie" is the creed he lives by, and he calls himself the Grim Reaper because "I have never witnessed miracles, but I have seen many dead men". ⏎  ⏎ He met Hilde Schbeiker, an OZ volunteer soldier, when he infiltrated the Lunar Base. She had complete and blind faith in OZ, but Duo managed to open her eyes to the truth through their interactions. They have worked together since then. In the final battle, he infiltrated the Libra with information obtained from Hilde. He freed the captured Scientists and brought them to Peacemillion, and also successfully altered Libra's falling trajectory. ⏎  ⏎ Along with Heero, he spied on the Mariemaia Army's movements and piloted the Gundam once more, battling against the enemy of peace.

### dic\_pilot\_DUO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8d60b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8d60b012\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱鎮圧後は、コロニーでヒルデと共にジャンク屋を営んでいる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the suppression of the Mariemaia Army, he opened a junk shop with Hilde in one of the colonies.

### dic\_pilot\_TOROWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b000\]
> JP (źródło tłumaczenia): 　オペレーション・メテオでＬ３コロニー群から送り込まれたエージェント。推定年齢１６歳。 ⏎ 　ガンダムヘビーアームズ改のパイロット。 ⏎ 　幼い頃から傭兵として各地の戦場を飛び回っており、多くの経歴が不明な寡黙で冷静な少年。だが、冷徹な人間というわけではなく、仲間想いな優しさを持っている。 ⏎ 　特にガンダムパイロットではカトルとの親交が深く、彼がコロニー側の姿勢に絶望して暴走した時にも、自らの身の危険を顧みずに説得。自身の機体が大破し、行方不明になるも、代わりにカトルの正気を取り戻すなど、自身の身すら顧みない行動を取った。 ⏎ 　その後は記憶と戦意を喪失した状態で発見され、潜伏先のサーカス団にて、キャスリンの弟として匿われていた。カトルの呼びかけに応じるようにして、再び戦線復帰を果たすが、必ず生きて帰る事をキャスリンに誓った。 ⏎ 　トロワ・バートンという名前は本名ではなく、名前自体はオペレーション・メテオの意見対立によって殺されたヘビーアームズの本来のパイロットの物である。偶然、殺害現場を目撃した彼は、殺害隠匿のためにドクトルＳから、この名を託され、以降はトロワ・バートンの名前で生きることになった。 ⏎ 　マリーメイア軍の反乱では、マリーメイア軍に潜入し、内部からの捜査を行なう。 ⏎ 　ブリュッセルでの戦いではカトルによって届けられたヘビーアームズ改で華麗な戦いを見せた。
> EN (odniesienie oficjalne, NIE polski): An Operation Meteor agent sent from the L3 Colony Cluster. Age 16 (estimated). ⏎  ⏎ Pilot of the Gundam Heavyarms Custom. ⏎  ⏎ Having wandered from battlefield to battlefield as a mercenary since childhood, he is a reserved and quiet young man of unknown background. However, he is not a cold person by any means, and he shows quiet kindness to his friends. ⏎  ⏎ Among the Gundam pilots, he is especially close to Quatre. When Quatre went berserk in despair over his father's death, he tried to persuade Quatre to stop, without regard for his own personal safety. He was able to bring Quatre out of his unstable state, but Trowa's Mobile Suit was critically damaged in the process, and he went missing. ⏎  ⏎ He was later found, having lost his memory and will to fight, protected by Catherine's circus as her "brother". He returned to the fight in response to Quatre's call to arms, vowing to Catherine that he would return alive. ⏎  ⏎ "Trowa Barton" is not his real name, but that of the original intended pilot of the Heavyarms, who was killed in a disagreement over Operation Meteor. After inadvertently witnessing the murder, Doctor S gave him the name Trowa Barton to cover up the murder, and he has lived under that identity ever since. ⏎  ⏎ During the Mariemaia Army's rebellion, he infiltrated the army to investigate it from the inside. ⏎  ⏎ At the Battle of Brussels, he fought spectacularly with the Heavyarms Custom delivered to him by Quatre. ⏎ 

### dic\_pilot\_TOROWA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b001\]
> JP (źródło tłumaczenia): 　戦争終結後はキャスリンのサーカス団に帰っていった。
> EN (odniesienie oficjalne, NIE polski): He returned to Catherine's circus after the final battle.

### dic\_pilot\_CATOR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b002\]
> JP (źródło tłumaczenia): 　Ｌ４コロニー群の大富豪ウィナー家の嫡男。１６歳。 ⏎ 　オペレーション・メテオではエージェントとして地球に降り、ガンダムサンドロック改のパイロットを務めた。 ⏎ 　裕福で温かな家庭で育ったため、穏やかで優しい性格の持ち主。同時にガンダムを使いこなす戦闘センスと周囲の人間を動かす指揮能力を併せ持つ。 ⏎ 　２９人の腹違いの姉がおり、４０人の隊員で構成されているマグアナック隊を率いる。何処に行っても大勢の人間に囲まれており、その全てから慕われている。 ⏎ 　しかし、反ＯＺの姿勢を貫いていた父親がコロニーの人々によって殺された事で暴走。禁断のモビルスーツ・ウイングガンダムゼロを組み上げてコロニーを破壊した。トロワの決死の説得を受けて、ようやく自分を取り戻すが、大きな犠牲を払う事となってしまう。 ⏎ 　その後は自らの過ちを認め、罪を償うために奔走。行方不明だったトロワを戦場に連れ戻す事にも成功している。 ⏎ 　また、ともすればバラバラになりがちなガンダムパイロット達をまとめるなど、精神的にも成長を遂げた。 ⏎ 　終戦後、ガンダムを廃棄する提案を持ちかけ、五飛以外のガンダムを回収し、資源衛星に乗せ、太陽へと射出する。
> EN (odniesienie oficjalne, NIE polski): Eldest son of the prosperous Winner family on L4 Colony Cluster, he is 16 years old. ⏎  ⏎ He was raised in a well-off and warm family, and is a calm and kind person. He has 29 sisters from different mothers.  ⏎  ⏎ He descended to Earth as an agent in Operation Meteor, taking on the duty of piloting the Gundam Sandrock Custom. He also has good senses to pilot the Gundam in battle, and the natural ability to lead the people around him. He leads the Maganac squadron of 40 people. He is surrounded by people everywhere he goes, and is looked-up to by all of them. ⏎  ⏎ However, he lost control after his father, who stuck to his anti-OZ beliefs, was killed by the people of the colony. He teamed up with the forbidden Wing Gundam Zero and destroyed the colony. He was touched by Trowa's do-or-die spirit and finally regained his own sense of self, but at the cost of many lives sacrificed. He recognized the error in his ways, and gave his all in repaying his sins. He even succeeded in bringing Trowa, who had disappeared, back to the battlefield. He also managed to gather the Gundam pilots together, and grew as a person. ⏎  ⏎ After the final battle, he proposed the idea of discarding all the Gundams. They gathered all the Gundams except Wufei's onto a resource satellite, and sent them to the Sun.

### dic\_pilot\_CATOR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b003\]
> JP (źródło tłumaczenia): 　だが、マリーメイア軍の反乱が起きた事で、射出したガンダムの回収に向かう。回収船と資源衛星のランデブー時間が５秒程度しか取れないという状況で、衛星への乗り込みに成功。パイロット達にガンダムを届け、反乱鎮圧の大きな力となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ However, the Mariemaia Army started a rebellion, and he headed off to retrieve the Gundams. He succeeded even though there was only 5 seconds where the retrieval ship would cross paths with the resource satellite. He delivered the Gundams to their pilots, and they proved pivotal in the suppression of the rebellion.

### dic\_pilot\_UFEY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b004\]
> JP (źródło tłumaczenia): 　オペレーション・メテオで地球に降りたＬ５コロニー群出身のエージェント。１６歳。 ⏎ 　古代中国に端を発する戦士の一族の直系。「強さこそが正義」という信念の下、戦士として育てられた。 ⏎ 　力によって弱者を踏みにじるＯＺの行為を悪と感じ、より強い力を持って討ち倒す事が正義と信じて戦う。 ⏎ 　そのため、生身での戦いでトレーズに敗れたときは、自らの弱さを思い知って戦意を喪失する。その中で弱さを認め、それでも戦おうとするサリィ・ポォの姿勢を目の当たりにし、戦い続ける姿勢こそが世界を動かすと考えるようになり、再び戦う意志を取り戻す。 ⏎ 　だが、最終決戦でのトレーズとの再戦に勝利するものの、その結果が勝ち逃げとも取れる不可解な形で終わってしまう。 ⏎ 　終戦後は、平和が訪れた事によって戦う姿勢を忘れた市民や行き場のなくなった兵士達の存在する世界に正義があるか疑問を持つようになる。その答えとして、あえて悪となり、マリーメイア軍に参加する。
> EN (odniesienie oficjalne, NIE polski): An Operation Meteor agent sent from L5 Colony Cluster to Earth, he is 16 years old. ⏎  ⏎ He comes from a line of warriors from ancient China. He believes that strength is justice, and was raised as a warrior. He regards the OZ's actions of oppressing the weak with power as evil, and fights under the belief that justice is defeating them with greater strength. ⏎  ⏎ When he was bested by Treize in a physical fight, he realized how powerless he was and lost all will to fight. He was struck by how Sally Po recognized her own weakness, yet still continued to fight. He came to believe that never giving up is the way to change the world, and regained his will to fight. He went up against Treize once more in the final battle and defeated him this time, but it was an incomprehensible conclusion that felt as though Treize was quitting while ahead. ⏎  ⏎ After the battle, the world returned to peace and people forgot about the state of war. The warriors who lived on the battlefield had no place to go, causing Wufei to question whether there was justice in this world. He arrived at the conclusion that this type of world was evil, and joined the Mariemaia Army.

### dic\_pilot\_UFEY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b005\]
> JP (źródło tłumaczenia): 　戦いの中、ヒイロとの対話や、マリーメイア軍に戦いを挑む市民達を見て、自らの疑問に決着を付けて、戦いを終えた。 ⏎ 　その後はサリィ・ポォの誘いを受け、プリベンターへと参加する事となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Amidst the fighting, he conversed with Heero, and saw how the people stood up against the Mariemaia Army. He came to an answer to his questions, bringing an end to the conflict. Subsequently, he joined the Preventers on Sally Po's invitation.

### dic\_pilot\_RERENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b006\]
> JP (źródło tłumaczenia): 　地球圏統一国家の外務次官。１６歳。 ⏎ 　かつて完全平和主義を唱えたサンクキングダムの王女でもあり、本名はリリーナ・ピースクラフト。 ⏎ 　ドーリアン外務次官の娘として育てられるものの、父の暗殺によって、その出生を知ると完全平和主義を唱えた実父の遺志を継いでサンクキングダムを再興した。 ⏎ 　ＯＺの侵攻によって、国は崩壊してしまうものの、ロームフェラ財団の手引きで世界国家元首として就任。政治の思惑によって翻弄されながらも、一貫して非武装・非暴力の完全平和主義を世界に訴え続けた。 ⏎ 　トレーズの台頭により、世界国家元首の座は退くことになるも、彼女の平和を求め続けた姿勢は、多くの人間から支持され、終戦後も絶大な影響力を持っている。 ⏎ 　世界が非武装化の流れとなり、父の理念が達成された現在は、義父であるドーリアンの仕事を完遂させるべく、外務次官としてコロニーと地球の橋渡しを請け負っている。 ⏎ 　その影響力の大きさから、マリーメイア軍に拉致されるも、臆することなくマリーメイアとぶつかり、彼女の説得を続けた。
> EN (odniesienie oficjalne, NIE polski): The United Earth Sphere Nation's Vice Foreign Minister, 16 years old. ⏎  ⏎ She is the princess of the former Sanc Kingdom that advocated total pacifism, and her real name is Relena Peacecraft. She was raised as the daughter of Vice Minister Darlian. When he was assassinated, she learned of her real identity, and resolved to take on her real father's vision for total pacifism and re-establish the Sanc Kingdom. ⏎  ⏎ The kingdom was destroyed by OZ's invasion, but she became a leader of Earth and all colonies due to the influence of the Romefeller Foundation. Even as she was tossed around by others' political motives, she stuck fast to her belief of total pacifism, envisioning a world without arms and violence. ⏎  ⏎ She withdrew from her position as leader with the rise of Treize, but the people continued to support her vision for peace, and she remained a figure of great influence even after the final battle. As the world moved towards disarmament, her father's vision was finally becoming reality, seen through the work of her foster father Dorian. She assumed the position of Vice Foreign Minister, becoming the bridge between the Colonies and Earth. ⏎  ⏎ She was so influential that the Mariemaia Army kidnapped her. She faced Mariemaia without fear and kept trying to convince her.

### dic\_pilot\_RERENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b007\]
> JP (źródło tłumaczenia): 　彼女とヒイロの覚悟は戦いを忘れた人々の意識を変え、それはマリーメイア軍の反乱終結の大きな力となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Both Heero's and her resolve changed the opinion of those who had forgotten about war, becoming the key factor in ending the Mariemaia Army's rebellion.

### dic\_pilot\_HILDE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b008\]
> JP (źródło tłumaczenia): 　コロニー市民出身の元ＯＺ志願兵。当時の階級は特士。 ⏎ 　コロニーがＯＺを受け容れた後にコロニーを守りたいという一途な気持ちから兵士に志願する。しかし、デュオとの出会いによって、ＯＺのやり方に疑問を持ち、離反する事になる。 ⏎ 　以降は戦争とジャンク屋の両面からデュオのサポートをして回る。 ⏎ 　戦争終結後も変わらずデュオとジャンク屋を営んでいる。
> EN (odniesienie oficjalne, NIE polski): A former volunteer OZ soldier from the space colonies. ⏎  ⏎ When she left the service, her rank was Specialist. Originally, she joined when her colony acceded to OZ control, intending to protect her home. However, she defected after meeting Duo and realizing there were problems with OZ's methods.  ⏎  ⏎ After leaving the service, she acted as Duo's support in both his fighting and work as a junk dealer. Once the conflict ended she continued running her junk dealer business by Duo's side.

### dic\_pilot\_DOLOSY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00a\]
> JP (źródło tłumaczenia): 　ロームフェラ財団代表のデルマイユ公の孫娘。 ⏎ 　戦争を望み、戦争に対して独自の美学を持っている。 ⏎ 　トレーズとは遠縁（従姪）であり、眉毛の形が酷似している。 ⏎ 　リリーナと行動を共にし、完全平和主義を貫く彼女への憧れを率直に口にする。 ⏎ 　間接的とはいえ、自ら祖父デルマイユを死に追いやると、単身リーブラに乗り込み、ホワイトファングに参加。ゼロシステムを使ってモビルドール部隊を指揮し、ヒイロ達の前に立ちはだかった。 ⏎ 　しかし、戦いを好む性格の裏には、父親を奪った戦争を何よりも憎む気持ちが隠されていた。最終決戦の中で自らの本心を吐露し、戦争を止めさせるために悲惨な戦争を見せ付けようとした事を語った。 ⏎ 　決戦後、トレーズの墓参りで出会ったノインに過去を振り返る事に飽きたと話し、未来へと向かう姿勢を見せた。
> EN (odniesienie oficjalne, NIE polski): The granddaughter of Duke Dermail, representative of the Romefeller Foundation. ⏎  ⏎ She enjoys war, finding a unique beauty in conflict. Her distinct eyebrows are a shared trait with her distant cousin Treize. While working together with Relena, she was vocal of her admiration for Relena's dedication to total pacifism.  ⏎  ⏎ After indirectly sending her grandfather, Dermail, to his death, she chose to board the Libra and join the ranks of White Fang. While there, she used the Zero System to command a unit of Mobile Dolls against Heero and his comrades.  ⏎  ⏎ Her outward love for conflict, however, belied an inner hatred of the flames of war that snatched her father away from her. In the final conflict she admitted her true intentions to show the world the real tragedy of war.  ⏎  ⏎ After the war, she encountered Noin while visiting Treize's grave, telling her she was tired of dwelling on the past. She now wishes to keep her gaze fixed ahead to the future.

### dic\_pilot\_DOLOSY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00b\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱の際はくすぶっている市民を煽動し、数台の車両と共に市民を大統領府へ移送した。 ⏎ 　なお、専用車は昔と変わらず金色の塗装が施されていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the Mariemaia Army's rebellion, she instigated civilians to rally against the attacks, organizing a convoy of vehicles to transport them to the presidential mansion. ⏎  ⏎ Of course, she made sure that her own personal vehicle was painted gold, as was her wont.

### dic\_pilot\_SALY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00c\]
> JP (źródło tłumaczenia): 　プリベンターのメンバー。コードネームはウォーター。 ⏎ 　以前は連合軍の軍医を務めており、ヒイロ達との出会いを通してガンダムのパイロットに興味を持ち、ＯＺの地球圏支配をきっかけにレジスタンスとなった後は彼等のサポートを行なっていた。 ⏎ 　包容力があり、プリベンターやガンダムパイロット達の緩衝材のような役割を担っている。 ⏎ 　故郷の旧中国地区でゲリラ部隊に参加していた際には、その優しさでトレーズに敗北した事で戦意を喪失していた五飛を励まし、再起させた事もあった。 ⏎ 　行動的な一面も併せ持っており、大戦中は反ＯＺ勢力の一員として各種工作活動を支援・指揮してヘビーアームズ、サンドロックを回収し、パイロットへと届けた。
> EN (odniesienie oficjalne, NIE polski): A member of the Preventers, codenamed Water. Once a military doctor, she became interested in the Gundam pilots after meeting Heero and his companions. She ended up aiding them as part of the resistance once OZ took control of the Earth Sphere.  ⏎  ⏎ Thanks to her tolerant attitude, she is able to act as a sort of buffer between the Preventers and the Gundam pilots.  ⏎  ⏎ While fighting with the guerrilla forces in the former China region, her old home, she met Wufei. Though he had lost his will to fight after a crushing defeat at Treize's hands, her kindness helped reignite the fire within him.  ⏎  ⏎ Her kindness belies a more aggressive nature. During the war she worked as a member directing and supporting the anti-OZ movement, even managing to recover the Heavyarms and Sandrock and return them to their pilots.

### dic\_pilot\_SALY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00d\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱終結後は、五飛をプリベンターに勧誘し、活動を続けている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the Mariemaia rebellion she asked Wufei to join the Preventers, where she continues to work.

### dic\_pilot\_LADY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00e\]
> JP (źródło tłumaczenia): 　プリベンターのリーダー。コードネームはゴールド。 ⏎ 　凛々しさと優しさを兼ね備え、軍務から政治まであらゆる知略に長けた女性。 ⏎ 　大戦前はＯＺ総帥トレーズの副官を務めていた。トレーズに心酔しており、その理想を叶えるためなら手段を選ばず、妥協も許さない女性であった。その徹底ぶりは、トレーズの考えを理解するためにもう一人の聖女のような人格を生み出してしまう程。 ⏎ 　二つの人格はトレーズを理解できるまでは不安定なままであったが、トレーズの真意を理解する事で安定。現在の一つの人格として統合されている。
> EN (odniesienie oficjalne, NIE polski): The leader of the Preventers, under the codename Gold. She is refined, with a kind heart and a head for everything from politics to military administration.  ⏎  ⏎ Before the war, she acted as aide to Treize, commander in chief of the OZ forces. She was infatuated with Treize, and would do anything to make his ideals a reality, adopting a stance of no compromise as a result. This obsession led to her creating a second, saintly personality that could better understand Treize's thinking. ⏎  ⏎ The two personalities remained in an unbalanced state as she struggled to grasp Treize's ideals. However, once she was able to finally perceive his true intent, they stabilized. She has now returned to a single personality.

### dic\_pilot\_LADY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b00f\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱では、トレーズの忘れ形見であるマリーメイアを救うために大統領府に向かった。 ⏎ 　終戦後はマリーメイアを保護している。 ⏎ 
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the Mariemaia Army's rebellion, she headed to the presidential mansion to save Mariemaia, who was a living memorial of sorts to Treize. ⏎  ⏎ In the aftermath of the conflict, she became the caretaker of the young girl.

### dic\_pilot\_ZEKS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b010\]
> JP (źródło tłumaczenia): 　プリベンター所属のパイロット。コードネームはウインド。２０歳。 ⏎ 　本名はミリアルド・ピースクラフト。かつて完全平和主義を唱えて地球圏統一連合に滅ぼされたサンクキングダムの王子。 ⏎ 　前大戦では、ホワイトファングの指導者として、地球に対し宣戦布告を行った。 ⏎ 　リリーナ同様、父の遺志を継ぎ、平和を願う人間であったが、リリーナの再興した新生サンクキングダムが崩壊した事をきっかけに完全平和のためには戦争を起こす愚かしさを人類に見せ付けなければならないと考え、「リーブラ落とし」を敢行しようとした。 ⏎ 　最終決戦では、ガンダムパイロットの活躍により計画は阻止、自身もヒイロとの一騎打ちの末に敗北。リーブラの動力部破壊の爆発に巻き込まれ消息不明となっていたが、マリーメイア軍の反乱に対抗するため、「プリベンター・ウインド」の名と共にトールギスⅢを駆って戦場に戻った。 ⏎ 　祖国の復讐のためにＯＺのパイロットを行っていた過去がある事から、自身の手は汚れていると考えており、完全平和のためにリリーナの裏方として力を尽くそうと考えている。
> EN (odniesienie oficjalne, NIE polski): A member of the Preventers, his codename is Wind. He is 20 years old. He is prince of the former Sanc Kingdom that advocated total pacifism, and his real name is Milliardo Peacecraft. ⏎  ⏎ In the previous war, he declared war on Earth as leader of White Fang. Like Relena, he inherited their father's vision and wishes for peace. He wanted to make an example of those foolish people who destroyed the Sanc Kingdom that Relena re-established to trigger war in the name of total pacifism, and took the decisive action to crash Libra. ⏎  ⏎ In the final battle, his plans were foiled by the Gundam pilots, and he was shot down by Heero. He was caught up in the explosion of Libra's propulsion system, and was never seen again. However, he reappeared on the battlefield as Preventer Wind, piloting the Tallgeese III to stop the Mariemaia Army's rebellion. ⏎  ⏎ He was once an OZ pilot who fought for his country's revenge, but thought that his hands were too stained with blood, so decided to support Relena's efforts towards total pacifism from the shadows.

### dic\_pilot\_ZEKS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b011\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱終結後は、リリーナの考案するテラフォーミング計画を実行に移すために、ノインと二人で旅立って行った。
> EN (odniesienie oficjalne, NIE polski): In the aftermath of the Mariemaia Army's rebellion, he set off to implement Relena's Terraforming Project along with Noin.

### dic\_pilot\_NOIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b012\]
> JP (źródło tłumaczenia): 　プリベンターの一員。コードネームはファイヤー。 ⏎ 　かつてはＯＺの新兵養成教官であった。 ⏎ 　士官学校をトップのゼクスに次ぐ成績で卒業しており、指揮官としてもモビルスーツのパイロットとしても優秀。 ⏎ 　士官学校時代から、ゼクスを深く愛しており、離れていた時間を正確に記憶していたほど。 ⏎ 　養成していた新兵達を五飛の襲撃で失うと、仇討ちを誓ってゼクスの部下となるが、ゼクスがＯＺを脱退すると、それを追うように脱退。彼の妹であるリリーナの警護を務めるようになる。 ⏎ 　新生サンクキングダムをリリーナが興した際には、その補佐を務め、秘密裏に軍備を整えるなど実務を担っていた。 ⏎ 　戦後はプリベンターに所属し、平和の維持に務め、ブリュッセルでのマリーメイア軍との戦いではトーラスを駆り、ガンダムパイロットに劣らぬ活躍を見せた。
> EN (odniesienie oficjalne, NIE polski): A member of the Preventers, her codename is Fire. ⏎  ⏎ She was once the OZ's instructor for new recruits. She graduated from the military academy with stellar grades, second to only Zechs, and excels as both a commander and Mobile Suit pilot. She has been in love with Zechs since their days in the military academy, and clearly remembers how much time has elapsed since they last saw each other. ⏎  ⏎ After the new recruits she trained lost to Wufei in battle, she swore revenge and became Zech's subordinate, but followed him when he left OZ. She also comes to guard his younger sister Relena. When Relena re-established the Sanc Kingdom, she was her assistant, taking on the role of making military preparations behind the scenes. ⏎  ⏎ She became part of the Preventers after the war, working to maintain peace. She piloted the Taurus during the Mariemaia Army's attack on Brussels, performing just as well as the Gundam pilots.

### dic\_pilot\_NOIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8da0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b013\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱後は、再会したゼクスと共にテラフォーミング計画に従事すべく宇宙へと旅立っていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the aftermath of the Mariemaia Army's rebellion, she was reunited with Zechs and left for space together to implement Relena's Terraforming Project.

### dic\_pilot\_DEKIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8da0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8da0b014\]
> JP (źródło tłumaczenia): 　バートン財団総帥で、マリーメイアの祖父。 ⏎ 　財団の総帥として活動する一方で、裏ではカーンズら反抗勢力に支援を行い、オペレーション・メテオの計画を進めていた影の権力者。 ⏎ 　権力欲の強い人物であり、マリーメイアを象徴として、元ホワイトファングの兵士やトレーズ派の残党の一部をマリーメイア軍として編成。 ⏎ 　武装を放棄している地球圏をモビルスーツ部隊で掌握し、その支配を目論む。
> EN (odniesienie oficjalne, NIE polski): Leader of the Barton Foundation and Mariemaia's grandfather. ⏎  ⏎ While conducting himself as the Foundation's leader, he supports Quinze's resistance forces behind the scenes, and was influential in moving forward Operation Meteor. ⏎  ⏎ He hungers for power, and used Mariemaia as a symbol to gather former White Fang members and Treize faction together to form the Mariemaia Army. ⏎  ⏎ He aimed to seize and control the Earth Sphere, who had given up arms, with Mobile Suits.

### dic\_pilot\_DEKIM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8de0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b000\]
> JP (źródło tłumaczenia): 　しかし、ガンダムパイロットやゼクスたちプリベンターの活躍、平和を望む市民達の蜂起により反乱は失敗。妄執にとりつかれたデキムは、マリーメイアを見捨ててまで野望を実現しようとしたが、部下である元トレーズ派の青年将校に逆賊として射殺された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ However, due to the actions of the Gundam pilots, Zechs, and the Preventers, his rebellion failed at the hands of the peace-loving citizens. Dekim was so seized by his conviction that he could even abandon Mariemaia to realize his goals, but he was betrayed and shot by his subordinate, a young officer who was formerly of the Treize faction.

### dic\_pilot\_MARYM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b001\]
> JP (źródło tłumaczenia): 　マリーメイア軍の象徴の少女。７歳。 ⏎ 　トレーズとレイア・バートンの間に生まれた娘で、デキム・バートンは彼女の祖父にあたる。 ⏎ 　トレーズの娘であることを誇りとし、７歳の少女とは思えない聡明さを持っている。だが、一方でデキムの傀儡として育てられた事から、彼の歪んだ考えも刷り込まれており、他人に対して不遜な態度を取る。
> EN (odniesienie oficjalne, NIE polski): The symbol of the Mariemaia Army, she is 7 years old. ⏎  ⏎ Daughter to Treize Khushrenada and Leia Barton, Dekim Barton is her grandfather. She is proud of her status as Treize's daughter, and possesses wisdom beyond her years. However, she is also Dekim's puppet and has been brainwashed with his twisted ideals, and treats everyone else with disrespect.

### dic\_pilot\_MARYM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8de0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b002\]
> JP (źródło tłumaczenia): 　戦いの中、リリーナの説得やガンダムパイロット達の行動から、自身の過ちに気付き、デキムの銃弾から身を挺してリリーナを守った。 ⏎ 　象徴であるマリーメイアの戦意喪失と実質的指導者であるデキムの死により、戦いは終結した。 ⏎ 　その後は、レディ・アンと共に生活を送っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the fighting, she realized the error of her ways through Relena's words and the Gundam pilots' actions. Dekim fired at Relena, but she took the bullet upon herself to protect her. ⏎  ⏎ With the loss of their symbol's will to fight and the death of their actual leader Dekim, the Mariemaia Army came to an end. Thereafter, Mariemaia lived her life as Lady Ann.

### dic\_pilot\_SIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b003\]
> JP (źródło tłumaczenia): 　ザフトのミネルバ所属のモビルスーツパイロット。１６歳。 ⏎ 　生まれも育ちもオーブで、家族と共に戦争を知らず平和に過ごしていた。が、前大戦における地球連合軍のオーブ侵攻の際、目の前で両親と妹を一度に失っている。 ⏎ 間もなくオーブの軍人、トダカの勧めでプラントに移住し、「大切なものを守るためには力が必要」と考えてザフトに入隊。優秀な成績でアカデミーを卒業し、エリートパイロットの証である赤服を身に着けるまでになった。このような経緯からか、快活ながらも非常にナイーブな面があり、攻撃性が強く表に出る事がある。 ⏎ 　秘めたる力をデュランダルに期待され、最新鋭機体であるインパルスガンダムのパイロットに選ばれる。そして、セカンドステージのガンダム３機が強奪されると、それを奪い返すために出撃した。 ⏎ 　当初は実戦経験が不足していることもあって、さほど戦果は挙げられなかったが、やがて繰り返される戦いと死への反発からＳＥＥＤを発現させる。以降は獅子奮迅の活躍を見せ、エースへと成長していった。アスランの事は尊敬しつつも、どこか煮え切らない態度に怒りをぶつける事もしばしばだった。 ⏎ 　ステラを巡る戦いからキラを仇敵と認識し、キラとフリーダムガンダムを撃墜する。 ⏎ さらにデュランダルから離反したアスランを撃墜し、これを契機にデスティニーガンダムを与えられ、特務隊ＦＡＩＴＨの一員に任命されるなど、着実にデュランダルの尖兵と化していった。 ⏎ 　最終決戦の際にもアスランの説得を受けるが、かたくなに戦いを続ける。錯乱のあまり、心を通い合わせていたルナマリアにすら攻撃をしかけそうになるが、あわやというところをアスランに撃墜され、幻想の中でステラと再会。ルナマリアの膝の上で目覚め、涙の中で戦いの終焉を迎えた。 ⏎ 　『ファイナルプラス』で追加された後日談では、オーブの慰霊碑を訪れた際、２度目となるキラとの対面を果たす。そして、平和を維持する戦いを共に続けるという誓いの握手を交わした。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit pilot with ZAFT's Minerva. 16 years old. ⏎  ⏎ Born and raised on Orb, Shinn had led a peaceful life, blissfully unaware of the fighting that would soon come. During the invasion of Orb by the Earth Alliance, he watched as his parents and little sister were killed in front of him. ⏎  ⏎ Soon after, he moves to PLANT at the recommendation of Todaka, an Orb soldier. He joins ZAFT, motivated by his desire to become strong enough to protect that which is important to him. He graduates with excellent grades from the Academy, wearing a red uniform to show that he is an elite pilot. Shinn is lively but can be quite naive. There are times when he struggles to contain his aggression. ⏎  ⏎ Seeing the boy's potential, Dullindal expects great things from him and assigns Shinn to the cutting-edge Impulse Gundam. When three second-stage Gundam are stolen, he scrambles to retrieve them. ⏎  ⏎ Initially, Shinn's lack of combat experience holds him back, but with repeated fighting and a strong desire to live, SEED mode awakens in him. His skills develop into those of an ace pilot, and he fights with intense passion. Although Shinn respects Athrun, he often gets angry at his non-committal attitude to things. ⏎  ⏎ Shinn deems Kira to be his mortal enemy after the latter kills Stellar, leading him to take down Kira and the Freedom Gundam. ⏎  ⏎ Shinn then attacks Athrun, who has defected from Dullindal. He is rewarded with the Destiny Gundam and an appointment to Dullindal’s vanguard, the secret corps, FAITH. ⏎  ⏎ In the final battle, Athrun attempts to convince Shinn to stop fighting, but is unable to make him change his mind. In his deluded state, Shinn even almost attacks Lunamaria, someone who he previously shared a deep bond with. Fortunately, he is shot down by Athrun just in time, and whilst unconscious, Shinn hallucinates that he is reunited with Stellar. He wakes up with his head in Lunamaria's lap, and he cannot hold back his tears as he watches the closing of the war. ⏎  ⏎ In the sequel "Final Plus", he visits the memorial at Orb and once again comes face to face with Kira. This time, however, the two shake hands and vow to fight together to maintain the peace.

### dic\_pilot\_RUNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b005\]
> JP (źródło tłumaczenia): 　ザフトのミネルバ所属のモビルスーツパイロット。１７歳。 ⏎ 　シン、レイと共にアカデミーでは優秀な成績を残し、赤服と呼ばれているエリートの一員となる。主にパーソナルカラーのレッドに塗装したガナーザクウォーリアで戦った。 ⏎ 　妹のメイリンと共に、前大戦の英雄であるアスランに興味を抱き、様々なアプローチをかけた。だが、そのアスランはデュランダルに不信を抱いて軍を脱走、メイリンも行動を共にしたと聞いたのも束の間、さらに２人が撃墜されたと知って大きな衝撃を受ける。 ⏎ 　それ以降、互いの心の傷を癒すように支えあったシンとの距離は急速に縮まり、やがて恋愛へと発展する。 ⏎ 　最終決戦の際、何かにとりつかれたように戦いを続けようとするシンを制止しようとするが、逆に攻撃を受けてしまう。それでも、アスランに敗北したシンを介抱する献身さを見せた。 ⏎ 　『ファイナルプラス』での終戦後の一幕では、シンと共にオーブ慰霊碑を訪れている。そこでキラやアスランと和解して涙を流すシンを見つめ、共に新たな未来へと歩き出していった。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit pilot with ZAFT's Minerva. 17 years old. ⏎  ⏎ Lunamaria is a red-uniformed member of the elite, and mainly pilots a custom-colored Gunner Zaku Warrior. Together with Shinn and Rey, she has excellent results from her time at the Academy.  ⏎  ⏎ She likes Athrun, who distinguished himself as a hero during the previous war. Unfortunately, her little sister, Meyrin, also likes Athrun, and both try to start a relationship with him. Athrun, however, decides to leave because of his mounting distrust in Dullindal; Lunamaria is shocked to learn that he has gone with Meyrin. Shortly after, she suffers a double blow upon learning that the two of them have been shot down. ⏎  ⏎ Lunamaria and Shinn support each other during this difficult time. Over time, they become close, eventually falling in love. ⏎  ⏎ During the final battle, she tries to stop Shinn fighting after he goes berserk, but he attacks her instead. However, she still looks after Shinn when he is defeated by Athrun. ⏎  ⏎ At the end of "Final Plus", she visits the Orb memorial with Shinn. They reconcile with Kira and Athrun. Lunamaria sees Shinn crying, and together they walk toward a new future.

### dic\_pilot\_ASRAN\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b007\]
> JP (źródło tłumaczenia): 　前大戦を終結に導く要因となった１人で、プラントでその名を知らない者はいない程の英雄的存在。１８歳。 ⏎ 　終戦後はオーブへ亡命し、恋人であるカガリの護衛役を務めていた。だが、再び始まった戦争の前に、何もできない無力さを噛み締めていた。そこをデュランダルに誘われ、カガリに別れを告げてザフトへ復隊。特務隊ＦＡＩＴＨの一員となった。 ⏎ 　復隊時に託されたセイバーガンダムを駆り、ミネルバの搭乗員となって戦うも、やがて見解の相違から親友であるキラと対立してしまう。 ⏎ 　当初はデュランダルの理念に共感していたものの、ラクスの暗殺疑惑や偽者であるミーアを利用していた事、さらに志は同じであるはずのアークエンジェルへの攻撃命令などを受けて、徐々に不信感を募らせていった。 ⏎ 　その後、ザフトから脱走し、再びキラ達と共に戦うようになり、デュランダルの提唱する「デスティニープラン」に立ち向かっていった。 ⏎ 　最終決戦の際には、デュランダルに従うシンに対して、戦いを止めるよう説得するが失敗。錯乱したシンが制止に入ったルナマリアに対しても攻撃する姿勢を見せたため、ＳＥＥＤを発現させて撃墜した。
> EN (odniesienie oficjalne, NIE polski): One of the people who helped bring about the end of the previous war, everyone aboard the PLANTs knows Athrun as a hero. He is 18 years old. ⏎  ⏎ After the war ended, Athrun seeks refuge in Orb, where he becomes a bodyguard for his lover, Cagalli. When war begins once more, he finds himself entirely powerless, until one day when he receives an invitation to return from Dullindal. After saying his goodbyes to Cagalli, he returns to ZAFT to become a member of the special corps, FAITH. ⏎  ⏎ Upon his return, Athrun pilots the Savior Gundam, and fights as part of the Minerva crew. Unfortunately, a difference of opinion leads him to fall out with his best friend, Kira. ⏎  ⏎ Although he initially agreed with Dullindal's vision, Athrun begins to distrust him after Dullindal is accused of attempting to assassinate Lacus, seeing how he uses Meer, and after he finds himself ordered to attack Archangel, who was on their side. ⏎  ⏎ Athrun decides to escape from ZAFT, and after reconciling with his friend Kira, the two fight together to stop Dullindal's Destiny Plan. ⏎  ⏎ During the final battle, Athrun tries to persuade Shinn to leave Dullindal, but he is unable to convince him to stop fighting. When Shinn even tries to attack Lunamaria as she tried to stop the two fighting, Athrun enters SEED mode in order to shoot him down.

### dic\_pilot\_KIRA\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b009\]
> JP (źródło tłumaczenia): 　アークエンジェルの乗員で、ストライクフリーダムガンダムのパイロット。１８歳。 ⏎ 　遺伝子調整に加え、様々な実験を重ねた結果誕生した「スーパーコーディネイター」とでもいうべき存在。 ⏎ 　前大戦時は、第三勢力として地球連合とプラントの双方を相手に戦い抜き、戦争を終結に導いた。その後、共に戦ったマリューや、恋人であるラクスと共にオーブに亡命。戦いとは無縁の世界で隠棲していた。しかし、ユニウスセブンの落下事件を目の当たりにした事、そしてラクス暗殺部隊との一戦を契機に、拡大していく戦火を食い止める必要性を強く感じ始める。そしてついに、かつての仲間達と共に新たな戦いを開始した。 ⏎ 　戦闘能力は他者の追従を許さないほどに高い。にもかかわらず争いや人殺しを好まない優しすぎる性格のため、戦闘となっても武器やカメラだけを破壊して相手を殺さない戦い方を心がけている。やがてそれが仇となり、シンの捨て身の攻撃に一度は敗れてしまう。だが、のちに新たな翼、ストライクフリーダムガンダムを得て復活を果たした。 ⏎ 　デュランダルが「デスティニープラン」の存在を明らかにした後は、カガリの代表首長復帰に伴い正式にオーブ軍に所属している。最終決戦ではラウ・ル・クルーゼの因縁を引き継ぐレイと決着をつけると、メサイアに潜入してデュランダルと対峙。混迷の世界で戦い続ける覚悟を示した。
> EN (odniesienie oficjalne, NIE polski): A crew member of the Archangel and a pilot of the Strike Freedom Gundam, at 18 years old, Kira is the result of various experiments and gene modifications. He is known as the "Ultimate Coordinator". ⏎  ⏎ During the previous war, he fought both the Earth Alliance and the PLANTs as a third force, and helped bring about the end of the war. Later, Kira traveled to Orb with his comrade, Murrue, and his lover, Lacus, and they remained there for a while, secluded from the fighting. However, after witnessing the Junius Seven incident and battling the troops who came to assassinate Lacus, the three decide that they must stop the war from consuming anything else. Kira steps once more onto the battlefield alongside his comrades. ⏎  ⏎ Although Kira's combat prowess is unsurpassed, at heart he remains a gentle soul who abhors fighting and killing. Even in battle, he will only destroy weapons or cameras, in order to avoid lethally injuring his enemies. His kindness turns out to be his weakness, however, and he loses once to a desperate attack from Shinn. Despite his loss, he is able to make a comeback when he gains the Strike Freedom Gundam. ⏎  ⏎ After Dullindal reveals the Destiny Plan, Cagalli returns to act as representative and Kira formally joins the Orb troops. In the final battle, he faces Rey, who has inherited the fate of Rau Le Creuset. Kira infiltrates Messiah and confronts Dullindal, demonstrating that he is prepared to continue the fight for good in a world of chaos.

### dic\_pilot\_KAGA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b00b\]
> JP (źródło tłumaczenia): 　オーブ連合首長国の代表。１８歳。 ⏎ 　かつての代表である父ウズミの遺志を継いで、祖国と世界を平和に導こうとする。しかしその若さや経験不足、セイラン親子の暗躍もあって国がまとまらず、自身の力のなさを痛感する事になる。 ⏎ 　前大戦の折から恋仲であったアスランがオーブを離れる際、指輪を贈られている。だがその後、「国を１つにまとめるため」という理由から、やむなくユウナとの結婚を決意し、想いを断ち切ってしまう。しかし、結婚式の最中に双子の兄弟キラのフリーダムガンダムに連れ去られた事で結婚は御破算となった。 ⏎ 　その後、実権を奪ったセイラン家が地球連合と同盟を結んで軍を動かし始めたため、それを阻止しようと働きかけるも失敗。だが、オーブ軍人達の決死の覚悟を目の当たりにした事で、祖国を守るという決意を新たにした。さらにオーブに危機が訪れた際には、ウズミの遺したモビルスーツ・アカツキを駆って祖国の危機を救った。 ⏎ 　再びオーブ代表となった後は国をまとめ上げ、「デスティニープラン」を提唱するデュランダルに立ち向かった。
> EN (odniesienie oficjalne, NIE polski): Representative of the Orb United Emirates. 18 years old, she took over the position from her late father Uzumi and has been trying to lead her country and the world to peace as per his wishes. However, she is unable to keep her people united due to her age, lack of experience, and the plotting of the Seirans, making her keenly aware of her powerlessness. ⏎  ⏎ When Athrun—her lover since the last war—leaves Orb, she gives him a ring. However, she later breaks off the relationship when she finds herself with no choice but to marry Yuna in order to unite Orb as one. However, her twin brother Kira interrupts the wedding with his Freedom Gundam and takes her away, annulling the marriage. ⏎  ⏎ Afterwards, when the Seirans steal control of Orb and begin deploying their military after joining forces with the Earth Alliance, she attempts to stop them, but fails. However, seeing the do-or-die resolve of Orb's soldiers inspires her own determination to protect her nation. ⏎  ⏎ When Orb finds itself in even further danger, she saves it using the Akatsuki Mobile Suit left behind by Uzumi. After regaining her position as Orb's representative, she reunites her people and opposes Dullindal and his Destiny Plan proposal.

### dic\_pilot\_RAKUS\_P\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b00d\]
> JP (źródło tłumaczenia): 　かつて「プラントの歌姫」と呼ばれたアイドル的存在。１８歳。 ⏎ 　その存在感とカリスマ性は絶大で、前大戦ではキラやアスラン達に道を指し示し、志を同じくする者達を集めるなど、戦乱を終結に導く大きな原動力となっていた。 ⏎ 　前大戦終結後、共に戦ったバルトフェルドやマリュー、恋人であるキラと共にオーブへ渡った。そこでマルキオ導師やキラの義母であるカリダ、そして孤児達と静かに暮らしていたが、自身を暗殺せんとする者達の出現によって短い平穏が破られた事を知る。 ⏎ 　さらに偽者であるミーアの出現もあって、デュランダルへの疑念を強める。やがて表舞台に戻る事を決意したラクスは、キラと共にアークエンジェルに乗り込んだ。 ⏎ 　その後、自らも戦うために宇宙へ上がり、デスティニープランの存在を知ると、それに立ち向かう事を表明。 ⏎ 　キラとアスランに新たな機体を用意した際には、自ら∞ジャスティスガンダムに乗り込み、アスランの下へと届けている。さらに各方面から戦力を集めるなど精力的に活動。デュランダルに異を唱える者達の思想的、精神的支柱となっていく。 ⏎ 　最終決戦の際には、前大戦同様にエターナルに乗り込み、最前線で旗印としての役割を果たした。 ⏎ 　デュランダルとの戦いを終えた後は、公私を問わずキラと寄り添う姿が見られた。
> EN (odniesienie oficjalne, NIE polski): A former pop star known as the "Singing Princess of the PLANTs". She is 18 years old. ⏎  ⏎ Lacus has a real sense of presence and charisma. In the previous war, she was a major factor in bringing the war to an end by directing Kira and Athrun, and also by rallying together like-minded people. ⏎  ⏎ After the war, she went to Orb with her comrades Waltfeld, Murrue, and her lover, Kira. There, she lives a quiet life with Reverend Malchio, Kira's mother-in-law, Calida, and the orphans. However, an assassination attempt on her life breaks her temporary respite. ⏎  ⏎ With the emergence of Meer, her imposter, she is increasingly suspicious of Dullindal. Lacus decides to return to the stage and boards the Archangel with Kira. ⏎  ⏎ Later, Lacus goes into space to fight, too, and when she learns of the Destiny Plan, she announces her intention to oppose it. ⏎  ⏎ When new units are ready for Kira and Athrun, she pilots the Infinite Justice Gundam in order to deliver it to Athrun. She has a lot of energy, throwing herself into her battles. Lacus becomes a key support figure, both spiritually and ideologically, for those who disagree with Dullindal. ⏎  ⏎ In the final battle, Lacus is on board the Eternal, as in the previous war, where she acts as a banner for the front line. When the battle with Dullindal is over, Lacus and Kira decide to go public about their relationship.

### dic\_pilot\_BALT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b00f\]
> JP (źródło tłumaczenia): 　高速戦闘艦エターナルの艦長。３２歳。 ⏎ 　元はザフトに所属し、「砂漠の虎」の異名で恐れられていた猛者であった。だが、前大戦の最中に軍を離反し、ラクス達に協力し、戦乱を終結に導いた。 ⏎ 　前大戦終結後は、共に戦ったキラやマリュー、ラクス達と共にオーブへ亡命。趣味のコーヒーを嗜みながら、束の間の平和を享受していた。 ⏎ 　プラントへの移住を考えていた折、ラクス暗殺を目論む特殊部隊の襲撃を受け、これを退ける。それをきっかけとして、再び第三勢力として、戦争と向かい合う事を決意した。 ⏎ 　アークエンジェル発進後は副艦長的な立場でマリューを補佐しつつ、有事の際にはパーソナルカラーに染めたムラサメで出撃し、未だ衰えていない腕前を披露。やがてラクスがプラントの現状を確認するために行動を起こした際には、その護衛として共に宇宙に上がっている。 ⏎ 　エターナルが活動を開始すると、前大戦時と同じくその艦長席に座った。だが、エターナル単独での戦いを強いられた際には、かつての愛機の流れをくむガイアガンダムで出撃した事もあった。
> EN (odniesienie oficjalne, NIE polski): Captain of the high-speed warship, the Eternal. He is 32 years old.  ⏎  ⏎ Originally a member of ZAFT, Waltfeld was known for his nickname, "Desert Tiger", and was a feared veteran. However, during the previous war, he defected to join Lacus, a move which helped bring about an end to the fighting. ⏎  ⏎ With the war over, he seeks refuge on Orb, along with his fighting companions Kira, Marrue, and Lacus. He develops a taste for coffee while he enjoys the rare moment of peace. ⏎  ⏎ Waltfeld starts to consider moving to PLANT, but with the special corps' attempt on Lacus's life, he abandons these plans; instead, he decides to go back into battle as a third force. ⏎  ⏎ After the Archangel's departure, he takes on a vice-captaincy role, fighting in his custom-colored Murasame in times of emergency. It is plain to see that his skills have not diminished over time. When Lacus takes action to confirm the current status of PLANT, he travels with her as a bodyguard. ⏎  ⏎ When Eternal joins the fray, however, Waltfeld resumes his captaincy, just like in the previous war. When he is forced to fight with the Eternal alone, he also pilots his precious Gaia Gundam.

### dic\_pilot\_MEYRIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8de0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8de0b011\]
> JP (źródło tłumaczenia): 　高速戦闘艦エターナルのオペレーター。１６歳。 ⏎ 　元はザフトに所属し、ミネルバのクルーであったが、アスランのザフト脱走を手助けし、そのままオーブ軍に所属した。 ⏎ 　ルナマリアの妹であり、ライバル意識を見せる事もあったが、姉妹仲は良い。
> EN (odniesienie oficjalne, NIE polski): An operator of the high-speed warship, the Eternal, Meyrin is 16 years old. ⏎  ⏎ She originally belonged to ZAFT as a crew member of the Minerva, but after helping Athrun escape ZAFT, she joins the Orb military. Meyrin is Lunamaria's little sister, and the two often compete with each other. Deep down, however, they love each other.

### dic\_pilot\_KISA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b000\]
> JP (źródło tłumaczenia): 　オーブ陸軍に所属する軍人。階級は一佐。 ⏎ 　かつてのオーブ代表ウズミ直属の部下で、前大戦時はカガリの護衛を務めた事もあった。 ⏎ 　ウズミの死後は、カガリの後見人として彼女を見守り続けている。 ⏎ 　地球連合とオーブの同盟後は、地球連合軍に潜入してその動向を探っていた。その最中、アスランとメイリンの脱走を知り、撃墜された彼らを救出してアークエンジェルへと運んだ。 ⏎ 　オーブの危機を知って出撃すると言い張るカガリにウズミの遺したアカツキを託し、自らもムラサメで出撃した。
> EN (odniesienie oficjalne, NIE polski): A captain in the Orb military, he formerly served directly under the previous Representative of Orb, Uzumi, and acted as Cagalli's bodyguard during the last war. He has been watching over Cagalli as her guardian following Uzumi's death. ⏎  ⏎ After the Earth Alliance and Orb join forces, he infiltrates the Alliance to spy on them. While doing so, he discovers Athrun and Meyrin have defected from ZAFT, saves them after they are shot down, and brings them aboard the Archangel. ⏎  ⏎ After Cagalli insists on joining the fighting upon learning of the danger Orb is in, he entrusts her with the Akatsuki bequeathed by Uzumi while also taking part in the fight with a Murasame.

### dic\_pilot\_IZAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b002\]
> JP (źródło tłumaczenia): 　ザフトのジュール隊隊長。１９歳。 ⏎ 　前大戦時では最後の最後でアークエンジェルとエターナルに協力し、共に戦争終結の力となった。 ⏎ 　終戦後、デュランダルの助力もあってザフトに復帰し、その才能から若くして一部隊の隊長という立場に収まる。豊富な戦闘経験を活かした部隊の指揮能力や戦闘での実力は一級品。ミネルバとの協力によるユニウスセブンの落下阻止、地球連合軍の一方的な攻撃からのプラント防衛、プラントがレクイエムの目標となった際のビーム偏向ステーション破壊作業（これは失敗に終わるが）など、宇宙を舞台に幅広く活躍した。 ⏎ 　アスランとの再会時には復隊を強く勧めるなど、かつてこだわっていた些細な対抗心から解放された成長した姿を見せている。 ⏎ 　オーブ対プラントの最終決戦の際には、敵対する友人と自身の立場との板ばさみという状況に再度立たされる。しかし、レクイエムやネオジェネシスという大量破壊兵器を使用するデュランダルに反発し、再びキラ達に協力した。
> EN (odniesienie oficjalne, NIE polski): Leader of ZAFT's Jule Team. 19 years old, he assisted the Archangel and Eternal in the final battle of the last war and helped end it. Afterwards, he returned to ZAFT with Dullindal's aid and was assigned his own team in recognition of his talents despite his young age. ⏎  ⏎ His abilities to command his troops with his extensive combat experience and his piloting abilities are top-of-the-line. He participates in a broad range of space operations, including interfering with the dropping of Junius Seven with the help of the Minerva, protecting the PLANTs from attacks by the Earth Alliance, and working to destroy Requiem's beam relay station when it targets the PLANTs (albeit ultimately failing in the end). ⏎  ⏎ He has matured past his tendency to get aggressive at the most trivial of things, as seen in times such as when he strongly encourages Athrun to rejoin ZAFT after they reunite. ⏎  ⏎ In the final battle between Orb and the PLANTs, he is once again stuck in the position of being between his duty and fighting his friends. However, he revolts against Dullindal after he uses weapons of mass destruction such as Requiem and Neo Genesis, and fights alongside Kira's group once more.

### dic\_pilot\_DEAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b004\]
> JP (źródło tłumaczenia): 　ザフトに所属し、親友イザークの率いるジュール隊で補佐を務める副官役。１９歳。 ⏎ 　前大戦時でもザフトに所属していたが、捕虜になったのを契機にアークエンジェルに乗艦し、彼等と共闘した。 ⏎ 　第三勢力として戦争終結に貢献した後はザフトに復隊したが、当時の責を問われ、エリートの証である赤服ではなく一般兵用の軍服を着用している。 ⏎ 　しかし、パイロットとしての腕は健在であり、精神面も含めてより頼もしい男に成長している。 ⏎ 　熱をあげていたミリアリアとの関係は、彼女の口から「フっちゃった」との言葉が確認されている。
> EN (odniesienie oficjalne, NIE polski): Soldier of ZAFT and aide-de-camp to the Jule Team, led by his best friend Yzak. 19 years old, he was also a soldier for ZAFT in the previous war, but ended up joining the Archangel and fighting alongside them after they took him prisoner. ⏎  ⏎ After helping to end the war, he returned to ZAFT and was punished, as can be seen by the standard green soldier uniform he now wears instead of the elites' red. ⏎  ⏎ Despite this, his piloting skills remain as sharp as ever, and he has matured into the kind of man anyone would want watching their back. He once had a fling with Miriallia, but she claims she dumped him.

### dic\_pilot\_JBRL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b006\]
> JP (źródło tłumaczenia): 　軍産複合体ロゴスのメンバーにして、コーディネイターを廃絶せんとするブルーコスモスの新盟主。３１歳。 ⏎ 　過剰な貴族趣味と偏った選民思想を持つ男。普段は冷静で慇懃な態度をしてはいるが、事が思惑通りに運ばなければすぐに逆上し、物に当り散らす下劣な品性の持ち主でもある。 ⏎ 　ユニウスセブン落下事件を一部のコーディネイターの仕業と知るや、それを理由に一方的にプラントとの開戦を宣言。世界を再び混乱に陥れた。 ⏎ 　しかし母体のロゴス共々、デュランダルの手によってその存在を暴露され、民衆からの敵意を一身に受けることになってしまう。以後各地で敗戦を続け、ロゴスのメンバーや地球連合軍の士官といった、自分以外の全ての者を捨て石にしながらも逃げ続ける。最期の砦であった月のダイダロス基地でも敗北し、もはや再起は不能となってもなお脱出を図る。だが乗り込んだガーティ・ルーの艦橋もろともに撃ち抜かれ、その死をもって逃亡劇の幕を引いた。
> EN (odniesienie oficjalne, NIE polski): A member of the military-industrial complex "Logos" and a new leader of the Blue Cosmos, who aim to exterminate all Coordinators.  ⏎  ⏎ He is 31 years old and an elitist who is excessively preoccupied with nobility. Although normally calm and courteous, he can quickly become furious when things don't go his way, and if provoked too far, he will take his rage out on anything or anyone. He can also be very crass. ⏎  ⏎ When he learns that the Junius Seven plan was the work of some Coordinators, he uses it as a reason to declare war on the PLANTs, plunging the world back into chaos. ⏎  ⏎ However, the existence of Logos is leaked by Dullindal, making Djibril and his group the targets of hostility. He suffers defeat after defeat, eventually sacrificing everyone but himself in order to escape, including members of Logos and Earth Alliance officers. He is defeated on the Daedalus lunar base, and despite a comeback now being impossible, he still attempts to flee. However, his Girty Lue is intercepted; death becomes his final escape.

### dic\_pilot\_SLETA\_G\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b008\]
> JP (źródło tłumaczenia): 　ガンダム・エアリアルのパイロット。 ⏎ 　故郷の水星からアスティカシア高等専門学園のパイロット科２年に編入してきた。 ⏎ 　生まれ育った水星の外の世界に憧れを抱いており、学園生活での抱負を「やりたいことリスト」にまとめている。 ⏎ 　真っ直ぐだが内向的な性格で、他人とのコミュニケーションは得意ではないため、発言の際には緊張から言葉を言いよどんでしまう。 ⏎ 　母・プロスペラを心から信頼しており、「逃げたら一つ、進めば二つ」という母の教えを拠り所に行動する。 ⏎ 　編入初日、ミオリネ・レンブランと出会った事をきっかけに学園ナンバーワンパイロット「ホルダー」の称号を持つグエル・ジェタークと決闘する事になる。
> EN (odniesienie oficjalne, NIE polski): Gundam Aerial's pilot. A second-year piloting student who enrolled in Asticassia School of Technology from her home planet of Mercury, where she has lived since birth. Because of this, she longs to see the world outside of Mercury, and has a list of things she wants to do over the course of her school life. ⏎  ⏎ Though quite earnest, Suletta is also an introvert who has trouble communicating with others, causing her to get nervous and consequently trip over her words in conversation. She has the utmost trust in her mother Prospera, whose words "If you run, you gain one, but if you move forward, you gain two" Suletta has made her life's philosophy. ⏎  ⏎ On her first day of school she meets Miorine Rembran, which results in her getting into a duel with Guel Jeturk, the Holder—the title given to the top pilot in school.

### dic\_pilot\_SLETA\_G\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b009\]
> JP (źródło tłumaczenia): 　この勝利によってホルダーの座につくと同時にミオリネの婚約者候補の筆頭となったものの、エアリアルが「GUND-ARM」であるとの疑惑から、学園だけでなくベネリットグループ全体にまで及ぶ騒動に巻き込まれていく。 ⏎ 　ベネリットグループ御三家のパイロットとの決闘では、エアリアルの性能を最大限に発揮して勝利を収め、ミオリネの花婿候補の座を守った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She ends up defeating Guel and winning the title of Holder from him...and becomes the prime candidate to be Miorine's groom as a result. ⏎ However, the Aerial is suspected of being a GUND-ARM, which gets her wrapped up in conflicts both within the school and with the wider Benerit Group. Suletta wins duel after duel against the pilots of the Benerit Group's Three Branches by using the Aerial to its fullest potential, defending her position as Miorine's fiancée candidate.

### dic\_pilot\_MIOLN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b00a\]
> JP (źródło tłumaczenia): 　ベネリットグループの総裁であるデリング・レンブランの一人娘。 ⏎ 　アスティカシア高等専門学園経営戦略科２年生で、その成績は経営戦略科内でトップ。父親の威光と容姿端麗である事も合わせて一部からは「お姫様」と揶揄されている。 ⏎ 　一方的に物事を決定する父に強い反発心を持っており、学園から脱出して地球へ行く事を願っている。 ⏎ 　父の定めたルールにより、１７歳になった時点で「ホルダー」の地位にある人物と結婚する事が決められている。 ⏎ 　学園の敷地内で亡き母が作った品種のトマトを栽培しており、その温室を心の拠り所としている。
> EN (odniesienie oficjalne, NIE polski): The only daughter of Delling Rembran, president of the Benerit Group. A second-year management strategy student at Asticassia School of Technology, her grades are at the top of the management strategy department. Some teasingly refer to her as "princess" due to her beauty and her father's position of authority. ⏎  ⏎ In truth, she despises her father for making decisions about her life entirely on his own, and wishes to escape the school to go to Earth. As per her father's rules, she is to marry the one who holds the title of Holder when she turns seventeen. ⏎  ⏎ Grows a breed of tomatoes created by her late mother in a greenhouse on school grounds, which keep her going in hard times.

### dic\_pilot\_MIOLN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b00b\]
> JP (źródło tłumaczenia): 　グエルに勝利してホルダーとなったスレッタを利用して父の定めたルールからの逃走を図るが、スレッタの真っ直ぐさに徐々に心を開いていく。 ⏎ 　ガンダム・エアリアルをめぐってスレッタが窮地に立たされた際には「株式会社ガンダム」の事業提案を行い、父の信用を借りて出資を集める事に成功した。 ⏎ 　その後は、地球寮のメンバーを巻き込みながら、社長として株式会社ガンダムの経営に奔走した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Once Suletta won the title of Holder from Guel, she hatched a plan to use the technical letter of her father's rules to escape the yoke she found herself placed under. Suletta's sincerity and earnestness, however, made her slowly open her heart and wonder if there might be more to her "plan" than she imagined. ⏎  ⏎ Proposes the forming of GUND-ARM Inc. when Suletta finds herself in hot water over the Gundam Aerial, and succeeds in borrowing her father's trust to raise funds. Afterwards, she runs GUND-ARM Inc. as its president while bringing the members of Earth House on board with the idea of the company.

### dic\_pilot\_GUERU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b00c\]
> JP (źródło tłumaczenia): 　アスティカシア高等専門学園パイロット科３年生でジェターク寮のエースパイロット。 ⏎ 　ベネリットグループ御三家であるジェターク・ヘビー・マシーナリーのＣＥＯヴィム・ジェタークを父親に持つ。 ⏎ 　学園ナンバーワンパイロット「ホルダー」の称号を持ち、決闘委員会の筆頭も務める。 ⏎ 　荒々しい性格で、自分の力への過信から横暴な言動が目立つ。 ⏎ 　将来はカテドラル直轄の特殊部隊であるドミニコス隊のエースパイロットになる事を目標としている。
> EN (odniesienie oficjalne, NIE polski): A third-year piloting student at Asticassia School of Technology and Jeturk House's ace pilot. Son of Vim Jeturk, CEO of Jeturk Heavy Machinery, one of the Benerit Group's Three Branches. ⏎  ⏎ Initially possesses the title of Holder—the top pilot in the school—and is the head of the Dueling Committee. A ruffian with a penchant for bullying others due to his overconfidence. Dreams of one day becoming the ace pilot for the Dominicus Unit—Cathedra's personal special forces.

### dic\_pilot\_GUERU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b00d\]
> JP (źródło tłumaczenia): 　スレッタとの決闘に敗れて「ホルダー」の地位を失う。その後、スレッタと再戦してまたも敗北するが、その実力を認めた彼女に対してプロポーズする。 ⏎ 　敗北を重ねた事で父・ヴィムの怒りを買い、さらにはエラン・ケレスとの決闘で敗れた事からジェターク寮から退寮させられた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He lost the title of Holder to Suletta in a duel. He then challenged Suletta to a rematch, only to lose again, but proposed to her when she acknowledged his abilities. ⏎  ⏎ His losing streak earns the ire of his father, Vim, who kicks him out of Jeturk House and the school after he loses another duel to Elan Ceres.

### dic\_pilot\_ERAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8e60b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8e60b00e\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズが擁立するパイロット。 ⏎ 　アスティカシア高等専門学園パイロット科３年生で、ペイル寮の筆頭と決闘委員会のメンバーを務める。 ⏎ 　他人に興味を持たず、誰にも心を開かない事から、学園の一部の生徒からは「氷の君」と呼ばれている。
> EN (odniesienie oficjalne, NIE polski): A pilot backed by Peil Technologies, one of the Three Branches of the Benerit Group. ⏎  ⏎ He is a third-year piloting student at Asticassia School of Technology who serves as the head of Peil House and one of the members of the Dueling Committee. ⏎  ⏎ Is known by some students as the Ice Prince for his lack of interest in others and cold personality.

### dic\_pilot\_ERAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b000\]
> JP (źródło tłumaczenia): 　その正体は本物のエラン・ケレスと同じ容姿に整形された影武者であり、ペイル社では「強化人士４号」と呼ばれている。 ⏎ 　「GUND-ARM」搭乗のために身体改造を施されており、自身と同じ境遇にあると考えたスレッタに興味を示す。しかし、スレッタが自身と異なる境遇であると知ると彼女に決闘を申し込んだ。 ⏎ 　スレッタに敗北するが、自分にはないものと思っていた幸せな過去を思い出す。しかし、身体の限界から与えられた役目を果たせなくなり、その任務から降ろされた。 ⏎ 　なお、その役目は「強化人士５号」に引き継がれる事となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is, in fact, a body double who has been made to look like the real Elan Ceres via plastic surgery and is referred to as "Enhanced Person \#4" by Peil Technologies. ⏎  ⏎ His body has been modified to allow him to pilot a GUND-ARM, and he takes an interest in Suletta under the belief she is the same in that regard. But as soon as he realizes she isn't, he challenges her to a duel. ⏎  ⏎ He loses to Suletta, but remembers a happy past when he initially believed there was nothing to him at all. However, he was removed from the mission by Peil Technologies after his body reached its limits and he could no longer fulfill his duty. ⏎  ⏎ Afterwards, he was replaced by "Enhanced Person \#5".

### dic\_pilot\_SYADIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b001\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるグラスレー・ディフェンス・システムズのＣＥＯであるサリウス・ゼネリの養子。 ⏎ 　アスティカシア高等専門学園パイロット科３年生でもあり、決闘委員会のメンバーを務める。 ⏎ 　学生でありながら、すでに多くの業務において実績を挙げており、グループ内の次世代幹部候補として期待されている。 ⏎ 　外向的な性格で飄々としているが、裏では策謀を巡らせる野心家の一面を持つ。
> EN (odniesienie oficjalne, NIE polski): Adopted son of Sarius Zenelli, the CEO of Grassley Defense Systems, one of the Benerit Group's Three Branches. ⏎  ⏎ A third-year piloting student at Asticassia School of Technology and a member of the Dueling Committee. ⏎  ⏎ Although still a student, he has shown his skill in business too, and is a candidate for Sarius's successor. Extroverted and easygoing, yet also is secretly a schemer full of ambition.

### dic\_pilot\_SYADIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b002\]
> JP (źródło tłumaczenia): 　ミオリネが立ち上げた株式会社ガンダムを手中に収めるため、彼女に交渉を持ち掛けるも拒否される。 ⏎ 　事態解決をかけてミオリネに決闘を申し込まれ、自らモビルスーツに乗ってグラスレー寮を率い、地球寮との団体戦に臨んだ。各機の連携により有利に戦いを進めるもミオリネの采配とスレッタ達の活躍の前に敗北し、ミオリネを守ろうとする秘めた想いも彼女に届く事はなかった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He tried to negotiate with Miorine for ownership of GUND-ARM Inc., but she refused. ⏎  ⏎ He then challenged Miorine to a duel to settle the matter once and for all, resulting in a team duel between Grassley House and Earth House where he piloted a Mobile Suit and commanded his house. His team gained the advantage in the duel through coordinated teamwork from Grassley House's units, only to lose against Miorine's command and the efforts of Suletta and the rest of Earth House, leaving his secret desire to protect Miorine to fall on deaf ears.

### dic\_pilot\_NKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b003\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科２年生。 ⏎ 　チュチュからは「ニカ姉」の愛称で呼ばれている。 ⏎ 　優しく穏やかな性格をしており、編入してきたスレッタに声をかけ、地球寮の一員となるきっかけを作った。 ⏎ 　メカニックとしての腕は優秀で、チュチュが搭乗するデミトレーナーのカスタムを手掛けた。
> EN (odniesienie oficjalne, NIE polski): A second-year mechanical department student belonging to Earth House. ⏎  ⏎ Is close with Chuchu. A kind and gentle person, she reached out to Suletta after the latter arrived at the school and was the one who sparked the events that led to her joining Earth House. ⏎  ⏎ She is a skilled mechanic who personally customized Chuchu's Demi Trainer.

### dic\_pilot\_NKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b004\]
> JP (źródło tłumaczenia): 　スレッタがフロント外宙域で決闘を行う際には、エアリアルに外部高機動推進ユニットを取り付ける作業を行った。 ⏎ 　しかし、地球寮の面々が知らない一面を持ち、シャディクとも密かにつながりを持っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Suletta must fight a duel in space outside the Front, Nika augmented Aerial with an external high-performance thruster unit. ⏎  ⏎ However, she has a side to her that the rest of Earth House is unaware of, as well as a secret connection with Shaddiq.

### dic\_pilot\_CHUCHU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b005\]
> JP (źródło tłumaczenia): 　地球寮に所属するパイロット科１年生。 ⏎ 　「チュチュ」の愛称で親しまれる。 ⏎ 　アーシアンを差別するスペーシアンを心の底から嫌っている。 ⏎ 　気が強く、学園で喧嘩騒ぎを起こす事も多い。 ⏎ 　ニカがカスタムしたデミトレーナー チュチュ専用機に搭乗する。
> EN (odniesienie oficjalne, NIE polski): A first-year piloting student belonging to Earth House, known as "Chuchu" to her friends. ⏎  ⏎ A strong-willed girl, she possesses a deep-seated hatred for Spacians who discriminate against Earthians, and frequently gets into fights on campus. ⏎  ⏎ Pilots a Demi Trainer customized for her use by Nika.

### dic\_pilot\_CHUCHU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b006\]
> JP (źródło tłumaczenia): 　当初はスペーシアンであるスレッタと距離を取っていたが、自分と同じく故郷の想いを背負っているとわかってからは次第に打ち解けていった。なお、地球寮の一員となったスレッタに対して、自分の方が先に入寮していた事から「先輩」と呼ばせている。 ⏎ 　ミオリネが株式会社ガンダムを設立した際には、兵器を売る事には強く反対したが、方針が医療事業に固まってからは故郷のためにも協力するようになった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though she initially kept her distance from Suletta on account of Suletta being a Spacian, she gradually opened her heart to Suletta after learning that she, too, cared deeply for her home. After Suletta joins Earth House, Chuchu makes Suletta treat her as a "senior" since Chuchu joined the house first. ⏎  ⏎ She was highly opposed to GUND-ARM Inc. selling weapons after Miorine establishes the company, but starts helping them out after they decide to focus on GUND technology's medical possibilities.

### dic\_pilot\_PROSPE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b007\]
> JP (źródło tłumaczenia): 　シン・セー開発公社のＣＥＯでガンダム・エアリアルの開発責任者。 ⏎ 　スレッタの母であり、彼女からは絶大な信頼を得ている。 ⏎ 　事故で失った右腕はGUND技術を用いた義手であり、身体補助のためにヘッドギアを装着している。
> EN (odniesienie oficjalne, NIE polski): CEO of Shin Sei Development Corporation, chief developer of Gundam Aerial, and Suletta's mother. ⏎  ⏎ Suletta trusts her more than anyone in the world. ⏎  ⏎ Having lost her right arm in an accident, she now wears a mechanical GUND-based prosthesis. She also wears special headgear that provides physical support.

### dic\_pilot\_PROSPE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b008\]
> JP (źródło tłumaczenia): 　２１年前に起こったヴァナディース事変の生き残りだが、そこから今日に至るまでの経緯や行動の目的は明かされていない。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She survived the Vanadis Incident twenty-one years ago, but how she got from there to her current position is a complete mystery.

### dic\_pilot\_DERING\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b009\]
> JP (źródło tłumaczenia): 　ベネリットグループ総裁でミオリネの父。　 ⏎ 　監査組織カテドラルの統括代表を務める他、アスティカシア高等専門学園の理事長も兼任している。 ⏎ 　厳格で独善とも言える強い決断力を有する。グループ内で絶大な権力を持つが、内部の敵も多い。 ⏎ 　娘に対してもその厳しさは変わらず、親子関係は冷え切っている。 ⏎ 　２１年前のヴァナディース事変の中心的人物であり、「GUNDフォーマット」の使用を禁じた人物でもある。
> EN (odniesienie oficjalne, NIE polski): President of the Benerit Group and Miorine's father. He is the supervising representative of the auditing organization Cathedra as well as the chairman of Asticassia School of Technology's board. A very decisive man with a personality that can be described as stern and self-righteous. ⏎  ⏎ Though he possesses immense power in the Group, he also has many enemies within it. His stern attitude applies to his daughter as well, and there appears to be little love lost between them. ⏎  ⏎ Twenty-one years ago, he was a central figure behind the Vanadis Incident, and he is also the one who banned the usage of the GUND Format.

### dic\_pilot\_DERING\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00a\]
> JP (źródło tłumaczenia): 　ミオリネが株式会社ガンダムを設立する際、一度はその甘さを指摘しつつも、出資者集めを手助けする一面を見せた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He chided Miorine for her naïveté after she established GUND-ARM Inc., yet also helped her raise funds for the enterprise.

### dic\_pilot\_SALIUS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00b\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるグラスレー・ディフェンス・システムズのＣＥＯ。 ⏎ 　老齢であるが、聡明さと鋭い洞察力を持ち合わせる。 ⏎ 　会社に養子のシャディクを参加させている。
> EN (odniesienie oficjalne, NIE polski): CEO of Grassley Defense Systems, one of the Three Branches of the Benerit Group. ⏎  ⏎ Is wise and possesses a keen insight despite his advanced age. Has brought his adopted son Shaddiq into the company.

### dic\_pilot\_SALIUS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00c\]
> JP (źródło tłumaczenia): 　株式会社ガンダムの設立を容認してエアリアルの処断を行わないデリングに疑いの目を向けている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He views Delling with suspicion for approving of the establishment of GUND-ARM Inc. and for not disposing of Aerial.

### dic\_pilot\_VIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00d\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるジェターク・ヘビー・マシーナリーのＣＥＯでグエルの父。 ⏎ 　野心的な経営者で、その剛腕でジェターク社をまとめ上げている。息子のグエルに厳しく接する。
> EN (odniesienie oficjalne, NIE polski): The CEO of Jeturk Heavy Machinery, one of the Benerit Group's Three Branches, and Guel's father. ⏎  ⏎ He is an ambitious manager whose capabilities enable him to hold Jeturk together. He is exceptionally harsh with his son.

### dic\_pilot\_VIM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00e\]
> JP (źródło tłumaczenia): 　デリングの暗殺を画策するも、グエルが決闘で敗北して「ホルダー」の地位を失った事によって計画は中止せざるをえなくなった。 ⏎ 　その後あらゆる手を尽くしてグエルを勝たせようとするが、再びスレッタに敗北、自らの考えに反してエランと決闘しまたも敗北したため、ジェターク寮から退寮させた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He had planned to assassinate Delling, only to have to call the whole thing off after Guel lost the title of Holder in a duel. ⏎  ⏎ Afterwards, he resorted to a number of schemes to get Guel to win duels, only for him to lose once again to Suletta, and then even, despite his expectations, to Elan. As a result, he kicked Guel out of Jeturk House.

### dic\_pilot\_NEWGEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b00f\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズの共同ＣＥＯの一人。 ⏎ 　四人による合議制でペイル社を経営している。
> EN (odniesienie oficjalne, NIE polski): One of the four CEOs of Peil Technologies, one of the Three Branches of the Benerit Group. ⏎  ⏎ She and other CEOs manage Peil via a parliamentary system.

### dic\_pilot\_NEWGEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b010\]
> JP (źródło tłumaczenia): 　他の三人と共に秘密裏に「GUND-ARM」を開発させ、そのパイロットとして強化人士を生み出している。 ⏎ 　ベネリットグループのインキュベーション・パーティーでは、エアリアルが「GUND-ARM」である事を訴え、破棄へと誘導しようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ They develop GUND-ARMs in secret and create Enhanced Persons to pilot them. ⏎  ⏎ Accuses Aerial of being a GUND-ARM at the Benerit Group's incubation party and attempts to have it disposed of.

### dic\_pilot\_KAL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b011\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズの共同ＣＥＯの一人。 ⏎ 　四人による合議制でペイル社を経営している。
> EN (odniesienie oficjalne, NIE polski): One of the four CEOs of Peil Technologies, one of the Three Branches of the Benerit Group. ⏎  ⏎ She and other CEOs manage Peil via a parliamentary system.

### dic\_pilot\_KAL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b012\]
> JP (źródło tłumaczenia): 　他の三人と共に秘密裏に「GUND-ARM」を開発させ、そのパイロットとして強化人士を生み出している。 ⏎ 　ベネリットグループのインキュベーション・パーティーでは、エアリアルが「GUND-ARM」である事を訴え、破棄へと誘導しようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ They develop GUND-ARMs in secret and create Enhanced Persons to pilot them. ⏎  ⏎ Accuses Aerial of being a GUND-ARM at the Benerit Group's incubation party and attempts to have it disposed of.

### dic\_pilot\_NEBORA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ea0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ea0b013\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズの共同ＣＥＯの一人。 ⏎ 　四人による合議制でペイル社を経営している。
> EN (odniesienie oficjalne, NIE polski): One of the four CEOs of Peil Technologies, one of the Three Branches of the Benerit Group. ⏎  ⏎ She and other CEOs manage Peil via a parliamentary system.

### dic\_pilot\_NEBORA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b000\]
> JP (źródło tłumaczenia): 　他の三人と共に秘密裏に「GUND-ARM」を開発させ、そのパイロットとして強化人士を生み出している。 ⏎ 　ベネリットグループのインキュベーション・パーティーでは、エアリアルが「GUND-ARM」である事を訴え、破棄へと誘導しようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ They develop GUND-ARMs in secret and create Enhanced Persons to pilot them. ⏎  ⏎ Accuses Aerial of being a GUND-ARM at the Benerit Group's incubation party and attempts to have it disposed of.

### dic\_pilot\_GOLNE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b001\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズの共同ＣＥＯの一人。 ⏎ 　四人による合議制でペイル社を経営している。
> EN (odniesienie oficjalne, NIE polski): One of the four CEOs of Peil Technologies, one of the Three Branches of the Benerit Group. She and other CEOs manage Peil via a parliamentary system.

### dic\_pilot\_GOLNE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b002\]
> JP (źródło tłumaczenia): 　他の三人と共に秘密裏に「GUND-ARM」を開発させ、そのパイロットとして強化人士を生み出している。 ⏎ 　ベネリットグループのインキュベーション・パーティーでは、エアリアルが「GUND-ARM」である事を訴え、破棄へと誘導しようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ They develop GUND-ARMs in secret and create Enhanced Persons to pilot them. Accuses Aerial of being a GUND-ARM at the Benerit Group's incubation party and attempts to have it disposed of.

### dic\_pilot\_RAUDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b005\]
> JP (źródło tłumaczenia): 　ジェターク寮の副寮長でパイロット科３年生。 ⏎ 　グエルとは同学年だが、異母兄弟で弟にあたる。 ⏎ 　冷静かつ理性的な性格をしているが、強く兄を想う一面を持つ。
> EN (odniesienie oficjalne, NIE polski): Third-year piloting student and deputy leader of Jeturk House. ⏎  ⏎ As Guel's half-sibling by another mother, Lauda is actually his younger brother even though they are in the same school year. ⏎  ⏎ He is coolheaded and rational, yet also cares deeply for his brother.

### dic\_pilot\_RAUDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b006\]
> JP (źródło tłumaczenia): 　グエルが退寮となってからは寮長として周囲をまとめる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Takes over the house after Guel is kicked out.

### dic\_pilot\_FELCY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b007\]
> JP (źródło tłumaczenia): 　ジェターク寮に所属するパイロット科２年生。 ⏎ 　先輩のグエルをパイロットとして尊敬している。 ⏎ 　冷やかし好きで調子に乗りやすい性格。 ⏎ 　ペトラと二人で行動している事が多い。
> EN (odniesienie oficjalne, NIE polski): A second-year piloting department student belonging to Jeturk House. ⏎  ⏎ Respects her upperclassman Guel as a pilot. ⏎  ⏎ Likes wisecracks and tends to get ahead of herself. ⏎  ⏎ Often seen with Petra.

### dic\_pilot\_FELCY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b008\]
> JP (źródło tłumaczenia): 　グエルとスレッタの二度目の決闘では、グエルを勝利させるため、ペトラと共に管理システムを作動させて戦術試験区域に水散布を行った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Activates the control system and deploys sprinklers in the tactical testing sector with Petra during Guel's second duel with Suletta to help Guel win.

### dic\_pilot\_PETRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b009\]
> JP (źródło tłumaczenia): 　ジェターク寮に所属するメカニック科２年生。 ⏎ 　グエルを慕う後輩で、よくフェルシーと二人で行動している。 ⏎ 　知的でクールな雰囲気を持つが、フェルシーの冷やかしに便乗する事も多い。
> EN (odniesienie oficjalne, NIE polski): A second-year mechanical department student belonging to Jeturk House. ⏎  ⏎ Looks up to Guel and is rarely seen separated from Felsi. Though coolheaded and the smart type, she frequently joins in with Felsi's teasing.

### dic\_pilot\_PETRA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b00a\]
> JP (źródło tłumaczenia): 　グエルとスレッタの二度目の決闘では、グエルを勝利させるため、フェルシーと共に管理システムを作動させて戦術試験区域に水散布を行った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Activates the control system and deploys sprinklers in the tactical testing sector with Felsi during Guel's second duel with Suletta to help Guel win.

### dic\_pilot\_SSRIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b00b\]
> JP (źródło tłumaczenia): 　ブリオン寮に所属する経営戦略科２年生。 ⏎ 　決闘委員会のメンバーを務めている。 ⏎ 　皮肉屋で口が悪い。
> EN (odniesienie oficjalne, NIE polski): A second-year management strategy student belonging to Burion House. ⏎  ⏎ Serves as a member of the Dueling Committee. Has a sharp and sarcastic tongue.

### dic\_pilot\_ROUJI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b00d\]
> JP (źródło tłumaczenia): 　ブリオン寮に所属するメカニック科１年生。 ⏎ 　セセリアと共に決闘委員会のメンバーを務める。 ⏎ 　物静かな性格で、自身で改造したハロをよく抱えている。
> EN (odniesienie oficjalne, NIE polski): A first-year mechanical department student belonging to Burion House. ⏎  ⏎ He serves as a member of the Dueling Committee alongside Secelia. The quiet type, he is frequently seen carrying around a personally customized Haro.

### dic\_pilot\_MALTN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b00f\]
> JP (źródło tłumaczenia): 　地球寮の寮長で経営戦略科３年生。 ⏎ 　優柔不断な性格をしており、よく不安を口にする。 ⏎ 　個性の強い地球寮のメンバーに振り回される事が多いが、当惑しながらも必死に寮長の務めを果たそうとする。
> EN (odniesienie oficjalne, NIE polski): A third-year management strategy student who is the head of Earth House. An indecisive type who frequently voices his concerns. ⏎  ⏎ Though he is often strung around to the point of bewilderment by the strong personalities of Earth House, he does his best to fulfill his duties as house leader regardless.

### dic\_pilot\_MALTN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b010\]
> JP (źródło tłumaczenia): 　グラスレー寮との決闘ではパイロットとして参加したが、為す術もなく無力化された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Participated as a pilot in the duel with Grassley House, but was taken out of action before he had a chance to contribute.

### dic\_pilot\_NUNO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b011\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科２年生。 ⏎ 　ソフトウェアに精通している。 ⏎ 　戦争孤児だが、アーシアンが置かれた立場を達観している所がある。 ⏎ 　オジェロとは気の合う悪友の仲で、共に決闘の勝敗を予想するギャンブルに熱中している。
> EN (odniesienie oficjalne, NIE polski): A second-year mechanical department student belonging to Earth House. ⏎  ⏎ Has a solid knowledge of software. ⏎  ⏎ Though a war orphan, he has an unbiased opinion of the plight of the Earthians. He and Ojelo are partners in crime who are more than happy to bet on the outcomes of Duels.

### dic\_pilot\_NUNO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b012\]
> JP (źródło tłumaczenia): 　株式会社ガンダムの事業方針をめぐって一時はオジェロと険悪なムードになるも、会社のプロモーションビデオ製作を経て仲直りした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Had a bit of a temporary falling-out with Ojelo over the direction to take GUND-ARM Inc., but the two reconciled their issues when they made a commercial for the company. 

### dic\_pilot\_OJRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b013\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科２年生。 ⏎ 　陽気な性格で、地球寮の中でもムードメーカー的な存在。 ⏎ 　悪友のヌーノと共に決闘の勝敗を予想するギャンブルに寮の生活費を注ぎ込んでいる。
> EN (odniesienie oficjalne, NIE polski): A second-year mechanical department student belonging to Earth House. ⏎  ⏎ A cheerful type who often lightens the mood for Earth House. Wagers his very important living-expenses allowance on bets over the outcomes of duels with his partner in crime Nuno.

### dic\_pilot\_OJRO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b014\]
> JP (źródło tłumaczenia): 　株式会社ガンダムの事業方針をめぐって一時はヌーノと険悪なムードになるも、会社のプロモーションビデオ製作を経て仲直りした。 ⏎ 　グラスレー寮との決闘ではパイロットとして参加したが、為す術もなく無力化された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Had a temporary falling-out with Nuno over the direction to take GUND-ARM Inc., but the two reconciled their issues when they made a commercial for the company. ⏎  ⏎ Participated as a pilot in the duel with Grassley House, but was taken out of action before he had a chance to contribute.

### dic\_pilot\_TIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b015\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科３年生。 ⏎ 　冷静かつ物静かな性格で、地球寮を支える縁の下の力持ち的な存在。
> EN (odniesienie oficjalne, NIE polski): A third-year mechanical department student belonging to Earth House. ⏎  ⏎ Calm and taciturn, he is an unsung hero who supports the other members of the house.

### dic\_pilot\_TIL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b016\]
> JP (źródło tłumaczenia): デザインセンスがあり、ミオリネの依頼で株式会社ガンダムのロゴを作成した。 ⏎ 　グラスレー寮との決闘ではパイロットとして参加し、エナオからメカニック科にしては筋がいいと評された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He has a natural design sense, and at Miorine's request, he designed the logo for GUND-ARM Inc. ⏎  ⏎ Participated as a pilot in the duel with Grassley House, and was praised by Henao for having good instincts despite being registered under the mechanical department.

### dic\_pilot\_RRKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b017\]
> JP (źródło tłumaczenia): 　地球寮に所属する経営戦略科１年生。 ⏎ 　明るく親しみやすい性格で男子生徒によくモテる。 ⏎ 　恋バナが大好き。
> EN (odniesienie oficjalne, NIE polski): A first-year management strategy student belonging to Earth House. ⏎  ⏎ She is a cheerful and easygoing girl who is popular with the male students. Loves to gossip about romances.

### dic\_pilot\_RRKE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b018\]
> JP (źródło tłumaczenia): 　グラスレー寮との決闘では、男子生徒をめぐってレネに言いがかりをつけられた事でパイロットとして参加した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Participated as a pilot in the team duel with Grassley House after Renee personally challenged her over a false accusation regarding a male student.

### dic\_pilot\_ALYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b019\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科３年生。 ⏎ 　マイペースな性格で占いと家畜を愛する。 ⏎ 　故郷からヤギ、ヤク、ニワトリを地球寮に連れてきて飼育している。
> EN (odniesienie oficjalne, NIE polski): A third-year mechanical department student belonging to Earth House. ⏎  ⏎ She's generally unbothered by the chaos around her, and loves both fortune telling and livestock. ⏎  ⏎ She raises goats, yaks, chickens, and so on that she brought to Earth House from her hometown.

### dic\_pilot\_ALYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b01a\]
> JP (źródło tłumaczenia): 　グラスレー寮との決闘ではオペレーターとして参加した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Participates as an operator in Duels with Grassley House.

### dic\_pilot\_BELME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b01d\]
> JP (źródło tłumaczenia): 　ペイル・テクノロジーズ所属の技術研究員。 ⏎ 　ガンダム・ファラクトの開発に携わっており、エランの身体調整も担当する。 ⏎ 　２１年前のヴァナディ―ス事変の生き残りであり、当時はプロスペラの後輩であった。
> EN (odniesienie oficjalne, NIE polski): A technical researcher with Peil Technologies. ⏎  ⏎ She was involved in the development of the Gundam Pharact and is in charge of Elan's physical conditioning. ⏎  ⏎ She is a survivor of the Vanadis Incident twenty-one years ago, at which time she was working with Prospera.

### dic\_pilot\_BELME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b01e\]
> JP (źródło tłumaczenia): 　GUND技術の理想を夢見ながらも、その身を守るためにペイル社に協力しており、内心ではやりきれない思いを抱えている。 ⏎ 　株式会社ガンダムがGUND医療を扱う事業方針を打ち出してからは、ミオリネ達をサポートするようになる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though she believes in the possibilities of GUND technology, she works with Peil to save her own skin, which deep down fills her with guilt. ⏎  ⏎ Since they adopted using GUND technology for medical applications as its mission, she has been providing support to Miorine and her companions.

### dic\_pilot\_SABINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8ee0b01f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8ee0b01f\]
> JP (źródło tłumaczenia): 　グラスレー寮に所属するパイロット科３年生。 ⏎ 　シャディクの右腕として、学園内外の仕事を補佐している。 ⏎ 　冷静な性格で凛々しい雰囲気を持つ。
> EN (odniesienie oficjalne, NIE polski): A third-year piloting student belonging to Grassley House. ⏎  ⏎ She serves as Shaddiq's right hand, assisting him in his work both in and out of school. A calm and imposing individual.

### dic\_pilot\_RENE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b000\]
> JP (źródło tłumaczenia): 　グラスレー寮に所属するパイロット科２年生。 ⏎ 　シャディクを支える五人の女子生徒の一人。 ⏎ 　快活だが腹黒い性格で、男子の前と女子の前では態度を変える。 ⏎ 　学園内に多数のファンを抱えている。
> EN (odniesienie oficjalne, NIE polski): A second-year piloting student belonging to Grassley House and one of the five female students who support Shaddiq. ⏎  ⏎ Though she seems lighthearted, she is a malicious person who behaves differently with boys than with other girls. Has many fans all around the school.

### dic\_pilot\_RENE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b001\]
> JP (źródło tłumaczenia): 　団体戦となった地球寮との決闘では、自身がキープしている男子に恥をかかせたとしてリリッケに言いがかりをつけた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She falsely accused Lilique of humiliating one of her backup boyfriends at the team duel with Earth House.

### dic\_pilot\_ILIJA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b002\]
> JP (źródło tłumaczenia): 　グラスレー寮に所属するパイロット科２年生。 ⏎ 　シャディクを支える五人の女子生徒の一人。 ⏎ 　気弱で心配性な性格で、いつもぬいぐるみを抱えている。 ⏎ 　メイジーと特に仲がいい。
> EN (odniesienie oficjalne, NIE polski): A second-year piloting student belonging to Grassley House and one of the five female students who support Shaddiq. ⏎  ⏎ Always carries a stuffed animal due to her timid and anxious personality. ⏎  ⏎ Good friends with Maisie.

### dic\_pilot\_MAYG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b004\]
> JP (źródło tłumaczenia): 　グラスレー寮に所属するパイロット科２年生。 ⏎ 　シャディクを支える五人の女子生徒の一人。 ⏎ 　圧倒的なポジティブ思考の持ち主。 ⏎ 　イリーシャと特に仲がいい。
> EN (odniesienie oficjalne, NIE polski): A second-year piloting student belonging to Grassley House and one of the five female students who support Shaddiq. ⏎  ⏎ An optimist to an extreme degree. ⏎  ⏎ Good friends with Ireesha.

### dic\_pilot\_EONA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b006\]
> JP (źródło tłumaczenia): 　グラスレー寮に所属するパイロット科３年生。 ⏎ 　シャディクを支える五人の女子生徒の一人。 ⏎ 　寡黙でミステリアスな雰囲気を持つ。 ⏎ 　いつも精神を研ぎ澄ませ、第六感を働かせている。
> EN (odniesienie oficjalne, NIE polski): A third-year piloting student belonging to Grassley House and one of the five female students who support Shaddiq. ⏎  ⏎ The quiet and mysterious type, she is always honing her mind and utilizing her sixth sense.

### dic\_pilot\_SHOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b008\]
> JP (źródło tłumaczenia): 　ダンバインおよびビルバインのパイロットである日本人の青年。１８歳。 ⏎ 　地上にいた頃はモトクロッサー志望の青年であったが、エ・フェラリオのシルキー・マウによってバイストン・ウェルに招喚され、ダンバインのパイロットとなる。 ⏎ 　当初は状況に流されドレイクの味方をしていたが、マーベルとの出会いを経て、自らの意志で反ドレイク側に回る。その高いオーラ力からすぐに反ドレイク側勢力の中核を担い始め、味方からは聖戦士として頼られるようになる。 ⏎ 　本人はそういった扱いを面映ゆく思っている事が多かったが、戦いが進むに連れ徐々に自分の役割を認識し、戦士として、ニーの片腕としてその役割を全うし始める。 ⏎ 　経営コンサルタントの父と教育評論家の母を持つが、初めて地上へ帰還した際に再会した彼らはショウの生き方を認めることができずに決別。以降、ショウは地上への未練を捨て、バイストン・ウェルを自分の居場所と認識するようになる。 ⏎ 　全てのオーラマシンが地上へ展開してからは、地上にまで広がってしまったバイストン・ウェルの戦いを止める為に奔走する。
> EN (odniesienie oficjalne, NIE polski): The Japanese pilot of the Dunbine and Billbine. 18 years old. ⏎  ⏎ He was an aspiring motocross rider but became the Dunbine's pilot after being summoned to Byston Well by the E Ferario, Silky Mau. ⏎  ⏎ Caught up in his new situation, he was initially Drake's ally, but switched to the anti-Drake force after meeting Marvel and starting to think on his own. His high Aura Power proved valuable, and he immediately became the core of the anti-Drake forces, gaining the trust of his new allies as a Battler. He himself is embarrassed being treated as such, but gradually accepts his role as the battle progresses, embracing his role as a Battler and as Nie's right-hand man. ⏎  ⏎ His father is a management consultant while his mother is an education critic. When he first returned to Upper Earth and reunited with his parents, they were unable to accept that he was still alive, and they parted ways. After that, Show threw away all his attachments to Upper Earth, making a place for himself in Byston Well. ⏎  ⏎ Eventually, Aura Machines and the war in Byston Well spread to Upper Earth. Show went berserk in order to stop everything.

### dic\_pilot\_SHOU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b009\]
> JP (źródło tłumaczenia): 　最終決戦では因縁の敵であるバーンと相打ちに近い形で決着をつけ、シーラの浄化で地上から姿を消した。
> EN (odniesienie oficjalne, NIE polski):  In the final battle, he went head to head against his destined enemy, Bern. It was a close fight, but Bern disappeared from Upper Earth following Ciela's purification.

### dic\_pilot\_MARBL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00a\]
> JP (źródło tłumaczenia): 　ダンバインのパイロットを務めるアメリカ人の女性。１８歳。 ⏎ 　エ・フェラリオのナックル・ビーによってバイストン・ウェルに招喚された。 ⏎ 　ショウより先に招喚されており、反ドレイクの考えに賛同すると同時に、ニーに惹かれた事から、ギブン家に協力する。 ⏎ 　ショウにドレイクの悪を諭して味方に加え、以後は彼の想いを受け止め、互いのオーラ力を高めていく。 ⏎ 　東洋思想を学ぶ理知的な性格と同時に、激しい感情を露にする一面を持つ。 ⏎ 　乗機はダーナ・オシー、ボゾン、ボチューンと反ドレイク側オーラ・バトラーの最新鋭機を乗り継ぎ、最終的にショウのダンバインを譲り受ける。
> EN (odniesienie oficjalne, NIE polski): The American woman who pilots the Dunbine. Age 18. ⏎  ⏎ She was summoned to Byston Well by the E Ferario Knuckle Bee. ⏎  ⏎ She arrives before Show and aids House Given, both because she opposes Drake and because she's drawn to Nie. ⏎  ⏎ She gains Show's alliance by showing him Drake's evil intentions. Afterward, she comes to his viewpoint, and both pilots help raise the other's Aura Power. ⏎  ⏎ While she's an intellectual with an interest in studying Asian philosophy, she can also show intense emotions. ⏎  ⏎ She piloted the Dana-O'Shee, the Bozune, and the Botune, a series of cutting-edge Aura Battlers used by the anti-Drake faction, before taking over the Dunbine from Show.

### dic\_pilot\_MARBL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00b\]
> JP (źródło tłumaczenia): 　最終決戦ではショウと力を合わせショットのスプリガンを撃墜するも、バーンの駆るガラバによって致命傷を負わされ、ショウを戦いへと向かわせながら散っていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle, she joins forces with Show to attack Shot in his Spriggan. She was fatally injured by Bern in the Gallaba. Turning Show towards the battle, she passes away.

### dic\_pilot\_CHAM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00c\]
> JP (źródło tłumaczenia): 　ギブン家に協力するミ・フェラリオ。 ⏎ 　当初はニー・ギブンに想いを寄せ、ドレイク側にいたショウを半ば敵視していたが、ショウと行動を共にするに連れ、大切なパートナーとなる。 ⏎ 　戦闘中はショウの傍らで共に戦い、それ以外にも偵察や敵のかく乱に活躍する。 ⏎ 　家事にも長けており、着用している戦闘服は自らの手作りである。
> EN (odniesienie oficjalne, NIE polski): The Mi Ferario in service of House Given. ⏎  ⏎ Initially serving Nie Given, she viewed Show, who was at Drake's side, as an enemy. Through working with Show, she comes to treat him as a valuable partner. ⏎  ⏎ She fights alongside Show in battle, conducts reconnaissance, and disrupts the enemy. Besides that, she excels in doing housework. The battle uniform she wears is handmade.

### dic\_pilot\_CHAM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00d\]
> JP (źródło tłumaczenia): 　最後の戦いの後もただ一人地上に残され、地上の人々にショウたちの戦いの記録を伝えた後、人知れず姿を消した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She remains alone in Upper Earth after the final battle, disappearing after recording the events that transpired.

### dic\_pilot\_NEE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00e\]
> JP (źródło tłumaczenia): 　アの国の地方領主ロムン・ギブンの息子。２３歳。 ⏎ 　オーラ・シップ「ゼラーナ」の艦長を務め、ショウ達一行のリーダー役。戦闘では指揮を執る事が多いが、戦況に応じてオーラ・バトラーに搭乗する事もある。 ⏎ 　バイストン・ウェルの支配を目論むドレイクの野望を阻止するため、ショウやマーベル達と共に戦ってきた。 ⏎ 　当初は想いを寄せていたドレイクの娘・リムルに振り回されていた事でショウ達との対立も多かったが、戦いを経て大きく成長していった。
> EN (odniesienie oficjalne, NIE polski): The son of Romn Given, one of the lords of the Land of Ah. Age 23. ⏎  ⏎ Working as the captain of the Aura Ship Zelerna, he is the leader of the group Show's part of. ⏎  ⏎ Though he usually stays in a commander's role during combat, he will also join the battle in his own Aura Battler if the situation demands it.  ⏎  ⏎ He fought together with Show, Marvel, and the others to end Drake's ambition of taking over Byston Well. ⏎  ⏎ At first he let his affection for Drake's daughter Riml influence his actions, causing him to butt heads with Show and the others, but he grew in many ways across his countless battles.

### dic\_pilot\_NEE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b00f\]
> JP (źródło tłumaczenia): 　最終決戦では、リムルを殺害したドレイクの妻・ルーザとドレイクを討ち取りその悲願を果たすも直後に戦死を遂げた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle he fulfilled his desire to end the life of Drake, as well as Drake's wife Louser, who had killed his beloved Riml. He sadly met his own end soon after.

### dic\_pilot\_KEEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b010\]
> JP (źródło tłumaczenia): 　ギブン家に仕えてきたキッス家の娘。１６才。 ⏎ 　正義感が強く、純粋な性格。 ⏎ 　想いを寄せているニーに付き従い、オーラ・シップ「ゼラーナ」に乗り込む。 ⏎ 　戦いの中、一族を守るためにドレイク軍に与した父と戦う事になり、その苦難を契機に意志を強く固める。 ⏎ 　足手まといになる事を好まず、オーラ・バトラーに乗ってショウ達をサポートし、戦士として成長していった。
> EN (odniesienie oficjalne, NIE polski): The daughter of the Kiss family, retainers to House Given. Age 16. ⏎  ⏎ She joins the crew of the Aura Ship Zelerna following her feelings for Nie.  ⏎  ⏎ In the course of the war she is forced to cross swords with her own father, who serves the Drake Army in order to protect his household. The intense fights only serve to strengthen her will. ⏎  ⏎ Not wanting to hold her comrades back, she pilots an Aura Battler alongside Show and becomes a warrior in her own right.

### dic\_pilot\_KEEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b011\]
> JP (źródło tłumaczenia): 　最終決戦ではミュージィ・ポーの駆るブブリィの攻撃によって戦死した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle she is shot down by a Bubury piloted by Musiy Poe.

### dic\_pilot\_SHIRA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b012\]
> JP (źródło tłumaczenia): 　ナの国の女王。１７歳。 ⏎ 　その高潔なオーラ力から聖少女と呼ばれ、常に女王としての威厳と気品を併せ持つ。 ⏎ 　自らの使命と責任からグラン・ガランを建造させ、反ドレイク側の旗頭として戦う。 ⏎ 　また、自らの危機を救ったショウを真の聖戦士と認め、最新鋭オーラ・バトラー・ビルバインを託す。 ⏎ 　しかし、力に力で対抗する自らを含め、オーラマシンによって変わっていくバイストン・ウェル全体を憂い、ドレイク打倒を果たした後は全てのオーラマシンの破棄を決めていた。 ⏎ 　地上へ送られてからは、ドレイク軍と戦うと同時に地上に無用の混乱を呼ばぬよう尽力する。その方法としてイギリス女王との会見も行った。
> EN (odniesienie oficjalne, NIE polski): The Queen of the Land of Na. Age 17. ⏎  ⏎ She is known as the Holy Maiden because of her refined Aura Power, and always maintains her regal bearing and poise. ⏎  ⏎ She saw the construction of the Gran-Garan as her duty and her responsibility, and it becomes the flagship of the anti-Drake forces. ⏎  ⏎ When Show puts himself in danger, she recognizes him as a true Battler and entrusts him with the Billbine, a cutting-edge Aura Battler. ⏎  ⏎ However, she laments the way Aura Machines are changing all of Byston Well, making power oppose power, her own actions included. After Drake is defeated, she decides to eliminate all Aura Machines. ⏎  ⏎ When the battle is moved to Upper Earth, she does her best to keep it from senseless destruction even as she fights the Drake Army. She even has a meeting with the Queen of England as part of those efforts.

### dic\_pilot\_SHIRA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b013\]
> JP (źródło tłumaczenia): 　太平洋での最終決戦において、持てるオーラ力を解放し全ての悪しきオーラを浄化した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle over the Pacific, she released all her Aura Power and purified all evil aura.

### dic\_pilot\_KAWASE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b014\]
> JP (źródło tłumaczenia): 　オーラ・バトル・シップ「グラン・ガラン」の艦長。 ⏎ 　ナの国の女王シーラの忠臣で、陣頭に立つ彼女を傍らから支える。
> EN (odniesienie oficjalne, NIE polski): Captain of the Aura Battleship Gran-Garan. ⏎  ⏎ As one of Queen Ciela's loyal subjects from the Land of Na, he chooses to support her at her side as she takes command.

### dic\_pilot\_KAWASE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b015\]
> JP (źródło tłumaczenia): 　最終決戦では操舵手を失ったグラン・ガランを自ら操り、ドレイクの乗るオーラ・バトル・シップ「ウィル・ウィプス」へ特攻した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the last battle, after the Gran-Garan loses its helmsman, he takes the helm himself and rams the ship into Drake's Aura Battleship, the Will-Wips.

### dic\_pilot\_ELDN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b016\]
> JP (źródło tłumaczenia): 　女王シーラと行動を共にするミ・フェラリオ。 ⏎ 　口調が荒く、気が強い。 ⏎ 　何十年かに一度現れる嵐の玉にシーラと囚われていたところをショウによって救出された。 ⏎ 　シーラを慕い、ベル・アールと共に苦悩するシーラの身を案じる。
> EN (odniesienie oficjalne, NIE polski): A Mi Ferario that accompanies Queen Ciela. ⏎  ⏎ She is strong-willed with a sharp tongue. ⏎  ⏎ She was trapped within a Storm Sphere, a magical phenomena that only appears once every few decades, until she and Ciela were freed by Show. ⏎  ⏎ She adores Ciela and, together with Bell Arle, worries constantly over her queen.

### dic\_pilot\_EEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b018\]
> JP (źródło tłumaczenia): 　女王シーラと行動を共にするミ・フェラリオ。 ⏎ 　無邪気な性格で、子供じみたわがままを言う事も多い。 ⏎ 　シーラが負傷した際には食事を運んだり、その身を案じたりする等、健気な一面も持っている。
> EN (odniesienie oficjalne, NIE polski): A Mi Ferario who accompanies Queen Ciela. ⏎  ⏎ She has an innocent personality and often makes selfish requests like a child would. ⏎  ⏎ However, when Ciela was injured, she carried her food and looked after the Queen's safety, showing that she has a caring side as well.

### dic\_pilot\_DREIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b01a\]
> JP (źródło tłumaczenia): 　アの国の王。 ⏎ 　元々は地方領主に過ぎなかったが、地上人を招喚させてオーラマシンの開発を進め、前国王フラオン・エルフから武力で王位を奪った。 ⏎ 　バイストン・ウェル全てを支配する野望を抱いており、その力としてオーラ・バトル・シップのウィル・ウィプスを建造させた。 ⏎ 　知略と決断力と先見性に優れるだけでなく、冷酷さと情を併せ持ち、その強大なオーラ力と合わせて王に相応しい器を持った人物。
> EN (odniesienie oficjalne, NIE polski): The king of the Land of Ah. He was once merely a provincial lord. However, with the power of the Upper Earthers he summoned and the Aura Machines he had developed, he was able to take the crown from the former king, Folown Elf, by force.  ⏎  ⏎ Desiring to take control of all of Byston Well, he had the Will-Wips, a powerful Aura Battleship, developed.  ⏎  ⏎ Gifted with not only wisdom, decisiveness, and foresight, he is also able to strike a balance between ruthlessness and compassion. Add to this his immense Aura Power and you have a man seemingly worthy of his crown.

### dic\_pilot\_DREIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b01b\]
> JP (źródło tłumaczenia): 　戦いの舞台が地上へと移ってからは、その野望は二つの世界の制覇へと拡大していった。 ⏎ 　しかし戦いの中、妻ルーザが同盟を結んでいたクの国の王ビショット・ハッタと裏で通じていた事に気づき、己の野望が彼等に利用されていた事を知る。 ⏎ 　ルーザとビショットが死んだ後、決戦の最中に戦線離脱して再起を図ろうとするが、最期はニーによって討たれた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the conflict in Byston Well spread to the overworld, so too did his ambitions expand in turn. ⏎  ⏎ However, during the conflict, he learned of secret communications between his wife, Louser, and Bishot Hatta, king of the Kingdom of Ku, his erstwhile ally. He realized then that they had been using his ambitions for their own ends.  ⏎  ⏎ Once Louser and Bishot were dead, he attempted to flee in the middle of the final battle to regroup, rebuild and attempt to fulfill his ambitions another day. He was instead ignominiously shot down by Nie.

### dic\_pilot\_BURN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b01c\]
> JP (źródło tłumaczenia): 　かつてドレイク軍の指揮官であった騎士。 ⏎ 　騎士道精神を重んじる一方で、策謀家でもあり、自信家でもある。 ⏎ 　戦功を挙げてドレイクの後継者となる事を画策していたが、ショウに度重なる敗北を喫し、地位を剝奪されて失脚した。 ⏎ 　名誉も栄光も失った後、全ての原因がショウにあると考え、復讐のために素顔を隠して「黒騎士」となって戦場に現れた。
> EN (odniesienie oficjalne, NIE polski): A former officer and knight under Drake. ⏎  ⏎ Though he follows the path of chivalry, he is also a schemer with immense pride in his own abilities. ⏎  ⏎ He planned to use military success to propel himself onto Drake's throne, until he fell from grace and was stripped of his position after countless defeats at Show's hands. ⏎  ⏎ Bereft of his honor, he blamed all his failures on Show and returned to the battlefield to claim vengeance under the guise of the Black Knight.

### dic\_pilot\_BURN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b01d\]
> JP (źródło tłumaczenia): 　戦いでは、激しい憎悪によって増大したオーラ力でショウを圧倒した。 ⏎ 　最終決戦では生身でショウと対峙して刺し違え、女王シーラにより浄化された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In their new confrontation, he overpowered Show with the intense Aura Power created by his hatred. ⏎  ⏎ He and Show stabbed each other in a final, bare-fisted fight before he was put to rest thanks to the purification of Queen Ciela.

### dic\_pilot\_JAKOBA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8f20b01e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8f20b01e\]
> JP (źródło tłumaczenia): 　フェラリオの長。 ⏎ 　バイストン・ウェルのフェラリオ達が住む水の国を治めている。 ⏎ 　厳格な性格で、当初はショウ達に非協力的であったが、世界の秩序が乱れていく様を目の当たりにし、オーラマシンの排除をショウ達に依頼した。 ⏎ 　しかし、なおも戦火が拡大するバイストン・ウェルを見て、自らの力を以て全てのオーラマシンを地上へ転移させるが、その代償として急速に老化した。
> EN (odniesienie oficjalne, NIE polski): The elder of the Ferario who governs the Kingdom of Water where the Ferario of Byston Well dwells. Though at first, this strict ruler refused to help Show and his companions, she later relented and requested that they destroy the Aura Machines when she saw the chaos they were bringing to the world with her own eyes. ⏎  ⏎ However, when she saw that this only served to spread the conflict wider across Byston Well, she used the extent of her power to send the Aura Machines to Upper Earth, instantly aging herself in the process.

### dic\_pilot\_TODO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b000\]
> JP (źródło tłumaczenia): 　ショウと共にバイストン・ウェルに招喚された地上人。２３歳。 ⏎ 　ドレイク及びビショットの配下の聖戦士として何度もショウの前に立ちはだかる。 ⏎ 　地上にいた頃はボストン出身の空軍パイロット候補生だった。 ⏎ 　本来は何事も前向きに考える快活な性格であったが、ドレイクを裏切って敵となったショウに敗北を重ねる内に、彼に対し強い執着を持つようになる。 ⏎ 　ドレイクの企みを知っても騎士としての待遇が約束されているドレイクに与するなど、利己的な面も持つが、空軍時代の先輩であるアレンに対抗心を燃やしたり、度々母を心配したりするなど、ナイーブな面も持っている。 ⏎ 　一度、ショウとの戦いに敗れて消息不明となるも、後にクの国の聖戦士として戦線へと復帰。ビアレスを駆って再びショウをつけ狙うようになる。 ⏎ 　愛機は専用カラーのダンバイン、ドラムロを経て、再登場後はビアレス、ライネックを駆る。 ⏎ 　地上へと浮上した後は執着だけでなく、母の住まうボストンを守りたいという意志からもショウを狙うようになり、その力はさらに増大していく。 ⏎ 　しかし、増大し過ぎたオーラ力はハイパー化を招いてしまい、死闘の末ショウに討ち取られた。 ⏎ 　この戦いでドレイクは彼の働きを認め、ボストンだけは攻撃しないことを決めた。
> EN (odniesienie oficjalne, NIE polski): An Upper Earther who was summoned to Byston Well along with Show. 23 years old. He stood in Show's way on many occasions as Drake's and Bishot's subordinate. He was born in Boston, and was an Air Force pilot candidate. ⏎  ⏎ He was originally an optimistic and cheerful person. After Show betrayed Drake and won against Tod on multiple occasions, he became obsessed with Show. Even after finding out Drake's plans, he selfishly served at Drake's side for the promised remuneration. He also has a naive side, evinced in his rebelliousness against his senior in the Air Force, and always worries about his mother. ⏎  ⏎ He once disappeared after losing to Show in battle, but reappeared as a Battler for the Kingdom of Ku, piloting the Vierres against Show. ⏎  ⏎ He pilots a customized color Dunbine and a Drumlo. After reappearing, he pilots the Vierres and Wryneck. ⏎  ⏎ After surfacing to Upper Earth, he was driven to protect Boston where his mother lived, in addition to his obsession with Show. This caused his power to greatly increase. However, it was too much, and he went Hyper, going after Show in a battle to the death. Drake decided not to attack Boston in recognition of his efforts.

### dic\_pilot\_AREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b002\]
> JP (źródło tłumaczenia): 　ショウ達に続いてドレイクが招喚した地上人の一人。 ⏎ 　アメリカ空軍のエースパイロットでトッドの先輩にあたる。 ⏎ 　冷めた性格の裏で状況を見る眼力に長けており、バイストン・ウェルに招喚された自分達が実際は傭兵に過ぎないことを正確に把握していた。 ⏎ 　同時に自分からドレイク軍を利用しようとするしたたかさも併せ持つ。 ⏎ 　その高い戦闘力でショウ達を苦しめるが、ラウ攻防戦の中、ビルバインに乗り換えたショウに敗れる。
> EN (odniesienie oficjalne, NIE polski): One of the Upper Earthers summoned by Drake after Show and the others. ⏎  ⏎ He is a pilot with the American air force and also Tod's senior. ⏎  ⏎ Behind his cool personality lies excellent situational perception, accurately grasping that those summoned to Byston Well were nothing more than mercenaries. He also thought to manipulate the Drake Army, showing a stubborn side.  ⏎  ⏎ His high combat abilities gave Show and the others a tough time, but he eventually lost to Show in the assault on Rau when Show upgraded to the Billbine.

### dic\_pilot\_JRIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b004\]
> JP (źródło tłumaczenia): 　ショウ達に続いてドレイクが招喚した地上人の一人。 ⏎ 　アイルランド出身のロックシンガーでメッシュを入れた赤い髪を持つ。 ⏎ 　攻撃的な性格を持ち、バイストン・ウェルでの戦争をゲームのように楽しんでいた。 ⏎ 　地上に戻った後は故郷のアイルランドからギリシアに渡り、そのオーラ力でギリシア軍を傘下に置く。空軍の戦闘機を従えて、レプラカーンで飛ぶ様をパイロット達は「２０世紀のジャンヌ・ダルク」と評した。 ⏎ 　しかし、ショウとマーベルとの戦闘の中、怒りと憎しみのオーラ力を暴走させ、初のハイパー化現象を引き起こす。その強大な力でビルバインを追いつめるが、最後は暴走するオーラ力を制御できずに自滅していった。
> EN (odniesienie oficjalne, NIE polski): One of the Upper Earthers summoned by Drake after Show and the others. A rock singer from Ireland, she has highlights in her flaming red hair. With her aggressive personality, she enjoys the war in Byston Well as if it were a game. ⏎  ⏎ After returning to Upper Earth, she traveled from her homeland, Ireland, all the way to Greece. There, she became affiliated with the army with her high Aura Power where she commanded the combat air force. Flying through the skies in the Leprechaun, her visage earned her the name of "Jeanne d'Arc of the 20th century". ⏎  ⏎ However, she was overcome with anger and hatred while battling Show and Marvel and went berserk. She was the first instance of a pilot going Hyper. She cornered the Billbine with that immense power but went out of control, and self-destructed.

### dic\_pilot\_FEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b006\]
> JP (źródło tłumaczenia): 　ショウ達に続いてドレイクが招喚した地上人の一人。 ⏎ 　中国で売れない俳優をしていた過去を持つ。 ⏎ 　自信家のアレン、好戦的なジェリルに比べると落ち着いた性格ではあるが、功名心は強く、自己主張は怠らない。また、知恵が回るため、隊の参謀役を担う事もある。 ⏎ 　ミュージィの誘いを受けてゼラーナを強襲するが、自らの投げたレプラカーンのグレネードをショウのダンバインにはじき返されて爆死した。
> EN (odniesienie oficjalne, NIE polski): An out-of-work actor who was summoned from Upper Earth after Show's group. ⏎  ⏎ He has a relatively calm personality, compared to Allen's confidence and Jeril's aggressiveness. However, his desire for fame often pushes him to recklessly seek the spotlight. Thanks to his common sense and wisdom, he often finds himself acting as his squad's advisor.  ⏎  ⏎ Following Musiy's invitation, he attacks the Zelerna, only to die in an explosion when Show's Dunbine sends his own Leprechaun's grenade back at him.

### dic\_pilot\_SHOT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b008\]
> JP (źródło tłumaczenia): 　バイストン・ウェルに招喚された地上人の技師。 ⏎ 　ドレイクの下で地上人ゼット・ライトと協力して、ロボット工学とオーラ力を融合させたオーラマシンを開発する。 ⏎ 　同時にバイストン・ウェル制覇を目論むドレイクの野望に荷担する。 ⏎ 　しかし、その本心はドレイクを利用して自分が王になることを企み、地上に運ばれてからは独自に開発したオーラクルーザー・スプリガンを使い、己の思惑でドレイクとは別行動をとっていた。 ⏎ 　技術者として以上に策謀家としても有能で、ドレイクの疑いをかわしつつ計画を進めていく。
> EN (odniesienie oficjalne, NIE polski): An engineer from Upper Earth summoned to Byston Well. ⏎  ⏎ He works under Drake, along with fellow Upper Earther Zet Light, developing Aura Machines that combine robotics with Aura Power. ⏎  ⏎ He assisted Drake in his ambitions to conquer all of Byston Well. However, his true plan is to use Drake to become the ruler himself. After being brought to Upper Earth, he took his invention, the Aura Cruiser Spriggan, and took action on his own. ⏎  ⏎ He is a great tactician in addition to his talents as an engineer, furthering his own plans while avoiding Drake's suspicion.

### dic\_pilot\_SHOT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b009\]
> JP (źródło tłumaczenia): 　最終決戦の最中、腹心の部下であり恋人でもあるミュージィにドレイクを暗殺させるが失敗する。 ⏎ 　最期はショウとマーベルの攻撃によって、ミュージィと共に散る。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the middle of the final battle, his lover and trusted subordinate Musiy failed to assassinate Drake. ⏎  ⏎ In the end, he was attacked by Show and Marvel, and perished along with Musiy.

### dic\_pilot\_SION\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b00a\]
> JP (źródło tłumaczenia): 　バイストン・ウェルに住む狩人の少年。 ⏎ 　バランバランの村に立ち寄った際にラバーン・ザラマンドに捕獲され、オーラ・バトラー起動実験に使用される。そのオーラ力を認められ、バランバランの秘宝「サーバイン」を起動させるが、そこから逃走し、ラバーンの野望を阻止するために戦う事となり、「聖戦士」と呼ばれる。 ⏎ 　当初は戦いに巻き込まれた事に不満を持っていたが、レムルを守るため、また周囲の人間の影響を受け、次第に真剣になっていった。
> EN (odniesienie oficjalne, NIE polski): A young hunter who lives in Byston Well. ⏎  ⏎ While in the village of Baran-Baran, he is captured by Rabaan Zaramand to use in an experiment to activate an Aura Battler. The Treasure of Baran-Baran, the Sirbine, responds to his Aura Power and activates, but he escapes and fights to stop Rabaan's plans, earning the title of Battler. ⏎  ⏎ Initially opposed to getting caught in a fight he didn't ask for, he learns from the people he meets in his efforts to protect Remul and matures over time.

### dic\_pilot\_SION\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b00b\]
> JP (źródło tłumaczenia): 　その魂は、７００年前に聖戦士と呼ばれたショウ・ザマが転生したものである。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is actually the reincarnation of Show Zama, the Battler from 700 years ago.

### dic\_pilot\_SIRKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b00c\]
> JP (źródło tłumaczenia): 　オーラマシンによる戦いの時代から７００年後のバイストン・ウェルに住まうミ・フェラリオ。 ⏎ 　元はショウたちを地上から招喚したエ・フェラリオであったが、禁忌を破った罰としてフェラリオの長ジャコバ・アオンによってミ・フェラリオへと姿を変えられた。 ⏎ 　生まれ変わってからはチャムのような明るい性格となり、以前の落ち着いた雰囲気は消えている。 ⏎ 　シオン・ザバに生命を救われたことから、彼と行動を共にするようになる。 ⏎ 　サーバインの初戦闘時、ラバーンのズワウスを退けられたのは彼女のオーラ力が作用したことも一因である。 ⏎ 　またオーラ・バトラー戦以外でも捕らわれていたシオンやレムルを救出するなど、シオンのパートナーとして度々活躍した。
> EN (odniesienie oficjalne, NIE polski): A Mi Ferario living in Byston Well 700 years after the era of Aura Machines. ⏎  ⏎ She was the E Ferario who summoned Show and others from Upper Earth, and for breaking that taboo, she was sentenced by the Ferario leader Jacoba Aon to become a Mi Ferario instead. ⏎  ⏎ In her new life, she has a similarly sunny disposition to Chum, with none of the calmness she previously showed. ⏎ When Shion Zaba saves her life, she joins him on his journey. ⏎  ⏎ The Sirbine managed to drive back Rabaan's Zwauth in its first battle because she was providing her own Aura Power. ⏎  ⏎ She's been an incredibly helpful partner to Shion even outside of Aura Battler fights, once saving him and Remul when they were captured.

### dic\_pilot\_REMURU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b00e\]
> JP (źródło tłumaczenia): 　バランバランの秘宝「サーバイン」の在り処を知る村の姫。 ⏎ 　秘宝奪取を目論むラバーンに見初められ、村を襲撃された際に彼の城へと連れ去られるが、シオンに救出される。 ⏎ 　シオンを慕っており、よそ者である彼を偏見に囚われることなく信頼し、秘宝の下へと導いた。 ⏎ 　暴力に屈すること無く気丈に振る舞ったり、兵士から武器を奪って脱走したり、燃料庫にランプを放り込んで火事を起こしたりと芯が強く行動力のある勇敢な女性。
> EN (odniesienie oficjalne, NIE polski): A village girl who knows where Sirbine, the Treasure of Baran-Baran, is hidden. ⏎  ⏎ Rabaan kidnapped her when he attacked the village in search of the Treasure, but Shion rescued her from Rabaan's castle. ⏎  ⏎ She adores Shion and was not prejudiced against him for being an outsider. She trusted him and led him to the Treasure. ⏎  ⏎ A brave girl with nerves of steel who is unfazed even in the face of personal peril, she is fully capable of feats of daring like stealing weapons from soldiers or throwing a lamp into a fuel bunker to start a fire.

### dic\_pilot\_REMURU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b00f\]
> JP (źródło tłumaczenia): 　ラバーン達の陰謀に巻き込まれて何度も窮地に陥るが、シオンやシルキーの助けで逃げ延び、最後はシオンと結ばれる。 ⏎ 　その魂は、７００年の時を経てリムル・ルフトが転生したものである。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She has been caught up in Rabaan's nefarious plans many times, but always escapes his clutches with the help of Shion and Silky. In the end, she ties the knot with Shion. ⏎  ⏎ She is actually the reincarnation of Riml Luft who lived 700 years ago.

### dic\_pilot\_RABAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b010\]
> JP (źródło tłumaczenia): 　黒騎士を名乗る仮面の男。 ⏎ 　幼き頃、ズワウスと出逢って以来、その魅力に憑りつかれ、オーラ・バトラーの力で自らの野望を拡大させる。 ⏎ 　さらなる力としてサーバインを手に入れるためにバランバランを襲撃し、そこでシオンとレムルを捕獲した。 ⏎ 　居城の地下には、ショット・ウェポンを住まわせており、その知識を利用しようとしていた。
> EN (odniesienie oficjalne, NIE polski): A masked man who calls himself the Black Knight. ⏎  ⏎ He encountered the Zwauth at a young age and was immediately entranced, feeding his ambitions with the power of Aura Battlers. ⏎  ⏎ He attacks Baran-Baran to claim the Sirbine and its even greater power, leading to his capture of Shion and Remul. ⏎  ⏎ He allows Shot Weapon to live beneath his castle in an attempt to make use of his knowledge.

### dic\_pilot\_RABAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b011\]
> JP (źródło tłumaczenia): 　その魂は、７００年前に怨念のオーラのままに戦ったバーン・バニングスが転生したものである。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is actually the reincarnation of the grudge-filled Bern Bunnings who lived 700 years ago.

### dic\_pilot\_SHOT2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b012\]
> JP (źródło tłumaczenia): 　７００年前に地方領主ドレイク・ルフトにオーラマシンをもたらし、バイストン・ウェルを戦乱に包んだ人物。 ⏎ 　その罪により死ぬ事のない魂に縛られ、永遠の責め苦に遭っている。
> EN (odniesienie oficjalne, NIE polski): The man who placed Aura Machines into the hands of Drake Luft, lord of the land, and threw Byston Well into chaos 700 years ago. ⏎  ⏎ As punishment, his soul was bound so he could never die, doomed to lived in torturous pain forever.

### dic\_pilot\_SHOT2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fa0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fa0b013\]
> JP (źródło tłumaczenia): 　苦しみから逃れるためオーラロードを開いて地上に戻るか、そのエネルギーで自分自身を滅ぼす事を画策し、ラバーンとシオンを戦わせ、オーラ力を暴走させようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ To escape his suffering, he plotted to make Rabaan fight Shion, and cause their Aura Power to go out of control. He would then use it to open the Aura Road to return to Upper Earth, or use that energy to destroy himself.

### dic\_pilot\_DABA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b000\]
> JP (źródło tłumaczenia): 　エルガイムのヘッドライナー(パイロット)。 ⏎ 　親友のミラウー・キャオと共にポセイダル正規軍に志願すべく、惑星コアムの田舎から出てきた青年。 ⏎ 　優しげな顔立ちに似合わず頑固なところがあり、一度言い出すと聞かないタイプ。 ⏎ だが、その実直さと優しさ、強い意志は周囲の人間の信頼を集めていく。 ⏎ 　女性からも好意を集めるが、それに対して、その女性の人生を決める権利は自分にはないとして意思表示を拒むため、周囲をヤキモキさせる。 ⏎ 　１００万ギーンの手形を巡る騒動から、成り行きで反乱軍に入る事になり、父の形見のハンドメイドのＡ級ヘビーメタル・エルガイムを駆り、正規軍と戦いを繰り広げていく。
> EN (odniesienie oficjalne, NIE polski): L-Gaim's Headliner (its pilot). ⏎  ⏎ A young man from the planet Coam, Daba ventured forth from his hometown alongside his friend Mirawoo Kyao to enlist in Posaydal's regular army. ⏎  ⏎ Don't be deceived by his gentle facial features—Daba has a fiercely stubborn side to him, with a tendency to stop listening once he gets going. ⏎  ⏎ Nonetheless, his honesty, kindness, and powerful sense of determination were a magnet for trustworthy allies. ⏎  ⏎ He was also infamous as a magnet for the opposite sex, but typically refused to express his feelings in return, saying that he "had no right to determine the outcome of someone else's life"—a policy which tended to inspire jealousy. ⏎  ⏎ Daba's adventures, beginning with a simple task to deliver a 1-million-gheen credit chip, eventually led him to join the rebels. As a rebel, he fought against Posaydal's standing army in the handmade A Class Heavy Metal L-Gaim, a memento of his father.

### dic\_pilot\_DABA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b001\]
> JP (źródło tłumaczenia): 　その後、様々な経験を経て、反乱軍のリーダーとして決起する。 ⏎ 　なお、ダバ・マイロードの名は偽名であり、真の名はポセイダルによって滅ぼされた惑星ミズンのヤーマン王朝の後継者、カモン・マイロード。 ⏎ 　王家の家臣であったダバ・ハッサーに育てられ、クワサン・オリビーと兄妹同然に育てられた。婚約者であったオリビーは行方不明となっており、田舎から出たのは彼女を探すためでもあった。 ⏎ 　戦いの中、エルガイムからエルガイムＭｋ－Ⅱに乗り換え、反乱軍のリーダーとして人々を導き、真のオルドナ・ポセイダルの打倒を果たす。 ⏎ 　戦いが終わった後は新政府の要職につく事なく、精神崩壊したオリビーと共にコアムへと帰って行った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After a series of trials and tribulations, he ultimately became the leader of the rebellion.  ⏎  ⏎ In fact, the name Daba Myroad was itself a fabrication. His true identity was that of Camen Myroad, heir to the planet Mizun's Yaman Dynasty, which met its end at Posaydal's hands.  ⏎  ⏎ Raised by royal retainer Daba Hatzer, he grew up alongside Quwasan Olibee, who ultimately became his fiancée. When Olibee went missing, Daba set off from his hometown to find her.  ⏎  ⏎ Over the course of many battles, Daba upgraded the L-Gaim to the L-Gaim Mark-II, guided the populace of Pentagona World as leader of the rebellion, and ultimately brought down the true Oldna Posaydal.  ⏎  ⏎ With the war over, Daba declined a key position in the new government, opting instead to return to Coam to look after a mentally distraught Olibee.

### dic\_pilot\_LLS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b002\]
> JP (źródło tłumaczenia): 　ペンタゴナの先住民族、ミラリィ族の生き残り。 ⏎ 　見世物小屋に捕まっていたのをダバに救われて仲間になる。 ⏎ 　初めのうちは人間に対して心を閉ざし、一言も喋らないでいたが、次第に打ち解けてダバ達と心を通わせるようになった。 ⏎ 　ミラリィは平和主義であったが、人間世界に感化されてきているようで、本来は優しく温和であるが、勢いで他人を蹴っ飛ばしてから蹴った自分に驚くような一面もあった。 ⏎ 　料理と裁縫が得意で、自分の服は自分で仕立てるため多くの衣装を持っている。パジャマ姿や黒装束を披露した事もある。 ⏎ 　小さな身体と飛行能力を活かしての偵察や潜入、ヘビーメタルのコックピットに同乗してのサポートなど、ダバ達と共に戦った。
> EN (odniesienie oficjalne, NIE polski): A survivor of the Mirali, one of Pentagona's indigenous peoples.  ⏎  ⏎ After Daba rescued her from a circus, Lilis joins his crew. Though unwilling to open up to humans, she grew more comfortable around them in time, eventually forming an emotional bond with Daba and the others.  ⏎  ⏎ The Mirali were pacifists at heart, but the human world seemed to rub off on Lilis, who often found herself shocked at her willingness to see foes driven before the team.  ⏎  ⏎ A skilled cook and seamstress, Lilis had an extensive wardrobe of her own creation, and sometimes appeared in pajamas or a black sneaking suit.  ⏎  ⏎ Her Lilliputian size and ability to fly made her indispensable for recon and infiltration assignments, and she always tagged along with Daba in the cockpit of his Heavy Metal.

### dic\_pilot\_LLS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b003\]
> JP (źródło tłumaczenia): 　キャオと共に鉱山惑星パラータ・スターに乗り込み、同胞の魂と共に原子炉アルファ・ハートの爆発を食い止めた事もあった。 ⏎ 　戦いが終わった後はキャオと共に生き残りのミラリィを探す旅に出る事を決めた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Alpha Heart—Palata Star's nuclear reactor—was on the verge of meltdown, she was able to stop it with help from the spirits of her comrades.  ⏎  ⏎ After the war, she sets off with Kyao on a journey to find other Mirali survivors.

### dic\_pilot\_AMU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b004\]
> JP (źródło tłumaczenia): 　ダバと行動を共にする少女。 ⏎ 　芝居小屋で役者をやっていたが、ミヤマ・リーリンに素質を買われて盗賊の仲間に入った事でダバに出会い、一方的に惚れ込んで強引に同行するようになる。 ⏎ 　ダバに対しては一途な恋する乙女だが、ダバ以外にはあからさまに態度が変わり、素の勝ち気で調子のいい所が前面に出る。 ⏎ 　同じくダバに惹かれて軍を抜けたレッシィとは、恋のライバルとして激しい争奪戦を繰り広げていた。
> EN (odniesienie oficjalne, NIE polski): A girl travelling with Daba, Amm was a playhouse actress hired by bandit leader Miyama Lilen. After falling head-over-heels in love with Daba, however, she decided to tag along at the team's behest.  ⏎  ⏎ Around Daba, she was a girl in the throes of love most profound. Around everyone else, her feisty, competitive side roared to the forefront.  ⏎  ⏎ She viewed Leccee, who left Posaydal's army to travel with Daba, as a rival in love—a rivalry that sometimes erupts into all-out war.

### dic\_pilot\_AMU\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b005\]
> JP (źródło tłumaczenia): 　ダバの役に立とうとして奮闘し、ヘビーメタルも操縦するようになる。ダバがエルガイムＭｋ－Ⅱに乗り換えた後はエルガイムに乗った。 ⏎ 　戦いが終わった後は、オリビーと共にコアムに帰るダバを涙を流しながら見送った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She learned to pilot Heavy Metals in order to help Daba, and ends up piloting the L-Gaim after Daba upgraded to the Mark-II.  ⏎  ⏎ After the war, she saw Daba off with tears in her eyes as he returned to Coam with Olibee.

### dic\_pilot\_RESSY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b006\]
> JP (źródło tłumaczenia): 　ダバの仲間の一人。 ⏎ 　元ポセイダル正規軍１３人衆であったが、軍を離反して、ダバの人柄に惹かれ協力するようになった。 ⏎ 　情報戦略面の知識が豊富なだけでなく、戦士としても高い能力を持つ。 ⏎ 　気が強く意地っ張りであり、ダバを巡ってアムと壮絶な争奪戦を繰り広げる。
> EN (odniesienie oficjalne, NIE polski): One of Daba's allies.  ⏎  ⏎ A former member of Posaydal's Extra Thirteen, she was inspired to defect from the army by Daba's sense of character.  ⏎  ⏎ An accomplished fighter with extensive knowledge of tactical warfare, Leccee wages countless high-stakes, do-or-die battles with Amm...over Daba's affections.

### dic\_pilot\_RESSY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b007\]
> JP (źródło tłumaczenia): 　当初はアムと同じ土俵で争っていた彼女だったが、ダバの役に立つために同じ場所で戦う以外の方法を選択し、自らダバから離れていった。 ⏎ 　その後、戦艦ホエールの戦闘司令官として再登場した際には、コスチュームも一新し、言動も大人のものになっていた。 ⏎ 　スヴェートでの最終決戦ではミアン・クゥ・ハウ・アッシャーをラキシスの心臓へと送り届け、バイオリレーション・システムを停止させた。 ⏎ 　戦いが終わった後は、オリビーと共にコアムに帰るダバを涙を流しながら見送った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Eventually, she recognized that simply fighting alongside Daba and the others might not be the best way to assist his efforts, and chose to leave him of her own volition.  ⏎  ⏎ She reappeared later as combat commander of the warship Whele, with a new outfit and a more mature personality to match.  ⏎  ⏎ During the final battle at Sveet, she helped Mian Qu Haw Asher reach Lachesis's Heart to shut down the Biorelation System.  ⏎  ⏎ After the war, she saw off Daba with tears in her eyes as he returned to Coam with Olibee.

### dic\_pilot\_RESSY2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b008\]
> JP (źródło tłumaczenia): 　ダバの仲間の一人。 ⏎ 　元ポセイダル正規軍１３人衆であったが、軍を離反して、ダバの人柄に惹かれ協力するようになった。 ⏎ 　情報戦略面の知識が豊富なだけでなく、戦士としても高い能力を持つ。 ⏎ 　気が強く意地っ張りであり、ダバを巡ってアムと壮絶な争奪戦を繰り広げる。 ⏎ 　当初はアムと同じ土俵で争っていた彼女だったが、ダバの役に立つために同じ場所で戦う以外の方法を選択し、自らダバから離れていった。 ⏎ 　その後、戦艦ホエールの戦闘司令官として再登場した際には、コスチュームも一新し、言動も大人のものになっていた。
> EN (odniesienie oficjalne, NIE polski): One of Daba's allies.  ⏎  ⏎ A former member of Posaydal's Extra Thirteen, she was inspired to defect from the army by Daba's sense of character.  ⏎  ⏎ An accomplished fighter with extensive knowledge of tactical warfare, Leccee wages countless high-stakes, do-or-die battles with Amm...over Daba's affections.  ⏎  ⏎ Eventually, she recognized that simply fighting alongside Daba and the others might not be the best way to assist his efforts, and chose to leave him of her own volition.  ⏎  ⏎ She reappeared later as combat commander of the warship Whele, with a new outfit and more mature personality to match.

### dic\_pilot\_RESSY2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b009\]
> JP (źródło tłumaczenia): 　スヴェートでの最終決戦ではミアン・クゥ・ハウ・アッシャーをラキシスの心臓へと送り届け、バイオリレーション・システムを停止させた。 ⏎ 　戦いが終わった後は、オリビーと共にコアムに帰るダバを涙を流しながら見送った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the final battle at Sveet, she helped Mian Qu Haw Asher reach Lachesis's Heart to shut down the Biorelation System.  ⏎  ⏎ After the war, she saw off Daba with tears in her eyes as he returned to Coam with Olibee.

### dic\_pilot\_KYAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b00a\]
> JP (źródło tłumaczenia): 　ダバとは同郷の親友。 ⏎ 　一緒に正規軍に志願しようとコアムの田舎から出てきたが、ダバが反乱軍に入ったため、いやいやながら正規軍入りを諦めた。 ⏎ 　お調子者でおっちょこちょいのお人好しだが、美女とお金に弱く、短気なのが欠点。 ⏎ また、大食漢で怪力の持ち主でもある。 ⏎ 　超一流のメカニックとしてだけでなく、ヘビーメタルの操縦もこなし、ダバを様々な局面でサポートして戦い続けた。
> EN (odniesienie oficjalne, NIE polski): Daba's old friend from his hometown on Coam.  ⏎  ⏎ Though he originally set off with Daba to enlist in the army, he reluctantly abandons the idea when Daba joins the rebellion.  ⏎  ⏎ A good-natured goofball at heart, his weaknesses were beautiful women, money, and his short temper. One might not have imagined it at first glance, but he also possessed astonishing physical prowess and a tremendous appetite.  ⏎  ⏎ In addition to his incredible skills as a mechanic, Kyao could also pilot Heavy Metals, providing indispensable support to Daba during his journey.

### dic\_pilot\_KYAO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:8fe0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:8fe0b00b\]
> JP (źródło tłumaczenia): 　戦いの中、ポセイダル軍の新型であるアモンデュールを一目でヤーマン系のヘビーメタルと見抜き、エルガイムＭｋ－Ⅱに改造した。 ⏎ 　戦いが終わった後はリリスと共にミラリィの生き残りを探す旅に出る事を決めるが、本人はあまり乗り気でないようであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Posaydal deploys the Amoun Düül, a new Heavy Metal, Kyao immediately recognized it as a Camen-based design, and remodels it into the L-Gaim Mark-II.  ⏎  ⏎ After the war, he set off on a journey with Lilis to find survivors of the Mirali...even if his heart didn't quite seem to be in it.

### dic\_pilot\_GABLY\_\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b000\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍の一員。 ⏎ 　惑星コアムの田舎の貧しい豪族出身で、村の期待を背負って中古のアローンで正規軍に志願したが、その道中で食事を盗み食いした事が縁となり、ダバのライバルとなる。 ⏎ 　強い上昇志向と高い自尊心を持ち、クールに振る舞おうとしながらも感情的であり、加えて感極まりやすく子供じみたところまであり、さらに惚れっぽく、どこか憎めない人物。 ⏎ 　ヘッドライナーとしての腕は確かで、いくつかの部隊を転々とした後、作戦参謀の地位につき、Ａ級ヘビーメタルを任される。 ⏎ 　彼の故郷ではミラリィ族は悪魔の使いと考えられており、リリスを毛嫌いする。
> EN (odniesienie oficjalne, NIE polski): A soldier in Posaydal's regular forces.  ⏎  ⏎ Hailing from one of the less-successful aristocratic families in Coam's countryside, Gablae set off with a used Allone to enlist in the army, the village's hopes riding on his shoulders. When he stole Daba's lunch along the way, an eternal rivalry was born.  ⏎  ⏎ Incredibly self-confident, Gablae was always looking to improve his station in life, but his attempts to look cool frequently backfired. He was easy to impress, had a childish side to him, and fell in love at the drop of a hat...but for all his character flaws, it was and is nearly impossible to hate the gormless goober.  ⏎  ⏎ A skilled Headliner, he ended up in a key position after a series of transfers, and was ultimately entrusted with an A Class Heavy Metal.  ⏎  ⏎ His hometown believed the Mirali to be demonic familiars, leaving him with a deep-seated prejudice against Lilis.

### dic\_pilot\_GABLY\_\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b001\]
> JP (źródło tłumaczenia): 　紆余曲折を経て、クワサン・オリビーに想いを寄せ、彼女を救うためにダバと共闘する事となり、真のポセイダルやギワザの打倒に貢献する。 ⏎ 　戦いが終わった後は精神が崩壊したオリビーをダバに託し、コアムに帰る彼等を見送った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After many ups and downs, he ended up falling in love with Quwasan Olibee, joining forces with Daba to save her. In the end, he proved indispensable in the battle to defeat Giwaza and the true Posaydal.  ⏎  ⏎ Following the war, he entrusted a mentally shattered Olibee to Daba, and saw them off as they returned to Coam.

### dic\_pilot\_HASYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b002\]
> JP (źródło tłumaczenia): 　ギャブレーの部下。 ⏎ 　元はアムが所属していた盗賊団の副頭領であったが、成り上がろうとして頭である ⏎ リーリンを暗殺したのがばれて、盗賊団から逃げ出す。 ⏎ 　その後、反乱軍に参加したアムに取り入って一時期はダバ達の仲間になるが、賞金欲しさに裏切って、最終的にはギャブレーの下についた。 ⏎ 　小心者の小悪党で調子に乗りやすいタイプ。
> EN (odniesienie oficjalne, NIE polski): Gablae's subordinate. ⏎  ⏎ Hatchia was originally second-in-command of the bandit gang Amm hails from but was forced to flee after a botched assassination attempt against Lilen, the bandit leader. ⏎  ⏎ After seeing Amm join the rebellion, he fought alongside Daba for a time, but ultimately betrayed the team for money and ended up working for Gablae. ⏎  ⏎ As one might surmise, he was a petulant little goon who let everything go to his head.

### dic\_pilot\_HASYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b003\]
> JP (źródło tłumaczenia): 　最後まで生き残り、戦いが終わった後はギャブレーらと共にダバ達を見送った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After (somehow) managing to survive the war, he saw off Daba and the others alongside Gablae.

### dic\_pilot\_OLBY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b004\]
> JP (źródło tłumaczenia): 　ポセイダル軍の一員であり、ヤーマン族残党狩り専門の囮部隊隊長。 ⏎ 　後に近衛師団長に就任する。 ⏎ 　本来の姿はダバの義理の妹にして、婚約者だった少女が、ポセイダルによってコントローラーハーケンを打ち込まれ、精神制御されている。同時にポセイダルのセンサーとしての役割を持ち、情報収集をするだけでなく、時には代弁者としても機能する。 ⏎ 　ダバと過ごした当時の記憶は封じ込まれているが、彼との接触によって、封印の一部にほころびが生じ、それに苦しむ。 ⏎ 　戦場ではカルバリー・テンプル（通称ヘルミーネ）を駆る。
> EN (odniesienie oficjalne, NIE polski): Captain of Posaydal's decoy squadron, which was tasked with eradicating remnants of the Yaman clan, and later assigned as commander of the Imperial Guard.  ⏎  ⏎ She grew up as Daba's adopted sister, and was engaged to marry him, when Posaydal took over her mind with a Controller Harken. Entrusted with serving as Posaydal's sensor, Olibee also helps with information collection, and at times acts as Posaydal's proxy.  ⏎  ⏎ Though her memories of Daba have been sealed away, encountering him sometimes caused fragments to surge painfully back to life.  ⏎  ⏎ In combat, she headlines a Calvary Temple known as Hellmeene.

### dic\_pilot\_OLBY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b005\]
> JP (źródło tłumaczenia): 　その精神は徐々に不安定になっていき、真のポセイダルが討たれた後は崩壊してしまう。 ⏎ 　全てが終わった後は、兄ダバと共にコアムへと帰って行った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Her mind gradually grew more unstable over time, before shattering completely following the true Posaydal's defeat.  ⏎  ⏎ After the war, she returned to Coam with Daba.

### dic\_pilot\_NEY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b006\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍１３人衆の一人。 ⏎ 　Ａ級ヘビーメタル・オージェを駆る優秀な戦士であり、何度もダバを苦しめた。 ⏎ 　長身の美女であり、化粧をしない自分を恥じる等、常に女性らしさを忘れない。 ⏎ 　ギワザの愛人でもあり、１３人衆の中でも高い地位にいる。 ⏎ 　最初はギャブレーに目をかけていたが、ギャブレーが勝手な行動を取り始めてからは厳しい態度を取るようになった。
> EN (odniesienie oficjalne, NIE polski): A member of the Extra Thirteen in Posaydal's forces.  ⏎  ⏎ A distinguished soldier, Nei piloted the A Class Heavy Metal Auge, which she used to make Daba's life miserable on more than one occasion.  ⏎  ⏎ Tall and beautiful, she refused to abandon her feminine side, and wouldn't be caught dead without makeup.  ⏎  ⏎ She held considerable status within the Extra Thirteen, and was Giwaza's lover.  ⏎  ⏎ Though initially kind to Gablae, his capricious behavior required her to take a stricter approach.

### dic\_pilot\_NEY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b007\]
> JP (źródło tłumaczenia): 　愛するギワザのために戦った彼女であったが、最後はギワザにスパイ容疑をかけられてしまう。その仕打ちに怒りを覚え、ギワザの右腕を切り落として一矢を報いるが、直後にギワザに撃たれて生命を落とした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She fought in the name of her beloved Giwaza, but her efforts were for naught. When Giwaza punished her under suspicions of espionage, Nei flew into a rage and cut off Giwaza's right arm, but he shot her soon after, ending her life.

### dic\_pilot\_GWAZA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b008\]
> JP (źródło tłumaczenia): 　ポセイダル軍コアム師団情報局長。 ⏎ 　エリート集団である１３人衆を統率し、反ポセイダル勢力の摘発と処刑を主な任務としている。 ⏎ 　優秀な人物であるのは事実だが、狡猾かつ尊大であり、己の能力を過信している。一方、自己の利益のためには他人に対して徹底的に非情になれる一面を持つ。
> EN (odniesienie oficjalne, NIE polski): Intelligence director for Coam in the Posaydal Forces. ⏎  ⏎ Giwaza was in charge of the elite Extra Thirteen, with his primary duties being identifying and executing anti-Posaydal elements. ⏎  ⏎ An exceptional soldier with cunning, arrogance, and self-confidence in excess, Giwaza had no qualms about abusing others to advance his own goals.

### dic\_pilot\_GWAZA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b009\]
> JP (źródło tłumaczenia): 　ポセイダルに忠誠を誓っていたが、自らの処遇に対する不満や軍の腐敗をある程度黙認するポセイダルに疑念を抱き、謀反の計画を立てる。 ⏎ 　その野望実現のため、愛人であるネイですら裏切りの可能性ありとして処刑した。 ⏎ 　自分こそがペンタゴナの王となるに相応しいと思っていだが、世界を支えられる器ではなく、その野望は潰える。 ⏎ 　完全に勝機を失ったにも関わらず、戦力さえ整えれば巻き返しは可能だと、旗艦の乗員を見捨てて一人シャトルで脱出したが、エルガイムのバスターランチャーの直撃を受けて死亡した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Despite swearing an oath of fealty to Posaydal, he grew dissatisfied with his own treatment and suspicious of Posaydal's tacit acceptance of military corruption.  ⏎  ⏎ As he began to plot a rebellion, he went so far as to execute his lover, Nei, on mere suspicion of betrayal. ⏎  ⏎ Believing himself to be worthy of ruling Pentagona as its next king, his strength of character proved unsuited to the job. Whatever grand ambitions he harbored ended up scattered to the winds. ⏎  ⏎ His hopes of victory dashed, he abandoned his flagship in an escape shuttle, believing that he simply needed to regroup and try again...until a direct hit from L-Gaim's Buster Launcher vaporized him completely.

### dic\_pilot\_MACTMN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00a\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍１３人衆の一人。 ⏎ 　独特の髪型と衣装、さらには化粧により異様な風体を持つ。 ⏎ 　普段は落ち着いた人物に見えるが、興奮してくると言動がエキセントリックになっていき、不安定な情緒となる。 ⏎ 　搭乗ヘビーメタルは自らカスタムしたアトールⅤ（ファイブ）。
> EN (odniesienie oficjalne, NIE polski): A member of the Extra Thirteen in Posaydal's regular forces.  ⏎  ⏎ McTomin's hairstyle, manner of dress, and manner of makeup use gave him a peculiar air, even among the Extra Thirteen.  ⏎  ⏎ Normally calm and composed, he grew increasingly erratic whenever excited.  ⏎  ⏎ He piloted a personally-customized A-Taul V (Five).

### dic\_pilot\_MACTMN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00b\]
> JP (źródło tłumaczenia): 　ポセイダルに反旗を翻したギワザにつき、その命によりダバを狙い続ける。 ⏎ 　最後はエルガイムＭｋ－Ⅱのバスターランチャーで撃墜された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Aligning himself with Giwaza during his rebellion against Posaydal, McTomin used the opportunity to hound Daba.  ⏎  ⏎ In the end, he was shot down by a Buster Launcher shot from the L-Gaim Mark-II.

### dic\_pilot\_LLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00c\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍１３人衆の一人。 ⏎ 　気分屋かつ冷酷非情であり、過去の経験から男嫌いであると同時に男に尽くす女を憎悪している。 ⏎ 　搭乗ヘビーメタルはグルーンを愛用している。
> EN (odniesienie oficjalne, NIE polski): A member of the Extra Thirteen in Posaydal's regular forces.  ⏎  ⏎ Ruthless and prone to tempestuous mood swings, negative experiences left her with a hatred of men and a deep-seated loathing for any woman who seeks to please them.  ⏎  ⏎ She was fond of her Heavy Metal, the G.Roon.

### dic\_pilot\_LLY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00d\]
> JP (źródło tłumaczenia): 　ポセイダルに反旗を翻したギワザについたが、ギワザへの忠誠心は薄かった。 ⏎ 　人質にしたアムをいたぶった事により、両者の間には因縁が生まれ、最後はアムのエルガイムに撃墜された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Despite allying herself with Giwaza during his rebellion, her loyalty was decidedly less than ironclad. ⏎  ⏎ After taking Amm hostage, a small rivalry formed between the two. Fittingly, it was Amm who defeated Lili with the L-Gaim.

### dic\_pilot\_BURNG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00e\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍１３人衆の一人。 ⏎ 　冷静沈着な自信家。
> EN (odniesienie oficjalne, NIE polski): A cool, calm, and confident member of the Extra Thirteen.

### dic\_pilot\_BURNG\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b00f\]
> JP (źródło tłumaczenia): 　ポセイダルに反旗を翻したギワザについた。 ⏎ 　アシュラ・テンプルに搭乗し、ギワザを討とうとするダバを追い詰めたが、救援に現れたキャオとダバの連係の前に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He allied himself with Giwaza during his rebellion, and piloted an Ashura Temple.  ⏎  ⏎ Despite cornering Daba during his fight against Giwaza, he proved no match for some unexpected teamwork from Kyao.

### dic\_pilot\_ANTON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9020b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b010\]
> JP (źródło tłumaczenia): 　１３人衆の予備将校。 ⏎ 　ネイ・モー・ハンの部下であり、彼女が出撃する際は相棒のヘッケラーと共に左右を固める。 ⏎ 　血の気の多いヘッケラーと異なり、冷静なタイプ。
> EN (odniesienie oficjalne, NIE polski): A reserve officer in the Extra Thirteen.  ⏎  ⏎ As Nei Moh Han's subordinate, he provided her with steadfast support alongside his partner, Hekeler.  ⏎  ⏎ In contrast to his fiery partner, Antoon was cool and collected.

### dic\_pilot\_ANTON\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9020b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9020b011\]
> JP (źródło tłumaczenia): 　後にネイが前線を離れた後はギワザの副官となり、最後まで彼に従った。 ⏎ 　顔の模様は刺青だと思われていたが、最後の戦いの後、シールだった事が明らかになった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After Nei stopped serving on the front lines, he became Giwaza's adjutant, serving him until the bitter end.  ⏎  ⏎ His facial markings appeared to be tattoos, but they were revealed to be stickers in the aftermath of the final battle.

### dic\_pilot\_HECRR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b000\]
> JP (źródło tłumaczenia): 　１３人衆の予備将校の片目の男。 ⏎ 　ネイ・モー・ハンの部下であり、彼女が出撃する際は相棒のアントンと共に左右を固める。 ⏎ 　冷静なアントンと異なり、血の気が多いが、武人らしい実直さを持つ。
> EN (odniesienie oficjalne, NIE polski): A reserve officer in the Extra Thirteen. Has an eyepatch.  ⏎  ⏎ As Nei Moh Han's subordinate, he provided her with steadfast support alongside his partner, Antoon.  ⏎  ⏎ In contrast to the coolheaded Antoon, Hekeler had a fiery personality and a warrior's sense of honor.

### dic\_pilot\_HECRR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b001\]
> JP (źródło tłumaczenia): 　ポセイダルに反旗を翻したギワザにつき、バッシュでスヴェート侵攻の先鋒を務めるが、ハンス・アラハートの駆るカルバリー・テンプルに敗れ、戦闘不能となる。 ⏎ 　最後はエルガイムＭｋ－Ⅱからマフ・マクトミンをかばい、戦死する。 ⏎ 　その死の間際には、相棒であるアントンの名を呼んだ。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Allying himself with Giwaza during his rebellion, Hekeler led the charge against Sveet in his Bat-Shu, only to be struck down by Hanz Alahalt's Calvary Temple.  ⏎  ⏎ In the end, he died protecting MF McTomin from the L-Gaim Mark-II, uttering the name of his partner, Antoon, as he departed this mortal coil.

### dic\_pilot\_RYOKLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b002\]
> JP (źródło tłumaczenia): 　クワサン・オリビーの護衛兼お目付け役。 ⏎ 　オリビーと同じくコントローラーハーケンによって精神制御をされている。 ⏎ 　元は１３人衆で、生身においても高い戦闘力を持つ。 ⏎ 　オリビー本人に忠誠を誓っているわけではなく、任務の遂行を第一とする。
> EN (odniesienie oficjalne, NIE polski): Quwasan Olibee's bodyguard and inspector.  ⏎  ⏎ Like Olibee, a Controller Harken regulates his mind.  ⏎  ⏎ As a former member of the Extra Thirteen, he's a formidable fighter, even when unarmed.  ⏎  ⏎ He had no particular loyalty to Olibee, and valued the execution of his mission above all else.

### dic\_pilot\_RYOKLY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b003\]
> JP (źródło tłumaczenia): 　オリビーが近衛師団長に就任した後は、その副官となった。 ⏎ 　ポセイダルに反旗を翻したギワザ陣営や反乱軍に対し、黒いカルバリー・テンプルを駆って迎撃した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After Olibee is made the head of the Imperial Guard, he became her adjutant. When Giwaza rebelled against Posaydal, he piloted a black Calvary Temple against his forces.

### dic\_pilot\_HANS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b004\]
> JP (źródło tłumaczenia): 　ポセイダル正規軍１３人衆の一人。 ⏎ 　スヴェートの防衛を担当する。
> EN (odniesienie oficjalne, NIE polski): A member of Posaydal's Extra Thirteen.  ⏎  ⏎ Handles defensive operations at Sveet.

### dic\_pilot\_HANS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b005\]
> JP (źródło tłumaczenia): 　反旗を翻したギワザにはつかず、最後までポセイダル側で戦った。 ⏎ 　黒のカルバリー・テンプルに搭乗し、ギワザ側のヘッケラーの駆るバッシュを戦闘不能に追い込んだ。 ⏎ 　最後は、スヴェートの最深部で同じくポセイダル側についた１３人衆のマーハル・セヌーマと共にバイオリレーションの影響で死亡した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After Giwaza rebelled against Posaydal, he remained loyal to Posaydal, piloting a black Calvary Temple to render Hekeler's Bat-Shu inoperable.  ⏎  ⏎ Ultimately, he perished alongside fellow Extra Thirteen member Marhal Senuma in the heart of Sveet, a victim of the Biorelation System's deleterious effects.

### dic\_pilot\_AMNDR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b006\]
> JP (źródło tłumaczenia): 　ペンタゴナ・ワールド最大の財閥の創始者。 ⏎ 　ポセイダル正規軍に対してもかなりの発言力を持ち、その中核に入り込んでいる。 ⏎ 　ダバやギャブレーとは１００万ギーンの手形を巡って知り合い、ギャブレーに正規軍への紹介状を書いた。 ⏎ 　自身の所持するアマン商会を通じて正規軍と反乱軍の双方に武器を供給する死の商人で、各地に私設の軍隊を持っている。 ⏎ 　その行動原理は、基本的には商人としての立場に立脚しているが、自分の興味や関心を優先するかのような時もある。
> EN (odniesienie oficjalne, NIE polski): As founder of the largest conglomerate in Pentagona World, Amandra also had considerable sway with Posaydal's forces, and very nearly served as its core.  ⏎  ⏎ He learned of Daba and Gablae through the 1-million gheen credit chip, and wrote Gablae's letter of introduction to the regular forces.  ⏎  ⏎ A merchant of death, he supplied weapons to the regular forces and rebels alike through his company, the Amandra Concern, in addition to controlling private militaries across Pentagona World.  ⏎  ⏎ He seemed motivated primarily by business interests, but occasionally appeared to act according to his own sense of curiosity.

### dic\_pilot\_AMNDR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b007\]
> JP (źródło tłumaczenia): 　アマンダラ・カマンダラの名と立場は偽りのものであり、その正体はペンタゴナ・ワールドの統治者である真のオルドナ・ポセイダルであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ The name Amandra Kamandra is fake. In reality, he is the true Oldna Posaydal, ruler of Pentagona World.

### dic\_pilot\_POSEIDL\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b008\]
> JP (źródło tłumaczenia): 　アマンダラ・カマンダラの正体であり、ペンタゴナ・ワールドの真の支配者。 ⏎ 　自身の開発したバイオリレーション・システムによって、若さを保っている。 ⏎ 　かつて自分に想いを寄せていたミアンとフラットを道具として扱い、さらにバランスを取るためと称して正規軍と反乱軍を戦わせ、自らは影の支配者として世界をコントロールしていた。 ⏎ 　しかし、ダバ率いる反乱軍の想定以上の力とミアン、フラット両名の決別により、自らが表舞台に立つ事となる。
> EN (odniesienie oficjalne, NIE polski): Amandra Kamandra's true identity, and the actual ruler of Pentagona World.  ⏎  ⏎ He maintained his youth via the Biorelation System, which he developed himself.  ⏎  ⏎ Controlling the world from the shadows, he used former lovers Mian and Flat to exert factual control over Pentagona and do his bidding, and had "Posaydal's" army and the rebels fight each other in the name of maintaining balance.  ⏎  ⏎ When the Daba-led rebel forces exceeded his expectations, and Mian and Flat said their goodbyes to him, he was forced to reveal himself at last.

### dic\_pilot\_POSEIDL\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b009\]
> JP (źródło tłumaczenia): 　最終決戦ではオージに搭乗してダバのエルガイムＭｋ－Ⅱを圧倒したが、ミアンがバイオリレーション・システムを停止させた事で急激に老化して、敗北した。 ⏎ 　なお、その戦いの中で肉親がヤーマン族にむごい殺され方をしたと語り、その復讐のためにヤーマンの血統を根絶やしにしようとしていた事が明らかになった。
> EN (odniesienie oficjalne, NIE polski): In the final battle, he overwhelmed Daba's L-Gaim Mark-II with his original Auge, but Mian disabled the Biorelation System, causing him to perish after aging decades in an instant.  ⏎  ⏎ Prior to this, he revealed that his parents suffered grisly deaths at the hands of the Yaman—his quest to exterminate the Yaman bloodline born out of revenge for this original sin.

### dic\_pilot\_POSEIDL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00a\]
> JP (źródło tłumaczenia): 　ペンタゴナ・ワールドの統治者。 ⏎ 　６８歳の男性と言われているが、若さと妖艶な美貌を持つ謎多き存在。 ⏎ 　人前に姿を現す時はホログラムを多用し、自らを神の子と称するなど、過剰なまでに神秘性を演出して見せる。
> EN (odniesienie oficjalne, NIE polski): Ruler of Pentagona World.  ⏎  ⏎ Said to be a 68-year-old man, Posaydal's youthful appearance and bewitching beauty concealed many mysteries.  ⏎  ⏎ Posaydal referred to themselves as a child of God, and used holograms to appear before others with a sense of mystique bordering on the excessive.

### dic\_pilot\_POSEIDL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00b\]
> JP (źródło tłumaczenia): 　その正体は、真のポセイダルの同志であり恋人でもあった女性、ミアン・クゥ・ハウ・アッシャーであり、バイオリレーション・システムによって若さを保っていた。 ⏎ 　真のポセイダル（アマンダラ・カマンダラ）の操り人形であったが、徐々に自分の存在する意味と変わっていった恋人に疑問を持ち、最終的にはアマンダラと決別しようとする。 ⏎ 　アマンダラが正体を現し、ダバと戦っている最中、レッシィと共にスヴェートの最深部にあるラキシスの心臓でバイオリレーション・システムを停止させ、消滅するかのように落命した。 ⏎ 　それによってアマンダラも一気に老化し、敗北に至った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In reality, Posaydal's true identity was that of Mian Qu Haw Asher, the former lover of the actual Oldna Posaydal (Amandra Kamandra).  ⏎  ⏎ With her youth preserved by the Biorelation System, Mian acted as Amandra's public-facing puppet. Over time, however, Mian began to question her sense of purpose and ultimately chose to part ways with Amandra.  ⏎  ⏎ After Amandra reveals his true identity and begins fighting against Daba, Mian leads Leccee to Lachesis's Heart deep within Sveet's core. There, she disables the Biorelation System and breathes her last.  ⏎  ⏎ Without the Biorelation System's effects, Amandra ages decades in an instant and dies.

### dic\_pilot\_FRAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00c\]
> JP (źródło tłumaczenia): 　ポセイダルから治外法権を与えられた人工天体サート・スターの女主人。 ⏎ 　長きに渡り、女性だけが住むこの星を統治しているが、見た目からは年齢を感じさせない。 ⏎ 　治外法権によって正規軍も無断で立ち入れないのをいい事に気まぐれにダバ達に支援の手を差し伸べる。
> EN (odniesienie oficjalne, NIE polski): Keeper of Theart Star, an artificial satellite that Posaydal has granted extraterritoriality.  ⏎  ⏎ Though she ruled this all-female paradise for many years, her external appearance remained youthful and un-aging.  ⏎  ⏎ Theart Star's extraterritoriality prevented Posaydal's forces from interfering with its operations, allowing her to support Daba's crew whenever the mood struck her.

### dic\_pilot\_FRAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00d\]
> JP (źródło tłumaczenia): 　その正体は、かつてミアン・クゥ・ハウ・アッシャーと共に真のポセイダルのために戦った女性であり、その時の功績により特権を与えられている。 ⏎ 　しかし、女性を道具として扱う真のポセイダルを見限って離反し、彼を問い詰めるが、その最中に爆発に巻き込まれて生命を落とした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Her true identity was that of a warrior who once fought alongside Mian Qu Haw Asher for the sake of the true Posaydal, with her favorable treatment a reward for her efforts at the time.  ⏎  ⏎ Seeing the way the true Posaydal treated women as his playthings prompted a change of heart, however. She tracked him down and confronted him, but Flat was killed in an explosion as a result.

### dic\_pilot\_KOUZIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9060b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00e\]
> JP (źródło tłumaczenia): 　マジンカイザーの操縦者。 ⏎ 　マジンカイザーの開発者である祖父・兜十蔵博士から機体を託された。 ⏎ 　正義感の強い熱血漢で、仲間想いな性格。 ⏎ 　当初はその強大な力を秘めるマジンカイザーを制御する事が出来なかったが、数々の苦難を乗り越える中で真の操縦者となった。 ⏎ 　休養のためにパリを訪れていたが、戦闘獣軍団の侵略を食い止めるため、ローリィ姉妹やもりもり博士といった仲間を失いながらも光子力研究所へと向かう。
> EN (odniesienie oficjalne, NIE polski): The pilot of Mazinkaiser. ⏎  ⏎ He was entrusted with Mazinkaiser by its original creator, Dr. Juzo Kabuto, his grandfather. ⏎  ⏎ He is a hot-blooded young man with a strong sense of justice and comradeship. ⏎  ⏎ Initially, he was unable to control the powerful Mazinkaiser, but after overcoming many hardships, he was able to master it. ⏎  ⏎ The Mycenae Empire launches its invasion while he is on a trip to Paris. He makes his way to the Photon Power Laboratory in Japan to stop the Battle Beast Army, losing many of his friends, such as Dr. Morimori and the twin sisters, Loru and Lori.

### dic\_pilot\_KOUZIK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9060b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9060b00f\]
> JP (źródło tłumaczenia): 　宇宙にいる弓教授達から送り届けられたマジンカイザーに乗り、その驚異的な力で次々と戦闘獣軍団を倒していく。その末に暗黒大将軍との一騎討ちを制し、世界の未来を救った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After boarding Mazinkaiser, which was sent into space by Professor Yumi, he quickly dispatches the Battle Beast army. He then faces the Great General of Darkness himself in a fierce duel, defeating him and securing a future for humanity.

### dic\_pilot\_TETUYAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b000\]
> JP (źródło tłumaczenia): 　グレートマジンガーの操縦者。 ⏎ 　厳しい戦闘訓練を乗り越えて操縦者となった経緯から「戦闘のプロフェッショナル」と称される。 ⏎ 　甲児にとっては兄貴分であり、言動は厳しいものだが、その底には仲間を想う気持ちがある。 ⏎ 　アメリカのニューヨークに現れた戦闘獣と激戦を繰り広げた。
> EN (odniesienie oficjalne, NIE polski): The pilot of Great Mazinger. ⏎  ⏎ A decided combat professional, he overcame a rigorous training regiment to become a pilot. ⏎  ⏎ He acts as an older brother to Koji Kabuto. Although his words and actions are often harsh, he holds his comrades in high esteem. ⏎  ⏎ During the Mycenae Empire's invasion of Earth, he heroically stands his ground against the Battle Beasts in New York.

### dic\_pilot\_TETUYAK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b001\]
> JP (źródło tłumaczenia): 　七大将軍である魔魚将軍アンゴラスと大昆虫将軍スカラベスを相手に勝利し、街を守る事に成功するも、グレートマジンガーの半壊によって身動きが取れなくなった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is able to defend the city from Aquatic General Angoras and Insect General Scarabeth. However, Great Mazinger is partially destroyed in the attempt and incapacitated.

### dic\_pilot\_SAYAKAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b002\]
> JP (źródło tłumaczenia): 　光子力研究所の所長・弓教授の娘。 ⏎ 　明るく活発な性格で、甲児に想いを寄せている。 ⏎ 　以前はアフロダイＡに搭乗して、甲児達と共に敵と戦っていた。 ⏎ 　戦闘獣軍団の侵攻に伴い、甲児とパリから日本へ向かったが、ミケーネ帝国が差し向けたゴーゴン大公の攻撃で負傷した。
> EN (odniesienie oficjalne, NIE polski): The daughter of the director of the Photon Power Laboratory, Professor Yumi. ⏎  ⏎ Sunny and lively, she harbors feelings for Koji Kabuto. ⏎  ⏎ She used to fight alongside Koji as the pilot of Aphrodite A. ⏎  ⏎ When the Battle Beast Army begins its attack, she leaves Paris with Koji to go to Japan. She is injured by Archduke Gorgon, an assassin sent by the Mycenae Empire.

### dic\_pilot\_JUNK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b004\]
> JP (źródło tłumaczenia): 　ビューナスＡの操縦者。 ⏎ 　光子力研究所のオペレーターを務める。 ⏎ 　全世界へ侵攻を開始した戦闘獣と戦うべく、ビューナスＡを駆り、オーストラリアのシドニーで激戦を繰り広げる。
> EN (odniesienie oficjalne, NIE polski): The pilot of Venus A. ⏎  ⏎ She is one of the operators of the Photon Power Laboratory. ⏎  ⏎ During the Mycenae Empire's invasion of Earth, she bravely stands her ground against the Battle Beasts in Sydney, Australia.

### dic\_pilot\_JUNK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b005\]
> JP (źródło tłumaczenia): 　七大将軍の一角である悪霊将軍ハーディアスとの戦闘で敗北したが、一命は取り留めた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She is defeated by Spectral General Hadias, one of the leaders of the Seven Armies, narrowly escaping death.

### dic\_pilot\_BOSSK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b006\]
> JP (źródło tłumaczenia): 　ボスボロットの操縦者。 ⏎ 　甲児のよき友人であり、幾度も共に死線をくぐり抜けてきた。 ⏎ 　がさつな性格である一方、友情に厚く、甲児のピンチに助太刀に現れる。 ⏎ 　ヌケ、ムチャという二人の子分を連れて行動する事が多い。
> EN (odniesienie oficjalne, NIE polski): The pilot of Boss Robot. ⏎  ⏎ One of Koji's closest friends, they have brushed shoulders with death together many times. ⏎  ⏎ Though he can be tactless and ill-mannered, his loyalty is unquestionable, and he will always show up to help Koji in his time of need. ⏎  ⏎ He is rarely seen without his two sidekicks, Nuke and Mucha.

### dic\_pilot\_BOSSK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b007\]
> JP (źródło tłumaczenia): 　ミケーネ帝国が差し向けたゴーゴン大公の襲撃から甲児を救い、ボスボロットでカイザースクランダーを手配する等、様々な場面で甲児をサポートした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the Mycenae Empire's invasion of Earth, he supports Koji in many ways, such as rescuing him from Archduke Gorgon and hiding the Kaiser Scrander inside Boss Robot.

### dic\_pilot\_NUKEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b008\]
> JP (źródło tłumaczenia): 　ボスの子分の一人。 ⏎ 　気弱な性格ののんびり屋で、鼻水を垂らしている事が多い。
> EN (odniesienie oficjalne, NIE polski): One of Boss's sidekicks. ⏎  ⏎ He has a more timid disposition than Mucha. Very laid-back, he is often seen with a runny nose.

### dic\_pilot\_MUTYAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b00a\]
> JP (źródło tłumaczenia): 　ボスの子分の一人。 ⏎ 　気の強い性格で、ボスに意見する事もある。
> EN (odniesienie oficjalne, NIE polski): One of Boss's sidekicks. ⏎  ⏎ He has a more assertive disposition than Nuke. He occasionally expresses his opinions to Boss.

### dic\_pilot\_YUMIK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b00c\]
> JP (źródło tłumaczenia): 　光子力研究所の所長で、さやかの父。 ⏎ 　戦闘獣による世界侵攻が進む中、宇宙に浮かぶ研究施設・第二光子力研究所で強化していたマジンカイザーを地球へと送り込む。
> EN (odniesienie oficjalne, NIE polski): The director of the Photon Power Laboratory and Sayaka's father. ⏎  ⏎ Before the Battle Beasts' invasion, he was overhauling Mazinkaiser at the Second Photon Power Laboratory in space; at the peak of the invasion, he sends the super robot to Earth, allowing Koji Kabuto to turn the tide.

### dic\_pilot\_MRMRK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b00e\]
> JP (źródło tłumaczenia): 　兜十蔵博士の弟子で、三博士の一人。 ⏎ 　大柄な体型と立派なあごひげが特徴。 ⏎ 　甲児達と共にパリへ視察旅行へ訪れた際、戦闘獣の襲撃に遭い、欧州連合軍の基地に不時着する。
> EN (odniesienie oficjalne, NIE polski): One of the Doc Trio of the Photon Power Laboratory, pupils of Dr. Juzo Kabuto. ⏎  ⏎ He is recognizable by his large build and his distinguished beard. ⏎  ⏎ During a trip to Paris with Koji Kabuto and his friends, they are attacked by Battle Beasts and crash-land at a base of the European Union forces.

### dic\_pilot\_MRMRK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b00f\]
> JP (źródło tłumaczenia): 　甲児を無事に日本へ送り届けるため、基地に一人で残り、その身を犠牲にして戦闘獣を足止めした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ To ensure that Koji reaches Japan, he remains at the base, sacrificing his life to stop the Battle Beasts.

### dic\_pilot\_SEWAK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b010\]
> JP (źródło tłumaczenia): 　兜十蔵博士の弟子で、三博士の一人。 ⏎ 　小柄な体格と大きな口ひげが特徴で、せっかちな性格。
> EN (odniesienie oficjalne, NIE polski): One of the Doc Trio of the Photon Power Lab, pupils of Dr. Juzo Kabuto. ⏎  ⏎ He is recognizable by his short stature and impressive mustache. He is very restless and impatient.

### dic\_pilot\_NOSSOK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b012\]
> JP (źródło tłumaczenia): 　兜十蔵博士の弟子で、三博士の一人。 ⏎ 　三博士の中でも背が一番高く、大きな眉が特徴。 ⏎ 　おっとりとしており、物静かな性格。　
> EN (odniesienie oficjalne, NIE polski): One of the Doc Trio of the Photon Power Laboratory, pupils of Dr. Juzo Kabuto. ⏎  ⏎ He is recognizable by his tall stature and his prominent eyebrows. ⏎  ⏎ He has a calm personality and can be overly methodical at times.

### dic\_pilot\_SIROK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b014\]
> JP (źródło tłumaczenia): 　甲児の弟。 ⏎ 　元気で好奇心旺盛な性格であると同時に、兄想いの一面を持つ。 ⏎ 　第二光子力研究所から甲児や仲間達の戦いを応援する。
> EN (odniesienie oficjalne, NIE polski): Koji Kabuto's little brother. ⏎  ⏎ Full of youthful energy and curiosity, he occasionally displays a maturity beyond his age. ⏎  ⏎ He cheers on Koji and his friends from the Second Photon Power Laboratory.

### dic\_pilot\_DRKENPK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b016\]
> JP (źródło tłumaczenia): 　ミケーネ帝国の支配者。 ⏎ 　七大将軍を率いる暗黒大将軍を配下に従える絶対の権力者であり、地上から人類を駆逐するべく、永い眠りから目を覚ました。 ⏎ 　全身が炎と化している。
> EN (odniesienie oficjalne, NIE polski): The supreme ruler of the Mycenae Empire. ⏎  ⏎ After awakening from his long slumber, he commands the Great General of Darkness to lead the Seven Armies and wipe the human race from the face of the earth. ⏎  ⏎ His body is entirely made of flames.

### dic\_pilot\_DRKJENK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b018\]
> JP (źródło tłumaczenia): 　七つの戦闘獣軍団を率いるミケーネ帝国の将軍。 ⏎ 　数千年の間、地底に潜伏していたが、地球を征服するため地上に現れる。 ⏎ 　全世界に向け、人類とその文明の抹殺を宣言した。
> EN (odniesienie oficjalne, NIE polski): The general of the Seven Battle Beast Armies of the Mycenae Empire. ⏎  ⏎ After biding his time underground for thousands of years, he begins his conquest of Earth. ⏎  ⏎ In a message to the entire world, he declares death upon humanity and the destruction of its civilization.

### dic\_pilot\_DRKJENK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b019\]
> JP (źródło tłumaczenia): 　圧倒的なパワーでマジンカイザーを苦しめるも、仲間への想いに燃える甲児の猛攻の前に敗北した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though he initially overpowers Mazinkaiser, he is ultimately defeated by Koji Kabuto, fueled by the hopes and dreams of his fallen comrades.

### dic\_pilot\_HADEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01a\]
> JP (źródło tłumaczenia): 　七大将軍の一人で悪霊型戦闘獣の長。 ⏎ 　大鎌を武器とする。 ⏎ 　ジュンの搭乗するビューナスＡを斬り刻み、戦闘不能となるまで追い詰めた。
> EN (odniesienie oficjalne, NIE polski): One of the generals of the Seven Armies, leading the Spectral Battle Beasts. ⏎  ⏎ He wields a scythe as a weapon. ⏎  ⏎ He tears apart Jun's Venus A, rendering it unable to fight.

### dic\_pilot\_HADEK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01b\]
> JP (źródło tłumaczenia): 　他の戦闘獣と共に光子力研究所を陥落させるも、マジンカイザーの冷凍ビームにより凍結させられた後に砕け散った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He conquers the Photon Power Laboratory with other Battle Beasts, but ultimately he is frozen and shattered by Mazinkaiser's Freeze Beam.

### dic\_pilot\_DNTEK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01c\]
> JP (źródło tłumaczenia): 　光子力研究所を襲った悪霊型戦闘獣。 ⏎ 　戦闘獣軍団のリーダー格であり、甲児の抹殺を宣言する。
> EN (odniesienie oficjalne, NIE polski): One of the spectral-type Battle Beasts attacking the Photon Power Laboratory. ⏎  ⏎ As a Battle Beast commander, he declares death upon Koji Kabuto.

### dic\_pilot\_DNTEK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01d\]
> JP (źródło tłumaczenia): 　パイルダーオン直後に放たれたマジンカイザーの光子力ビームの直撃を受け、消滅した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Within seconds of Mazinkaiser's activation, he is hit square on by a Photon Power Beam and disintegrates.

### dic\_pilot\_GGONK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01e\]
> JP (źródło tłumaczenia): 　ミケーネ帝国が送り込んだ刺客。 ⏎ 　下半身が虎になっている。 ⏎ 　暗黒大将軍からの命を受け、甲児を暗殺するためにつけ狙う。
> EN (odniesienie oficjalne, NIE polski): An assassin dispatched by the Mycenae Empire. ⏎  ⏎ The lower half of his body is a tiger. ⏎  ⏎ Under orders of the Great General of Darkness, he stalks Koji Kabuto to assassinate him.

### dic\_pilot\_GGONK\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90a0b01f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b01f\]
> JP (źródło tłumaczenia): 　生身の甲児を追い詰めるが、現れたボスの活躍によって阻止される。最期は甲児の放った光子銃に身体を貫かれ、業火の中へ消えていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He almost succeeds in killing Koji but is stopped by Boss's intervention. Ultimately, he falls to Koji's photon gun before being consumed by a raging fire.

### dic\_pilot\_TAKUMA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90a0b020`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90a0b020\]
> JP (źródło tłumaczenia): 　ゲッターアークのパイロット。１９歳。 ⏎ 　初代ゲッターチームの流竜馬の息子であり、血気盛んな性格。 ⏎ 　生まれつき頑丈な身体を持ち、ゲッター操縦時にかかる重力負荷にパイロットスーツなしで耐え切る他、怪我からの回復も人一倍早い。 ⏎ 　コンビニのオニギリが好物。 ⏎ 　幼少期に母親を殺されており、その仇となる人物を探し出すため、山岸獏と共に早乙女研究所を訪れた。 ⏎ 　運命に導かれるようにゲッターロボに乗り、人類の敵と戦う。
> EN (odniesienie oficjalne, NIE polski): The pilot of Getter Arc. He is 19 years old. He is the son of Ryoma Nagare of the original Getter Team. ⏎  ⏎ A young man with a passionate personality, he is gifted with a sturdy body capable of withstanding the g-force burden of piloting Getter without wearing a pilot suit; furthermore, he can heal from injuries more quickly than the average person. His favorite food is convenience store rice balls. ⏎  ⏎ His mother was killed when he was a child. To find her murderer, he visits the Saotome Laboratory with his friend Baku Yamagishi. As if guided by fate, he boards Getter Robo and starts fighting the enemy of humanity.

### dic\_pilot\_TAKUMA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b000\]
> JP (źródło tłumaczenia): 　戦いの中、ゲッターロボを狙うアンドロメダ流国の中に母親の仇であるマクドナルドを見つけ出し、遥か未来の宇宙でその決着をつける。 ⏎ 　その後は現代へと帰還し、ゲッターエンペラーと人類による宇宙の支配を知って敵となったカムイを止めるべく戦った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the conflict, he discovers that McDonald, his mother's murderer, is a member of the Andromeda Stellaration. Eventually, he is able to get his revenge in the faraway future. ⏎  ⏎ After returning to the present time, he faces Kamui, who had decided to eradicate humanity to prevent their domination of the galaxy and the creation of Getter Emperor.

### dic\_pilot\_KAMUI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b001\]
> JP (źródło tłumaczenia): 　ゲッターキリクのパイロット。１９歳。 ⏎ 　かつてゲッターロボに敗北した恐竜帝国のハチュウ人類と人類のハーフであり、その事をからかう者を許さない。 ⏎ 　人類とは異なる風貌をしており、強靭な肉体と身体能力を兼ね備えている。 ⏎ 　幼少期から早乙女研究所の神隼人の下で育てられ、ゲッターロボのパイロットとして訓練されてきた。
> EN (odniesienie oficjalne, NIE polski): The pilot of Getter Kirik. He is 19 years old. He is a hybrid between a human and a Saurian from the Dinosaur Empire, defeated by Getter Robo long ago; he does not tolerate any slights or insults about this. ⏎  ⏎ Due to his Saurian blood, he has a different appearance from humans. He is gifted with a stronger body and greater physical abilities than the average human. ⏎  ⏎ He was raised by Hayato Jin at the Saotome Laboratory, who trained him to become a Getter Robo pilot.

### dic\_pilot\_KAMUI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b002\]
> JP (źródło tłumaczenia): 　遥か未来の宇宙で人類が行き着く進化の恐ろしさを目の当たりにし、そこで百鬼帝国の生き残りであるマクドナルドから最終兵器・バグを託される。 ⏎ 　現代に戻った後、皇帝ゴール三世から恐竜帝国の実権を奪い、完成させたバグを駆って人類の敵として拓馬達の前に立ち塞がった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In his journey to the faraway future, he witnesses the horrors of humanity's evolution. McDonald, one of the survivors of the Hyakki Empire, entrusts him with the ultimate weapon BUG. ⏎  ⏎ When he returns to the present time, he stages a coup, deposing Emperor Gore III and taking the reins of the Dinosaur Empire. After perfecting the design of the BUG, he stands against Takuma as the enemy of humanity.

### dic\_pilot\_BAKU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b003\]
> JP (źródło tłumaczenia): 　ゲッターカーンのパイロット。２２歳。 ⏎ 　かつて真ゲッターロボに搭乗したグリーンアース教の先代教祖・タイールの弟にあたる。 ⏎ 　かすかな予知能力を持つが、兄の力には遠く及ばない事を認識しており、それに負い目を感じている。 ⏎ 　心優しい性格の巨漢。 ⏎ 　幼少期から共に旅をしてきた拓馬を支えながら、ゲッターに関わる者の運命を受け入れ、ゲッターチームの一員として戦う道を選ぶ。
> EN (odniesienie oficjalne, NIE polski): The pilot of Getter Khan. He is 22 years old. He is the younger brother of Tahir, the founder of the Green Earth Religion who piloted Shin Getter Robo in the past. ⏎  ⏎ While he possesses a premonition ability, he is painfully aware that his powers pale in comparison to his brother's. ⏎  ⏎ A big man with a bigger heart, he has been traveling with Takuma since childhood, always ready to support him. He accepts the fate of those chosen by Getter, fighting as a member of Getter Team.

### dic\_pilot\_BAKU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b004\]
> JP (źródło tłumaczenia): 　遥か未来の宇宙でゲッターエンペラーと人類による宇宙の支配を知った後は、別の道を探し出すべく、ゲッターエンペラーが作り出した空間に残る事を選択した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After learning that humanity and Getter Emperor rule over the galaxy in the faraway future, he chooses to stay in the space created by Getter Emperor to find a new path.

### dic\_pilot\_HAYATOA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b005\]
> JP (źródło tłumaczenia): 　早乙女研究所の所長。 ⏎ 　初代ゲッターチームのメンバーであり、亡き早乙女博士の遺志を継いでゲッター線の研究を続ける。 ⏎ 　その一方で地球各地に出現する未知の敵と戦うべく、司令官としてゲッターＤ２部隊の運用も任されている。 ⏎ 　様々な戦いで多くの仲間を失っており、それ故に強い責任感と覚悟を持つ。
> EN (odniesienie oficjalne, NIE polski): The director of the Saotome Laboratory. One of the pilots of the original Getter Team, he continues the research on Getter Rays, carrying on the legacy of the late Dr. Saotome. ⏎  ⏎ He is also the general of the Getter D2 squadron, fighting against the unknown enemy threatening the world. Having lost many of his comrades throughout various conflicts, he has a strong sense of responsibility and an unwavering determination.

### dic\_pilot\_HAYATOA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b006\]
> JP (źródło tłumaczenia): 　未来から帰還したカムイ率いる恐竜帝国が早乙女研究所へと侵攻した際には、ゲッターザウルスのパイロット達を格闘で圧倒する。 ⏎ 　しかし、カムイに背中を撃たれた事で研究所の最深部に落下し、人類の未来を拓馬達に託してゲッタードラゴンの眠る「地獄の釜」の蓋を開いた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When the Dinosaur Empire led by Kamui (who had returned from the future) attacks the Saotome Laboratory, he overwhelms the Gettersaurus pilots with his fighting skills. ⏎  ⏎ After being shot by Kamui, he falls to the deepest part of the laboratory. There, he opens the lid of the Cauldron of Hell, where Getter Dragon slumbers, leaving the future of humanity in the hands of the younger generation.

### dic\_pilot\_SHIKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b007\]
> JP (źródło tłumaczenia): 　早乙女研究所の兵器開発主任。 ⏎ 　大小を問わず様々な武器や兵器を開発しており、研究所全体の防衛システムも手掛ける。 ⏎ 　常識外れの火器や爆発を好むマッドサイエンティストで、自らの身体もサイボーグ化しており、全身が武器となっている。 ⏎ 　古くから早乙女研究所を守ってきた人物であり、拓馬の父・竜馬とも面識がある。
> EN (odniesienie oficjalne, NIE polski): The head of Saotome Laboratory's weapons research and development. ⏎  ⏎ In addition to developing a wide variety of weapons of all kinds and sizes, he is also in charge of the lab's defense systems. ⏎  ⏎ A mad scientist with a penchant for unconventional firearms and (many, many) explosions, he has cybernetically enhanced his own body to become a living weapon. ⏎  ⏎ He has protected the Saotome Laboratory for a long time and knew Takuma's father, Ryoma, back when Ryoma was a Getter pilot.

### dic\_pilot\_IGARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b009\]
> JP (źródło tłumaczenia): 　ゲッターＤ２を運用するチームの隊長。 ⏎ 　面倒見のいい性格であり、チームのメンバーからも信頼されている。 ⏎ 　元々はゲッターロボの予備パイロットであったが、指導教官を経て現在に至った。
> EN (odniesienie oficjalne, NIE polski): Chief of the Getter D2 squadron. He has earned the trust of his team thanks to his caring personality. ⏎  ⏎ He was originally a reserve pilot for Getter Robo, but has assumed the role of instructor since then.

### dic\_pilot\_KOMEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b00b\]
> JP (źródło tłumaczenia): 　遥か宇宙の彼方から、地球へ戦闘兵器・インセクターを送り込む指揮官。 ⏎ 　その目的と正体は不明。
> EN (odniesienie oficjalne, NIE polski): The commander of the Insectors, attacking Earth from a faraway location in space. ⏎  ⏎ His purpose and identity are shrouded in mystery.

### dic\_pilot\_KOMEI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b00c\]
> JP (źródło tłumaczenia): 　その正体は、アンドロメダ流国の統治者である大女王メルドウサから地球攻略を任された指揮官であり、宇宙を支配する人類とそれを生み出すゲッターエンペラーを消滅させる事が目的であった。 ⏎ 　ゲッターロボを破壊するために本拠地を大爆発させ、その炎の中で消滅していった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It is later revealed that he is acting under the orders of Supreme Queen Meldusa, leader of the Andromeda Stellaration. His purpose is to annihilate humanity, preventing them from taking over the galaxy and creating Getter Emperor. ⏎  ⏎ In his attempt to destroy Getter Robo, he generates a massive explosion from within his stronghold, vanishing within the flames.

### dic\_pilot\_MACD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b00d\]
> JP (źródło tłumaczenia): 　コーメイの懐刀。 ⏎ 　拓馬の母親を殺した張本人であり、同時に拓馬の生命をつけ狙うが、その目的は不明。
> EN (odniesienie oficjalne, NIE polski): Kongming's right-hand man. ⏎  ⏎ He is the man responsible for the death of Takuma's mother. He seems to be obsessed with Takuma, but his goals are unknown.

### dic\_pilot\_MACD\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b00e\]
> JP (źródło tłumaczenia): 　その正体は過去に滅んだ百鬼帝国の生き残り。 ⏎ 　ゲッターロボに倒されたブライ大帝の無念を晴らすべく、ゲッターロボとそのパイロットである流竜馬の息子・拓馬の生命を狙っていた。 ⏎ 　拓馬達が未来へ転移してきた際にはカムイに最終兵器・バグを託し、自らは魔獣ウザーラを駆って戦ったが、拓馬達の前に敗れ去った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is later revealed to be one of the survivors of the Hyakki Empire, which was destroyed long ago. He seeks to avenge the death of Emperor Brai by destroying Getter Robo and killing Takuma, son of Ryoma Nagare, who caused the ruin of the Hyakki Empire. ⏎  ⏎ During the Getter Team's journey to the future, he entrusts Kamui with the ultimate weapon BUG. Then, he faces Takuma with the Legendary Beast Uzala, but he is ultimately defeated.

### dic\_pilot\_TOEN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b00f\]
> JP (źródło tłumaczenia): 　戦闘兵器・インセクターを率いる前線指揮官。 ⏎ 　ストーカと呼ばれる亜空間ゲートから現れ、早乙女研究所にインセクターを先導する。 ⏎ 　擬態能力と分身能力を持っており、ゲッターＤ２部隊を翻弄した。
> EN (odniesienie oficjalne, NIE polski): The front commander leading the Insector army. ⏎  ⏎ He appears through the hyperspace gate known as the Stoker and leads the Insectors to the Saotome Laboratory. ⏎  ⏎ He toys with the Getter D2 squadron, using his shape-shifting and multiplying abilities.

### dic\_pilot\_TOEN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b010\]
> JP (źródło tłumaczenia): 　正式にゲッターのパイロットとなった拓馬達の初陣で、ゲッターアークのダブルトマホークで倒された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He was killed by Getter Arc's Double Tomahawk attack during Takuma, Kamui, and Baku's first official deployment as Getter pilots.

### dic\_pilot\_QEIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b011\]
> JP (źródło tłumaczenia): 　アンドロメダ流国が送り込んだ生物。 ⏎ 　繫殖能力が高く、大量の蟲を産卵する。 ⏎ 　孵化した蟲は人間の身体を乗っ取り、昆虫人間へと変容させる。 ⏎ 　配下の無数の蟲を従えて、旧早乙女研究所の最深部を占拠した。
> EN (odniesienie oficjalne, NIE polski): A creature sent by the Andromeda Stellaration. ⏎  ⏎ Her high reproductive capacity allows her to spawn insects in large quantities. The newly hatched spawn take over people and turn them into humanoid insect creatures. ⏎  ⏎ With countless such beings under her control, she easily occupies the deepest area of the old Saotome Laboratory.

### dic\_pilot\_QEIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b012\]
> JP (źródło tłumaczenia): 　研究所を壊滅寸前まで追い詰めるも、最期はゲッターアークに噛み潰された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though she almost causes the destruction of the laboratory, she ultimately meets her end in the jaws of Getter Arc.

### dic\_pilot\_GOAL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b013\]
> JP (źródło tłumaczenia): 　恐竜帝国の皇帝。 ⏎ 　過去の戦いでゲッターロボに倒された帝王ゴールの血を引く。 ⏎ 　地球の脅威となるインセクターに対抗するため、人類と和平を結び、早乙女研究所との同盟軍を結成した。
> EN (odniesienie oficjalne, NIE polski): The emperor of the Dinosaur Empire. He is the descendant of Emperor Gore, who was defeated by Getter Robo long ago. ⏎  ⏎ He makes peace with humanity and allies with the Saotome Laboratory to oppose the threat of the Insectors.

### dic\_pilot\_GOAL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b014\]
> JP (źródło tłumaczenia): 　表向きは人類と手を組む一方、裏ではアンドロメダ流国との戦いの後にゲッターロボを破壊するようにカムイに命令する。 ⏎ 　しかし、カムイが未来から戻ってきた後はクーデターによって実権を奪われ、傀儡の皇帝となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ But this is only a ruse. Behind the scenes, he orders Kamui to destroy Getter Robo when the Andromeda Stellaration is defeated. ⏎  ⏎ However, Kamui stages a coup when he returns from the future. Gore is deprived of his authority and becomes a puppet ruler.

### dic\_pilot\_HAN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b015\]
> JP (źródło tłumaczenia): 　恐竜帝国の科学長官。 ⏎ 　組織の中でも穏健派の長老であり、ハチュウ人類と人類の共存による平和を願っている。 ⏎ 　カムイの過去を知る数少ない人物でもある。
> EN (odniesienie oficjalne, NIE polski): The elderly head of the Dinosaur Empire's scientific department. He belongs to the moderate faction of the empire, believing that Saurians and humanity can find peace through coexistence. He is one of the few individuals who are aware of Kamui's past.

### dic\_pilot\_HAN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b016\]
> JP (źródło tłumaczenia): 　亜空間固定装置ゾルドを組み立て、ゲッターチームとザウルスチームを時空の果てへと転移させた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He develops the hyperspace anchor module Zold, allowing the Getter and Saurus teams to travel through time and space.

### dic\_pilot\_BAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b017\]
> JP (źródło tłumaczenia): 　恐竜帝国の老将。 ⏎ 　帝王ゴールが治めていた時代からの唯一の生き残り。 ⏎ 　かつての流竜馬との戦いを語る事が生き甲斐になっており、その老いた姿は周囲から呆れられている。
> EN (odniesienie oficjalne, NIE polski): An old general of the Dinosaur Empire. He is the sole survivor of Emperor Gore's rule. ⏎  ⏎ He lives to tell the tale of his battles with Ryoma Nagare, though most around him do not take him seriously due to his elderly age.

### dic\_pilot\_BAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b018\]
> JP (źródło tłumaczenia): 　未来から戻ってきたカムイが蜂起した際には、かつての力強さを取り戻し、カムイ側についた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kamui returns from the future and stages his coup, he drops his facade, joining Kamui's side as he reveals that he has never lost his former vigor.

### dic\_pilot\_BYS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b019\]
> JP (źródło tłumaczenia): 　ゲッターザウルスのメインパイロット。 ⏎ 　ハチュウ人類の中でも下層民である地リュウ一族の出身。 ⏎ 　他の一族に比べて生命を軽視されており、発言権を得るためにパイロットに志願した。武功を挙げるべく、身を賭して戦う。 ⏎ 　好戦的な性格で拓馬と対立する事も多い。 ⏎ 　カムイとは幼馴染であり、慕うと同時に敬意を払っている。
> EN (odniesienie oficjalne, NIE polski): The main pilot of Gettersaurus. He is a Terrasaur, considered a lower class among Saurians. ⏎  ⏎ As his race is valued the least within the Dinosaur Empire, he volunteers to pilot Gettersaurus to be acknowledged by his peers, risking his life for military success. ⏎  ⏎ His quarrelsome personality often puts him at odds with Takuma. He has great admiration and respect for Kamui, his childhood friend.

### dic\_pilot\_BYS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01a\]
> JP (źródło tłumaczenia): 　未来から帰還したカムイが決起した際には、それに従って人類の敵となる。 ⏎ 　早乙女研究所で神隼人を討つべく生身で戦うも、返り討ちに遭った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kamui returns from the future and stages his coup, he joins his side, becoming an enemy of humanity. ⏎  ⏎ He joins the attack on the Saotome Laboratory, trying to kill Hayato Jin, but he dies at the hands of his would-be victim.

### dic\_pilot\_GNRY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01b\]
> JP (źródło tłumaczenia): 　ゲッターザウルスのサブパイロット。 ⏎ 　バイス、ゴズロと同じく、地リュウ一族の出身。
> EN (odniesienie oficjalne, NIE polski): One of the sub-pilots of Gettersaurus. He is a Terrasaur, like Vise and Gozro.

### dic\_pilot\_GNRY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01c\]
> JP (źródło tłumaczenia): 　未来から帰還したカムイが決起した際には、それに従って人類の敵となる。 ⏎ 　早乙女研究所で神隼人を討つべく生身で戦うも、返り討ちに遭った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kamui returns from the future and stages his coup, he joins his side, becoming an enemy of humanity. ⏎  ⏎ He joins the attack on the Saotome Laboratory, trying to kill Hayato Jin, but he dies at the hands of his would-be victim.

### dic\_pilot\_GOZR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01d\]
> JP (źródło tłumaczenia): 　ゲッターザウルスのサブパイロット。 ⏎ 　バイス、ガンリューと同じく、地リュウ一族の出身。
> EN (odniesienie oficjalne, NIE polski): One of the sub-pilots of Gettersaurus. He is a Terrasaur, like Vise and Ganryu.

### dic\_pilot\_GOZR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01e\]
> JP (źródło tłumaczenia): 　未来から帰還したカムイが決起した際には、それに従って人類の敵となる。 ⏎ 　早乙女研究所で神隼人を討つべく生身で戦うも、返り討ちに遭った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kamui returns from the future and stages his coup, he joins his side, becoming an enemy of humanity. ⏎  ⏎ He joins the attack on the Saotome Laboratory, trying to kill Hayato Jin, but he dies at the hands of his would-be victim.

### dic\_pilot\_MUSASHIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b01f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b01f\]
> JP (źródło tłumaczenia): 　ゲッター軍団の司令官。 ⏎ 　初代ゲッターロボのベアー号のパイロットを務めた人物で、かつての恐竜帝国との決戦で戦死している。 ⏎ 　地球人類の存亡を懸けた戦いに身を置き、敵に対しては冷酷な一面を見せる。
> EN (odniesienie oficjalne, NIE polski): The general of the Getter Legion. He was the pilot of the Bear machine of the original Getter Robo, who sacrificed his life against the Dinosaur Empire. ⏎  ⏎ He is currently engaged in a war for the survival of humanity, fighting with chilling ruthlessness.

### dic\_pilot\_MUSASHIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b020`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b020\]
> JP (źródło tłumaczenia): 　その正体は「巴武蔵」の遺伝子を受け継ぐ人造人間であり、ゲッターエンペラーの記憶に基づいて造られた。多数が存在しており、戦死しても記憶を受け継いだ新たな個体が即座に戦線に復帰する。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It is later revealed that he is a manufactured human who has inherited the genes of Musashi Tomoe, created based on Getter Emperor's memories. He is one of many, and even if he dies in battle, a new Musashi would immediately take his place, inheriting the memories of his previous iteration.

### dic\_pilot\_KAMMOM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b021`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b021\]
> JP (źródło tłumaczenia): 　カムイの母親。 ⏎ 　帝王ゴールが治めていた時代の恐竜帝国にさらわれて、ゴールの子であるカムイを生む。 ⏎ 　人望が厚いカムイを従わせるため、ゴール三世に人質として幽閉されており、息子とは会えない日々を過ごす。
> EN (odniesienie oficjalne, NIE polski): Kamui's human mother. She was kidnapped by the Dinosaur Empire during the reign of Emperor Gore, giving birth to his son, Kamui. ⏎  ⏎ She is held hostage by Emperor Gore III to keep Kamui, who is very popular among Saurians, under control.

### dic\_pilot\_KAMMOM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:90e0b022`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b022\]
> JP (źródło tłumaczenia): 　恐竜帝国の実権を握ったカムイが帝国内の人類を始末しようとした際、抵抗したロン・シュヴァイツァが放った銃弾からカムイをかばい、息子の腕の中で息を引き取った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kamui returns from the future and stages his coup, Ron Schweitzer tries to stop him with a gun; Kamui's mother covers her son with her own body, dying shortly after in his arms.

### dic\_pilot\_SHUVI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:90e0b023`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:90e0b023\]
> JP (źródło tłumaczenia): 　国連から恐竜帝国に派遣された研究者。 ⏎ 　かつて国連軍所属の静止衛星の所長を務め、１９年前に真ゲッターロボが火星へ飛ぶ姿を目撃した。
> EN (odniesienie oficjalne, NIE polski): A scientist dispatched to the Dinosaur Empire by the UN. ⏎  ⏎ He was the director of a stationary satellite for the UN forces 19 years ago; on that occasion, he witnessed Shin Getter Robo's flight to Mars.

### dic\_pilot\_SHUVI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b000\]
> JP (źródło tłumaczenia): 　恐竜帝国のハン博士と共に亜空間固定装置ゾルドを研究し、拓馬達を未来の宇宙へ送り出した。 ⏎ 　恐竜帝国の実権を握ったカムイが帝国内の人類を始末しようとした際、抵抗するも撃たれて死亡した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He develops the hyperspace anchor module Zold with Professor Han of the Dinosaur Empire, allowing Takuma and his comrades to travel through time and space. ⏎  ⏎ When Kamui takes over the Dinosaur Empire with the goal of annihilating humanity, he attempts to resist before being shot to death.

### dic\_pilot\_SHUWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b001\]
> JP (źródło tłumaczenia): 　連合軍の提督。 ⏎ 　かつては米軍所属の有人型ロボット「ステルバー」のパイロットを務めた。その戦いの中、一文字號の率いるゲッターチームと共闘し、橘翔とは恋仲となった。
> EN (odniesienie oficjalne, NIE polski): Admiral of the UN forces. ⏎  ⏎ He used to pilot the humanoid robot Stelber for the US military. During this time, he fought alongside Go Ichimonji's Getter Team and became romantically involved with Sho Tachibana.

### dic\_pilot\_SHOUG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b003\]
> JP (źródło tłumaczenia): 　連合軍の監査官。 ⏎ 　１９年前、人類の敵と戦ったゲッターチームの一員で、男勝りな性格。 ⏎ 　真ゲッターロボ タラクに乗って現れた、かつての仲間である一文字號を気にかけている。
> EN (odniesienie oficjalne, NIE polski): Inspector of the allied forces. ⏎  ⏎ She commands respect in a society ruled mainly by men. She was one of the members of Getter Team who fought for the sake of humanity 19 years ago. ⏎  ⏎ The unexpected arrival of Shin Getter Robo Tarak, piloted by her former comrade Go Ichimonji, weighs heavily on her mind.

### dic\_pilot\_GOUA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b005\]
> JP (źródło tłumaczenia): 　１９年前の戦いでゲッターロボを駆ったパイロット。 ⏎ 　その戦いの最後で流竜馬、山岸獏の兄・タイールと共に真ゲッターロボに搭乗して地球を救った後、消息不明となる。 ⏎ 　地球の危機に際し、真ゲッターロボ タラクに乗って現れた。
> EN (odniesienie oficjalne, NIE polski): One of the pilots of Getter Robo from 19 years ago. ⏎  ⏎ He piloted Shin Getter Robo alongside Ryoma Nagare and Baku Yamagishi's brother Tahir. Though they saved the Earth, they all disappeared from the face of the world. ⏎  ⏎ In Earth's moment of crisis, he shows up once more aboard Shin Getter Robo Tarak.

### dic\_pilot\_GOUA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b006\]
> JP (źródło tłumaczenia): 　亜空間固定装置ゾルドがアンドロメダ流国の攻撃で暴走した際には、その身を差し出してゾルドを守り、拓馬達を見送った後に機体と共に消滅した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When the Andromeda Stellaration's attack causes the hyperspace anchor module Zold to run amok, he uses his own life to protect the device and allow Takuma and his comrades to cross before disappearing from the world alongside his machine.

### dic\_pilot\_HAYATE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b007\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部・デルタ小隊に所属する新人パイロット。コールサインはデルタ５。 ⏎ 　規則に縛られる事を好まない奔放な性格。 ⏎ 　音やリズムに対する感性に優れており、踊るように機体を操る様は「インメルマン・ダンス」と周囲から称される。 ⏎ 　自由に空を飛ぶ事を信条としており、上官であるメッサーやミラージュと衝突する事も多い。 ⏎ 　惑星イオニデスにおけるヴァールシンドローム鎮圧任務の最中、貨物船で密航していた少女フレイアと出会いを果たす。
> EN (odniesienie oficjalne, NIE polski): The newest pilot of Delta Flight, employed by the interstellar conglomerate Xaos's Ragna branch. His callsign is Delta 5.  ⏎  ⏎ He has a wild personality and dislikes being bound by rules. His sense of rhythm is exceptional, and his dance-like fighting style has been named the Immelmann Dance, in praise, by onlookers. His creed is to fly in the sky freely, which often brings him in conflict with his superiors such as Messer and Mirage. ⏎  ⏎ During a mission to suppress Vár Syndrome on the planet Ionideth, he met Freyja, who had stowed away on a transport.

### dic\_pilot\_HAYATE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b008\]
> JP (źródło tłumaczenia): 　戦いの中、フレイアと交流を重ね、自分の飛ぶ意味を見つけていく。 ⏎ 　最終決戦ではフレイアと共に突破口を開き、ウィンダミア王国の最大戦力シグル＝バレンスの中枢を破壊して、戦いの終結に大きく貢献した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In combat he and Freyja come together time and again, leading to him discovering a reason to fly. ⏎  ⏎ Together with Freyja he cuts a path in the final battle, breaking into the core of an enormous Windermerian battleship, the Sigur Berrentzs, which proved key to ending the battle.

### dic\_pilot\_MIRAGE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b009\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部・デルタ小隊に所属する女性パイロット。コールサインはデルタ４。 ⏎ 　生真面目な性格で規律に厳格な所がある。 ⏎ 　かつての大戦で大きな戦功を挙げたマクシミリアン・ジーナスの孫に当たり、偉大な「ジーナス家」に生まれた重圧を感じている。 ⏎ 　新人パイロットであるハヤテの指導役を務める傍ら、彼の自由な生き方に影響を受け、恋心を抱くようになる。
> EN (odniesienie oficjalne, NIE polski): A Delta Squadron pilot with the interstellar conglomerate Xaos's Ragna branch. Her callsign is Delta 4.  ⏎  ⏎ She is extremely serious and can be quite a fussbudget about the rules. ⏎  ⏎ As one of the grandchildren of Maximillian Jenius, the legendary war hero who contributed massively in the great conflicts with the Zentradi and Protodeviln, she finds the legacy of the Jenius name overwhelming. ⏎  ⏎ While serving as a mentor to newly-inducted squadmate Hayate, she finds herself attracted to his carefree attitude towards life and develops feelings for him.

### dic\_pilot\_MIRAGE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b00a\]
> JP (źródło tłumaczenia): 　戦いの中、互いに惹かれ合うハヤテとフレイアの姿を見て、自身の想いには決着をつけるものの、飛ぶ意味を見つけた事で自らを縛っていた重圧から解放される。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When she discovered that Hayate and Freyja had developed feelings for each other over the course of the war, she put an end to her own romantic attraction, but nonetheless her relationship with Hayate helped her discover a reason for her to fly herself, freeing her from her burdens.

### dic\_pilot\_ARAD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b00b\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部・デルタ小隊の隊長を務めるパイロット。コールサインはデルタ１。 ⏎ 　懐の大きい人物で、癖の強いパイロット達をまとめ上げている。 ⏎ 　指揮官を務めるだけでなく、新人パイロットのスカウティングも行う。 ⏎ 　かつては新統合軍に在籍しており、マクロス・エリシオン艦長のアーネストとは当時からの戦友。
> EN (odniesienie oficjalne, NIE polski): A pilot who serves as the commander of Delta Flight, employed by interstellar conglomerate Xaos's Ragna branch. His callsign is Delta 1.  ⏎  ⏎ He is a considerate, wise man, which helps him command the very unique personalities of Delta Flight. In addition to serving as their commanding officer, he also scouts new hires. He once served with N.U.N.S, with the captain of the Macross Elysion, Ernest, being a former comrade from that period.

### dic\_pilot\_MESSA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b00d\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部・デルタ小隊に所属するパイロット。コールサインはデルタ２。 ⏎ 　冷静な性格で、状況判断力に優れるデルタ小隊のエース格。 ⏎ 　自他共に対して厳しい一面を持ち、隊のパイロット達の指導役も務める。 ⏎ 　２年前の戦闘でヴァール化したが、カナメの歌により沈静化を果たした過去を持つ。
> EN (odniesienie oficjalne, NIE polski): A Delta Flight pilot with the interstellar conglomerate Xaos's Ragna branch. His callsign is Delta 2.  ⏎  ⏎ He is a quiet, rational person, with situational judgment that easily makes him Delta Flight's ace pilot. He can be quite severe towards both himself and others, but is also a leader to the Delta pilots. ⏎  ⏎ He suffered from Vár Syndrome two years ago, which was suppressed by Kaname.

### dic\_pilot\_MESSA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b00e\]
> JP (źródło tłumaczenia): 　デルタ小隊でも屈指の操縦技術で、空中騎士団の白騎士・キースとも互角の戦いを見せる。 ⏎ 　その後、ヴァール化が再発した事により他部署への転属を命じられるも、惑星アル・シャハルでの戦闘に駆けつける。 ⏎ 　デルタ小隊とワルキューレの危機を救い、キース機を撃墜するが、ここまでのダメージにより、カナメの腕の中で息を引き取った。 ⏎ 　その愛機はハヤテへと引き継がれる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ As Delta Flight's leading man in pilot skill, he was able to fight the White Knight of the Aerial Knights, Keith, on equal footing. ⏎  ⏎ Due to his Vár Syndrome relapsing, he was to be transferred to a different group, but chose to set out onto the battlefield on Al Shahal nonetheless. He saved both Delta Flight and Walküre in a critical moment, as well as shot down Keith, but ravaged as he was by Vár Syndrome, he breathed his last in Kaname's arms. ⏎  ⏎ Hayate takes over his personal unit.

### dic\_pilot\_CHACK\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b00f\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部・デルタ小隊に所属するパイロット。コールサインはデルタ３。 ⏎ 　主に早期警戒任務を担当している。 ⏎ 　惑星ラグナで生まれたラグナ人で、身体に水かきやエラを持っている。 ⏎ 　底抜けに明るい性格で、誰にでも気さくに話しかける。 ⏎ 　平時は料理店「裸喰娘娘」（らぐにゃんにゃん）で料理人を務め、妹や弟達と共に店を営んでいる。
> EN (odniesienie oficjalne, NIE polski): A Delta Flight pilot with the interstellar conglomerate Xaos's Ragna branch. His callsign is Delta 3.  ⏎  ⏎ His primary responsibility is advance scouting missions. ⏎  ⏎ He is a native Ragnan, so his body has qualities like webbing and gills. He's a tremendously bright person, able to get along well with anyone. When Xaos isn't on contract, he works as the chef of the restaurant Rag-Nyan Nyan, together with his younger siblings.

### dic\_pilot\_ARNST\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b011\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部所属のマクロス級戦艦マクロス・エリシオンの艦長。 ⏎ 　地球人とゼントラーディのハーフで巨体の持ち主で、豪放な性格。 ⏎ 　かつては新統合軍に在籍しており、第一次ウィンダミア独立戦争が勃発する前はウィンダミア王国に軍事顧問として赴任していた経歴を持つ。
> EN (odniesienie oficjalne, NIE polski): The captain of the Macross-class ship, the Macross Elysion, in the employ of interstellar conglomerate Xaos's Ragna branch.  ⏎  ⏎ A large person in both heart and body, he is, in fact, half Earthnoid and half Zentradi. While he formerly served in the N.U.N.S., he also was employed by Windermere prior to the First Windermere War of Independence as a military advisor.

### dic\_pilot\_BESS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b013\]
> JP (źródło tłumaczenia): 　マクロス級戦艦マクロス・エリシオンのオペレーター。
> EN (odniesienie oficjalne, NIE polski): An operator aboard the Macross-class Macross Elysion.

### dic\_pilot\_KEES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9120b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b015\]
> JP (źródło tłumaczenia): 　ウィンダミア王家直属の精鋭部隊・空中騎士団のエースパイロット。 ⏎ 　「ダーウェントの白騎士」の称号を持つ。 ⏎ 　騎士道精神の持ち主で、祖国の平和を奪った新統合軍を打倒すべく、空中騎士団を率いて戦いに臨む。 ⏎ 　前国王グラミアの長男であったが、側室の子であったため、王位はハインツに譲っている。 ⏎ 　ウィンダミア王国の宰相であるロイド・ブレームとは幼少期からの友人。
> EN (odniesienie oficjalne, NIE polski): The ace pilot of the elite team under the direct command of the Windermerian royal family, the Aerial Knights. Known as the White Knight of Derwent.  ⏎  ⏎ A chivalrous man and a paragon of knighthood, he leads the Aerial Knights into battle against the New U.N. Spacy, which stole his homeland's peace. While he is the eldest son of the previous king, Grammier, he is the son of a concubine, and thus, the crown was handed to Heinz. ⏎  ⏎ He has been friends with the Windermerian prime minister, Roid Brehm, since they were children.

### dic\_pilot\_KEES\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9120b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9120b016\]
> JP (źródło tłumaczenia): 　デルタ小隊のエースパイロット・メッサーと激闘を繰り広げ、アル・シャハルでの戦いで撃墜されるも、一命を取り留める。 ⏎ 　戦いの中、プロトカルチャーの遺跡を使って銀河の掌握を目論んでいたロイドと道を違え、最終決戦ではデルタ小隊に加勢してロイドを討つが、共に爆発の中へ消えていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In a fierce battle with the Delta Flight ace Messer, he was shot down on Al Shahal, but was able to survive. ⏎  ⏎ In later battles, he would end up enemies with Roid, who sought to use the ruins of the Protoculture to control the galaxy. For the final battle, he aided the Delta Flight to fight Roid, and ultimately the two of them disappeared into the ashes of an explosion.

### dic\_pilot\_ROID\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b000\]
> JP (źródło tłumaczenia): 　ウィンダミア王国の宰相。 ⏎ 　空中騎士団の騎士団長も務めている他、プロトカルチャーの研究を専門とした学者としての一面も併せ持つ。 ⏎ 　ワルキューレに加入したフレイアのデビューライブと時を同じくして新統合政府に宣戦布告を行った。
> EN (odniesienie oficjalne, NIE polski): The prime minister of the Kingdom of Windermere. ⏎  ⏎ He also serves as the leader of the Aerial Knights, and is independently a researcher specializing in studies of the Protoculture.  ⏎  ⏎ He declared war on the New United Nations Government at the same time as Walküre were holding Freyja's debut concert.

### dic\_pilot\_ROID\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b001\]
> JP (źródło tłumaczenia): 　国王ハインツの「風の歌」で戦局を有利に運ぶが、その後、ワルキューレの美雲を操って「星の歌」とプロトカルチャーの遺したシステムによって全銀河を手中に収めようと画策する。 ⏎ 　しかし最終決戦では、理想を違えた空中騎士団のキースとデルタ小隊とワルキューレに野望を絶たれ、キースの手により討たれた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He used the Wind Song, sung by King Heinz, to great effect on the battlefield, but later would prove to be planning to manipulate Mikumo of Walküre into singing the Star Song, which together with a system left behind by the Protoculture would have put all the galaxy under his control.  ⏎  ⏎ However, his ambitions were broken by the combined efforts of Delta Flight and the Aerial Knights, who disagreed with his ideals, and he met his end at the hands of Keith.

### dic\_pilot\_BOAG\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b002\]
> JP (źródło tłumaczenia): 　空中騎士団の最年少パイロット。 ⏎ 　ウィンダミア王国の名門・コンファールト家の出身。 ⏎ 　かつての戦争で家族を失い、新統合政府に対して強い怒りと憎しみを剥き出しにする。
> EN (odniesienie oficjalne, NIE polski): The youngest member of the Aerial Knights.  ⏎  ⏎ Scion of the Con-Vaart family, a noted family in Windermere. He lost his family in war, resulting in him bearing a great deal of open hostility and hatred towards the New United Nations Government.

### dic\_pilot\_BOAG\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b003\]
> JP (źródło tłumaczenia): 　戦いの中、ワルキューレの歌に触れ、嫌悪しながらも説明のつかない感情に翻弄されていく。 ⏎ 　最終決戦ではロイドと決別したキースに従い、デルタ小隊と共闘した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the war, he was touched by the songs of Walküre, which disgusted him even as they toyed with his heart, instilling an emotion in him he could not describe. ⏎  ⏎ In the final battle he assisted Delta Flight under the orders of Keith, who perished together with Roid.

### dic\_pilot\_HELMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b004\]
> JP (źródło tłumaczenia): 　空中騎士団の最年長パイロット。３３歳。 ⏎ 　平均寿命が３０歳であるウィンダミア人の中でも年長者にあたり、顔から首元にかけて結晶化が進んでいる。 ⏎ 　騎士道精神を重んじる人物で、実力を認めた者には誠実な態度をとる。
> EN (odniesienie oficjalne, NIE polski): The eldest pilot amongst the Aerial Knights at the age of 33.  ⏎  ⏎ As Windermerians have an average age of 30, he is also one of the oldest living Windermerians, with much of his face and neck having crystallized. He deeply values chivalry, and never fails to be sincere with those who he feels have ability worthy of respect.

### dic\_pilot\_KASIM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b006\]
> JP (źródło tłumaczenia): 　大柄な身体を持つ空中騎士団のパイロット。 ⏎ 　故郷の実家はリンゴ農園を営んでおり、一人息子を持つ。
> EN (odniesienie oficjalne, NIE polski): A large man and a pilot of the Aerial Knights. ⏎  ⏎ His family runs an apple farm back at his hometown, and he has one son.

### dic\_pilot\_TEO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b008\]
> JP (źródło tłumaczenia): 　空中騎士団に所属する双子のパイロット。ザオの双子の兄。 ⏎ 　ウィンダミア王国でも有名な商家の出身で、左の頬にタトゥー、右側の髪に丸みがかったルンを持つ。 ⏎ 　普段は冷静かつ真面目な性格であるが、戦闘中は激しい一面も見せる。
> EN (odniesienie oficjalne, NIE polski): One of two twin pilots in the Aerial Knights, he is Xao's brother.  ⏎  ⏎ Born to a group of noted Windermerian merchants, he has a tattoo on the left side of his face and his rounded rune is on the right side of his hair. While generally calm and collected he can become much more fierce in combat.

### dic\_pilot\_ZAO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b00a\]
> JP (źródło tłumaczenia): 　空中騎士団に所属するパイロット。テオの双子の弟。 ⏎ 　ウィンダミア王国でも有名な商家の出身で、右の頬にタトゥー、左側の髪には尖った形状のルンを持つ。 ⏎ 　好戦的な性格をしている。
> EN (odniesienie oficjalne, NIE polski): A pilot with the Aerial Knights, and the twin brother of Theo. ⏎  ⏎ Born to a group of noted Windermerian merchants, he has a tattoo on the right side of his face and his pointy rune is on the left side of his hair. ⏎  ⏎ He has a belligerent attitude.

### dic\_pilot\_HINTS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b00c\]
> JP (źródło tłumaczenia): 　ウィンダミア王国の国王。 ⏎ 　１年前に先王グラミアが死去した事により、幼いながら即位した。 ⏎ 　白騎士キースは異母兄に当たる。 ⏎ 　「風の歌」の歌い手で、ヴァール化した人々を制御下に置く事が出来る。 ⏎ 　戦争の早期終結を望んでおり、宰相であるロイドの求めに応じて、身を削りながらも「風の歌」を歌い続ける。
> EN (odniesienie oficjalne, NIE polski): The king of Windermere.  ⏎  ⏎ With the death of the previous king one year ago, he was forced to take the throne at a young age, even for a Windermerian. The White Knight, Keith, is his half-brother. He is the singer of the Wind Song, which places people affected by the Vár Syndrome under his control.  ⏎  ⏎ Despite wishing for an early end to the war, he sacrifices his well-being to sing the Wind Song at the request of Roid, his prime minister.

### dic\_pilot\_HINTS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b00d\]
> JP (źródło tłumaczenia): 　アル・シャハルのプロトカルチャー遺跡を通じて、美雲やフレイアの歌と共鳴した事で結晶化が大きく進み、以降は病床に臥した。 ⏎ 　最終決戦ではロイドとキースの最期を感じ取り、彼ら亡きウィンダミア王国を治めていく決意を固め、戦争を終わらせた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After experiencing resonance with Mikumo and Freyja's songs through the Protoculture ruins on Al Shahal, his crystallization became drastically worse, leading to him being stuck in bed as an invalid. He felt the passing of Keith and Roid in the final battle, and resolved to rule Windermere in their absence, and thus ended the war.

### dic\_pilot\_MIKUMO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b00e\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」のエースボーカル。 ⏎ 　決め台詞は「歌は神秘」。 ⏎ 　年齢や経歴が全て伏せられているミステリアスな存在で、単独行動が多い。 ⏎ 　歌を歌う事に対する想いは人一倍強く、その歌声には高い生体フォールド波が含まれている。 ⏎ 　歌への真摯な姿勢は、ワルキューレの新メンバーであるフレイアに大きな影響を与える。
> EN (odniesienie oficjalne, NIE polski): The ace vocalist of the Tactical Sound Unit Walküre. Her catchphrase is "Music is mystery".  ⏎  ⏎ A mysterious person whose age and past are kept secret, she often does things by herself and possesses an air of aloofness. Her passion for singing is greater than most, however, and her voice contains Bio-Fold Waves. Her sincere attitude towards music leaves a strong impact on Walküre's new member, Freyja.

### dic\_pilot\_MIKUMO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b00f\]
> JP (źródło tłumaczenia): 　その正体は、プロトカルチャーの遺跡から回収された「星の歌い手」の細胞片から生まれたクローンである。 ⏎ 　ウィンダミア王国の宰相であるロイドに操られて「星の歌」を歌い、全銀河の生命の意識を統一させる道具として利用されそうになるが、ワルキューレの歌と仲間達の呼びかけによって自らを取り戻した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She would later be revealed to be a clone made from cellular remnants of the Singer of the Stars found in the Protoculture ruins. ⏎  ⏎ Roid, the prime minister of Windermere, forced her to sing the Star Song as little more than a tool in order to unite the entire galaxy into one lifeform, but the songs and calls of her dear friends and the Walküre allowed her to reassert control over herself.

### dic\_pilot\_KANAME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b010\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」のリーダー。 ⏎ 　決め台詞は「歌は生命（いのち）」。 ⏎ 　かつてはアイドルとしてソロデビューを果たしたが、人気が出ずに引退した経歴を持つ。 ⏎ 　その後、フォールドレセプターの数値が高い事が判明してワルキューレの創設メンバーとなる。 ⏎ 　ワルキューレに美雲が加入してからはエースの座を譲り、メンバーをまとめる役割に落ち着きながらも、美雲への対抗心も持ち合わせている。
> EN (odniesienie oficjalne, NIE polski): The leader of the Tactical Sound Unit Walküre. Her catchphrase is "Music is life".  ⏎  ⏎ Though she originally debuted as a solo idol, she failed to accumulate any popularity. Later, she would become one of the founding members of Walküre as it was discovered she was able to produce a major reaction with a Fold Receptor. ⏎  ⏎ After Mikumo joined, she yielded the star position to her, and so despite being a calm person who still often leads the group, she feels a sense of (friendly) rivalry towards Mikumo.

### dic\_pilot\_KANAME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b011\]
> JP (źródło tłumaczenia): 　プロトカルチャー遺跡をめぐる惑星アル・シャハルでの戦いにおいて、窮地に駆けつけたメッサーのヴァール化を止めるべく、自身のソロデビュー曲であった「ＡＸＩＡ～ダイスキでダイキライ～」を歌った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the battle over the Protoculture ruins at Al Shahal, she sang her solo debut song, "AXIA ~I love you, I hate you~" in an attempt to halt Messer's Vár Syndrome.

### dic\_pilot\_REINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b012\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」のメンバー。 ⏎ 　決め台詞は「歌は愛」。 ⏎ 　メンバーのマキナとは特に仲がよく、プライベートでも行動を共にする事が多い。 ⏎ 　ワルキューレに加入する以前は、星間複合企業体ケイオスのサイバー部門にてハッカーとして活動していたが、フォールドレセプターの値が高い事が判明してメンバーに選出された。 ⏎ 　ワルキューレの歌にウイルスを盛り込む等、ハッカーとしての腕前は健在。
> EN (odniesienie oficjalne, NIE polski): A member of the Tactical Sound Unit Walküre. Her catchphrase is "Music is love".  ⏎  ⏎ She is close with fellow member Makina, and the two of them often spend their off-work hours together as well. Prior to joining Walküre, she was employed as a hacker with the interstellar conglomerate Xaos's cyber-tech group, but was nominated as a member of Walküre when she proved to have high Fold Receptor scores. ⏎  ⏎ She nonetheless continues to act as a hacker, adding computer viruses to the songs sung by Walküre and such from time to time.

### dic\_pilot\_REINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b013\]
> JP (źródło tłumaczenia): 　最終決戦では合流したマキナや他のワルキューレのメンバーと共に美雲を救出し、デルタ小隊をサポートした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle she joined with Makina and the other members of Walküre to rescue Mikumo and support Delta Flight.

### dic\_pilot\_MAKINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9160b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b014\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」のメンバー。 ⏎ 　決め台詞は「歌は希望」。 ⏎ 　メンバーのレイナとは特に仲がよく、プライベートでも行動を共にする事が多い。 ⏎ 　オーディションに合格した事で加入し、ワルキューレの活動初期からカナメやレイナと活動を続けてきた。 ⏎ 　メカニックとしての一面もあり、高い整備技能を持つ。
> EN (odniesienie oficjalne, NIE polski): A member of the Tactical Sound Unit Walküre. Her catchphrase is "Music is hope".  ⏎  ⏎ She is close with fellow member Reina, and the two of them often spend their off-work hours together as well. She joined Walküre through an audition, contributing to their efforts since the earliest days with Kaname and Reina. ⏎  ⏎ Also a capable mechanic, she is able to provide excellent care to machines.

### dic\_pilot\_MAKINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9160b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9160b015\]
> JP (źródło tłumaczenia): 　惑星アル・シャハルのプロトカルチャー遺跡での戦いにて、レイナをかばって負傷し、捕虜としてウィンダミア王国の治療室に隔離される。 ⏎ 　最終決戦では仲間に救出され、他のワルキューレのメンバーと共にデルタ小隊をサポートした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the battle over Al Shahal's Protoculture ruins, she was injured protecting Reina, and captured with the others, isolated in one of Windermere's medical wards. ⏎  ⏎ After being rescued by her comrades in the final battle, she rejoined the other members of Walküre to support Delta Flight.

### dic\_pilot\_FREIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b000\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」の新メンバー。 ⏎ 　決め台詞は「歌は元気」。 ⏎ 　ワルキューレに憧れ、オーディションを受けるために故郷のウィンダミア王国から惑星ラグナに密航してきた。 ⏎ 　明るく、天真爛漫な性格。 ⏎ 　フォールドレセプターの持ち主であり、高い数値を出した事からオーディションに合格し、ワルキューレのメンバーに選出された。 ⏎ 　言葉には若干の訛りがあり、「ごりごり」が口癖。 ⏎ 　密航の際に知り合ったデルタ小隊のハヤテとは、互いに励まし合う関係が続く。
> EN (odniesienie oficjalne, NIE polski): The newest member of the Tactical Sound Unit Walküre. Her catchphrase is "Music is energy!"  ⏎  ⏎ She aspired to join Walküre and stowed away on a ship from her native homeland of Windermere to the planet Ragna in order to audition.  ⏎  ⏎ She has a bright, innocent personality. She possesses a Fold Receptor, and passed her audition with high scores, earning her a spot in Walküre. She has a mild accent, and often speaks of things as crunchy. She and Hayate, the Delta Flight pilot she met while a stowaway, both support each other in their aspirations.

### dic\_pilot\_FREIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b001\]
> JP (źródło tłumaczenia): 　惑星アル・シャハルでの戦いで右手から結晶化が進むが、最終決戦では生命を懸けて歌い、ハヤテのフォールドレセプターと共鳴する事でその力を大きく引き出した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though her right hand suffered some crystallization in the battle at Al Shahal, she sung her heart out in the final battle, resonating with Hayate's pendant Fold Receptor and drawing out its power.

### dic\_pilot\_LLSH\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b002\]
> JP (źródło tłumaczenia): 　かつて悪逆皇帝として、世界征服を果たし、世界中の憎しみを一身に集めた少年。 ⏎ 　しかし、それは力による憎しみの連鎖が続く世界を壊し、武器を持たないすべての人が話し合いによって紡がれる世界を創るための所業だった。 ⏎ 　世界の三分の一を支配する超大国、神聖ブリタニア帝国の第１１皇子として生まれたルルーシュだったが、母を暗殺され、最愛の妹ナナリーが不具になったことで、人質として日本へと送られる。そこで生涯の親友であり宿敵となる枢木スザクと出会い、ささやかな安寧の日々を送るが、父であるシャルル皇帝が行った日本への武力侵攻でその日々さえ失ってしまう。 ⏎ 　戦場となった日本でルルーシュは、皇族の証であるブリタニア姓を捨てて母の姓を名乗り、ブリタニアの植民地と化した日本で妹のナナリーと共に身を潜めて暮らしていた。 ⏎ 　祖国ブリタニアへの復讐を誓うルルーシュは、偶然出会った少女Ｃ．Ｃ．から「絶対遵守の力」のギアスを得、仮面の男ゼロとしてブリタニアへの反逆を開始する。その結果、ルルーシュは自ら作り出した正義の象徴たるゼロに、憎しみのすべてを一身に受けた自分が殺されることこそが、妹ナナリーが安心して暮らせる世界を創り出すという考えに至る。そして、スザクにゼロを託し、自らが殺されることで、平和な世界を創り出すゼロ・レクイエムを完遂した。 ⏎ 　全ての人々の憎しみを一身に受けた悪逆皇帝ルルーシュが正義の象徴たるゼロに殺されることで憎しみの連鎖を断ち切ったゼロ・レクイエム。ルルーシュとスザクという２人の少年によって行われたこの計画により、世界はようやく平和な時代を手に入れた。 ⏎ 　ゼロ・レクイエムから一年、人類史上において戦争もテロもない「奇蹟の明日」と呼ばれる時代、死んだはずのルルーシュの身体は、彼の戦いの中で引き継がれてしまった「コード」によって蘇生されてしまう。正常なコードの引継ぎが行われていたならＣ．Ｃ．と同様の不老不死になるはずだったが、Ｃの世界が異常を引き起こしたことによって、ルルーシュの魂はＣの世界に取り残されたままとなってしまった。 ⏎ 　Ｃ．Ｃ．は、そんなルルーシュの心を取り戻すために、世界各地の遺跡を巡る旅に出た。
> EN (odniesienie oficjalne, NIE polski): His true name is Lelouch vi Britannia.  ⏎  ⏎ The man who dragged the world into the depths of chaos as the Emperor of the Holy Britannian Empire, eventually slain by the leader of the Black Knights, Zero, and believed dead by the whole world.  ⏎  ⏎ Formerly a high school-level student at the privately held Ashford Academy, his true identity was the eleventh prince of the Holy Britannian Empire, seventeenth in line for the Imperial throne, Lelouch vi Britannia.  ⏎  ⏎ During the Shinjuku Incident, Lelouch encountered C.C., and in return for promising to grant her wish, he gained a Geass with the absolute power to command. He would use this power in a rebellion against the world, seeking to create a safe world for his sister, Nunnally, where she could live happily and in peace.  ⏎  ⏎ Possessing both a brilliant mind and an astounding eye for strategy, along with the new power of his Geass, Lelouch was able to absorb the various resistance groups in Area 11 (Britannian-occupied Japan) into one group, forming the Black Knights and taking the role of their leader, "Zero". From there he slowly built up his forces until he was able to fight on an equal footing with the Britannian forces.  ⏎  ⏎ However, in the decisive battle for the liberation of Japan, the Black Rebellion, he lost Nunnally, his entire motive for fighting, to an abduction, and abandoned the battlefield. Searching for Nunnally, he would make his way to Kamine Island, where he faced his close friend, Suzaku. This ended in the total rejection of his existence, with his identity fully revealed, and he was dragged before the Emperor of Britannia.  ⏎  ⏎ There he learned his father, Charles, was also a Geass user, and by that Geass his memories would be overwritten. He was returned to a time before he was Zero, and implanted with memories of being the scion of lower nobility.  ⏎  ⏎ This peace would last but a year, before Kallen and C.C.'s return would bring it to an end.  ⏎  ⏎ Lelouch regained his memories courtesy of C.C. and would return to being Zero. Eventually, through multiple schemes and strategies, he would form a unified alliance, the United Federation of Nations, to oppose Britannia.  ⏎  ⏎ During this battle, however, Lelouch would lose C.C. (who in turn had lost her memories and was no longer the previous C.C.) and Nunnally, ultimately further losing his position with the Black Knights due to his brother Schneizel's own plot, and then during his escape lost Rolo, the assassin-turned-friend by his side, as well.  ⏎  ⏎ With nothing left to lose, Lelouch charged into C's World, believing he would never return, and faced off against his father...and his deceased mother. His parents explained to him their plan, to unify all human consciousness, which he rejected in totality. Together with C.C., who had regained her memories, he erased his father and mother from existence entirely.  ⏎  ⏎ Having claimed victory over Schneizel and the Black Knights, Lelouch held the entire world in his hand, but was finally slain by Suzaku, in the guise of Zero.  ⏎  ⏎ However, this was all a plot by Suzaku, Lelouch, and their co-conspirators, who wanted nothing more than to build a new future. This plot, which would be known as the Zero Requiem, concluded with Lelouch's death, leading the world to a new age.  ⏎  ⏎ Lelouch's corpse would be smuggled out in secret, and reconstructed by C.C. on her own initiative. She gambled on Lelouch having inherited the Code from Charles Zi Britannia, making him functionally immortal. However, C's World, the source of power for the Code, had become unstable when Lelouch killed the collective unconsciousness. As a result, though his body was in fact still alive, his mind (including his will and memories) did not return, making him, in C.C.'s own words, a void inside Lelouch's body, the last traces of who he once was.

### dic\_pilot\_LLSH\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b003\]
> JP (źródło tłumaczenia): 　いくつもの遺跡を巡るＣ．Ｃ．と心の戻らないルルーシュは、一縷の望みをもって、遺跡を祀るジルクスタン王国へと入り、残されていたアラムの門と呼ばれる遺跡によって心を取り戻したルルーシュは復活を果たす。 ⏎ 　復活したルルーシュは、ジルクスタン王国の聖神官シャムナの企てにより囚われたナナリーを救い出すため、一時的にゼロとして起つ。同じ成り損ないであるシャムナのギアスに苦戦するも、スザクやカレンたち仲間の力を借りてシャムナを降し、ナナリーを救い出すことに成功する。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After C.C.'s attempt to contact C's World through Adam's Gate in the Kingdom of Zilkhstan, his mind fully revived, and he returned to the world as Zero once again.  ⏎  ⏎ Defeating the priestess Shamna of the Kingdom of Zilkhstan, who sought to use Nunnally, he left her ambitions in shambles and rescued Nunnally from her clutches.  ⏎  ⏎ Henceforth, he renamed himself L.L., and set forth on a journey with C.C. to test the determination of those who would possess the Geass.

### dic\_pilot\_ZERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b004\]
> JP (źródło tłumaczenia): 　復活したルルーシュが扮する新たなゼロ。 ⏎ 　死んだ人間であり、存在自体が不確かな人間が世界に関与すべきではないというルルーシュ自身の考えのもと、ルルーシュは一時的にゼロへと戻った。そのため、事件後はスザクにその役目を戻す。
> EN (odniesienie oficjalne, NIE polski): A new Zero disguise for the revived Lelouch. ⏎  ⏎ Because he was a dead man, and was unsure if he even truly "existed" once more, Lelouch believed it was better if he had as little effect on the world as possible. Therefore, he took up the mantle of Zero again only temporarily, and afterwards passed it back to Suzaku.

### dic\_pilot\_CC\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b006\]
> JP (źródło tłumaczenia): 　不老不死の肉体とギアスを与えることが出来る「コード」を持つ少女。 ⏎ 　かつて、死を得るためにルルーシュにギアスを与え、コードを引き継がせるために行動をともにしていたが、明日を得ようともがくルルーシュの姿を見て、心情を変化させる。共犯者としてルルーシュと共に歩んだ結果、ゼロ・レクイエムでルルーシュの死を見届けた。 ⏎ 　シャルルを介してＶ．Ｖ．のコードを継承した後もギアスを使えていたことから、ルルーシュがコード保持者となることは失敗したと思われていたが、ゼロ・レクイエム後に肉体が蘇生してしまう。しかし、身体は元に戻っても心が戻らず幼児のようになったルルーシュ。その心がＣの世界に閉じ込められていると推測し、Ｃの世界とアクセスできる遺跡を求めて旅を開始した。最終的にアラムの門があるジルクスタン王国へと辿り着く。
> EN (odniesienie oficjalne, NIE polski): A girl with the Code, the power that grants the Geass and also gives its possessor an immortal body. In her quest for death, she gave Lelouch his Geass and followed him in hopes that she could pass her Code on to him. However, she had a change of heart as she watched Lelouch fight for a better future.  ⏎  ⏎ As his accomplice, she bore witness to Lelouch' death as part of the Zero Requiem. Because Lelouch retained his Geass power after taking the Code of Charles' backer, V.V., she assumed he couldn't bear a Code, an assumption proven false by his physical resurrection after the Zero Requiem.  ⏎  ⏎ However, only his body had resurrected, leaving him in a childlike state. Under the theory that his mind was trapped in the World of C, she took him on a journey to ruins that could allow them to access it. This journey finally brought them to Adam's Gate in the Kingdom of Zilkhstan.

### dic\_pilot\_CC\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b007\]
> JP (źródło tłumaczenia): 　そこでルルーシュの復活に成功すると、ナナリーを救出するために再びルルーシュと共に戦う。 ⏎ 　ジルクスタン王国聖神官シャムナの持つギアス「無限新生」の前に絶望したルルーシュを叱咤し、その心を奮い立たせ、救出成功へと導いた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ There, she finally succeeded in truly reviving Lelouch, and once again took Lelouch's side as he fought to rescue Nunnally. ⏎  ⏎ When Lelouch had given up all hope in the face of the Zilkhstani priestess Shamna's Geass of endless rebirth, her passionate plea revived his spirit and made the rescue a success.

### dic\_pilot\_SUZAK\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b008\]
> JP (źródło tłumaczenia): 　ルルーシュの親友であり、最大の敵。 ⏎ 　ルルーシュとは幼少期に出会って以来親友となったが、神聖ブリタニア帝国が日本に侵攻した際に生き別れとなってしまう。 ⏎ 　戦争を終わらせようと日本最後の首相であった父ゲンブを殺害したことから、その罪に悩まされており、「間違った方法で手に入れた結果に意味はない」という信念を持つようになる。そのため、ブリタニアを内部から変えようとブリタニア軍に入隊。そこでルルーシュと再会する。しかし、お互いに素性を明かさないまま、ゼロとなったルルーシュと幾度も対峙し、その結果、最愛の女性であるユーフェミアを失ってしまう。ユーフェミアの死により、結果を追い求めることになったスザクは、ルルーシュをシャルル皇帝に差し出すことで帝国最強の騎士ナイトオブラウンズにまで上りつめる。しかし、その行動の結果、大量破壊兵器フレイヤを使用して多くの人命を奪うことになり、その罪を贖うためにルルーシュとゼロ・レクイエムを決行する。 ⏎ 　ゼロ・レクイエムによりゼロという英雄の仮面を被り続けることになったスザクは、自らの人生を捨ててゼロとして世界の平和のために従事する。 ⏎ 　難民キャンプへの視察に向かったナナリーの護衛を務めるが、シャリオの罠にはまり、ナナリーとともにジルクスタン王国に囚われてしまう。
> EN (odniesienie oficjalne, NIE polski): Lelouch's best friend and worst enemy. ⏎  ⏎ He and Lelouch were close friends when they were children, but their lives went in drastically different directions when the Holy Britannian Empire invaded Japan. ⏎  ⏎ He assassinated his father, Genbu, the last prime minister of Japan, in an effort to put an end to the war. Haunted by his own terrible misdeed, he convinced himself that the ends never justifies the means, and this belief led him to join the Britannian military in hopes of changing Britannia from the inside. ⏎  ⏎ He eventually came back into contact with Lelouch, with neither of them revealing their true identity to the other. He fought Lelouch—masquerading as Zero—several times, until ultimately, Lelouch's struggles took the life of Euphemia, Lelouch's older sister and the love of Suzaku's life. Euphemia's death drove Suzaku to once again prioritize the ends over the means, and by capturing Lelouch for Emperor Charles, he secured himself a spot within the Knights of the Round, the greatest knights of Britannia. ⏎  ⏎ His actions led to the use of the F.L.E.I.J.A., a weapon of mass destruction, resulting in innumerable deaths. To atone for his sins, he resolved to work with Lelouch to carry out the Zero Requiem. ⏎  ⏎ In the Zero Requiem, Suzaku donned the mask of a hero and took on the identity of Zero. He gave everything up in order to live as Zero and serve the cause of world peace. ⏎  ⏎ He was in charge of security for Nunnally when she visited a refugee camp, but fell for a trap set by Shalio, leading to both him and Nunnally being taken prisoner by Zilkhstan.

### dic\_pilot\_SUZAK\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b009\]
> JP (źródło tłumaczenia): 　復活したルルーシュに救出され、ナナリー救出のために再び呪われた機体であるランスロットに搭乗する。 ⏎ 　最強に固執するジルクスタン国王シャリオのナギド・シュ・メインと戦い、ランスロットsiNでこれを降した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When rescued by Lelouch, he first assumed that Lelouch's resurrection had been planned from the start, not understanding the circumstances under which Lelouch had returned.  ⏎  ⏎ He eventually learned of the full circumstances, and returned the title of Zero to Lelouch until Nunnally was rescued, joining the rescue operation with the Lancelot siN and defeating Shalio.

### dic\_pilot\_SUZAK\_X\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b00a\]
> JP (źródło tłumaczenia): 　黒の騎士団首席顧問。 ⏎ 　黒く塗られたナイトメアフレームを駆り、テロや紛争を撲滅するために戦う。 ⏎ 　その正体は、ルルーシュの願いを受けたスザク。
> EN (odniesienie oficjalne, NIE polski): Chief advisor to the Order of the Black Knights. ⏎  ⏎ He pilots a black Knightmare Frame and fights to eradicate terrorism and strife. His true identity is Suzaku Kururugi, having taken on Lelouch's burdens.

### dic\_pilot\_ROYD\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b00c\]
> JP (źródło tłumaczenia): 　ゼロ・レクイエムの際、長らく付き合ってきたスザクに協力し、ナイトオブゼロとなったスザクの乗機となるランスロット・アルビオンを建造した。 ⏎ 　ゼロ・レクイエム後はルルーシュに協力していたことから、超合集国での要職に就けず、見かねたカノンの取り計らいで民間企業に勤めるも、人間性の問題から日に日に降格され、まともなナイトメアフレームの研究開発が出来ずに嘆いている。 ⏎ 　ゼロであるスザクが誘拐されたことから、カレンと咲世子とともにジルクスタン王国潜入する。
> EN (odniesienie oficjalne, NIE polski): During the Zero Requiem, he continued working with Suzaku, building the Lancelot Albion for his new role as the Knight of Zero. Afterwards, he was unable to find work with the United Federation of Nations due to his cooperation with Lelouch.  ⏎  ⏎ With Kanon's assistance, he found work in the private sector. However, his employers are dissatisfied with his personality, and he himself dearly misses developing cutting-edge Knightmare Frames. He is later abducted by Suzaku as Zero and assists in the infiltration of Zilkhstan with Kallen and Sayoko.

### dic\_pilot\_ROYD\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b00d\]
> JP (źródło tłumaczenia): 　そのまま、カレン達と共にルルーシュの復活とナナリー救出作戦に協力した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He remained with the group through the entire affair, assisting with both Lelouch's resurrection and the Nunnally rescue operation.

### dic\_pilot\_CESIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b00e\]
> JP (źródło tłumaczenia): 　ランスロットの元開発メンバー。 ⏎ 　神聖ブリタニア帝国の崩壊前は特別派遣嚮導技術部、キャメロットなどに在籍し、上司であるロイドの補佐役を務めていた。 ⏎ 　ナナリーが拉致された事を知り、ロイドやニーナと共に救出作戦に参加する。
> EN (odniesienie oficjalne, NIE polski): A former member of the Lancelot development team. ⏎  ⏎ She worked for the Advanced Special Envoy Engineering Corps, Camelot, as Lloyd Asplund's assistant, in addition to other roles prior to the fall of the Holy Britannian Empire. ⏎  ⏎ She later joined Lloyd and Nina to participate in the operation to rescue Nunnally upon the discovery of her kidnapping.

### dic\_pilot\_CESIL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b00f\]
> JP (źródło tłumaczenia): 　作戦行動中、銃撃を受けて重傷を負ったものの、一命を取り留めた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Was shot and gravely injured during the operation, but survived.

### dic\_pilot\_NEENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b010\]
> JP (źródło tłumaczenia): 　セシルと行動を共にする研究者。 ⏎ 　かつては大量破壊兵器フレイヤを開発するも、それによる被害を目の当たりにした事で、以後はフレイヤの平和利用を模索している。 ⏎ 　ナナリー救出作戦のため、ルルーシュ達に合流した。
> EN (odniesienie oficjalne, NIE polski): Researcher who works with Cecile. ⏎  ⏎ Has been looking for peaceful ways to use the technology behind the weapons of mass destruction known as the F.L.E.I.J.A. after witnessing the destruction their use caused. Met up with Lelouch's group to assist them in the operation to rescue Nunnally.

### dic\_pilot\_NEENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b011\]
> JP (źródło tłumaczenia): 　作戦中、ジルクスタン王国の暗殺部隊の隊長・クジャパットにより、ロイド達と共に窮地に追いやられるも、機転を利かせて敵の一網打尽に成功する。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Lloyd, Cecile, and Nina found themselves in grave danger during the operation at the hands of Qujappat, the leader of the Kingdom of Zilkhstan's assassination team, but managed to make it through thanks to Nina's quick wit.

### dic\_pilot\_SHUNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b012\]
> JP (źródło tłumaczenia): 　超合集国最高評議会の首席補佐官。 ⏎ 　かつては神聖ブリタニア帝国の第２皇子であり、ブリタニア皇帝となったルルーシュと世界の覇権を賭けて戦うも、敗北した。 ⏎ 　その時にルルーシュにかけられた「ゼロに仕えよ」というギアスに現在も忠実に従っている。 ⏎ 　ゼロとナナリーがさらわれた事を知り、ロイド達をジルクスタン王国へと派遣した。
> EN (odniesienie oficjalne, NIE polski): Secretary-General of the United Federation of Nations Supreme Council. ⏎  ⏎ He is the former second prince of the Holy Britannian Empire. After Lelouch became emperor of Britannia, the two fought in a battle with dominion of the world on the line. ⏎  ⏎ Upon his defeat, Lelouch commanded him with his Geass to "serve Zero", a command he still loyally follows to this day. ⏎  ⏎ He dispatched Lloyd's team to Zilkhstan upon learning of Zero's and Nunnally's kidnapping.

### dic\_pilot\_SHUNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b013\]
> JP (źródło tłumaczenia): 　ナナリー救出作戦では、紅蓮特式とランスロットsiNをロイド達の下へ手配した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Provided the Guren Type Special and Lancelot siN to Lloyd's team for the operation to rescue Nunnally.

### dic\_pilot\_NNRY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:91a0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b014\]
> JP (źródło tłumaczenia): 　ルルーシュの同腹の妹。 ⏎ 　神聖ブリタニア帝国を乗っ取るようにして皇帝となった兄ルルーシュと敵対したが、敗北。反逆者として処刑されようとしたパレードで、ゼロに兄が討たれる様を目にする。そこで初めてルルーシュの真意を理解したナナリーは、平和になった世界で人々のために従事することを誓う。 ⏎ 　平和になった世界で世界人道支援機関の名誉顧問として難民キャンプを訪れた際、謎の部隊を装ったシャリオらジルクスタンに拉致される。
> EN (odniesienie oficjalne, NIE polski): Lelouch's full-blooded sister. ⏎  ⏎ She opposed (in vain) her brother's takeover of the Holy Britannian Empire. During a parade in which she was to be executed as a traitor, she saw him killed by Zero before her eyes. Realizing Lelouch's plan in that final moment, she swore to lead the people in the new, peaceful world.  ⏎  ⏎ After the war, on a visit to a refugee camp as an honorary advisor to the World Humanism Agency, she was abducted by an unknown force led by Shalio and taken to Zilkhstan.

### dic\_pilot\_NNRY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:91a0b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:91a0b015\]
> JP (źródło tłumaczenia): 　聖神官シャムナにＣの世界に自由にアクセスするための鍵として利用されそうになったが、ルルーシュらによって救出された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Priestess Shamna attempted to use her as a key to freely access C's World, but she was rescued by Lelouch.

### dic\_pilot\_CONERIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b000\]
> JP (źródło tłumaczenia): 　元神聖ブリタニア帝国の第２皇女。 ⏎ 　ルルーシュとナナリーにとっては腹違いの姉に当たる。 ⏎ 　皇帝ルルーシュを忠臣ギルフォードらと共に暗殺しようとしたが、ゼロ・レクイエムによってゼロがルルーシュを討つという結末を見届ける事になった。 ⏎ 　現在は超合集国の防衛を担う黒の騎士団の陸軍第十一旅団長であり、ナナリー救出作戦に参加する部隊を率いた。
> EN (odniesienie oficjalne, NIE polski): The former second princess of the former Holy Britannian Empire.  ⏎  ⏎ She served briefly as the governor of Area 11, but would relinquish this position after the Black Rebellion. ⏎  ⏎ After learning the truth about the Geass, she attempted to assassinate Emperor Lelouch after his victory over Schneizel but ultimately ended up an observer to the conclusion of the Zero Requiem. ⏎  ⏎ She ended up leading the eleventh mobile ground unit of the Order of the Black Knights, the defenders of the United Federation of Nations, and commanded a unit in the Nunnally rescue operation.

### dic\_pilot\_CONERIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b001\]
> JP (źródło tłumaczenia): 　復活したルルーシュと再会した際、最愛の妹ユーフェミアを殺したことのわだかまりがあったが、正体を晒して懇願するルルーシュにけじめをつける。そして、自らの妹でもあるナナリー救出のため、クインローゼスで部隊を率い、褐色の城壁と畏れられるボルボナ・フォーグナーと戦った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Upon being reunited with Lelouch, she initially balked at helping him, the murderer of her beloved sister Euphemia. ⏎  ⏎ However, when Lelouch unmasked himself and made a heartfelt plea for her aid, she put her grudges to rest. Together they rescued Nunnally, their remaining sister, by leading a Quinn Roses squad and battling Bolvona Forgnar, the so-called "Brown Bulwark".

### dic\_pilot\_ARNYA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b002\]
> JP (źródło tłumaczenia): 　神聖ブリタニア帝国最強の騎士、ナイトオブラウンズの一人だった少女。 ⏎ 　ルルーシュの母マリアンヌの心を渡るギアスによって、マリアンヌの意識を宿しており、マリアンヌの意識が表層化した際の影響による記憶障害に苦しんでいた。 ⏎ 　敵対していたジェレミアのギアス・キャンセラーによってギアスからは解放されており、ゼロ・レクイエム後はジェレミアと共にオレンジ農園を経営している。
> EN (odniesienie oficjalne, NIE polski): A former Knight of the Round, one of the strongest knights in Britannia. ⏎  ⏎ Lelouch's mother, Marianne, used her Geass of possession to hide her consciousness in Anya. She suffered amnesia whenever Marianne's mind took over. ⏎  ⏎ She was released from her Geass by Jeremiah's Geass Canceler. After the Zero Requiem, she joined him at his orange orchard.

### dic\_pilot\_ARNYA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b003\]
> JP (źródło tłumaczenia): 　ジェレミアと共にジルクスタン王国でのナナリー救出作戦にも参加し、モルドレッド・ビルドアップに搭乗した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She participated in the Nunnally rescue operation against the Kingdom of Zilkhstan, piloting a Mordred Buildup.

### dic\_pilot\_JEREM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b004\]
> JP (źródło tłumaczenia): 　クロヴィス統治下のエリア１１では、ブリタニア軍の中でもブリタニア人至上主義を掲げる「純血派」を率いていたが、クロヴィス暗殺の嫌疑をかけられたスザクの身柄をゼロに奪われた際、ギアスによってスキャンダルを起こさせられて失脚した。 ⏎ 　その後、紅蓮弐式との戦闘で瀕死の重傷を負ったことにより、ギアス能力の実験体とされ、その結果、偶然にギアスを無効化する「ギアス・キャンセラー」を得た。その能力をもって一時はＶ．Ｖ．の刺客として動くも、敬愛していたルルーシュの母マリアンヌを暗殺から守れなかったという後悔から、その遺児であるルルーシュに忠誠を誓って臣下となる。 ⏎ 　ゼロ・レクイエムの真相を知っている者の一人。平和になった世界では、アーニャとともにオレンジ農園を営んでいる。
> EN (odniesienie oficjalne, NIE polski): The former leader of the Purebloods, a faction believing in Britannian supremacy among the Britannian military, under Clovis' administration. He was disgraced when Zero not only foiled their attempts to frame Suzaku for the assassination of Clovis, but used his Geass to destroy his reputation.  ⏎  ⏎ Later on, after being nearly killed in battle with the Guren Mk-II, he became the subject of Geass experimentation that gave him the power to neutralize all Geasses, called the Geass Canceler. After this, he served as V.V.'s assassin for a time, but then swore loyalty to Lelouch, as his first and greatest loyalty was to Lelouch's mother...and his failure to prevent her assassination, and the essential exile of her children, had haunted him.  ⏎  ⏎ One of the few who knows the truth of the Zero Requiem. With the coming of peace, he retired to an orange orchard he runs with Anya.

### dic\_pilot\_JEREM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b005\]
> JP (źródło tłumaczenia): 　ジルクスタン王国でのナナリー救出作戦にも参加。ルルーシュの指揮の下、サザーランド・ローヤルに搭乗して戦った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He participated in the Nunnally rescue operation against the Kingdom of Zilkhstan, piloting a Sutherland Royal.

### dic\_pilot\_KAREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b006\]
> JP (źródło tłumaczenia): 　黒の騎士団のエースパイロット。 ⏎ 　ブリタニアと日本のハーフだが、兄ナオトの意志を継いで反ブリタニア勢力として活動していた。その戦いの中で、ゼロとしてのルルーシュと出会い、日本解放を目指して紅蓮弐式を駆って戦い続けることになる。 ⏎ 　第一次トウキョウ決戦とも呼ばれるブラック・リベリオン時に、ゼロの正体がルルーシュであることを知ってしまうが、ナナリーのために戦う姿を信じ、紅蓮可翔式、紅蓮聖天八極式のパイロットとして、その力となった。 ⏎ 　しかし、ゼロ・レクイエムでは、ルルーシュの心中を知ることが出来ずに敵対し、そのまま彼の死を見届ける。ゼロ・レクイエム後、平和になった世界で戦いから遠ざかるために黒の騎士団の予備役となって大学生活を送っていたが、ゼロとナナリー誘拐の知らせを聞いて、咲世子、ロイドと共にジルクスタン王国へと潜入する。
> EN (odniesienie oficjalne, NIE polski): The Order of the Black Knights' ace pilot. ⏎  ⏎ She's half-Britannian and half-Japanese, but shares her brother Naoto's intense hatred of Britannia and is central to the rebel forces arrayed against them. These battles lead her to meet Lelouch, in his guise as Zero, and fight in the Guren Type-2. ⏎  ⏎ During the Black Rebellion, also known as the First Battle of Tokyo, she discovered Zero's true identity. However, he won her faith by standing to fight for Nunnally, and she continued to fight for him in the Guren Flight-Type and the Guren S.E.I.T.E.N. Eight Elements. ⏎  ⏎ However, she never learned Lelouch's intentions during the Zero Requiem until she was forced to watch him die. Afterward, she distanced herself from fighting in the peaceful new world and attended college. When she learned of Zero's and Nunnally's kidnapping, she went with Sayoko and Lloyd to Zilkhstan.

### dic\_pilot\_KAREN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b007\]
> JP (źródło tłumaczenia): 　その後、Ｃ．Ｃ．と再会し、ルルーシュ復活に協力。 ⏎ 　そのままナナリー救出作戦に参加し、紅蓮特式でビトゥルのバタララン・ドゥと死闘を演じた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She there encountered C.C. and, recovering from the shock of seeing Lelouch "alive", chose to help C.C. in her attempt to resurrect Lelouch, eventually piloting the Guren Type Special and fighting Bitool's Batalalan Du after his full resurrection in the operation to rescue Nunnally.

### dic\_pilot\_OUGI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b008\]
> JP (źródło tłumaczenia): 　カレンの兄でもある親友のナオトの意志を引き継いで反ブリタニア勢力のリーダーを務めていたが、自分の能力不足に悩んでいた。そこに現れたゼロのカリスマに惹かれ、ゼロを信じ続けた。しかし、戦いの中で出会った記憶喪失のヴィレッタと恋に落ち、彼女からギアスの力を知ってしまう。その不可思議な力の存在に、ゼロの正体だと暴露されたルルーシュを信じる事が出来なくなり、黒の騎士団から追放した。 ⏎ 　ゼロ・レクイエム時も黒の騎士団の副司令として対峙した。 ⏎ 　ゼロ・レクイエム後は、合衆国日本の初代総理大臣に就任し、ヴィレッタと結婚して息子のナオトを授かるなど、幸せな日常を送る。
> EN (odniesienie oficjalne, NIE polski): The former leader of the counter-Britannian resistance, following the last wishes of his friend and Kallen's brother Naoto. He was plagued with doubts about his own leadership and placed his faith in Zero after he appeared. During the war, he fell in love with an amnesiac, Viletta, and learned about the Geass as a result.  ⏎  ⏎ Between fear of such an unknown power and the revelation that Zero was really Lelouch, he lost his faith and exiled Lelouch from the Order of the Black Knights.  ⏎  ⏎ During the Zero Requiem, he continued serving as the Black Knights' second in command. After the Zero Requiem, he lived a happy life, serving as the new United States of Japan's Prime Minister, marrying Viletta, and fathering a son, Naoto.

### dic\_pilot\_OUGI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b009\]
> JP (źródło tłumaczenia): 　就任半年ほどで総理大臣の任を辞していたところ、ゼロとナナリー誘拐の知らせを受けて、玉城と共にゼロとナナリー救出作戦に参加する。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He participated in the Nunnally rescue operation with Tamaki, and upon encountering Zero, attempted to apologize for his previous rejection by attempting suicide. Zero ultimately stopped his drastic behavior.

### dic\_pilot\_TAMAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b00a\]
> JP (źródło tłumaczenia): 　Ｃａｆｅ　ＺＥＲＯの経営者。 ⏎ 　かつては黒の騎士団の創設時からのメンバーだった。 ⏎ 　ゼロの親友を自称しており、その存在を信頼していたため、黒の騎士団とゼロが決別した時は本気で嘆き悲しんだ。 ⏎ 　ゼロ・レクイエム後は新しい日本政府には参加せず、ゼロとコラボしたというカフェバーを経営し、二号店を開くほどの商才を発揮している。
> EN (odniesienie oficjalne, NIE polski): The manager of Cafe ZERO. ⏎  ⏎ One of the founding members of the Order of the Black Knights. ⏎  ⏎ As Zero's most fervent believer and self-styled confidant, he was devastated when Zero left the Black Knights. After the Zero Requiem, rather than serving in the Japanese government, he started a cafe-bar, which saw enough success to have opened a second location.

### dic\_pilot\_TAMAKI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b00b\]
> JP (źródło tłumaczenia): 　扇と共にナナリー救出作戦に参加し、図らずも敵の通信を利用することをルルーシュに想起させる活躍を見せた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He joined Ohgi on the Nunnally rescue operation, and notably took control of the enemy communications.

### dic\_pilot\_RACSHTA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b00c\]
> JP (źródło tłumaczenia): 　かつての黒の騎士団の技術顧問。現在は、超合集国の世界科学委員会会長、国際保険機関相談役、超合集国大学名誉学長、超合集国ボランティア事務局顧問、世界公共安全調査庁非常勤委員、合衆国インド厚生大臣相談役など多岐にわたる。 ⏎ 　世界中の天才児を集めた私設機関「パール・パーティー」の設立者でもある。 ⏎ 　ナナリー救出作戦では、そのパール・パーティーの一員であるシャンティがフレームコートの手配を行った。
> EN (odniesienie oficjalne, NIE polski): The former technical advisor to the Order of the Black Knights. Currently juggling a multitude of positions, including chair of the UFN's World Science Committee, consultant to the WHO, honorary dean of the UFN University, volunteer administrative advisor to the UFN, part-time agent to the World Public Security Intelligence Agency, and advisor to the United Indian Nation's Minister of Health and Welfare. ⏎  ⏎ She also founded the Pearl Party, a private organization that assembles gifted youths from the world over. ⏎  ⏎ Shanti, a member of the Pearl Party, is the one who provided the Frame Coats for the operation to rescue Nunnally.

### dic\_pilot\_SAYOKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b00e\]
> JP (źródło tłumaczenia): 　篠崎流三十七代目当主。 ⏎ 　アッシュフォード家のメイドとして、ルルーシュとナナリーの身の回りの世話をしていたが、後に黒の騎士団に参加する。ゼロの正体がルルーシュだと明かされた後は、ルルーシュの隠密として仕え、ゼロ・レクイエムの際も協力し、最後まで指示に従った。 ⏎ 　ゼロ・レクイエム後は、裏から世界の紛争解決に協力していたが、ナナリーがさらわれたという報せを聞き、カレン、ロイドと共にジルクスタン王国に潜入した。
> EN (odniesienie oficjalne, NIE polski): 37th master of the Shinozaki School, and a member of the Order of the Black Knights.  ⏎  ⏎ Formerly had a public persona of a maid dispatched by the Ashford family to care for Lelouch and Nunnally.  ⏎  ⏎ Voluntarily came to serve Emperor Lelouch until his final moments.  ⏎  ⏎ After the events of the Zero Requiem, she helped resolve conflict across the world from the shadows, and joined Kallen in infiltrating the Kingdom of Zilkhstan.

### dic\_pilot\_SAYOKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9220b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b00f\]
> JP (źródło tłumaczenia): 　Ｃ．Ｃ．と再会した後は、そのままルルーシュの復活、ナナリー救出作戦に協力した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She then accompanied this group through the entire affair, assisting with both Lelouch's resurrection and the Nunnally rescue operation.

### dic\_pilot\_MIREY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9220b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9220b010\]
> JP (źródło tłumaczenia): 　ニュースリポーター。 ⏎ 　ナナリーがさらわれた難民キャンプでの襲撃事件を取材するためリヴァルとともにジルクスタン王国におもむいた。 ⏎ 　ルルーシュがかつて通っていたアッシュフォード学園の生徒会長であり、面倒見のいい性格で生徒たちから慕われていた。
> EN (odniesienie oficjalne, NIE polski): A news reporter. ⏎  ⏎ She came to Zilkhstan with Rivalz to chase the story of the attack on the refugee camp in which Nunnally was abducted. As the Student Council President at Ashford Academy, Lelouch's old school, her dependability earned her many admirers in the student body.

### dic\_pilot\_SHRLY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b000\]
> JP (źródło tłumaczenia): 　ルルーシュがアッシュフォード学園に通っていた頃のガールフレンド。 ⏎ 　ルルーシュがゼロである事を知りながらも、その助けになろうとした。 ⏎ 　ゼロ・レクイエムでルルーシュが死亡した後、ジェレミアと共にその遺体を運び出す役目を果たした。 ⏎ 　その縁で現在でもＣ．Ｃ．と連絡を取り合っている。
> EN (odniesienie oficjalne, NIE polski): Lelouch's girlfriend during his time at the Ashford Academy.  ⏎  ⏎ Even after learning that Lelouch was Zero, she did what she could to help him.  ⏎  ⏎ After Lelouch's death during the Zero Requiem, she helped Jeremiah sneak Lelouch's body out of custody.  ⏎  ⏎ She and C.C. have both made a point of keeping in touch with each other since then.

### dic\_pilot\_SHAMNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b002\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の聖神官。 ⏎ 　国王シャリオの実姉であり、「予言の力」でジルクスタンを導く。
> EN (odniesienie oficjalne, NIE polski): The priestess for the Kingdom of Zilkhstan, titled "the Divine". ⏎  ⏎ The elder sister of the king, Shalio, she guides Zilkhstan with her "power of prophecy".

### dic\_pilot\_SHAMNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b003\]
> JP (źródło tłumaczenia): 　ギアス嚮団から分派したファルラフの末裔であり、「無限新生」のギアスを持つ。このギアスは死亡する事で記憶を持ったまま、時間をさかのぼる事が出来るものであり、その力で過去に戻り、予言を与えていた。 ⏎ 　なお、元々は「先読み」のギアスであったが、変質して、この力となった。 ⏎ 　ゼロ・レクイエムによってもたらされた平和で、兵力の輸出が無価値となったジルクスタン王国を救うために世界そのものを変えようとする。その手段として、さかのぼる時を自由にするためにＣの世界へのアクセスを制御しようとし、その鍵とするためにナナリーを拉致した。 ⏎ 　最後はルルーシュのギアスにより、永遠に眠る事となる。 ⏎ 　その後、Ｃの世界でＣ．Ｃ．と出会い、自分のために散っていった生命やシャリオに対する悔恨の情を見せた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ A member of Farlaf, which branched off from the Geass Order, and the possessor of a Geass of endless rebirth. Her Geass allows her to effectively travel back in time from the moment of her death, with memories intact; which she uses to return to the past to create "prophecies". ⏎  ⏎ It was originally a form of future prediction Geass, but its power changed and transformed into its current state.  ⏎  ⏎ She set out to change the world, as her country, the Kingdom of Zilkhstan, found its primary export—its mercenary companies—to be worthless in the peace created by the Zero Requiem. To do this, she attempted to access C's World to freely control how far back her Geass would allow her to go, and kidnapped Nunnally as a means to this end.  ⏎  ⏎ Ultimately she is placed in an eternal sleep by Lelouch's Geass.  ⏎  ⏎ In the end she met once again with C.C. in C's World, where she expressed guilt towards the lives lost due to her actions and the suffering experienced by Shalio.

### dic\_pilot\_SHARIO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b004\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の国王。 ⏎ 　生まれつき身体が弱く、普段は車椅子を必要とする。 ⏎ 　ナイトメアフレームの操縦については天性の才能を持つ。 ⏎ 　国民に対する責任のため、自身の存在意義を示すため、愛する姉シャムナを助けるため、専用機であるナギド・シュ・メインを駆り、世界最強の戦士を目指す。 ⏎ 　その目的のためには、あらゆる事をする覚悟を持っている。 ⏎ 　シャムナの予言に絶対の信頼を寄せており、その指示のままに動く。
> EN (odniesienie oficjalne, NIE polski): The king of the Kingdom of Zilkhstan. Born with a frail, weak body, he required a wheelchair to move about. He nonetheless possessed incredible natural talent at piloting Knightmare Frames.  ⏎  ⏎ To fulfill his responsibilities to his citizens, to justify his own existence, and to help his dear sister Shamna, he piloted his personal Knightmare Frame, the Nagid Shu Meyn, and aspired to be the greatest warrior in the world. He was willing to do anything and everything needed to fulfill that goal.  ⏎  ⏎ He had unshakable faith in Shamna's prophecies, and obeyed them to the letter.

### dic\_pilot\_SHARIO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b005\]
> JP (źródło tłumaczenia): 　最強の証としてスザクを倒そうとするが、シャムナがルルーシュに倒された事で予言を得られず、スザクとランスロットsiNに敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He attempted to defeat Suzaku to prove his supremacy in battle, but ultimately lost to Suzaku's Lancelot siN after Shamna's defeat at Lelouch's hands robbed him of the benefit of her prophecies.

### dic\_pilot\_SHESTA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b006\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の聖神官シャムナの親衛隊隊長。 ⏎ 　大将軍ボルボナ・フォーグナーの息子。 ⏎ 　自惚れが強く、自己の能力を過信している面がある。
> EN (odniesienie oficjalne, NIE polski): The captain of the royal guard of the Kingdom of Zilkhstan's queen, the priestess Shamna. ⏎  ⏎ The son of the great general Bolvona Forgnar. Extremely self-absorbed, he thinks very highly of his own abilities.

### dic\_pilot\_SHESTA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b007\]
> JP (źródło tłumaczenia): 　大監獄を掌握したルルーシュ達を包囲して降伏を迫る。しかし、その力を侮り、ルルーシュの策の前に敗北した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Lelouch occupied the prison, his forces surrounded it to demand his surrender. However, he underestimated his opponent and was defeated by Lelouch's plan.

### dic\_pilot\_BOLBNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b008\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の大将軍。 ⏎ 　シャムナ、シャリオ、兵達からの信頼も厚く、王国の屋台骨を支える重要人物。
> EN (odniesienie oficjalne, NIE polski): The greatest general of the Kingdom of Zilkhstan. ⏎  ⏎ He held the trust of Shamna, Shalio, and his soldiers, and was one of the foundations of the entire Kingdom.

### dic\_pilot\_BOLBNA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b009\]
> JP (źródło tłumaczenia): 　ナナリー救出作戦ではコーネリア率いる部隊を迎え撃ち、一騎打ちを演じる。彼女を葬るために周囲の兵達に自分ごと撃つように命じたが、ジルクスタン最後の城壁である彼を失う事を恐れた兵達により、その命令は果たされなかった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Cornelia brought her forces to rescue Nunnally, he sortied his own to engage them while he challenged her to a duel. Ultimately, he commanded his soldiers to shoot at him to kill her, but his soldiers refused to fulfill this order, fearing the loss of Zilkhstan's last great support.

### dic\_pilot\_KJAPAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00a\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の暗殺部隊隊長。 ⏎ 　「敵と味方の顔の認識を入れ替える」ギアスを持ち、ジルクスタンに潜入したカレン達と戦った。
> EN (odniesienie oficjalne, NIE polski): The leader of an assassination team of the Kingdom of Zilkhstan.  ⏎  ⏎ He possessed a Geass that allowed him to alter his opponent's perception of their enemies and allies, and used it in his fight with Kallen's group.

### dic\_pilot\_KJAPAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00b\]
> JP (źródło tłumaczenia): 　ナナリー救出作戦に参加したロイド達を追い詰めたが、ニーナの機転の前に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He posed a grave danger to Lloyd's group during the Nunnally rescue operation, but Nina's quick wit ultimately overcame him.

### dic\_pilot\_BITUL\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00c\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の大監獄獄長。 ⏎ 　元は山賊の首領であり、部下共々、ジルクスタン王国に買い取ってもらったが、大監獄を根城に好き放題をやっている。 ⏎ 　性格は粗野にして自分本位であるが、生身においてもナイトメアフレームの操縦においても剛の者。 ⏎ 　戦闘では、ナイトギガフォートレス、バタララン・ドゥを駆る。
> EN (odniesienie oficjalne, NIE polski): Jailor in charge of the Kingdom of Zilkhstan's prison.  ⏎  ⏎ Formerly the head of a group of bandits, his entire group was hired by the Kingdom of Zilkhstan. However, he treated the prison he was given as a hideout from which he essentially did whatever he wanted.  ⏎  ⏎ He was selfish and crude, but at the same time a man of steel, powerful in both Knightmare Frame and human-scale combat.  ⏎  ⏎ In combat, he piloted the Knight Gigafortress Batalalan Du.

### dic\_pilot\_BITUL\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00d\]
> JP (źródło tłumaczenia): 　ルルーシュを復活させるために大監獄に潜入したカレンと互いに生身で対決して一度は圧倒するが、ナナリー救出作戦ではカレンの紅蓮特式に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Kallen snuck into the prison to resurrect Lelouch, he overpowered her in hand-to-hand combat. Later, during the Nunnally rescue operation, he was defeated by her in the Guren Type Special.

### dic\_pilot\_ZEE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00e\]
> JP (źródło tłumaczenia): 　ビトゥルの部下。 ⏎ 　頭の切れる人物で、ビトゥルの指示の下で監獄のメンバーを動かす。 ⏎ 　戦い慣れしており、咲世子と生身の戦闘で渡り合った。
> EN (odniesienie oficjalne, NIE polski): Bitool's subordinate. ⏎  ⏎ A sharp individual who drove the prisoners into action at Bitool's command, he is a combat expert who traded blows with Sayoko.

### dic\_pilot\_ZEE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b00f\]
> JP (źródło tłumaczenia): 　復活したルルーシュのギアスにより、自ら生命を絶った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He took his own life under the orders of the newly resurrected Lelouch's Geass.

### dic\_pilot\_IZURU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b010\]
> JP (źródło tłumaczenia): 　レッドファイブのパイロット。１６歳。 ⏎ 　チームラビッツのリーダーで、持ち前の明るさと素直さでチームをまとめる。 ⏎ 　集中力に優れており、チームの中でもハーモニックレベルが最も高い。 ⏎ 　グランツェーレ都市学園に通っていた際、多くのヒーロー漫画を読んだ事でヒーローになるという夢を持っており、それが戦いの動機にもなっている。 ⏎ 　常にポジティブかつ純粋だが、それ故の天然発言で周囲から総ツッコミを受ける事も多い。 ⏎ 　趣味は漫画を描く事だが、絵が下手過ぎて周囲からは不評である。 ⏎ 　仲間との数々の作戦任務を経験し、チームとしても個人としても大きく成長していった。
> EN (odniesienie oficjalne, NIE polski): The pilot of Red 5. 16 years old.  ⏎  ⏎ As Team Rabbits' "leader", Izuru keeps the team grounded with his sincerity and unfailing good spirit.  ⏎  ⏎ His concentration is especially developed, and his Harmonic Level is the highest among the team.  ⏎  ⏎ He was inspired by a TV hero in a magazine he happened across when he first came to Glanzehre Cosmopolitan Academy. This would ultimately come to serve as his inspiration and role model. ⏎  ⏎ He is an eternal optimist, which often manifests itself in rather tone-deaf remarks which his entire team gets on his case about.  ⏎  ⏎ His hobby is drawing manga, but, sadly, he lacks the skill to make his manga truly compelling.  ⏎  ⏎ Over the course of many missions, Izuru grew in leaps and bounds, both as an individual and as a member—and leader—of his team. ⏎ 

### dic\_pilot\_IZURU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b011\]
> JP (źródło tłumaczenia): 　圧倒的な戦闘力を持つジアートに唯一対抗し、彼に獲物として認識されている。 ⏎ 　母親はウルガル人のテオーリア、父親はシモン司令であり、アサギとは異母兄弟であった。 ⏎ 　最終決戦では、ハーモニックレベルの極端な上昇による異常が発見され、ゴディニオンで待機を命じられたが、仲間たちの窮地を救うために出撃する。ジアートとの戦いの中で覚醒し、レッドファイブを真の姿へと変貌させ、勝利をつかんだ。
> EN (odniesienie oficjalne, NIE polski): He performed well enough against the powerful Jiart for the latter to mark him as his personal prey.  ⏎  ⏎ His mother is the Wulgaru Teoria, and his father is Commander Simon, making him Asagi's half-brother.  ⏎  ⏎ In the final battle, he initially stood by on the Godinion due to health problems caused by his increasing Harmonic Level. But when the Rabbits were in danger, he deployed, heedless of his health, to help them. ⏎ His latent power awakened in combat with Jiart and transformed Red 5 into its true form, leading to his victory.

### dic\_pilot\_ASAGI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9260b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b012\]
> JP (źródło tłumaczenia): 　ブルーワンのパイロット。１７歳。 ⏎ 　チームラビッツのフォワード担当で、前衛で格闘戦を展開する。 ⏎ 　優れた操縦技術と豊富な知識を持っているが、プレッシャーに弱く、なかなか本来の力を発揮できない。 ⏎ 　冷静でまじめかつ常識人でラビッツのメンバーへのツッコミも担当するが、アガリ症で何かと胃を痛めているため、常に胃薬を持ち歩き手放せない。
> EN (odniesienie oficjalne, NIE polski): The pilot of Blue 1. 17 years old.  ⏎  ⏎ As Team Rabbits' "forward", he takes the front line in melee combat.  ⏎  ⏎ Despite his impressive piloting skill and deep knowledge, he handles pressure extremely poorly and has difficulty fighting at his full potential in live combat.  ⏎  ⏎ He takes things seriously and is generally the most "normal" among the Rabbits, so it falls to him to call out his teammates' more glaring shenanigans.  ⏎  ⏎ This tendency, though, tends to give him a negative outlook on life. He never goes anywhere without medicine for his stomach. ⏎ 

### dic\_pilot\_ASAGI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9260b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9260b013\]
> JP (źródło tłumaczenia): 　成長を続けるイズルとの実力差に悩んでいたが、スズカゼに相談をしたことで、イズルをエースパイロットと認め自身はサポートに徹することを決めた。悩みが吹っ切れたことで大きく成長していった。 ⏎ 　なお、イズルとは、シモン司令に提供された遺伝子を共有する異母兄弟であった事が後に判明した。
> EN (odniesienie oficjalne, NIE polski): The more Izuru outpaced him, the more his stress grew. After speaking with Suzukaze, he recognized Izuru as an ace pilot and resolved to support him. With his inner troubles resolved, he was able to grow as a person. ⏎  ⏎ He also learned that he shared his paternal genes from Commander Simon with Izuru, making the two half-brothers. ⏎ 

### dic\_pilot\_KEI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b000\]
> JP (źródło tłumaczenia): 　パープルツーのパイロット。１６歳。 ⏎ 　チームラビッツのコントロール担当で、戦況分析と味方機への管制指揮を行う。 ⏎ 　高い空間把握能力と聴力を持ち、特殊な電波を聞き分けることも出来る。 ⏎ 　冷静な性格だが仲間想いで、タマキの面倒やアサギの体調にも気を配っている。 ⏎ 　極度の甘党で、趣味で作るケーキはあまりにも甘すぎる味付けと色味が相まって周囲には不評であるが、本人は気づいていない。
> EN (odniesienie oficjalne, NIE polski): The pilot of Purple 2. 16 years old.  ⏎  ⏎ As Team Rabbits' "control", their combat coordinator, she analyzes the flow of combat and gives tactical instructions to her allies.  ⏎  ⏎ Her hearing and spatial reasoning are heightened, and she can naturally perceive special electromagnetic frequencies via her sense of hearing.  ⏎  ⏎ She has a subdued demeanor, but cares deeply about her teammates; she looks out for Tamaki and frets over Asagi's health.  ⏎  ⏎ She likes baking cakes, but one might argue that her sweet tooth is another faculty of hers that's been "enhanced"—her cakes are all overly sweet (and tend to look outrageous), though she herself thinks they're just fine. ⏎ 

### dic\_pilot\_KEI\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b001\]
> JP (źródło tłumaczenia): 　イズルに窮地を助けられてから、ほのかな想いを寄せるようになる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She began to develop feelings for Izuru after he saved her from peril.

### dic\_pilot\_TAMA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b002\]
> JP (źródło tłumaczenia): 　ローズスリーのパイロット。１５歳。 ⏎ 　チームラビッツのブースター担当で、スピードを活かした突撃で敵を錯乱させる。 ⏎ 　動体視力とＧ耐性に優れ、機体加速時に発生する最大２０Ｇの力にも耐えられる。 ⏎ 　細かい事は気にしない天真爛漫な性格で本能的に行動するが、本質を突くような発言をする事もある。 ⏎ 　恋愛に憧れていて惚れやすく、イケメンを見るとすぐに告白し、玉砕を繰り返してきた。 ⏎ 　大好物はイカの塩辛で、てんこ盛りの白ご飯と一緒に食べる。
> EN (odniesienie oficjalne, NIE polski): The pilot of Rose 3. 15 years old.  ⏎  ⏎ As Team Rabbits' "booster", she breaks up enemy formations with high-speed charge maneuvers.  ⏎  ⏎ Her visual tracking and g-force tolerance are heightened to the point where she can handle acceleration equal to 20 times Earth gravity without blacking out.  ⏎  ⏎ She has a bubbly, worry-free personality and largely acts according to her whims, but once in a while, she can drop a piercing insight on you from seemingly nowhere.  ⏎  ⏎ She loves the idea of romance and develops crushes easily. She wastes no time asking out any hot guy she sees...and ends up consistently rejected.  ⏎  ⏎ Her favorite food is squid shiokara, which she eats on heaping piles of rice.

### dic\_pilot\_TAMA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b003\]
> JP (źródło tłumaczenia): 　パトリックの死後、自分への恋心を理解して、ケイに対しては後悔と悲しみを吐露していた。そして、アサギの命令を無視してオペレーション・ヘブンズゲートでルティエルをパトリックの仇として追い回し、結果的に彼女を撃破した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She realized after Patrick's death that he had feelings for her, and she aired all her anguish and sorrow over this with Kei. ⏎  ⏎ She disregarded Asagi's orders during Operation Heaven's Gate and chased down Lutiel, succeeding in avenging Patrick's death.

### dic\_pilot\_SRUGA\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b004\]
> JP (źródło tłumaczenia): 　ゴールドフォーのパイロット。１６歳。 ⏎ 　チームラビッツのガンナー担当で、後方からの長距離射撃で味方を援護する。 ⏎ 　卓越した記憶力を持ったミリタリーオタクでもあり、兵器のスペックに詳しく、専門分野の話になると早口になる。 ⏎ 　明るい性格の軟派で、美人を見るとすぐに口説きにいくが、成功した事はない。 ⏎ 　根は純情であり、大人向けのコンテンツを直視できない事もあった。 ⏎ 　大好物はカレーで、本格的なものよりもレトルト味を好む。
> EN (odniesienie oficjalne, NIE polski): The pilot of Gold 4. 16 years old.  ⏎  ⏎ As Team Rabbits' "gunner", his position is self-explanatory: he provides long-range support fire from the back line.  ⏎  ⏎ He has a photographic memory which, combined with his obsession with military hardware, makes him an expert in weapon specifications. When he can raise the subject, he starts talking a mile a minute.  ⏎  ⏎ He's cheery and relaxed. He hits on any beautiful woman he sees, with a success rate expressible as a big fat zero.  ⏎  ⏎ Despite appearances, he's very innocent and he's proven quite unable to watch adult content.  ⏎  ⏎ He loves curry, and prefers instant curry to fresh.

### dic\_pilot\_SRUGA\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b005\]
> JP (źródło tłumaczenia): 　宇宙から地上への超長距離狙撃でウルガル軍団長のクレインを撃墜した他、ゴディニオンとの管制リンクによってルティエルの撃破にも成功する等、得意の狙撃で大きな戦果を挙げた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His sniping skills were key to multiple victories. He destroyed the Wulgaru commander Klein on the Earth's surface from orbit, and Lutiel by linking up with the Godinion's weapons systems.

### dic\_pilot\_ANJU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b006\]
> JP (źródło tłumaczenia): 　ブラックシックスのパイロット。１５歳。 ⏎ 　チームラビッツの追加メンバーとして配属された。 ⏎ 　普段は控えめでおとなしい性格だが、アッシュに乗ると凶暴になり罵詈雑言を吐く。 ⏎ 　個人的な戦闘能力は高いものの、協調性に欠ける一面があり、戦場では独断行動をとる場面が多い。 ⏎ 　兵器に関する知識や射撃の腕も一級品で、搭乗するアッシュの整備も自ら行う。 ⏎ 　なお、性別は不明。
> EN (odniesienie oficjalne, NIE polski): The pilot of Black 6. 15 years old.  ⏎  ⏎ Ange was assigned to Team Rabbits as an additional member.  ⏎  ⏎ Normally shy and reserved, Ange becomes enraged, foul-mouthed, and brash in the cockpit of an AHSMB.  ⏎  ⏎ Ange is very strong in combat but virtually incapable of teamwork, so they're often assigned to tasks best suited to individual action.  ⏎  ⏎ Ange's weapons mastery and shooting skill is unparalleled, and they maintain their AHSMB on their own.  ⏎  ⏎ Ange's gender is unclear, and the team respects their wish to stay silent on the matter. (Though this doesn't stop a bit of curiosity from the other Rabbits.)

### dic\_pilot\_ANJU\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b007\]
> JP (źródło tłumaczenia): 　最終決戦では、チームドーベルマンのチャンドラと共に量産アッシュ部隊を率いて活躍した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the final battle, Ange joined Team Doberman's Chandra at the head of the mass-produced AHSMB division. ⏎ 

### dic\_pilot\_RANDY\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b008\]
> JP (źródło tłumaczenia): 　チームドーベルマンのリーダー。 ⏎ 　気さくなお調子者で、その言動からチームが「マンザイスリー」「ガッカリスリー」などと呼ばれる事もある。 ⏎ 　一方で機体の操縦技術は極めて優秀であり、多くの戦果を挙げてきた。 ⏎ 　また、面倒見のいい性格で、グランツェーレ都市学園の後輩であるイズルにヒーローについて説いたり、秘蔵のコレクションを貸したりするなどした。
> EN (odniesienie oficjalne, NIE polski): The leader of Team Doberman.  ⏎  ⏎ Randy's continually laidback attitude has earned his team nicknames like "Comedic Three" and "Bummer Three". ⏎  ⏎ As a pilot, however, he is an elite among elites and has carried out many successful operations.  ⏎  ⏎ He is also a reliable mentor, counseling his younger fellow Glanzehre student Izuru in heroism and then lending him part of his secret "collection".

### dic\_pilot\_RANDY\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b009\]
> JP (źródło tłumaczenia): 　ウルガルのゲートを強行偵察するオペレーション・イーグルランデッドでは、最後まで獅子奮迅の活躍をし、生還する希望を捨てずに戦うも、その望みは叶わなかった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In Operation Eagle Landed, the mission to scout the Wulgaru's gate, he fought with incredible ferocity and never gave up hope of surviving to the very end, but his optimism proved to be in vain. ⏎ 

### dic\_pilot\_CHNDR\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00a\]
> JP (źródło tłumaczenia): 　チームドーベルマンのサブリーダー。 ⏎ 　真面目かつ冷静な性格で、ランディのボケに対するツッコミ役を自認している。 ⏎ 　高い戦術分析能力を持ち、戦況把握や情報共有といった後方支援のポジションでチームを支える。 ⏎ 　地球に住むふくよかな体格の許嫁に対し、一途な想いを寄せている。
> EN (odniesienie oficjalne, NIE polski): Team Doberman's sub-leader.  ⏎  ⏎ Diligent and cool-headed, Chandra tries to put a brake on Randy's more outlandish habits.  ⏎  ⏎ A talented tactician, he supports the team by monitoring and analyzing the situation and communicating with his teammates.  ⏎  ⏎ He sincerely loves his fiancée, a quite attractive girl who lives on Earth.

### dic\_pilot\_CHNDR\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00b\]
> JP (źródło tłumaczenia): 　オペレーション・イーグルランデッドではチームで唯一生き残り、重要なデータをＭＪＰに持ち帰る。 ⏎ 　最終決戦では量産型アッシュ部隊を率いて奮闘した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ As his team's only survivor of Operation Eagle Landed, he brought critical strategic data to the MJP.  ⏎  ⏎ In the final battle, he returned to duty leading the production AHSMB division.

### dic\_pilot\_PTRIC\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00c\]
> JP (źródło tłumaczenia): 　チームドーベルマンのメンバー。 ⏎ 　天然ボケでおっとりとした性格をしているが、場の空気を読まない発言をすることも多い。 ⏎ 　ランディとチャンドラの後輩でもあり、チームでは遊撃的な役割で前衛のランディと後衛のチャンドラをサポートする。
> EN (odniesienie oficjalne, NIE polski): Team Doberman's third member.  ⏎  ⏎ Patrick is quiet, naive, and tends to say fairly oblivious things.  ⏎  ⏎ Being younger than Randy and Chandra, he backs up Randy's assaults and Chandra's support as necessary. ⏎ 

### dic\_pilot\_PTRIC\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00d\]
> JP (źródło tłumaczenia): 　戦いの中、タマキに対して、密かに好意を抱くようになる。 ⏎ 　オペレーション・イーグルランデッドにおいて、作戦終了後にイカの塩辛のプレゼントと共にタマキへ想いを伝えるつもりでいたが、ウルガル軍団長のルティエルの攻撃で戦死した。
> EN (odniesienie oficjalne, NIE polski): He developed feelings for Tamaki over the course of the war.  ⏎  ⏎ He planned to tell her how he felt after Operation Eagle Landed with a gift of squid shiokara, but was tragically killed by the Wulgaru commander Lutiel.

### dic\_pilot\_SIMON\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00e\]
> JP (źródło tłumaczenia): 　ＭＪＰの司令官。階級は大佐。 ⏎ 　ウルガルの地球侵攻に備え、アッシュ開発やパイロット育成を主導した。 ⏎ 　過去に負った傷が原因で、補助装置が組み込まれた金属製ゴーグルと杖が手放せなくなっている。 ⏎ 　冷静沈着な態度の裏には強い決意を秘めている。
> EN (odniesienie oficjalne, NIE polski): Commander of the MJP. Holds the rank of captain.  ⏎  ⏎ Gato is in charge of counter-operations to the Wulgaru invasion of Earth, developing the AHSMB units and training pilots.  ⏎  ⏎ He wears a metal eyepiece with assistive features and carries a cane due to old wounds.  ⏎  ⏎ His cold demeanor belies an iron will.

### dic\_pilot\_SIMON\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92a0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b00f\]
> JP (źródło tłumaczenia): 　イズルとアサギへの遺伝子提供者であり、遺伝子上は彼等の父親にあたる。 ⏎ 　最終決戦では、総司令官として全体の指揮を執り、最後は捨て身の覚悟で母艦と化したスターローズをウルガルの移送ゲートにぶつけて作戦を成功させた。 ⏎ 　自身は生命を捨てるつもりであったが、テオーリアに間一髪のところで救助され、生還を果たした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His genetics were used to clone Izuru and Asagi, making him, essentially, their father.  ⏎  ⏎ He was the operational commander in the final battle. At the climax of the battle, he risked his life to personally ram the Star Rose, repurposed as a mothership, into the Wulgaru warp gate.  ⏎  ⏎ He was prepared to die in the attempt, but Teoria rescued him at the last second. ⏎ 

### dic\_pilot\_SZKAZE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b010\]
> JP (źródło tłumaczenia): 　ゴディニオンの艦長。 ⏎ 　階級は少佐。２８歳。 ⏎ 　グランツェーレ都市学園で教官としてパイロットを育成する任務に就いていたが、教え子であるチームラビッツの実戦配備に伴って転属した。 ⏎ 　かつてＧＤＦのパイロット時代にウルガルとの戦闘を経験し、唯一生き残った過去を持ち、その時の負傷により前線を退く。 ⏎ 　イズル達を厳しく指導するが、同時に素性を知る彼らを戦わせる事に思い悩んでいる。 ⏎ 　整備長のレイカとは幼馴染で相談する事も多いが、泣き上戸で普段は言わない弱音を吐き出してしまう事もある。なお、彼女から愛称である「リンリン」と呼ばれる事は拒否している。 ⏎ 　棒付きのキャンディをいつも持ち歩いており、部下をリラックスさせる際などにふるまう。
> EN (odniesienie oficjalne, NIE polski): Captain of the Godinion.  ⏎  ⏎ Holds the rank of lieutenant commander. She is 28 years old.  ⏎  ⏎ Rin was a piloting instructor at Glanzehre Cosmopolitan Academy until her students, Team Rabbits, were deployed into combat and she was transferred with them.  ⏎  ⏎ She was the only GDF pilot to have survived combat with the Wulgaru, but she had to leave the front lines due to the injuries she sustained.  ⏎  ⏎ Rin plays a strict instructor to the Rabbits, but she knows their nature and feels conflicted about having to order them into combat.  ⏎  ⏎ She has known the Rabbits' head mechanic, Reika, since childhood and often vents to her, crying over drinks and revealing doubts she would never voice in public. Reika, meanwhile, still calls her "Rin-Rin" (despite Rin's many, and vociferous, protests).  ⏎  ⏎ She always carries small lollipops with her and uses them to ease her soldiers' tension.

### dic\_pilot\_ZIKFRT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92a0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92a0b012\]
> JP (źródło tłumaczenia): 　ゴディニオンの通信士。階級は中尉。 ⏎ 　真面目な性格で、非番の時でも仕事関連の雑事をこなす傍ら、筋肉トレーニングに精を出す一面もある。 ⏎ 　情報処理能力に秀でており、軍学校時代からの腐れ縁であるジュリアーノと連携して戦況や艦の航行状況などをスズカゼ艦長に報告する。
> EN (odniesienie oficjalne, NIE polski): A comms officer on the Godinion. Holds the rank of lieutenant junior grade.  ⏎  ⏎ Siegfried is a hard worker, dedicated to his duties and his personal training even when off duty.  ⏎  ⏎ He uses his strong analytical skills to work with his academy acquaintance Giuliano and keep Captain Suzukaze up to date on the state of combat and the ship's maneuvers. ⏎ 

### dic\_pilot\_JRIANO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b000\]
> JP (źródło tłumaczenia): 　ゴディニオンの通信士。階級は中尉。 ⏎ 　直観力と操艦能力が高く、成績だけなら軍学校始まって以来の天才と称されていた。ただし当時は素行不良で、学友のジークフリートに問題を揉み消してもらっていたという過去を持つ。 ⏎ 　猫好きであり、女性に対しては紳士的かつフランクに接する。 ⏎ 　イケメン好きのタマキを「子猫ちゃん」と呼ぶ事などでハーモニックレベルの上昇に一役買っている。
> EN (odniesienie oficjalne, NIE polski): A comms officer on the Godinion. Holds the rank of lieutenant junior grade. ⏎  ⏎ Giuliano's instincts and piloting skills are well-developed. He has been lauded as a genius ever since his time in military school. However, he was never especially serious and had to be bailed out of many self-inflicted problems by his friend Siegfried.  ⏎  ⏎ He likes cats and acts gentlemanly and openly toward women.  ⏎  ⏎ Since Tamaki likes handsome men, he calls her "kitty" to raise her Harmonic Level. ⏎ 

### dic\_pilot\_REIKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b002\]
> JP (źródło tłumaczenia): 　ゴディニオンの整備長。階級は大尉。 ⏎ 　豪胆な姉御肌の酒豪であると同時に、細やかな気遣いを見せる。その頼りがいから部下の整備士からは「おやっさん」と呼ばれている。 ⏎ 　スズカゼとは幼馴染かつ士官学校時代の同期で、彼女の良き相談相手でもあり、彼女の事を「リンリン」と呼ぶ。が、本人には拒否されている。 ⏎ 　戦闘時にはブリッジで戦況や各アッシュのハーモニックレベルをモニターする。 ⏎ 　京都にある大手製薬会社・西園寺製薬の令嬢である。
> EN (odniesienie oficjalne, NIE polski): The head mechanic on the Godinion. Holds the rank of lieutenant (which is to say, one rank below Rin).  ⏎  ⏎ She is fearless, trustworthy, and a strong drinker, while also having a caring and discreet side. Her dependability leads to her staff calling her "Boss". ⏎  ⏎ She is both a childhood friend and a classmate of Lieutenant Commander Suzukaze, and calls her "Rin-Rin", a nickname that Rin complains about. Often.  ⏎  ⏎ She monitors the battle and the status of the AHSMBs on the bridge during combat.  ⏎  ⏎ She is the heiress to the Kyoto-based pharmaceutical giant Saionji Pharmaceuticals, but went into practical mechanics despite her family's opposition. ⏎ 

### dic\_pilot\_RURA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b004\]
> JP (źródło tłumaczenia): 　ゴディニオンの軍医。 ⏎ 　チームラビッツを心身両面からケアし、ジュリアシステムへの適応度を計測する。 ⏎ 　スズカゼ、レイカとは士官学校時代の同期。
> EN (odniesienie oficjalne, NIE polski): The Godinion's medic.  ⏎  ⏎ She handles Team Rabbits' physical and psychological care and helps adjust the Juria System.  ⏎  ⏎ She was classmates with Suzukaze and Reika at the officer's academy.

### dic\_pilot\_DANN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b006\]
> JP (źródło tłumaczenia): 　レッドファイブのピットクルーの一人。 ⏎ 　整備士として確かな腕を持つ。 ⏎ 　平凡な見た目ではあるが、長いフルネームを持つ。
> EN (odniesienie oficjalne, NIE polski): A member of Red 5's pit crew. ⏎  ⏎ His talent as a mechanic is undeniable. ⏎  ⏎ He has a long and complicated name in spite of his plain appearance. ⏎ 

### dic\_pilot\_MAYU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b008\]
> JP (źródło tłumaczenia): 　レッドファイブのピットクルーの一人。 ⏎ 　明るく気さくな性格で、イズルのことを「イズルっち」「イーちゃん」「イズぴょん」などのあだ名で呼ぶ。 ⏎ 　整備士として優れた直観力を持ち、機械の故障箇所や原因の素早い把握が出来る。 ⏎ 　出身はＭＪＰ本部のある富良野で、親もＭＪＰで働いている。 ⏎ 　長い間、実家を離れており、同じピットクルーのデガワを父、ダンを兄のように慕っている。
> EN (odniesienie oficjalne, NIE polski): A member of Red 5's pit crew.  ⏎  ⏎ She's flighty and cheery. She likes to call Izuru by various nicknames like Izurucchi or Ichan or Izupyon. ⏎  ⏎ She has a strong mechanic's intuition and can quickly find the locations and causes of mechanical failures.  ⏎  ⏎ She was born on an MJP base in Furano, and her father works for the MJP as well.  ⏎  ⏎ She has been away from her home so long that she considers her crewmates her own family: Degawa as her father, and Dan her brother. ⏎ 

### dic\_pilot\_DEGAWA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b00a\]
> JP (źródło tłumaczenia): 　レッドファイブのピットクルーの一人。 ⏎ 　力仕事を得意としており、整備ではダンとマユのサポート役に回ることが多い。 ⏎ 　趣味は俳句で、五七五の韻を踏んだ発言をするが、たいていは季語が含まれてないため、川柳になってしまっている。
> EN (odniesienie oficjalne, NIE polski): A member of Red 5's pit crew.  ⏎  ⏎ He mainly uses his great strength to assist Dan and Mayu.  ⏎  ⏎ He enjoys composing haiku, but since most of his extemporaneous poetry lacks a nature theme, he's technically composing senryu. (This matters not a jot to him.)

### dic\_pilot\_AMANE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b00c\]
> JP (źródło tłumaczenia): 　ＧＤＦ統合参謀本部の情報士官。 ⏎ 　参謀次長のコミネ大佐の副官を務めるが、実務の多くは彼女が担当している。 ⏎ 　情報収集と作戦立案を主な任務としているが、実戦部隊の指揮に関わることも多い。 ⏎ 　スズカゼ達は士官学校時代の先輩にあたり、よく一緒に飲みに行く。
> EN (odniesienie oficjalne, NIE polski): An intelligence analyst at GDF Staff HQ.  ⏎  ⏎ She serves as assistant to the GDF's vice-chief, Captain Komine, and ultimately handles most of the actual day-to-day work.  ⏎  ⏎ Her official duties are data collection and tactical planning, but she often finds herself in live command.  ⏎  ⏎ She was just behind Suzukaze and her classmates at the officer's academy and often goes drinking with them.

### dic\_pilot\_AMANE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b00d\]
> JP (źródło tłumaczenia): 　わずか一日で大尉から大佐に昇進し、最終決戦では艦隊指揮を任された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She was promoted from Lieutenant to Captain in the space of just a day and commanded the fleet during the final battle.

### dic\_pilot\_KOMINE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b00e\]
> JP (źródło tłumaczenia): 　ＧＤＦ統合参謀本部の参謀次長。階級は大佐。 ⏎ 　アマネの上官で、実戦部隊の指揮を執るが、作戦立案の多くはアマネに委ねている。 ⏎ 　手柄や自らの保身に目を奪われ、正しい戦況判断が出来ないことがある。
> EN (odniesienie oficjalne, NIE polski): The vice-chief of the GDF Staff HQ. Holds the rank of Captain.  ⏎  ⏎ He is Amane's superior and officially in charge of operational command, but delegates most of the actual tactical planning to Amane.  ⏎  ⏎ He is focused only on his own glory and job security, which has led to him making tactical blunders.

### dic\_pilot\_KOMINE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b00f\]
> JP (źródło tłumaczenia): 　オペレーション・ナイトブロウでは、敵部隊の戦力を見誤りながらも作戦を強行してチームラビッツを全滅寸前まで追い込んだ。 ⏎ 　ケレス大戦ではウルガルの奇襲に遭い、作戦予定時間を繰り上げて戦闘を開始して全軍を窮地に立たせ、以降は前線での任務を外された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In Operation Night Blow, he misjudged the enemy forces but insisted on continuing the operation, driving Team Rabbits to near defeat.  ⏎  ⏎ When the Wulgaru launched their ambush at the Battle of Ceres, he opened combat ahead of schedule and placed all his forces at risk. Afterwards, he was removed from active frontline command.

### dic\_pilot\_TEORIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b010\]
> JP (źródło tłumaczenia): 　謎の少女。 ⏎ 　記憶を消される前のイズルとは親しい仲であり、彼から必ず守ることを誓われた過去がある。
> EN (odniesienie oficjalne, NIE polski): A mysterious girl. ⏎  ⏎ She was close with Izuru before his memories were erased, and he once promised her that he would always protect her. ⏎ 

### dic\_pilot\_TEORIA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b011\]
> JP (źródło tłumaczenia): 　その正体は地球に亡命してきたウルガルの皇女（プレ・エグゼシア）で、ジアートの妹。 ⏎ 　様々な種族を滅ぼすウルガルの狩りに心を痛めた母の密命を受け、地球にウルガルの情報をもたらした。 ⏎ 　ＭＪＰ機関にジュリアシステムの元となる技術とパイロット育成のために自らの遺伝子を提供しており、イズルの遺伝子上の母親にあたる。 ⏎ 　最終決戦では自ら機動兵器で出撃し、特攻したシモンの生命を救った。
> EN (odniesienie oficjalne, NIE polski): In reality, she is Jiart's younger sister and is the Wulgaru's Prae Exousia, or princess, who defected to Earth.  ⏎  ⏎ Like her mother, she regretted the way the Wulgaru exterminated vast numbers of species, and leaked Wulgaru information to Earth.  ⏎  ⏎ Among the information she brought was the specifications for the technology that would be developed into the Juria System by the MJP, as well as her own DNA to be used to grow pilots. She is Izuru's genetic mother.  ⏎  ⏎ She joined the final battle in her own mobile weapon and saved Simon's life. ⏎ 

### dic\_pilot\_DANIEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b012\]
> JP (źródło tłumaczenia): 　テオーリアに付き添う執事。 ⏎ 　護衛も兼任しており、格闘術に秀でる。 ⏎ 　テオーリアの身を第一に考えて行動する。
> EN (odniesienie oficjalne, NIE polski): A butler who serves Teoria. ⏎  ⏎ He is also her bodyguard and is skilled at close quarters combat. ⏎  ⏎ He always puts Teoria's safety above all else. ⏎ 

### dic\_pilot\_DANIEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b013\]
> JP (źródło tłumaczenia): 　テオーリアと同じくウルガル人で、共に地球に亡命してきた。 ⏎ 　最終決戦では機動兵器に搭乗して、ウルガルと戦った。
> EN (odniesienie oficjalne, NIE polski): In fact, he is a Wulgaru like Teoria, and joined her when she defected to Earth.  ⏎  ⏎ He joined the final battle in his mobile weapon and fought against his fellow Wulgaru.

### dic\_pilot\_ZIAT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b014\]
> JP (źródło tłumaczenia): 　ウルガルの第二皇子（プレ・エグゼス）。 ⏎ 　皇帝ガルキエの異母弟。 ⏎ 　好戦的な性格で、自らの本能や欲望に忠実に行動する。 ⏎ 　戦いにおいても独自の美学を持ち、戦うに値しない弱い敵には目を向けない。
> EN (odniesienie oficjalne, NIE polski): The Wulgaru's Prae Exous, or second prince.  ⏎  ⏎ He is the half-brother of Emperor Galkie by their father.  ⏎  ⏎ He enjoys combat and never resists his instincts or passions.  ⏎  ⏎ He has high standards for what constitutes good combat and pays no attention to enemies he deems unworthy.

### dic\_pilot\_ZIAT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b015\]
> JP (źródło tłumaczenia): 　自らの好敵手を探しており、戦場で出会ったイズルを狩りの獲物「ラマタ」として認識する。 ⏎ 　妹であるテオーリアに執着しており、ルメスから情報を得る前から彼女が地球にいるのではないかと考えていた。 ⏎ 　最終決戦では、オーバーロードモードとなった機体でイズルと激戦を繰り広げるも、敗北した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His search for a good fight led him to mark Izuru as his "lamata", or personal prey, after they met on the battlefield.  ⏎  ⏎ He is obsessed with his sister Teoria, and he weighed the possibility that she was on Earth even before Lumes gave him information on her whereabouts. ⏎  ⏎ In the final battle, he used his mobile weapon's Overlord Mode in pitched combat with Izuru that ultimately ended in his own defeat. ⏎ 

### dic\_pilot\_GALKIE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b016\]
> JP (źródło tłumaczenia): 　ウルガルの皇帝。 ⏎ 　ジアートの異母兄にあたる。 ⏎ 　冷徹な判断もいとわない合理主義者で、前皇帝の父を暗殺して実権を握った。 ⏎ 　３００年に一度の宣託を受け、地球への侵攻を決定した。 ⏎ 　ジアートの独断行動は諫めずに黙認しており、ジアートからも一角の敬意を払われている。
> EN (odniesienie oficjalne, NIE polski): Emperor of the Wulgaru, and Jiart's half-brother. ⏎  ⏎ He is ruthless and coldly logical. He ascended by having his father, the former Emperor, assassinated. ⏎  ⏎ He began his invasion of Earth after receiving his first premonition in 300 years. ⏎  ⏎ He observes Jiart's feats in the war without interfering or giving any feedback. Jiart, in turn, respects him greatly.

### dic\_pilot\_GALKIE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b017\]
> JP (źródło tłumaczenia): 　最終決戦では地球側に移送ゲートを破壊され、狩りは中断する事となったが地球人にウルガルの進化の可能性を感じ取った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the Earth-side warp gate was destroyed in the final battle, the hunt of Earth had to be called off. However, he still believed the Earthlings held the key to Wulgaru evolution. ⏎ 

### dic\_pilot\_CLAIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:92e0b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b018\]
> JP (źródło tłumaczenia): 　ウルガル第１１氏族の長で、軍団長（レガトゥス）の一人。 ⏎ 　圧倒的なスピードを活かした奇襲と相手部隊を翻弄する戦術を得意とする。 ⏎ 　短気で残忍な性格をしており、他人に先を越される事を嫌う。
> EN (odniesienie oficjalne, NIE polski): A Legatus and the chief of the 11th Wulgaru clan.  ⏎  ⏎ His tactics revolve around dominating enemy forces with overwhelming speed.  ⏎  ⏎ He is impatient and impetuous, and hates it when others are ahead of him.

### dic\_pilot\_CLAIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:92e0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:92e0b019\]
> JP (źródło tłumaczenia): 　戦いの中でアンジュの乗るブラックシックスを狩りの獲物として見定める。 ⏎ 　その後、グランツェーレ都市学園を強襲するが、チームラビッツの連係攻撃とスルガの超長距離射撃の前に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He fought Ange's Black 6 and designated it as his personal target.  ⏎  ⏎ Later, in the assault on Glanzehre Cosmopolitan Academy, he was defeated by Team Rabbits' combined attacks and Suruga's ultra-long-range snipe shot. ⏎ 

### dic\_pilot\_RADA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b000\]
> JP (źródło tłumaczenia): 　ウルガル第１３氏族の長で、軍団長（レガトゥス）の一人。 ⏎ 　ヒステリックかつサディスティックな性格で、相手をいたぶってから殲滅する陰湿な戦術を好む。
> EN (odniesienie oficjalne, NIE polski): A Legatus and the chief of the 13th Wulgaru clan.  ⏎  ⏎ He is brutish and sadistic, and loves strategies that toy with his enemy, draining them of hope before crushing them utterly.

### dic\_pilot\_RADA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b001\]
> JP (źródło tłumaczenia): 　ジアートとルメスの会話を盗み聞きしてテオーリアの所在を知ってしまい、口封じのためにジアートに殺された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He discovered Teoria's location while spying on Jiart and Lumes' conversation. Jiart then murdered him to ensure his silence.

### dic\_pilot\_LUTEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b002\]
> JP (źródło tłumaczenia): 　ウルガル軍団長（レガトゥス）の一人。 ⏎ 　美しいか否かを全ての価値基準にしており、戦いでもそのこだわりが強い。 ⏎ 　スピードで相手を圧倒する戦術を得意とする。
> EN (odniesienie oficjalne, NIE polski): A Legatus of the Wulgaru.  ⏎  ⏎ Everything she does, including the way she fights, is based on her sense of aesthetics and beauty.  ⏎  ⏎ Her strategies are based on outmaneuvering the enemy with speed.

### dic\_pilot\_LUTEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b003\]
> JP (źródło tłumaczenia): 　オペレーション・イーグルランデッドに参加したチームドーベルマンを圧倒するほどの力を持っておりパトリックを撃墜した。 ⏎ 　最終決戦では、アサギとタマキとアンジュの連係に動きを封じられ、スルガの制御するゴディニオンの主砲に撃墜された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She shot down Patrick at the end of Team Doberman's involvement in Operation Eagle Landed, demonstrating might enough to overwhelm Team Doberman. ⏎  ⏎ In the final battle, she was cornered by a coordinated assault from Asagi, Tamaki, and Ange, before being shot by Suruga operating the Godinion's main cannon. ⏎ 

### dic\_pilot\_RUMES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b004\]
> JP (źródło tłumaczenia): 　ウルガル軍団長（レガトゥス）の一人。 ⏎ 　知略に長ける理性派で、戦線後方からの機動防御を得意とする。 ⏎ 　ウルガル皇族に仕える氏族の出身で、ジアートの密命を遂行する。
> EN (odniesienie oficjalne, NIE polski): A Legatus of the Wulgaru.  ⏎  ⏎ He is logical and mainly concerned with intel. He prefers to fight defensively from the rear guard.  ⏎  ⏎ He hails from a clan that supports the Wulgaru imperial family and is fully loyal to Jiart.

### dic\_pilot\_RUMES\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b005\]
> JP (źródło tłumaczenia): 　地球側の燃料採掘基地であったヴェスタ基地を襲撃し、ＭＪＰに関するデータの入手に成功したことで、グランツェーレ都市学園侵攻のきっかけを生んだ。 ⏎ 　最終決戦では、軍団長不在のクレイン隊とラダ隊を指揮して機動防御と後方支援を担当し、地球側の亜光速誘導弾を迎撃するなど鉄壁の守りを見せた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the attack on the Earth fuel mining facility Vesta Base, he obtained data on the MJP, leading to the attack on Glanzehre Cosmopolitan Academy.  ⏎  ⏎ In the final battle, he took command of the leaderless Klein and Rada squadrons and handled defense and rear support. His defenses were virtually impenetrable and he successfully foiled the Earth's sublight guided missile assault.

### dic\_pilot\_DOLGN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b006\]
> JP (źródło tłumaczenia): 　ウルガルの軍団長（レガトゥス）の一人で、最強の将。 ⏎ 　忠義に厚い武人で、皇帝ガルキエの下で作戦立案と前線での指揮を行う。 ⏎ 　数多の作戦を経験してきており、大部隊を率いた正面突破による戦いを得意とする。
> EN (odniesienie oficjalne, NIE polski): A Legatus of the Wulgaru and its most capable general.  ⏎  ⏎ A fiercely loyal warrior, he strategically advises Emperor Galkie as well as leading operations from the front.  ⏎  ⏎ He is a veteran of many battles. His strategies involve overpowering the enemy with numbers in direct clashes.

### dic\_pilot\_DOLGN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b007\]
> JP (źródło tłumaczenia): 　最終決戦ではゲートの防衛を指揮した。自らも機動兵器で参戦し、スターローズの特攻を阻止するために奔走するが、ブラックシックスとライノスの集中砲火を食らい、配下の機動兵器に回収されて撤退した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He commanded the gate's defense in the final battle. He took the field in his own mobile weapon and fought hard to stop Star Rose's assault, but he came under concentrated fire from Black 6 and Rhinos. He retreated with his unit being towed off by a subordinate's mobile weapon. ⏎ 

### dic\_pilot\_MEI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b008\]
> JP (źródło tłumaczenia): 　幻想生物研究を専攻する大学院生。 ⏎ 　明朗な性格と天才的な頭脳を持つが、どこか抜けている側面もある。 ⏎ 　教授の代理でミサキオク電波観測所を訪れた事をきっかけに、怪獣がもたらす世界の危機に巻き込まれていく。 ⏎ 　有川ユンの開発したコミュニケーション支援ＡＩ「ナラタケ」をウェブ上からインストールした事で誕生した「ペロ２」を相棒に、世界で起きている異変の解明に挑む。
> EN (odniesienie oficjalne, NIE polski): A graduate student specializing in fictional creatures. She is energetic and possesses a brilliant mind, but has her share of what one might call "personal foibles". ⏎  ⏎ Visiting the Misakioku Radio Observatory on behalf of her professor leads to her becoming embroiled in the kaiju threat against the world. ⏎  ⏎ Her partner, Pelops II, is an AI instance created when she downloads Yun Arikawa's communication AI Naratake and installs it on her personal computer. Together, the two of them delve into the mysteries of reality.

### dic\_pilot\_MEI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b009\]
> JP (źródło tłumaczenia): 　幻想生物研究に関するアイデアをペロ２が論文にまとめて公表した事で、葦原研究の第一人者である李博士から共同研究の招待を受ける。 ⏎ 　ペロ２と共に情報収集と分析を行い、葦原の目的を突き止める事に成功した後は、ウパラ研究所のＢＢらと超時間計算機のある場所を目指した。 ⏎ 　紅塵の発生とゴジラによる世界の破局を回避するため、オーソゴナル・ダイアゴナライザーの完成に必要なコードを解析し、破局を食い止める事に多大な貢献をした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After Pelops II organizes her data on imaginary creatures and publishes the resulting paper, she is invited to join Professor Li, who worked on Ashihara's research firsthand. ⏎  ⏎ With Pelops II's help gathering and analyzing data, she uncovers Ashihara's agenda. She then joins BB's staff at the Upala facility and locates the Super Dimension Calculator. She is instrumental in averting the Catastrophe caused by the Red Dust's spread and Godzilla's attack, thanks to decrypting the code necessary to complete the Orthogonal Diagonalizer.

### dic\_pilot\_PERO2\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00a\]
> JP (źródło tłumaczenia): 　コミュニケーション支援ＡＩ「ナラタケ」から生まれた人工知能であり、犬の姿のアバターをしている。 ⏎ 　メイの行動をサポートをする相棒で、彼女のＰＣに住み着いている。 ⏎ 　ペロ２という名は、メイが以前飼っていた犬の「ペロ」に由来する。
> EN (odniesienie oficjalne, NIE polski): An artificial intelligence instance of the communication assistance AI Naratake program. He appears as an avatar of a dog. ⏎  ⏎ He lives in Mei's personal computer and assists her with her goals. The name Pelops II comes from Mei's former pet dog, Pelops.

### dic\_pilot\_PERO2\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00b\]
> JP (źródło tłumaczenia): 　メイとの旅を経て、シヴァ共同事業体が持つ超時間計算機に潜り込み、世界の破局を回避すべく解析を行った。 ⏎ 　その末に「ジェットジャガーを最強にするプロトコル」を発見してジェットジャガー・ユングと一つになり、ゴジラによる破局を食い止める重要な役割を担った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His travels with Mei led it to infiltrate SHIVA.consortium's Super Dimension Calculator, where he analyzed paths to avert the Catastrophe threatening the world. ⏎  ⏎ There, he discovered the protocol to make Jet Jaguar invincible and integrated with Jet Jaguar Yung, becoming the key to stopping Godzilla from bringing the feared Catastrophe about.

### dic\_pilot\_PERO2R\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00c\]
> JP (źródło tłumaczenia): 　コミュニケーション支援ＡＩ「ナラタケ」から生まれた人工知能。 ⏎ 　メイのＰＣに住み着いていたが、シヴァ共同事業体からボディ提供を受けた事で、自力での移動が可能となった。
> EN (odniesienie oficjalne, NIE polski): An artificial intelligence instance of the communication assistance AI Naratake program. ⏎  ⏎ He formerly lived within Mei's personal computer, but was provided a body by SHIVA.consortium which allows him to move around on his own.

### dic\_pilot\_PERO2R\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00d\]
> JP (źródło tłumaczenia): 　メイとの旅を経て、シヴァ共同事業体が持つ超時間計算機に潜り込み、世界の破局を回避すべく解析を行った。 ⏎ 　その末に「ジェットジャガーを最強にするプロトコル」を発見してジェットジャガー・ユングと一つになり、ゴジラによる破局を食い止める重要な役割を担った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His travels with Mei led it to infiltrate SHIVA.consortium's Super Dimension Calculator, where he analyzed paths to avert the Catastrophe threatening the world. ⏎  ⏎ There, he discovered the protocol to make Jet Jaguar invincible and integrated with Jet Jaguar Yung, becoming the key to stopping Godzilla from bringing the feared Catastrophe about.

### dic\_pilot\_YUN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00e\]
> JP (źródło tłumaczenia): 　オオタキファクトリーで働くエンジニア。 ⏎ 　幅広い分野に精通する天才で、ロボット製造や制御ソフトウェア設計、ＡＩ開発等を手掛ける。 ⏎ 　鋭い洞察力の持ち主でもあるが、人との接し方には難がある。 ⏎ 　幽霊屋敷と噂された洋館の調査を機に怪獣との戦いに巻き込まれていく。
> EN (odniesienie oficjalne, NIE polski): An engineer working for Otaki Factory. ⏎  ⏎ A genius skilled in multiple disciplines, he works on robot construction, control software, AI development, and more. ⏎  ⏎ He also has keen observational skills, but struggles when it comes to interacting with other people. After he goes to investigate rumors of a haunted mansion, he finds himself at the forefront of the kaiju conflict.

### dic\_pilot\_YUN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b00f\]
> JP (źródło tłumaczenia): 　自身で開発したコミュニケーション支援ＡＩ「ナラタケ」から生まれた「ユング」をジェットジャガーに移し替え、怪獣の脅威へと立ち向かった。 ⏎ 　メイとは直接面識がないながらもチャットでコミュニケーションを取り、目の前の謎を共に解き明かしていった。 ⏎ 　ゴジラとの最終決戦では、東京駅上空に届くメッセージを受け取るため、ジェットジャガーに同行して世界の破局を防いだ。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Yun transfers "Yung", his instance of his self-developed communication assistance AI Naratake, into Jet Jaguar's frame to fight against the kaiju menace. ⏎  ⏎ He works together with Mei to solve their respective mysteries, entirely by text messages, never once meeting in person. ⏎  ⏎ In the final battle with Godzilla, he receives a message written in the sky over Tokyo and averts the Catastrophe with Jet Jaguar.

### dic\_pilot\_JJAGUAR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b010\]
> JP (źródło tłumaczenia): 　オオタキファクトリーの社長・大滝が開発したロボット。 ⏎ 　「地球を守る」活動を目的に造られた。 ⏎ 　当初は夏祭りで使用される予定だったが、怪獣との戦いをきっかけに戦闘用に改造された。何度かの改造を経て、機体は搭乗型から現在のAI搭載型の無人機となった。 ⏎ 　対話型インターフェースには有川ユンの開発したコミュニケーション支援ＡＩ「ナラタケ」から生まれた「ユング」が組み込まれている。
> EN (odniesienie oficjalne, NIE polski): A robot built by Otaki, the owner of the Otaki Factory. Otaki designed it to defend Earth. ⏎  ⏎ It was originally meant to be exhibited at an upcoming summer festival, but when the kaiju attacked, it was refitted for combat. Several upgrades later, it has evolved from its original manned configuration to the AI-controlled unit it currently operates as. ⏎  ⏎ Its speech interface incorporates Yung, an instance of the Naratake communication assistance AI developed by Yun Arikawa.

### dic\_pilot\_JJAGUAR\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b011\]
> JP (źródło tłumaczenia): 　怪獣との戦いでは、幾度となくオオタキファクトリーや人々を救ってきた。 ⏎ 　「ゴジラ」との最終決戦では、ペロ２が発見した「ジェットジャガーを最強にするプロトコル」により、ペロ２と一体化し、「ジェットジャガーＰＰ」として巨大化して戦った。破局を回避するために必要なオーソゴナル・ダイアゴナライザーのコードが自分自身であると気付くと、それを発動させて世界を守った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Jet Jaguar saves many lives, including those of the Otaki Factory, on a number of occasions. ⏎  ⏎ In the final battle with Godzilla, the protocol to make Jet Jaguar invincible unearthed by Pelops II causes him to merge with Pelops II and transform into the gigantic Jet Jaguar PP to do combat. When he realized that he himself was the Orthogonal Diagonalizer code that alone could prevent the catastrophe, he executed the program and saved the world.

### dic\_pilot\_HABEL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b012\]
> JP (źródło tłumaczenia): 　オオタキファクトリーで働く電子エンジニア。 ⏎ 　趣味は筋トレ。高校時代は「バーベル」というあだ名で呼ばれていた。 ⏎ 　有川ユンの相棒として、共に怪獣の脅威に立ち向かっていく。
> EN (odniesienie oficjalne, NIE polski): An electrical engineer working for Otaki Factory. He works out for fun and was nicknamed "Barbell" in high school. ⏎  ⏎ As Yun Arikawa's work partner, he stands by him in the fight against the kaiju.

### dic\_pilot\_HABEL\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9320b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b013\]
> JP (źródło tłumaczenia): 　オオタキファクトリーのバイクに対ラドン用特殊アンテナを取り付け、人々を怪獣の危害から救うなどして活躍した。 ⏎ 　メイとは高校の同級生であり、ユンのチャット相手「カミムシ」がメイであると気付いた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He was instrumental in saving people from the kaiju by attaching special counter-Rodan antennae to Otaki Factory's motorcycle. ⏎  ⏎ As a former classmate of Mei's, he is the one who realizes that she is the identity of the "Kamimushi" Yun exchanges texts with.

### dic\_pilot\_OTAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b014\]
> JP (źródło tłumaczenia): 　オオタキファクトリーの社長。 ⏎ 　社員のユン達には「おやっさん」と呼ばれている。 ⏎ 　複数の特許を所有する世界的科学者でありながらオカルトの話題に目がなく、「地球を守る」活動に没頭している。 ⏎ 　ジェットジャガーの開発者でもあり、ジェットジャガーが有人機の時には操縦者を務めていた。 ⏎ 　ジェットジャガーがAI搭載型に改造された後もユン達と共に怪獣退治に奔走する。
> EN (odniesienie oficjalne, NIE polski): The CEO of the Otaki Factory. His employees all call him "Mr. O". ⏎  ⏎ Despite being a world-class scientist with a slate of qualifications, he's obsessed with all things paranormal and thinks only of "saving the planet" from such threats. ⏎  ⏎ He originally built Jet Jaguar and served as its pilot when it was a manned machine. After the robot was improved with onboard AI, he continues helping Yun and his staff hunt kaiju.

### dic\_pilot\_SATOMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b016\]
> JP (źródło tłumaczenia): 　オオタキファクトリーの事務。 ⏎ 　ユン達が出動した際は事務所の留守番をしている。 ⏎ 　パンクファッションを好み、私生活は謎に包まれている。 ⏎ 　趣味は水引作成。
> EN (odniesienie oficjalne, NIE polski): The clerical worker at the Otaki Factory. She takes care of duties at the office while the others are out on jobs. ⏎  ⏎ She has a punk fashion sense, and her private life is a mystery. Her hobby is mizuhiki knot-tying.

### dic\_pilot\_SATO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9320b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9320b018\]
> JP (źródło tłumaczenia): 　ミサキオクの主任職員。 ⏎ 　外務省勤務の官僚で、出向により異動してきた。 ⏎ 　鹿子行江の部下にあたる。 ⏎ 　ミサキオクでの警報騒ぎをきっかけに地下に眠る巨大生物の骨や葦原の存在を知り、その謎を追う。
> EN (odniesienie oficjalne, NIE polski): An administrative worker in Misakioku. He is actually in the Ministry of Foreign Affairs, but is currently working under transfer. He reports to Yukie Kanoko. ⏎  ⏎ Through the abnormal alerts in Misakioku, he learns of a massive creature's skeleton underground and of Ashihara's work, and continues pursuing the mystery.

### dic\_pilot\_KANOKO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b000\]
> JP (źródło tłumaczenia): 　外務省官僚で佐藤の上司。 ⏎ 　画期的な新素材であるアーキタイプ出資事業の検討調査のため、葦原の足跡を追っている。 ⏎ 　自衛隊の松原美保とは旧知の仲。
> EN (odniesienie oficjalne, NIE polski): Sato's superior at the Ministry of Foreign Affairs. She is following Ashihara's trail, hoping to discover how to manufacture the revolutionary material known as Archetype. ⏎  ⏎ She is an old friend of Yoshiyasu Matsubara of the JSDF.

### dic\_pilot\_KANOKO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b001\]
> JP (źródło tłumaczenia): 　ドバイで行われたアーキタイプの講演会に出席し、李博士の招きを受けていたメイと接触する。 ⏎ 　その後、ＢＢが手配したオーソゴナル・ダイアゴナライザーを受け取り、日本に輸送した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She meets Mei at the conference on Archetype in Dubai, which Mei had been invited to by Professor Li. ⏎  ⏎ Later, she retrieves the Orthogonal Diagonalizer from BB and transports it to Japan.

### dic\_pilot\_KAITAKE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b002\]
> JP (źródło tłumaczenia): 　自称、独立自営ジャーナリスト。 ⏎ 　怪獣の動向を追っているが、その素性や目的は不明。 ⏎ 　李博士の代理でメイに接触し、ドバイへの招待状を渡した。
> EN (odniesienie oficjalne, NIE polski): A self-styled independent reporter. He follows the kaiju wherever they go, but who he is or what he wants is a mystery. ⏎  ⏎ He approaches Mei with an invitation to Dubai on behalf of Professor Li.

### dic\_pilot\_KAITAKE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b003\]
> JP (źródło tłumaczenia): 　シヴァ共同事業体の人物とも通じており、怪獣に立ち向かうユン達とも何度か接触を繰り返し、インドのウパラの遺跡ではメイ達に命運を託す。 ⏎ 　ゴジラの脅威が去った後、謎の人物らと共に何かを企んでいるようなそぶりを見せた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is also in contact with members of the SHIVA.consortium. He contacts Yun several times in their battles with the kaiju, and ultimately entrusts the future to Mei and her allies at the Upala ruins in India. ⏎  ⏎ After the threat of Godzilla passes, he is seen conspiring with unknown figures.

### dic\_pilot\_REEKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b004\]
> JP (źródło tłumaczenia): 　シヴァ共同事業体の顧問研究員。 ⏎ 　葦原の研究に関する第一人者でもある。 ⏎ 　ウェブ上にアップされたメイの論文を読み、その才能を認めて彼女をドバイへ招待する。
> EN (odniesienie oficjalne, NIE polski): A research advisor who works with the SHIVA.consortium. She was personally involved in Ashihara's research. ⏎  ⏎ She reads Mei's paper on the internet, recognizes her potential, and invites her to Dubai.

### dic\_pilot\_REEKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b005\]
> JP (źródło tłumaczenia): 　葦原から引き継いだロンドンの屋敷にメイを案内し、膨大な研究資料を託す。 ⏎ 　超時間計算機で破局を回避できると信じて行動していたが、その途中でラドンの襲撃に遭い、この世を去った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She brings Mei to the London mansion she inherited from Ashihara and provides her with a staggering amount of research material. ⏎  ⏎ She believed that the Super Dimension Calculator could prevent the Catastrophe until her very end, which came via a Rodan attack. Unfortunately, she didn't live to see the conclusion of the project.

### dic\_pilot\_BB\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b006\]
> JP (źródło tłumaczenia): 　インドに建設されたウパラ研究所の研究部長。 ⏎ 　アーキタイプ研究のスペシャリストであり、葦原の熱烈な支持者でもある。 ⏎ 　優秀だがプライドが高く、自身より賢い人間を嫌う。
> EN (odniesienie oficjalne, NIE polski): The lead researcher at the Upala facility in India. He is an Archetype expert and a zealous supporter of Ashihara's theories. ⏎  ⏎ He is a genius in his own right, but his pride keeps him from getting along with anyone smarter than him.

### dic\_pilot\_BB\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b007\]
> JP (źródło tłumaczenia): 　メイのまとめた論文を元にオーソゴナル・ダイアゴナライザーの実証実験を行った。 ⏎ 　世界の破局が迫る中、独断で世界各地にオーソゴナル・ダイアゴナライザーを送る。自身はメイ達と共に超時間計算機の解析を行い、破局回避に貢献した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He live-tests the Orthogonal Diagonalizer based on Mei's paper. As global Catastrophe looms, he takes it upon himself to provide the Orthogonal Diagonalizer to responders around the world. ⏎  ⏎ He himself accompanies Mei to help with the Super Dimension Calculator's analysis, successfully averting the Catastrophe.

### dic\_pilot\_REENA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b008\]
> JP (źródło tłumaczenia): 　ＢＢの娘。 ⏎ 　父親譲りで肝が据わっており、好奇心が強い。 ⏎ 　研究第一のＢＢの食事作りや身の回りの世話を担っている。
> EN (odniesienie oficjalne, NIE polski): BB's daughter. She has endless pride in her father and plenty of pluck and curiosity. ⏎  ⏎ When BB is engrossed in his research, she takes care of household chores like preparing food.

### dic\_pilot\_REENA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b009\]
> JP (źródło tłumaczenia): 　メイをＢＢまで送り届け、その後は両名と共にウパラの遺跡の最深部へと向かい、破局回避に貢献した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She first brings Mei to BB, and later accompanies both of them into the deepest part of the Upala ruins and helps them avert the Catastrophe.

### dic\_pilot\_MATBR\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b00a\]
> JP (źródło tłumaczenia): 　陸上自衛隊一佐。 ⏎ 　日本の国防の最前線を担っている。 ⏎ 　まじめで実直な性格。 ⏎ 　外務省官僚の鹿子とは旧知の仲で、「美保（みほ）ちゃん」と呼ばれている。
> EN (odniesienie oficjalne, NIE polski): A colonel in the Ground Self Defense Force. He defends Japan on the front lines. ⏎  ⏎ Serious and pragmatic, he is old friends with Kanoko from the Ministry of Foreign Affairs, who affectionately calls him "Miho", a feminine reading of his name.

### dic\_pilot\_TILDA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b00c\]
> JP (źródło tłumaczenia): 　シヴァ共同事業体の代表。 ⏎ 　インドのウパラ研究所を管理下に置いている。 ⏎ 　保守的な考え方の持ち主で、ＢＢとよく対立する。
> EN (odniesienie oficjalne, NIE polski): The chair of the SHIVA.consortium. ⏎  ⏎ She is in charge of the Upala facility in India. ⏎  ⏎ Her conservative approach often puts her at odds with BB.

### dic\_pilot\_TILDA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b00d\]
> JP (źródło tłumaczenia): 　オーソゴナル・ダイアゴナライザーの完成を優先し、破局への直接的な対応は二の次にした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She prioritizes the completion of the Orthogonal Diagonalizer over actually dealing with the impending Catastrophe.

### dic\_pilot\_GAUMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b00e\]
> JP (źródło tłumaczenia): 　自称「怪獣使い」を名乗る男。 ⏎ 　ある人を捜しており、その人物から託された竜のオブジェを持ち歩いていた。 ⏎ 　行動は破天荒だが、真面目な性格をしており、義理人情に厚い。 ⏎ 　怪獣使いとしての力は現在は失われていて、空腹で倒れていた所を蓬に助けられた。 ⏎ 　街に現れた怪獣に対して竜のオブジェから生まれたダイナゼノンを駆り、その場に居合わせた蓬、夢芽、暦を戦いに巻き込んでいく。 ⏎ 　ダイナゼノンのメインの操縦者を務め、分離時には脚部となる潜水艦型の「ダイナダイバー」を担当する。 ⏎ 　普段は河川敷の橋の下に住んでおり、アルバイトを掛け持ちしている。
> EN (odniesienie oficjalne, NIE polski): A man who claims to be a "kaiju user". He's looking for someone, and is never without a sculpture of a dragon that they left to him. ⏎  ⏎ His rough manner belies an unyielding dedication to duty and honor. Yomogi found him starving and having lost his kaiju user powers. ⏎  ⏎ He pilots Dynazenon, the robot formed from the dragon sculpture, recruiting Yomogi, Yume, and Koyomi when they happened to be nearby. He is the main pilot of the combined Dynazenon, and when it's not combined, he pilots the Dyna Diver, the submarine that forms its legs. ⏎  ⏎ Otherwise, he lives under the bridge over the river and makes his living through part-time jobs.

### dic\_pilot\_GAUMA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b00f\]
> JP (źródło tłumaczenia): 　五千年前、怪獣使いを排除しようとした国に反抗した怪獣優生思想のメンバーと対立し、相打ちとなって死亡するが、怪獣の力により現代によみがえった。 ⏎ 　将来を誓い合った「姫」を捜しているが、最後まで出会う事は叶わなかった。 ⏎ 　最終決戦を前に不調となり、ダイナゼノンに乗る事も出来ない状態となるが、全ての決着をつけるべく戦う事を選ぶ。 ⏎ 　しかしガギュラとの最後の戦いの後、肉体は限界を迎えて蓬達の前から姿を消した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ 5,000 years ago, he sided against the Kaiju Club when their country sought to eliminate all kaiju users. Neither side survived their final battle, but Gauma was revived by a kaiju's power in the present. ⏎  ⏎ He is looking for his princess, with whom he promised their future but never met in the end. ⏎ As the final battle approached, his condition worsened to the point that he could no longer pilot Dynazenon, but he decided to fight anyway to settle his scores. ⏎  ⏎ However, after finally defeating Gagula, his body gave out, and he vanished before the team's eyes.

### dic\_pilot\_YOMOGI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b010\]
> JP (źródło tłumaczenia): 　都立フジヨキ台高等学校に通う高校一年生。 ⏎ 　温和な性格で友人が多い。 ⏎ 　母と祖母の三人暮らしをしているが、家から自立したいと考えており、スーパーマーケット「ゆりマート」でアルバイトをしている。 ⏎ 　河川敷の橋の下、空腹で倒れているガウマを助けた事をきっかけに怪獣との戦いへと巻き込まれていく。 ⏎ 　ダイナゼノン分離時には竜人型の「ダイナソルジャー」を操縦する。
> EN (odniesienie oficjalne, NIE polski): A freshman at Fujiyokidai High School. His approachable nature has earned him lots of friends. ⏎  ⏎ He lives with his mother and grandmother, but yearns for independence. To this end, he works a part-time job at the Yuri Mart supermarket. ⏎  ⏎ He finds Gauma starving under a bridge and helps him, which leads to him fighting against the kaiju. When Dynazenon isn't combined, he pilots the draconic humanoid robot Dyna Soldier.

### dic\_pilot\_YOMOGI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b011\]
> JP (źródło tłumaczenia): 　怪獣との戦いの中で自らに怪獣使いの素質がある事に気付き、最終決戦ではその力でガギュラの攻撃をそらして攻撃のチャンスを生み出した。 ⏎ 　クラスメイトである夢芽に対して徐々に想いを寄せていき、最終決戦前にその気持ちを告白し、全ての戦いの後には互いを呼び捨てで呼び合う関係まで発展した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the ongoing battles against kaiju, he discovers kaiju user potential in himself. In the final battle, he uses his power to prevent Gagula from landing a hit, giving the team an opening to strike. ⏎  ⏎ He gradually develops feelings for Yume, who is in his class. He reveals those feelings during the final battle, and afterwards, the two grow even closer.

### dic\_pilot\_YUME\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b012\]
> JP (źródło tłumaczenia): 　蓬のクラスメイト。 ⏎ 　男子生徒と待ち合わせの約束をして、それをすっぽかす行為を続けていた。 ⏎ 　小学生の時に姉・香乃を亡くした過去を抱え、生前の姉が持っていた知恵の輪をいつも携帯している。 ⏎ 　蓬とも会う約束をし、それを破るつもりであったが、それをガウマにとがめられ、さらに怪獣が現れた事をきっかけに戦いへ巻き込まれていく。 ⏎ 　ダイナゼノン分離時には、ダイナゼノンの胸部・翼を構成する「ダイナウイング」の操縦を担当する。
> EN (odniesienie oficjalne, NIE polski): Yomogi's classmate. ⏎  ⏎ She has a habit of setting up meetings with boys only to leave them hanging. ⏎  ⏎ When she was in elementary school, she lost her sister Kano. She always carries an ankh puzzle that used to belong to her sister. ⏎  ⏎ She invited Yomogi to a meeting she meant to skip, but when Gauma tracked her down in a rage and then a kaiju attacked, she was forced to fight along with them. When Dynazenon isn't combined, she pilots the Dyna Wing, which forms its chest and wings.

### dic\_pilot\_YUME\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b013\]
> JP (źródło tłumaczenia): 　姉の死の真相を確かめるべく行動していく中で怪獣の力によって姉の過去と気持ちを知り、前へ踏み出す決意を固める。 ⏎ 　最終決戦後は蓬と両想いになり、少しずつではあるが、クラスにも馴染んでいった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ As she digs into what really happened to her sister, a kaiju's power reveals the whole story and how Kano felt. This allows her to choose to move past it. ⏎  ⏎ She returns Yomogi's feelings after the final battle, and also begins to open up to the rest of the class.

### dic\_pilot\_KOYOMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b014\]
> JP (źródło tłumaczenia): 　無職生活を続けている青年。 ⏎ 　やりたい事もなく、怠惰な日々を送っていた。 ⏎ 　口数は少なく、物静かな性格。 ⏎ 　部屋に入り浸っていた従妹のちせと怪獣騒ぎの見物に訪れていた所をガウマに巻き込まれ、怪獣との戦いに協力していく。
> EN (odniesienie oficjalne, NIE polski): A longtime shut-in. He leads a lazy life without any goals to pursue. ⏎  ⏎ He speaks very little and doesn't stick out. When he left his room (a rare occasion) with his cousin Chise to witness a kaiju attack, Gauma forcibly recruited him to fight by his side.

### dic\_pilot\_KOYOMI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b015\]
> JP (źródło tłumaczenia): 　蓬のアルバイト先の稲本とは中学の同級生であり、当時の行動を今でも引きずっていたが、偶然再会した事を機に酒を飲み交わす。 ⏎ 　また、自らと同様にやりたい事のない怪獣優生思想のムジナと心を通わせるが、敵対する彼女との関係がそれ以上進展する事はなかった。 ⏎ 　しかし、怪獣との戦いを通じて過去と向き合った事で精神的に成長し、戦いの終わった後は髪を切り、就職活動を始める。その結果、稲本の夫の会社で働く事が決まった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Yomogi's boss, Inamoto-san, was in his class in middle school. His regrets from that time still haunt him, but when they happen to meet again, they share a drink and reminisce. ⏎  ⏎ He and the Kaiju Club member Mujina share a connection since neither of them has a strong drive, but being on opposite sides ensures their relationship never develops. ⏎  ⏎ In the course of fighting the kaiju, he manages to face his past regrets and move forward. After their final battle, he cuts his hair and starts looking for a job, ultimately finding one at the company where Inamoto-san's husband works.

### dic\_pilot\_CHISE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b016\]
> JP (źródło tłumaczenia): 　暦の従妹にあたる中学生。 ⏎ 　学校には行かず、暦の部屋に入り浸っている。 ⏎ 　ダイナゼノンの操縦者ではないが、ガウマ隊の一員としての想いは人一倍強い。 ⏎ 　最初の怪獣との戦いで、白い石のような物を拾う。
> EN (odniesienie oficjalne, NIE polski): Koyomi's middle-schooler cousin. She doesn't actually attend school, preferring to stay with Koyomi in his room during the day. ⏎  ⏎ Despite not being chosen as a Dynazenon pilot, she is the most dedicated of Gauma's ragtag crew. ⏎  ⏎ She finds a small white stone just after their first battle.

### dic\_pilot\_CHISE\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b017\]
> JP (źródło tłumaczenia): 　以前に通っていた学校で孤独や疎外感に苦しんでいた過去を持つ。 ⏎ 　ゼンタングルアートを描くのが趣味で、左腕のアームカバーの下にはボディペイントが描かれている。 ⏎ 　以前拾った怪獣の種から生まれたゴルドバーンと心を通わせ、怪獣との戦いでも活躍するようになる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She struggled with isolation and loneliness at her old school. She's fond of Zentangle artwork and has a design painted underneath the wrappings around her left arm. ⏎  ⏎ When Goldburn emerges from the kaiju seed she found, she finds a friend as well as a way to help fight the kaiju.

### dic\_pilot\_GLDBRN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b018\]
> JP (źródło tłumaczenia): 　ちせが拾った種から成長した怪獣。 ⏎ 　ちせと心を通わせ、ガウマ達の手助けをする。 ⏎ 　口から吐く金色の光は物体の大きさを変え、融合させる力がある。
> EN (odniesienie oficjalne, NIE polski): The kaiju born from the seed found by Chise. ⏎  ⏎ It understands her feelings and helps Gauma in battle. ⏎  ⏎ The golden light it breathes from its mouth can alter the size of objects and fuse them together.

### dic\_pilot\_GLDBRN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b019\]
> JP (źródło tłumaczenia): 　カイゼルグリッドナイトに合体時は前面装甲と兜を構成する。 ⏎ 　単独でシールド形態に変形する事も可能でダイナゼノンのピンチを救う事もあった。 ⏎ 　最後の戦いが終わった後は、グリッドナイト同盟と共にフジヨキ台を去って行った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It forms Kaiser Gridknight's front armor and helmet. Uncombined, it can also transform into a shield, in which form it saved Dynazenon from near defeat. ⏎  ⏎ It left Fujiyokidai with the Gridknight Alliance after the final battle.

### dic\_pilot\_JUGA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b01a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b01a\]
> JP (źródło tłumaczenia): 　怪獣優生思想のメンバーで怪獣使いの一人。 ⏎ 　真面目で冷静な性格。 ⏎ 　五千年前は先輩であったガウマに憧れていたが、現在は怪獣使いとして彼を越えようと意気込み、戦いを挑み続ける。 ⏎ 　二足歩行の怪獣を操る適性がある。
> EN (odniesienie oficjalne, NIE polski): A kaiju user in the Kaiju Club. Calm, composed, and earnest. ⏎  ⏎ 5,000 years ago, he joined the group after Gauma and had nothing but respect for him. Now, he wants to surpass the kaiju user Gauma once was, and challenges him relentlessly to prove it. ⏎  ⏎ He has an affinity for controlling bipedal kaiju.

### dic\_pilot\_JUGA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b01b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b01b\]
> JP (źródło tłumaczenia): 　ダイナゼノンを倒すのではなく、味方につけた方がよいと考え、蓬に接近した事もあった。 ⏎ 　最後の戦いでガウマ達に敗れ、消息不明となる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He approaches Yomogi directly, hoping to recruit Dynazenon to their cause, rather than defeat it in battle. ⏎  ⏎ He went missing after losing to the Dynazenon team in the final battle.

### dic\_pilot\_ONIJA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9360b01c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b01c\]
> JP (źródło tłumaczenia): 　怪獣優生思想のメンバーで怪獣使いの一人。 ⏎ 　好戦的で荒々しい性格。 ⏎ 　怪獣の力は人間を殺すためにあると考えている。 ⏎ 　他のメンバー以上に仲間意識が強く、怪獣優生思想を裏切ったガウマを憎んでいる。 ⏎ 　二足歩行で尻尾を持つ怪獣を操る適性がある。
> EN (odniesienie oficjalne, NIE polski): A kaiju user in the Kaiju Club. He has a rough demeanor and is always itching for a fight. ⏎  ⏎ He believes that the power of kaiju is for killing people. He is deeply loyal to the group and harbors a deep grudge against Gauma for betraying the Kaiju Club. ⏎  ⏎ He has an affinity for controlling bipedal, tailed kaiju.　

### dic\_pilot\_ONIJA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9360b01d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9360b01d\]
> JP (źródło tłumaczenia): 　ダイナゼノンに度重なる敗北を喫し、やる気を出したムジナと意気投合した。 ⏎ 　怪獣が出現しなくなった後は怪獣なしで人類抹殺を考えたが、出来るはずもなく、最後の戦いでガウマ達に敗れて消息不明となる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Bitter from all his losses to Dynazenon, he teams up with Mujina, who had found her fighting spirit. ⏎  ⏎ When the kaiju stopped appearing, he considered trying to exterminate humanity without their help, but gave up on the idea. He goes missing after losing to the Dynazenon team in the final battle.

### dic\_pilot\_MUZINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b000\]
> JP (źródło tłumaczenia): 　怪獣優生思想のメンバーで怪獣使いの一人。 ⏎ 　やりたい事がなく、他のメンバーが決めた事に従う性格。 ⏎ 　仲間と共に行動しているものの、怪獣を操る事やガウマとの戦いについてはやる気がない。 ⏎ 　四足歩行の怪獣を操る適性がある。
> EN (odniesienie oficjalne, NIE polski): A kaiju user in the Kaiju Club. Not having any goals of her own, she tends to go along with whatever the group decides. ⏎  ⏎ Despite always being with the group, she shows no real interest in controlling kaiju or fighting Gauma. She has an affinity for controlling quadrupedal kaiju.

### dic\_pilot\_MUZINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b001\]
> JP (źródło tłumaczenia): 　自らと似た一面を持つ暦と接触した事で自分には怪獣しかないと気付かされ、戦いに意欲を見せるようになる。その際はこれまでとは打って変わって好戦的になった。 ⏎ 　最後の戦いでガウマ達に敗れ、消息不明となる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Finding a kindred spirit in Koyomi makes her realize that kaiju are all she has in life, and she begins displaying very uncharacteristic aggression and bloodlust. ⏎  ⏎ She goes missing after losing to the Dynazenon team in the final battle.

### dic\_pilot\_SHIZM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b002\]
> JP (źródło tłumaczenia): 　怪獣優生思想のメンバーで怪獣使いの一人。 ⏎ 　落ち着いた性格だが、その意図を計りかねるミステリアスな言動が多い。 ⏎ 　怪獣の声を聴く能力があり、怪獣がもたらす自由と解放だけを目指している。
> EN (odniesienie oficjalne, NIE polski): A kaiju user in the Kaiju Club. ⏎  ⏎ His manner is calm and quiet, but his actions are mysterious and often baffling. ⏎  ⏎ He can hear the voices of kaiju, and seeks the liberation he believes they can bring.

### dic\_pilot\_SHIZM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b003\]
> JP (źródło tłumaczenia): 　フジヨキ台高校に交換留学生として潜入し、好奇心から蓬と夢芽に接近した。 ⏎ 　その体内に怪獣を宿しており、最終決戦では自らにインスタンス・ドミネーションをかけ、ガギュラと一体化した。怪獣優生思想のメンバーを取り込んだ事でさらなるパワーアップを果たすも、ガウマ達に敗れ、消息不明となる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He later infiltrates Fujiyokidai High School, posing as a transfer student, and approaches Yomogi and Yume out of curiosity. ⏎  ⏎ He hosts a kaiju within his body. In the final battle, he used Instance Domination on himself and fused with Gagula. Gagula then powered up by absorbing the rest of the Kaiju Club but was still defeated by Gauma and the others, after which Sizumu went missing.

### dic\_pilot\_KNIGHT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b004\]
> JP (źródło tłumaczenia): 　グリッドナイトに変身する青年。 ⏎ 　２代目と共にグリッドナイト同盟を結成し、怪獣の脅威から世界を守るために戦っている。 ⏎ 　無愛想であり、突っかかってくるガウマに対しては辛辣な言葉と鉄拳を放った。
> EN (odniesienie oficjalne, NIE polski): A young man who transforms into Gridknight. He and The 2nd form the Gridknight Alliance, which fights to protect worlds from the menace of kaiju. ⏎  ⏎ His standoffish attitude has led him to exchange barbed banter as well as physical blows with Gauma.

### dic\_pilot\_KNIGHT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b005\]
> JP (źródło tłumaczenia): 　当初はガウマ隊を否定していたが、後にその存在を認めて共闘するようになる。 ⏎ 　全ての戦いの後、次の使命のために２代目と共にフジヨキ台から去っていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His initial disdain for Gauma's team eventually gives way to acceptance and alliance. ⏎  ⏎ After the final battle, he left Fujiyokidai with The 2nd to pursue their next mission.

### dic\_pilot\_GRIDKT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b006\]
> JP (źródło tłumaczenia): 　ナイトが変身した姿。 ⏎ 　ダイナゼノンとゴルドバーンと合体する事で、カイゼルグリッドナイトになる事が出来る。
> EN (odniesienie oficjalne, NIE polski): The form Knight transforms into. He can further combine with Dynazenon and Goldburn into Kaiser Gridknight.

### dic\_pilot\_KGRIDKT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b008\]
> JP (źródło tłumaczenia): 　ゴルドバーンの力によって、グリッドナイトがダイナゼノン、ゴルドバーンと合体した姿。
> EN (odniesienie oficjalne, NIE polski): Gridknight's form after combining with Dynazenon and Goldburn using the latter's powers.

### dic\_pilot\_NIDAI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b00a\]
> JP (źródło tłumaczenia): 　グリッドナイト同盟のメンバー。 ⏎ 　ナイトと共に行動し、怪獣の脅威から様々な世界を守るべく戦う。 ⏎ 　明るく朗らかな性格。 ⏎ 　ライブバトンと呼ばれるバトンを持ち歩いており、物体を修復するフィクサービームを使用する権限を持っている。
> EN (odniesienie oficjalne, NIE polski): A member of the Gridknight Alliance. She travels with Knight to protect worlds from the kaiju menace. She's always bright and cheery. ⏎  ⏎ She carries a stick called the Live Baton and has permissions to use the Fixer Beam to repair objects.

### dic\_pilot\_NIDAI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b00b\]
> JP (źródło tłumaczenia): 　全ての戦いの後、次の使命のためにナイトと共にフジヨキ台から去っていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the final battle, she left Fujiyokidai with Knight to pursue their next mission.

### dic\_pilot\_INAMT\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b00c\]
> JP (źródło tłumaczenia): 　蓬のアルバイト先のスーパーマーケット「ゆりマート」のバイトリーダー。 ⏎ 　既婚者であり、結婚を機に地元のフジヨキ台に戻って暮らしている。
> EN (odniesienie oficjalne, NIE polski): Yomogi's supervisor at his part-time job at the Yuri Mart supermarket. ⏎  ⏎ She returned to Fujiyokidai, her hometown, when she got married.

### dic\_pilot\_INAMT\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b00d\]
> JP (źródło tłumaczenia): 　暦とは中学の同級生で、偶然の再会で暦と飲み明かす。 ⏎ 　中学時代、一万円札が大量に入ったバッグを見つけた秘密を暦と共有する。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She attended middle school with Koyomi and invites him for a catch-up drink when they happen to cross paths. ⏎  ⏎ The two share a secret: in middle school, they found a bag stuffed full of 10,000 yen bills.

### dic\_pilot\_MEIDZ\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b00e\]
> JP (źródło tłumaczenia): 　夢芽の友人。 ⏎ 　温厚な性格で、夢芽からは「お母さん」と呼ばれている。 ⏎ 　趣味はカメラ。
> EN (odniesienie oficjalne, NIE polski): Yume's closest friend. Her caring nature leads Yume to jokingly call her "Mom". ⏎  ⏎ Her hobby is photography.

### dic\_pilot\_YOMOMUM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b010\]
> JP (źródło tłumaczenia): 　蓬の母親。 ⏎ 　蓬が小学三年生の時に夫と離婚し、現在は実家で蓬と母（蓬にとっては祖母）と三人で暮らしている。 ⏎ 　恋人がおり、蓬にも紹介している。
> EN (odniesienie oficjalne, NIE polski): Yomogi's mother. She and his father divorced when he was a third grader, and she now lives in her childhood home with Yomogi and her mother, Yomogi's grandmother. ⏎  ⏎ She is seeing a man who she has introduced to Yomogi.

### dic\_pilot\_KANO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b012`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b012\]
> JP (źródło tłumaczenia): 　夢芽の姉。
> EN (odniesienie oficjalne, NIE polski): Yume's older sister.

### dic\_pilot\_MIRIARIA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b014`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b014\]
> JP (źródło tłumaczenia): 　アークエンジェルのクルーで通信管制を担当。１８歳。 ⏎ 　元は一学生にすぎなかったが、巻き込まれる形で戦闘に参加した。 ⏎ 　戦場で恋人トールを失った事から、一時はコーディネイターへの憎しみに囚われていたが、精神的に成長し、終戦まで戦い抜いた。 ⏎ 　大戦終結後は戦場カメラマンとして世界各地を旅していた。　　　　　 ⏎ 　アークエンジェルが行動を開始した際には共に戦うべく再び艦に乗り込み、カガリが代表の座に戻った後には正式にオーブ軍に参加した。
> EN (odniesienie oficjalne, NIE polski): The Archangel's communications officer. Age 18. ⏎  ⏎ She was an ordinary student before the war found her and forced her into fighting. ⏎  ⏎ The death of her partner Tolle in combat drove her to despise all Coordinators for some time, but she moved past it and fought throughout the war. ⏎  ⏎ Afterwards, she traveled the world as a photographer. ⏎  ⏎ When the Archangel returned to battle, she boarded it to fight alongside its crew. She officially joined the Orb Forces when Representative Cagalli returned to office.

### dic\_pilot\_MHERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b016`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b016\]
> JP (źródło tłumaczenia): 　日本古来の忍者を源流とする特殊戦闘員「ＮＩＮＪＡ（New Infinity Neuron - Japanese Assassin）であり、ＮＩＮＪＡ集団「特戦隠密・朧」の頭領。 ⏎ 　２１歳、男性。 ⏎ 　任務の遂行を最優先し、そのためならば一切の私情を捨てる覚悟の持ち主。任務遂行に必要ならば、自分の存在すら偽る事が出来る。それ故に周囲からは冷静沈着、冷酷非情と思われている。 ⏎ 　朧史上、最強のＮＩＮＪＡとされ、忍技・忍牙の腕だけでなく、機動忍鎧の操縦においても圧倒的な力を見せる。 ⏎ 　完全に自分の肉体を精神でコントロールしており、あらゆる毒物に対しても高い耐性を持っている。
> EN (odniesienie oficjalne, NIE polski): A special forces operative called a NINJA (New Infinity Neuron Japanese Assassin), based on the ancient Japanese ninja, and leader (or "head") of the Special Stealth Forces NINJA group known as Haze. ⏎  ⏎ Age 21, male. ⏎  ⏎ He puts the mission first and doesn't allow his feelings to interfere with the job; he'll even go so far as to adopt completely false identities to finish a mission. As a result, he's sometimes considered cold and even heartless by those around him. ⏎  ⏎ He is the strongest NINJA in the history of Haze. He is not only skilled at Ninja Arts and Ninja Fangs but possesses an amazing mastery of Mobile Armored Ninja piloting. ⏎  ⏎ He also has complete mental control over his body, which gives him a tremendous resistance to poisons and toxins.

### dic\_pilot\_MHERO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b017\]
> JP (źródło tłumaczenia): 　本名は八神ヤイチ。 ⏎ 　八神テツロウの息子であり、八神ヤチヨ（月ノ輪フォルテ）とエチカ・Ｙ・フランバーネットの兄である。 ⏎ 　幼少の頃に八神テツロウによりエチカを守るためにＮＩＮＪＡとなる事を命じられる。発端は自分の意思ではなかったものの、そこに一切の迷いはなく、妹・エチカの存在は生きる意味となった。 ⏎ 　今まで味わった事のなかった感情やエチカに振り回されながら、仲間と共にエーアデントでの任務を楽しんでいる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His real name is Yaichi Yagami. ⏎  ⏎ He is the son of Tetsuro Yagami, and the older brother of both Yachiyo Yagami (Forte Tsukinowa) and Echika Y. Franburnett. ⏎  ⏎ He was commanded by Tetsuro to become a NINJA from a young age, in order to protect his sister. Although he did not volunteer for this mission, he nonetheless took it up without hesitation and now lives to keep Echika safe. ⏎  ⏎ As he goes about his life aboard the A. Advent with his newfound friends, he finds he enjoys this mission and he experiences new emotions...all while being dragged about by Echika's (well-meaning) whims.

### dic\_pilot\_MHERO\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93a0b018`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b018\]
> JP (źródło tłumaczenia): 　日本古来の忍者を源流とする特殊戦闘員「ＮＩＮＪＡ（New Infinity Neuron - Japanese Assassin）であり、ＮＩＮＪＡ集団「特戦隠密・朧」の頭領。 ⏎ 　２１歳、男性。 ⏎ 　任務の遂行を最優先し、そのためならば一切の私情を捨てる覚悟の持ち主。任務遂行に必要ならば、自分の存在すら偽る事が出来る。それ故に周囲からは冷静沈着、冷酷非情と思われている。 ⏎ 　朧史上、最強のＮＩＮＪＡとされ、忍技・忍牙の腕だけでなく、機動忍鎧の操縦においても圧倒的な力を見せる。 ⏎ 　完全に自分の肉体を精神でコントロールしており、あらゆる毒物に対しても高い耐性を持っている。
> EN (odniesienie oficjalne, NIE polski): A special forces operative called a NINJA (New Infinity Neuron Japanese Assassin), based on the ancient Japanese ninja, and leader (or "Head") of the Special Stealth Forces NINJA group known as Haze. ⏎  ⏎ Age 21, male. ⏎  ⏎ He puts the mission first and doesn't allow his feelings to interfere with the job; he'll even go so far as to adopt completely false identities to complete a mission. As a result, he's sometimes considered cold and even heartless by those around him. ⏎  ⏎ He is the strongest NINJA in the history of Haze, not only skilled at Ninja Arts and Ninja Fangs, but possessed of an amazing mastery of Mobile Armored Ninja piloting. ⏎  ⏎ He also has complete mental control over his body, which gives him a tremendous resistance to poisons and toxins.

### dic\_pilot\_MHERO\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93a0b019`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93a0b019\]
> JP (źródło tłumaczenia): 　本名は八神ヤイチ。 ⏎ 　八神テツロウの息子であり、八神ヤチヨ（月ノ輪フォルテ）とエチカ・Ｙ・フランバーネットの兄である。
> EN (odniesienie oficjalne, NIE polski):  ⏎ His real name is Yaichi Yagami. ⏎ He is Tetsuro Yagami's son, and the older brother of both Yachiyo Yagami (a.k.a. Forte Tsukinowa) and Echika Y. Franburnett.

### dic\_pilot\_FHERO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b000\]
> JP (źródło tłumaczenia): 　日本古来の忍者を源流とする特殊戦闘員「ＮＩＮＪＡ（New Infinity Neuron - Japanese Assassin）であり、ＮＩＮＪＡ集団「特戦隠密・朧」の隊員。 ⏎ 　１７歳、女性。 ⏎ 　ＮＩＮＪＡとしては経験が浅く、全てにおいて未熟ではあるが、持ち前のポジティブな性格で困難へと立ち向かっていく。素質は見るべきものがあるものの、それを引き出す経験と技量が不足しており、単独での任務遂行は不安視されていたが、頭領である月ノ輪クロスの決定によりエチカ・Ｙ・フランバーネット護衛任務に就く。
> EN (odniesienie oficjalne, NIE polski): A special forces operative called a NINJA (New Infinity Neuron Japanese Assassin), based on the ancient Japanese ninja, and a member of the Special Stealth Forces NINJA group known as Haze. ⏎  ⏎ Age 17, female. ⏎  ⏎ While inexperienced as a NINJA (and by most measures, a bit immature for her age in general), her go-getting, positive attitude helps her endure and challenge the trials and tribulations she regularly faces. Despite having considerable talent, she lacks the skill and experience to make use of them, which makes her a risk to deploy on missions alone. She nonetheless was assigned to the task of guarding Echika Y. Franburnett on the decision of the head of Haze, Cross Tsukinowa.

### dic\_pilot\_FHERO\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b001\]
> JP (źródło tłumaczenia): 　本名は八神ヤチヨ。 ⏎ 　八神テツロウの娘であり、八神ヤイチ（月ノ輪クロス）の妹にして、エチカ・Ｙ・フランバーネットの姉である。 ⏎ 　幼少の頃、兄クロスを追ってＮＩＮＪＡに志願するが、当時から能力は疑問視されていた。しかし、兄と共に妹・エチカを守る事を心の支えとして、過酷な修行をクリアし、今ではそれが生きる意味となっている。 ⏎ 　そういった過去や葛藤を周囲には見せない事を美学にエーアデントでの任務とエチカとの生活を楽しんでいる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Her real name is Yachiyo Yagami. ⏎  ⏎ She is the daughter of Tetsuro Yagami, and younger sister of Yaichi Yagami (Cross Tsukinowa) and older sister of Echika Y. Franburnett. ⏎  ⏎ Unlike Cross, she strenuously volunteered to become a NINJA in her youth, but her aptitude for NINJA-hood has always been suspect. Nonetheless, her devotion to protecting her siblings sustained her through the harsh training needed and has become her entire reason to live. ⏎  ⏎ She enjoys her life aboard the A. Advent with Echika, fulfilling her mission and priding herself in keeping her pain and her past a secret from those around her.

### dic\_pilot\_FHERO\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b002\]
> JP (źródło tłumaczenia): 　日本古来の忍者を源流とする特殊戦闘員「ＮＩＮＪＡ（New Infinity Neuron - Japanese Assassin）であり、ＮＩＮＪＡ集団「特戦隠密・朧」の隊員。 ⏎ 　１７歳、女性。 ⏎ 　ＮＩＮＪＡとしては経験が浅く、全てにおいて未熟ではあるが、持ち前のポジティブな性格で困難へと立ち向かっていく。
> EN (odniesienie oficjalne, NIE polski): A special forces operative called a NINJA (New Infinity Neuron Japanese Assassin), based on the ancient Japanese ninja, and a member of the Special Stealth Forces NINJA group known as Haze. ⏎  ⏎ Age 17, female. ⏎  ⏎ While inexperienced as a NINJA (and by most measures, a bit immature for her age in general), her go-getting, positive attitude helps her endure and challenge the trials and tribulations she regularly faces.

### dic\_pilot\_FHERO\_S\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b003\]
> JP (źródło tłumaczenia): 　本名は八神ヤチヨ。 ⏎ 　八神テツロウの娘であり、八神ヤイチ（月ノ輪クロス）の妹にして、エチカ・Ｙ・フランバーネットの姉である。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Her real name is Yachiyo Yagami. ⏎  ⏎ She is Tetsuro Yagami's daughter, the younger sister of Yaichi Yagami (a.k.a. Cross Tsukinowa), and the older sister of Echika Y. Franburnett.

### dic\_pilot\_ECHIKA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b004\]
> JP (źródło tłumaczenia): 　八神市の地主の娘。 ⏎ 　１４歳、女性。 ⏎ 　父母を亡くしており、八神市の広大な屋敷で家庭教師のアニーナと９９人のメイドと共に暮らしていた。学校には通っていなかったが、将来、統治者となるべく様々な教育をアニーナから施されており、それは政治・経済の分野に止まらず、軍事の範囲にまでも及んでいた。 ⏎ 　性格は生真面目で何事にも熱心であり、さらに負けず嫌いでもある。他人と接触する機会が少なかったため、コミュニケーションの取り方が不器用であるが、親しい相手には年相応に子供らしい所も見せる。
> EN (odniesienie oficjalne, NIE polski): The daughter of Yagami City's primary landholder. ⏎  ⏎ Age 14, female. ⏎  ⏎ Her mother died when she was young, leaving her to live alone in an enormous mansion in Yagami City together with her teacher Annina and her ninety-nine maids. While she never attended a formal school, she's received a wide variety of lessons from Annina to prepare her to be the next governor of Yagami City. This has left her well educated in not just politics and economics but even military affairs. ⏎  ⏎ She takes everything she does seriously and throws herself into it, and hates making a poor showing of herself. While she can be somewhat clumsy when communicating with others due to her lack of experience, she acts like the young girl she is at heart when she is with the people she's grown close to.　

### dic\_pilot\_ECHIKA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b005\]
> JP (źródło tłumaczenia): 　機動要塞都市エーアデントの所有者となり、そのまま選挙により、機動都市国家エーアデントの代表に選出される。 ⏎ 　その出自は超人類イザナのコピーであり、八神テツロウやクロス、フォルテと血のつながりはない。 ⏎ 　超人類覚醒体としてヴィルを制御する力を持つが、その能力を封印し、エーアデントの住民達の精神エネルギーを束ねて戦っていった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She is the legal owner of the Mobile Fortification A. Advent, and is also the legally elected representative of the mobile city-state. ⏎  ⏎ In truth, she is a copy of the Superhuman Izana, and has no blood relationship to Tetsuro Yagami, Cross, or Forte. ⏎  ⏎ As a fully awakened Superhuman, she has the power to control the Willforce but has locked that ability away, instead choosing to wield the mental energy of the A. Advent's citizens to battle on their behalf.

### dic\_pilot\_ANINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b006\]
> JP (źródło tłumaczenia): 　エチカの家庭教師。 ⏎ 　２７歳、女性。 ⏎ 　３年前から屋敷に住み込み、統治に必要な各種の教育をエチカに施してきた。 ⏎ 　元はエチカの父親である科学者・八神テツロウの助手であり、八神が事故で死亡した後、その遺言によりエチカの家庭教師となった。 ⏎ 　博識であると同時に思慮深く、常に微笑みを絶やさない穏やかな女性であるが、場の空気に対しては無頓着であり、時に的外れな言動を見せる事もある。しかし、エチカを誰よりも理解しており、彼女からも全幅の信頼を寄せられている。
> EN (odniesienie oficjalne, NIE polski): Echika's live-in tutor. ⏎  ⏎ Age 27, female. ⏎  ⏎ For the last three years she has lived in the Franburnett mansion, teaching Echika everything she needs in order to govern. ⏎  ⏎ She was formerly an assistant to Echika's father, the scientist Tetsuro Yagami, and began to live with Echika as her home tutor under the terms of Dr. Yagami's will. ⏎  ⏎ She is a widely-studied and deeply considerate person who maintains a calm, mild smile at all times, but she can also be very disconnected from the people around her in ways that lead her to be wildly off the mark at times. Regardless, she knows Echika better than anyone else and has earned Echika's complete and utter trust.

### dic\_pilot\_ANINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b007\]
> JP (źródło tłumaczenia): 　エーアデント起動後は艦内ステータスの管理を担当し、副長的なポジションに就く。 ⏎ 　同時に八神テツロウの遺したデータから、システム・ニーラカナイとエチカの謎を追っていた。それは学究的な意思に加え、愛するエチカの事をより知りたいという欲求からのものであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Following the activation of the A. Advent, she took over the job of shipboard management, affording her a position equivalent to that of a second-in-command. ⏎  ⏎ Meanwhile, she also attempts to unravel the mystery of the System Nira-Kana-I left behind by Tetsuro Yagami. In both of these pursuits she is motivated both by her own scientific curiosity and a deep desire to know more about her beloved Echika than any other.

### dic\_pilot\_NOVY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b008\]
> JP (źródło tłumaczenia): 　元新地球連邦軍所属の軍人。 ⏎ 　４８歳、男性。 ⏎ 　軍人時代の階級は中佐であり、艦長を務めていたが、自ら退役を選択して気ままな暮らしを送っていた。 ⏎ 　自由気ままで責任を嫌う言動から、一見するといいかげんな人間であるが、最低限の倫理と道徳は備えている。なお、行動原理として報酬を第一としているが、その実、金銭に対する執着は薄い。 ⏎ 　愛煙家であったが、退役後はミナに言われ、煙草を控えている。
> EN (odniesienie oficjalne, NIE polski): A former soldier in the New EFF. ⏎  ⏎ Age 48, male. ⏎  ⏎ A commander during his days in the military, he served as a ship captain but chose to resign from his position to live a freelance life. ⏎  ⏎ While his carefree attitude (and seeming distaste for responsibility) makes him seem like a complete deadbeat, he does in fact have a bare minimum of ethical and moral capacity. He also makes a show of putting his pursuit of money first, but in truth he seems to have very little attachment to wealth. ⏎  ⏎ Formerly a smoker, he has (at Mina's insistence) refrained following his resignation from the EFF.

### dic\_pilot\_NOVY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b009\]
> JP (źródło tłumaczenia): 　経験を買われてエーアデントの艦長に就任し、戦闘に関する一切を取り仕切るが、戦術・戦略レベルの決定は全てエチカに任せている。 ⏎ 　軍人時代は第３１独立部隊「インディゴ・チェイサー」の副司令であったが、偶発的に遭遇したラー・ヴァルベルムに部隊を壊滅させられた過去を持つ。 ⏎ 　その後、ヴァルベルムを追跡する事を上申するも、それを握りつぶされた事で退役を決める。その胸にヴァルベルムへの怒りや憎しみはないものの、ヴァルベルムという強大な力とそれを隠蔽した強大な権力に対する自らの無力さに憤りと絶望を感じていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Hired as the captain of the A. Advent for his experience, he takes total command of the ship during battle but leaves tactical and strategic decisions to Echika. ⏎  ⏎ He was formerly the second in command of the 31st Autonomous Corps, the Indigo Chasers, who were eliminated during a chance encounter with Ra Valbelm. ⏎  ⏎ After that, he wished to pursue Ra Valbelm, but the entire encounter was covered up by his superiors, forcing him to resign. While he has no exceptional hate or anger towards Valbelm himself, he instead harbors a deep sense of resentment and despair both at the literal strength of Valbelm himself, and at the political power that swept the entire affair under the rug.

### dic\_pilot\_MINA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b00a\]
> JP (źródło tłumaczenia): 　元新地球連邦軍の軍人。 ⏎ 　１８歳、女性。 ⏎ 　当時からノーヴィーの部下であり、彼の指揮する艦の優秀なオペレーターであった。 ⏎ 　退役したノーヴィーを追って軍を辞め、彼と行動を共にしてだらしない私生活の面倒を見ていた。 ⏎ 　生真面目な性格で曲がった事が許せず、過去の経験から権力を持った人間に対して厳しい態度を取る。
> EN (odniesienie oficjalne, NIE polski): A former soldier in the New EFF. ⏎  ⏎ Age 18, female. ⏎  ⏎ She has been part of Novey's staff for some time, and served as a capable operator for the ship under his command. ⏎  ⏎ She resigned alongside Novey, and has since accompanied him, helping Novey keep it together with his otherwise sloppy lifestyle. ⏎  ⏎ She is serious, very intolerant of impropriety, and her past experiences have also left her with a hostile attitude towards people in positions of power.

### dic\_pilot\_MINA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b00b\]
> JP (źródło tłumaczenia): 　ノーヴィーと共にエチカに雇われ、エーアデントのオペレーターを務める。 ⏎ 　第３１独立部隊を壊滅させた敵を追うというノーヴィーの上申が握りつぶされた事から権力を持った人間に絶望していたが、エチカとの出会いを経て、徐々に考えを改めていった。 ⏎ 　趣味はコスプレであり、エーアデントの何でも屋「カナイ・カナイ」の店員を務める際には自前の衣装に身を包む。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She was hired on by Echika as a package deal of sorts with Novey, and took up the role of primary operator and communications coordinator for the A. Advent. ⏎  ⏎ After experiencing the burial of Novey's request to hunt down the foe that took out the 31st Autonomous Corps, she was unable to expect anything good from people in positions of power. Her experiences with Echika have slowly worn down her pessimism. ⏎  ⏎ She likes to cosplay and has a unique costume she wears when working as staff for the A. Advent's general store, the Kana-Kana-I.

### dic\_pilot\_RENREN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b00c\]
> JP (źródło tłumaczenia): 　フランバーネット邸に勤めるメイド。 ⏎ 　屋敷のインフラを担当するメカニック班のリーダー。 ⏎ 　姉御肌で９９人のメイドのまとめ役でもある。
> EN (odniesienie oficjalne, NIE polski): One of the maids employed at the Franburnett Manor. ⏎  ⏎ Leader of the mechanics division that maintains the manor's infrastructure. ⏎  ⏎ The big-sister type, she is also the informal leader of the manor's 99 maids.

### dic\_pilot\_RENREN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b00d\]
> JP (źródło tłumaczenia): 　八神テツロウによってエーアデントの存在も知らされており、他のメイドやアニーナと共に起動の日に備えていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She was informed in advance about the A. Advent by Tetsuro Yagami and spent her days with Annina and the other maids, waiting for the day when it would activate.

### dic\_pilot\_AITY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:93e0b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:93e0b00e\]
> JP (źródło tłumaczenia): 　フランバーネット邸に勤めるメイド。 ⏎ 　エチカのために世界中のあらゆる情報を集める情報班のリーダー。 ⏎ 　冷静沈着ではあるが、その思考様式は世間の常識とは少しズレており、目的のためなら一切手段を選ばないという危険性も併せ持っている。
> EN (odniesienie oficjalne, NIE polski): One of the maids employed at the Franburnett Manor. ⏎  ⏎ Leader of the information division, who serves Echika by gathering information from across the globe. ⏎  ⏎ She seems calm and collected, but her thought patterns are a bit unusual. She also has a dangerous side in that she will do anything to achieve her goals.

### dic\_pilot\_AITY\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b000\]
> JP (źródło tłumaczenia): 　八神テツロウによってエーアデントの存在も知らされており、他のメイドやアニーナと共に起動の日に備えていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She was informed in advance about the A. Advent by Tetsuro Yagami and spent her days with Annina and the other maids, waiting for the day when it would activate.

### dic\_pilot\_COOKIN\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b001`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b001\]
> JP (źródło tłumaczenia): 　フランバーネット邸に勤めるメイド。 ⏎ 　屋敷の家事全般を担当する生活班のリーダー。 ⏎ 　世界中のあらゆる料理を作る抜群の腕を持ち、エチカの身体的な成長を楽しみにしている。
> EN (odniesienie oficjalne, NIE polski): One of the maids employed at the Franburnett Manor. ⏎  ⏎ Leader of the general support division, which handles chores and other actual housekeeping about the manor. ⏎  ⏎ She is a master chef who can create dishes from cultures across the world, and takes great joy in watching Echika grow.

### dic\_pilot\_COOKIN\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b002\]
> JP (źródło tłumaczenia): 　八神テツロウによってエーアデントの存在も知らされており、他のメイドやアニーナと共に起動の日に備えていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She was informed in advance about the A. Advent by Tetsuro Yagami and spent her days with Annina and the other maids, waiting for the day when it would activate.

### dic\_pilot\_YAGAMI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b003`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b003\]
> JP (źródło tłumaczenia): 　エチカの父親。 ⏎ 　精神感応素材とエネルギー工学の権威であり、特戦隠密・朧の使用する機動忍鎧の開発にも関係していた。 ⏎ 　八神市の地下に機動要塞都市エーアデントを秘密裏に建造していたが、エチカが１０歳の時に研究中の事故により死亡した。 ⏎ 　だが、その事故は自らの秘密の研究を進めるために世間から身を隠すためのものであった。
> EN (odniesienie oficjalne, NIE polski): Echika's father. ⏎  ⏎ A leading name in the development of materials and energies related to the human mind, he was also involved in the development of the Mobile Armored Ninjas used by the Special Stealth Forces, Haze. ⏎  ⏎ He later built the Mobile Fortification A. Advent beneath Yagami City, but perished in a research accident when Echika was ten years old. ⏎  ⏎ That accident, however, was merely a cover to allow him to pursue his own secret research, hidden from the world.

### dic\_pilot\_YAGAMI\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b004\]
> JP (źródło tłumaczenia): 　研究至上主義のエゴイスティックな性格は養子であるクロスやフォルテからも疎まれており、エチカに対しても研究素材以上の感情は持っていない。エチカの母…つまり、妻の存在も架空のものであり、エチカの精神を縛りつけるための材料に過ぎないものであった。 ⏎ 　なお、様々な方面にスポンサーを持ち、エーアデントの建造費はそこから出されているが、それ以上の資産が秘密資金として隠されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ An egotistical man who puts his research above all, he is distant to his adopted children Cross and Forte, and even Echika is nothing but a research subject to him. Echika's mother, his "wife", was actually a fictional person created solely to help control Echika's mind and give her a cover story. ⏎  ⏎ While he has significant financial sponsors from many groups which helped fund the A. Advent's construction, he also has a tremendous amount of personal wealth hidden away.

### dic\_pilot\_AID\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b005`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b005\]
> JP (źródło tłumaczenia): 　新地球連邦の初代にして最後の大統領。 ⏎ 　新地球連邦解散後には、国家間の調停機関である新国際連合の事務総長に就任し、過渡期にある世界のために尽力している。
> EN (odniesienie oficjalne, NIE polski): The first and final president of the New Earth Federation. ⏎  ⏎ After the disbanding of the New Earth Federation, he moved on to serve as the chief of staff for the New League of Nations, which served as an international affairs intermediary, to serve the world in this time of change and chaos.

### dic\_pilot\_AID\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b006\]
> JP (źródło tłumaczenia): 　その実態は汎星間帝国ラー・ヴァルの最初期からの協力者であり、強大な力を持った彼等の存在を知った時から服従を誓っていた。 ⏎ 　地球連邦の上院議員だった頃から秘密裏にラー・ヴァルに便宜を図り、ノーヴィーのヴァルベルム追跡の上申を握りつぶしていた張本人でもある。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In truth, he was a supporter of the Pan-Stellar Empire Ra Val from the start, who swore fealty upon learning of their existence and immense power. ⏎  ⏎ He served the interests of Ra Val as far back as his days in the Earth Federation, and was the one who buried Novey's request to hunt down Valbelm.

### dic\_pilot\_VALBLM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b007`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b007\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの第６８代天帝。 ⏎ 　４９歳、男性。 ⏎ 　ラー・ヴァルの支配者である天帝は世襲ではなく、完全に実力で決まり、ヴァルベルムも前天帝を討ち、その座に就いた。 ⏎ 　ラー・ヴァル史上最強の軍事指導者であると同時に最強の戦士としても称えられており、戦闘に関する能力を司る「生存戦略遺伝子」が最も発達した個体でもある。 ⏎ 　自他ともに厳しく、部下達から熱烈な信奉を集めると同時に恐れられており、直接意見を述べる事が出来る人間は限られている。
> EN (odniesienie oficjalne, NIE polski): The 68th Celestial Emperor of the Pan-Stellar Empire Ra Val. ⏎  ⏎ Age 49, male. ⏎  ⏎ The rulership position of Ra Val and title of "Celestial Emperor" is not hereditary; it is instead won entirely on merit. Valbelm, like past Celestial Emperors, won the title by slaying his predecessor. ⏎  ⏎ Hailed as both the greatest commander as well as the greatest single warrior in Ra Val history, he is the greatest individual expression of the survival strategy genes that determine Ra Valian combat capability. ⏎  ⏎ Strict with both others and himself, he has earned both deep respect and fear from the people under him, which means that only a limited few are able to express their opinion to him.

### dic\_pilot\_VALBLM\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b008\]
> JP (źródło tłumaczenia): 　その胸には２５００年先の未来で地球人類の末裔に敗北した事が大きな傷となって残っており、その戦いで散っていった同志の魂に報いると同時にラー・ヴァル人の誇りを取り戻すため、たった独りになっても地球人類を屈服させて銀河を制覇しようとした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He still bears scars from his defeat at the hands of the Earthlings' descendants 2500 years in the future. For the souls of those who died in that battle, and to reclaim his pride as a Ra Valian, he is committed to conquering the Earthlings and the entire galaxy, even if he has to do it alone.

### dic\_pilot\_SEYVAS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b009`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b009\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝親衛隊隊員「天騎士」。 ⏎ 　２３歳、男性。 ⏎ 　自由を愛する陽気な性格で、部下である天闘士達からも人気が高い。 ⏎ 　反面、規律を重んじる一派からはうとまれているが、本人もそれを自覚しており、敢えて彼等に対して挑発的な言動を取って反応を楽しんでいる節がある。 ⏎ 　それらは全て天帝ヴァルベルムとラー・ヴァルのためであり、閉塞感に包まれたラー・ヴァルに新しい何かを吹き込みたいと考えている。
> EN (odniesienie oficjalne, NIE polski): A Celestial Knight, one of the elite guards of the Pan-Stellar Empire Ra Val. ⏎  ⏎ Age 23, male. ⏎  ⏎ A freedom-loving man with a sunny disposition, he is liked by the Celestial Warriors under him. ⏎  ⏎ More conservative groups, on the other hand, find him distasteful, which he is fully aware of. Indeed, he enjoys inciting them to see them bluster. ⏎  ⏎ Everything he does, he does for the Celestial Emperor, and he believes the stagnant Ra Val culture is in need of fresh ideas.

### dic\_pilot\_SEYVAS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00a\]
> JP (źródło tłumaczenia): 　ヴァルベルムと共に現在の地球に跳ばされた数少ない天騎士の一人であり、転移の時点では見習いに近い立場であった。しかし、自らの使命を強く自覚し、名実共にラー・ヴァル最強の戦士となるべく努力し、それに相応しい力を得た。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He is one of the few Celestial Knights who was sent to the current time together with Valbelm, although he was essentially a novice at the time. His strong sense of duty compelled him to aspire to be Ra Val's strongest in name and in action, and enabled him to gain the strength needed to fill such a role.

### dic\_pilot\_SISTIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00b`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00b\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝親衛隊隊員「天騎士」。 ⏎ 　２３歳、女性。 ⏎ 　規律を重んじる性格で、ラー・ヴァル軍内の風紀を取り締まる立場にある。 ⏎ 　セイヴァースの同期であるが、性格は合わないため、必要以上には会話もしない関係にある。 ⏎ 　高い指揮能力を持ち、ヴァルベルムの命により、ラー・ヴァル全軍を率いる権限を有している。
> EN (odniesienie oficjalne, NIE polski): A Celestial Knight, one of the elite guards of the Pan-Stellar Empire Ra Val. ⏎  ⏎ Age 23, female. ⏎  ⏎ As someone who values order and discipline, she often ends up in the position of ensuring the Ra Valian armies maintain proper conduct. ⏎  ⏎ She joined around the same time as Seivas, but they get along like oil and water, so she only speaks to him when absolutely necessary. ⏎  ⏎ She is an excellent commander, and Valbelm has given her full authority over the Ra Valian army.

### dic\_pilot\_SISTIS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00c\]
> JP (źródło tłumaczenia): 　ヴァルベルムに対して忠誠心以上の想いを寄せているが、覇道を進むヴァルベルムに対して常に一歩引いた位置から付き従い、自らの想いは伏せたままにしている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Her feelings for Valbelm go beyond simple loyalty, but she keeps them well hidden in her heart as she accompanies Valbelm on his path of conquest, always one step behind him.

### dic\_pilot\_NEGSIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00d`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00d\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの筆頭参謀「天賢」。 ⏎ 　４８歳、男性。 ⏎ 　天帝ヴァルベルムの第一の側近であり、ヴァルベルムが天帝に就く前から、その参謀を務めてきた。 ⏎ 　明晰な頭脳と戦略眼を持っているが、慇懃無礼であり、ラー・ヴァル内でも多くの人間の反感を買っている。同時に誰もが、その頭脳を評価しており、畏怖されている存在。 ⏎ 　ヴァルベルムの意思の代弁者でもあり、他組織との交渉役も一手に引き受けている。
> EN (odniesienie oficjalne, NIE polski): The chief strategist of Pan-Stellar Empire Ra Val, and the Empire's "Celestial Sage". ⏎  ⏎ Age 48, male. ⏎  ⏎ The closest aide of the Celestial Emperor Valbelm, he has been Valbelm's strategist since before his coronation. ⏎  ⏎ While a clever intellectual with a sharp tactical eye, the veiled disrespect he treats people with tends to earn him a great deal of opposition amongst the people of Ra Val. However, those same people acknowledge his sharp mind and often stand in awe of him. ⏎  ⏎ He serves Valbelm as his speaker, and is often in charge of negotiation with outside forces.

### dic\_pilot\_NEGSIS\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b00e`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00e\]
> JP (źródło tłumaczenia): 　ヴァルベルムの心情を理解しながらも、ラー・ヴァル存続のために彼の野望には反対しており、穏便な着地点を模索していた。 ⏎ 　二人の間には他の人間が割って入る事の出来ない絆があり、最終的には袂を分かったものの、最期の瞬間までヴァルベルムとラー・ヴァルの勝利を願っていた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ While he understands Valbelm's heart well, he opposes Valbelm's ambitions out of concern for the continuation of Ra Val, hoping to find a peaceable common ground. ⏎  ⏎ The two share an unbreakable bond that none can come between, and though they would end up going their separate ways, he hoped Valbelm and Ra Val would seek victory to the very end.

### dic\_pilot\_IZANA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b00f`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b00f\]
> JP (źródło tłumaczenia): 　超古代文明・怨の一族の遺した因子が目覚めた超人類。 ⏎ 　１６歳、女性。 ⏎ 　人類史上初の超人類の覚醒者であるが、２歳の時、その超能力の全てを制御する前に事故により精神を暴走させてしまい、以降は長い眠りについていた。 ⏎ 　その後、八神テツロウによって保護され、その遺伝子からコピーであるエチカが生み出された。イザナの名も八神によってつけられたものであり、それ以前の経歴の記録は抹消されている。
> EN (odniesienie oficjalne, NIE polski): A Superhuman who manifested the factor left in the world by the supercivilization known as the Animus Clan. ⏎  ⏎ Age 16, female. ⏎  ⏎ While technically she is humanity's first fully awakened superhuman, her inability to fully control her abilities at the age of two caused her mind to lose control, and she fell into a long sleep. ⏎  ⏎ Afterwards, she was taken by Tetsuro Yagami, who genetically copied her to create Echika. "Izana" is the name given to her by Dr. Yagami, and all records of her prior to coming into his care have been lost or erased.

### dic\_pilot\_IZANA\_00\_1

Adres: `dic\_text\_pilot/01fdb9ba:9420b010`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b010\]
> JP (źródło tłumaczenia): 　怨の一族の残留思念ヴィルの集合体であるイヴォルバーの新たな肉体となるはずであったが、そこから解放され、妹であるエチカ達と共に自分の意思で生きていく事を決める。
> EN (odniesienie oficjalne, NIE polski):  ⏎ The Evolvers, the collective lingering psyches of the Animus Clan in the form of Willforce, intended to use her as their new body, but she was freed from their control, choosing to live by her own will together with her "little sister", Echika.

### dic\_pilot\_IVRVER\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b011`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b011\]
> JP (źródło tłumaczenia): 　超古代文明・怨の一族の残留思念であるヴィルの集合体。 ⏎ 　現在の地球人類を戦闘的に進化させる存在として、八神テツロウによって、その名がつけられた。 ⏎ 　過去に果たせなかった銀河支配の野望を地球人類を駒として使う事で実現しようと目論み、超人類として目覚めたイザナの肉体を自分達の新たな器にしようとした。
> EN (odniesienie oficjalne, NIE polski): The combined mass of the Willforce, which is the lingering psyches of the extinct supercivilization known as the Animus Clan. ⏎  ⏎ Tetsuro Yagami named it because it aims to force humanity to evolve into a fighting species. ⏎  ⏎ It seeks to use humanity as a pawn to accomplish the galactic conquest it failed in once before, and attempted to turn Izana's body into its vessel following her awakening as a superhuman.

### dic\_pilot\_MOB\_14\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b013`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b013\]
> JP (źródło tłumaczenia): 　エーアデント居住区の居酒屋「栄伝屋」の店主。 ⏎ 　元々は違う店名であったが、エチカが選挙によってエーアデントの代表に正式に就任した事を記念して、今の店名に変えた。 ⏎ 　洋の東西を問わない各種のお酒と、それを引き立てる様々な料理によって店は大繁盛している。
> EN (odniesienie oficjalne, NIE polski): The owner of the Ale &amp; Vent Bar and Lounge in the A. Advent's residential quarter. ⏎  ⏎ The store had a different name previously, but it was changed in celebration of Echika's formal election to the position of representative. ⏎  ⏎ It serves alcohol of all kinds from across the globe, as well as meals to best bring out the flavor of that alcohol, making it a very successful establishment and a favorite hangout of many of the A. Advent's pilots.

### dic\_pilot\_MOB\_12\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b015`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b015\]
> JP (źródło tłumaczenia): 　エーアデント居住区のカフェ「Ａアデン」の店主。 ⏎ 　元々は違う店名であったが、エチカが選挙によってエーアデントの代表に正式に就任した事を記念して、今の店名に変えた。 ⏎ 　居心地のいい雰囲気、多種多様なスイーツと豊富なランチメニューでお店は大人気であり、エチカも事あるごとに入り浸っている。 ⏎ 　店を取り仕切る彼女は、街のマドンナ的な存在である。
> EN (odniesienie oficjalne, NIE polski): The owner of the "A. Ardent", a cafe in the A. Advent's residential quarter. ⏎  ⏎ The cafe had a different name previously, but it was changed in celebration of Echika's formal election to the position of representative. ⏎  ⏎ Its pleasant atmosphere combined with its wide variety of sweets and lunch options make it a popular spot, and one frequented by Echika as much as she can justify. ⏎  ⏎ Her role as owner and face of the shop has made her something of a local celebrity.

### dic\_pilot\_MASAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9420b017`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9420b017\]
> JP (źródło tłumaczenia): 　魔装機神サイバスターの操者。 ⏎ 　地底世界ラ・ギアスに存在する神聖ラングラン王国に、地上人招喚計画の対象者として日本から招喚される。 ⏎ 　その後、サイバスターの守護精霊サイフィスに選ばれ、魔装機神操者となった。 ⏎ 　直情径行的で破滅的な方向音痴という弱点もあるが、スポーツ万能で正義感が強い。
> EN (odniesienie oficjalne, NIE polski): Herald of the Elemental Lord known as Cybaster. ⏎  ⏎ Originally from Japan, Masaki was summoned to the Holy Kingdom of Langran in the subterranean world of La Gias as part of a plan to summon overworlders. ⏎  ⏎ Once there, he was chosen by Cybaster's guardian spirit, Cyphis, to become an Elemental Lord Herald. ⏎  ⏎ Though impulsive to a fault (and incapable of finding his way out of a paper bag), Masaki's athleticism and strong sense of justice made him a stalwart ally through thick and thin.

### dic\_pilot\_KURO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b000\]
> JP (źródło tłumaczenia): 　マサキのファミリア。 ⏎ 　彼の無意識の一部を切り取った使い魔で、性格が似ていないのはペルソナの一つだからである。 ⏎ 　マサキと共にサイバスターへ搭乗し、彼のサポートを行う。 ⏎ 　割とノンビリとした性格をしているが、どちらかといえば心配性で、無茶をしがちなシロやマサキをたしなめることが多い。
> EN (odniesienie oficjalne, NIE polski): One of Masaki's feline familiars. ⏎  ⏎ Although her personality appears to be different from her master's, Kuro was created from Masaki's unconscious mind and can be considered one of his alternate personas. She rides alongside him in Cybaster's cockpit to provide support. ⏎  ⏎ Kuro is fairly easygoing, but also a bit of a worrywart, often chiding Masaki and Shiro for their tendency to get in over their heads.

### dic\_pilot\_SHIRO\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b002\]
> JP (źródło tłumaczenia): 　マサキのファミリア。 ⏎ 　彼の無意識の一部を切り取った使い魔で、性格が似ていないのはペルソナの一つだからである。 ⏎ 　マサキと共にサイバスターへ搭乗し、彼のサポートを行う。 ⏎ 　割とノンビリとした性格をしているが、どちらかといえば勝ち気な性格で一言多い。
> EN (odniesienie oficjalne, NIE polski): One of Masaki's feline familiars. ⏎  ⏎ Although his personality appears to be different from his master's, Shiro was created from Masaki's unconscious mind and can be considered one of his alternate personas. He rides alongside him in Cybaster's cockpit to provide support. ⏎  ⏎ Shiro is relatively easygoing, but get into an argument with him and you won't hear the end of it.

### dic\_pilot\_SOUJI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b004\]
> JP (źródło tłumaczenia): 　地球連邦軍月面特殊戦略研究所防衛隊の隊員。階級は三尉。２３歳。 ⏎ 　以前は月面航空隊第２５部隊に所属していたが、他の隊員が全て戦死したために隊は解散となり、研究所防衛隊に配属された。 ⏎ 　浅黒い肌は紫外線にさらされた影響であり、本人曰く宇宙パイロットの証。 ⏎ 　「人生を楽しく生きる」をモットーとした快楽主義者で、何事もポジティブに捉える不屈の精神の持ち主。 ⏎ 　なお、第２５部隊所属時は真面目な性格で周囲からは堅物と見られていたが、散っていった戦友達の供養として、彼等の分まで「人生を楽しく生きる」事を決め、様々な「楽しい事」に手を出している。が、少なくともナンパには不向きである。 ⏎ 　研究所で開発されたＥＲＳ－１００を移送するために地球へと降りた。 ⏎ 　ＥＲＳ－１００に「人間」というものを教えた事により、彼女の制作した機動兵器ヴァングレイに搭乗する事になり、地球を救うための旅に出る。 ⏎ 　そこでの経験を糧にパートナーであるナインと共に成長し、地球を救うための大きな力となった。
> EN (odniesienie oficjalne, NIE polski): A member of the EFF's Lunar Special Tactical Lab Defense Force of the rank of ensign. Age 23. ⏎  ⏎ Formerly part of the 25th Squadron, Lunar Aviation Wing until his entire team perished in combat; this warranted the squad's disbandment and his assignment to the lab defense force. His dark-tanned skin is the result of UV-ray exposure. He claims it's the mark of a space pilot. ⏎  ⏎ He is a hedonist whose motto is to "enjoy life", which gives him an indomitable mindset able to see the silver lining in anything. While originally more of a serious, even inflexible person, after the death of his comrades he chose to enjoy life for their sakes as well and became focused on seeking pleasure. For all that, however, he is very poor at hitting on women. ⏎  ⏎ He descended to Earth accompanying the recently developed ERS-100. ⏎  ⏎ After teaching ERS-100 about humans, he would take command of the mobile weapon she developed, the VangRay, he then went on a journey to save the world. ⏎  ⏎ He learned a great deal alongside his partner Nine and was key to saving the Earth.

### dic\_pilot\_CHITOSE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b006\]
> JP (źródło tłumaczenia): 　地球連邦軍第三特殊戦略研究所防衛隊の隊員。階級は三尉。１９歳。 ⏎ 　両親と妹を戦禍で失い、天涯孤独の身。 ⏎ 　実戦経験はほとんどないが、人手不足のために研究所防衛隊の唯一の隊員となる。 ⏎ 　機動兵器の操縦については一通りの訓練を受けただけであるが、射撃の腕を始めとして素質はあると評価されている。 ⏎ 　性格は真面目かつ明朗快活で、常に前向きな姿勢は周囲の人間の心を明るくし、研究所の所員達の間ではムードメーカー的な存在であった。 ⏎ 　職務上、研究所の防衛以外にも様々な雑用をこなさなくてはならない事と、所員達の私的な希望により、軍服の着用が免除されている。 ⏎ 　ＥＲＳ－１００に「人間」というものを教えた事により、彼女の制作した機動兵器ヴァングレイに搭乗する事になり、地球を救うための旅に出る。 ⏎ 　そこでの経験を糧にパートナーであるナインと共に成長し、地球を救うための大きな力となった。
> EN (odniesienie oficjalne, NIE polski): A member of the EFF's Lunar Special Tactical Lab Defense Force of the rank of ensign. Age 19. ⏎  ⏎ Having lost her parents and sister in war, she has no living family. She has no real experience in combat, and became a member of the lab defense force due to a shortage of personnel. ⏎  ⏎ She's only received basic training in mobile weapon piloting, but she's well regarded for her many aptitudes, particularly in shooting. ⏎  ⏎ Her good cheer and enthusiasm brightens the hearts of everyone around and keeps up the energy of the research staff. ⏎  ⏎ Because of the many tasks she undertakes around the lab outside of her duties, and by special request of the research staff, she isn't required to be in uniform. ⏎  ⏎ After teaching ERS-100 about humans, she would take command of the mobile weapon the system developed, the VangRay, she then went on a journey to save the world. ⏎  ⏎ She learned a great deal alongside her partner Nine and was key to saving the Earth.

### dic\_pilot\_NINE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b008\]
> JP (źródło tłumaczenia): 　ヴァングレイの制御ＯＳであるシステム９９が組み込まれたアンドロイド。 ⏎ 　ソウジやチトセとはぐれた際、情報の収集や円滑なコミュニケーションのために人間の姿の方が都合がいいと判断し、女性の人格に合わせ、システム９９自らが少女型ボディを造り上げた。 ⏎ 　その正体は地球再生システム「ＥＲＳ－１００」であり、人間に憧れ、人間を学ぶために、その姿を真似ている。なお、スチームパンク風の衣装は、機械と人間の間にある自分のアイデンティティを表現している。 ⏎ 　システム９９の時よりも感情が豊かになったが、基本的には常に冷静で、周囲に対してシニカルな態度を取る。これは極度にシャイな性格を隠すための一種の強がりと思春期の少女に見られる、いわゆる反抗期の産物である。 ⏎ 　超文明ガーディムの生み出した文明再建システム「ネバンリンナ」の端末であり、スレイブナンバー２０４４のコードを持つ。情報収集を目的として、調査活動を行なっていた際、トラブルからネバンリンナから独立する事になり、後に地球人に発見されてＥＲＳ－１００として調整された。 ⏎ 　なおネバンリンナの端末の役目は外部の情報収集であり、本来ならばネバンリンナと独立した意思を持つ事はあり得ない。しかし、トラブルによって本体の意思が遮断された事で端末内の補助ＡＩが独自の自我を持ったと推測される。 ⏎ 　その機能を用いて、ヴァングレイ他の機体を製造し、大切に想う人達を守り、彼等と共に戦うようになる。 ⏎ 　三つの世界の地球を救った後は、大切な人達と共に各地の復興のために旅に出る事を決めた。
> EN (odniesienie oficjalne, NIE polski): An android with the VangRay's operating system, System 99, installed into it. ⏎  ⏎ When separated from Soji and Chitose, she judged it would be better to have a human form to facilitate information gathering and ease communication. She synthesized this with a feminine personality and constructed the body of a small girl for herself. ⏎  ⏎ She is in fact the Earth Regeneration System ERS-100, and she chose to construct a human body out of her adoration for humanity and desire to learn about them. Her steampunk-ish attire is an attempt at expressing her own identity as someone in between machine and humanity. ⏎  ⏎ While more emotional than when she was System 99, she remains fundamentally level-headed and often takes a cynical attitude towards those around her. This tends to come off as a girl trying to mask her shyness with a strong front, almost like a rebellious phase. ⏎  ⏎ Her true nature is a "terminal" of the Gardim supercivilization's creation, the Civilization Reconstruction System Nevanlinna, and she's assigned the moniker Slave 2044. Her purpose is information gathering, but after she encountered trouble during an investigation she was disconnected from Nevanlinna and rebuilt into ERS-100 by the Earthlings who discovered her. ⏎  ⏎ As a rule, Nevanlinna's terminals exist solely to gather information and should not be able to possess their own individual will. It's believed that when she was disconnected from the core unit, a support AI inside the terminal activated and gained its own sense of self. ⏎  ⏎ Using her abilities, she built the VangRay and other machines and fought alongside the people she cared for to keep them safe. After saving the three Earths, she set out on a journey across the worlds to help rebuild.

### dic\_pilot\_IORI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b00a\]
> JP (źródło tłumaczenia): 　魔従教団でドグマを修めた術士。１８歳。 ⏎ 　「菫青石（きんせいせき）の術士」の二つ名を持つ。 ⏎ 　アル・ワースとは別世界で生まれた異界人であり、本名は「葵伊織」。 ⏎ 　勝ち気かつ生真面目で強い正義感を持っている。 ⏎ 　幼き頃より修練を積んできたドグマに自信と誇りを持ち、その力で何が出来るかを模索している。 ⏎ 　魔従教団を脱走後、魔法生物ホープスと共にオート・ウォーロック、ゼルガードを駆り、旅をしていた。 ⏎ 　教主となる素質を持った人間を集めていた魔従教団によって招喚された異界人であり、アル・ワースで過ごした時間は約一年程度であるが、精神制御下にあった時には幼き頃から教団で修練していたと思い込まされていた。 ⏎ 　元の世界では、感情をはっきりと示す事が出来ない自分を変えたいと願っており、その「破壊の意思」をエンデに見込まれる事となった。 ⏎ 　様々な人々と出会う中、自らのドグマですべき事を学んで魔力を高め、独自のドグマを完成させていった。 ⏎ 　また、当初は険悪であったホープスとの関係も徐々に変化していき、相棒と言うべき存在となっていった。 ⏎ 　アル・ワースを救った後も完全に世界が平穏を取り戻すまで、アル・ワースに留まる事を決めた。
> EN (odniesienie oficjalne, NIE polski): A sorcerer with the Keepers of Order, trained in Dogma. Age 18. ⏎  ⏎ Also known as the Iolite Sorcerer. ⏎  ⏎ He is an otherworlder born from a world beyond Al-Warth, originally called Iori Aoi. ⏎  ⏎ Fierce of spirit with a strong sense of justice. He has trained extensively in Dogma since his youth and is confident in his ability, but now is searching for something he can do to contribute with this ability. ⏎  ⏎ After leaving the Keepers of Order, he departs on a journey aboard the Autowarlock Xelguard, together with the magical creature Spero. ⏎  ⏎ The Keepers of Order summoned him as part of a project to collect humans with the qualities of their Founder. In fact, he's only been in Al-Warth for around a year, but his memories have been magically falsified so he believes he's been training with the Keepers from a young age. ⏎  ⏎ In his original world he desired to change himself and his difficulty expressing his emotions, but this "destructive will" would catch Ende's attention. ⏎  ⏎ Through many encounters he slowly came to see what he could do with his Dogma abilities and strengthened his magic, ultimately creating his own unique Dogma. ⏎  ⏎ His relationship with Spero also slowly improved from its original hostility, and he eventually came to regard Spero as a partner. ⏎  ⏎ After saving Al-Warth, he chose to remain there to help ensure a thorough, lasting peace returned.

### dic\_pilot\_IORI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94a0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94a0b00c\]
> JP (źródło tłumaczenia): 　魔従教団でドグマを修めた術士。１８歳。 ⏎ 　「菫青石（きんせいせき）の術士」の二つ名を持つ。 ⏎ 　アル・ワースとは別世界で生まれた異界人であり、本名は「葵伊織」。 ⏎ 　生真面目で強い正義感を持っているが、少し気弱な所がある。 ⏎ 　教主となる素質を持った人間を集めていた魔従教団によって招喚された異界人であり、アル・ワースで過ごした時間は約一年程度であるが、精神制御下にあった時には幼き頃から教団で修練していたと思い込まされていた。 ⏎ 　元の世界ではアマリのクラスメートであり、彼女に想いを寄せていたが、気弱さもあり、具体的なアプローチは出来ないでいた。 ⏎ 　アマリによって自らを取り戻した後はゼルガードに搭乗して共に戦ったが、恋のライバル（？）であるホープスとは、あまり仲がよくない。 ⏎ 　アル・ワースを救った後も完全に世界が平穏を取り戻すまで、アマリと共にアル・ワースに留まる事を決めた。
> EN (odniesienie oficjalne, NIE polski): A sorcerer with the Keepers of Order, trained in Dogma. Age 18. ⏎  ⏎ Also known as the Iolite Sorcerer. ⏎  ⏎ He is an otherworlder born from a world beyond Al-Warth, originally called Iori Aoi. ⏎  ⏎ Although he is a serious, just person, he can be weak-willed at times. ⏎  ⏎ The Keepers of Order summoned him as part of a project to collect humans with the qualities of their Founder. In fact, he's only been in Al-Warth for around a year, but his memories have been magically falsified so he believes he's been training with the Keepers from a young age. ⏎  ⏎ In his original world he was a classmate of Amari who had feelings for her, but his weak-willed nature made it hard for him to approach her in any real way. ⏎  ⏎ After he regained his self thanks to Amari, he joined her in battle aboard the Xelguard, though he maintained a poor relationship with his love rival(?), Spero. ⏎  ⏎ After saving Al-Warth, he chose to join Amari in remaining there to help ensure a thorough, lasting peace returned.

### dic\_pilot\_AMARI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b000\]
> JP (źródło tłumaczenia): 　魔従教団でドグマを修めた術士。１８歳。 ⏎ 　「藍柱石（らんちゅうせき）の術士」の二つ名を持つ。 ⏎ 　アル・ワースとは別世界で生まれた異界人であり、本名は「天野亜真里」。 ⏎ 　礼儀正しく真面目であるが、気弱で臆病な所がある。 ⏎ 　しかし、心の底には強い決意を持っており、自分が何のために生きているかを探し求めている。 ⏎ 　その目的のため、魔法生物ホープスと共にオート・ウォーロック、ゼルガードを駆り、旅をしていた。 ⏎ 　教主となる素質を持った人間を集めていた魔従教団によって招喚された異界人であり、アル・ワースで過ごした時間は約一年程度であるが、精神制御下にあった時には幼き頃から教団で修練していたと思い込まされていた。 ⏎ 　元の世界では、内気で引っ込み思案の自分を変えたいと願っており、その「破壊の意思」をエンデに見込まれる事となった。 ⏎ 　様々な人々と出会う中、自らのドグマですべき事を学んで魔力を高め、独自のドグマを完成させていった。 ⏎ 　その優しさと秘めた強さは、ホープスをも魅了した。 ⏎ 　アル・ワースを救った後も完全に世界が平穏を取り戻すまで、アル・ワースに留まる事を決めた。
> EN (odniesienie oficjalne, NIE polski): A sorcerer with the Keepers of Order, trained in Dogma. Age 18. ⏎  ⏎ Also known as the Aquamarine Sorcerer. ⏎  ⏎ She is an otherworlder born from a world beyond Al-Warth, and her real name is Amari Amano. ⏎  ⏎ She is a polite, serious person, but also indecisive and sometimes cowardly. Deep down she has a strong will, however, and seeks to find something worth living for. ⏎  ⏎ In pursuit of that, she journeys together with the magical creature Spero aboard the Autowarlock Xelguard. ⏎  ⏎ The Keepers of Order summoned her as part of a project to collect humans with the qualities of their Founder. In fact, she's only been in Al-Warth for around a year, but her memories have been magically falsified so she believes she's been training with the Keepers from a young age. ⏎  ⏎ In her old world, she desired to cast aside the shy, reclusive parts of her, but this "destructive will" would catch Ende's attention. ⏎  ⏎ Through many encounters she slowly came to see what she could do with her Dogma abilities and strengthened her magic, ultimately creating her own unique Dogma. ⏎  ⏎ The strength wrapped inside her gentle heart also utterly charmed Spero. ⏎  ⏎ After saving Al-Warth, she chose to remain there to help ensure a thorough, lasting peace returned.

### dic\_pilot\_AMARI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b002\]
> JP (źródło tłumaczenia): 　魔従教団でドグマを修めた術士。１８歳。 ⏎ 　「藍柱石（らんちゅうせき）の術士」の二つ名を持つ。 ⏎ 　アル・ワースとは別世界で生まれた異界人であり、本名は「天野亜真里」。 ⏎ 　教団の精神制御下にあった時には生真面目で融通の利かない所が目立ったが、本来は礼儀正しく穏やかな性格をしている。 ⏎ 　教主となる素質を持った人間を集めていた魔従教団によって招喚された異界人であり、アル・ワースで過ごした時間は約一年程度であるが、精神制御下にあった時には幼き頃から教団で修練していたと思い込まされていた。 ⏎ 　元の世界ではイオリのクラスメートであり、彼から密かに想いを寄せられていた。 ⏎ 　イオリによって自らを取り戻した後はゼルガードに搭乗して共に戦い、彼の知られざる一面に驚く事になる。 ⏎ 　アル・ワースを救った後も完全に世界が平穏を取り戻すまで、イオリと共にアル・ワースに留まる事を決めた。
> EN (odniesienie oficjalne, NIE polski): A sorcerer with the Keepers of Order, trained in Dogma. Age 18. ⏎  ⏎ Also known as the Aquamarine Sorcerer. ⏎  ⏎ She is an otherworlder born from a world beyond Al-Warth, and her real name is Amari Amano. ⏎  ⏎ When in the Order she seemed to be very serious and inflexible, but normally she's very polite and gentle. ⏎  ⏎ The Keepers of Order summoned her as part of a project to collect humans with the qualities of their Founder. In fact, she's only been in Al-Warth for around a year, but her memories have been magically falsified so she believes she's been training with the Keepers from a young age. ⏎  ⏎ In her original world, she was a classmate of Iori who had feelings for him that she never had the courage to act upon. ⏎  ⏎ After regaining her sense of self with Iori's help, she joined him in battle aboard the Xelguard, though she would be surprised at the new sides of him she would see. ⏎  ⏎ After saving Al-Warth, she chose to join Iori in remaining there to help ensure a thorough, lasting peace returned.

### dic\_pilot\_HOPES\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b004\]
> JP (źródło tłumaczenia): 　ドグマで創られた人工生命体。 ⏎ 　偏屈かつ慇懃無礼で、自分より下と見た相手に対しては口調は丁寧だが、その端々で見下したような言動を取る。 ⏎ 　幅広い知識を持ち、その知識を広げるために旅をしている。 ⏎ 　オドを増幅する力を持っており、エンデの加護から外れつつあったゼルガードがドグマを使えたのは、ホープスの力による所が大きい。 ⏎ 　その正体は魔獣エンデと同じく高次元生物の幼生体であり、エンデが自らの生命のスペアとするために別の世界より呼び寄せたが、その運命から逃れるために教団から脱走した。 ⏎ 　エンデと同様に人間の感情を食するが、様々な出会いにより、エンデとは逆に人間の喜びや愛や希望を好むようになった。
> EN (odniesienie oficjalne, NIE polski): An artificial life form created with Dogma. ⏎  ⏎ He veils his distaste for those he finds to be "lesser" with a polite effect, but it's still fairly obvious when he's looking down on someone. ⏎  ⏎ His studies have been broad and deep, and sets out on a journey to further expand his knowledge. He has the power to enhance Od, which contributed significantly to allowing the Xelguard to use Dogma even after Ende stripped his boon away. ⏎  ⏎ He is in fact an infantile higher-dimensional creature akin to Ende the Devourer, and though Ende summoned him to use as a spare life for himself, Spero escaped from the Keepers to avoid that fate. ⏎  ⏎ Although he feeds on human emotions in the same way Ende does, his encounters with countless people ultimately send him down a path that leads him to become Ende's opposite, favoring human emotions such as hope, love, and joy.

### dic\_pilot\_SAIZOU\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b006\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課の主任。２７歳。 ⏎ 　三課では試作機「ティラネード」のメインパイロットを務める。 ⏎ 　サラリーマンである事に誇りを持ち、業務の遂行に生命を懸けているが、それ以外の事には無頓着であり、周囲からは奇人と見られている。 ⏎ 　その無頼な言動は、いい言い方をすれば「ワイルド」、悪い言い方をすれば「傍若無人」であり、「ネクタイを締めた野生の獣」として陰では「野獣ネクタイ」と呼ばれている。 ⏎ 　ＶＴＸ入社前はエアレースのプライベーターであり、一匹狼的な性格は、その頃に由来する。入社後数年は、その性格が災いして社内で孤立気味であったが、アマサキ係長（当時）の指導によって皆で力を合わせるサラリーマンの生き方に感銘を受け、以降は会社の一員である事に強い誇りを持つようになる。 ⏎ 　しかし、それ故にプライベートな時間が軽視されており、周囲の人間には呆れと心配が混じった感情を向けられている。 ⏎ 　黎明戦争後は「ＶＴＸユニオンの社長になる」という新たな目標を掲げ、特務三課を引っ張っていくようになった。
> EN (odniesienie oficjalne, NIE polski): Chief of the VTX Union Co.'s Special Section 3. Age 27. ⏎  ⏎ He serves as Section 3's main pilot for the experimental Tyranado. ⏎  ⏎ To him, being a salaryman is something to be proud of; he's dedicated to his job, but otherwise relatively indifferent to most other things, which serves to give others the impression that he's a bit strange. ⏎  ⏎ His crude attitude can be said to be free and unbound...in a positive light. In a more negative light, one could say he has no consideration for others at all. This leads to some calling him a "beast with a necktie", or simply "the necktie beast", behind his back. ⏎  ⏎ Prior to joining VTX, he was an air-race privateer, and his solo-flying attitude is a leftover from his speed demon days. A few years after joining VTX, his personality caused him trouble and threatened to isolate him, but manager Amasaki's guidance helped him find value in the life of a salaryman, of being someone who works together with the people around him, and ever since he has been fiercely proud of being a member of the company. ⏎  ⏎ This had the side effect of making him disregard his personal time, which earns confusion and concern from the people around him. ⏎  ⏎ Following the Daybreak War, he found a new goal for himself—to become president of VTX Union Co., a goal which drives him to lead Special Section 3.

### dic\_pilot\_SAIZOU\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b008\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務一課に所属する人物。２７歳。 ⏎ 　一課では試作機のパイロットを務める。 ⏎ 　サラリーマンである事に誇りを持ち、業務の遂行に生命を懸けているが、それ以外の事には無頓着であり、周囲からは奇人と見られている。 ⏎ 　その無頼な言動は、いい言い方をすれば「ワイルド」、悪い言い方をすれば「傍若無人」であり、「ネクタイを締めた野生の獣」として陰では「野獣ネクタイ」と呼ばれている。 ⏎ 　黎明戦争後、特務一課の廃止に伴い、特務三課に転籍となった。
> EN (odniesienie oficjalne, NIE polski): A member of the VTX Union Co.'s Special Section 1. Age 27. ⏎  ⏎ A test pilot for Special Section 1, to him being a salaryman is something to be proud of. He's dedicated in pursuit of his job but otherwise relatively indifferent to most other things, which serves to give others the impression that he's a bit strange. ⏎  ⏎ His crude attitude can be said to be free and unbound...in a positive light. In a more negative light, one could say he has no consideration for others at all. This leads to some calling him a "beast with a necktie", or simply "the necktie beast", behind his back. ⏎  ⏎ Following the Daybreak War, he was reassigned to Special Section 3 following Section 1's dissolution.

### dic\_pilot\_SAGIRI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b00a`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b00a\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課の主任。２７歳。 ⏎ 　三課では試作機「ティラネード」のメインパイロットを務める。 ⏎ 　可憐なルックスを持ちながら、「ずぼら、大雑把、テキトー」な性格により、見た目とのギャップで「堕天使」の異名を持つ。 ⏎ 　その天才的な操縦技術が社内でも注目されているが、本人は至ってマイペースであり、「給料とボーナスのために働く」と公言している。 ⏎ 　そういった自由な生き方と無意識に繰り出される男前な言動によって、社内に多数の女性ファンを持ち、あだ名の「堕天使」は「天使を堕とす者」の意味も持つ。 ⏎ 　入社時の配属希望先は「食品部門でお菓子の企画」であったが、適性検査によって高い操縦能力を持つ事が判明し、その方面の配属となった過去を持つ。 ⏎ 　なお、照れ屋な所があり、その自由奔放な言動は照れ隠しである事が多い。主任に任命された後も柄ではないとして部下達には「センパイ」と呼ばせていたが、それは力不足の自分に対するためらいのためでもあった。 ⏎ 　黎明戦争後は、周囲から「いつかはＶＴＸユニオンの社長に！」と担ぎ上げられ、特務三課を引っ張っていくようになった。
> EN (odniesienie oficjalne, NIE polski): Chief of the VTX Union Co.'s Special Section 3. Age 27. ⏎  ⏎ She serves as Section 3's main pilot for the experimental Tyranado. ⏎  ⏎ Contrary to her neat, dignified appearance, she is in fact a very careless slob, and the cavernous gap between these two sides of her has earned her the nickname "Fallen Angel". ⏎  ⏎ While her genius-level piloting skills have earned her a great deal of attention within VTX, she nonetheless does things as she alone sees fit, stating simply she "works solely for the salary and bonuses". ⏎  ⏎ Her open and frank ways and unconscious masculine-esque attitude have earned her many fans amongst the women of the company, to the point that her nickname "Fallen Angel" is taken to mean that she's the one who makes angels fall. ⏎  ⏎ While she originally applied to join the foodstuffs division as part of the sweets design team, testing discovered her piloting abilities and so she was ultimately assigned to her current posting. ⏎  ⏎ She is easily embarrassed, and no small portion of her freewheeling attitude helps to disguise it. ⏎  ⏎ While she asked her staff to refer to her casually after she became chief, in truth this was not just because it didn't suit her, but also because of her own feelings of impostor syndrome. ⏎  ⏎ After the Daybreak War, people started insisting she will be the VTX Union president someday, and she is rising to the role of leader for Special Section 3.

### dic\_pilot\_SAGIRI\_S\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:94e0b00c`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:94e0b00c\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務一課に所属する人物。２７歳。 ⏎ 　一課では試作機のパイロットを務める。 ⏎ 　可憐なルックスを持ちながら、「ずぼら、大雑把、テキトー」な性格により、見た目とのギャップで「堕天使」の異名を持つ。 ⏎ 　その天才的な操縦技術が社内でも注目されているが、本人は至ってマイペースであり、「給料とボーナスのために働く」と公言している。 ⏎ 　そういった自由な生き方に惹かれてか、社内に多数の女性ファンを持つ。 ⏎ 　黎明戦争後、特務一課の廃止に伴い、特務三課に転籍となった。
> EN (odniesienie oficjalne, NIE polski): A member of VTX Union Co.'s Special Section 1. Age 27. ⏎  ⏎ She served as a test pilot for Special Section 1. ⏎  ⏎ Contrary to her neat, dignified appearance, she is in fact a very careless slob, and the cavernous gap between these two sides of her has earned her the nickname "Fallen Angel". ⏎  ⏎ While her genius-level piloting skills have earned her a great deal of attention within VTX, she nonetheless does things as she alone sees fit, stating simply she "works solely for the salary and bonuses". ⏎  ⏎ Her open and frank ways and unconscious masculine-esque attitude have earned her many fans amongst the women of the company. ⏎  ⏎ Following the Daybreak War, he was reassigned to Special Section 3 following Section 1's dissolution.

### dic\_pilot\_RAMYY\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9520b000\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課に配属された新入社員。２０歳。 ⏎ 　三課では試作機「ティラネード」のコ・パイロットを務める。 ⏎ 　地球連邦軍の軍事大学を飛び級で卒業した才媛であり、ＶＴＸユニオンでは戦術研究課に配属される予定であったが、ゴードウィン社長の薦めによって特務三課の所属となった。 ⏎ 　性格は真面目であるが、融通の利かない所があり、一度悩み始めるととことんまで考え込んでしまうクセがある。 ⏎ 　惑星ダーブネス出身であり、クォーク・ドライブ試作機と共に３年前に地球へとたどり着く。その後、ゴードウィン社長の保護を受け、アマサキ家の養女となった。 ⏎ 　本来の髪の色は青色であるが、ナノマシンによるカラーリングで地球人風の髪色にしている。これは異星人である事を隠すと同時に、地球人のファッションスタイルを好むラミィの趣味のためである。 ⏎ 　養父である特務三課のヒロスケ・アマサキ課長を実父同様に慕っており、完全に地球での生活に適応し、それを楽しんでいる。
> EN (odniesienie oficjalne, NIE polski): A new employee assigned to VTX Union Co.'s Special Section 3. Age 20. ⏎  ⏎ She serves as the copilot of Section 3's experimental Tyranado. ⏎  ⏎ As a rare talent who graduated early from the EFF's military college, she was a shoo-in for VTX Union's tactical section, but was instead assigned to Section 3 at President Goldwin's recommendation. ⏎  ⏎ While a serious, devoted person, she is worryingly inflexible and often vulnerable to becoming trapped in the maze of her own cares and fears once something starts eating at her. ⏎  ⏎ Originally from Planet Darbness, she arrived on Earth three years ago alongside the test version of the Quark Drive. After arriving, she was taken in by President Goldwin, and was then adopted by the Amasaki family. ⏎  ⏎ Her hair is actually naturally blue, and is colored to look similar to Earthlings through the use of nanomachines. Naturally, this serves to disguise her extraterrestrial origins, but it also reflects Rami's fashion choices as she appreciates this aspect of Earthling culture. ⏎  ⏎ She cares for her adopted father Hirosuke Amasaki as though he is her real father and has adapted to life on Earth happily.

### dic\_pilot\_AMASAKI\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9520b002\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課の課長。５２歳。 ⏎ 　プロジェクトＴＮＤの責任者であり、統合戦術支援機「キャリアクス」の操縦を担当している。 ⏎ 　腰の低い温和な人物で、普段の業務は部下それぞれの自主性に任せている。 ⏎ 　その育成能力には定評があり、何人もの問題社員を一人前に育て上げた実績を持っている。 ⏎ 　ＶＴＸユニオン入社前は軍人であり、その頃からの知り合いであるダイマ・ゴードウィン社長とはプライベートでも付き合いがある。 ⏎ 　軍人時代はダイマ・ゴードウィンの上官であり、強い正義感を持ちながらも独善的な彼に他人と協調して物事を成し遂げる事の大切さ…「サラリーマンの意味」を学ばせたいと考え、共にＶＴＸに入社した過去を持つ。 ⏎ 　妻との間に子供が出来なかったため、養女であるラミィを実の娘のように可愛がっているが、彼女が結婚する日の事を思ってしんみりしてしまう事もある。
> EN (odniesienie oficjalne, NIE polski): Section manager of VTX Union Co.'s Special Section 3. Age 52. ⏎  ⏎ He is Project TND's chief manager, as well as the pilot of the tactical support unit Carriax. ⏎  ⏎ A humble, peaceful man, he is generally happy to let his staff manage themselves. ⏎  ⏎ He's well respected for his ability to drive the growth of people under him, and many of the company's problem employees have been molded into respectable team members in his hands. ⏎  ⏎ Prior to joining VTX, he was a military man, and he's been a personal acquaintance of President Dyma Goldwin since his military days. ⏎  ⏎ In the military, he was Dyma Goldwin's superior, and while he was impressed with Goldwin's strong sense of justice, he wanted to teach Goldwin to overcome the self-righteous mindset that kept him from working with others. ⏎  ⏎ To this end, they joined VTX together so he could teach Goldwin the spirit of a salaryman. ⏎  ⏎ Despite Hirosuke and his wife being unable to conceive a child, he loves his adopted daughter Rami as dearly as if she were their own. He gets very depressed when thinking of the day she goes off to get married.

### dic\_pilot\_MERIL\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9520b004\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課の課員。２４歳。 ⏎ 　以前は技術部第一課で火器の開発をしていたため、三課ではティラネードの整備と各種火器の調整をしている。 ⏎ 　また、統合戦術支援機「キャリアクス」のオペレーターを務め、外部からティラネードの火器管制を担当する。 ⏎ 　一見するとクールで理性的だが、非常に短気かつ一本気であり、「鬼火のメリル」と陰で呼ばれている。その性格ゆえに周囲とのトラブルが絶えず、優秀ではあったが、問題社員のレッテルを貼られていた。 ⏎ 　本人は、そういった自分を恥じており、何とか改善しようとしていたが、特務三課で信頼できる仲間達に出会い、徐々に性格は円くなっていった。 ⏎ 　なお否定してはいるが、可愛いものが大好きで、その対象は小動物から小物、果ては少年少女にまで及ぶ。
> EN (odniesienie oficjalne, NIE polski): Staff member of VTX Union Co.'s Special Section 3. Age 24. ⏎  ⏎ Formerly part of Technology Section 1, in charge of developing weaponry, she is now responsible for the management of the Tyranado and its armaments. ⏎  ⏎ She is also an operator aboard the tactical support unit Carriax, managing the Tyranado's weapons externally. ⏎  ⏎ She normally projects an air of being collected and logical, but in reality is short-tempered and very single-minded to the extent she's sometimes referred to as Meltdown Meryl (outside of earshot). ⏎  ⏎ As a result, despite her skills she was an endless source of trouble to the people she had to work with, earning her a label as a major, unquestioned "problem employee". ⏎  ⏎ She herself feels ashamed at how she acts and wants to change, and she gets a chance through her encounters with her new comrades in Section 3, helping her slowly soften her edges. ⏎  ⏎ She would deny it openly but she loves anything cute, including animals, trinkets, and the like.

### dic\_pilot\_EIMIS\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b006`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9520b006\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの特務三課の課員。２４歳。 ⏎ 　以前は総務部に所属しており、経理課の経験もあるため、特務三課の庶務全般を受け持っている。 ⏎ 　また、統合戦術支援機「キャリアクス」のオペレーターを務め、情報処理技術を活かし、通信と索敵を担当する。 ⏎ 　愛らしいルックスと柔らかな人当たり、細やかな気配りに勘違いする男性社員が後を絶たず、トラブルの元となっていたが、それらを遠慮のない辛辣な言動でやり込める事から「ミス・ストレート」の異名を持つ。　 ⏎ 　本人は、そういった自分を恥じており、何とか改善しようとしていたが、特務三課で信頼できる仲間達に出会い、その毒舌は軽口レベルまで緩和された。 ⏎ 　が、まれに腹黒な言動が見られ、同僚のメリルを恐れさせている。
> EN (odniesienie oficjalne, NIE polski): Staff member of VTX Union Co.'s Special Section 3. Age 24. ⏎  ⏎ Formerly a part of the general affairs department, she is now in charge of handling similar duties for Special Section 3 specifically. She also serves as an operator aboard the full tactical support unit Carriax, using her information management skills to handle communications and sensors. ⏎  ⏎ Her charming appearance and gentle front, combined with her meticulous and exacting work attitude, has left in her wake a trail of male employees who "misread" the situation. ⏎  ⏎ While that makes her an unfortunate source of trouble (of sorts), she fends such accusations (and woebegotten suitors) off easily with a few pointed jabs of the utterly merciless scathing comments that earned her the nickname "Miss Straight". ⏎  ⏎ She herself isn't entirely proud of how quickly the thorns can come out and would like to change, and she gets a chance through her encounters with her new comrades in Section 3, softening the edges of her tongue. Somewhat. ⏎  ⏎ Still, her colleague Meryl finds her fearsome as she catches the occasional glimpse of her darker side.

### dic\_pilot\_NEBLNNA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9520b008`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9520b008\]
> JP (źródło tłumaczenia): 　超文明ガーディムが開発した文明再建システム。 ⏎ 　自律型のＡＩであり、女性の人格を有している。 ⏎ 　その性格形成には、端末であるナンバー２０４４の集めたデータが大きな影響を与えており、強い責任感と覚悟、使命遂行の障害に対する不屈の闘志を持っている。 ⏎ 　内部には超文明ガーディムを構成する、あらゆるデータが保存されており、崩壊寸前であったガーディム本星から少数のガーディム人と共に銀河系へと逃げ延びた。 ⏎ 　システムを起動させた場合、周囲の環境をガーディム人にとって最適なものに改造し、周辺の資源を使用して文明を再建するというプロセスを取る。 ⏎ 　使命遂行の障害を排除し、ガーディム文明を守るための戦闘機能も有しており、その手段として自らの肉体となる機動兵器アーケイディアを造り上げた。 ⏎ 　スレイブナンバー２０４４ことナインの集めたデータを取り込む事で、人間を超えた存在を自称したが、自らが理解できなかった「愛」という感情への恐れから自滅する。 ⏎ 　しかし、最終的には自らの非を悟り、自身の使命をナインに託して散っていった。
> EN (odniesienie oficjalne, NIE polski): The civilization reconstruction system created by the Supercivilization Gardim. ⏎  ⏎ She is a fully sapient AI with a female personality. Much of her personality is based on data received from terminal number 2044, giving her a strong will and sense of responsibility, as well as an unflagging hostility to anything that would obstruct her mission. ⏎  ⏎ She carries inside her a complete dataset of every element of Gardim, whose people left their home planet with her in tow just prior to that world's destruction. ⏎  ⏎ When activated, the system's purpose is to transform the local environment into one suitable for the people of Gardim, collect available resources and use them to rebuild Gardim society. ⏎  ⏎ In order to remove potential obstacles, and also to defend the legacy of Gardim, she is equipped with combat capability and constructed the mobile weapon Arcadia as a body to use in combat. ⏎  ⏎ While she believes the data provided by Nine, a.k.a. Slave 2044, has made her into a superior being to humans, it is her fear of "love", a concept she failed to understand, that spelled her defeat. ⏎  ⏎ Even so, in her last moments she accepted her own wrongdoing and entrusted her mission to Nine before meeting her end.

### dic\_pilot\_ENDE\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b000`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9560b000\]
> JP (źródło tłumaczenia): 　アル・ワースの創造主。 ⏎ 　人知を越えた超絶的な力を持つ高次元生物であり、その意思の力で認識宇宙内にアル・ワースを創り上げた。 ⏎ 　その目的は、そこに人間を繁殖させ、そこで生まれる感情を食する事にあり、人間の悲しみや苦しみや絶望を好む。それらを生み出すために魔従教団を組織し、アル・ワースの戦乱を望むままにコントロールしてきた。 ⏎ 　その食事は生きていくために必須というわけではなく、あくまで自らの快楽のためのものであり、人間の言葉で表現すれば、残酷で無慈悲なエゴイスト。 ⏎ 　既に３０００年以上の時を生きており、いつかは寿命が尽きると考え、自らのスペアとなる「精神・肉体・生命」を求めている。 ⏎ 　その死後もアル・ワースは、そこに住む人々の願いによって存在し続けた。
> EN (odniesienie oficjalne, NIE polski): The creator of Al-Warth. He is a higher dimensional creature possessed with unbelievable power who manifested Al-Warth into observable reality solely through the power of his will. ⏎  ⏎ His goal was to have humanity live there, which would allow him to feast on their emotions, with a specific taste for despair, sadness, pain, and other such feelings. ⏎  ⏎ To ensure this came to pass, he also founded the Keepers of Order and through them manipulated the tides of war to his will. ⏎  ⏎ Despite the metaphor of food being used when describing him, he does not consume emotions to survive as such, and humans would describe him as a cruel, merciless egoist. ⏎  ⏎ While he has lived for over three thousand years, he is aware that he will die, and seeks a spare "mind, body, and life" to ensure his continuity. ⏎  ⏎ Following his death, Al-Warth remains in existence, now instead sustained by the wishes of its inhabitants.

### dic\_pilot\_DAIMA\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b002`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9560b002\]
> JP (źródło tłumaczenia): 　株式会社ＶＴＸユニオンの元社長。４８歳。 ⏎ 　豪腕で知られる人物であり、３８歳という若さで世界的大企業であるＶＴＸユニオンの社長に就任し、そこから１０年間、世界の経済界をリードしてきた存在。 ⏎ 　ワンマン経営で内外に敵も多いが、その器の大きさに心酔し、命を投げ出す覚悟で付き従う人間も多い。 ⏎ 　強い意志を持ち、一度決めた事は曲げないが、経営に対しては柔軟な思考でＶＴＸを幅広い分野へと進出させた。 ⏎ 　入社前は軍人であり、スーパーロボット「ガイアーン」を駆り、人類の敵と戦ってきた英雄であった。 ⏎ 　しかし、自らの死を偽り、かねてから画策していた「銀河統一計画」を実行に移す。ＶＴＸユニオンの資産を流用して造り上げた「機動要塞ＶＴＸ」と絶対決戦兵器「ダイガイアン」を駆り、新たなる地球の守護者を自称した。 ⏎ 　「銀河統一計画」を心の底から人類のためになると信じており、その遂行こそが自らの使命であり、正義であると考えていた。 ⏎ 　ＶＴＸユニオンの社長業を務めながら、ダイガイアンのパイロットとして再び戦場に立つ日のためにトレーニングに明け暮れ、軍人時代以上の戦闘力を持つ。 ⏎ 　敗北の後は自分の非を認めて投降し、その計画は終焉を迎えた。
> EN (odniesienie oficjalne, NIE polski): The former president of VTX Union Co. Age 48. ⏎  ⏎ Known to be incredibly capable, he became president of VTX Union at the relatively young age of 38 and has held the reins of world economics for over ten years. ⏎  ⏎ He handles everything himself at the management level and has many enemies inside and outside the company, but his capabilities also inspire a fervor in others that make them follow him even at the cost of their lives. ⏎  ⏎ While generally the sort to never go back on a decision, his flexible thinking as a manager has enabled VTX to develop across countless fields of business. ⏎  ⏎ Prior to joining the company, he was a military man, a hero who fought the enemies of humanity aboard the super robot Gaian. Later, he faked his own death and set out to execute what he referred to as the Galactic Unification Plan. ⏎  ⏎ He used the resources of VTX to construct the Mobile Fortress VTX, as well as the "ultimate victory weapon" Dygaian, proclaiming himself Earth's new guardian. ⏎  ⏎ He sincerely and truly believes the Galactic Unification Plan is in humanity's best interest and feels it his duty to see this "moral good" completed. ⏎  ⏎ While serving as president of the company, he also trained to ensure he would be able to stand on the battlefield once more aboard Dygaian, making him even more capable than in his military days. ⏎  ⏎ Following his defeat, he surrendered, signaling the end of his plan.

### dic\_pilot\_CLREUM\_00\_0

Adres: `dic\_text\_pilot/01fdb9ba:9560b004`

> \[BRAK PL: dic\_text\_pilot/01fdb9ba:9560b004\]
> JP (źródło tłumaczenia): 　クエスターズの実行部隊隊長。 ⏎ 　第１２銀河の戦闘種族ヴァウルーガの民であり、仲間達と共にクエスターズにスカウトされたという経歴を持つ。 ⏎ 　クエスターズ指導者の代理人として、地球文明の調査や実験を主任務とする。 ⏎ 　「先生」によって、審判の後に地球の王になる事を指示されており、その証として与えられる機体・ヴァリンの最上位機であるグラヴァリンを駆る。 ⏎ 　しかし、地球文明との接触の中、真理の探究者の一員らしく様々なものに興味を持った結果、傲慢さは徐々に消えていき、新鮮な体験の連続に驚く純粋さが目立つようになる。さらには自らと「先生」の関係にまで疑問を持つに至る。 ⏎ 　その正体は、他のクエスターズの構成員と同じく「先生」のクローンであり、記憶も思考も「先生」に用意されたものであった。 ⏎ 　「先生」の死後は「次元の番人」を自称し、知的好奇心を満たすために様々な並行世界を旅している。
> EN (odniesienie oficjalne, NIE polski): The captain of the execution team of the Quaestors. He is one of the Valrouga, a warlike species from Galaxy 12, who was recruited with his fellows into the Quaestors. ⏎  ⏎ As the proxy lead of the Quaestors, he takes the initiative to study and research the civilization of Earth. ⏎  ⏎ Declared by the Magister to be the King of Earth after the planet is judged, he was given the final upgraded version of his machine, the Gravalin, to serve as proof of his title. ⏎  ⏎ Paradoxically, in his encounters with the civilization of Earth, he acted upon his curiosity just as he thought a seeker of truth ought to, and the stream of new experiences gradually peeled back his egotism to reveal a surprising innocence beneath. This would cause him to begin to doubt his relationship with the Magister. ⏎  ⏎ Ultimately it would turn out that he, like all other Quaestors members, were clones of the Magister, and his thoughts and memories were manufactured. ⏎  ⏎ After the death of the Magister he went on to title himself the Keeper of Dimensions, wandering countless parallel dimensions to satisfy his intellectual curiosity.

### dic\_pilot\_KIDJ\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:df20b000`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:df20b000\]
> JP (źródło tłumaczenia): 　本名、木戸丈太郎。 ⏎ 　元地球連邦正規軍レッド・ローズ特別射撃隊所属の凄腕スナイパー。その腕前は１００メートル先のハエをも撃ち落とすほど。あらゆる銃器を使いこなし、高い戦闘力で単独での突入・潜入任務を得意とする。 ⏎ 　クールに気取ってみせるが、図らずも熱い部分が出てしまうナイスガイ。普段は子供っぽさも残る気さくで陽気な性格だが、悪党には容赦なく引き鉄を引く。 ⏎ 　趣味は愛用の銃磨き、レコードコレクションとギタープレイ。ギターは超人気バンド・レイダースのロニー・ペイジと組んでいたほどの腕前であり、自作のダブルネックギター・ストラトマスターを愛用している。
> EN (odniesienie oficjalne, NIE polski): His real name is Jotaro Kido, former sniper of the Earth military's Red Rose special sniper unit. ⏎  ⏎ He is capable of shooting down a fly at 100 meters with any type of weapon and specializes in solo infiltration missions with his powerful combat abilities. ⏎  ⏎ Though he tries to play it cool, he's actually quite a nice guy who sometimes lets his more passionate side slip through. ⏎  ⏎ Normally he comes across as childish and energetic, but when he's facing down an evildoer, he won't hesitate to pull the trigger. ⏎  ⏎ His hobbies are polishing his beloved guns, collecting records, and playing the guitar. He's talented enough with the guitar to have played side by side with Ronny Page from the mega-popular band the Raiders, and he is often found playing his favorite double-necked Stratomaster, which he himself made.

### dic\_pilot\_BOY\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b001`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfa0b001\]
> JP (źródło tłumaczenia): 　本名、スティーブン・ボウィー。 ⏎ 　太陽系最大のレースであるル・マン・デ・ソールの連続最多優勝記録保持者。　　 ⏎ 　トレードマークはキャップとそばかす。 ⏎ 　アイザックの招きとブライサンダーに魅了されてＪ９のメンバーとなる。　 ⏎ 　ノリの軽い陽気な二枚目半で美人に目がない。彼が困っている美人を助けて事件に巻き込まれるのが、Ｊ９の依頼受理の基本パターン。 ⏎ 　しかし、その内面はナイーブかつ純情で、昔の想い人や恩人へのこだわりを見せる事もある。 ⏎ 　また、独特の口調で一人称は「俺ちゃん」、愛車ブライサンダーを「仔猫ちゃん」と呼ぶ。
> EN (odniesienie oficjalne, NIE polski): His real name is Steven Bowie, and he currently holds the record for most consecutive wins at the Le Mans Desol, the biggest race in the solar system. ⏎  ⏎ His trademarks are his hat and freckles. After being invited by Isaac and instantly falling in love with the Brai-Thunder, he joined J9. ⏎  ⏎ He has a reputation as a laid-back, handsome jokester with a fondness for women. In fact, most of the requests J9 receives come from him getting tangled up in some plot while trying to help a beauty in need. ⏎  ⏎ However, deep down, he has a naive and innocent streak, and he feels deep obligation to past loves and those who have helped him. ⏎  ⏎ He has a unique way of talking about himself, and always refers to his beloved Brai-Thunder as his "kitten".

### dic\_pilot\_MACHI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b003`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfa0b003\]
> JP (źródło tłumaczenia): 　本名、マチコ・ヴァレンシア。 ⏎ 　潜入任務と破壊工作を得意とし、ボンバーギャルの異名を持つ。また、軽やかな身のこなしと女性の武器を最大限に活かしたその情報収集力はＪ９に不可欠の戦力。 ⏎ 　父親は木星開発局の長官であるが、その父の生き方が許せずに家を飛び出し、一時は木星のガリレオ・コネクションの一員だった過去を持つ。 ⏎ 　自由とスリルを愛し、恋に生きる情熱的な性格。
> EN (odniesienie oficjalne, NIE polski): Her real name is Machiko Valencia. ⏎  ⏎ She specializes in infiltration and sabotage, earning her the nickname "bomber girl". ⏎  ⏎ With her airy personality and masterful use of her feminine wiles, she has become an irreplaceable source of information and strategy for J9.  ⏎  ⏎ Her father is the head of the Jupiter Development Division, but due to her father not accepting her lifestyle, she ran away from home and joined the Galileo Connection for a brief period. ⏎  ⏎ She loves freedom and the thrills it brings, and lives her life with burning passion.

### dic\_pilot\_IZAQ\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfa0b005`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfa0b005\]
> JP (źródło tłumaczenia): 　本名、アイザック・ゴドノフ。 ⏎ 　コズモレンジャーＪ９の創設者にしてリーダー。 ⏎ 　高い情報分析力と知略でＪ９の頭脳としてメンバーを指揮し、同時に彼等から絶大な信頼を得ている。 ⏎ 　北欧の貴族の家に生まれるが、幼少に父親が権力争いに巻き込まれて死亡。その後の経歴は謎に包まれているが、アステロイドのウエストゾーンＪ区９番地にあるＪ９基地で始末屋を営むに至る。 ⏎ 　冷めた表情の下で権力と悪を憎む心を燃やす静かなる正義漢。基本的にはどんな困難な依頼でも報酬次第で引き受けるが、自分の気に入らない相手や悪党からの依頼は引き受けないポリシーを持つ。体術も一流で愛用の電子ムチをふるい、悪党には容赦のない一撃を浴びせる。 ⏎ 　普段はクールで物静かであるが、ジョークを解し、身寄りのないシンやメイを引き取る等、人情家としての一面も持つ。 ⏎ 　嫌いなものは金の貸し借りとピーマン、弱点は全く酒が飲めないことである。
> EN (odniesienie oficjalne, NIE polski): His real name is Isaac Godunov, creator and leader of the Cosmo Rangers J9. ⏎  ⏎ With his brilliant analytical and strategic mind, he serves as the brains of J9, handing out orders to the other members, all of whom trust him completely. ⏎  ⏎ He was born to an aristocratic northern European family, but lost his father to a political power struggle at an early age. His life since then is shrouded in mystery, but at some point he began to operate a troubleshooting organization from the J9 base, located in the asteroid belt's West Zone, J Ward 9th District. ⏎  ⏎ Though he has a cold exterior, beneath it is a quiet warrior fighting for justice, whose heart burns with hatred of authority and evil. ⏎  ⏎ For the most part, he will accept any job as long as the price is right, though he does maintain a policy of rejecting requests from evildoers or anyone else he doesn't personally like. ⏎  ⏎ He is a master of martial arts and lashes out ruthlessly at his evil foes with his favorite electric whip. ⏎  ⏎ His cold exterior belies a warm sense of humor and a humanitarian side demonstrated when he took in Sin and Mei despite having no relation to them. ⏎  ⏎ His biggest dislikes are lending money and eating green peppers, and his greatest weakness is his inability to hold his liquor.

### dic\_pilot\_PONCH\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b000`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b000\]
> JP (źródło tłumaczenia): 　裏社会の闇商人にしてＪ９のマネージャー。 ⏎ 　依頼の交渉を受け持つが、アイザックの目を盗んで報酬をちょろまかすことを企む。しかし、生来のおっちょこちょいにより、その策の成功率は極めて低い。 ⏎ 　アイザックには逆らえないようであるが、決して渋々服従しているわけではなく、内心ではＪ９に相当入れ込んでいる。 ⏎ 　また、戦闘時には輸送船ブライ・キャリアを操縦してブライ・カノンの運搬を行う。 ⏎ 　なお、彼の築いた莫大な富は後の世に「パンチョ・ポンチョの隠し財産」として伝説となる。
> EN (odniesienie oficjalne, NIE polski): A black market salesman and the manager of J9. ⏎  ⏎ He handles negotiations for their jobs and sometimes steals a little off the top when Isaac isn't looking. However, due to his natural clumsiness, his rate of success at this is extremely low. ⏎  ⏎ He can't say no to Isaac, but his obedience isn't forced. In reality, he strongly believes in what J9 is doing. ⏎  ⏎ In combat he pilots the Brai-Carrier transport vessel to carry the Brai-Cannon. ⏎  ⏎ The enormous wealth he amassed over his life later became known as the legendary Hidden Treasure of Pancho Poncho.

### dic\_pilot\_ROGER\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b002`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b002\]
> JP (źródło tłumaczenia): 　記憶を失った街「パラダイムシティ」随一のネゴシエイター。２５歳。 ⏎ 　元軍警察警部補としての過去を持ち、軍警察のダストンはかつての上司にあたる。 ⏎ 　ユーモラスかつウィットに富んだ口調で交渉を確実に進めていき、依頼人の期待以上の成果をもたらす。 ⏎ 　基本的にフェミニストで紳士だが、感情が昂りやすい所もあり、こちらの言葉に耳を傾けずに誠意とルールを破る者に対しては実力行使に出る事もある。ただし、どんな危険な仕事に赴く時でも銃は持たない主義。 ⏎ 　自分の考えを曲げるのを嫌う頑固者だが、ドロシーが猫を飼いたいと言ってきた時など、結局は願いを聞き入れてしまうお人良しの面も持つ。 ⏎ 　ビッグオーを操縦するメモリーを持ち、ビッグオーと共に巨悪に立ち向かっていく。それは正義の味方を気取っての行為ではなく、誠意や人としてのルールを破った者に対し、自らの法を以て当たった結果である。なお、ロジャー自身は、自分が何故ビッグオーを操縦できるメモリーを持つかをわからない。 ⏎ 　アウト・オブ・ドームにある朽ちた銀行を屋敷としている。彼の屋敷に住む者は皆黒い服を着る決まりがある。また、彼の屋敷に無条件で入れるのは女性だけである。 ⏎ 　趣味は砂時計の収集。 ⏎ 　さわやかな目覚めをとても大切に考えているものの、寝起きが悪いためにドロシーの極端なピアノ演奏で起こされる事もある。
> EN (odniesienie oficjalne, NIE polski): The number one negotiator in Paradigm City, the city that has lost its memory. ⏎  ⏎ Twenty-five years old. Dastun, the chief of the Military Police, is his former commanding officer. ⏎  ⏎ His sense of humor and wit give him a startling eloquence that often proves key in negotiation and ensures he always exceeds his clients expectations. ⏎  ⏎ He is generally chivalrous and a gentleman, but he can be swayed by his emotions and is not too shy about using force against people who try to stonewall him, act disrespectfully, or break the rules. Despite this, he makes a point of never carrying a gun no matter how dangerous the situation he faces is. ⏎  ⏎ While he tends to be extremely stubborn in his decision-making, he also can be very caring, such as when he changed his rules to let Dorothy keep a cat. ⏎  ⏎ He has the Memories needed to pilot Big O, and uses Big O to face off against oversized threats. However, he does so not out of any belief in himself as a hero but instead simply as justified punishment to those who act without sincerity or break the rules of decent human behavior. ⏎  ⏎ Incidentally, Roger himself has no idea why he has Memories regarding the piloting of ⏎ Big O. ⏎  ⏎ Roger lives in an abandoned bank on 72nd street, just outside one of the domes. His favorite color is black, and he insists that anyone residing with him must wear all black to match. Only women are allowed to break this rule when visiting. ⏎  ⏎ He collects hourglasses as a hobby. ⏎  ⏎ While he prefers a languid, peaceful rise from bed, these days he is often woken up in the morning by Dorothy's intense piano performances.

### dic\_pilot\_DRTHY\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b004`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b004\]
> JP (źródło tłumaczenia): 　ティモシー・ウェインライトによって、彼の娘そっくりに作られたアンドロイド。ただし体重は１３０キログラムある。 ⏎ 　ソルダーノ重工令嬢誘拐事件に端を発する一連の事件をきっかけに、報酬の肩代わりの名目でロジャーの屋敷にいついてしまった。 ⏎ 　アンドロイドとしての完成度が高いだけでなく、猫に愛情を注ぎ、恋愛に関する質問をロジャーに投げかけるなど、非常に人間に近い存在として制作されている。そのためロジャーは、時々彼女がアンドロイドである事を忘れてしまう。 ⏎ 　無愛想で傍若無人な態度は、時にロジャーを閉口させるが、時が経つにつれ彼の良きパートナー的存在となっていった。 ⏎ 　頭部のカチューシャ部分はメモリードライブになっており、しばしば光源としても利用された。 ⏎ 　ピアノ演奏を趣味としているが、当初のレパートリーは激しい曲調のものばかりであった。だがピアニストアンドロイドのＲ・インストルの指導により、徐々に演奏の幅を広げていった。
> EN (odniesienie oficjalne, NIE polski): An android created by Timothy Wayneright in the image of his daughter. The only difference is her weight; the scales measure her at 130kg. ⏎  ⏎ Her involvement in the Soldano kidnapping case set off a chain of events that led to her serving at Roger's mansion in lieu of payment. ⏎  ⏎ She is an extremely advanced android who displayed complex expressions to Wayneright, showed love for a pet cat, and brings up questions of love to Roger, displaying tremendously human-like qualities. ⏎  ⏎ Roger himself sometimes forgets she is, in fact, an android. ⏎  ⏎ Her usual flat and brusque attitude can leave Roger speechless, but as they spend time together, she turns into a treasured partner, of sorts, for Roger. ⏎  ⏎ Her "hairband" is a storage slot that contains her memory drive, and the casing can be used as a light source if needed. ⏎  ⏎ Her hobby is playing the piano, and although her repertoire originally only had very intense pieces, lessons with a pianist android by the name of R. Instro have helped expand her musical skills.

### dic\_pilot\_SHVRT\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b006`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b006\]
> JP (źródło tłumaczenia): 　４０年以上前に失われたメモリーの正体を探究する男。 ⏎ 　かつてはマイクル・ゼーバッハという名のパラダイムプレスの新聞記者だったが、真実を追い求める事に取り憑かれた結果、正気を失ってしまった。地下回廊の底でメガデウスのアーキタイプを発見する。 ⏎ 　なお、シュバルツバルトとはドイツ語で「黒い森」を意味する。 ⏎ 　その後ビッグデュオを発見し、ロジャーに対決を挑むも敗北。その時にひとりでに動き出したビッグデュオを見て驚愕し、表舞台から姿を消した。 ⏎ 　まるで詩を朗読するかのような口調で話し、真実を探究せず、思考することを止めた人間は価値のない生き物だと考えている。
> EN (odniesienie oficjalne, NIE polski): A man in pursuit of the truth of the Memories lost forty years ago. ⏎  ⏎ Once a newbie reporter working for Paradigm Press under the name Michael Seebach, his search for the truth took hold of him, driving him insane. In his mad quest, he discovered the Megadeus archetype in the depths of the underground labyrinth. ⏎  ⏎ His name, Schwarzwald, means "Black Forest" in German. ⏎  ⏎ Later he discovered Big Duo, which he used to challenge Roger in battle, and lost. Struck with shock when Big Duo then began moving on its own, he vanished, but his influence continued to be felt. ⏎  ⏎ He speaks in a poetic tone that implies deeper meaning, and views people who live without thinking or seeking truth as worthless animals.

### dic\_pilot\_BECK\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b008`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b008\]
> JP (źródło tłumaczenia): 　パラダイムシティで悪事を重ねる犯罪者。２２歳。 ⏎ 　下品な笑いと共に現れ、銀行強盗や誘拐、詐欺などあらゆる犯罪に手を染める。その言動はチンピラそのもので、ロジャーからはプロたる資格なき犯罪者だと思われる。 ⏎ 　メガデウスの操縦にとって重要なインターフェイス代替技術のメモリーを持っているため、メガデウスを調達しては犯罪に使用している。 ⏎ 　ソルダーノ令嬢誘拐事件でロジャーに刑務所に送られてからは、彼を「カラス野郎」と呼んで復讐を誓う。その後は脱獄を繰り返しては、ロジャーに引導を渡すべく幾度となく策を弄する。
> EN (odniesienie oficjalne, NIE polski): A criminal responsible for much of the modern villainy in Paradigm City. 22 years old. ⏎  ⏎ He gladly dirties his hands with any crime, from kidnapping to bank robbery to fraud, accompanied by his trademark crude laugh. In truth, he's little more than a small-time punk with too-large robots, and Roger describes him as a criminal who has none of the qualities of a true professional. ⏎  ⏎ He possesses a key Memory regarding the engineering and construction of Megadeus control interfaces, which he takes advantage of to use Megadeuses in his crimes. Ever since Roger was dispatched against him in the Soldano kidnapping incident, he's burned for revenge against Roger, who to Beck is "that damn crow". This has led to him managing to escape from prison on several occasions, always with a plot to finally get one over on Roger.

### dic\_pilot\_DAV\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00a`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b00a\]
> JP (źródło tłumaczenia): 　ベックの部下の色白の男。 ⏎ 　女性口調で話すのが特徴。
> EN (odniesienie oficjalne, NIE polski): Beck's lighter-colored underling. He speaks in a feminine fashion.

### dic\_pilot\_TBON\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00c`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b00c\]
> JP (źródło tłumaczenia): 　ベックの部下の小太りの男。 ⏎ 　ダヴと共にベックを脱獄させた。
> EN (odniesienie oficjalne, NIE polski): Beck's smaller, rounder underling. He's always imprisoned with Beck and Dove.

### dic\_pilot\_SHOTA\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b00e`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b00e\]
> JP (źródło tłumaczenia): 　鳴海探偵事務所に所属する私立探偵。 ⏎ 　ハードボイルドを気取るが、完全には徹しきれない二枚目半であり、周囲から「ハーフボイルド」と言われる事もある。 ⏎ 　情に厚い好漢であり、その行動力と強い意志は周囲の人間を巻き込んでいく。 ⏎ 　生まれ育った風都を愛し、私立探偵としてトラブルを解決すると同時に、相棒のフィリップと共に仮面ライダーＷとなり、ドーパントとガイアメモリに関する事件に立ち向かっていく。
> EN (odniesienie oficjalne, NIE polski): The Narumi Detective Agency's private investigator. ⏎  ⏎ His attempts to act "hard-boiled" always end in a comical pratfall. In fact, most people who know him call him "half-boiled". ⏎  ⏎ But he wears his heart on his sleeve, spares no effort to help someone in need, and stands up for his principles no matter what, so others can't help but follow along. ⏎  ⏎ He was born and raised in Fuuto and loves it with all his heart. This drives him to lead his double life: as a private investigator who protects his beloved city from threats, and together with Philip, as Kamen Rider Double, solving cases related to Dopants and Gaia Memories.

### dic\_pilot\_PHILP\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b010`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b010\]
> JP (źródło tłumaczenia): 　翔太郎の相棒。 ⏎ 　飽くなき好奇心と冷静な判断力、脳内にある「地球（ほし）の本棚」への検索により、翔太郎の頭脳として活躍する。 ⏎ 　翔太郎と共に仮面ライダーＷとなり、ドーパントとガイアメモリに関する事件に立ち向かっていく。 ⏎ 　理論・理屈を重視する故にコンビを組んだ当初は翔太郎の感情を理解できなかったが、戦いの中、翔太郎の行動に感化されて心情を変化させていき、強い信頼で結ばれたパートナーとなっていった。
> EN (odniesienie oficjalne, NIE polski): Shotaro's partner. ⏎  ⏎ He serves as the brains of the pair. His assets are his inexhaustible curiosity, a cool head for rational decision-making, and the ability to access and perform searches on the Gaia Library within his own mind. ⏎  ⏎ Together with Shotaro, he transforms into Kamen Rider Double to deal with cases involving Dopants and Gaia Memories. ⏎  ⏎ At first, his logical outlook put him at odds with Shotaro's more emotional approach. As they fought together, however, Shotaro made an impression on him, and his feelings changed. He and Shotaro gradually grew together as partners with an unbreakable bond of trust.

### dic\_pilot\_TOKI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:dfe0b012`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:dfe0b012\]
> JP (źródło tłumaczenia): 　風都の住民に「Ｔ字路の魔女」と噂されていた謎の女性。 ⏎ 　当初はロード・ドーパントの正体として目されていたが、翔太郎の調査により、疑いが晴れる。 ⏎ 　記憶の一部が欠けており、自身の素性も思い出せないが、事件後は鳴海探偵事務所で翔太郎の助手として活動する事になる。
> EN (odniesienie oficjalne, NIE polski): A mysterious girl who became known to the people of Fuuto as the "T-intersection witch". ⏎  ⏎ She was suspected of being the Road Dopant, but Shotaro's investigation cleared her name. ⏎  ⏎ She's missing some of her memories, including her real name and past. After the initial case is cleared up, she joins the Narumi Detective Agency as Shotaro's assistant.

### dic\_pilot\_AKIK\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b000`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b000\]
> JP (źródło tłumaczenia): 　鳴海探偵事務所の所長。 ⏎ 　自身は探偵ではなく、事務や雑務を引き受けている。 ⏎ 　大阪育ちでスリッパを使ったツッコミが得意技。 ⏎ 　行動力にあふれ、トラブルメーカーな所もあるが、父親であり、翔太郎の師である鳴海荘吉譲りの正義感を見せる。 ⏎ 　事件の中で知り合った照井竜と結婚したが、彼からは相変わらず「所長」と呼ばれている。
> EN (odniesienie oficjalne, NIE polski): The chief of the Narumi Detective Agency. ⏎  ⏎ Not being a detective herself, she handles admin, accounting, and other errands. ⏎  ⏎ Proudly raised in Osaka, she strikes down stupidity with a sharp smack of her signature slapstick slipper. ⏎  ⏎ Her energy and enthusiasm often get her into trouble, but they also come with a strong moral compass inherited from her father and Shotaro's mentor, Sokichi Narumi. ⏎  ⏎ She met Ryu Terui in the course of their work. The two are now married, but he still calls her Chief like he did back then.

### dic\_pilot\_TERU\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b002`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b002\]
> JP (źródło tłumaczenia): 　風都署の超常犯罪捜査課に所属する刑事。 ⏎ 　仮面ライダーアクセルへと変身し、ガイアメモリ犯罪を追う。 ⏎ 　当初は鳴海探偵事務所とは距離をとっていたが、共に事件を追う中、信頼関係が生まれ、所長の亜樹子とは結婚するに至った。 ⏎ 　表面的にはクールに振る舞うが、その裏には激情を秘めている。 ⏎ 　なお、他人に質問される事を嫌い、「俺に質問をするな」と先制することが多い。
> EN (odniesienie oficjalne, NIE polski): A police detective with Fuuto PD's Paranormal Crime Division. ⏎  ⏎ He becomes Kamen Rider Accel to investigate Gaia Memory crimes. ⏎  ⏎ When he first arrived, he kept a healthy distance with the Narumi Detective Agency, but as their paths kept crossing, he came to trust them and ultimately married their chief, Akiko. ⏎  ⏎ He hides his intense emotions under a cold facade. ⏎  ⏎ He hates answering questions and, in response, usually snaps "Do not question me!".

### dic\_pilot\_RIDERW\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b004`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b004\]
> JP (źródło tłumaczenia): 　左翔太郎とフィリップが、ダブルドライバーとサイクロンメモリ、ジョーカーメモリで変身した姿。 ⏎ 　使用するメモリから「サイクロンジョーカー」と呼ばれる形態であり、スピードと格闘能力に優れる。素早い格闘攻撃を繰り出しながら、風を取り込んでスタミナを回復させられる。 ⏎ 　ドライバー左右のメモリを入れ替える事によって別の形態へと再変身する事が可能であり、それに応じて特性とカラーが変化する。 ⏎ 　変身時には片方の意識は肉体のベースとなる身体に憑依する形となっている。サイクロンジョーカーの場合、翔太郎の身体にフィリップの意識が融合している。
> EN (odniesienie oficjalne, NIE polski): The form Shotaro and Philip take when they load the Cyclone Memory and the Joker Memory into the W Driver. ⏎  ⏎ This form is named Cyclone Joker, based on the Memories that access it. It vastly improves the users' speed and striking power, allowing them to fight with a rapid onslaught of punches and kicks, while absorbing the power of the wind to restore their energy. ⏎  ⏎ Other Memories can be loaded into the Drivers' respective left and right slots to change forms, each with different colors and powers. ⏎  ⏎ When the two become Double, one of their bodies actually transforms, while the other's consciousness is transferred into it. Cyclone Joker uses Shotaro's body, with Philip's mind sharing it.

### dic\_pilot\_AXEL\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b006`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b006\]
> JP (źródło tłumaczenia): 　照井竜がアクセルドライバーとアクセルメモリで変身した姿。 ⏎ 　アクセルメモリによる加速力の記憶と、それを引き出すアクセルドライバーにより、超加速と高い身体能力を誇る。
> EN (odniesienie oficjalne, NIE polski): The form Ryu Terui takes when he loads the Accel Memory into the Acceldriver. ⏎  ⏎ The Acceldriver harnesses and channels the memory of acceleration, giving its user superhuman strength and incredible speed.

### dic\_pilot\_SOUKITI\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b008`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b008\]
> JP (źródło tłumaczenia): 　鳴海探偵事務所の初代所長。 ⏎ 　ハードボイルドを体現したような私立探偵で、翔太郎の師匠にあたる。 ⏎ 　人知れず仮面ライダースカルに変身し、風都のガイアメモリ犯罪に立ち向かってきた。 ⏎ 　とある依頼を受け、名前と記憶を失った少年フィリップを救出するも、組織「ミュージアム」の凶弾に倒れ、命を落とした。 ⏎ 　彼の意志は、弟子である翔太郎とその相棒フィリップに引き継がれている。
> EN (odniesienie oficjalne, NIE polski): The founding chief of the Narumi Detective Agency. ⏎  ⏎ He is virtually the concept of the hard-boiled PI made flesh, and Shotaro's mentor. ⏎  ⏎ He has a secret alter ego as Kamen Rider Skull, fighting Gaia Memory crime in Fuuto. ⏎  ⏎ One such case was to rescue a young man who had lost his name and memories, later called Philip. It led to his death by gunfire from an organization called the Museum. ⏎  ⏎ His apprentice Shotaro, and Shotaro's partner Philip, would carry on his work.

### dic\_pilot\_SCULL\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00a`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b00a\]
> JP (źródło tłumaczenia): 　鳴海荘吉がロストドライバーとスカルメモリを使用して変身した姿。 ⏎ 　「骸骨」の記憶を持つメモリの力により、肉体が強化されているほか、変身中は不死身となる。 ⏎ 　その身体は冷たく、死者同然といえる。
> EN (odniesienie oficjalne, NIE polski): The form Sokichi Narumi assumes when he loads the Skull Memory into the Lostdriver. ⏎  ⏎ The skeletal power not only increases his physical strength, but makes him immortal while in that form. ⏎  ⏎ He becomes cold to the touch, as if dead.

### dic\_pilot\_REA\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00c`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b00c\]
> JP (źródło tłumaczenia): 　「シルクハットの老紳士」を捜す女性。 ⏎ 　複数の人物にその捜索を依頼した。 ⏎ 　おしとやかな性格で、上品な雰囲気をまとう。 ⏎ 　何者かに生命を狙われており、エーアデントへ逃げ込んだ。
> EN (odniesienie oficjalne, NIE polski): A woman in pursuit of the "gentleman in the silk hat", with multiple contracts out to find him. ⏎  ⏎ She is gentle by nature and has a refined air about her. ⏎  ⏎ She has a target on her head, which brought her to flee to the A. Advent.

### dic\_pilot\_ALF\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b00e`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b00e\]
> JP (źródło tłumaczenia): 　謎の老紳士。 ⏎ 　裏社会で金色のゴーレムを売買しており、悪事の為し方を人々に教え回っている事から、「悪の伝道師」の通り名を持つ。 ⏎ 　シルクハットを被り、鍵穴と歯車型の飾りがあしらわれたスカーフを愛用する。
> EN (odniesienie oficjalne, NIE polski): An old gentleman shrouded in mystery. ⏎  ⏎ He sells gold golems on the black market and instructs people in the ways of misdeeds, which has earned him the nickname "The Preacher of Evil". ⏎  ⏎ He wears a silk hat and an ascot pinned by a lock-shaped ornament.

### dic\_pilot\_ALF\_S\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b010`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b010\]
> JP (źródło tłumaczenia): 　アルフコートの本当の姿であり、怪人。 ⏎ 　人間の顔を投影して裏社会に溶け込んでいたが、その正体を暴かれた事で本性をさらけ出した。 ⏎ 　自らを美食家であると語る。 ⏎ 　傲慢な性格で、人をミジンコと同等の存在だと思っている。
> EN (odniesienie oficjalne, NIE polski): Alfcourt's true, monstrous form. ⏎  ⏎ He wore a human face to blend in and carry out his black market business, but his true colors emerged when he was unmasked. ⏎  ⏎ He considers himself a gourmet. ⏎  ⏎ He is tremendously arrogant and sees humans as mere vermin.

### dic\_pilot\_NEKO\_00\_0

Adres: `dic\_text\_pilot-DLC1/00000375:e020b012`

> \[BRAK PL: dic\_text\_pilot-DLC1/00000375:e020b012\]
> JP (źródło tłumaczenia): 　アルフコートが放し飼いしている猫。 ⏎ 　自由気ままな気質で、神出鬼没。 ⏎ 　宙に浮く姿が確認されている。
> EN (odniesienie oficjalne, NIE polski): A cat kept by Alfcourt, allowed to wander free. ⏎  ⏎ It's a free spirit that can pop up at any time or place. ⏎  ⏎ It's even been seen floating in midair.

### dic\_pilot\_IRIS\_30\_00\_0

Adres: `dic\_text\_pilot-DLC1/00202cef:2920b000`

> \[BRAK PL: dic\_text\_pilot-DLC1/00202cef:2920b000\]
> JP (źródło tłumaczenia): 　自称・幸運の妖精。 ⏎ 　性格は、生意気で傍若無人でイタズラ好き。 ⏎ 　その正体は、神文明エーオスの統治者であるサイクラミノスが従者として造り上げた人工生命体。 ⏎ 　サイクラミノスは同種の人工生命体を複数所持していたが、その多くを自ら処罰しており、現存するのはイーリスのみとなっている。 ⏎ 　全ての戦いが終わった後は、カールレウムと共にサブ・スペースで次元の番人の一人となった。
> EN (odniesienie oficjalne, NIE polski): A self-appointed good-luck fairy. ⏎  ⏎ She is cheeky, brazen, and a fan of pranks. ⏎  ⏎ In actuality, she is an artificial lifeform created by Cyclaminos, ruler of the Divine Civilization Aos, as a servant. Cyclaminos originally created several artificial lifeforms like her, but executed most of them as punishment, leaving Iris as the last one left. ⏎  ⏎ After all the conflicts were over, Iris remained in subspace as a Keeper of Dimensions, along with Caruleum.

### dic\_pilot\_HIROS\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f520b000`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f520b000\]
> JP (źródło tłumaczenia): 　父である司馬遷次郎の手により改造されたサイボーグ戦士で鋼鉄ジーグの頭部パーツに変身する。 ⏎ 　新進気鋭のカーレーサーであり、自動車整備工場「司馬モータース」の若社長でもある。 ⏎ 　本人も知らない間に改造されており、邪魔大王国との戦いが始まっても、しばらくの間は自分がサイボーグだと知らないでいた。 ⏎ 　無鉄砲ですぐに無茶をする性格だが、サイボーグであった事を知った後は自分が普通の人と違うことに悩む姿も見せた。しかし、最後には人々を守るために邪魔大王国と戦っていく決意をする。
> EN (odniesienie oficjalne, NIE polski): A young man transformed into a cyborg warrior by his father, Senjiro Shiba. He is capable of morphing into the head component of Kotetsu Jeeg. ⏎  ⏎ He is a promising young racer and the owner of the car repair shop "Shiba Motors". ⏎  ⏎ Unbeknownst to him, he had been modified into a cyborg; he remained unaware of his nature during the early battles against the Jamatai Kingdom. ⏎  ⏎ Reckless and prone to rash actions, he initially struggled with the realization that he was no longer an ordinary human. However, he ultimately resolved to fight the Jamatai Kingdom to protect humanity.

### dic\_pilot\_JEEG\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6a0b001`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6a0b001\]
> JP (źródło tłumaczenia): 　司馬博士が対邪魔大王国用に開発したマグネロボット。 ⏎ 　司馬宙が変身したジーグヘッドにビッグシューターから発射された各種ジーグパーツが合体して完成する。 ⏎ 　磁流波エネルギーを動力源とし、出力は７５万馬力を誇る。 ⏎ 　ダイナマイトキック、ジーグブリーカーなどの格闘攻撃のほか、ナックルボンバー、スピンストームなどの武器を装備するが、最大の特徴はマグネットパワーで各種パーツを換装して戦うことである。マッハドリルやジーグバズーカだけでなく、物語の後半ではジーグバックラーやスカイパーツ、アースパーツ、マリンパーツといったパーツを状況に応じて使い分けるようになった。
> EN (odniesienie oficjalne, NIE polski): The Magnetic Robot developed by Dr. Shiba to counter the Jamatai Kingdom. ⏎  ⏎ Kotetsu Jeeg is formed when the Jeeg Parts, launched from the Big Shooter, combine with the Jeeg Head (which Hiroshi Shiba transforms into). ⏎ Powered by magnetic current energy, it boasts an impressive output of 750,000 horsepower. ⏎  ⏎ In addition to close-quarters combat techniques like the Dynamite Kick and Jeeg Breaker, it is equipped with ranged weapons such as the Knuckle Bomber and Spin Storm. Its most distinctive feature, however, is the Magnet Power, which allows Jeeg to easily swap parts during battle. ⏎  ⏎ Jeeg initially has access to the Mach Drill and the Jeeg Bazooka, but his arsenal is expanded throughout the story to include additional equipment such as the Jeeg Buckler, the Sky Parts, the Earth Parts, and the Marine Parts, enabling Hiroshi to adapt to any combat situation.

### dic\_pilot\_JEEG\_H\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b000`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b000\]
> JP (źródło tłumaczenia): 　サイボーグ宙が変身したジーグの頭部パーツ。 ⏎ 　この状態ではジーグビームと体当たりくらいしか攻撃方法がなく、ビッグシューターがいないと鋼鉄ジーグはまさに手足をもがれた状態となる。 ⏎ 　一応、単独で空を飛べる。
> EN (odniesienie oficjalne, NIE polski): The head component of Kotetsu Jeeg, which Cyborg Hiroshi transforms into. ⏎  ⏎ In this state, its combat options are limited to the Jeeg Beam and ramming attacks; without the Big Shooter to launch its parts, Kotetsu Jeeg is, quite literally, disarmed. ⏎ With that said, it is capable of independent flight.

### dic\_pilot\_CYHIRO\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b002`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b002\]
> JP (źródło tłumaczenia): 　司馬宙が両拳のグローブを撃ち合わせて変身した姿。 ⏎ 　変身の掛け声は「チェンジ・サイボーグ」 ⏎ 　この姿からさらにジーグヘッドに変形する。 ⏎ 　常人をはるかに上回るパワーを持ち、邪魔大王国のハニワ兵士を圧倒する。 ⏎ 　武器は持っておらず、そのパワーを活かした格闘戦を得意とする。
> EN (odniesienie oficjalne, NIE polski): The form Hiroshi Shiba takes after clashing his gloves together. ⏎ The transformation call is "Change Cyborg". ⏎ From this cyborg form, Hiroshi can further transform into the Jeeg Head. ⏎  ⏎ Possessing power far beyond that of an ordinary human, Hiroshi can easily overwhelm the Haniwa Soldiers of the Jamatai Kingdom. ⏎  ⏎ This cyborg form is unarmed, relying solely on its physical prowess and hand-to-hand combat.

### dic\_pilot\_CYHIRO2\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b004`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b004\]
> JP (źródło tłumaczenia): 　特訓により、新たなサイボーグへと生まれ変わった宙の姿。 ⏎ 　ジーグビュートというムチを武器に、ロボット兵やロボット獣などと戦う。 ⏎ 　身体能力はさらにパワーアップしており、超人的な動きを見せる。
> EN (odniesienie oficjalne, NIE polski): The new cyborg form Hiroshi acquired through rigorous training. ⏎ Armed with the Jeeg Whip, this form allows Hiroshi to stand against Robot Soldiers and Robot Beasts. ⏎  ⏎ His physical abilities are significantly enhanced compared to his previous form, allowing him to display superhuman agility.

### dic\_pilot\_MIWA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b006`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b006\]
> JP (źródło tłumaczenia): 　ビッグシューターの専属パイロット。 ⏎ 　愛称はミッチー。 ⏎ 　幼い頃に両親が行方不明になり、司馬家で実の娘同然に育てられる。 ⏎ 　元は司馬博士の助手をしており、研究に忙殺される司馬博士を見て、自らもビッグシューターのパイロットに志願し、青春をかけて邪魔大王国と戦う決心をした。 ⏎ 　冷静で責任感が強く、宙のサポートとして、なくてはならないパートナー。 ⏎ 　邪魔大王国との戦闘で心身ともにボロボロになるが、決して弱音を吐かず、過酷な任務に耐え続けた。
> EN (odniesienie oficjalne, NIE polski): The exclusive pilot of the Big Shooter, affectionately called "Micchi" by her friends. ⏎ She was raised by the Shiba family as their own daughter after her parents went missing during her childhood. ⏎  ⏎ Originally an assistant to Dr. Shiba, she volunteered to pilot the Big Shooter upon seeing how overwhelmed he was with his research. She pledged to dedicate her youth to fighting the Jamatai Kingdom. ⏎ Calm and highly responsible, she has become an indispensable partner to Hiroshi. ⏎  ⏎ Despite the physically and emotionally taxing nature of her missions, she has never once complained, enduring her grueling duties with grim determination.

### dic\_pilot\_RYOMA\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b008`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b008\]
> JP (źródło tłumaczenia): 　異なる時空で生み出された流竜馬の生体クローン。 ⏎ 　流竜馬の記憶はあるが、全く別の個体。戦士として生み出された存在であることは理解している。 ⏎ 　本能型攻撃思考を持ち、ダメ押しの一撃で威力を発揮する。
> EN (odniesienie oficjalne, NIE polski): A bio-clone of Ryoma Nagare, created in an alternate space-time. ⏎  ⏎ Although he retains the memories of the original Ryoma, he is an entirely separate individual. He fully understands that he was created solely as a warrior. ⏎ Exhibiting an instinct-driven mindset, his attacks are always delivered with lethal intent.

### dic\_pilot\_HAYAT\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00a`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b00a\]
> JP (źródło tłumaczenia): 　異なる時空で生み出された神隼人の生体クローン。 ⏎ 　神隼人の記憶はあるが、全く別の個体。戦士として生み出された存在であることは理解している。 ⏎ 　精密型攻撃思考を持ち、無駄な動きを排除した正確無比の戦闘スタイルが特徴。
> EN (odniesienie oficjalne, NIE polski): A bio-clone of Hayato Jin, created in an alternate space-time. ⏎  ⏎ Although he retains the memories of the original Hayato, he is an entirely separate individual. He fully understands that he was created solely as a warrior. ⏎ Exhibiting a precise and analytical mindset, his fighting style is characterized by calculated, flawless attacks, eliminating any unnecessary movements.

### dic\_pilot\_MUSAS\_B\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00c`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b00c\]
> JP (źródło tłumaczenia): 　異なる時空で生み出された巴武蔵の生体クローン。 ⏎ 　巴武蔵の記憶はあるが、全く別の個体。戦士として生み出された存在であることは理解している。 ⏎ 　論理型攻撃思考を持ち、故に必要な状況であれば、自己犠牲を選択することも厭わない。
> EN (odniesienie oficjalne, NIE polski): A bio-clone of Musashi Tomoe, created in an alternate space-time. ⏎  ⏎ Although he retains the memories of the original Musashi, he is an entirely separate individual. He fully understands that he was created solely as a warrior. ⏎ Exhibiting a cold, logical mindset, he is prepared to sacrifice his life if the situation demands it.

### dic\_pilot\_SEIJ\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b00e`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b00e\]
> JP (źródło tłumaczenia): 　緑ヶ浜小学校の５年生。 ⏎ 　性格はお調子者だが、正義感が強い。 ⏎ 　地球の意思と呼べる存在から「オーリン」を託され、勇者達の隊長となる。 ⏎ 　軍の高官である父・光一郎とアナウンサーの母・美鈴が二人共、不在がちであるため家では一人でいる事が多く、料理が得意。 ⏎ 　良くも悪くも純粋であり、思った事をすぐに口にしたり、考え無しに行動したりして自らピンチを招く事も多いが、その真っ直ぐさにより勇者達と協力して、地球を守るために戦っていく。　
> EN (odniesienie oficjalne, NIE polski): A fifth grader at Midorigahama Elementary. ⏎  ⏎ He has a playful and mischievous personality but also a strong sense of justice. ⏎  ⏎ Entrusted with the Aurin by what might be called the will of the Earth itself, he becomes the commander of the Brave Fighters. ⏎  ⏎ Since both his father, Koichiro, a high-ranking military officer, and his mother, Misuzu, a news anchor, are frequently away from home, he often spends time alone; as a result, he has become surprisingly skilled at cooking. ⏎  ⏎ Seiji is a pure-hearted boy, in both good and bad senses—he speaks his mind without hesitation and often acts impulsively, occasionally landing himself in trouble. ⏎ However, it is thanks to his unwavering sincerity that he is able to cooperate with the Brave Fighters and continue fighting to protect the Earth.　

### dic\_pilot\_SEIJ\_S\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b010`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b010\]
> JP (źródło tłumaczenia): 　星史がキャプテンスーツを身につけた姿。 ⏎ 　防護に加え、正体を隠すためのものであり、ヘルメットは状況に応じてマスク部分も追加され、素顔が隠される。 ⏎ 　戦闘時、星史はこの姿となり、発信装置「ダイレクター」で勇者達に指令を与える。　
> EN (odniesienie oficjalne, NIE polski): Seiji's identity in his Captain Suit. ⏎  ⏎ The suit not only protects his safety, but also his identity when he wears a face mask incorporated into the helmet. ⏎  ⏎ Seiji assumes this persona in combat, commanding the Braves through a transmitter called the Director.　

### dic\_pilot\_HIKA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b012`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b012\]
> JP (źródło tłumaczenia): 　星史の幼なじみの少女。 ⏎ 　家も隣同士であり、実家は自然食レストラン「つくし」を営む。 ⏎ 　明るく勝ち気な性格であり、両親が不在がちな星史の世話を何かと焼こうとするが、本人には迷惑がられる事もある。 ⏎ 　また、星史が他の女性に対してデレデレすると嫉妬めいた言動を見せる。 ⏎ 　なお、星史が勇者達の隊長である事には気づいていない。
> EN (odniesienie oficjalne, NIE polski): Seiji's childhood friend and neighbor. Her family runs the all-natural food restaurant "Tsukushi". ⏎  ⏎ Cheerful and strong-willed, she often tries to look after Seiji, whose parents are frequently away due to work, though he usually finds her attention annoying (or so he says). ⏎ She is quite obviously jealous whenever Seiji acts overly friendly with other girls. ⏎  ⏎ For most of the story, she remains unaware that Seiji is the commander of the Brave Fighters.

### dic\_pilot\_HOTA\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b014`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b014\]
> JP (źródło tłumaczenia): 　星史のクラスメイト。 ⏎ 　無口で感情をあまり表に出さず、ミステリアスな雰囲気を持つ。 ⏎ 　動物や自然の声を聞く事ができるかのような言動を見せる。 ⏎ 　星史が勇者達の隊長である事を知っているようであり、助言めいた事を与える事もある。
> EN (odniesienie oficjalne, NIE polski): One of Seiji's classmates. ⏎  ⏎ Rarely showing her emotions, she is a quiet girl with a mysterious aura. ⏎ She often speaks and acts as if she can hear the voices of animals and nature. ⏎  ⏎ She seems to be immediately aware that Seiji is the commander of the Brave Fighters and occasionally offers him advice.　

### dic\_pilot\_DGAN\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f6e0b016`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f6e0b016\]
> JP (źródło tłumaczenia): 　プラネットエナジーが生み出した勇者。 ⏎ 　星史の住む緑ヶ浜の寺にある仏像の額にあった勇者の石から復活を遂げた。 ⏎ 　勇者達のリーダー的な存在であり、星史を体内に乗せる事も多い。 ⏎ 　普段はパトカーの姿で交番にいる。
> EN (odniesienie oficjalne, NIE polski): One of the Brave Fighters born of Planet Energy. ⏎  ⏎ He was resurrected from the Brave Stone embedded in the forehead of a Buddha statue at the temple in Midorigahama, where Seiji lives. ⏎ As the leader of the Braves, he often carries Seiji inside his machine body. ⏎  ⏎ Outside of combat, he takes the form of a patrol car parked at the local police box.

### dic\_pilot\_DGAN\_X\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b001`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f720b001\]
> JP (źródło tłumaczenia): 　地球が生み出した勇者ダ・ガーンが、サポートメカのアースファイター、アースライナーと合体した巨大ロボ。 ⏎ 　アースファイターが上半身、アースライナーが下半身を形成し、ダ・ガーンを挟み込む形で完成する。 ⏎ 　胸部の地球をかたどったパーツからエネルギーを撃ち出すブレストアースバスターが最大の必殺技。
> EN (odniesienie oficjalne, NIE polski): A giant robot formed when Da-Garn, the Brave Fighter birthed by the Earth, combines with his support mecha, the Earth Fighter and the Earth Liner. ⏎  ⏎ In this form, the Earth Fighter serves as the upper body, the Earth Liner as the lower body, and Da-Garn is positioned between them. ⏎ His ultimate finishing move is the Breast Earth Buster, which fires a beam of energy from his Earth-shaped chest piece.

### dic\_pilot\_DGAN\_GX\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b003`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f720b003\]
> JP (źródło tłumaczenia): 　ダ・ガーンＸとガ・オーンが伝説合体した姿。 ⏎ 　ガ・オーンのパーツがダ・ガーンＸの各部にパーツとして装着される形で構成される。 ⏎ 　ＧキャノンとＧバルカンを連結させたＧＸバスターが最強の武装。なお、ＧＸバスターは組み替える事でＧＸバスターバルカンとしても使用できる。
> EN (odniesienie oficjalne, NIE polski): The "Legend Combined" form of Da-Garn X and Ga-Orn. ⏎  ⏎ This form is created by attaching parts of Ga-Orn to various sections of Da-Garn X as additional components. ⏎  ⏎ His most powerful weapon is the GX Buster, formed by linking the G-Cannon and G-Vulcan together. ⏎ Additionally, the GX Buster can be reconfigured and used as the GX Buster Vulcan.

### dic\_pilot\_GAON\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b005`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f720b005\]
> JP (źródło tłumaczenia): 　キリマンジャロから復活した勇者。 ⏎ 　その身を挺してアフリカ大陸の崩壊を食い止めるダ・ガーンに代わり、星史と共に戦った。 ⏎ 　ダ・ガーンが復活した後、彼と伝説合体してグレートダ・ガーンＧＸとなった。
> EN (odniesienie oficjalne, NIE polski): The Brave Fighter resurrected from Kilimanjaro. ⏎  ⏎ For a time, he fought alongside Seiji in place of Da-Garn, who had sacrificed himself to prevent the collapse of the African continent. ⏎  ⏎ After Da-Garn was revived, he combined with him in a Legend Combination, forming Great Da-Garn GX.

### dic\_pilot\_REDRN\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b007`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f720b007\]
> JP (źródło tłumaczenia): 　オーボスに最初に派遣された前線指揮官。 ⏎ 　メカのコレクションが趣味であり、メカに関して独特の美学を持つ。 ⏎ 　任務失敗によって一度は後退させられたが、身体をサイボーグ化して専用機体「レッドガイスト」と共に再び地球に襲来する。 ⏎ 　以前の詰めの甘さは影を潜め、冷徹な復讐者となり、レッドガイストの強大な力と共に星史とダ・ガーン達を何度も苦しめた。
> EN (odniesienie oficjalne, NIE polski): The first frontline commander dispatched by Ohbosu. ⏎  ⏎ He has a passion for collecting machines and possesses a unique sense of aesthetics regarding them. ⏎  ⏎ After failing his mission, he was forced to withdraw temporarily; however, he later returned to Earth as a cyborg, piloting his personal robot, Red Gaist. ⏎  ⏎ No longer hindered by his previous lack of decisiveness, he became a cold and ruthless avenger, repeatedly tormenting Seiji and the Brave Fighters with Red Gaist's immense power.

### dic\_pilot\_EXIS\_00\_0

Adres: `dic\_text\_pilot-DLC2/000002ae:f720b009`

> \[BRAK PL: dic\_text\_pilot-DLC2/000002ae:f720b009\]
> JP (źródło tłumaczenia): 　現在の地球以外の文明によって創られたロボット。 ⏎ 　永久機関に近い機能を持つ動力炉から生み出される高エネルギーにより、圧倒的な戦闘力と継戦能力を誇る。 ⏎ 　テクノロジーの詳細は不明であるが、自律的な意思と心と呼べるものを持っており、自らの判断に従って行動する。 ⏎ 　その性格は、いい意味で実直、悪い意味で頑固であり、自らの使命である正義の遂行に全てを懸けている。同時に自らのアイデンティティに強い思い入れがあり、エチカにもらった「イグジス」の名を大切にしている。
> EN (odniesienie oficjalne, NIE polski): A robot created with technology far surpassing that of modern Earth. ⏎ Equipped with a power reactor that grants him nigh-infinite energy, he boasts overwhelming combat prowess and fighting capabilities. ⏎  ⏎ Though the details of the technology are unknown, he appears to possess autonomous will, allowing him to act based on his own judgment. ⏎  ⏎ His personality is honest and forthright—at its best, though he can be quite stubborn. He throws everything he has into fulfilling his mission of justice. At the same time, he thinks deeply about his identity and cherishes the name Exis that Echika bestowed on him.

### dic\_pilot\_BELT\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:22a0b000`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:22a0b000\]
> JP (źródło tłumaczenia): 　エゥーゴの支援組織であるカラバのメンバー。 ⏎ 　活動的な女性だが、思った事をすぐに口に出してしまう性格のため、周囲の反感を買う事もしばしばあった。 ⏎ 　アウドムラと接触した際には、元もと興味を持っていたという一年戦争の英雄アムロと会えた事を喜んでいた。すぐに彼に強烈なアプローチを繰り返し、やがて奮起したアムロを恋人として支えるようになった。
> EN (odniesienie oficjalne, NIE polski): A member of Karaba, a supporting organization for the A.E.U.G. ⏎  ⏎ An energetic woman, she tends to speak her mind without thinking, a trait that frequently offends others. ⏎  ⏎ To her delight, when she made contact with the Audhumla, she got to meet Amuro, hero of the One Year War, a man she'd always been interested in. She began making advances on him without delay, and when he finally roused himself to action, she supported him as his lover.

### dic\_pilot\_COSMO\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b001`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2320b001\]
> JP (źródło tłumaczenia): 　ソロ星科学庁長官ユウキ・ロウル博士の息子で、Ａメカ及びイデオンのパイロット。１６歳。 ⏎ 　ソロ星がバッフ・クランに襲撃を受けた際、身を守るためにイデオンのＡメカに乗り込み、なし崩し的にイデオンのパイロットとなる。 ⏎ 　身勝手な大人達や異星人バッフ・クランに対する怒り、生への執着心で当初は戦い抜いたが、無限エネルギー・イデの危険性が明確になるにつれ、戦いに対する考え方が変わっていく。 ⏎ 　特技はナイフ投げで、飛行中の超小型偵察機を落とすほどの腕前である。また、機械いじりも得意で、イデオンの電子機器の整備も手伝っていた。 ⏎ 　皮肉屋で斜に構えた性格だったが、ブラジラー基地で出会ったカミューラ・ランバン、植民星キャラルで出会ったキッチ・キッチンらの死をはじめ、バッフ・クランからの逃避行の中での様々な出来事がコスモを大人にさせていった。 ⏎ 　開拓者として育ったためか、過酷な環境下でも諦めることなく戦い続ける強さを持ち、バッフ・クランとの最終決戦における絶望的な状況でも、最後まで生き抜こうとする姿勢をやめなかった。
> EN (odniesienie oficjalne, NIE polski): The 16-year-old son of Dr. Rawl Yuki, Director of the Science Agency on Planet Solo. He is the pilot of Ideon's A Mecha and of Ideon itself. ⏎  ⏎ When Planet Solo was attacked by the Buff Clan, he boarded the A Mecha to survive; in doing so, he was unwillingly thrust into the role of Ideon's main pilot. ⏎  ⏎ At first, he fought out of sheer anger—toward both the selfish adults around him and the alien Buff Clan—as well as out of a stubborn refusal to die. But as the dangers of the Ide's infinite energy became increasingly clear, his perspective on war began to change. ⏎  ⏎ He is highly skilled at knife-throwing, capable of hitting small reconnaissance drones mid-flight. He also has a knack for machinery, and often helped with the maintenance of Ideon's electronics. ⏎  ⏎ Though initially cynical and standoffish, the deaths of Camulla Lanban, the commander at the Brazillier base, and Kittie Kitten, whom he met on the colony planet Carale, as well as the many hardships he endured during his group's desperate flight from the Buff Clan forced Cosmo to mature. ⏎  ⏎ Perhaps due to his upbringing as a settler, he possesses remarkable resilience, always willing to fight on no matter how harsh the conditions are. Even in the face of the hopeless final battle against the Buff Clan, he never abandoned his will to survive 'till the bitter end.

### dic\_pilot\_DEKU\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b003`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2320b003\]
> JP (źródło tłumaczenia): 　ソロ星移民の子供でコスモの弟分。１０歳。 ⏎ 　ラパパというリスに似たペットを飼っている。 ⏎ 　バッフ・クランによる襲撃で両親を失っており、逃亡当初は非戦闘員であったが、子供ゆえのヒーロー志向とバッフ・クランに対する憎しみから、Ａメカのサブパイロットに申し出る。 ⏎ 　最初は足手まといでしかなかったが、コスモのサポートに欠かせないパイロットに成長し、熱くなりすぎるコスモを抑える役目に回ることも度々あった。ギジェを欠き、カーシャが降りた後はＢメカのメインパイロットとなり、完全に一人前の戦士となっていた。
> EN (odniesienie oficjalne, NIE polski): One of the children from Planet Solo and Cosmo's sidekick. He is 10 years old. ⏎ He keeps a pet squirrel-like creature he calls Rapapa. ⏎  ⏎ He lost both parents during the Buff Clan attack. Although he was initially a non-combatant, his deep hatred for the Buff Clan and childlike admiration for heroes drove him to volunteer as the subpilot of Ideon's A Mecha. ⏎  ⏎ At first, he was little more than a burden, but over time, he grew into Cosmo's most reliable assistant, often stepping in to temper his hot-headedness. ⏎  ⏎ After Gije's death and Kasha stepping down from piloting, he takes over as the main pilot of the B Mecha, fully proving himself as a true fighter.

### dic\_pilot\_CASHA\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2320b005`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2320b005\]
> JP (źródło tłumaczenia): 　イデオンＣメカのメインパイロットで、イデオンのミサイルコントロール担当。１７歳。 ⏎ 　英才教育を受けており、ロケット整備士の免許を持つ。親から離され、夏と冬だけのＡ‐９２という植民星で育ったため、誰にも頼らない生き方を信念にしている。それゆえ、一人で突っ走る傾向が強く、周囲の人間の反感を買うことになる。こと恋愛に関しては否定的で、馴れ合い・騙し合いなどと言って嫌悪していた。また、自尊心による攻撃的な性格は、他者を傷つける発言をさせることも多く、その度にたしなめられていた。 ⏎ 　それでも悲壮感漂う逃避行の中、次第にコスモに心を許すようになっていく。
> EN (odniesienie oficjalne, NIE polski): The main pilot of Ideon's C Mecha, responsible for missile control. She is 17 years old. ⏎  ⏎ She received a specialized education for gifted children and holds a rocket mechanic's license. ⏎ Having grown up away from her parents on A-92, a colony planet with only summer and winter seasons, she developed a strong sense of self-reliance. As a result, she has a tendency to act impulsively and independently, often antagonizing those around her. ⏎  ⏎ She is particularly dismissive of romance, viewing it as mere deception and superficial attachment—things she despises. Her prideful and assertive nature frequently leads her to make harsh remarks that wound others, for which she is often reprimanded. ⏎ Nevertheless, during their hopeless escape, she gradually begins to open her heart to Cosmo.

### dic\_pilot\_LUU\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b000`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b000\]
> JP (źródło tłumaczenia): 　ソロ星移民の赤ん坊で１歳半。 ⏎ 　バッフ・クラン襲撃の際、親を失っている。 ⏎ 　赤ん坊ゆえ、自分を守ろうとする「純粋な防衛本能」を持っており、イデはそれに反応する（イデ自身の防衛本能もある）。 ⏎ 　よって、ルウなくしてイデオンのパワーアップは難しいということになり、ソロシップの守り神のような存在となっていった。
> EN (odniesienie oficjalne, NIE polski): One of the infants among the Planet Solo colonists. He is only a year and a half old. He lost his parents during the Buff Clan attack. ⏎  ⏎ As a baby, he possesses a "purer kind of self-defense"—a primal urge to protect himself from danger. The Ide attuned itself to that feeling, as it harbors a self-defense instinct of its own. Because of this, Lou's presence becomes essential for Ideon's power to manifest, making him something of a guardian figure aboard the Solo Ship.

### dic\_pilot\_HARUK\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b002`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b002\]
> JP (źródło tłumaczenia): 　iDOL「インベル」のマスター。 ⏎ 　アイドルとなるためにオーディションを受けたが、それがiDOLの操縦者の選抜である事を知らずに世界規模の災害からの復興を支援するための組織「モンデンキント」に所属し、アイドルマスターとなる。 ⏎ 　常にポジティブで芯の強さを見せるが、同時にあまり深く考えずに状況を受け入れる淡泊な面や心の弱さも併せ持つ。 ⏎ 　リボンがトレードマークで、周囲の人間からそれにちなんだあだ名で呼ばれる事が多い。 ⏎ 　戦いの中、インベルに心がある事を知り、強い信頼関係を築いていき、それは恋愛感情にまで昇華された。
> EN (odniesienie oficjalne, NIE polski): The master of the iDOL Imber. ⏎  ⏎ She applied to an idol audition which turned out to be one for iDOL pilots. Now she's an idolmaster under the international agency Mondenkind, which helps rebuilding efforts in the wake of worldwide disaster. ⏎  ⏎ Though she is normally positive and steadfast, she also has a tendency to be a bit too carefree with accepting whatever situation is presented to her, and cracks of weakness sometimes manifest in her heart. Her hair ribbon is her trademark, and those around her often give her nicknames based on it. After she discovered Imber had a heart of its own, she developed a deep trust in her iDOL which eventually blossomed into love.

### dic\_pilot\_TAKT\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b004`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b004\]
> JP (źródło tłumaczenia): 　南十字島へやってきた少年。 ⏎ 　南十字学園高等部の一年生であり、演劇部「夜間飛行」に所属している。 ⏎ 　明るく前向きな性格と爽やかさで学園の人気者。 ⏎ 　サイバディ「タウバーン」のスタードライバーであり、第３フェーズに達した「銀河美少年」として、タウバーンに直接乗り込む。 ⏎ 　ワコとは島に流れ着いた時からの付き合いであり、スガタとはワコをめぐってのライバルでもあり、親友でもある。 ⏎ 　サイバディの力を我が物としようとする綺羅星十字団と戦い、最後は王のサイバディ「キング・ザメク」とそれを自らの野望の道具とした綺羅星十字団ヘッドの父・トキオを倒し、スガタとワコを宿命から解放した。 ⏎ 　戦いの後はゼロ時間から解き放たれたサイバディを追って、スガタ、ワコと共に南十字島を出ている。
> EN (odniesienie oficjalne, NIE polski): A boy who arrived on Southern Cross Island. ⏎  ⏎ He enrolls as a first-year student at Southern Cross High School and joins the Midnight Flight drama club. ⏎  ⏎ His relentless positivity and energy makes him instantly popular in school. ⏎  ⏎ He is the Star Driver of the Cybody Tauburn and a Ginga Bishonen who has reached Phase 3, allowing him to pilot Tauburn directly. ⏎  ⏎ Wako was the first to find him washed up on the island's shores. He develops a rivalry with Sugata over her favor, as well as a deep friendship. ⏎  ⏎ He opposes the Kiraboshi Order of Cross's plans to take control of the Cybodies' powers. This leads to a final battle with the king Cybody King Samekh, taken over by the Order's Head (in reality his father Tokio) for his personal ambitions. In his victory, he frees Sugata and Wako from their fates. ⏎  ⏎ Afterwards, he leaves Southern Cross Island with Sugata and Wako, hunting down the other Cybodies now released from zero-time.

### dic\_pilot\_SGATA\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b006`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b006\]
> JP (źródło tłumaczenia): 　南十字島の名家であるシンドウ家の跡継ぎの少年。 ⏎ 　タクトと同じく南十字学園高等部の一年生であり、演劇部「夜間飛行」に所属する。 ⏎ 　端正な容姿に加え、タクトとは好対照な知的でクールな雰囲気で彼と学園の女生徒の人気を分け合う。 ⏎ 　幼なじみのワコは許嫁でもあり、彼女を守る決意を胸に秘めている。 ⏎ 　古武道の使い手でもあり、タクトの指南役であると同時にワコをめぐるライバル兼親友でもある。 ⏎ 　王のサイバディ「キング・ザメク」のドライバーであり、全てのリビドーを吸い上げるキング・ザメクを自らを犠牲にして封印しようとしたが、ヘッドにザメクを奪われてしまう。 ⏎ 　ザメクを倒したタクトに救出された後は宿命から解放され、新たな生き方を探すようになる。
> EN (odniesienie oficjalne, NIE polski): The heir of the Shindo family, a prominent Southern Cross Island dynasty. ⏎  ⏎ He is a first-year student at Southern Cross High School like Takuto, and a member of the Midnight Flight drama club. ⏎  ⏎ Not only is he incredibly handsome, he has an intellectual and composed bearing that makes a sharp contrast to Takuto, earning them both a lot of attention from female students. ⏎  ⏎ He has known Wako from childhood and is also in an arranged betrothal. Though he doesn't show it, he is fiercely dedicated to her safety. ⏎  ⏎ He is also a student of traditional Japanese combat arts and is Takuto's instructor as well as his rival for Wako's favor. ⏎  ⏎ He is the Star Driver of King Samekh, the king Cybody. He had a plan to sacrifice himself to seal away King Samekh's all-consuming libido-draining power, but the massive Cybody was hijacked by Head. ⏎  ⏎ Takuto defeated Samekh, freeing him from his chains, and he was able to chart his own path at last.

### dic\_pilot\_WAKO\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b008`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b008\]
> JP (źródło tłumaczenia): 　南十字島に住む少女。 ⏎ 　泳いで島を目指して漂着したタクトを助けてから縁が続く。 ⏎ 　タクトと同じく南十字学園一年生で演劇部「夜間飛行」に所属する。 ⏎ 　明るく活発であると同時に妄想癖を持つ。 ⏎ 　サイバディを封印する「四方の巫女」の一人「皆水（みなみ）の巫女」であり、歌手になる夢を持っているが、その使命ゆえに島を出られないでいる。 ⏎ 　幼なじみのスガタは許嫁でもあるが、タクトの事も同じくらい気になっている。 ⏎ 　キング・ザメクとの戦いの中、サイバディ「ワウナ」とアプリボワゼしたが、結果としてワウナは失われ、巫女の封印は破られ、ゼロ時間は消滅する事となった。 ⏎ 　タクトによってザメクが倒され、スガタと共に宿命から解放された後は島から出て、新しい生き方を探している。
> EN (odniesienie oficjalne, NIE polski): A girl from Southern Cross Island. ⏎  ⏎ When Takuto tried to swim to the island and washed up on the beach, she is the one who found him, and they only grew closer afterwards. ⏎  ⏎ Like Takuto, she's a first-year student at Southern Cross High School and a member of the Midnight Flight drama club. ⏎  ⏎ She's upbeat, energetic, and prone to flights of fancy. ⏎  ⏎ She is the Southern Maiden, one of the Shrine Maidens of the Four Directions tasked with keeping the Cybodies sealed. This keeps her on the island despite her dreams to be a singer. ⏎  ⏎ She is a childhood acquaintance and the arranged fiancée of Sugata, but her feelings for Takuto are just as strong. ⏎  ⏎ During the battle with King Samekh, she apprivoised with her Cybody Wawna, but it was destroyed, her seal was broken, and zero-time was erased. ⏎  ⏎ Takuto's victory over Samekh meant she and Sugata were freed from their fates and able to decide their own lives.

### dic\_pilot\_ANGE\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b00a`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b00a\]
> JP (źródło tłumaczenia): 　皇女ではなくなった、ただのアンジュ。 ⏎ 　ノーマであることが発覚した事で全てを失い、ラグナメイル「ヴィルキス」に乗ってドラゴンと戦う事を余儀なくされる。 ⏎ 　当初は皇女としてのプライドの高さから周囲と衝突してばかりいたものの、様々な経験を通して少しずつ仲間たちとの絆を深めていった。 ⏎ 　多少頑固なところがあるものの、何者にも屈しない強い心を持っている。 ⏎ 　元々、運動能力が高い上にエアリアをやっていた事もあり、対ドラゴンの戦闘においてすぐに頭角を現していった。 ⏎ 　アルゼナル壊滅と前後する形で様々な事実が発覚。そんな中でも支え続けてくれたタスクとモモカを失った事で一度は戦う理由を見失いかけるも、思いがけずタスクと再会したことで世界を守る決意を固めた。
> EN (odniesienie oficjalne, NIE polski): Angelise after losing her right to the throne, now simply called Ange. ⏎  ⏎ After others discovered that she was a Norma, she was forced to fight against the Dragons in a Ragna-Mail called Villkiss. ⏎ While her pride as a princess led her to constantly clash with those around her at first, as time went on and they experienced more and more, she formed bonds with them. ⏎  ⏎ She can be somewhat stubborn, but her heart and mind are powerful and unyielding. She quickly distinguished herself in the war against the Dragons with her already high level of physical ability and Iaria experience. ⏎  ⏎ During the events leading to and from Arzenal's destruction, she made many discoveries, but lost her staunch supporters Tusk and Momo in the chaos. For a time, she lost her reason to fight, but after a surprising reunion with Tusk, she swore to protect the world. ⏎ 

### dic\_pilot\_ANGE\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:2360b00b`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:2360b00b\]
> JP (źródło tłumaczenia): 　その後、ジルに代わって総司令となり、残された仲間と共に「ラストリベルタス」を決行。特異な力を持つエンブリヲに捕らえられて、一度は次元の狭間に閉じ込められるも、タスクらの手によって救出され、エンブリヲに支配された世界を破壊した。
> EN (odniesienie oficjalne, NIE polski): After that, Ange took over Jill's role as commander and rallied her remaining allies to carry out the Last Libertas. Though Ange was captured and trapped in the gap between dimensions by Embryo, who wielded supernatural powers, Tusk and the others rescued her, and they destroyed the world ruled by Embryo.

### dic\_pilot\_ENBRW\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b000`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b000\]
> JP (źródło tłumaczenia): 　自らを調律者と称する謎の存在。 ⏎ 　為政者達よりもさらに一段高いところに立って、世界の動向を冷めた目で見つめている。 ⏎ 　太古の兵器や技術を有しており、ラグナメイル「ヒステリカ」を駆ってアンジュの前に姿を現した。 ⏎ 　心の隙間に入り込み、一種の精神制御のような形で他人を支配する。その力は、特に女性に対して有効に発揮される。 ⏎ 　また、相手の痛覚と快楽を操る事ができ、それを以てアンジュを翻弄した。 ⏎ 　その正体は、別の世界の地球の科学者。自らが発見したエネルギー・ドラグニウムの力によって世界が滅ぶと、その地球に見切りをつけて、アンジュ達の世界へとやってきた。 ⏎ 　人類を滅亡から救うには人間自体を作り変えるしかないと考え、マナが使える人類を生み出すも、その性質は彼の理想には程遠かったために世界そのものを作り変える事を画策。その手段として、二つの地球を一つにする時空融合を企てた。
> EN (odniesienie oficjalne, NIE polski): A mysterious man calling himself the Tuner. ⏎  ⏎ He stood on a level higher than any politician or administrator, watching the trends and movements of the world with cold, calm eyes. Possessing ancient weaponry and technology, he appeared before Ange piloting his Ragna-Mail, Hysterica. ⏎  ⏎ Embryo penetrates the gaps in one's mind, dominating others in a form of mind control. His power is especially effective on women. He can also control a person's pain and pleasure senses, an ability he used in order to trifle with Ange. ⏎  ⏎ His identity was that of a researcher from a parallel Earth. He had decided Earth was hopeless, and that he would destroy the world using Dragunium, an energy he discovered, before arriving in Ange's world. ⏎  ⏎ Believing the only way to save humanity from extinction was to remake humans themselves, he created humans who could use Mana, only to scheme to recreate the world itself when it was pushed too far from his ideal as a result. One of his plans was to fuse space-time, merging two Earths together.

### dic\_pilot\_ENBRW\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b001`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b001\]
> JP (źródło tłumaczenia): 　新たな世界を共に生み出す存在としてアンジュを自らの花嫁に選ぶも、完全否定され、ヒステリカと共に倒されて完全に消滅した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Despite choosing Ange as his bride so they could give birth to a new world together, he was utterly and completely rejected, defeated along with his Hysterica, and destroyed.

### dic\_pilot\_EUREK\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b002`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b002\]
> JP (źródło tłumaczenia): 　独立師団無任所部隊A.C.I.Dの上級戦闘員。 ⏎ 　かつてはスカブコーラル（珊瑚状の情報生命体）を生み出す能力を持っていたが、スカブコーラル内の仮想世界「グリーンアース」が現実世界「ブルーアース」に出現する災害「大融合」を引き起こし、同時に能力を失った。 ⏎ 　その胸には、愛する少年・レントンが自らの行動の巻き添えで生命を落とした事が傷になって残っているが、同時にどこかの世界で彼が生きている事にかすかな希望をつないでいる。 ⏎ 　かつての自分と同じくスカブコーラルを生み出す能力を持つ少女・アイリスの保護を命じられるが、デューイの襲撃を受け、地球に降りる事となった二人は組織の支援を得られないまま、逃避行を続ける。
> EN (odniesienie oficjalne, NIE polski): A senior combatant assigned to the Autonomous Corps of Independent Division (A.C.I.D.). ⏎  ⏎ Once possessed of the ability to create Scab Corals (coral-like information-based life-forms), she lost that power after triggering the Great Merging, a cataclysmic event that caused Green Earth—the virtual world inside the Scab Corals—to appear in Blue Earth, the real world. ⏎  ⏎ Still carrying the pain of her beloved Renton losing his life after getting mixed up in her affairs, she nevertheless held onto a tiny ray of hope that he was still alive in some world somewhere. She received orders to protect a girl named Iris, who could create Scab Corals as Eureka herself once could, but after Dewey attacked them, the two descended to Earth and went on the run without any organizational support.

### dic\_pilot\_EUREK\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b003`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b003\]
> JP (źródło tłumaczenia): 　孤独な旅の中、アイリスと徐々に心を通わせていく。 ⏎ 　アイリスを捕らえたデューイとの最後の戦いの中、ニルヴァーシュＺに搭乗して世界を救い、そこに宿るレントンと再会を果たした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Over the course of their journey alone, she and Iris steadily opened up to each other. During Eureka's final battle with Dewey, who took Iris captive, Eureka saved the world by piloting Nirvash Z and reunited with Renton, who was inhabiting it.

### dic\_pilot\_IRIS\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b004`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b004\]
> JP (źródło tłumaczenia): 　スカブコーラルを生み出す能力を持った少女。 ⏎ 　かつて同じ力を持っていたエウレカになぞらえ、その力は「EUREKA」と呼ばれる。 ⏎ 　それゆえにグリーンアースのデューイ・ノヴァクの標的となり、彼から逃れるためにエウレカと逃避行を続ける。
> EN (odniesienie oficjalne, NIE polski): A girl with the power to create Scab Corals. ⏎  ⏎ She is called a "Eureka" because of that power, likening her to Eureka, who once had the same ability. ⏎  ⏎ This trait led Dewey Novak of Green Earth to target her, forcing her and Eureka on a runaway journey to escape him.

### dic\_pilot\_IRIS\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b005`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b005\]
> JP (źródło tłumaczenia): 　孤独な旅の中、最初は険悪だったエウレカと徐々に心を通わせていき、彼女の事を「おばさま」と呼ぶようになった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ While initially hostile toward Eureka, she steadily opened up to her over the course of their solitary journey and started calling her "Auntie".

### dic\_pilot\_DEWEY\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b006`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b006\]
> JP (źródło tłumaczenia): 　グリーンアースの軍人。 ⏎ 　「大融合」以前よりブルーアースに転移していたが、「大融合」をきっかけとして複数の生命と超常の力を得る。 ⏎ 　グリーンアースを生み出した存在であるエウレカに複雑な感情を抱いており、自分達の意思と心の存在を証明するため、創造主であるエウレカと彼女と同じ力を持つアイリスを標的とする。
> EN (odniesienie oficjalne, NIE polski): A Green Earth soldier. ⏎  ⏎ Though he had already moved to Blue Earth prior to the Great Merging, the event gave him multiple lives as well as supernatural abilities. ⏎  ⏎ His feelings toward Eureka, the one who created Green Earth, are complex. ⏎ He chose to target Iris, a girl with the same powers over creation Eureka had, to prove that the hearts and minds of those from Green Earth were worth something.

### dic\_pilot\_DEWEY\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b007`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b007\]
> JP (źródło tłumaczenia): 　アイリスを捕獲したものの、彼女を救出に来たエウレカに敗れる。 ⏎ 　死の間際、胸の内をエウレカに語りながら、世界を崩壊させるために旧星間宇宙移民船を地球へと落下させる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Though he took Iris captive, Eureka arrived to rescue her and defeated him. ⏎  ⏎ On the brink of death, he laid his heart bare to Eureka, then sent the old interstellar immigration spaceship plummeting toward Earth to destroy the world.　

### dic\_pilot\_RENTN\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b008`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b008\]
> JP (źródło tłumaczenia): 　エウレカと愛し合う少年。 ⏎ 　事故によりエウレカの目の前で死亡し、その後のエウレカが創り出した幾多の世界でも生命を落とし続ける。 ⏎ 　しかしエウレカは、どこかの世界でレントンが生きている事を信じている。
> EN (odniesienie oficjalne, NIE polski): The boy who returned Eureka's love. ⏎  ⏎ He died in an accident before Eureka's eyes, and despite the many worlds Eureka created after that, he continued to lose his life in each one. ⏎  ⏎ Nevertheless, Eureka believed Renton was still alive in some world.

### dic\_pilot\_RENTN\_00\_1

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b009`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b009\]
> JP (źródło tłumaczenia): 　その存在はニルヴァーシュＺと共にあり、エウレカと世界を救うために手を差し伸べ、全てが終わった後、エウレカと再会を果たした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He existed as one with Nirvash Z, and he reached out to help Eureka save the world. At the end of it all, he finally reunited with Eureka.

### dic\_pilot\_LLSH\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00a`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b00a\]
> JP (źródło tłumaczenia): 　神聖ブリタニア帝国第９９代唯一皇帝。 ⏎ 　貴族制度の廃止など、神聖ブリタニア帝国の根幹を揺るがす改革を断行すると同時に、世界の全てを掌握するため反対勢力を力によって一掃しようとする。
> EN (odniesienie oficjalne, NIE polski): The ninety-ninth emperor of the Holy Britannian Empire, as well as its last. ⏎  ⏎ He would shake that empire with countless drastic changes to the core of the nation, such as ending the systems of nobility.  ⏎  ⏎ At the same time, he also sought to claim the whole world and laid low all opposition to his conquest through pure might.

### dic\_pilot\_SUZAK\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00c`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b00c\]
> JP (źródło tłumaczenia): 　皇帝ルルーシュの騎士。 ⏎ 　かつてはナイトオブラウンズの一人であったが、ルルーシュの即位と共に彼の唯一の騎士としてナイトオブゼロを名乗る。 ⏎ 　世界を掌握しようとするルルーシュに従い、その覇道の障害となる者と戦う。
> EN (odniesienie oficjalne, NIE polski): A knight of Emperor Lelouch. ⏎  ⏎ One of the former Knights of the Round, he became the one and only knight after Lelouch took the throne with the title of the Knight of Zero. ⏎  ⏎ Committed to Lelouch's conquest, he fought any and all who would serve to obstruct it.

### dic\_pilot\_CC\_E\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b00e`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b00e\]
> JP (źródło tłumaczenia): 　皇帝ルルーシュの側近の一人。 ⏎ 　ルルーシュの覇道に従い、彼の盾として戦う。
> EN (odniesienie oficjalne, NIE polski): One of Emperor Lelouch's closest aides. ⏎  ⏎ She is committed to his conquest and willing to fight as his shield.

### dic\_pilot\_JEREM\_A\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b010`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b010\]
> JP (źródło tłumaczenia): 　皇帝ルルーシュの忠実な家臣。 ⏎ 　ブリタニア皇族の中でもマリアンヌ妃に強い忠誠を誓い、その息子であるルルーシュの覇道に付き従う。
> EN (odniesienie oficjalne, NIE polski): A loyal servant of Emperor Lelouch. ⏎  ⏎ Deeply loyal to Empress Marianne, he fights to further the conquest of Lelouch, her son.

### dic\_pilot\_KAREN\_A\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b012`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b012\]
> JP (źródło tłumaczenia): 　ブリタニア貴族の父と日本人の母の間に生まれたハーフで、黒の騎士団創設時からのメンバー。１８歳。 ⏎ 　神聖ブリタニア帝国の精鋭であるナイトオブラウンズにも匹敵すると評された腕と愛機の紅蓮で、幾多の戦場で勝利を収めてきた。 ⏎ 　黒の騎士団から追放されたゼロが皇帝ルルーシュとなった際、会談の場で再会したルルーシュに決別のキスを贈った後、仲間達と共に彼の覇道の前に立ち塞がった。
> EN (odniesienie oficjalne, NIE polski): A half-Japanese girl born to a Britannian noble father and a Japanese mother, she is one of the original members of the Order of the Black Knights. ⏎  ⏎ Aboard her beloved machine, the Guren, she fought across many battlefields, claiming victory after victory, and would earn recognition as a pilot as skilled as any Knight of the Round. ⏎  ⏎ When Zero was exiled from the Black Knights and became Emperor Lelouch, she gave him a farewell kiss at their final meeting and then joined her comrades in opposing his conquest.

### dic\_pilot\_USPR\_S\_00\_0

Adres: `dic\_text\_pilot-DLC3/000013e4:23a0b014`

> \[BRAK PL: dic\_text\_pilot-DLC3/000013e4:23a0b014\]
> JP (źródło tłumaczenia): 　自ら「簒奪者」を名乗る謎の人物。 ⏎ 　普段は道化を模した仮面をかぶっており、素性は隠している。 ⏎ 　その正体は、エーアデント住民の四城カノトであり、アニーナに強く想いを寄せている。 ⏎ 　様々な世界から無限の力を持つ者を集め、その力によってアニーナと自分の理想郷を創り上げるため、世界の破壊と再生を目論む。 ⏎ 　元々の性格は少し気弱なお調子者であったが、身に余る力を手に入れた事により、残忍で自分本位な人間へと変質していった。
> EN (odniesienie oficjalne, NIE polski): A mysterious man who took on the name "Usurper". He hides his true identity behind a clown mask at all times. ⏎  ⏎ His true identity is Kanoto Shijo, a resident of A. Advent who is deeply infatuated with Annina. ⏎  ⏎ He has gathered wielders of infinite power from other worlds for the sole purpose of destroying the world and rebuilding it into an ideal paradise for himself and Annina. ⏎  ⏎ He was originally a timid, joyless man, but gaining power has turned him cruel and selfish.

### dic\_pilot\_KENAN\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84428000`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84428000\]
> JP (źródło tłumaczenia): 　ＭＳ開発評議会の監査組織カテドラル直轄の特殊部隊「ドミニコス隊」の司令。 ⏎ 　２１年前のヴァナディース事変では、ベギルベウのパイロットとして大きな戦果を挙げた。 ⏎ 　現在は司令として艦隊指揮を担う。 ⏎ 　２１年の間に大きく体型が変わっている。
> EN (odniesienie oficjalne, NIE polski): A commander in the Dominicus Force, a special forces unit under the direct supervision of Cathedra, the Mobile Suit Development Council's auditing organization. ⏎  ⏎ He made a name for himself as the pilot of the Beguir-Beu during the Vanadis Incident twenty-one years ago. ⏎  ⏎ He currently serves as a fleet commander. ⏎  ⏎ Physically, he has changed a lot in the last twenty-one years.

### dic\_pilot\_KENAN\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28000`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28000\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_NAZI\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28001`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28001\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」のリーダー。 ⏎ 　シャディクと通じており、プラント・クエタのデリング襲撃時には、輸送船をハイジャックして作戦を指揮した。
> EN (odniesienie oficjalne, NIE polski): Leader of the Dawn of Fold, an anti-Spacian organization. ⏎  ⏎ He's secretly connected to Shaddiq, and during their attack on Delling and Plant Quetta, he hijacked the transport and commanded the operation.

### dic\_pilot\_OLCOT\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28003`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28003\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」の一員で、モビルスーツ隊を率いる。 ⏎ 　歴戦の勇士で仲間からの信頼も厚い。
> EN (odniesienie oficjalne, NIE polski): A member of the Dawn of Fold, an anti-Spacian organization, and leader of their Mobile Suit team. ⏎  ⏎ He's a battle-hardened hero who has earned the full trust of his comrades.

### dic\_pilot\_OLCOT\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:84c28004`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:84c28004\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_SOFI\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028000`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028000\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」の一員。 ⏎ 　ガンダム・ルブリス・ウルのパイロットを務める。 ⏎ 　自分の本能に素直で、欲求を満たすためならば暴力をいとわない。 ⏎ 　心には常に渇いた飢えがあり、何より本物の家族を欲していた。 ⏎ 　スレッタとエアリアルに関心を抱き、自らを「地球の魔女」とする。
> EN (odniesienie oficjalne, NIE polski): A member of the Dawn of Fold, an anti-Spacian organization, who pilots the Gundam Lfrith Ur. ⏎  ⏎ She is honest about her desires and does not hesitate to use violence to satisfy them. ⏎  ⏎ There has always been a void in her heart, and more than anything, she longs for a real family. ⏎  ⏎ She is interested in Suletta and the Aerial, and she calls herself a "witch from Earth".

### dic\_pilot\_SOFI\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028001`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028001\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_NOREA\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028002`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028002\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」の一員。 ⏎ 　ガンダム・ルブリス・ソーンのパイロットを務める。 ⏎ 　ソフィとバディを組んでおり、暴走しがちな彼女をいさめる役。 ⏎ 　アーシアンの悲惨な境遇からスペーシアンに強い憎悪を持つ。
> EN (odniesienie oficjalne, NIE polski): A member of the Dawn of Fold, an anti-Spacian organization. ⏎  ⏎ She pilots the Gundam Lfrith Thorn. ⏎  ⏎ She frequently has to admonish her team partner Sophie, who tends to run amok. ⏎  ⏎ She harbors a powerful hatred of Spacians because of the miserable conditions faced by Earthians.

### dic\_pilot\_NOREA\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028003`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028003\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_CEDO\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028004`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028004\]
> JP (źródło tłumaczenia): 　地球の特定復興計画地区で暮らすアーシアンの少年。 ⏎ 　年相応に臆病だが、シーシアのことを気にかけ行動を共にする。
> EN (odniesienie oficjalne, NIE polski): An Earthian boy living in a designated recovery plan area on Earth. ⏎  ⏎ Though timid for his age, he cares about Seethia and stays by her side.

### dic\_pilot\_CEDO\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028005`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028005\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_LEADER\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028006`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028006\]
> JP (źródło tłumaczenia): 　ミオリネが平和的な対話を臨んだ際のデモ隊の交渉人。 ⏎ 　ベネリットグループの不当な治安維持活動を非難し、地球からスペーシアンが出ていくことをミオリネに要求した。
> EN (odniesienie oficjalne, NIE polski): The protesters' negotiator when Miorine took part in peace talks. ⏎ He criticized the Benerit Group's unfair public security activities and demanded that all Spacians leave Earth.

### dic\_pilot\_LEADER\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028007`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028007\]
> EN (odniesienie oficjalne, NIE polski): 　As a result of their discussions, he came to trust Miorine somewhat, promising her a temporary cessation of protests until the Benerit Group's presidential election could be held. However, a battle immediately broke out which ruined the talks altogether.

### dic\_pilot\_ELICT\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028008`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028008\]
> JP (źródło tłumaczenia): 　プロスペラの娘。 ⏎ 　２１年前のヴァナディース事変の後、母と共に水星に逃げ延びたが、宇宙の環境に耐えられず、GUND技術によってガンダム・エアリアルに生体コードを移された。 ⏎ 　以降、ガンダム・エアリアルがその体となり、エアリアルに搭乗したスレッタをデータストームから守ってきた。 ⏎ 　データストームの中でしか生存できないエリクトの居場所を作るため、プロスペラはクワイエット・ゼロを建造し、エリクトはそれを止めようとするスレッタたちの前に立ち塞がった。
> EN (odniesienie oficjalne, NIE polski): Prospera's daughter. ⏎  ⏎ During the Vanadis Incident twenty-one years ago, she fled to Mercury with her mother. However, she was unable to withstand the environment in space, prompting Prospera to use GUND technology to transfer her biometric code into the Gundam Aerial. ⏎  ⏎ Since then, Ericht has been the very body of the Gundam Aerial, protecting the pilot, Suletta, from data storms. ⏎  ⏎ Prospera constructed Quiet Zero to create a place for Ericht to live, since she could only live in data storms. When Suletta and the others tried to stop them, Ericht stood in their way.

### dic\_pilot\_ELICT\_00\_1

Adres: `dic\_text\_pilot-DLC4/000dfe0d:85028009`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:85028009\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_GOOGOL\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800a`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:8502800a\]
> JP (źródło tłumaczenia): 　３０００年後の未来世界で人類と戦いを繰り広げる謎の存在「ウツロ」が、その時代の特戦隠密「朧」の頭領である月ノ輪プサイに擬態したもの。 ⏎ 　人間という存在に興味を持ち、人類の歴史の大きな転換期を観察に来た。 ⏎ 　成長や繁殖、感情や生命といったものを持たない「ウツロ」は生物とは異なる何かであり、「概念」が形を成したものである。そのため物理的なダメージを受けても三次元世界に置かれた姿がいくらかの影響を受けるだけであり、その根源が消滅する事はない。「ウツロ」を消滅させるためには、高次元にある真の存在を直接攻撃するか、三次元世界上の概念を崩壊させる必要がある。 ⏎ 　人間から心や感情を学んだ事により、その概念は失われ、代わりに生命を得る。
> EN (odniesienie oficjalne, NIE polski): The mysterious being known as the Void who fights against humankind in the future world 3000 years from now, in its mimicry of Psi Tsukinowa, the head of the Special Stealth Forces Haze in that era. ⏎  ⏎ Its interest in the beings known as humans prompted it to observe a major turning point in mankind's history. ⏎  ⏎ The Void is not a living creature—it cannot grow or reproduce, and it has no emotions or life. Rather, it is a concept made manifest. As such, attacking it physically only has a minor effect on the part of it that exists within the three-dimensional world; such attempts will never be able to destroy the Void. In order to do so, one needs to directly attack its true form in a higher dimension or destroy its concept in the three-dimensional world. ⏎  ⏎ By learning from humans about hearts and emotions, its concept was lost, and it gained life in exchange.

### dic\_pilot\_YAGAMI\_S\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800c`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:8502800c\]
> JP (źródło tłumaczenia): 　エチカの父・八神テツロウが虚獣マグダと融合した姿。 ⏎ 　八神テツロウはイザナの目覚めの際の事故で死亡したと思われていたが、父親と母親という存在に興味を持ったグーゴル・プレックスに観察対象として回収されていた。 ⏎ 　虚獣マグダと融合した事で「ウツロ」に触れ、その精神は異常をきたして自我は崩壊している。残されているのは醜いエゴと自身の最高傑作であるエチカへの執着だけであり、ただひたすらにエチカを求め続ける。
> EN (odniesienie oficjalne, NIE polski): Echika's father, Tetsuro Yagami, fused with the Void Beast Magudda. ⏎  ⏎ Tetsuro Yagami was thought to have died in the accident that resulted in Izana's awakening, but he was retrieved as an observation subject by Googolplex, who had developed an interest in mothers and fathers. ⏎  ⏎ In fusing with the Void Beast Magudda, he touched the Void, which caused his mind to malfunction and his ego to collapse. All that's left of him are a terrible ego and an attachment to his greatest masterpiece, Echika. He continues to do nothing but seek her out.

### dic\_pilot\_CROW\_00\_0

Adres: `dic\_text\_pilot-DLC4/000dfe0d:8502800e`

> \[BRAK PL: dic\_text\_pilot-DLC4/000dfe0d:8502800e\]
> JP (źródło tłumaczenia): 　スコート・ラボ所属の次元獣バスター。 ⏎ 　破界事変では愛機ブラスタと共に自由と平和を求めて戦い、多額の借金の返済にも成功した。 ⏎ 　ニヒルな無頼漢を気取るが、そのポーズが長続きしない二枚目半。様々な特技を持ち、軍隊格闘術システマを駆使し、生身での戦闘でも実力を発揮する。 ⏎ 　女嫌いを自称し、美人は信用しないと公言する。その原因は過去に由来するが、本人は語ろうとしない。 ⏎ 　軍の特殊部隊「ファイヤバグ」に所属していた事を悔いており、それについて触れられる事を嫌がる。 ⏎ 　破界事変後はサラリーマン次元獣バスターとして、世界各地に出没する次元獣退治を生業としていたが、新たな借金を背負う事になり、戦いに身を投じていく。 ⏎ 　その戦いの中、新たな愛機リ・ブラスタと共に「揺れる天秤」のスフィアに目覚めていく。が、借金の宿命から逃れる事は出来なかった。 ⏎ 　超時空修復後も借金返済に追われるが、それなりに満足のいく日々を送る。
> EN (odniesienie oficjalne, NIE polski): A Damon Buster working for the Scott Lab. ⏎  ⏎ He fought for peace and freedom in his mech, the Brasta, during the Time of Ruination and repaid his hefty debt in the process. ⏎  ⏎ He tries to look like a pessimist and a cad, but he always ends up outing himself as a joker. He has many skills, and with his training in the military martial art Cistema, can fight on foot as well as in a robot. ⏎  ⏎ He claims to distrust women—especially pretty ones—because of something that happened in his past, but he refuses to elaborate. ⏎  ⏎ His membership in the Firebugs, a military special ops squad, is one of his biggest regrets, and he doesn't like it when the subject is brought up. ⏎  ⏎ After the Time of Ruination came to an end, he became a full-time Damon Buster, exterminating the Damons that continued to appear around the world. Eventually, though, he once again ended up burdened with debt and threw himself back into the fray. ⏎  ⏎ As he fought on in his new mech, the Li-Brasta, his Sphere—the Wavering Scales—began to awaken. In the end, he was never able to escape from his debt-ridden destiny. ⏎  ⏎ Debt collectors hounded him even after the dimensions were repaired, but he's fairly satisfied with his life regardless.

### dic\_pilot\_ERAN\_D\_00\_0

Adres: `dic\_text\_pilot-DLC4/0036f7c2:4220b000`

> \[BRAK PL: dic\_text\_pilot-DLC4/0036f7c2:4220b000\]
> JP (źródło tłumaczenia): 　ペイル社のＡＩ評価システム「ペイル・グレード」でトップグレードの評価を誇る次期ＣＥＯ候補。 ⏎ 　モビルスーツ操縦適性は低く、ミオリネの花婿を決める「決闘」が始まったため、影武者の強化人士を送り、自身はペイル社に身を隠していた。
> EN (odniesienie oficjalne, NIE polski): A candidate for the next CEO who boasts a top-grade evaluation in Peil's AI assessment system, Peil Grade. ⏎  ⏎ However, he has a low aptitude for Mobile Suit piloting, and when the duels to select Miorine's groom began, he sent an enhanced body double in his place while remaining hidden within the company.

### dic\_pilot\_ERAN\_5S\_00\_0

Adres: `dic\_text\_pilot-DLC4/0036f7c2:4320b000`

> \[BRAK PL: dic\_text\_pilot-DLC4/0036f7c2:4320b000\]
> JP (źródło tłumaczenia): 　ベネリットグループ御三家であるペイル・テクノロジーズが擁立するパイロット。 ⏎ 　アスティカシア高等専門学園パイロット科３年生で、ペイル寮の筆頭と決闘委員会のメンバーを務める。 ⏎ 　その正体は本物のエラン・ケレスと同じ容姿に整形された影武者であり、ペイル社では「強化人士５号」と呼ばれている。 ⏎ 　天使のような笑顔を持つが、自身を「命の安い者」と例えながら誰よりも生に執着し、生き延びようとあがいている。 ⏎ 　株式会社ガンダムのテストパイロットとなり、地球寮に協力する。
> EN (odniesienie oficjalne, NIE polski): A pilot backed by Peil Technologies, one of the Three Branches of the Benerit Group. ⏎  ⏎ He is a third-year piloting student at Asticassia School of Technology who serves as head of Peil House and one of the members of the Dueling Committee. ⏎  ⏎ His true identity is a body double who has been altered to look like the real Elan Ceres. At Peil Technologies, he is known as "Enhanced Person \#5". ⏎  ⏎ Although he describes himself as someone whose life is cheap, he clings to life more than anyone and struggles to survive. ⏎  ⏎ He becomes a test pilot for GUND-ARM Inc. and cooperates with Earth House.

### dic\_pilot\_SLETA\_G\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800b`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:3782800b\]
> JP (źródło tłumaczenia): 　プロスペラの計画が進行する中、ミオリネに見放されたショックと、出生の秘密を知り、プロスペラとエアリアルとのつながりも断ち切れたことで失意の底にいた。しかし、戦闘で被害を受けた学園の復旧に奔走し、自分のやるべき事を見つけていく。 ⏎ 　自身がプロスペラの実の娘であるエリクト・サマヤの遺伝子から作られた「リプリチャイルド」であり、ガンダムの呪いを受けなかったのはエアリアルに生体コードを移されたエリクトが代わりに引き受けていたためである事を知った後、プロスペラとエリクトを止めるために行動する。 ⏎ 　クワイエット・ゼロ突入作戦では、データストームに苦しみながらもガンダム・キャリバーンを駆り、最後はエリクトと共に宇宙議会連合の惑星間レーザー送電システムを停止させた。 ⏎ 　クワイエット・ゼロの事件から３年後は、データストームによりダメージを負った体のリハビリを行ないながら、幸せに暮らしている。
> EN (odniesienie oficjalne, NIE polski): 　As Prospera's plan progressed, she fell into a deep despair from the shock of being abandoned by Miorine, discovering the truth about her birth, and losing her connection to Prospera and the Aerial. However, while restoring the school after it was damaged in battle, she began to figure out what she needed to do. ⏎  ⏎ After learning that she was a repli-child created from the genes of Ericht Samaya, Prospera's real daughter, and that she hadn't suffered from the Gundam's curse because Ericht, whose biometric code had been transferred into the Aerial, had borne it in her place, she took action to stop Prospera and Ericht. ⏎  ⏎ During the operation to breach Quiet Zero, she piloted the Gundam Calibarn while enduring the data storm. In the end, she and Ericht stopped the Space Assembly League's interplanetary laser power transmission system. ⏎  ⏎ Three years after the Quiet Zero incident, she lives happily while undergoing rehabilitation for the damage her body suffered from the data storm.

### dic\_pilot\_MIOLN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800c`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:3782800c\]
> JP (źródło tłumaczenia): 　プロスペラによるスレッタへのマインドコントロールともいえる扱いを知り、今後プロスペラがスレッタとかかわらないことを条件に次期総裁になることを決意する。 ⏎ 　総裁選への実績作りのために抗議デモを続ける地球側との会談に臨むが、プロスペラの計略によって大規模な戦闘が起きた事で交渉は決裂する。自責の念に駆られ自室に閉じこもっていたが、スレッタの真っ直ぐな気持ちに救われ、前に進む気概を取り戻す。 ⏎ 　周囲と協力してクワイエット・ゼロへ直接乗り込みその機能を停止させた後、ベネリットグループ総裁として事件の終息を図るためにグループ解散を宣言した。 ⏎ 　クワイエット・ゼロの事件から３年後は、自身の起こしたクイン・ハーバーでの惨劇の償いのために、自らにできることを続けている。
> EN (odniesienie oficjalne, NIE polski): 　Upon learning that Prospera had been manipulating Suletta in a manner bordering on mind control, she decided to run for president on the condition that Prospera would have no further involvement with Suletta. ⏎  ⏎ To build her record for the presidential election, she began negotiations with the Earth side, which was holding protest demonstrations. However, the talks broke down when Prospera's scheme caused widespread fighting. Driven by guilt, she shut herself away in her room. However, she was saved by Suletta's sincerity and earnestness, regaining the will to move forward. ⏎  ⏎ After working with her allies to board Quiet Zero and disable it, she used her position as president of the Benerit Group to dissolve the Group and bring the incident to an end. ⏎  ⏎ Three years after the Quiet Zero incident, she continues to do what she can to atone for the Quin Harbor tragedy she unwittingly sparked.

### dic\_pilot\_GUERU\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800d`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:3782800d\]
> JP (źródło tłumaczenia): 　学園を去った後は「ボブ」を名乗り、輸送船で働いていた。 ⏎ 　反スペーシアン組織「フォルドの夜明け」のプラント・クエタ襲撃に巻き込まれ、モビルスーツで脱出するが、テロリストに誤認された結果、父・ヴィムの操縦する機体を意図せず撃墜してしまう。 ⏎ 　その後、父とのつながりである会社を立て直すため、学園に帰還しＣＥＯに就任。 ⏎ 　ミオリネと共に地球へ降りるが、そこでシャディクが「フォルドの夜明け」とのつながりがあることを知り、自らの手でシャディクの計画を阻止する。 ⏎ 　クワイエット・ゼロ突入作戦にも参加し、ミオリネを狙う弟・ラウダの駆るガンダム・シュバルゼッテと交戦する。グエルの身を挺した説得に救われ、フェルシーの助けもあり兄弟ともに生還を果たす。 ⏎ 　クワイエット・ゼロの事件から３年後は、ジェターク社ＣＥＯとして、エランやセセリアの協力を受け、やや立場の弱さに付け込まれながらも会社の再建に尽力している。
> EN (odniesienie oficjalne, NIE polski): After leaving the school, he adopted the name "Bob" and found work on a transport ship. ⏎  ⏎ He was caught up in the attack on Plant Quetta by the anti-Spacian organization, the Dawn of Fold, and escaped in a Mobile Suit. However, after being mistaken for a terrorist, he unintentionally shot down the unit piloted by his father, Vim. ⏎  ⏎ After that, he returned to school and became CEO in order to rebuild the company that connected him to his father. ⏎  ⏎ He descended to Earth with Miorine. Upon learning that Shaddiq had ties to the Dawn of Fold, he intervened to stop his plan. ⏎  ⏎ He also participated in the operation to breach Quiet Zero and fought against the Gundam Schwarzette, which was targeting Miorine and piloted by his younger brother, Lauda. Thanks to Guel's persuasion at the risk of his own life and Felsi's help, both brothers survived. ⏎  ⏎ Three years after the Quiet Zero incident, he serves as the CEO of Jeturk Heavy Machinery and is devoted to rebuilding it with the help of Elan and Secelia, although they often take advantage of his relatively weak standing.

### dic\_pilot\_SYADIK\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3782800f`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:3782800f\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」の活動を支援する黒幕であり、自らの計画のため、プラント・クエタを襲撃させ、さらにはグラスレー社ＣＥＯの養父・サリウス・ゼネリを誘拐・軟禁した。 ⏎ 　ペイル社の協力を取り付けて総裁選に立候補してミオリネの対抗馬となるが、「フォルドの夜明け」とのつながりをつかんだグエルとの戦闘に敗北し、その計画は潰えた。 ⏎ 　クワイエット・ゼロの事件から３年後は、自らの意思でクワイエット・ゼロに関する罪も被り、公判に向かう。
> EN (odniesienie oficjalne, NIE polski): 　The mastermind supporting the activities of the anti-Spacian organization, the Dawn of Fold. To advance his own agenda, he had Plant Quetta attacked and abducted his adoptive father, Sarius Zenelli, the CEO of Grassley Defense Systems. ⏎  ⏎ He secured Peil's cooperation and ran against Miorine in the presidential election; however, after being defeated in battle by Guel, who had discovered his connection to the Dawn of Fold, his plan came to an end. ⏎  ⏎ Three years after the Quiet Zero incident, he willingly takes responsibility for the crimes related to Quiet Zero and heads to trial.

### dic\_pilot\_NKA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828010`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828010\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_CHUCHU\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828011`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828011\]
> JP (źródło tłumaczenia): 　ランブルリングの事件をきっかけに自分の行動次第でスペーシアンとも友好な関係を築けると心境に変化が生じはじめる。「対話の大切さ」を胸に人と接するようになり、ニカの秘密を知った際も対話を求めるようになった。 ⏎ 　ノレアの学園襲撃時からブリオン寮提供のデミバーディングに乗り換え、クワイエット・ゼロへの突入ではミオリネ達を運ぶ役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、就職先でロウジを相棒に職務に励んでいる。罪を償ったニカとも再会し、他の地球寮の面々と共にスレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　After the Rumble Ring incident, her mindset changed. She realized that, depending on her actions, she could build friendly relationships with Spacians. Believing in the importance of dialogue, she began interacting with others in this manner. Even when she learned Nika's secret, she sought dialogue instead of conflict. ⏎  ⏎ After Norea attacked the school, she switched to the Demi Barding provided by Burion House. During the assault on Quiet Zero, she took on the role of transporting Miorine and the others. ⏎  ⏎ Three years after the Quiet Zero incident, she works hard at her job with Rouji as her partner. She also reunites with Nika, who has atoned for her crimes, and visits Suletta and the others with the rest of Earth House.

### dic\_pilot\_PROSPE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828012`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828012\]
> JP (źródło tłumaczenia): 　本名はエルノラ・サマヤ。　　 ⏎ 　水星へと逃げ延びた後、幼くして亡くなった愛娘エリクトの存在を何とかつなぎ止めようと、生体コードをガンダムに転移させた。 ⏎ 　また、パーメットスコアを上げる鍵としてリプリチャイルドのスレッタを創り出し、データストーム内でしか生きられないエリクトの居場所を作るためにクワイエット・ゼロを完成させた。 ⏎ 　最終的にプロスペラの計画はスレッタ達によって阻止されたが、スレッタとエリクトの願いを受け止め、３年後はスレッタとエリクトと共に余生を穏やかに過ごしている。
> EN (odniesienie oficjalne, NIE polski): Her real name is Elnora Samaya. ⏎  ⏎ After fleeing to Mercury, she transferred her beloved daughter Ericht's biometric code into a Gundam in an effort to preserve her existence after she died at a young age. ⏎  ⏎ She also created the repli-child Suletta as the key to raising the Permet Score and completed Quiet Zero to create a place where Ericht could live, as she could only exist within the data storm. ⏎  ⏎ Prospera's plan was ultimately thwarted by Suletta and her friends, and after accepting Suletta's and Ericht's wishes, she spends the rest of her life peacefully with them.

### dic\_pilot\_DERING\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828013`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828013\]
> JP (źródło tłumaczenia): 　反スペーシアン組織「フォルドの夜明け」のプラント・クエタ襲撃により、重体となる。 ⏎ 　意識不明の状態が続いたが、徐々に回復の兆しを見せ、その中でミオリネからも一応の理解を得られるようになった。クワイエット・ゼロの突入作戦においては宇宙議会連合に対して緊急特別総会の開催を要求することで貢献を果たした。
> EN (odniesienie oficjalne, NIE polski): 　The attack on Plant Quetta by the anti-Spacian organization, the Dawn of Fold, left him in critical condition. ⏎  ⏎ He remained unconscious for some time but gradually began to show signs of recovery. In the process, he was able to reach a new level of understanding with Miorine. During the operation to breach Quiet Zero, he contributed by demanding that the Space Assembly League convene an emergency special general assembly.

### dic\_pilot\_SALIUS\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828014`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828014\]
> JP (źródło tłumaczenia): 　意識不明が続くデリングの代わりに学園でのランブルリングの立会人となるが、シャディクに誘拐され、以降は軟禁状態となる。 ⏎ 　シャディクの逮捕により解放された後は、ベネリットグループ崩壊の危機に対して、総裁となったミオリネにアドバイスを送った。
> EN (odniesienie oficjalne, NIE polski): 　He became the witness for the Rumble Ring at the school in place of Delling, who was still unconscious at the time. However, he was later kidnapped by Shaddiq and placed under house arrest. ⏎  ⏎ After being freed following Shaddiq's arrest, he advised Miorine, the new president, regarding the crisis of the Benerit Group's collapse.

### dic\_pilot\_VIM\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828015`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828015\]
> JP (źródło tłumaczenia): 　デリングを排除するために「フォルドの夜明け」を手引きしたが、シャディクの計略により、プラント・クエタの襲撃に巻き込まれる。事態を打開するために自らモビルスーツで出撃するが、行方不明になっていたグエルをテロリストと誤認して交戦となり、撃墜されてしまう。グエル共々、そこで初めて戦っていた相手が誰であったかを知り、衝撃を受けるグエルにその身を案じる言葉を遺して死んでいった。
> EN (odniesienie oficjalne, NIE polski): 　He called in the Dawn of Fold to eliminate Delling, but due to Shaddiq's scheme, he became caught up in the attack on Plant Quetta. In an attempt to break the deadlock, he piloted a Mobile Suit personally. However, after mistaking the long-missing Guel for a terrorist, the two engaged in combat, and he was shot down. Only at that moment did he and Guel realize who they had been fighting against. He died leaving words of concern for his son, who was devastated by the revelation.

### dic\_pilot\_NEWGEN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828016`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828016\]
> JP (źródło tłumaczenia): 　アスティカシア高等専門学園内での一般生徒を巻き込んだ戦闘行為、グラスレー社のサリウスＣＥＯの誘拐、さらにはクワイエット・ゼロの秘匿開発といったベネリットグループの不祥事を宇宙議会連合に告発した。 ⏎ 　連合と組んでベネリットグループに壊滅的な打撃を与えた後に復興の主導権を握ろうとしたが、総裁となったミオリネによるグループ解散の声明により、その企みは阻止された。
> EN (odniesienie oficjalne, NIE polski): 　She reported several scandals involving the Benerit Group to the Space Assembly League. These included combat at Asticassia School of Technology involving ordinary students; the kidnapping of Grassley's CEO, Sarius; and the secret development of Quiet Zero. ⏎  ⏎ After collaborating with the League to deliver a devastating blow to the Benerit Group, she attempted to seize the initiative in the reconstruction process. However, her plans were thwarted when Miorine, the new president, announced the dissolution of the Group.

### dic\_pilot\_KAL\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37828017`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37828017\]
> JP (źródło tłumaczenia): 　アスティカシア高等専門学園内での一般生徒を巻き込んだ戦闘行為、グラスレー社のサリウスＣＥＯの誘拐、さらにはクワイエット・ゼロの秘匿開発といったベネリットグループの不祥事を宇宙議会連合に告発した。 ⏎ 　連合と組んでベネリットグループに壊滅的な打撃を与えた後に復興の主導権を握ろうとしたが、総裁となったミオリネによるグループ解散の声明により、その企みは阻止された。
> EN (odniesienie oficjalne, NIE polski): 　She reported several scandals involving the Benerit Group to the Space Assembly League. These included combat at Asticassia School of Technology involving ordinary students; the kidnapping of Grassley's CEO, Sarius; and the secret development of Quiet Zero. ⏎  ⏎ After collaborating with the League to deliver a devastating blow to the Benerit Group, she attempted to seize the initiative in the reconstruction process. However, her plans were thwarted when Miorine, the new president, announced the dissolution of the Group.

### dic\_pilot\_NEBORA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28000`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28000\]
> JP (źródło tłumaczenia): 　アスティカシア高等専門学園内での一般生徒を巻き込んだ戦闘行為、グラスレー社のサリウスＣＥＯの誘拐、さらにはクワイエット・ゼロの秘匿開発といったベネリットグループの不祥事を宇宙議会連合に告発した。 ⏎ 　連合と組んでベネリットグループに壊滅的な打撃を与えた後に復興の主導権を握ろうとしたが、総裁となったミオリネによるグループ解散の声明により、その企みは阻止された。
> EN (odniesienie oficjalne, NIE polski): 　She reported several scandals involving the Benerit Group to the Space Assembly League. These included combat at Asticassia School of Technology involving ordinary students; the kidnapping of Grassley's CEO, Sarius; and the secret development of Quiet Zero. ⏎  ⏎ After collaborating with the League to deliver a devastating blow to the Benerit Group, she attempted to seize the initiative in the reconstruction process. However, her plans were thwarted when Miorine, the new president, announced the dissolution of the Group.

### dic\_pilot\_GOLNE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28001`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28001\]
> JP (źródło tłumaczenia): 　アスティカシア高等専門学園内での一般生徒を巻き込んだ戦闘行為、グラスレー社のサリウスＣＥＯの誘拐、さらにはクワイエット・ゼロの秘匿開発といったベネリットグループの不祥事を宇宙議会連合に告発した。 ⏎ 　連合と組んでベネリットグループに壊滅的な打撃を与えた後に復興の主導権を握ろうとしたが、総裁となったミオリネによるグループ解散の声明により、その企みは阻止された。
> EN (odniesienie oficjalne, NIE polski): 　She reported several scandals involving the Benerit Group to the Space Assembly League. These included combat at Asticassia School of Technology involving ordinary students; the kidnapping of Grassley's CEO, Sarius; and the secret development of Quiet Zero. ⏎  ⏎ After collaborating with the League to deliver a devastating blow to the Benerit Group, she attempted to seize the initiative in the reconstruction process. However, her plans were thwarted when Miorine, the new president, announced the dissolution of the Group.

### dic\_pilot\_RAUDA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28003`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28003\]
> (brak tekstu źródłowego w S6)

### dic\_pilot\_FELCY\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28004`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28004\]
> JP (źródło tłumaczenia): 　グエルがジェターク寮を離れてからは、決闘の立会人の代理を務めたり、ランブルリングに出場したりした。 ⏎ 　グエルとラウダが壮絶な戦いを繰り広げた際には、グエルの機体の爆発を防いで兄弟を救うという活躍を見せた。 ⏎ 　クワイエット・ゼロの事件から３年後は、学園を卒業したジェターク寮の仲間たちと一緒に働いている。
> EN (odniesienie oficjalne, NIE polski): 　After Guel left Jeturk House, she served as a substitute witness for duels and took part in the Rumble Ring. ⏎  ⏎ When Guel and Lauda fought a fierce battle, she was instrumental in preventing Guel's unit from exploding and saving the brothers. ⏎  ⏎ Three years after the Quiet Zero incident, she works with her fellow members of Jeturk House who graduated from the academy.

### dic\_pilot\_PETRA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28005`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28005\]
> JP (źródło tłumaczenia): 　暴走したノレアが学園内を破壊した際に、建物の倒壊に巻き込まれて重傷を負う。 ⏎ 　クワイエット・ゼロの事件から３年後は、義足をつけながら、株式会社ガンダムのテスターとなり、ラウダと共に穏やかな日々を過ごしている。
> EN (odniesienie oficjalne, NIE polski): 　When Norea went on a rampage and destroyed part of the school, she was caught in a building collapse and suffered serious injuries. ⏎  ⏎ Three years after the Quiet Zero incident, she lives peacefully with Lauda, wearing a prosthetic leg and working as a tester for GUND-ARM Inc.

### dic\_pilot\_SSRIA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28006`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28006\]
> JP (źródło tłumaczenia): 　ニカについて悩むマルタンに対して本音を引き出し、地球寮の仲間に真実を打ち明けるきっかけを作った。 ⏎ 　暴走したノレアが学園を攻撃した際、地球寮のチュチュにブリオン社の新型機「デミバーディング」を貸与した。 ⏎ 　クワイエット・ゼロの事件の３年後は、オリジナルのエラン・ケレスと組んで仕事をしている。
> EN (odniesienie oficjalne, NIE polski): 　She drew out Martin's true feelings as he worried over Nika, creating the opportunity for him to tell the truth to the members of Earth House. ⏎  ⏎ When Norea went on a rampage and attacked the school, she lent Burion Company's new model, the Demi Barding, to Earth House's Chuchu. ⏎  ⏎ Three years after the Quiet Zero incident, she works together with the original Elan Ceres.

### dic\_pilot\_ROUJI\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28007`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28007\]
> JP (źródło tłumaczenia): 　自らの興味からクワイエット・ゼロの突入作戦に参加した。 ⏎ 　クワイエット・ゼロの事件から３年後は、チュチュと同じ職場で働いている。
> EN (odniesienie oficjalne, NIE polski): 　He took part in the operation to breach Quiet Zero out of his own interest. ⏎  ⏎ Three years after the Quiet Zero incident, he works alongside Chuchu.

### dic\_pilot\_MALTN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28008`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28008\]
> JP (źródło tłumaczenia): 　偶然からニカがテロリストの一員である事を知り、葛藤の末に彼女をフロント管理会社に通報した。 ⏎ 　仲間を差し出した事に人知れず苦しんだが、事実を地球寮の面々に告白し、彼らと共にニカと正面から向き合う事を決めた。 ⏎ 　クワイエット・ゼロの突入作戦では自ら志願し、寮長に恥じない行動をした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　He learned by chance that Nika was working with terrorists. After wrestling with his inner conflict, he reported her to the Front's management company. ⏎  ⏎ He struggled privately over having turned in a friend but confessed to the Earth House members and decided to confront Nika with them. ⏎  ⏎ During the operation to breach Quiet Zero, he volunteered and acted like a true House head. ⏎  ⏎ Three years after the Quiet Zero incident, she reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_NUNO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28009`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28009\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロの突入作戦では、地球寮の一員として自分の出来る役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　He did what he could as a member of Earth House during the operation to breach Quiet Zero.  ⏎  ⏎ Three years after the Quiet Zero incident, he reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_OJRO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800a`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c2800a\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロの突入作戦では、地球寮の一員として自分の出来る役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　He did what he could as a member of Earth House during the operation to breach Quiet Zero.  ⏎  ⏎ Three years after the Quiet Zero incident, he reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_TIL\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800b`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c2800b\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロの突入作戦では、地球寮の一員として自分の出来る役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　He did what he could as a member of Earth House during the operation to breach Quiet Zero.  ⏎  ⏎ Three years after the Quiet Zero incident, he reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_RRKE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800c`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c2800c\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロの突入作戦では、地球寮の一員として自分の出来る役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　She did what she could as a member of Earth House during the operation to breach Quiet Zero.  ⏎  ⏎ Three years after the Quiet Zero incident, she reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_ALYA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800d`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c2800d\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロの突入作戦では、地球寮の一員として自分の出来る役割を果たした。 ⏎ 　クワイエット・ゼロの事件から３年後は、罪を償ったニカと他の地球寮の面々と共に再会し、スレッタたちに会いに行った。
> EN (odniesienie oficjalne, NIE polski): 　She did what she could as a member of Earth House during the operation to breach Quiet Zero.  ⏎  ⏎ Three years after the Quiet Zero incident, she reunites with Nika, who has atoned for her crimes, and the other members of Earth House and goes to see Suletta and the others.

### dic\_pilot\_BELME\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c2800f`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c2800f\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロを止めるためにガンダム・キャリバーンに搭乗する決意をしたスレッタに危険性を訴え、これまで自分のやってきたことへの後悔と謝罪を口にした。 ⏎ 　ミオリネたちと共にクワイエット・ゼロに乗り込んだ際は、プロスペラと正面から対峙し、機能停止に貢献した。 ⏎ 　クワイエット・ゼロの事件から３年後は、宇宙議会連合のグストン・パーチェと共に墓参りに赴く。
> EN (odniesienie oficjalne, NIE polski):  ⏎ She warned Suletta about the danger of piloting the Gundam Calibarn to stop Quiet Zero and apologized for her actions up to that point. ⏎  ⏎ When she, Miorine, and the others boarded Quiet Zero, she confronted Prospera directly and helped shut it down. ⏎  ⏎ Three years after the Quiet Zero incident, she visits a cemetery with Guston Parche of the Space Assembly League.

### dic\_pilot\_SABINA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28010`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28010\]
> JP (źródło tłumaczenia): 　シャディクの計画に参加し、最終的には仲間たちと共に逮捕されたが、一連の事件はシャディクひとりの計画だったことになり、のちに釈放された。 ⏎ 　クワイエット・ゼロの事件から３年後は、できることをやり続けるというミオリネに同行している。
> EN (odniesienie oficjalne, NIE polski): 　She participated in Shaddiq's plan and was arrested alongside her comrades. However, the series of incidents was ultimately attributed to Shaddiq alone, and she was released. ⏎  ⏎ Three years after the Quiet Zero incident, she accompanies Miorine, who continues to do what she can do in the moment.

### dic\_pilot\_RENE\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28011`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28011\]
> JP (źródło tłumaczenia): 　シャディクの計画に参加し、最終的には仲間たちと共に逮捕されたが、一連の事件はシャディクひとりの計画だったことになり、のちに釈放された。 ⏎ 　クワイエット・ゼロの事件から３年後は、できることをやり続けるというミオリネに同行している。
> EN (odniesienie oficjalne, NIE polski): 　She participated in Shaddiq's plan and was arrested alongside her comrades. However, the series of incidents was ultimately attributed to Shaddiq alone, and she was released. ⏎  ⏎ Three years after the Quiet Zero incident, she accompanies Miorine, who continues to do what she can do in the moment.

### dic\_pilot\_ILIJA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28012`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28012\]
> JP (źródło tłumaczenia): 　シャディクの計画に参加し、最終的には仲間たちと共に逮捕されたが、一連の事件はシャディクひとりの計画だったことになり、のちに釈放された。 ⏎ 　クワイエット・ゼロの事件から３年後は、できることをやり続けるというミオリネに同行している。
> EN (odniesienie oficjalne, NIE polski): 　She participated in Shaddiq's plan and was arrested alongside her comrades. However, the series of incidents was ultimately attributed to Shaddiq alone, and she was released. ⏎  ⏎ Three years after the Quiet Zero incident, she accompanies Miorine, who continues to do what she can do in the moment.

### dic\_pilot\_MAYG\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28013`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28013\]
> JP (źródło tłumaczenia): 　シャディクの計画に参加し、最終的には仲間たちと共に逮捕されたが、一連の事件はシャディクひとりの計画だったことになり、のちに釈放された。 ⏎ 　クワイエット・ゼロの事件から３年後は、できることをやり続けるというミオリネに同行している。
> EN (odniesienie oficjalne, NIE polski): 　She participated in Shaddiq's plan and was arrested alongside her comrades. However, the series of incidents was ultimately attributed to Shaddiq alone, and she was released. ⏎  ⏎ Three years after the Quiet Zero incident, she accompanies Miorine, who continues to do what she can do in the moment.

### dic\_pilot\_EONA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:37c28014`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:37c28014\]
> JP (źródło tłumaczenia): 　シャディクの計画に参加し、最終的には仲間たちと共に逮捕されたが、一連の事件はシャディクひとりの計画だったことになり、のちに釈放された。 ⏎ 　クワイエット・ゼロの事件から３年後は、できることをやり続けるというミオリネに同行している。
> EN (odniesienie oficjalne, NIE polski): 　She participated in Shaddiq's plan and was arrested alongside her comrades. However, the series of incidents was ultimately attributed to Shaddiq alone, and she was released. ⏎  ⏎ Three years after the Quiet Zero incident, she accompanies Miorine, who continues to do what she can do at the moment.

### dic\_pilot\_KENAN\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428055`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38428055\]
> JP (źródło tłumaczenia): 　ベネリットグループの総裁選に立候補したミオリネとジェターク社ＣＥＯとなったグエルが地球に降下した際、護衛役として同行する。 ⏎ 　地球で出会った少年・セドから「フォルドの夜明け」とシャディクにつながりがあることをつかみ、グエルと共にアスティカシア高等専門学園へと向かい、シャディクの計画を阻止する。そこでの戦闘では自らもモビルスーツに搭乗し、ドミニコス隊を指揮した。 ⏎ 　以降もミオリネに協力し、彼女たちを守ってクワイエット・ゼロに突入し、その停止に貢献した。
> EN (odniesienie oficjalne, NIE polski): 　When Miorine, now a candidate for president of the Benerit Group, and Guel, already the CEO of Jeturk Heavy Machinery, descended to Earth, Kenanji accompanied them as an escort. ⏎  ⏎ After learning about the connection between the Dawn of Fold and Shaddiq from a boy named Sedo whom he met on Earth, he went to Asticassia School of Technology with Guel to stop Shaddiq's plot. During the battle, he piloted a Mobile Suit and took direct command of the Dominicus Force. ⏎  ⏎ After that, he continued to help Miorine, protecting and assisting her and the others as they stormed Quiet Zero and shut it down.

### dic\_pilot\_OLCOT\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428057`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38428057\]
> JP (źródło tłumaczenia): 　本名はリドリック・クルーヘル。 ⏎ 　かつてはドミニコス隊に所属しており、アーシアンのテロによって家族を失った過去を持つ。
> EN (odniesienie oficjalne, NIE polski): 　His real name is Ridrick Kruger. ⏎  ⏎ He once belonged to the Dominicus Force, having lost his family in an Earthian terrorist attack.

### dic\_pilot\_SOFI\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428058`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38428058\]
> JP (źródło tłumaczenia): 　自分たちの邪魔をする同志のニカを排除しようとするが、彼女を守ろうとするスレッタから決闘を申し込まれる。ランブルリングに乱入してスレッタと戦ったが、その最中、パーメットスコア上昇による負荷に耐えきれず生命を落とす。
> EN (odniesienie oficjalne, NIE polski): 　When Nika tried to get in her way despite being a comrade, Sophie attempted to eliminate her. Then, however, Suletta requested a duel to protect Nika. Sophie barged into the Rumble Ring and fought Suletta, but lost her life during the battle, unable to withstand an increase in her Permet Score.

### dic\_pilot\_NOREA\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38428059`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38428059\]
> JP (źródło tłumaczenia): 　ソフィと共にランブルリングで乱入するが、その後はシャディクによってグラスレー寮に軟禁される。 ⏎ 　任務のためガンダムに乗るが、心の奥では死の恐怖におびえ、本心では生きたいと願っていた。 ⏎ 　エアリアルが地球で破壊活動をする姿を見て暴走し、学園内を攻撃する。エランの説得によって動きを止めるが、ドミニコス隊に狙撃されて生命を落とした。
> EN (odniesienie oficjalne, NIE polski): 　She and Sophie burst into the Rumble Ring, but afterward, Shaddiq placed her under house arrest in Grassley House. ⏎  ⏎ Although she piloted a Gundam for her mission, deep down she feared death and truly wished to live. ⏎  ⏎ After seeing the Aerial causing destruction on Earth, she lost control and attacked the school. Elan convinced her to stop, but she was shot down by the Dominicus Force and lost her life.

### dic\_pilot\_CEDO\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:3842805a`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:3842805a\]
> JP (źródło tłumaczenia): 　ベネリットグループの攻撃によって友人のシーシアを失った後は、指定避難民として生活する。 ⏎ 　地球に降り立ったグエルと再会するも、そこでの何気ない一言をケナンジに詰問され、プリンスの正体がシャディクであることが判明する要因となった。 ⏎ 　クワイエット・ゼロの事件の３年後は、念願であった学校に通うようになっている。
> EN (odniesienie oficjalne, NIE polski): 　After losing his friend Seethia in an attack by the Benerit Group, he lived as a designated refugee. ⏎  ⏎ When he reunited with Guel, who had descended to Earth, he was closely questioned by Kenanji on a casual remark he'd made. That questioning led to the discovery that the Prince's true identity was Shaddiq. ⏎  ⏎ Three years after the Quiet Zero incident, Sedo begins attending school, fulfilling his greatest wish.

### dic\_pilot\_LEADER\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828000`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38828000\]
> JP (źródło tłumaczenia): 　会談によりミオリネに一応の信頼を寄せ、ベネリットグループの総裁選までは抗議活動の一時休止を約束するが、直後に発生した戦闘により交渉は決裂した。
> EN (odniesienie oficjalne, NIE polski): 　As a result of their discussions, he came to trust Miorine somewhat, promising her a temporary cessation of protests until the Benerit Group's presidential election could be held. However, a battle immediately broke out which ruined the talks altogether.

### dic\_pilot\_ELICT\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828001`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38828001\]
> JP (źródło tłumaczenia): 　宇宙議会連合の惑星間レーザー送電システムからプロスペラを守るため、体であるエアリアルは大きなダメージを受ける。その後、エアリアルは超広域のデータストームの展開によりパーメット粒子となって消滅するが、エリクトの生体コードはスレッタの持つキーホルダー「ホッツさん」の姿となった。 ⏎ 　クワイエット・ゼロの事件の３年後は、ミオリネとも打ち解けている。
> EN (odniesienie oficjalne, NIE polski): 　To protect Prospera from the Space Assembly League's interplanetary laser power transmission system, the Aerial, which served as her body, sustained significant damage. Afterward, the Aerial dissipated into Permet particles as the data storm expanded to cover a vast area. However, Ericht's biometric code was transferred into Suletta's Hots keychain. ⏎  ⏎ Three years after the Quiet Zero incident, she appears to have grown somewhat friendly with Miorine.

### dic\_pilot\_ERAN\_D\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828005`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38828005\]
> JP (źródło tłumaczenia): 　クワイエット・ゼロを巡る戦いの中、ペイル社に見切りをつけて、辞表を提出した。 ⏎ 　クワイエット・ゼロ消失から３年後は、セセリアと組んでジェターク社に事業斡旋などをしている。
> EN (odniesienie oficjalne, NIE polski): 　During the battle over Quiet Zero, he abandoned Peil Technologies and submitted his resignation. ⏎  ⏎ Three years after Quiet Zero's disappearance, he begins working with Secelia to arrange business deals for Jeturk.

### dic\_pilot\_ERAN\_5S\_00\_2

Adres: `dic\_text\_pilot-DLC4/00633a0d:38828006`

> \[BRAK PL: dic\_text\_pilot-DLC4/00633a0d:38828006\]
> JP (źródło tłumaczenia): 　学園に編入してきたノレア・デュノクには自らの境遇が重なり、死に急ぐ彼女を救い出そうと行動した。 ⏎ 　また、スレッタの境遇と覚悟を知った後は、クワイエット・ゼロへの突入に協力した。 ⏎ 　クワイエット・ゼロの事件から３年後は、ノレアの遺したスケッチブックに描かれた風景の場所を探して旅をしている。
> EN (odniesienie oficjalne, NIE polski): 　Seeing his own circumstances reflected in Norea Du Noc, who transferred into the school, he acted to save her as she rushed toward death. ⏎  ⏎ He also participated in the assault on Quiet Zero after learning about Suletta's circumstances and resolve. ⏎  ⏎ Three years after the Quiet Zero incident, he travels Earth in search of the places depicted in Norea's sketchbook.

### dic\_pilot\_NKA\_SY\_00\_0

Adres: `dic\_text\_pilot-DLC4/007a68e4:20828000`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:20828000\]
> JP (źródło tłumaczenia): 　地球寮に所属するメカニック科２年生。 ⏎ 　チュチュからは「ニカ姉」の愛称で呼ばれている。 ⏎ 　優しく穏やかな性格をしており、編入してきたスレッタに声をかけ、地球寮の一員となるきっかけを作った。 ⏎ 　メカニックとしての腕は優秀で、チュチュが搭乗するデミトレーナーのカスタムを手掛けた。
> EN (odniesienie oficjalne, NIE polski): A second-year mechanical department student belonging to Earth House. ⏎  ⏎ Is close with Chuchu. A kind and gentle person, she reached out to Suletta after the latter arrived at the school and was the one who sparked the events that led to her joining Earth House. ⏎  ⏎ She is a skilled mechanic who personally customized Chuchu's Demi Trainer.

### dic\_pilot\_NKA\_SY\_00\_1

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028000`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:22028000\]
> JP (źródło tłumaczenia): 　スレッタがフロント外宙域で決闘を行う際には、エアリアルに外部高機動推進ユニットを取り付ける作業を行った。 ⏎ 　しかし、地球寮の面々が知らない一面を持ち、シャディクとも密かにつながりを持っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Suletta must fight a duel in space outside the Front, Nika augmented Aerial with an external high-performance thruster unit. ⏎  ⏎ However, she has a side to her that the rest of Earth House is unaware of, as well as a secret connection with Shaddiq.

### dic\_pilot\_NKA\_SY\_00\_2

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028001`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:22028001\]
> JP (źródło tłumaczenia): 　シャディクと反スペーシアン組織「フォルドの夜明け」の連絡係であった。 ⏎ 　間接的ではあったが、その行動が仲間を危険に晒し、学園をも巻き込む惨事を生むことになった。 ⏎ 　その後、自分の力で地球と宇宙の架け橋になるという決心を固め、自分のやってきた事に向き合いながら、チュチュのデミバーディングに同乗してクワイエット・ゼロの突入作戦に参加する。 ⏎ 　クワイエット・ゼロの事件の後に自首をし、罪を償った３年後に地球寮の面々と再開した。
> EN (odniesienie oficjalne, NIE polski): She served as the liaison between Shaddiq and the anti-Spacian organization, the Dawn of Fold. ⏎  ⏎ Though indirectly, her actions endangered her friends and led to a tragedy engulfing the school. ⏎  ⏎ Afterward, she resolved to become a bridge between Earth and space and face what she had done as she joined the operation to breach Quiet Zero, riding with Chuchu in the Demi Barding. ⏎  ⏎ After the Quiet Zero incident, she turned herself in, and three years later, after atoning for her crimes, she reunites with the members of Earth House.

### dic\_pilot\_RAUDA\_S2\_00\_0

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028002`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:22028002\]
> JP (źródło tłumaczenia): 　ジェターク寮の副寮長でパイロット科３年生。 ⏎ 　グエルとは同学年だが、異母兄弟で弟にあたる。 ⏎ 　冷静かつ理性的な性格をしているが、強く兄を想う一面を持つ。
> EN (odniesienie oficjalne, NIE polski): Third-year piloting student and deputy leader of Jeturk House. ⏎  ⏎ As Guel's half-sibling by another mother, Lauda is actually his younger brother even though they are in the same school year. ⏎  ⏎ He is coolheaded and rational, yet also cares deeply for his brother.

### dic\_pilot\_RAUDA\_S2\_00\_1

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028003`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:22028003\]
> JP (źródło tłumaczenia): 　グエルが退寮となってからは寮長として周囲をまとめる。
> EN (odniesienie oficjalne, NIE polski): Takes over the house after Guel is kicked out.

### dic\_pilot\_RAUDA\_S2\_00\_2

Adres: `dic\_text\_pilot-DLC4/007a68e4:22028004`

> \[BRAK PL: dic\_text\_pilot-DLC4/007a68e4:22028004\]
> JP (źródło tłumaczenia): 　父・ヴィムの死後はジェターク社のＣＥＯ代理を務めるが、グエルが復帰してからはその座を譲ってサポートに回る。 ⏎ 　しかし、グエルへのコンプレックスとグエルがヴィムの生命を奪ったのを知った事により、全ての元凶はミオリネであると考え、クワイエット・ゼロを巡る戦いの中、グエルと対峙することになった。 ⏎ 　最終的にグエルの身を挺した説得に救われ、フェルシーの助けもあり、グエルと共に生還した。 ⏎ 　クワイエット・ゼロの事件から３年後は、ペトラに寄り添い、自身の道を歩み始めている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After the death of his father, Vim, he served as the acting CEO of Jeturk Heavy Machinery, but yielded the position to Guel upon his return and taking on a supporting role. ⏎  ⏎ However, due to his complicated feelings toward Guel and learning that his brother had killed Vim, he came to believe that Miorine was the root of all his suffering. During the conflict over Quiet Zero, he ended up clashing with Guel. ⏎  ⏎ Ultimately, he was saved by Guel, who risked his own life to persuade him, and with Felsi's help, they both survived. ⏎  ⏎ Three years after the Quiet Zero incident, he stays by Petra's side, walking his own path.

## Mechy — opisy

### dic\_robot\_RIDEEN\_00\_0

Adres: `dic\_text\_robot/014d369b:92e0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:92e0b000\]
> JP (źródło tłumaczenia): 　１万２０００年前に古代ムー帝国の科学によって造られた神秘のスーパーロボット。 ⏎ 　普段は神面岩に金色の素体状態で収容されており、洸が中に乗り込むこと（フェードイン）で動き出す。謎のエネルギー・ムートロンを使用し、装甲に使用されているムートロン金属は素体状態に戻ることで自己修復能力を発揮する。　 ⏎ 　また、内部には解明されていない部分も多く、戦いが進むに連れ、新たな機能が解放されていった。主な必殺技は鳥型へ変形してマッハ７のスピードで突撃するゴッドバード。 ⏎ 　ライディーンはムー帝国の皇帝ラ・ムーの血を引く洸にしか乗ることが出来ず、その操縦法は洸の身体の動きと一体化した独特のものである。
> EN (odniesienie oficjalne, NIE polski): A mysterious super robot constructed 12,000 years ago by the science of the ancient Empire of Mu. Normally hidden as a golden statue in the God Face Cliff, it activates when Akira joins with it by Fading In.  ⏎  ⏎ Its armor, constructed using mysterious mutron energy, can self-repair by returning its mutron alloy to its base state. Beyond this, it has many other hidden functions which are discovered over the course of countless battles.  ⏎  ⏎ It's main finishing attack is God Bird, in which it shifts into a bird form and crashes into its foes at mach 7.  ⏎  ⏎ Reideen can only be piloted by Akira, who carries the blood of Ra Mu, the emperor of the ancient Mu Empire, and its movements are directly linked to the movements of Akira's body.

### dic\_robot\_RIDEEN\_00\_1

Adres: `dic\_text\_robot/014d369b:9760b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b000\]
> JP (źródło tłumaczenia): 　妖魔大帝バラオとの決戦では解放されたムートロンにより、巨大化した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the final battle with Yoma Emperor Barao, it grows to a gigantic size using unleashed mutron energy.

### dic\_robot\_DROME\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b001\]
> JP (źródło tłumaczenia): 　妖魔帝国が送り込む妖魔獣。 ⏎ 　ガンテと共に現れ、空中や水中を自由に動き回る。 ⏎ 　口から火炎を吐く他、触手を使った攻撃を行う。 ⏎ 　戦闘力は高くはないが、大量に投入されて牽制や足止めなどに使われた。
> EN (odniesienie oficjalne, NIE polski): Yoma Beasts sent by the Yoma Empire. They often appear with Gantes, moving freely through both the sea and air. ⏎  ⏎ They can spit fire from their mouths and use their tentacles to smash their foes. ⏎  ⏎ Though they are not incredibly strong in combat, their large numbers make them effective for stopping enemies in their tracks.

### dic\_robot\_GNTE\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b003`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b003\]
> JP (źródło tłumaczenia): 　妖魔帝国の移動要塞型妖魔獣。 ⏎ 　全身が岩で出来ており、手を模した形をしている。 ⏎ 　指先の竜の口からミサイルや炎を放って攻撃する。 ⏎ 　中指に当たる頭部に妖魔帝国の戦闘指揮官が乗り込み、陣頭指揮を行う事もあった。
> EN (odniesienie oficjalne, NIE polski): A mobile fortress beast of the Yoma Empire. ⏎  ⏎ Its entire body is made of boulders, and shaped like a giant hand.  ⏎  ⏎ It can fire missiles and flames from each of the dragons that act as its fingers. The dragon acting as the middle finger will sometimes be piloted by a commander of the Yoma Empire.

### dic\_robot\_GARDON\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b005`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b005\]
> JP (źródło tłumaczenia): 　激怒巨烈獣ガンダーと豪雷巨烈獣ゲルドンが合体した姿。 ⏎ 　ガンダーが上半身、ゲルドンが下半身を構成する。 ⏎ 　それまでは妖魔帝国の幹部・激怒巨烈と豪雷巨烈の兄弟がそれぞれ用意した巨烈獣が妖魔大帝バラオの前で戦い、勝者がライディーンに挑戦してきたが、このガードンから両者の巨烈獣をバラオの力で一つにした合体巨烈獣が送り出されるようになった。 ⏎ 　ライディーンの二倍ほどの巨体を持ち、圧倒的なパワーが特徴。 ⏎ 　二体に分離する事も可能で、それぞれの巨烈獣の力を活かしながら戦う。
> EN (odniesienie oficjalne, NIE polski): The fused form of Gekido Fury Beast Gander and Gorai Fury Beast Geldon, with Gander as the top half and Geldon forming the bottom half. ⏎  ⏎ Up until the creation of this fused beast, the Gekido Fury and Gorai Fury brothers, pillars of the Yoma Empire, would have their Fury Beasts fight in front of Yoma Emperor Barao, with the victor being chosen to fight Reideen. ⏎ However, with Gandon, Barao used his power to fuse two of the Fury Beasts.  ⏎  ⏎ The fused form is twice the size of Reideen, with overwhelming power. ⏎ Gandon can also split into its original Fury Beasts, unleashing both of their powers as it fights.

### dic\_robot\_BRAO\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b007\]
> JP (źródło tłumaczenia): 　妖魔帝国の支配者。 ⏎ 　妖魔島から上半身が生えている形であったが、戦いの中で球根型の下半身があらわになった。 ⏎ 　ライディーンを遥かに凌ぐ巨体の持ち主であり、巨大な弓や鎌、大剣等の武器を扱う他、爪や頭部のツノから強力な破壊光線を発射する。
> EN (odniesienie oficjalne, NIE polski): Ruler of the Yoma Empire. ⏎  ⏎ Originally his lower half was planted in Yoma Island. However, over the course of the conflict, his bulbous bottom half was revealed.  ⏎  ⏎ He is far more massive than even Reideen and wields countless weapons, such as a giant bow, sickles, and a great sword. He can also fire a Destructive Beam from his claws and the horns on his head.

### dic\_robot\_COMV\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b009`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b009\]
> JP (źródło tłumaczenia): 　異星人の地球侵略を予測した南原博士が超電磁物理学を応用して開発した合体型のスーパーロボット。 ⏎ 　バトルジェット、バトルクラッシャー、バトルタンク、バトルマリン、バトルクラフトという５機のバトルマシンの合体によって完成する。合体キーワードは「レッツ、コンバイン」で、動力には超電磁エネルギーを使用し、装甲はサーメット製。 ⏎ 　なお、合体には各バトルマシンに搭乗する５人の脳波が同調しなくてはならず、小型ロボット・ロペットの計測でそれが確認されて、初めて合体可能となる。 ⏎ 　武装が多いことが特徴の１つであり、戦いの中でも何度か追加され、その総数は２０近くにも及ぶ。その中でも、自身を高速回転させてドリルのように敵を貫く必殺技「超電磁スピン」を多用する。
> EN (odniesienie oficjalne, NIE polski): A combining super robot developed by Dr. Nambara, who had predicted that the Earth would be invaded by an alien force in the near future. ⏎  ⏎ Combattler V is the result of the combination of the 5 Battle Machines: the Battlejet, the Battlecrasher, the Battletank, the Battlemarine, and the Battlecraft. Combattler's combination key-phrase is "Let's combine". It is powered by super electromagnetic energy, and its armor is made of cermet. ⏎  ⏎ It can only combine when the brainwaves of the Battle Team are aligned, a process assisted by the brainwave-measuring robot Ropet. ⏎  ⏎ Combattler V is known for its massive variety of weapons; during the course of the story, new weapons were added when needed, reaching a total count of almost 20. Its most frequent attack is the "Super Electromagnetic Spin" finisher, where Combattler V rotates at high speed, turning its entire body into a drill that pierces the enemy.

### dic\_robot\_BGGRD\_00\_0

Adres: `dic\_text\_robot/014d369b:9760b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9760b00b\]
> JP (źródło tłumaczenia): 　ガルーダが搭乗する巨大戦闘用ロボット。 ⏎ 　ガルーダに似た外観を持つ。 ⏎ 　開発半ばで放棄されていたものをガルーダが発見し、自ら完成させた。 ⏎ 　巨大な弓からミサイル矢を放つビッグボウの他、胸部からのミサイルや口からの火炎を武器に戦う。また、腕部にはチェーンソーが内蔵されている。 ⏎ 　自らがアンドロイドであったと知ったガルーダが、コン・バトラーＶと雌雄を決するべく乗り込み、死闘を繰り広げた。
> EN (odniesienie oficjalne, NIE polski): A giant fighting robot controlled by Garuda. ⏎  ⏎ Its appearance resembles that of Garuda himself. ⏎  ⏎ It had been abandoned mid-development, but Garuda finds it and personally completes it. ⏎  ⏎ It can shoot missiles from its chest and release flames from its mouth. It is equipped with the Big Bow, a weapon that launches missile arrows, and has a chainsaw built into its arm. ⏎  ⏎ After Garuda discovers that he is, in fact, an android, he controls this robot to have one last fight to the death with Combattler V.

### dic\_robot\_ZGN\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b000\]
> JP (źródło tłumaczenia): 　アナハイム・エレクトロニクスが開発した、エゥーゴの可変モビルスーツ。 ⏎ 　Ｚ計画で培われたノウハウの集大成となる機体で、ガンダムＭｋ－Ⅱのムーバブル・フレーム技術と、フライング・アーマーのアイデアを組み合わせて完成した。 ⏎ 　装甲材のガンダリウムγと新型ジェネレーターの採用によりパワーウェイトレシオに優れ、群を抜いた機動力を実現している。その高い出力は、メガ・バズーカ・ランチャーにも匹敵する威力を持つ携行武器、ハイパー・メガ・ランチャーの使用を可能とする。 ⏎ 　さらにウェイブ・ライダーに変形する事により、長大な航続力と加速力を発揮する。 ⏎ 単機での大気圏突入や大気圏内での単独飛行、僚機を背に搭載しての作戦行動など、あらゆる場面で活躍が可能な機体となっている。 ⏎ 　後に簡易サイコミュであるバイオセンサーが搭載された事で、研ぎ澄まされたカミーユの反応に対する追従性を手に入れた。さらに敵モビルスーツの動きに干渉して停止させるなど、仕様には含まれてない不可解な現象の発現も確認されている。 ⏎ 　後の第一次ネオ・ジオン抗争ではカミーユに代わり、ジュドーやルーが搭乗した。
> EN (odniesienie oficjalne, NIE polski): An AEUG transformable Mobile Suit developed by Anaheim Electronics. ⏎  ⏎ The culmination of all the know-how cultivated over the course of Project Zeta, the Zeta combines the Gundam Mk-II's Movable Frame technology and the Flying Armor concept. ⏎  ⏎ With Gundarium γ armor plating and a cutting-edge generator, it achieves an incredible power-weight ratio that gives it mobility far ahead of the curve. Its high output enables it to use a Hyper Mega Launcher, a handheld beam cannon with power on par with the Mega Bazooka Launcher. ⏎  ⏎ In addition, its Waverider transformation grants it a long cruise range and higher acceleration. It is capable of unassisted atmospheric re-entry and atmospheric flight, and it can carry escort units on its back, giving it a wide range of tactical uses. ⏎  ⏎ It has an onboard Biosensor, a simplified Psycommu device that enables the machine's systems to keep up with Kamille's keen reactions. It has also been seen exhibiting strange phenomena not outlined in its specs, such as interfering with the operational capabilities of enemy Mobile Suits. ⏎  ⏎ Later on, during the First Neo Zeon War, Judau, and Roux pilot it in Kamille's stead.

### dic\_robot\_GD2\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b002\]
> JP (źródło tłumaczenia): 　ティターンズがグリプスで独自に開発したモビルスーツ。 ⏎ 　初代ガンダムの再設計機であるが、その最大の特徴はコア・ブロック・システムを廃止し、ムーバブル・フレームを採用した事である。これによって、より人体に近い動きが可能となり、高い運動性を獲得した。 ⏎ 　他にも全周囲モニターのリニア・シート式コクピットや脱着式バルカン・ポッド・システムなど、新技術が各所に盛り込まれている。 ⏎ 　カミーユらの手によりティターンズから奪取されてエゥーゴの所属となった後、機体色をブラックからホワイトへと変更される。 ⏎ 　第一次ネオ・ジオン抗争では、主にエル・ビアンノが搭乗し、最新鋭モビルスーツ相手に奮闘した。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit independently developed at Gryps by the Titans. ⏎  ⏎ While it is a redesign of the first Gundam, it omits the Gundam's most distinctive feature, the Core Block System, in favor of a Movable Frame. This gives it more humanlike movement and greater maneuverability. ⏎  ⏎ It integrated other new technologies as well, such as a Linear Seat cockpit with monitors all around the pilot as well as a detachable Vulcan Pod system. ⏎  ⏎ After Kamille stole one from the Titans and it became part of the AEUG's arsenal, it was repainted from black to white. ⏎  ⏎ During the First Neo Zeon War, it was mainly piloted by Elle Vianno, who struggled against brand-new Mobile Suits.

### dic\_robot\_MET\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b004\]
> JP (źródło tłumaczenia): 　アナハイム・エレクトロニクスが開発した、エゥーゴ初の可変モビルスーツ。 ⏎ 　Ｚ計画における変形機構を検証するための機体であるゆえに戦闘能力は低く、機体強度も高くはない。 ⏎ 　アーガマに配備され、レコアやファによって運用された。 ⏎ 　劇場版では２機が登場し、各所で活躍した。
> EN (odniesienie oficjalne, NIE polski): The first transformable Mobile Suit of the AEUG, developed by Anaheim Electronics as part of Project Zeta. ⏎  ⏎ As its main purpose was testing the transformation mechanism, its combat abilities are low, and it is not particularly sturdy. ⏎  ⏎ Assigned to the Argama, it was piloted by Reccoa and later Fa. In the movie version, multiple models were produced, and were active on various battlefields.

### dic\_robot\_GZC\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b006\]
> JP (źródło tłumaczenia): 　アクシズが開発した量産型可変モビルスーツ。 ⏎ 　元々は開発・建造作業用のガザＡ・ガザＢをベースに、攻撃能力を持つ可変モビルスーツとして開発された機体である。モビルアーマー形態では、ナックル・バスターによる砲撃や脚部クローを使った対艦攻撃を行なう。運動性や近接格闘能力は低く、遠距離からの集団砲撃などが基本戦術となっている。一方、生産性は高く、アクシズの工廠で大量生産される。 ⏎ 　アクシズと地球連邦軍が一時手を組んだ時期があったため、アクシズ（ＡＭＸ－００３）と連邦（ＭＭＴ－１）の両軍の認識番号を持つ。 ⏎ 　上記以外の主な武装として、ビーム・ガン、ビーム・サーベルがある。
> EN (odniesienie oficjalne, NIE polski): A mass-production, transformable Mobile Suit developed at Axis. ⏎  ⏎ A transformable Mobile Suit with offensive capabilities, based on the development and construction units Gaza A and Gaza B, respectively. In Mobile Armor form, it conducts anti-ship attacks with its Knuckle Buster cannon and arm claws.  ⏎  ⏎ It has poor maneuverability and close combat capabilities, meaning its primary use is ⏎ group-based bombardments from long distances. However, it is easy to mass produce, and was produced in large numbers at Axis' factory. ⏎  ⏎ Because Axis and the Earth Federation joined forces for a brief period of time, it has two separate IDs: AMX-003 (Axis) and MMT-1 (Federation). ⏎  ⏎ Aside from the weapons listed above, it also has a beam gun and beam saber.

### dic\_robot\_HBRB\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b008\]
> JP (źródło tłumaczenia): 　ティターンズの可変モビルスーツ。 ⏎ 　機体各所のスタビライザーによって高い運動性を持ち、モビルアーマー形態時になるとさらに機動性が向上する。 ⏎ 　変形機構がシンプルなため、戦闘中に臨機応変な対応が可能であり、量産も容易な機体である。 ⏎ 　独自の特殊武装であるショックワイヤー（海ヘビ）による電撃攻撃は強力で、機体のみならずパイロットにもダメージを与える。 ⏎ 　ヤザンの率いる部隊は、３機が連携する事によって高い戦闘能力を発揮した。
> EN (odniesienie oficjalne, NIE polski): One of the Titans' transforming Mobile Suits. Its various stabilizers give it excellent mobility, which can be further improved when it is in Mobile Armor form. ⏎  ⏎ Its simple transformation mechanism means that it can transform mid-battle, and is also easily mass-produced. The Hambrabi has a unique attack known as the Shock Wire (Sea Snake), which delivers strong electrical shocks, damaging both the unit and the pilot inside. Three Hambrabi units in Yazan's squad demonstrated excellent battle capacity.

### dic\_robot\_ZO\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b00a\]
> JP (źródło tłumaczenia): 　シロッコが自らの搭乗する機体として設計・開発したモビルスーツ。 ⏎ 　コクピットに装備された独自開発のバイオセンサーにより高い追従性を誇る事に加え、全身の反動姿勢制御システムやロケットモーターによって最高水準の機動力と運動性能を持つ。 ⏎ 　武装として大型のビーム・ライフルを装備し、腰部のフロントアーマーには白兵戦で絶大な効果を発揮する特殊アーム（隠し腕）が格納されている。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit designed and developed by Scirocco himself for his own personal use. ⏎  ⏎ In addition to boasting advanced interfacing capability thanks to an independently developed Biosensor built into the cockpit, it also possesses top-of-the-line mobility and maneuverability for its size via rocket motors and reaction control systems embedded all throughout the frame. ⏎  ⏎ Its armaments include a massive Beam Rifle along with unique sub-arms (Hidden Arms) built into the armor on the front of the waist that prove extremely effective in close-quarters combat.

### dic\_robot\_NGD\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b00c\]
> JP (źródło tłumaczenia): 　アナハイム・エレクトロニクスがロンド・ベルの要請を受けて開発した、ニュータイプ専用モビルスーツ。パイロットのアムロが自ら設計を担当している。 ⏎ 　歴代ガンダムの性能を分析し、最新技術を導入して開発されたため、急造とは思えないほどの超高性能機として完成している。 ⏎ 　コクピット周辺に組み込まれたサイコ・フレームによって、破格の運動性と追従性を実現している。また、ガンダム系のモビルスーツでは初となるサイコミュ兵器、フィン・ファンネルが使用可能である。これは通常のファンネルよりも大型であり、その分高出力となっている。攻撃としての使用のほか、数基を繋ぎ合わせてＩフィールドを発生させて対ビーム・バリアを形成することもでき、攻守に渡って活用できる。 ⏎ 　ネオ・ジオンによるアクシズ落としを阻止するべく、同じくサイコ・フレームを備えたシャアのサザビーとの決戦に挑み、勝利した。 ⏎ 　その後、アクシズを押し戻そうと奮闘する姿は多くの人間の心を一つにし、その結果、サイコ・フレームによって輝く力場が形成され、アクシズの軌道は変更された。 ⏎ 　そして、その光は後に「アクシズ・ショック」と呼ばれ、多くの人間に影響を与えた。
> EN (odniesienie oficjalne, NIE polski): A Newtype Mobile Suit developed by Anaheim Electronics at the request of the Londo Bell and designed personally by its pilot, Amuro Ray. ⏎  ⏎ Developed using cutting-edge technologies based on analysis of past Gundams, it has such high performance that nobody would guess it was a rush job. ⏎  ⏎ The Psycho-frame integrated around its cockpit gives it exceptional maneuverability and tracking. In addition, it can use Fin Funnels, the first Psycommu weaponry made for a Gundam-type MS. Fin Funnels are larger than standard Funnels and possess superior output. Good for both offense and defense, they can be used both for attacking and to emit I-Fields between multiple units to form anti-beam barriers. ⏎  ⏎ This MS fought and won its battle against Char's Sazabi, an MS similarly equipped with Psycho-frame, during Amuro's efforts to stop the Neo Zeon-led Axis Drop. ⏎  ⏎ After the conclusion of that fight, the sight of this MS struggling to push Axis back unified the hearts of many people, leading to the Psycho-frame forming a glowing force field that altered the trajectory of Axis. ⏎  ⏎ This light phenomenon was later called the Axis Shock, and it deeply affected everyone who witnessed it, both on Earth and in space.

### dic\_robot\_REGZ\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b00e\]
> JP (źródło tłumaczenia): 　アナハイム・エレクトロニクス社が開発した試作モビルスーツ。 ⏎ 　Ｚガンダムの簡易量産試作機であり、バック・ウェポン・システムを装備することでモビルアーマー形態となる。この機構によって高い機体性能を維持しながらも生産性の向上に成功し、量産化を目指した。しかし、それでも他の量産機と比較すれば製造費は高価であり、実戦配備はロンド・ベル隊の１機のみに終わった。 ⏎ 　なお、リ・ガズィは「リファインド・ガンダム・ゼータ」の略称。 ⏎ 　主な武装は、バック・ウェポン・システムの他に、ビーム・サーベル、ビーム・ライフル、２連装グレネード・ランチャー、バルカンなどである。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit developed by Anaheim Electronics. ⏎  ⏎ A simple mass-production prototype, the Re-GZ is a Mobile Armor-type equipped with a Back Weapon System. This offers it increased productivity while allowing it to maintain high performance, but still keeps it within means of being easily mass-produced. Despite this, manufacturing costs are considerably higher than other mass-production types, and Londo Bell only ever deployed one unit in battle. ⏎  ⏎ Re-GZ is an abbreviation of "Refined Gundam Zeta". Its main armaments, other than the Back Weapon System, are the Beam Saber, Beam Rifle, Twin Grenade Launcher, and Vulcan.

### dic\_robot\_REGZ\_BWS\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b010\]
> JP (źródło tłumaczenia): 　リ・ガズィがバック・ウェポン・システムを装備したモビルアーマー形態。 ⏎ 　運動性・長距離巡航能力・火力などが飛躍的に向上している。だが、バック・ウェポン・システムは使い捨てに近い形で使用され、切り離してモビルスーツとなった後の再装備は、戦場では不可能である。 ⏎ 　主な武装は、機首に装備されたメガ・ビーム・キャノン、ミサイル・ランチャーなどである。
> EN (odniesienie oficjalne, NIE polski): A Mobile Armor-type unit equipped with a Back Weapon System. ⏎  ⏎ The Re-GZ (BWS) has dramatically improved mobility, long-distance cruising, and firepower. However, the Back Weapon System is not very hardy. Once removed, the unit reverts to a Mobile Suit and the Back Weapon System cannot be re-equipped in the field. ⏎  ⏎ Its main armaments are the missile launcher and Mega Beam Cannon equipped to its neck.

### dic\_robot\_JEG\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b012`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b012\]
> JP (źródło tłumaczenia): 　地球連邦軍の主力となる量産型モビルスーツ。 ⏎ 　様々な開発・改良がされてきたジム系とネモ系の設計データを統合して開発された機体で、高い性能と信頼性を誇る。ロンド・ベルに優先的に配備されており、以降も長い期間、各方面で運用された。 ⏎ 　なお、連邦軍の主力機としては初めて、軍内部ではなく、アナハイム・エレクトロニクスにて開発・量産された。 ⏎ 　主な武装は、ビーム・ライフル、ビーム・サーベル、バルカン・ポッド・システム、ハンド・グレネードなどである。
> EN (odniesienie oficjalne, NIE polski): A mass production Mobile Suit, the main workhorse of the Earth Federation Forces. ⏎  ⏎ A reliable, high-performance machine developed by integrating design data from across the entire spectrum of GM and Nemo series, and all the developments and improvements to them over the years. The Londo Bell was given priority in receiving them, and they continued to be fielded for a wide variety of uses for many years after. ⏎  ⏎ In a first for a mainline EFF unit, they were developed and mass produced by Anaheim Electronics, rather than by military arsenals. ⏎  ⏎ Its primary armaments include a beam rifle, beam saber, a vulcan pod system, and hand grenades.

### dic\_robot\_LKAI\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b014`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b014\]
> JP (źródło tłumaczenia): 　地球連邦軍外郭新興部隊ロンド・ベルの旗艦。 ⏎ 　艦長はブライト・ノア大佐で、歴代のガンダム搭載艦と同様に、艦の色はホワイトが基調となっている。 ⏎ 　通常の発進用カタパルトの他に、船体後部に着艦専用の甲板を持つのが特徴。また、通常時に使用するブリッジとは別に、防弾性の高い戦闘用ブリッジが存在する。 ⏎ 　基本性能は高く、開発から５０年以上が経過しても同型艦が就役している。 ⏎ 　主砲となる４門の２連装メガ粒子砲の他に、無数のミサイル・ランチャーや対空機銃を装備している。 ⏎ 　決戦前には、カムランから渡された核ミサイル１５発を装備した。
> EN (odniesienie oficjalne, NIE polski): The flagship of the Londo Bell, a unit operating outside Earth Federation Forces jurisdiction. ⏎  ⏎ Captained by Bright Noa, its base color is white, the traditional color of warships loaded with Gundams. ⏎  ⏎ In addition to its standard launch catapults, the aft section of the ship is armored for landings. It also has both a regular bridge and a more durable combat bridge. Its base performance is strong enough that this warship class remained in service for over 50 years after the Ra Cailum's maiden voyage. ⏎  ⏎ It has four sets of twin mega particle cannons as its main weapon, and it is also armed with countless missile launchers and AA autocannons. ⏎  ⏎ Before its decisive battle, it was armed with 15 nuclear missiles provided by Cameron Bloom.

### dic\_robot\_GDOGA\_00\_0

Adres: `dic\_text\_robot/014d369b:97a0b016`

> \[BRAK PL: dic\_text\_robot/014d369b:97a0b016\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍の量産型モビルスーツ。 ⏎ 　これまでのジオン系モビルスーツの集大成とも言える機体であり、各種装備の充実による高い汎用性やシンプルな構造による高い生産性などが特徴で、ネオ・ジオン軍の主力機となっている。 ⏎ 　主な武装は、ビーム・マシンガン、ビーム・ソード・アックス、シュツルム・ファウスト、グレネード・ランチャー、電磁ワイヤーなどである。
> EN (odniesienie oficjalne, NIE polski): A Neo Zeon mass-production Mobile Suit. ⏎  ⏎ Arguably the culmination of all prior Zeon MS technology, this Neo Zeon Forces mainline unit is distinguished by its variety of equipment options and ease of mass production, making it a solid all-rounder. ⏎  ⏎ Its primary armaments include a beam machine gun, beam sword-axe, Sturm Faust, grenade launcher, and electromagnetic wires.

### dic\_robot\_GDOGA\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b000\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍の量産型モビルスーツ。 ⏎ 　小隊長機としてジオン伝統の頭飾りが装備されている。 ⏎ 　レズンの専用機としてブルーのカラーリングを施されているが、性能的には一般兵士用の機体と大差はなく、武装も共通している。
> EN (odniesienie oficjalne, NIE polski): A mass-production type Mobile Suit in the Neo Zeon forces. ⏎  ⏎ As a squad leader unit, its is equipped with the traditional Zeon head ornament. ⏎  ⏎ This is Rezin's personal unit, and it is customized a blue color. There is no great difference between this and a regular unit, and the equipment is also almost the same.

### dic\_robot\_JDOGA\_G\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b002\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍のニュータイプ専用モビルスーツ。 ⏎ 　アナハイム・エレクトロニクス社のグラナダ工場にて開発される。試作機として２機製造され、そのうちの青い機体がギュネイの専用機となった。 ⏎ 　サイコ・フレームを採用し、操縦の追従性や即応性に優れている。 ⏎ 　ビーム・アサルト・ライフル、ビーム・サーベル、シールドに内蔵された４連装メガ粒子砲の他に、６基のファンネルを装備している。 ⏎ 　アクシズ攻防戦では、ロンド・ベル隊の放った核ミサイルを全て撃ち落とす活躍を見せたが、νガンダムに撃墜された。
> EN (odniesienie oficjalne, NIE polski): The Neo Zeon forces' Newtype-exclusive Mobile Suit. ⏎  ⏎ It was developed at Anaheim Electronics' Granada Plant. Two prototype units were made, and the green one became Gyunei's personal unit. ⏎  ⏎ It has a Psycommu frame and has excellent handling and response. Besides the built-in Beam Assault Rifles, Beam Saber, shields, and Quadruple Mega Particle Cannon, it is also equipped with six Funnels. ⏎  ⏎ In the Battle of Axis, it shot down all of Londo Bell's nuclear missiles, but was destroyed by the Nu Gundam.

### dic\_robot\_JDOGA\_Q\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b004\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍のニュータイプ専用モビルスーツ。 ⏎ 　アナハイム・エレクトロニクス社のグラナダ工場にて開発される。試作機として２機製造され、そのうちの赤い機体がクェスの専用機となった。 ⏎ 　サイコ・フレームを採用し、操縦の追従性や即応性に優れている。 ⏎ 　６基のファンネルを始めとする武装の多くはギュネイ機と共通であるが、クェス機はメガ・ガトリング・ガンを装備している。
> EN (odniesienie oficjalne, NIE polski): The Neo Zeon forces' Newtype-exclusive Mobile Suit. ⏎  ⏎ It was developed at Anaheim Electronics' Granada Plant. Two prototype units were made, and the red one became Quess' personal unit.  ⏎  ⏎ It has a Psycommu frame and has excellent handling and response. Its weapons are mostly similar to Gyunei's unit, like the six Funnels, but this has an additional Mega Gatling Gun.

### dic\_robot\_AAZIL\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b006\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍の超大型ニュータイプ専用モビルアーマー。 ⏎ 　エルメスやキュベレイなどのサイコミュ対応機を参考にして開発された機体である。 ⏎ 　主な武装として、メガ粒子砲、２連装バルカン砲、有線サイコミュ式メガ・アーム砲、ファンネルなど。 ⏎ 　対艦戦を想定して設計されており、戦艦に匹敵する火力を備えている。その制御にはサイコミュが使用され、有線のメガ・アーム砲や大型ファンネルによってオールレンジ攻撃も可能。 ⏎ 　また、脚部の巨大なシュツルム・ブースターは使用後に切り離す事も出来る。 ⏎ 　クェスをパイロットに、ネオ・ジオン軍の切り札として地球寒冷化作戦に投入された。
> EN (odniesienie oficjalne, NIE polski): A powerful Newtype Mobile Armor and part of the Neo Zeon forces. ⏎  ⏎ It has been developed with Psycommu-compatible units in mind, like the Qubeley and Elmeth. ⏎  ⏎ Its main armaments are the Mega Particle Cannon, Twin Vulcan Cannon, Wire-Guided Psycommu Mega Arm Cannon, and Funnels. Because it was designed to fight warships, it has an incredible amount of firepower. ⏎  ⏎ It is controlled via Psycommu, and can perform all-range attacks with its Wire-Guided Psycommu Mega Arm Cannon and Funnels. In addition, the large Sturm boosters on its legs may be detached after use.  ⏎  ⏎ With Quess as its pilot, the Alpha Azieru was the Neo Zeon forces' trump card during their Earth Nuclear Winter Plan.

### dic\_robot\_SAZA\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b008\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍のニュータイプ専用モビルスーツ。 ⏎ 　総帥シャア・アズナブルの専用機で、真紅にカラーリングされている。 ⏎ 　サイコ・フレームを採用する事で、従来の機種を遥かに超える追従性を獲得している。また、重装甲でありながら全身のスラスター類によって機動性も高く、シャアが乗るに相応しい強力な機体である。 ⏎ 　主な武装として、ビーム・ショット・ライフル、腹部のメガ粒子砲、ビーム・サーベル、ファンネルなどを装備し、他を圧倒する高火力を誇る。
> EN (odniesienie oficjalne, NIE polski): The Neo Zeon forces' Newtype-exclusive Mobile Suit. ⏎  ⏎ It is Commander Char Aznable's personal unit, and finished with a bright red color. ⏎  ⏎ It is equipped with a Psycommu frame, giving it handling and response that far surpasses previous units. The thrusters on its whole body give it high mobility despite being ⏎ heavily-armored, and it becomes a formidable opponent when Char pilots it. ⏎  ⏎ Its main weapons are the Beam Shot Rifle, Mega Particle Cannon on its midriff, Beam Saber, and Fin Funnels, giving it overwhelming firepower.

### dic\_robot\_REUL\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b00a\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍の旗艦。 ⏎ 　旧ジオン公国軍の旗艦だったグワジン級戦艦の発展型で、推進装置や冷却剤タンク等を継承している。 ⏎ 　本艦の火力やモビルスーツの搭載量は、ネオ・ジオンと地球連邦軍の両軍中でも最大を誇り、第二次ネオ・ジオン抗争では艦隊の主力として戦った。
> EN (odniesienie oficjalne, NIE polski): Flagship of the Neo Zeon forces. ⏎  ⏎ Developed from the Gwazine-class warship of the former Principality of Zeon, it has similar propulsion devices and cooling tanks. ⏎  ⏎ It boasts the greatest firepower and number of Mobile Suits on board among ships of both Neo Zeon and the Earth Federation Forces, and was the main force in the Second Neo Zeon War.

### dic\_robot\_MSKA\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b00c\]
> JP (źródło tłumaczenia): 　ネオ・ジオン軍が建造した軽巡洋艦。 ⏎ 　ムサイ級の発展型であり、放熱フィンなどによりエンジン内部の冷却を可能としており、それにより巡航能力が上がっている。 ⏎ 　第二次ネオ・ジオン抗争の際、主力艦として多数建造され、第三次ネオ・ジオン抗争でも運用された。
> EN (odniesienie oficjalne, NIE polski): A light cruiser built by the Neo Zeon forces. ⏎  ⏎ An improved version of the Musai-class with an improved cruising capability, made possible by heat-radiating fans that increase its ability to cool the internal engine. ⏎  ⏎ Many of these vessels were built as capital ships during the Second Neo Zeon War, and they were used until the Third Neo Zeon War.

### dic\_robot\_MNGD\_F\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b00e\]
> JP (źródło tłumaczenia): 　地球連邦軍の量産型モビルスーツ。 ⏎ 　第二次ネオ・ジオン抗争の長期化を危惧したロンド・ベルがジェガン以上の主力モビルスーツを求めて計画したνガンダムの量産機。 ⏎ 　基本的な武装は、ほぼνガンダムに準拠しており、バックパックにはインコム・ユニット、またはフィン・ファンネルを装備する。 ⏎ 　こちらはフィン・ファンネルを装備した状態。
> EN (odniesienie oficjalne, NIE polski): A mass-produced Mobile Suit of the Earth Federation Forces. ⏎  ⏎ It is the mass production version of the Nu Gundam. Concerned that the Second Neo Zeon War might be prolonged, the Londo Bell foresaw that they required something more powerful to replace their current mainline Mobile Suit, the Jegan. ⏎  ⏎ Its arsenal is mostly the same as that of the Nu Gundam. Its backpack can be mounted with either Fin Funnels or Incom Units, depending on whether the pilot is a Newtype or not. ⏎  ⏎ This version is equipped with Fin Funnels.

### dic\_robot\_MNGD\_I\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b010\]
> JP (źródło tłumaczenia): 　地球連邦軍の量産型モビルスーツ。 ⏎ 　第二次ネオ・ジオン抗争の長期化を危惧したロンド・ベルがジェガン以上の主力モビルスーツを求めて計画したνガンダムの量産機。 ⏎ 　基本的な武装は、ほぼνガンダムに準拠しており、バックパックにはインコム・ユニット、またはフィン・ファンネルを装備する。 ⏎ 　こちらはインコム・ユニットを装備した状態。
> EN (odniesienie oficjalne, NIE polski): A mass-produced Mobile Suit of the Earth Federation Forces. ⏎  ⏎ It is the mass production version of the Nu Gundam. Concerned that the Second Neo Zeon War might be prolonged, the Londo Bell foresaw that they required something more powerful to replace their current mainline Mobile Suit, the Jegan. ⏎  ⏎ Its arsenal is mostly the same as that of the Nu Gundam. Its backpack can be mounted with either Fin Funnels or Incom Units, depending on whether the pilot is a Newtype or not. ⏎  ⏎ This version is equipped with Incom Units.

### dic\_robot\_F100R\_00\_0

Adres: `dic\_text\_robot/014d369b:9820b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9820b012\]
> JP (źródło tłumaczenia): 　百式の改良機である百式改の武装強化プランの１つ。 ⏎ 　ビーム兵器、実弾兵器両方を本体に装備させて火力の向上を図ると同時に胸部のリフレクター・パネルによって防御力も強化されている。 ⏎ 　実際には大型可変モビルスーツが全盛となり、量産されることはなかった。
> EN (odniesienie oficjalne, NIE polski): One of enhanced variants of the Hyaku-Shiki Kai, the improved version of the original ⏎ Hyaku-Shiki. ⏎  ⏎ Its body features various built-in beam and live-ammunition weaponry; furthermore, the addition of reflector panels on its chest increase its defensive abilities. ⏎  ⏎ Due to the trend of developing large transformable Mobile Suits at the time of its development, this Full Armor variant never entered mass production.

### dic\_robot\_GODGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b000\]
> JP (źródło tłumaczenia): 　ネオジャパンが第１３回ガンダムファイト決勝大会用に投入した最新鋭のモビルファイター。 ⏎ 　シャイニングガンダムの全てのデータが移植されており、そのパワーはノーマルモードにおいてもシャイニングガンダムのスーパーモードを遥かに上回る。 ⏎ 　シャイニングガンダムのスーパーモードに当たる形態として、ファイターのドモンの気の高まりに応じてハイパーモードへと変形可能。ハイパーモード発動時には背部のフィールド発生装置が展開し、胸部のエネルギーマルチプライヤーが開放される。 ⏎ 　さらにドモンが明鏡止水の境地に達すると全身が金色に輝き、圧倒的な力を生み出す。 ⏎ 　ドモンの技を完全にトレースし、様々な技を繰り出す。その中でも必殺技の「爆熱ゴッドフィンガー」は絶大な破壊力を誇り、敵モビルファイターを一撃で破壊し、流派東方不敗の最終奥義「石破天驚拳」はデビルガンダムをも葬り去った。
> EN (odniesienie oficjalne, NIE polski): The cutting-edge Mobile Fighter sent by Neo Japan before the final rounds of the 13th Gundam Fight. ⏎  ⏎ Endowed with all of the data of the Shining Gundam, its Normal Mode far surpasses the Shining Gundam's Super Mode. ⏎  ⏎ Like its predecessor, it can activate a powered-up state, the Hyper Mode, when Domon Kasshu's fighting spirit is burning. In this mode, the field generators on its back unfold, and the energy multiplier in its chest opens. ⏎  ⏎ When Domon's mind is clear and serene, reaching the state of Meikyou-Shisui, the Burning Gundam's body glows gold, displaying its overwhelming might. ⏎  ⏎ Tracing Domon's fighting style, it can unleash a variety of techniques. These include the Erupting Burning Finger, which has tremendously devastating power capable of destroying enemy Mobile Fighters in a single blow, and the ultimate technique of the School of Master Asia, the Sekiha Tenkyoken, which was capable of defeating the Dark Gundam.

### dic\_robot\_RSGGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b002\]
> JP (źródło tłumaczenia): 　シャイニングガンダムのプロトタイプとして造られたモビルファイター。 ⏎ 　デビルガンダムとの戦いのためにウルベが用意した。 ⏎ 　ヒートナギナタやビームボウといった武装を持つ。 ⏎ 　基本性能はシャイニングガンダムに匹敵するが、スーパーモードは使用できない。また、シャイニングガンダムからいくつかのパーツがオミットされており、軽量化がなされている。 ⏎ 　肩部装甲を分離させ、左腕パーツと合体させる事でライジングシールドを形成する。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter developed as a prototype for the Shining Gundam. ⏎  ⏎ Major Urube had it prepared for battle against the Dark Gundam. ⏎  ⏎ It is equipped with a Heat Naginata and a Beam Bow. ⏎  ⏎ Its basic performance is comparable to that of the Shining Gundam, but as some components were removed to reduce weight, it cannot activate Super Mode. ⏎  ⏎ The shoulder pads can detach and combine with the left arm to form the Rising Shield.

### dic\_robot\_GDMST\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b004\]
> JP (źródło tłumaczenia): 　第１３回ガンダムファイト用に開発されたネオアメリカのモビルファイター。 ⏎ 　ファイターであるチボデーのボクシング技術をトレースして戦う。 ⏎ 　両肩のアーマーはグラブにもなり、装着すると内蔵されたブースターによってパンチカが大幅に向上する。 ⏎ 　また、全身に装備されたアーマーを外すことで防御力は低下するものの機動性と運動性を向上させられるといった柔軟性も持つ。 ⏎ 　専用銃「ギガンティックマグナム」を装備し、距離を取った戦いにも対応するが、 必殺技である「バーニングパンチ」、さらなる特訓で会得した「豪熱マシンガンパンチ」などにより接近戦でこそ真価を発揮する。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter sent by Neo America for the 13th Gundam Fight. ⏎  ⏎ It fights by tracing Chibodee Crocket's boxing techniques. ⏎  ⏎ Its shoulder pads can also be used as boxing gloves, and its built-in boosters increase the power of its punches. ⏎  ⏎ By shedding its full body armor, it can increase mobility at the expense of defense. ⏎  ⏎ Equipped with custom-made guns, the Gigantic Magnums, it can engage opponents from a distance. However, it is in melee combat that Chibodee can unleash the true might of Gundam Maxter, using the moves he has learned through intense training: the Burning Punch and its upgraded version, the Burning Machine Gun Punch.

### dic\_robot\_DRGGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b006\]
> JP (źródło tłumaczenia): 　第１３回ガンダムファイトにネオチャイナが送り込んだモビルファイター。 ⏎ 　ファイターであるサイ・サイシーの少林寺拳法をトレースし、俊敏かつ意表を突く動きで戦う。 ⏎ 　両腕は伸縮自在のドラゴンクローになっており、ある程度の距離から敵を捕え、超高熱の火炎を噴射する。 ⏎ 　また、背中に背負ったフェイロンフラッグは旗状のビームを発生し、打撃・斬撃・投てき武器として使用できる。 ⏎ 　他にも多彩な技を持つが、その中でも自らの生命を燃やす少林寺最終奥義「真・流星胡蝶剣」は圧倒的な破壊力を持つ。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter sent by Neo China for the 13th Gundam Fight. ⏎  ⏎ Tracing Sai Saici's Shaolin Kung Fu, it fights with agile movements that catch opponents off guard. ⏎  ⏎ Its arms are telescoping Dragon Claws, which allow it to attack its enemies from a distance and douse them in super-hot flames. The Feilong Flags on its back emit a flag-shaped beam and can be used as striking, slashing, and throwing weapons. ⏎  ⏎ It has an array of other techniques; among them is the ultimate Shaolin move, the Shin Ryuusei Kochouken, which consumes the life force of the pilot in a devastating and destructive attack.

### dic\_robot\_GDROS\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b008\]
> JP (źródło tłumaczenia): 　ネオフランスが第１３回ガンダムファイトに送り込んだモビルファイター。 ⏎ 　専用剣「シュバリエサーベル」を装備し、ファイターであるジョルジュの剣術による攻撃を基本戦術とする。 ⏎ 　加えて、マント部に多数格納されている「ローゼスビット」による多方向からの一斉ビーム攻撃やビームネットによる結界、ビットの自爆攻撃等、距離を取っての戦いも得意とする。 ⏎ 　敵を完全包囲する「ローゼススクリーマー」を必殺技とし、さらに強力な技として強烈なエネルギーの流れで敵を討つ「ローゼスハリケーン」を後に会得した。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter sent by Neo France for the 13th Gundam Fight. ⏎  ⏎ Equipped with its custom-made sword, the Chevalier Saber, it traces George's swordsmanship as its primary fighting strategy. ⏎  ⏎ Its cape also conceals numerous Rose Bits, which can execute simultaneous beam attacks from multiple directions, deploy a beam net barrier, and self-destruct to attack; this versatile weapon makes it excel at long-range combat. ⏎  ⏎ Its killer move is the Rose Screamer, which completely surrounds an enemy. Through rigorous training, it later acquired the Rose Hurricane, an even more powerful move that shoots enemies with an intense stream of energy.

### dic\_robot\_BRTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b00a\]
> JP (źródło tłumaczenia): 　ネオロシアが第１３回ガンダムファイトに送り込んだモビルファイター。 ⏎ 　機体の各所に独立駆動機関「ビクトル・エンジン」を搭載しており、圧倒的な出力を誇る。それにより見た目に反する高い機動力を持つ。 ⏎ 　ファイターのアルゴもパワー殺法を好み、圧倒的な質量で相手を粉砕する「グラビトンハンマー」などで戦う。 ⏎ 　後に拳から発するエネルギーを大地に叩きつけ、それによって地形を変形させて相手を攻撃する「炸裂ガイアクラッシャー」を体得し、さらにそのエネルギーを直接相手に叩き込む「零距離ガイアクラッシャー」を身につけた。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter sent by Neo Russia for the 13th Gundam Fight. ⏎  ⏎ Various parts of the unit are equipped with the Victor Engine, an independent drive engine that gives it tremendous power output. As a result, it has a high degree of maneuverability that belies its heavy appearance. ⏎  ⏎ Its pilot, Argo, fights with brute force, using attacks such as the Graviton Hammer, which crushes enemies with overwhelming mass. ⏎  ⏎ Its Bursting Gaia Crusher alters the terrain by pounding the ground with immense energy emitted from its fist, and it later learns how to focus that energy directly on its enemy with the Point-Blank Gaia Crusher.

### dic\_robot\_NBGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b00c\]
> JP (źródło tłumaczenia): 　ネオスウェーデンのモビルファイター。 ⏎ 　ビームリボンやビーム・フープなど華麗な技を持ち、細身のプロポーションからは想像もつかない戦闘力を持つ。 ⏎ 　その最大の特徴は、内蔵された「バーサーカーシステム」にある。この機能を外部から作動することによって搭乗者であるアレンビーの潜在能力を１２０％引き出し、圧倒的な戦闘力を生み出す。しかし、作動中はアレンビーの理性は失われ、外部からのコントロールに支配されてしまう。 ⏎ 　なお、ドモンとのタッグバトルの際には、ゴッドガンダムの必殺技であるゴッドフィンガーを使用した。
> EN (odniesienie oficjalne, NIE polski): The Mobile Fighter of Neo Sweden. ⏎  ⏎ With elegant moves such as the Beam Ribbon and Beam Hoop, its slender frame hides unimaginable combat power. ⏎  ⏎ Its most notable feature is the Berserker System. When activated externally, it draws out 120% of the latent abilities of its pilot, Allenby, giving her devastating combat skills. However, this also causes Allenby to lose her mind in battle, allowing her to be controlled and manipulated externally. ⏎  ⏎ During the tag battle with Domon, it showed that it could use the Burning Gundam's ultimate move, the Burning Finger.

### dic\_robot\_MSTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9860b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9860b00e\]
> JP (źródło tłumaczenia): 　ネオホンコンが第１３回ガンダムファイトに送り込んだ最新鋭モビルファイター。 ⏎ 　第１２回ガンダムファイトで優勝したクーロンガンダムの発展改良型であり、ファイターである東方不敗の流派東方不敗の技で戦う。 ⏎ 　背面の翼は、全身を覆うとマント型へと変形可能。 ⏎ 　東方不敗の技量と合わさり、圧倒的な戦闘力を誇り、第１３回ガンダムファイト決勝大会ではドモンのゴッドガンダムと死闘を演じた。 ⏎ 　必殺技「ダークネスフィンガー」はシャイニングガンダムのシャイニングフィンガーを上回る威力を持ち、流派東方不敗の最終奥義「石破天驚拳」も使用できる。 ⏎ 　ボディにはＤＧ細胞が使用されており、戦闘中でも自己修復が可能である。
> EN (odniesienie oficjalne, NIE polski): The cutting-edge Mobile Fighter sent by Neo Hong Kong for the 13th Gundam Fight. ⏎  ⏎ Developed and improved from the Haow Gundam, champion of the 12th Gundam Fight, it fights with the techniques of the School of Master Asia. ⏎  ⏎ The wings on its back can transform into a cape that protects its entire body. ⏎  ⏎ Combined with Master Asia's skills, it boasts overwhelming combat abilities. It fought to the death against Domon's Burning Gundam in the finals of the 13th Gundam Fight. ⏎  ⏎ Its killer move, the Darkness Finger, far surpasses the Shining Gundam's Shining Finger. It can also perform the School of Master Asia's ultimate technique, the Sekiha Tenkyoken. ⏎  ⏎ As its body is composed of DG cells, it is capable of self-repair even in the midst of battle.

### dic\_robot\_DTAM\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b000\]
> JP (źródło tłumaczenia): 　デビルガンダムの自己増殖能力によって生み出されるモビルスーツ。 ⏎ 　モビルファイターと比較すると個々の戦闘力は高くないが、デビルガンダム軍団の尖兵として大量に戦線に投入される。 ⏎ 　搭乗者はＤＧ細胞によってゾンビ化した人間。 ⏎ 　このデスアーミーを基本形として、デスバーディ、デスネービーなど、様々なバリエーションを持つ。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit created by the self-replication ability of the Dark Gundam. ⏎  ⏎ Its combat capabilities are much lower than those of a Mobile Fighter. However, since it can be easily mass-produced, it constitutes the vanguard of the Dark Gundam's army. ⏎  ⏎ It is controlled by a human pilot, zombified by the DG cells. ⏎  ⏎ The Dark Army is the basic form; many variations exist, such as the Dark Birdy and the Dark Navy.

### dic\_robot\_GMTGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b002\]
> JP (źródło tłumaczenia): 　コロニーと融合したデビルガンダムの体内でデビルガンダム四天王であるマスターガンダム、ガンダムヘブンズソード、グランドガンダム、ウォルターガンダムが再生・合体した姿。 ⏎ 　四天王の全ての能力を有しており、強力な攻撃でシャッフル同盟を苦しめた。
> EN (odniesienie oficjalne, NIE polski): The form in which the Dark Gundam Four Kings (Master Gundam, Raven Gundam, Grand Gundam, and Walter Gundam) regenerated and combined within the Dark Gundam after it fused with a space colony. ⏎  ⏎ Possessing all of the Four Kings' abilities, it torments the Shuffle Alliance with its powerful attacks.

### dic\_robot\_DVGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b004\]
> JP (źródło tłumaczenia): 　ネオジャパンが開発したアルティメットガンダムが変容した姿。 ⏎ 　元々は「自己再生」「自己進化」「自己増殖」の三大理論によって地球環境を再生させるために開発されたが、軍事利用される事を回避するため地上に強引に降下した際、システムに異常をきたし、人類の排除を目的として行動するようになった。 ⏎ 　自己進化によって様々な形態を取るが、この姿は最終形態とも呼べるもの。 ⏎ 　自己増殖によって分身でもあるデスアーミーを大量に生み出し、自らの戦力とする。 ⏎ 　圧倒的なパワーを誇り、高い戦闘力を持つが、真の力を発揮するためには生体ユニットを必要とする。この生体ユニットは新たな生命を生み出す事が出来る女性が最適とされている。
> EN (odniesienie oficjalne, NIE polski): The transformed appearance of the Ultimate Gundam developed by Neo Japan. ⏎  ⏎ It was originally developed based on the "Three Great Principles" of self-regeneration, ⏎ self-evolution, and self-replication to restore Earth's environment. It was forcefully sent to Earth to avoid being used for military purposes, but due to a system anomaly, it began taking actions to eliminate humanity. ⏎  ⏎ Due to its self-evolution, it has taken on many different appearances, but this can be considered its final form. ⏎  ⏎ It can spawn numerous Dark Army units using its self-replication, adding them to its fighting strength. ⏎  ⏎ Boasting overwhelming power and high combat abilities, it requires a bio-unit to draw out its full strength. Due to their natural ability to create life, human females are considered the most suitable bio-units.

### dic\_robot\_WG0\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b006\]
> JP (źródło tłumaczenia): 　ヒイロ・ユイが搭乗するガンダム。 ⏎ 　背部に設置された、鳥の翼のような羽が特徴。ウイングバインダーと呼ばれるこの翼状のパーツは、破格の機動力と運動性能を生み出している。さらに、大気圏突入時の耐熱シールド、バスターライフル発射時の衝撃緩衝材など、多くの機能を有している。 ⏎ 　本機は、単機での拠点制圧を主眼として開発されており、機動力に加えて圧倒的な攻撃力を持ち、主武装のツインバスターライフルは一撃でコロニーを破壊出来る程の威力を持つ。また、高い運動性により、ビームサーベルによる格闘戦においても力を発揮する。 ⏎ 　コックピットには、システムが勝利するために必要な行動をコンソールを通じてパイロットの脳に伝達する「ゼロシステム」が搭載されている。戦闘において、非常に有用なシステムであるが、パイロットへの精神負荷が大きく、暴走を起こす事も多々ある。しかしヒイロは、前大戦の際、このシステムを克服しており、完全に使いこなすまでに至った。 ⏎ 　戦後は太陽に投棄されるはずだったが、マリーメイア軍の反乱鎮圧のために再びヒイロの下に戻り、アルトロンガンダムと大気圏間際で戦闘を行なった。
> EN (odniesienie oficjalne, NIE polski): The Gundam piloted by Heero Yuy. It has characteristic bird-like wings attached to its back—known as the Wing Binder— that boasts extraordinary mobility and maneuverability. They are multifunctional and act as an anti-heat shield when entering the atmosphere, as well as cushioning the recoil from firing the Buster Rifle. ⏎  ⏎ This unit was developed with the main purpose of securing locations alone, so it has overwhelming offensive capabilities in addition to its mobility. Its main weapons are the Twin Buster Rifles, which are powerful enough to destroy a colony with one shot. Its superior mobility also makes it excellent at close combat with the Beam Saber. ⏎  ⏎ The cockpit is equipped with the Zero System, which sends information on how to win through the console directly into the pilot's brain. It is a highly useful system in battle, but causes great mental strain on the pilot which could cause them to lose their minds. However, Heero overcame this system in the previous war, and is able to fully utilize it. ⏎  ⏎ It should have been disposed of in the Sun after the war, but made its way back to Heero's side in order to suppress the Mariemaia Army's rebellion where it battled against the Altron Gundam in the atmosphere.

### dic\_robot\_WG0\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b007`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b007\]
> JP (źródło tłumaczenia): 　その後、マリーメイアが立て篭もる大統領府の核シェルターを破壊するため、半壊状態でツインバスターライフルを連射。シェルターの破壊には成功するものの、自機も反動で大破し、その役目を終えた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In order to break through the Presidential Office's nuclear shelter where Mariemaia had barricaded herself, it fired the Twin Buster Rifle despite being half-destroyed. It succeeded in breaking through but was destroyed in the backlash.

### dic\_robot\_GDH\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b008\]
> JP (źródło tłumaczenia): 　デュオの搭乗するガンダム。 ⏎ 　背後に搭載された、シールドと機体制御を兼ねるアクティブクロークを広げ、携行武装のビームシザースを構えた姿は「死神」をイメージさせる。 ⏎ 　敵機のセンサーを一時的に無効化するハイパージャマーによって高いステルス性能を持ち、敵機を死角から攻撃する戦法を得意とする。 ⏎ 　正面からの戦闘でも、ビームシザースを用いて高い格闘戦能力を誇る。
> EN (odniesienie oficjalne, NIE polski): The Gundam piloted by Duo. It looks like a Grim Reaper with its Active Cloak, for shielding and control, extending from its back and Beam Sabers. ⏎  ⏎ It is a highly stealthy unit, with its Hyper Jammer capable of disabling enemy units' sensors for a short period of time. It excels at attacking from blind spots. ⏎  ⏎ Even in head-on battles, its Beam Scissors are great for close combat.

### dic\_robot\_GDH\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b009`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b009\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱鎮圧後、平和な時代に兵器はいらないとしてデュオ自身の手で廃棄された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After suppressing the Mariemaia Army's rebellion, Duo himself discarded the unit because weapons were not needed in times of peace.

### dic\_robot\_GHA\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b00a\]
> JP (źródło tłumaczenia): 　トロワの搭乗するガンダム。 ⏎ 　単機での拠点制圧、多数の攻撃対象との戦闘をコンセプトに開発されており、全身に大量の火器が搭載されている。 ⏎ 　開発にはバートン財団が関わっており、主武装であるダブルガトリングガンはサーペントも使用している。 ⏎ 　本機は、華麗な運動性で、このガトリングを２丁同時に使いこなし、サーペント部隊を圧倒した。
> EN (odniesienie oficjalne, NIE polski): The Gundam piloted by Trowa, it was developed to handle multiple enemies and secure locations alone, thus is equipped with a massive amount of firearms. ⏎  ⏎ The Barton Foundation was involved in its development, so its primary weapon, the Double Gatling Gun, is also used by the Serpent. ⏎  ⏎ This unit has great mobility, wielding two Gatling Guns at the same time to take out an entire Serpent squadron.

### dic\_robot\_GHA\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98a0b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b00b\]
> JP (źródło tłumaczenia): 　マリーメイア軍の反乱鎮圧後、平和な時代に兵器はいらないとして、トロワ自身の手で廃棄された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After suppressing the Mariemaia Army's rebellion, Trowa himself discarded the unit because weapons were not needed in times of peace.

### dic\_robot\_GSR\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98a0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:98a0b00c\]
> JP (źródło tłumaczenia): 　カトルの搭乗するガンダム。 ⏎ 　大型のヒートショーテルを主武装とするパワーと防御に優れた機体。 ⏎ 　頭部には複数のセンサーが搭載されており、優れた情報収集能力を持つ。これらの情報を基に戦況を分析し、的確な指示を味方機に送る。 ⏎ 　装甲強度は五機のガンダムの中で最高を誇り、さらに強化装甲とアンチビームコーティングが施されたマントを装備する事も出来る。
> EN (odniesienie oficjalne, NIE polski): The Gundam piloted by Quatre, its large Heat Shotel are excellent for offense and defense. ⏎  ⏎ It excels at information gathering with the numerous sensors installed in the head. It analyzes the battle with this information, and issues precise orders to its allies. It boasts the best cape among all 5 Gundams, and can also be equipped with an additional cape and ⏎ anti-beam coating.

### dic\_robot\_GSR\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98e0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b000\]
> JP (źródło tłumaczenia): 　マリーメイア軍の鎮圧後、平和な時代に兵器はいらないとして、カトル自身の手で廃棄された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After suppressing the Mariemaia Army's rebellion, Quatre himself discarded the unit because weapons were not needed in times of peace.

### dic\_robot\_ARG\_EW\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b001`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b001\]
> JP (źródło tłumaczenia): 　五飛の搭乗するガンダム。 ⏎ 　格闘戦に特化した機体で、優れた運動性能を持つ。 ⏎ 　携行武器は、ツインビームトライデントしか持たず、極端なまでに格闘戦に特化されているが、両腕に装備されたドラゴンハングを使う事で中距離の戦闘も可能となる。「双頭龍」の名を体現する、この武器は、自在に伸縮させる事が出来る上に正方形のパーツが連結した多重関節により、フレキシブルな攻撃を繰り出す事が可能である。
> EN (odniesienie oficjalne, NIE polski): The Gundam piloted by Wufei. ⏎  ⏎ It is specialized for close combat and boasts excellent mobility. ⏎  ⏎ It is so specialized that it only carries the Twin Beam Trident, but both arms are equipped with Dragon Fangs that can be used for mid-ranged attacks. ⏎  ⏎ The Altron's name is derived from “two-headed dragon", alluding to the Twin Beam Trident. It is a versatile weapon made of multiple square-shaped parts linked up, and can freely extend and contract.

### dic\_robot\_ARG\_EW\_00\_1

Adres: `dic\_text\_robot/014d369b:98e0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b002\]
> JP (źródło tłumaczenia): 　マリーメイア軍に属し、ヒイロ達の前に立ち塞がったが、反乱鎮圧後、五飛自らの手で廃棄された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It faced off against Heero as part of the Mariemaia Army, but Wufei himself discarded the unit after the rebellion was over.

### dic\_robot\_TRS\_W\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b003`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b003\]
> JP (źródło tłumaczenia): 　リーオーに次ぐ主力機として開発された可変モビルスーツ。 ⏎ 　黄道１２星座の「おうし座」が名前のモチーフになっている。 ⏎ 　宇宙用に開発されたモビルスーツだったが、可変機能を使い分ける事で大気圏内でも高い機動性を維持したままの運用が可能。 ⏎ 　ガンダニュウム合金ですら破壊できるビームカノンも携行でき、全ての面においてリーオー、エアリーズを上回る性能を持つ。 ⏎ 　ホワイトのカラーは、サンクキングダム防衛用に配備されたもので、主にノインが使用し、マリーメイア軍の反乱においてもガンダムと共に戦った。
> EN (odniesienie oficjalne, NIE polski): The transformable Mobile Suit developed following the Leo as the United Earth Sphere Nation's main forces. ⏎  ⏎ Its motif is Taurus from the 12 ecliptic constellations. ⏎  ⏎ It was developed for use in space, but its transformability gives it great mobility in the atmosphere too. It is equipped with the Beam Cannon, powerful enough to pierce through Gundamium alloy, and is superior to the Leo and Aries in all aspects. ⏎  ⏎ This white colored unit was deployed to defend the Sanc Kingdom, and is used mainly by Noin. It also fought alongside the Gundams during the Mariemaia Army's rebellion.

### dic\_robot\_TG3\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b005`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b005\]
> JP (źródło tłumaczenia): 　トレーズ・クシュリナーダの指示によって開発されたトールギスの派生機。 ⏎ 　「高機動・重装甲」というトールギスの極端な性能を維持したまま、更に攻撃力の強化を図った機体である。 ⏎ 　そのコンセプト通り、新たに装備されたメガキャノンはドーバーガンを上回る威力を持ち、最大出力で発射された場合、資源衛星すらも一撃で破壊する。 ⏎ 　また、メガキャノンは砲身の長さによって威力を調節する事が出来るため、戦況に合わせて臨機応変な戦い方が取れるようになっている。 ⏎ 　終戦後はプリベンターの手で管理されていたが、マリーメイア軍の反乱の際にゼクス・マーキスの乗機として運用された。
> EN (odniesienie oficjalne, NIE polski): A derivation of the Tallgeese developed under instructions from Treize Khushrenada. ⏎  ⏎ While having great mobility and heavy armor like the Tallgeese, its attack power has been increased. ⏎  ⏎ It is equipped with the new Mega Cannon which surpasses the Dober Gun in firepower. At its greatest output, the Mega Cannon can destroy a resource satellite in one shot. ⏎  ⏎ In addition, the output can be adjusted according to its length, making it a flexible weapon that can adapt to the conditions of battle. ⏎  ⏎ It fell into the Preventers' administration after the war, but was piloted by Zechs Merquise during the Mariemaia Army's rebellion.

### dic\_robot\_TRS\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b007`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b007\]
> JP (źródło tłumaczenia): 　量産型可変モビルスーツ。 ⏎ 　有人機でもあるが、無人戦闘システム・モビルドールが初めて組み込まれた機体でもある。 ⏎ 　モビルドールシステムが搭載された機体は、一般的なパイロットをしのぐ反応速度と高い機動力を持つ。攻撃目標への射撃も正確である一方、卓越した技量を持つパイロットを相手にする場合には行動パターンを読まれやすいといった弱点も持っている。
> EN (odniesienie oficjalne, NIE polski): A mass-produced transformable Mobile Suit. It can be piloted, but is also the first Mobile Suit to include the Mobile Doll System for unmanned use as well. ⏎  ⏎ Units operated using the Mobile Doll System are capable of outpacing most average pilots with their superb mobility and firing accuracy. However, skilled pilots may find their movement patterns easy to read.

### dic\_robot\_SPNT\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b009`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b009\]
> JP (źródło tłumaczenia): 　マリーメイア軍の主力となる量産型重モビルスーツ。 ⏎ 　ガンダムヘビーアームズの開発に関わったバートン財団の手によって開発された。 ⏎ 　砲撃戦を得意とする機体で、ガンダムヘビーアームズ改と同型のダブルガトリングガンやビームキャノンなど強力な射撃兵器を携行できる。 ⏎ 　また装甲材質もガンダニュウム合金と同程度の硬度を持つとされる新素材、ネオ・チタニュウム合金が採用されており、高い防御力を持つ。 ⏎ 　マリーメイア軍の反乱時には約４００機近くがブリュッセルへと降下し、ガンダムと戦闘した。
> EN (odniesienie oficjalne, NIE polski): The mass-produced Mobile Suit that forms the main force of the Mariemaia Army. ⏎  ⏎ It was developed by the Barton Foundation, which also had a hand in developing the Gundam Heavyarms. It excels at battles of firepower, and is equipped with the same Double Gatling Gun and Beam Cannon as the Gundam Heavyarms Custom. ⏎  ⏎ It has high defensive capabilities as its armor is made of a neo-titanium alloy, a new material as hard as Gundamium alloy. ⏎  ⏎ Roughly 400 units were sent to Brussels during the Mariemaia Army's rebellion where they fought against the Gundams.

### dic\_robot\_DSGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b00b\]
> JP (źródło tłumaczenia): 　地球連合軍との戦いに決着をつけるべく開発された、ザフトの最新鋭モビルスーツ。 ⏎ 　シンの急速な成長に伴い、インパルスガンダムではその才能を活かしきれないと考えたデュランダルの手によって細部に調整が加えられたため、事実上、シンの専用機となっている。 ⏎ 　核動力とデュートリオンビーム送電システムを併用した動力機関「ハイパーデュートリオンエンジン」を装備しており、ウイングパーツから光の翼を発生させて絶大な機動性を発揮する。 ⏎ 　インパルスガンダムの３形態それぞれの長所を併せ持ち、距離を選ばない多彩な武装と抜群の運動性を両立させる事に成功した。さらに掌部ビーム砲やミラージュコロイドを応用した残像現象などの独自の機能も加わり、単機であらゆる戦況に対応するというコンセプトを実現した機体となっている。 ⏎ 　メサイア攻防戦の最中、インフィニットジャスティスとの戦闘で大破し、そのまま月面へと落下して戦線を離脱した。
> EN (odniesienie oficjalne, NIE polski): A cutting-edge suit belonging to ZAFT that was developed to bring victory in the fight with the Earth Alliance. ⏎  ⏎ After Shinn's abilities developed so rapidly, Dullindal felt that the Impulse Gundam was holding him back, so he started to make adjustments to his current Gundam, resulting in a totally new mobile suit exclusively for Shinn. ⏎  ⏎ The Destiny Gundam is powered by a hyper Deuterion engine, which uses nuclear energy and a Deuterion beam system, producing wings of light and granting the mobile suit tremendous maneuverability. ⏎  ⏎ It combines the strengths of the three Impulse Gundam forms and has outstanding mobility with a wide range of weapons that can be used for attacks of any range. Furthermore, it boasts some unique features, such as a palm beam cannon and the ability to create ⏎ after-images with its Mirage Colloid systems. Its frame allows it to participate in any battle as a single unit. ⏎  ⏎ During the Messiah assault, Destiny Gundam is badly damaged in the battle with Infinite Justice, it falls to the surface of the moon, retreating from the front lines.

### dic\_robot\_FIGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00d`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b00d\]
> JP (źródło tłumaczenia): 　ザフトの新世代高性能機「セカンドステージシリーズ」のインパルスガンダムが、フォースシルエットを装着した状態。 ⏎ 　インパルスガンダムの特徴として、母艦からの遠隔エネルギー供給が可能な「デュートリオンビーム送電システム」、コクピットが小型戦闘機へ変形する「コアスプレンダー機構」、３種の兵装ユニットを戦況に応じて使い分ける「シルエットシステム」を有していることが挙げられる。 ⏎ 　インパルスガンダム３形態の中では特に機動性に優れ、大気圏内でも単独飛行が可能なため、最も多く使用された。 ⏎ 　シンがデスティニーガンダムに乗り換えてからは、乗機を失っていたルナマリアが引き継いだ。
> EN (odniesienie oficjalne, NIE polski): The Impulse Gundam, part of ZAFT's Second Stage series of new high-performance machines, equipped with the Force Silhouette. ⏎  ⏎ The Impulse Gundam's main features are its deuterion beam energy supply system, which allows it to be supplied by a distant energy beam from a carrier; its Core Splendor mechanism, which transforms the cockpit into a small fighter craft; and its Silhouette system, which uses three types of armaments depending on the tactical situation. ⏎  ⏎ Of the Impulse Gundam's three forms, this one was the most frequently used, excelling in mobility and capable of unassisted atmospheric flight. ⏎  ⏎ After Shinn moved to piloting the Destiny Gundam, Lunamaria, who no longer had her own Mobile Suit, began using this one.

### dic\_robot\_SFRGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b00f\]
> JP (źródło tłumaczenia): 　反デュランダル勢力であるクライン派の拠点「ファクトリー」で、インフィニットジャスティスと共に開発された最新鋭モビルスーツ。 ⏎ 　新型のレーザー核融合エンジンを搭載しており、フリーダムの数倍の出力を誇る。 ⏎ 　新たに装備された「スーパードラグーン（機動兵装システム）」は、機動力を向上させるウイング部分を分離させ、無線誘導型のビーム兵器として使用できる装備。初出撃の際にはこの新兵器を使用して、たった２分で計２５機のザクウォーリアとグフイグナイテッドを戦闘不能にさせた。 ⏎ 　装甲もＶＰＳ装甲に変更され、ビームシールドまでも内蔵しているため、攻守に渡り隙の見つからない機体となっている。 ⏎ 　ただし、その力を発揮するためには高い操縦技術を必要とし、キラ以外のパイロットでは運用は難しいとされる。
> EN (odniesienie oficjalne, NIE polski): A cutting-edge mobile suit developed alongside the Infinite Justice Gundam at the Clyne faction stronghold, Factory, which serves as a base for those working against Dullindal. ⏎  ⏎ It is equipped with the new laser fusion engine, boasting an output many times greater than the previous Freedom. ⏎  ⏎ The newly-equipped Super DRAGOONs (mobile weapon system) allows the wing parts to separate, leading to increased mobility, and can also be used as a wireless-guided beam weapon. Thanks to this, the Strike Freedom Gundam managed to take down twenty five ZAKU Warriors and GOUF Igniteds in just two minutes during its first sortie using the new weapon. ⏎  ⏎ Because it now uses VPS armor and has a built-in beam shield, this suit has impenetrable offense and defense. ⏎  ⏎ However, to fully utilize the suit's potential, its pilot must be exceptionally talented, and the only pilot who can truly use it is Kira.

### dic\_robot\_INFGD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b011`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b011\]
> JP (źródło tłumaczenia): 　反デュランダル勢力であるクライン派の拠点「ファクトリー」で、ストライクフリーダムガンダムと共に開発された最新鋭モビルスーツ。 ⏎ 　アスランが前大戦時に搭乗していたジャスティスガンダムの発展型であり、ザフトの「セカンドステージシリーズ」の技術も流用されている。シルバーのフレームにレーザー核融合エンジンを搭載し、最大の特徴であったスラスター兼兵装ユニット「ファトゥム‐０１」も大幅な強化・改良が施されている。 ⏎ 　最終決戦では、デスティニーを撃破し、さらにはレクイエムを破壊し、戦局を決定づけた。
> EN (odniesienie oficjalne, NIE polski): A cutting-edge mobile suit developed alongside the Strike Freedom Gundam at the Clyne faction stronghold, known as the Factory, which serves as a base for those working against Dullindal. ⏎  ⏎ It is a developed form of the Justice Gundam piloted by Athrun in the previous war, and appropriates ZAFT's second stage series' technology. The silver frame is equipped with a laser fusion engine, and its greatest feature, the thruster unit "Phantom 01", has undergone significant strengthening and improvements. ⏎  ⏎ In the final battle, it defeats the Destiny and Requiem, bringing an end to the war.

### dic\_robot\_ETNL\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b013`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b013\]
> JP (źródło tłumaczenia): 　ザフトが前大戦で開発したフリーダムガンダムとジャスティスガンダムの専用運用艦。その後継機であるストライクフリーダムガンダムとインフィニットジャスティスガンダムの母艦としても運用された。 ⏎ 　クライン派のシンボルであるラクスや艦長のバルトフェルド、ダコスタやメイリンといった元ザフトのクルーが多数乗り込んでいる。 ⏎ 　アークエンジェルと比較すると火力では劣るものの、ザフトの高速艦ナスカ級を容易に振り切るほどの速力を持つ。 ⏎ 　また、ストライクフリーダムとインフィニットジャスティスの兵装ユニット「ミーティア」を艦首に装備しており、両機が使用する際には切り離されるが、普段は砲台として使用している。
> EN (odniesienie oficjalne, NIE polski): Developed by ZAFT in the previous great war, the Eternal is a dedicated operational ship for the Freedom Gundam and Justice Gundam. Later, it serves as a carrier for its successors, the Strike Freedom Gundam and Infinite Justice Gundam. ⏎  ⏎ Many of the original ZAFT crew work aboard, for example, the famous members of the Clyne Faction, Lacus and Captain Waltfeld, as well as DaCosta and Meyrin. ⏎  ⏎ Although it has less firepower than the Archangel, the Eternal has so much speed that it easily runs rings around the ZAFT's high-speed Nazca class. ⏎  ⏎ Furthermore, its bow is also equipped with the heavily armed Meteor units of the Strike Freedom and Infinite Justice. These disconnect when used by either unit, but normally they are used as turrets.

### dic\_robot\_UGRD\_00\_0

Adres: `dic\_text\_robot/014d369b:98e0b015`

> \[BRAK PL: dic\_text\_robot/014d369b:98e0b015\]
> JP (źródło tłumaczenia): 　地球連合軍が開発した量産型巨大モビルアーマー。 ⏎ 　ザムザザーやゲルズゲーのような特異な外観は持たないが、大型ビーム砲と陽電子リフレクターによって攻守のバランスが良く、機動性も上々である。ただし近接戦闘用の武装を全く持ち合わせていないため、接近戦には弱い。
> EN (odniesienie oficjalne, NIE polski): A mass-production type, giant mobile armor developed by the Earth Alliance. ⏎  ⏎ It doesn't have a unique appearance like the Zamza-Zah or Gells-Ghe, but it offers a good balance between offense and defense with its massive beam cannon and Positron reflector, and also has improved mobility. However, it is not armed for melee combat and so is unsuited for close-range combat.

### dic\_robot\_ZMZZR\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b000\]
> JP (źródło tłumaczenia): 　地球連合軍が開発した試作型モビルアーマー。 ⏎ 　巨体ながらも高い機動力を持ち、クローやビーム砲により距離を問わない戦い方が可能。さらに機体前面にはミネルバのタンホイザーをも防ぐ陽電子リフレクターを展開する。 ⏎ 　その性能を活かすため、機長・操舵手・砲手と３人のパイロットを必要とする。
> EN (odniesienie oficjalne, NIE polski): A prototype Mobile Armor developed by the Earth Alliance. It is quite mobile despite its large size and can fight both long and close-range battles thanks to its claws and beam cannons. ⏎  ⏎ Furthermore, it can deploy a positron reflector—capable of deflecting even the Minerva's Tannhäusers—in front of itself. It requires a team of three to make use of all these functions: a captain, a pilot, and a gunner.

### dic\_robot\_GDARRAL\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b002\]
> JP (źródło tłumaczenia): 　スレッタが水星からアスティカシア高等専門学園に持ち込んだモビルスーツ。 ⏎ 　水星に本社を持つシン・セー開発公社で開発された。 ⏎ 　パーメットを利用した身体機能拡張技術であるGUNDを軍事転用した「GUNDフォーマット」を搭載している。しかし、搭載機の特徴として見られる、パイロットの身体に負荷を強いるデータストームは検出されていない。 ⏎ 　１１基のガンビットで構成された次世代群体遠隔操作兵器システム「ガンビット」を装備しており、ビットを機動砲台として操るだけでなく、補助推進システムやシールドとして運用する等、攻防に使用する。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit Suletta brought to Asticassia School of Technology from Mercury. Developed by the Mercury-based Shin Sei Development Corporation. ⏎  ⏎ It's equipped with the GUND Format, a system which uses GUND (a body-enhancement technology utilizing Permet) for military applications. However, uniquely, it does not exhibit the technology's signature data storms, which put massive physical strain on the pilot. ⏎  ⏎ It carries a shield made up of eleven GUND-Bits, a next-generation remote-controlled swarm weapon system. These Bits can be used not just as remote turrets, but also as an auxiliary propulsion system, a shield, and so on.　

### dic\_robot\_GDARRAL\_00\_1

Adres: `dic\_text\_robot/014d369b:9920b003`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b003\]
> JP (źródło tłumaczenia): 　その機能から「GUND-ARM」であるとの嫌疑が掛けられたものの、データストームが検出されない理由については明らかになっていない。 ⏎ 　真偽は不明瞭であったが、後にシン・セー開発公社ＣＥＯのプロスペラによって「GUND-ARM」である事が明かされた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ While those functions garnered suspicion of it being a GUND-ARM, it is still unclear why no data storms are detected from it. ⏎  ⏎ Though the truth was formerly obscured, it was later revealed to be a GUND-ARM by Shin Sei Development Corporation CEO Prospera.

### dic\_robot\_GDARRALRB\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b004\]
> JP (źródło tłumaczenia): 　シン・セー開発公社により改修されたガンダム・エアリアル。 ⏎ 　「GUND-ARM」の基本構造を引き継ぎつつ、グラスレー寮との「決闘」によるダメージを修理した際、外部装甲や装備類が刷新された。 ⏎ 　新たに追加となったフライトユニットに回転式展開翼を採用した事で運動性と旋回能力が大幅に向上している。 ⏎ 　また、ガンビットライフルを新たに装備し、ライフルの銃身に各ガンビットを接続する事で対艦級の火力を持たせることができる。
> EN (odniesienie oficjalne, NIE polski): Gundam Aerial after it was improved by Shin Sei Development Corporation. ⏎  ⏎ Inheriting the basic structure of a GUND-ARM, its external armor and equipment were renovated after the unit was repaired from the damage it took in a team duel with Grassley House. ⏎  ⏎ Its maneuverability and turning capabilities were greatly enhanced thanks to its new Flight Unit that utilized deployable rotating wings. ⏎  ⏎ Furthermore, it is now equipped with a GUND-Bit Rifle, which gives its Beam Rifle anti-warship firepower by linking Bits to the rifle's barrel.

### dic\_robot\_DMTRNR\_CC\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b006\]
> JP (źródło tłumaczenia): 　ニカがカスタマイズした、チュチュ専用のデミトレーナー。 ⏎ 　旧型のデミトレーナーをベースにしており、性能差を埋めるために独自の改良が施されている。 ⏎ 　大型ビームライフルによる一撃離脱戦法を想定し、急な加減速が出来るように脚部側面のブースター基部が可動式となっている。また、脚部底に車輪を取り付けたウィルダッシュ機構によって地面の滑走も可能。
> EN (odniesienie oficjalne, NIE polski): A Demi Trainer customized by Nika for Chuchu's use. ⏎  ⏎ Based off an older-model Demi Trainer, it's been given unique enhancements in order to put it on par with more advanced units. ⏎  ⏎ Designed for hit-and-run tactics with its Large Beam Rifle, its legs feature rapid acceleration and deceleration boosters that allow it to swivel rapidly. Furthermore, it has wheels in its feet that allow it to drift-slide along the ground at high speeds.

### dic\_robot\_DLNZA\_GEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b008\]
> JP (źródło tłumaczenia): 　ジェターク社の汎用モビルスーツ・ディランザをグエル用にチューニングした機体。 ⏎ 　高いパワーと堅牢な装甲を持っており、重量の増加による機動性の低下は推進機構の強化によって補っている。 ⏎ 　機体色は人目を引くマゼンタで、華美な装飾も施されている。 ⏎ 　ビーム刃を出力する長尺の槍・ビームパルチザンを主武装とする。また、両肩部のシールドには打突に効果的なスパイクが取り付けられている。
> EN (odniesienie oficjalne, NIE polski): A version of the Dilanza—an all-purpose Mobile Suit developed by Jeturk Heavy Machinery—tuned for Guel's use. ⏎  ⏎ Powerful and possessing solid armor, it also comes with enhanced propellers to compensate for the loss of mobility brought on by the increased weight. ⏎  ⏎ The MS has an eye-catching magenta color scheme and is splendidly (a few might say excessively) decorated. ⏎  ⏎ Excelling in close-quarters combat, its main weapon is a Beam Partizan—a long lance that can deploy a beam blade. Furthermore, the shields on its shoulders come with spikes that are effective in charges.

### dic\_robot\_DRLBLDE\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b00a\]
> JP (źródło tłumaczenia): 　ジェターク社が開発した第５世代実証機。 ⏎ 　意思拡張ＡＩを搭載しており、パイロットの操縦なしで自律行動が可能。 ⏎ 　ドローン技術を用いた攻撃ユニット「イーシュヴァラ」と両肩部に装備された大型シールド形状の防御ユニット「アンビカー」を駆使した戦闘を行う。 ⏎ 　また手持ちの武装として、錨形状のビームアンカーと爪形状のビームクナイを連結させた近接用兵器・ビームジャベリンを装備する。
> EN (odniesienie oficjalne, NIE polski): A fifth-generation demonstration machine developed by Jeturk Heavy Machinery. ⏎  ⏎ Equipped with a Decision Making Extension AI that can pilot the mech by itself without requiring input from a pilot. ⏎  ⏎ The unit fights using Isvara attack units that utilize drone technology, and Ambika defensive units shaped like giant shields on its shoulders. ⏎  ⏎ It's also equipped with a Beam Javelin for close-range combat, made by attaching a Beam Anchor (shaped, unsurprisingly, like a ship anchor) and a claw-shaped Beam Kunai.

### dic\_robot\_GDPHARCT\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b00c\]
> JP (źródło tłumaczenia): 　ペイル社が開発したGUNDフォーマット搭載機「GUND-ARM」。 ⏎ 　GUNDフォーマットによって高次元の慣性制御を誇る反面、搭乗したパイロットの身体には強い負荷が伴う。 ⏎ 　背部と両肩部には高機動戦術のための大推力のブラストブースターが装備されている。また、スタン効果付きの電磁ビームを発生させるガンビットを両肩部に格納する。 ⏎ 　主兵装のライフル「ビームアルケビュース」は、GUNDフォーマットの知覚リンクによって超高精度の狙撃が可能。 ⏎ 　機体の開発には、元ヴァナディース機関の研究員・ベルメリアが関与している。
> EN (odniesienie oficjalne, NIE polski): A GUND-ARM, a machine that utilizes a GUND Format, developed by Peil Technologies. ⏎  ⏎ Though the GUND Format grants it high-order inertial control, its data storms also place its pilot under severe physical strain. ⏎  ⏎ Equipped with powerful Blast Boosters on its back and shoulders, making it suited for high-mobility tactics. Furthermore, its shoulders house GUND-Bits capable of generating mech-stunning electromagnetic beams. ⏎  ⏎ Its main armament—a rifle known as a Beam Arquebus—utilizes a GUND Format sensory link that can provide significant sniping accuracy. This unit was developed by Belmeria, a former Vanadis Institute researcher.

### dic\_robot\_MCAELS\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b00e\]
> JP (źródło tłumaczenia): 　グラスレー社が開発した最新鋭モビルスーツ。 ⏎ 　GUNDフォーマット妨害装置「アンチドート」を搭載する。 ⏎ 　右腕には、戦術複合装備であるビームブレイサーを採用しており、アンチドートの他ビームサーベルやビームキャノン等の主要兵装が集約されている。 ⏎ 　ビームブレイサーは、各種モードへの変形機能を持つ他、腕から分離させる事で有線式の遠隔攻撃にも使用が可能。
> EN (odniesienie oficjalne, NIE polski): A state-of-the-art Mobile Suit developed by Grassley Defense Systems. ⏎  ⏎ It's equipped with an Antidote system, which can jam the GUND Format. ⏎  ⏎ Its right arm is equipped with a tactical combination device called a Beam Bracer, and aside from the Antidote, its main armaments are its Beam Saber and Beam Cannon. ⏎  ⏎ The Beam Bracer can not only transform into different modes, but also detach from the arm and remotely launch attacks via wire control.

### dic\_robot\_BGRPNT\_00\_0

Adres: `dic\_text\_robot/014d369b:9920b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9920b010\]
> JP (źródło tłumaczenia): 　ヴァナディース事変で投入されたグラスレー社製モビルスーツ・ベギルベウの後継機。 ⏎ 　対「GUND-ARM」戦を想定した機体であり、大型シールドにGUNDフォーマット妨害装置「アンチドート」を搭載している。 ⏎ 　ビームライフルには、大型エネルギータンクが備えられている他、命中精度の向上のためにツインセンサー方式を採用。 ⏎ 　地球寮との「決闘」に際し、運用実証実験を兼ねてグラスレー寮に５機が配備された。
> EN (odniesienie oficjalne, NIE polski): The successor to the Beguir-Beu—the Mobile Suit employed during the Vanadis Incident—developed by Grassley Defense Systems. ⏎  ⏎ Designed with anti-GUND-ARM combat in mind, they have Antidotes, counter-GUND Format jammers, built into their giant shields. ⏎  ⏎ Their main armament, a Beam Rifle, comes equipped with a large energy tank and incorporates twin sensor systems to improve accuracy. ⏎  ⏎ Five units are assigned to Sabina and other pilots from Grassley House to be field tested in their team duel with Earth House.

### dic\_robot\_DNBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b000\]
> JP (źródło tłumaczenia): 　ショットの開発した試作型オーラ・バトラー。 ⏎ 　全部で３機が製造されており、パープルの塗装が施された本機はショウが搭乗する機体である。 ⏎ 　搭乗者のオーラ力によって性能が大きく左右されるという特徴を持っており、コモン人などのオーラ力の低い者からは扱いが難しい機体とされている。 ⏎ 　反面、オーラ力の高い者が搭乗すれば、その性能を最大限に発揮することができ、ショウが搭乗した本機は、そのオーラ力も相まって多大な戦果を挙げた。 ⏎ 　ショウがビルバインに乗り換えた後は、マーベルの搭乗機として使用され、初期型のオーラ・バトラーでありながら、終戦まで現役で活躍し続けた。
> EN (odniesienie oficjalne, NIE polski): A prototype Aura Battler developed by Shot. ⏎  ⏎ Three units were constructed, and this one, colored purple, is the one Show pilots. ⏎  ⏎ It's somewhat unique in that its performance depends greatly on its pilot's Aura Power, meaning Commoners and others with low Aura Power have difficulty using it. ⏎  ⏎ On the other hand, a pilot with high Aura Power can use it to its full potential. Show's Aura Power allowed him to use this one to great effect during the war. ⏎  ⏎ After Show switches to the Billbine, it becomes Marvel's unit and serves to the end of the war despite being an early model.

### dic\_robot\_BLBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b002\]
> JP (źródło tłumaczenia): 　ナの国が開発した最新鋭の可変オーラ・バトラー。 ⏎ 　ウイング・キャリバーへの変形機構を持ち、これまでの機種には見られない迅速な戦場への到達、ならびに離脱が可能である。 ⏎ 　また機動性だけでなく火力面の向上も図られており、内蔵火器としてオーラ・キャノン２門が搭載された他、新機軸の武装であるオーラ・ソード・ライフルも携行可能となっている。これはオーラ・ショットとしてだけでなく、オーラ力をそのままソードにするオーラ・ビーム・ソードとしても使用することができ、遠近両面に対応した火力の強化が行われている。 ⏎ 　乗りこなすには高いオーラ力が必要とされるが、対価に見合うだけの高いポテンシャルを持った機体である。 ⏎ 　本機はナの国の女王シーラから真の聖戦士と認められたショウへと託される。搭乗者であるショウの高いオーラ力も相まって、終戦まで反ドレイク勢力の中核を担い続けた。
> EN (odniesienie oficjalne, NIE polski): The latest model of transforming Aura Battler developed by the Land of Na. ⏎  ⏎ It can transform into a Wing Caliver form, allowing it to join battle at unprecedented speeds, as well as to disengage at will. ⏎  ⏎ It's designed for impressive firepower in addition to its mobility, mounting two integrated Aura Cannons and being equipped with the innovative new Aura Sword Rifle. The weapon can fire the standard Aura Shots as well as form an Aura Beam Sword by projecting Aura Power into a blade form, allowing it to fight effectively at any range. ⏎  ⏎ It requires exceptional Aura Power to pilot, but the potential effectiveness makes it more than worth it. ⏎  ⏎ This unit was provided to Show by Queen Ciela of the Land of Na in recognition of his status as a true Battler. It made great use of Show's considerable Aura Power to form the core of the anti-Drake forces' strategy until the end of the war.

### dic\_robot\_GRNGLAN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b004\]
> JP (źródło tłumaczenia): 　ナの国が開発したオーラ・バトル・シップ。 ⏎ 　三方に広がるブロックと城のようにそびえるブリッジで構成されている。 ⏎ 　他のオーラ・バトル・シップに比べて機動力は低いものの、各ブロックに砲座を備えており、立体的な砲撃が可能。 ⏎ 　多数のオーラ・バトラーを搭載しており、対ドレイク軍との戦闘においてはラウの国のゴラオンと共に旗艦として大きな役割を担った。
> EN (odniesienie oficjalne, NIE polski): An Aura Battleship developed by the Land of Na. ⏎  ⏎ It's formed of three blocks extending in different directions around a bridge designed like a castle. ⏎  ⏎ It's slower than other Aura Battleships, but the turrets on each block allow it to lay down fire in all directions. ⏎  ⏎ It can board a host of Aura Battlers and served as a flagship of the anti-Drake forces alongside the Land of Rau's Goraon.

### dic\_robot\_DRMR\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b006\]
> JP (źródło tłumaczenia): 　ショットがドレイクの命を受けて開発した、初の量産型オーラ・バトラー。 ⏎ 　同時期に開発されたダンバインと比較して、装甲が厚く、内蔵式の火器が採用されている。 ⏎ 　必要オーラ力が低く、操作方法も他オーラ・バトラーに比べて比較的簡便であり、一般兵士にも扱いやすい機体として仕上がっている。 ⏎ 　その完成度の高さから、改良は重ねられつつも戦争終盤までドレイク軍の主力として使用され続けた。
> EN (odniesienie oficjalne, NIE polski): The first mass-production Aura Battler designed by Shot under Drake's orders. ⏎  ⏎ Compared to its contemporary, the Dunbine, it has thicker armor and integrated weaponry. ⏎  ⏎ It requires little Aura Power and has simpler controls than other Aura Battlers, making it well suited to be used by rank and file soldiers. ⏎  ⏎ Its high quality allowed it to remain, with incremental upgrades, the main unit of the Drake Army until the very end of the war.

### dic\_robot\_BARS\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b008\]
> JP (źródło tłumaczenia): 　クの国が開発したオーラ・バトラー。 ⏎ 　一般兵士の使用を前提に設計されたオーラ・バトラーの発展機であり、コモンでも扱いやすい機体として仕上がっている。 ⏎ 　トータルバランスも高いレベルでまとまっており、後にドレイク軍でも量産型オーラ・バトラーとして採用された。 ⏎ 　内蔵火器はオーラバルカンのみだが、特徴的な鎌状のブレードは中近距離用の投擲武器としても使用することができる。
> EN (odniesienie oficjalne, NIE polski): An Aura Battler developed by the Kingdom of Ku. ⏎  ⏎ It was developed for any soldier to be able to pilot, resulting in a machine even a Commoner could control. ⏎  ⏎ It's highly balanced across the board and would see use as a mass-production unit in the Drake Army later on. ⏎  ⏎ Its only integrated weapons are Aura Vulcans, but its distinctive sickle-shaped blade can be thrown at mid-range.

### dic\_robot\_RPRKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b00a\]
> JP (źródło tłumaczenia): 　ショットが開発したオーラ・バトラー。 ⏎ 　全身に火器を内蔵した新機軸の機体であり、ある程度の数が量産されたが、装甲等の点においてバランスが悪いという欠点を持ち、主力機とはならなかった。 ⏎ 　ジェリルが搭乗し、ハイパー化をした初の機体である。
> EN (odniesienie oficjalne, NIE polski): An Aura Battler developed by Shot. ⏎  ⏎ It's designed around a new concept that mounts integrated weapons all over its body, and some were mass-produced. However, its lack of balance, particularly in its poor armor, proved to be a problem, and it never saw broad adoption. ⏎ It has the distinction of being the first machine to go Hyper, while piloted by Jeril.

### dic\_robot\_GLABA\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b00c\]
> JP (źródło tłumaczenia): 　黒騎士が搭乗するオーラ・ファイター。 ⏎ 　オーラ・バトラーとウイング・キャリバー両方のコンセプトを取り入れて造られており、高い機動力と火力に加えて格闘戦も可能であり、既存のオーラマシンを上回る優れた戦闘能力を持つ。 ⏎ 　オーラ・コンバーターは一般的なオーラ・バトラーの数倍の大きさがあり、そこから生み出されるスピードにより一撃離脱戦法を得意とする。 ⏎ 　量産されたものの、使いこなせるパイロットは黒騎士ぐらいであった。 ⏎ 　ショウとの戦いの中、黒騎士の怨念によりハイパー化したが、自らの生命を犠牲にしたエレによって阻止された。
> EN (odniesienie oficjalne, NIE polski): The Aura Fighter piloted by the Black Knight. ⏎  ⏎ It was developed using concepts from both Aura Battlers and Wing Calivers, giving it impressive mobility and firepower that puts other Aura Machines to shame. ⏎  ⏎ Its Aura Converter is several times larger than that of a normal Aura Battler, and with the speed boost the converter provides, it specializes in hit-and-run attacks. ⏎  ⏎ Although it was technically mass-produced, only the Black Knight proved capable of piloting it. ⏎  ⏎ The Black Knight's grudge against Show caused it to go Hyper; Elle was able to stop the phenomenon at the cost of her life.

### dic\_robot\_WLWPS\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b00e\]
> JP (źródło tłumaczenia): 　ドレイク軍のオーラ・バトル・シップ。 ⏎ 　高い火力と防御力、膨大なオーラマシンの積載量など、全てが高水準であり、オーラ・シップとしての総合的な性能は最強と言われる。 ⏎ 　ウィル・ウィプスの登場によって戦いは大規模化し、結果としてバイストン・ウェルからオーラマシンが排除される事となった。 ⏎ 
> EN (odniesienie oficjalne, NIE polski): An Aura Battleship fielded by the Drake Army. ⏎  ⏎ It has high capabilities in multiple directions, boasting great firepower, armor, and Aura Machine capacity. Some say it is, overall, the strongest Aura Ship in existence. ⏎  ⏎ The Will-Wips' appearance escalated the war, ultimately leading to Aura Machines disappearing from Byston Well entirely.

### dic\_robot\_SRBIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b010\]
> JP (źródło tłumaczenia): 　バランバランの聖地に眠っていたオーラ・バトラー。 ⏎ 　ジャコバ・アオンによってオーラマシンが地上に送られた後もバイストン・ウェルに残されていた数少ないオーラ・バトラーのうちの一つ。 ⏎ 　他のオーラ・バトラーとは異なる設計思想で開発されており、コックピットにはモニター類が一切配置されていない。代わりに専用の兜が設置されており、搭乗者はこれを装着し、オーラ力による「心眼」でターゲットを感じるようになっている。 ⏎ 　バランバランの民によって７００年の間守られ続けてきたが、ショウ・ザマの転生体であるシオン・ザバが乗り込んだことで起動し、黒騎士ラバーンの駆るズワウスと激戦を繰り広げることとなる。 ⏎ 　武装は剣を持つのみだが、シオンとシルキーが乗り込むことで強力なバリアを発生させることが出来る。その力は強大であり、最終決戦では核ミサイルの爆発からシオン、シルキー、レムルを守り切る程であった。
> EN (odniesienie oficjalne, NIE polski): An Aura Battler slumbering in the holy grounds of Baran-Baran. ⏎  ⏎ It's one of very few Aura Machines remaining in Byston Well after Jacoba Aon sent most of them to Upper Earth. ⏎  ⏎ It's built on an entirely different concept to most Aura Machines, with no monitors mounted in its cockpit. Instead, it's equipped with a special helmet that allows its wearer to sense their target through an Aura Power-based clairvoyance. ⏎  ⏎ The people of Baran-Baran kept watch over it for 700 years. That ended when Shion Zaba, the reincarnation of Show Zama, activated and piloted it in a series of fierce battles with the Black Knight Rabaan's Zwauth. ⏎  ⏎ Its only weapon is a sword, but when Shion and Silky are on board, it can project a powerful barrier. The barrier is potent enough to have protected Shion, Silky, and Remul from the blast of a nuclear missile in its final battle.

### dic\_robot\_VRVN\_00\_0

Adres: `dic\_text\_robot/014d369b:9960b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9960b012\]
> JP (źródło tłumaczenia): 　全てが謎に包まれたオーラ・バトラー。 ⏎ 　ダンバインから連なる高機動型オーラ・バトラーの究極型。
> EN (odniesienie oficjalne, NIE polski): An Aura Battler shrouded in mystery. ⏎  ⏎ It represents the culmination of high-mobility Aura Battlers descended from the Dunbine's design.

### dic\_robot\_ZWUS\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b001`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b001\]
> JP (źródło tłumaczenia): 　黒騎士ラバーンの駆る漆黒のオーラ・バトラー。 ⏎ 　尻尾や独特の形状の翼など、他のオーラ・バトラーに見られない特徴を持つ。
> EN (odniesienie oficjalne, NIE polski): The jet-black Aura Battler piloted by the Black Knight Rabaan. ⏎  ⏎ Much about it is unique compared to other Aura Battlers, including its tail and the shape of its wings.

### dic\_robot\_LGIM\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b003`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b003\]
> JP (źródło tłumaczenia): 　ダバ・ハッサーが作り上げたハンドメイドのＡ級ヘビーメタル。 ⏎ 　ヤーマン族のヘビーメタル、ガイラムが元になっており、ヤーマン族の技術が至る所に活かされているが、量産が可能となるように意図的にデチューンされている部分もあるため、Ａ級ヘビーメタルの中では決して高い性能ではない。 ⏎ 　操縦席となるスパイラル・フローにより、コックピット内への物理的な衝撃が緩和されるという特徴を持つ。 ⏎ 　フロッサーの出力が不足しているため、飛行にはランドブースターを必要とする。
> EN (odniesienie oficjalne, NIE polski): A handmade A Class Heavy Metal put together by Daba Hatzer. ⏎  ⏎ It is based on the Gayrahm, a Heavy Metal of the Yaman Clan. While it makes use of advanced Yaman technological expertise, it has been intentionally detuned to allow future mass production; for this reason, its performance does not rank high among other A Class Heavy Metals. ⏎  ⏎ The Spiral Flow, an air bike that doubles as cockpit when docked into the L-Gaim, mitigates the effects of physical impacts on the pilot. ⏎  ⏎ Due to the Flossor's low output, it requires a Land Booster to fly.

### dic\_robot\_LGIM\_MK2\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b005`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b005\]
> JP (źródło tłumaczenia): 　強奪したポセイダル軍の新型ヘビーメタル「アモンデュール」を改造して作り上げたＡ級ヘビーメタル。 ⏎ 　アモンデュール自体がヤーマン族の技術を使用しており、そこにスパイラル・フローシステムなどの技術を導入したため、エルガイムの後継機として「Ｍｋ－Ⅱ」と名付けられる。 ⏎ 　最大の特徴はランドブースター「プローラー」への変形機能であり、これにより迅速な戦線への移動や離脱が可能となり、他の機体の運搬などにも使用される。 ⏎ 　また、搭載されたスパイラル・フローシステムはエルガイムのものをさらに発展させ、コックピット内での完全浮遊と３６０度スクリーンが実現されている。 ⏎ 　高出力ジェネレーターを装備した事により、バスターランチャーの運用も可能であり、高い機動性と攻撃力を兼ね備えた強力なＡ級ヘビーメタルとして完成した。 ⏎ 　また、その頭部には生体コンピュータのシルエットが浮かび上がる事がある。 ⏎ 　ダバ・マイロードが搭乗し、ポセイダルに抵抗する反乱軍の象徴となった。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal created by modifying the Amoun Düül, a new Heavy Metal model stolen from the Posaydal Forces. ⏎  ⏎ The Amoun Düül itself employed Yaman technology such as the Spiral Flow System; this modification was thus considered a successor to the L-Gaim, and named "Mark-II". ⏎  ⏎ Its most distinctive feature is the ability to transform into the Land Booster Plloler, giving this Heavy Metal the ability to quickly move to and from the battlefield, as well as transport allied units. ⏎  ⏎ The Spiral Flow System has received further development from the original L-Gaim; the seat can now fully float in the cockpit, from which the pilot has a 360-degree view of the outside. ⏎  ⏎ Mounted with a high-output generator, the Mark-II is designed to use the Buster Launcher, making it one of the best A Class Heavy Metal suits, possessing both high mobility and firepower. ⏎  ⏎ Occasionally, the silhouette of its bio-computer can be glimpsed in its head. ⏎  ⏎ Piloted by Daba Myroad, the L-Gaim Mark-II became the symbol of the rebellion against Posaydal.

### dic\_robot\_NDSD\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b007`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b007\]
> JP (źródło tłumaczenia): 　ガウ・ハ・レッシィがアマンダラ・カマンダラからホエールと共に譲り受けたＡ級ヘビーメタル。 ⏎ 　本来は別の機体であったが、エルガイムの量産機ディザードの技術が導入されて完成し、その名となった。その際、コックピットはスパイラル・フローシステムとなっている。 ⏎ 　両肩のバインダーに装備されたパワーランチャーが主な武装。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal that Gaw Ha Leccee acquired from Amandra Kamandra alongside the Whele. ⏎  ⏎ Originally planned to be a different unit, it was completed with the technology used in the mass-produced L-Gaim, the D-Sserd, and thus named after it. Because of this development history, the Novel D-Sserd utilizes the Spiral Flow System. ⏎  ⏎ Its main weapons are the Power Launchers mounted on both shoulder binders.

### dic\_robot\_BLBD\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b009`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b009\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＢ級ヘビーメタル。 ⏎ 　高性能なパーツを使用しているため、Ｂ級の中では別格の高性能を誇り、ポセイダル軍の兵士の中でも上位者に与えられている。
> EN (odniesienie oficjalne, NIE polski): One of the B Class Heavy Metals of the Posaydal Forces. ⏎  ⏎ Due to the implementation of high-performance parts, it is considered one of the best Heavy Metals of its class, supplied only to high-ranking officers in the army.

### dic\_robot\_BLBD\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b00b\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＢ級ヘビーメタル。 ⏎ 　高性能なパーツを使用しているため、Ｂ級の中では別格の高性能を誇り、ポセイダル軍の兵士の中でも上位者に与えられている。 ⏎ 　このカラーリングはポセイダル軍近衛師団が使用するもの。
> EN (odniesienie oficjalne, NIE polski): One of the B Class Heavy Metals of the Posaydal Forces. ⏎  ⏎ Due to the implementation of high-performance parts, it is considered one of the best Heavy Metals of its class, supplied only to high-ranking officers in the army. ⏎  ⏎ Its colors indicate that this Bal-Bud is affiliated with Posaydal's Imperial Guard.

### dic\_robot\_BASH\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00d`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b00d\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　白兵戦を得意とするが、豊富なオプション兵装で距離を問わず戦える。 ⏎ 　また、バスターランチャーも運用可能。 ⏎ 　他のＡ級ヘビーメタルと比較して、多くのレプリカが量産されている。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ While it is specialized in close-ranged combat, it can equip a variety of optional armaments to fight at any range. ⏎  ⏎ It is designed to use the Buster Launcher. ⏎  ⏎ Compared to other A Class Heavy Metals, many replicas of the Bat-Shu are known to exist.

### dic\_robot\_ASRAT\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b00f\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　四本の腕が特徴で、肩からのサブ・アームにはパワーランチャーを備えたサーカス・バインダーが装備されている。 ⏎ 　豊富な内蔵武装を持ち、バスターランチャーの運用も可能。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ Unlike common Heavy Metal designs, the Ashura Temple has two sub arms mounted on the back. These arms are used to operate the Circus Binders, each furnished with a Power Launcher. ⏎  ⏎ In addition to a wide range of built-in armaments, it's also designed to use the Buster Launcher.

### dic\_robot\_CRBLT\_P\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b011`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b011\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　格闘戦を重視した機体であり、バインダーは装備していないが、胸のリフレクターでパワーランチャーを跳ね返す事も出来る。 ⏎ 　また、バスターランチャーも運用可能。 ⏎ 　このカラーリングはクワサン・オリビーが使用した機体のものであり、ヘルミーネの名で呼ばれる。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ Developed with a focus on melee combat, it is not fitted with binders. The chest reflectors are capable of repelling even a Power Launcher shot. ⏎  ⏎ It is designed to use the Buster Launcher. ⏎  ⏎ Its colors indicate that this Calvary Temple is the model piloted by Quwasan Olibee, codenamed "Hellmeene."

### dic\_robot\_CRBLT\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b013`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b013\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　格闘戦を重視した機体であり、バインダーは装備していないが、胸のリフレクターでパワーランチャーを跳ね返す事も出来る。 ⏎ 　また、バスターランチャーも運用可能。 ⏎ 　このカラーリングはリョクレイ・ロン他が搭乗したもので、複数のレプリカが存在する。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ Developed with a focus on melee combat, it is not fitted with binders. The chest reflectors are capable of repelling even a Power Launcher shot. ⏎  ⏎ It is designed to use the Buster Launcher. ⏎  ⏎ Its colors indicate that this Calvary Temple is one of the various replicas assigned to Posaydal Forces officers such as Ryoklay Ront.

### dic\_robot\_GRON\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b015`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b015\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　ムーバル・フレームはＳサイズであるが、ジェネレーターはＭサイズのものを使用しており、パワーに優れる。 ⏎ 　パワーランチャーが内蔵されたロングスピアが主武装。 ⏎ 　また、バスターランチャーも運用可能。 ⏎ 　他のＡ級ヘビーメタルと比較して、多くのレプリカが量産されている。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ Though it was developed with an S-size movable frame, it mounts an M-size generator, giving it a comparatively higher power output. ⏎  ⏎ It is equipped with the Long Spear, a melee weapon with a built-in Power Launcher. Additionally, it is designed to use the Buster Launcher. ⏎  ⏎ Compared to other A Class Heavy Metals, many replicas of the G.Roon are known to exist.

### dic\_robot\_ATOL5\_00\_0

Adres: `dic\_text\_robot/014d369b:99a0b017`

> \[BRAK PL: dic\_text\_robot/014d369b:99a0b017\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル「アトール」をベースに５種類のＡ級ヘビーメタルを組み合わせたカスタム機。 ⏎ 　オージェのラウンド・バインダー、バッシュのバインダー、アシュラ・テンプルのサーカス・バインダー、グルーンのロングスピアを装備している。 ⏎ 　また、バスターランチャーも運用可能。
> EN (odniesienie oficjalne, NIE polski): A custom build that combines the features of five different Posaydal Forces A Class Heavy Metals. ⏎  ⏎ Using the A-Taul as a base, it has been mounted with the Auge's Round Binder, the Bat-Shu's arm binders, the Ashura Temple Circus Binders, and the G.Roon's Long Spear. ⏎  ⏎ The Bat-Shu's arm binders allow this build to use the Buster Launcher.

### dic\_robot\_AUGE\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b000\]
> JP (źródło tłumaczenia): 　ポセイダル軍のＡ級ヘビーメタル。 ⏎ 　最大の特徴は金を使用した装甲で、非常に高価な機体。 ⏎ 　両肩に装備されたラウンド・バインダーは腕とは独立して可動し、先端にはパワーランチャー、裏には多数のスロウランサーが装備されている。
> EN (odniesienie oficjalne, NIE polski): An A Class Heavy Metal of the Posaydal Forces. ⏎  ⏎ Its most distinctive feature is the armor, which is plated with actual gold, making this a particularly expensive Heavy Metal. ⏎  ⏎ The Round Binders on the shoulders can move independently from the arms. They are fitted with Power Launchers on the extremities, as well as multiple internally-mounted Throw Lancers.

### dic\_robot\_AUG\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b002\]
> JP (źródło tłumaczenia): 　真のオルドナ・ポセイダルが搭乗したヘビーメタル。 ⏎ 　バイオリレーション・システムとスヴェートから供給されるエネルギーで圧倒的なパワーを誇り、至近距離からのパワーランチャーの直撃も無効化した。 ⏎ 　左肩のバインダーに装備されたランチャーやスロウランサーの他に連結式のサイズ（鎌）を使用する。
> EN (odniesienie oficjalne, NIE polski): The Heavy Metal piloted by the true Oldna Posaydal. ⏎  ⏎ Enhanced by the energy provided by Sveet through the Biorelation System, this "original" Auge was capable of brushing off a point-blank Power Launcher shot. ⏎  ⏎ In addition to the Launchers and Throw Lancers mounted on the shoulder binders, the Auge is equipped with a combinable scythe. ⏎ 

### dic\_robot\_SUGEO\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b004\]
> JP (źródło tłumaczenia): 　ポセイダル軍のプラネット・クルーザー。 ⏎ 　多数のレーザー砲塔を装備し、ヘビーメタルの搭載数も多い。 ⏎ 　大気圏内外で使用可能。 ⏎ 　このカラーリングはギワザ・ロワウの座乗艦のもの。
> EN (odniesienie oficjalne, NIE polski): A planet cruiser of the Posaydal Forces. ⏎  ⏎ It is mounted with numerous laser cannons, and it is capable of carrying a large number of Heavy Metals. ⏎  ⏎ The Sarge Aupus can be operated both within and outside of an atmosphere. ⏎  ⏎ Its colors indicate that this particular vessel is captained by Giwaza Lowaw.

### dic\_robot\_SUGEO\_M\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b006\]
> JP (źródło tłumaczenia): 　ポセイダル軍のプラネット・クルーザー。 ⏎ 　多数のレーザー砲塔を装備し、ヘビーメタルの搭載数も多い。 ⏎ 　大気圏内外で使用可能。
> EN (odniesienie oficjalne, NIE polski): A planet cruiser of the Posaydal Forces. ⏎  ⏎ It is mounted with numerous laser cannons, and it is capable of carrying a large number of Heavy Metals. ⏎  ⏎ The Sarge Aupus can be operated both within and outside of an atmosphere.

### dic\_robot\_GMAZINGS\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b008\]
> JP (źródło tłumaczenia): 　鉄也が操縦するスーパーロボット。 ⏎ 　マジンガーＺの兄弟機であり、「偉大な勇者」の名に相応しいパワーを持つ。 ⏎ 　光子力エネルギーを動力としており、装甲は超合金ニューＺに覆われている。 ⏎ 　頭部に合体する小型戦闘機ブレーンコンドルがそのまま操縦席になり、背面のスクランブルダッシュで飛行が可能。 ⏎ 　胸部の高熱板から放つ熱線のブレストバーンの他、頭部のアンテナで雷を集めて指先から電撃を発射するサンダーブレーク等の武装を持つ。
> EN (odniesienie oficjalne, NIE polski): The super robot piloted by Tetsuya Tsurugi. ⏎  ⏎ A sibling machine to Mazinger Z, it holds a power worthy of the title "Great Hero". ⏎  ⏎ It is fueled by photon power energy and fully armored with Chogokin New Z. ⏎  ⏎ It is controlled through the Brain Condor, a small fighter that docks into the robot's head. The Scramble Dash on its back allows it to fly. ⏎  ⏎ In addition to the Breast Burn, a heat ray emitted from its chest plates, it can gather electricity from its antennas and cast it from its finger: the Thunder Break.

### dic\_robot\_DKJEN\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b00a\]
> JP (źródło tłumaczenia): 　七つの戦闘獣軍団を率いるミケーネ帝国の将軍。 ⏎ 　圧倒的なパワーを誇り、頭部の目から光線を放つ他、大剣を振るって戦う。 ⏎ 　羽織っているマントは、マジンカイザーのファイヤーブラスターをも弾く。
> EN (odniesienie oficjalne, NIE polski): The general of all Seven Battle Beast Armies of the Mycenae Empire. ⏎  ⏎ Boasting formidable strength, he wields a broadsword and can release energy beams from his eyes. ⏎  ⏎ His cape is capable of repelling Mazinkaiser's Fire Blaster.

### dic\_robot\_HRDIAS\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b00c\]
> JP (źródło tłumaczenia): 　悪霊型戦闘獣の長であり、ミケーネ七大将軍の一人。 ⏎ 　大鎌による攻撃の他、左腕の顔から５万度の火の玉を吐き出す。
> EN (odniesienie oficjalne, NIE polski): One of the generals of the Seven Armies, leading the Spectral Battle Beasts. ⏎  ⏎ In addition to wielding a scythe, the head he carries in his left arm can emit fireballs the temperature of 50,000 degrees Celsius.

### dic\_robot\_DANTE\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b00e\]
> JP (źródło tłumaczenia): 　悪霊型戦闘獣。 ⏎ 　光輪を駆使して戦う。
> EN (odniesienie oficjalne, NIE polski): A spectral-type Battle Beast. ⏎  ⏎ He fights using rings of light.

### dic\_robot\_MAZINKZR\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b010\]
> JP (źródło tłumaczenia): 　ある世界の兜十蔵博士が開発した、光子力反応炉を搭載するマジンガーＺのプロトタイプ。 ⏎ 　「魔神皇帝」「デビルマジンガー」とも呼ばれる。 ⏎ 　搭載されている光子力反応炉は絶大な出力を誇るが、その制御は難しく、起動時に暴走する危険性を持つ。そのため、兜十蔵博士は光子力反応炉ごとカイザーを光子力研究所の第７格納庫に封印した。その際、光子力エネルギーを使用したロボット…すなわちマジンガーが悪用されることを懸念した博士によって、「悪のマジンガーを倒すためのマジンガー」という役目も与えられた。 ⏎ 　また、マジンカイザーには自律回路に似た装置が組み込まれており、起動した際には「魔」「神」「Ｚ」の３つのモードが選択される。 ⏎ 　まず、「魔」モードは悪のマジンガーの存在を探知した場合、パイルダーなしでも自動的に戦闘するモードである。しかし、その制御はほぼ不可能であり、最悪の場合はカイザーそのものが破壊の権化となってしまう。 ⏎ 　次に、「神」モードはカイザーが秘められたパワーを解放するモードであるが、その詳細は不明である（マジンパワーの一種だと想定される）。 ⏎ 　最後に「Ｚ」モードはカイザーパイルダーがパイルダーオンした状態で、通常はこのモードで戦闘を行う。 ⏎ 　装甲は超合金ニューＺα、操縦系統にはシンクロシステムが使用され、操縦者の意志によって無限の力を引き出すことが出来る。
> EN (odniesienie oficjalne, NIE polski): The prototype of Mazinger Z developed by the Juzo Kabuto of another world. ⏎  ⏎ It is also known as the "Mazin Emperor" and the "Devil Mazinger". ⏎  ⏎ Its Photon Power Reactor can generate immense power, but it is very difficult to control, and there is a high risk that it could run berserk; this is why Dr. Juzo sealed Mazinkaiser in Hangar 7 of the Photon Power Laboratory. At the time, Dr. Juzo was concerned that Mazinger Z might be stolen and misused for evil; thus, he developed what he called a "Mazinger to defeat an evil Mazinger". ⏎  ⏎ Mazinkaiser incorporates a device akin to an autonomous circuit that selects one of three modes when activated: Devil, God, and Z. ⏎  ⏎ Devil Mode is activated when Mazinkaiser detects the presence of an evil Mazinger. It will automatically engage in combat, even if the Pilder is not docked. However, it is nearly impossible to control in this mode; in the worst-case scenario, Mazinkaiser could become the avatar of destruction. ⏎  ⏎ God Mode is how Mazinkaiser can unleash its true powers, but the details are unknown. It is speculated that it may utilize a type of Mazin Power. ⏎  ⏎ Z Mode is Mazinkaiser's normal state, activated when the Kaiser Pilder is docked to its head; this is the mode typically used for combat. ⏎  ⏎ Its armor is composed of Super Alloy New Z Alpha. It implements the Synchro System, which allows Mazinkaiser to draw out virtually unlimited power depending on its pilot's will.

### dic\_robot\_MAZINENG\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b012`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b012\]
> JP (źródło tłumaczenia): 　兜十蔵博士が開発したもう一体の魔神皇帝。 ⏎ 　マジンカイザーの危機に呼応して起動するように設定されていたが、同時にマジンカイザーが暴走した際の抑止力となる存在とされている。 ⏎ 　グレートマジンガーをベースに設計されており、あらゆる点でマジンガーＺとグレートマジンガーを上回り、「偉大なる魔神皇帝」の異名を持つ。 ⏎ 　本来の名称は「マジンエンペラー」だが、グレートマジンガーの搭乗者であった剣鉄也によって、グレートを継ぐ者として「Ｇ」がつけられた。
> EN (odniesienie oficjalne, NIE polski): The other "emperor" developed by Dr. Juzo Kabuto. ⏎  ⏎ While it is set to activate should a crisis befall the Mazinkaiser, it is more properly intended as a deterrent in case Mazinkaiser goes berserk. ⏎  ⏎ Its design is based on Great Mazinger. Surpassing both Mazinger Z and Great Mazinger in every way, it has earned the name of "Great Emperor". ⏎  ⏎ Its original name is "Mazin Emperor", but Tetsuya Tsurugi added the "G" as a tribute to his beloved Great Mazinger.

### dic\_robot\_DKEN\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b014`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b014\]
> JP (źródło tłumaczenia): 　ミケーネ帝国の支配者。 ⏎ 　七大将軍を率いる暗黒大将軍を配下に従えるほどの絶対的な力を持ち、地上から人類を駆逐するべく、永い眠りから目を覚ました。 ⏎ 　全身が炎と化している。
> EN (odniesienie oficjalne, NIE polski): The supreme ruler of the Mycenae Empire. ⏎  ⏎ After awakening from his long slumber, he commands the Great General of Darkness to lead the Seven Armies and wipe the human race from the face of the earth. ⏎  ⏎ His body is entirely made of flames.

### dic\_robot\_BKDR\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b016`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b016\]
> JP (źródło tłumaczenia): 　ミケーネ帝国が造り上げた機械生命体。 ⏎ 　異文明を滅ぼす事を目的としている。 ⏎ 　小型タイプは他の機体に取り付いて、その制御を奪う力を持つが、大型タイプは直接的な戦力として使われる。
> EN (odniesienie oficjalne, NIE polski): A mechanical life form created by the Mycenae Empire. ⏎  ⏎ Its purpose is to destroy other civilizations. ⏎  ⏎ The small variant can attach itself to other machines and control them, while the large variant is employed directly for combat.

### dic\_robot\_GTRARK\_00\_0

Adres: `dic\_text\_robot/014d369b:99e0b018`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b018\]
> JP (źródło tłumaczenia): 　三機のゲットマシンがアーク号、キリク号、カーン号の順に合体したゲッターロボ。 ⏎ 　第４世代のゲッターロボであり、早乙女研究所の前所長である早乙女博士の最後の遺産と呼ばれる。 ⏎ 　従来のゲッターロボに比べて、安定性やエネルギー効率、戦闘力が格段に向上している。 ⏎ 　搭乗者に大きな重力負荷を強いるが、高速での飛行も可能。 ⏎ 　腕部の伸縮自在な刃で切り裂くバトルショットカッターの他、機体の四方へ雷撃を放つサンダーボンバー等の武装を持つ。
> EN (odniesienie oficjalne, NIE polski): The Getter Robo form created by the combination of the Get Machines Arc, Kirik, and Khan (in that order). ⏎  ⏎ It is the fourth generation Getter Robo, the final legacy of Dr. Saotome, the former director of the Saotome Laboratory. ⏎  ⏎ It has greater stability, energy efficiency, and combat power than previous Getter Robo models. It can fly at incredible speeds, though this places a heavy g-force burden on its pilots. ⏎  ⏎ In addition to the telescoping Battle Shot Cutter blades in its arms, it is equipped with the Thunder Bomber, a weapon that fires lightning bolts in all directions.

### dic\_robot\_GTRARK\_00\_1

Adres: `dic\_text\_robot/014d369b:99e0b019`

> \[BRAK PL: dic\_text\_robot/014d369b:99e0b019\]
> JP (źródło tłumaczenia): 　遥か未来での魔獣ウザーラとの決戦において、その力を覚醒させ、新たな必殺技・アークシャインボンバーを放った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the decisive battle against the Legendary Beast Uzala in the faraway future, it awakened a new power, the Arc Shine Bomber.

### dic\_robot\_GTRKRIK\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b000\]
> JP (źródło tłumaczenia): 　三機のゲットマシンがキリク号、カーン号、アーク号の順に合体したゲッターロボ。 ⏎ 　スピードを活かした高速戦闘を得意としており、左腕のアームと右腕のドリルを使い分けて戦う。 ⏎ 　状況に応じて両腕をドリルに変化させる事も可能で、全身をドリルにして敵に突撃するダブルドリルストームを必殺技とする。
> EN (odniesienie oficjalne, NIE polski): The Getter Robo form created by the combination of the Get Machines Kirik, Khan, and Arc (in that order). ⏎  ⏎ Specializing in high-speed combat, it employs its two asymmetrical arms strategically. When the situation calls for additional piercing power, it can turn both arms into drills, charging the enemy in a maneuver called Double Drill Storm.

### dic\_robot\_GTRKARN\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b002\]
> JP (źródło tłumaczenia): 　三機のゲットマシンがカーン号、アーク号、キリク号の順に合体したゲッターロボ。 ⏎ 　パワーに優れている他、深海等の高圧下での戦闘を得意とする。 ⏎ 　巨大なタイヤ型のカーンローバー形態に変形し、敵を内部から真っ二つにするスパインクラッシャーを必殺技とする。 ⏎ 　また、水中ではカーンローバー形態のまま回転して水流を巻き起こすメイルストロームが使用可能。
> EN (odniesienie oficjalne, NIE polski): The Getter Robo form created by the combination of the Get Machines Khan, Arc, and Kirik (in that order). ⏎  ⏎ In addition to its superior raw power, it excels at fighting in high-pressure underwater environments. By transforming into the tire-shaped Khan Rover form, it can perform the Spine Crusher maneuver, splitting its opponent in half from the inside. ⏎  ⏎ When fighting underwater in the Khan Rover form, it can spin at high speeds to create a powerful current, the Maelstrom.

### dic\_robot\_GTRTRK\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b004\]
> JP (źródło tłumaczenia): 　黒い真ゲッターロボ。 ⏎ 　圧倒的なスピードを持ち、長距離を一瞬で移動する。 ⏎ 　両手に構えるゲッタートマホークや腹部から発射するゲッタービームの他、人差し指から超収束型ゲッターエネルギーを放つゲッターレーザー等を武器とする。
> EN (odniesienie oficjalne, NIE polski): A black Shin Getter Robo. It can instantaneously travel long distances with its overwhelming speed. ⏎  ⏎ Its weapons include a two-handed Getter Tomahawk, the Getter Beam in its abdomen, and the Getter Laser, high-focused Getter energy emitted from its index finger.

### dic\_robot\_GTRTRK\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b005`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b005\]
> JP (źródło tłumaczenia): 　ジュラ・デッド作戦において、海中でアンドロメダ流国の襲撃を受ける拓馬達の救援に現れ、亜空間固定装置ゾルドから彼等を時空の彼方へ送り出した後、パイロットの號と共に消滅した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It appears during Operation Jura Dead to rescue Takuma and his comrades from the Andromeda Stellaration. It protects the hyperspace anchor module Zold, allowing Getter Team to cross time and space before disappearing alongside its pilot, Go Ichimonji.

### dic\_robot\_GTRZURS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b006\]
> JP (źródło tłumaczenia): 　恐竜帝国のゲットマシンであるボアレックス、ガリム、メガロンの三機が合体したゲッターロボ。 ⏎ 　隼人が恐竜帝国のハン博士に提供した技術で完成した。 ⏎ 　主な武器は棍棒の両端に突起の付いたダブルシュテルンで、ゲッターアークと共にアンドロメダ流国に立ち向かった。
> EN (odniesienie oficjalne, NIE polski): The Dinosaur Empire Getter Robo created by combining the Get Machines Vorex, Gallim, and Megalon. It was developed by Professor Han of the Dinosaur Empire, using technology provided by Hayato Jin. ⏎  ⏎ Its primary weapon is the Double Stern, a twin-headed spiked mace that it wielded in the battle against the Andromeda Stellaration.

### dic\_robot\_GTRZURS\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b007\]
> JP (źródło tłumaczenia): 　遥か未来から現代に戻ったカムイによって量産され、人類の敵となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It enters mass production after Kamui returns from the faraway future, becoming the enemy of humanity.

### dic\_robot\_TENKU\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b008\]
> JP (źródło tłumaczenia): 　戦闘兵器・インセクターを率いる前線指揮官。 ⏎ 　擬態能力の他、分身能力を持ち、ゲッターＤ２部隊を苦しめた。
> EN (odniesienie oficjalne, NIE polski): The front commander leading the Insector army. ⏎  ⏎ He toys with the Getter D2 squadron, using his shape-shifting and multiplying abilities.

### dic\_robot\_TENKU\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b009`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b009\]
> JP (źródło tłumaczenia): 　ゲッターアークのダブルトマホークにより、斬り刻まれて倒された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He was torn apart by Getter Arc's Double Tomahawk.

### dic\_robot\_ZLDXX\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b00a\]
> JP (źródło tłumaczenia): 　謎の敵が送り込んだ巨大兵器。 ⏎ 　下半身に無数の触手を持ち、相手に突き刺して攻撃する他、上半身の単眼からビームを発射する。 ⏎ 　ゲッタートマホークやゲッタービームが通じないほどの堅牢な装甲を持つ。
> EN (odniesienie oficjalne, NIE polski): A giant weapon sent by a mysterious enemy. Its lower body is covered in countless tentacles, which it can use to pierce its opponents; furthermore, it can release beams from the eye on its top section. ⏎  ⏎ Its armor is so resistant that neither the Getter Tomahawk nor the Getter Beam can penetrate it.

### dic\_robot\_ZLDXX\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b00b\]
> JP (źródło tłumaczenia): 　装甲の損傷部分に拓馬が乗るゲッターＤ２とカムイが乗るゲッターアークのビームを受けて爆発した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It is finally destroyed when the combined beams of Takuma's Getter D2 and Kamui's Getter Arc target the damaged section of its armor.

### dic\_robot\_INSCTR\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b00c\]
> JP (źródło tłumaczenia): 　謎の敵が送り込む兵器。 ⏎ 　ストーカと呼ばれる亜空間から無数に現れる。
> EN (odniesienie oficjalne, NIE polski): A weapon sent by a mysterious enemy. Countless of them emerge from the hyperspace gate known as Stoker.

### dic\_robot\_UZAR\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b00e\]
> JP (źródło tłumaczenia): 　太古の地球に存在したアトランティス文明の超兵器。 ⏎ 　雷撃による攻撃の他、重力を遮断する光線を放つ。 ⏎ 　特殊な合金・オリハルコンで出来た堅牢な装甲を誇り、かつて拓馬の父・流竜馬達がゲッタードラゴンで戦った際には傷一つつける事が出来なかった。 ⏎ 　竜馬達に協力して百鬼帝国を壊滅させた後は宇宙空間に姿を消していたが、百鬼帝国の生き残りであるマクドナルドの手に落ち、その戦力となった。
> EN (odniesienie oficjalne, NIE polski): A super weapon of the Atlantis civilization that once existed on Earth. In addition to lightning strikes, it can emit a beam that isolates gravity. ⏎  ⏎ Its armor is composed of a special alloy called Orichalcum, a robust material that not even Ryoma Nagare could put a dent in when he fought it with Getter Dragon many years ago. ⏎  ⏎ It disappeared into space after cooperating with Ryoma's team to defeat the Hyakki Empire; however, it has fallen into the hands of McDonald.

### dic\_robot\_UZAR\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b00f\]
> JP (źródło tłumaczenia): 　遥か未来での戦闘では圧倒的な力で拓馬達を苦しめたが、ゲッターアークのアークシャインボンバーの前に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In the faraway future, it overwhelms Takuma's team with its tremendous power, but it finally falls to Getter Arc's Arc Shine Bomber.

### dic\_robot\_BUGU\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b010\]
> JP (źródło tłumaczenia): 　アンドロメダ流国が設計した超兵器。 ⏎ 　バグという名称は、「Biogeocenosis」（生態系）・「Unlimited」（無限界）・「Genocidemachine」（抹消機）の頭文字を取ってつけられた。 ⏎ 　カムイがマクドナルドから託されたデータとマテリアルを現代に持ち帰り、恐竜帝国の科学力を合わせる事で完成した。 ⏎ 　惑星を創り変えるほどの絶対的な力を持つ。
> EN (odniesienie oficjalne, NIE polski): A super-weapon designed by the Andromeda Stellaration. BUG is an acronym for "Biogeocenosis Unlimited Genocidemachine". ⏎  ⏎ Kamui received the original from McDonald in the faraway future; he then used the technological prowess of the Dinosaur Empire to complete the design and produce it. ⏎  ⏎ It possesses the power of planetary alteration, capable of rebuilding a planet according to its pilot's wishes.

### dic\_robot\_BUGU\_00\_1

Adres: `dic\_text\_robot/014d369b:9a20b011`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b011\]
> JP (źródło tłumaczenia): 　その強大な戦闘力により、拓馬の乗るゲッターアークを圧倒した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ With its tremendous power, it could easily overwhelm Takuma's Getter Arc.

### dic\_robot\_GTRHDGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9a20b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9a20b012\]
> JP (źródło tłumaczenia): 　進化により新たな段階となったゲッタードラゴン。 ⏎ 　早乙女研究所の地中深くで進化を続けていたが、バグとゲッターアークの戦いの場に現れた。
> EN (odniesienie oficjalne, NIE polski): The next stage of evolution reached by Getter Dragon.  ⏎  ⏎ After constantly evolving in the depths of the Saotome Laboratory, it appears at the site of the battle between the BUG and Getter Arc.

### dic\_robot\_VF31JSGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b000\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のデルタ小隊が使用する可変戦闘機「VF-31」J型の改造機。 ⏎ 　VF-31Jは、幅広い任務に対応する制宙支援仕様に区分される最新鋭の機体。 ⏎ 　搭乗者であるハヤテ・インメルマンのフライトデータをベースに操縦系統がカスタマイズされているため、この名称を持つ。 ⏎ 　なお、機体のカラーリングとパーソナルマークは、戦死したメッサー・イーレフェルト搭乗機の意匠を受け継いだものとなっている。
> EN (odniesienie oficjalne, NIE polski): A customized version of the VF-31 Variable Fighter used by the Ragna branch of the interstellar conglomerate Xaos's Delta Flight. ⏎  ⏎ The VF-31J is a cutting-edge air-superiority unit intended to be adaptable to a wide variety of mission conditions. ⏎  ⏎ The unit gets its designation from the fact that it's customized based on the flight data of its pilot, Hayate Immelmann. ⏎  ⏎ On the other hand, its color scheme and marking are inherited from the personal machine of Messer Ihlefeld, who was killed in battle.

### dic\_robot\_VF31JSGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b002\]
> JP (źródło tłumaczenia): 　VF-31Jが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31J equipped with a Super Pack for outer space operations. ⏎  ⏎ It has improved mobility in space theaters.

### dic\_robot\_VF31JGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b004\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のΔ小隊が使用する可変戦闘機「VF-31」のバリエーションの一つ。 ⏎ 　VF-31 ジークフリードは、ケイオスがVF-31A カイロスをヴァール鎮圧任務用に改修した機体であり、マルチパーパスコンテナユニットを継承しつつ、より大型のフォールド・クォーツを搭載している。これにより、戦術音楽ユニット「ワルキューレ」の歌に含まれるフォールド波を増幅する。 ⏎ 　VF-31Jは、幅広い任務に対応する制宙支援仕様に区分される最新鋭の機体。 ⏎ 　バトロイド形態時の頭部レーザー砲は１門。 ⏎ 　Δ小隊では、コールサイン・Δ５、ハヤテ・インメルマン准尉が搭乗する。
> EN (odniesienie oficjalne, NIE polski): A variant model of the VF-31 Variable Fighter, used by the Ragna branch of the interstellar conglomerate Xaos's Delta Squadron.  ⏎  ⏎ The VF-31 Siegfried is a remodeled version of the VF-31A Kairos built for use during Var Syndrome suppression missions. It inherits the multipurpose container unit from the previous model, but is equipped with more Fold Quartz. As a result, it is able to amplify the Fold Waves contained within the songs of the Tactical Sound Unit Walküre.  ⏎  ⏎ The VF-31J is a cutting-edge air superiority unit intended to be adaptable to a wide variety of mission conditions. In its Battroid Mode, it has a single head-mounted laser gun. ⏎  ⏎ In Delta Squadron, this Valkyrie's callsign is Delta 5, and is piloted by Warrant Officer Hayate Immelmann.

### dic\_robot\_VF31JGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b006\]
> JP (źródło tłumaczenia): 　VF-31Jが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31J, equipped with a Super Pack for outer space operations. Provides increased mobility in space theaters.

### dic\_robot\_VF31FSGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b008\]
> JP (źródło tłumaczenia): 　Δ小隊が運用していたVF-31Fにウィンダミア王国軍の無人小型支援機「リル・ドラケン」を装備した状態。 ⏎ 　ウィンダミア軍に鹵獲されたVF-31Fをハヤテが現地で調整した。 ⏎ 　リル・ドラケンの補助スラスターにより推力が向上し、より立体的な機動が可能となった。
> EN (odniesienie oficjalne, NIE polski): Delta Squadron's VF-31F, equipped with the Windermerian autonomous fighter Lilldraken. ⏎  ⏎ This setup was used by Hayate when he acquired a VF-31F on location after it was captured by the Windermerian military. ⏎  ⏎ The auxiliary thrust provided by the Lilldrakens increases the VF-31F's overall thrust, granting it superior three-dimensional agility.

### dic\_robot\_VF31FGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b00a\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のΔ小隊が使用する可変戦闘機「VF-31」のバリエーションの一つ。 ⏎ 　VF-31 ジークフリードは、ケイオスがVF-31A カイロスをヴァール鎮圧任務用に改修した機体であり、マルチパーパスコンテナユニットを継承しつつ、より大型のフォールド・クォーツを搭載している。これにより、戦術音楽ユニット「ワルキューレ」の歌に含まれるフォールド波を増幅する。 ⏎ 　VF-31Fは、主に敵機との戦闘を担当する制宙支配仕様に区分される。 ⏎ 　バトロイド形態時の頭部レーザー砲は４門。 ⏎ 　Δ小隊では、コールサイン・Δ２、メッサー・イーレフェルト中尉が搭乗し、機体上面には死神のパーソナルマークが描かれている。
> EN (odniesienie oficjalne, NIE polski): A variant model of the VF-31 Variable Fighter, used by the Ragna branch of the interstellar conglomerate Xaos's Delta Squadron.  ⏎  ⏎ The VF-31 Siegfried is a remodeled version of the VF-31A Kairos built for use during Var Syndrome suppression missions. It inherits the multipurpose container Unit from the previous model, but is equipped with more Fold Quartz. As a result, it is able to amplify the Fold Waves contained within the songs of the Tactical Sound Unit Walküre.  ⏎  ⏎ The VF-31F is primarily an air superiority model designed for dogfighting with enemy fighters. It has four head-mounted laser guns in Battroid Mode. ⏎  ⏎ In Delta Squadron, this Valkyrie's callsign is Delta 2, and is piloted by First Lieutenant Messer Ihlefeld, with his personalized grim reaper mark on the top of the fighter.

### dic\_robot\_VF31FGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b00c\]
> JP (źródło tłumaczenia): 　VF-31Fが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31F, equipped with a Super Pack for outer space operations. Provides increased mobility in space theaters.

### dic\_robot\_VF31CGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b00e\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のΔ小隊が使用する可変戦闘機「VF-31」のバリエーションの一つ。 ⏎ 　VF-31 ジークフリードは、ケイオスがVF-31A カイロスをヴァール鎮圧任務用に改修した機体であり、マルチパーパスコンテナユニットを継承しつつ、より大型のフォールド・クォーツを搭載している。これにより、戦術音楽ユニット「ワルキューレ」の歌に含まれるフォールド波を増幅する。 ⏎ 　VF-31Cは、火力によって前線の作戦行動を支援する戦術支援仕様に区分される。 ⏎ 　バトロイド形態時の頭部レーザー砲は２門。 ⏎ 　Δ小隊では、コールサイン・Δ４、ミラージュ・ファリーナ・ジーナス少尉が搭乗する。
> EN (odniesienie oficjalne, NIE polski): A variant model of the VF-31 Variable Fighter, used by the Ragna branch of the interstellar conglomerate Xaos's Delta Squadron.  ⏎  ⏎ The VF-31 Siegfried is a remodeled version of the VF-31A Kairos built for use during Var Syndrome suppression missions. It inherits the multipurpose container unit from the previous model, but is equipped with more Fold Quartz. As a result, it is able to amplify the Fold Waves contained within the songs of the Tactical Sound Unit Walküre.  ⏎  ⏎ This model is the VF-31C, with an emphasis on improved firepower to provide tactical fire support for frontline operations. ⏎ It also has two head-mounted laser guns available in Battroid Mode. ⏎  ⏎ In Delta Squadron, this Valkyrie's callsign is Delta 4, and is piloted by Second Lieutenant Mirage Farina Jenius.

### dic\_robot\_VF31CGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b010\]
> JP (źródło tłumaczenia): 　VF-31Cが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31C, equipped with a Super Pack for outer space operations. Provides increased mobility in space theaters.

### dic\_robot\_VF31EGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b012\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のΔ小隊が使用する可変戦闘機「VF-31」のバリエーションの一つ。 ⏎ 　VF-31 ジークフリードは、ケイオスがVF-31A カイロスをヴァール鎮圧任務用に改修した機体であり、マルチパーパスコンテナユニットを継承しつつ、より大型のフォールド・クォーツを搭載している。これにより、戦術音楽ユニット「ワルキューレ」の歌に含まれるフォールド波を増幅する。 ⏎ 　VF-31Eは、早期警戒任務用に収容式のレーダードームを装備しており、展開して使用する。 ⏎ 　バトロイド形態時の頭部レーザー砲は２門。 ⏎ 　Δ小隊では、コールサイン・Δ３、チャック・マスタング少尉が搭乗する。
> EN (odniesienie oficjalne, NIE polski): A variant model of the VF-31 Variable Fighter, used by the Ragna branch of the interstellar conglomerate Xaos's Delta Squadron. ⏎  ⏎ The VF-31 Siegfried is a remodeled version of the VF-31A Kairos built for use during Var Syndrome suppression missions. It inherits the multipurpose container unit from the previous model, but is equipped with more Fold Quartz. As a result, it is able to amplify the Fold Waves contained within the songs of the Tactical Sound Unit Walküre. ⏎  ⏎ The VF-31E has a deployable radar dome which can be utilized in reconnaissance missions. It also has two head-mounted laser guns available in Battroid Mode. ⏎  ⏎ In Delta Squadron, this Valkyrie's callsign is Delta 3, and is piloted by Second Lieutenant Chuck Mustang.

### dic\_robot\_VF31EGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9a60b014`

> \[BRAK PL: dic\_text\_robot/014d369b:9a60b014\]
> JP (źródło tłumaczenia): 　VF-31Eが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31E, equipped with a Super Pack for outer space operations. Provides increased mobility in space theaters.

### dic\_robot\_VF31SGKF\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b000\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオス・ラグナ支部所属のΔ小隊が使用する可変戦闘機「VF-31」のバリエーションの一つ。 ⏎ 　VF-31 ジークフリードは、ケイオスがVF-31A カイロスをヴァール鎮圧任務用に改修した機体であり、マルチパーパスコンテナユニットを継承しつつ、より大型のフォールド・クォーツを搭載している。これにより、戦術音楽ユニット「ワルキューレ」の歌に含まれるフォールド波を増幅する。 ⏎ 　VF-31Sは、指揮官機として通信管制システムが強化されている。 ⏎ 　バトロイド形態時の頭部レーザー砲は４門。 ⏎ 　Δ小隊では、コールサイン・Δ１、アラド・メルダース少佐が搭乗し、機体上面にはドラゴンスカルのパーソナルマークが描かれている。
> EN (odniesienie oficjalne, NIE polski): A variant model of the VF-31 Variable Fighter, used by the Ragna branch of the interstellar conglomerate Xaos's Delta Squadron.  ⏎  ⏎ The VF-31 Siegfried is a remodeled version of the VF-31A Kairos built for use during Var Syndrome suppression missions. It inherits the multipurpose container unit from the previous model, but is equipped with more Fold Quartz. As a result, it is able to amplify the Fold Waves contained within the songs of the Tactical Sound Unit Walküre.  ⏎  ⏎ The VF-31S is equipped with an improved communications and command suite to match its intended role as a command unit. In its Battroid Mode, it has four head-mounted laser guns. ⏎  ⏎ In Delta Squadron, this Valkyrie's callsign is Delta 1, and is piloted by Major Arad Mölders, and it has his personal dragon skull mark on the top of the fighter.

### dic\_robot\_VF31SGKFS\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b002\]
> JP (źródło tłumaczenia): 　VF-31Sが大気圏外の作戦行動用にスーパーパックを装備した状態。 ⏎ 　宇宙空間における機動性が向上している。
> EN (odniesienie oficjalne, NIE polski): The VF-31S, equipped with a Super Pack for outer space operations. Provides increased mobility in space theaters.

### dic\_robot\_MCRS\_ERSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b004\]
> JP (źródło tłumaczenia): 　星間複合企業体ケイオスのラグナ支部の拠点を兼ねるマクロス級戦艦。 ⏎ 　サイズは８００メートル級。 ⏎ 　要塞艦型と強攻型の二つの形態を持ち、平時は惑星ラグナに強攻型形態で駐留している。 ⏎ 　強攻型形態時の両腕部は切り離しが可能となっており、右腕部には、空母「ヘーメラー」が接続されており、主砲マクロス・キャノンにも変形可能。左腕には空母「アイテール」が接続されており、Δ小隊とワルキューレが所属している。
> EN (odniesienie oficjalne, NIE polski): A Macross-class battleship which also serves as the Ragna branch of the interstellar conglomerate Xaos. It is an 800-meter-class ship with two forms—Fortress Mode and Assault mode. ⏎  ⏎ During peacetime, it is stationed on the planet Ragna in Assault Mode. ⏎ When in Assault Mode it is able to detach its arms, which each serve a different role. The right arm has the independent carrier ship Hemera integrated into it, and is also capable of forming the Macross Cannon. The left arm has the carrier ship Aether integrated into it, and is generally tasked with servicing Delta Squadron and acting as home to Walküre.

### dic\_robot\_MCRS\_GRSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b006\]
> JP (źródło tłumaczenia): 　マクロス・エリシオンと同型のマクロス級戦艦。 ⏎ 　基本装備や性能はマクロス・エリシオンと共通だが、カラーリングが異なる。 ⏎ 　艦全体の色は緑褐色系。
> EN (odniesienie oficjalne, NIE polski): A Macross-class battleship of the same design as the Macross Elysion. ⏎  ⏎ Its general specifications and capabilities are equivalent to the Macross Elysion, so it is instead distinguished by different coloring.

### dic\_robot\_MCRS\_MGSON\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b008\]
> JP (źródło tłumaczenia): 　マクロス・エリシオンと同型のマクロス級戦艦。 ⏎ 　基本装備や性能はマクロス・エリシオンと共通だが、カラーリングが異なる。 ⏎ 　艦全体の色は茶褐色系。
> EN (odniesienie oficjalne, NIE polski): A Macross-class battleship of the same design as the Macross Elysion. ⏎  ⏎ Its general specifications and capabilities are equivalent to the Macross Elysion, so it is instead distinguished by different coloring.

### dic\_robot\_VF17NTMP\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b00a\]
> JP (źródło tłumaczenia): 　新統合軍が使用する可変戦闘機。 ⏎ 　一般パイロットでも扱えるように設計された機体で、旧式になりつつあるが、配備領域は広範囲に渡る。
> EN (odniesienie oficjalne, NIE polski): A variable fighter employed by the New United Nations Government. ⏎  ⏎ This model is designed for use by standard pilots, and though it is gradually becoming outdated is still found employed in military forces far and wide.

### dic\_robot\_SV262BDKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b00c\]
> JP (źródło tłumaczenia): 　ウィンダミア王国が使用する可変戦闘機。 ⏎ 　局地戦と拠点防御用として設計された最新鋭機で、高い上昇力と加速性能、機動性能を持つ。 ⏎ 　また、光学ステルスシステムを外装に施しており、カラーリングを自在に変更する事が可能。 ⏎ 　両翼に無人戦闘機「リル・ドラケン」を装着して運用する。
> EN (odniesienie oficjalne, NIE polski): A Variable Fighter used in battle by the Kingdom of Windermere. ⏎  ⏎ This cutting-edge model was designed for high-priority sorties and base defense, and its design enables it to perform incredibly rapid climbs, extreme acceleration, and highly mobile maneuvers.  ⏎  ⏎ It is also equipped with an optical stealth system, which also allows it to change its coloring on the fly. One Lilldraken autonomous fighter is mounted on each wing.

### dic\_robot\_SV262BDKN\_H\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b00e\]
> JP (źródło tłumaczenia): 　Sv-262Baの空中騎士団ヘルマン・クロース搭乗機。 ⏎ 　機体上面には空中騎士団の紋章と家紋である斧をかたどった意匠が施されている。 ⏎ 　カラーリングのラインは白とグレー。
> EN (odniesienie oficjalne, NIE polski): Aerial Knight Hermann Kroos's personal Sv-262Ba. ⏎  ⏎ It bears a design with the crest of the Aerial Knights and his family crest, an axe. ⏎  ⏎ Its trim is white and grey.

### dic\_robot\_SV262BDKN\_B\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b010\]
> JP (źródło tłumaczenia): 　Sv-262Baの空中騎士団ボーグ・コンファールト搭乗機。 ⏎ 　機体上面には空中騎士団の紋章と家紋である槍をかたどった意匠が施されている。 ⏎ 　カラーリングのラインはピンク。
> EN (odniesienie oficjalne, NIE polski): Aerial Knight Bogue Con-Vaart's personal Sv-262Ba. ⏎  ⏎ It bears a design with the crest of the Aerial Knights and his family crest, a spear. ⏎  ⏎ Its trim is pink.

### dic\_robot\_SV262BDKN\_K\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b012\]
> JP (źródło tłumaczenia): 　Sv-262Baの空中騎士団カシム・エーベルハルト搭乗機。 ⏎ 　機体上面には空中騎士団の紋章と家紋である馬をかたどった意匠が施されている。 ⏎ 　カラーリングのラインはオレンジ。
> EN (odniesienie oficjalne, NIE polski): Aerial Knight Kassim Eber-hardt's personal Sv-262Ba. ⏎  ⏎ It bears a design with the crest of the Aerial Knights and his family crest, a horse. ⏎  ⏎ Its trim is orange.

### dic\_robot\_SV262BDKN\_T\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b014`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b014\]
> JP (źródło tłumaczenia): 　Sv-262Baの空中騎士団テオ・ユッシラ搭乗機。 ⏎ 　機体上面には空中騎士団の紋章と家紋である車輪をかたどった意匠が施されている。 ⏎ 　カラーリングのラインは青。
> EN (odniesienie oficjalne, NIE polski): Aerial Knight Theo Jussila's personal Sv-262Ba. ⏎  ⏎ It bears a design with the crest of the Aerial Knights and his family crest, a chariot. ⏎  ⏎ Its trim is blue.

### dic\_robot\_SV262BDKN\_Z\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b016`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b016\]
> JP (źródło tłumaczenia): 　Sv-262Baの空中騎士団ザオ・ユッシラ搭乗機。 ⏎ 　機体上面には空中騎士団の紋章と家紋である車輪をかたどった意匠が施されている。 ⏎ 　カラーリングのラインは紫。
> EN (odniesienie oficjalne, NIE polski): Aerial Knight Xao Jussila's personal Sv-262Ba. ⏎  ⏎ It bears a design with the crest of the Aerial Knights and his family crest, a chariot. ⏎  ⏎ Its trim is purple.

### dic\_robot\_SV262BDKN\_W\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b018`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b018\]
> JP (źródło tłumaczenia): 　星の歌の力でシグル＝バレンスを通じて操られたSv-262Ba。 ⏎ 　機体性能は通常の機体と変わらないが、カラーリングが光学ステルスシステムにより、白色に変更されている。
> EN (odniesienie oficjalne, NIE polski): An Sv-262Ba controlled by the Sigur Berrentz via the power of the Star Song. ⏎  ⏎ Its capabilities are equal to standard models, but the optical stealth system has colored it monochrome.

### dic\_robot\_SV262HDKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01a`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b01a\]
> JP (źródło tłumaczenia): 　Sv-262の指揮官機。 ⏎ 　空中騎士団のエースであり、「ダーウェントの白騎士」の異名を持つキース・エアロ・ウィンダミアの乗機。 ⏎ 　バトロイド形態時の頭部は特徴的なセンサー形状を持つ。 ⏎ 　ウィンダミア王家に由来する高純度フォールド・クォーツの搭載により、通常比１３０％の推力でのオーバーブーストが可能。 ⏎ 　カラーリングは濃紺色をベースに金色のラインが施されている。
> EN (odniesienie oficjalne, NIE polski): A commander-model Sv-262. ⏎  ⏎ The personal fighter of the ace of the Aerial Knights, Keith Aero Windermere, the White Knight of Derwent. ⏎  ⏎ It has a distinctly-shaped sensor module on its head in Battroid Mode.  ⏎  ⏎ With the high-purity Fold Quartz provided by the Windermerian royal family directly, it is able to overboost to 130% of its normal thrust. ⏎  ⏎ It has a dark blue color scheme with golden trim.

### dic\_robot\_SV262HDKN\_R\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01c`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b01c\]
> JP (źródło tłumaczenia): 　ロイドが操るSv-262Hs。 ⏎ 　搭載されているフォールド・クォーツは、先王から譲り受けた王家由来の物。元々は一つの塊であったが、二つに砕けた事でキース機と分け合っている。 ⏎ 　カラーリングは、ロイドが精神制御した部隊のSv-262Baと同じく白色をベースとし、そこに金色のラインが施されている。
> EN (odniesienie oficjalne, NIE polski): An Sv-262Hs controlled by Roid.  ⏎  ⏎ The Fold Quartz installed in it was provided by the royal family during the previous king's reign. The quartz was provided in a single lump, but it was split so it could be divided up between both Keith and Roid's machines.  ⏎  ⏎ Its coloring is the same monochrome as the Sv-262Ba models controlled mentally by Roid, but with golden lines.

### dic\_robot\_SGLBRNS\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b01e`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b01e\]
> JP (źródło tłumaczenia): 　プロトカルチャーの遺産の一つである巨大艦。 ⏎ 　ブリージンガル球状星団各地に出現したプロトカルチャーの遺跡と連動する事で「歌」を拡散させる力を持つ。 ⏎ 　この形態は「星の歌い手」によって解放されたモードで、プロトカルチャーの遺産「鳥の人」に似たフォルムを持つ。 ⏎ 　中枢に置かれた神殿によって「星の歌」の力を増幅し、周囲に次元断層を発生させる。この次元断層は、敵からの攻撃を遮断するバリアとしても機能する。
> EN (odniesienie oficjalne, NIE polski): An enormous ship which is a relic of the Protoculture. ⏎  ⏎ It is able to connect to several Protoculture ruins across the Brisingr Globular Cluster to spread the power of song. ⏎  ⏎ This form is specifically unlocked by the Singer of the Stars, and is similar in form to another legacy of the Protoculture, the "Bird Human". ⏎  ⏎ The temple situated in the core is able to amplify the power of the Star Song, manifesting a dimensional fault around the ship. This dimensional fault also serves as a barrier to shield the ship from enemy attack.

### dic\_robot\_WNDBTLSP\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b020`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b020\]
> JP (źródło tłumaczenia): 　ウィンダミア王国に所属する砲撃艦。 ⏎ 　各部砲塔からビームを発射する。
> EN (odniesienie oficjalne, NIE polski): A gunship used by the Kingdom of Windermere. It fires beams from its various gun turrets.

### dic\_robot\_RRAZ\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b022`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b022\]
> JP (źródło tłumaczenia): 　ゼロ（枢木スザク）の専用ＫＭＦ。 ⏎ 　ラクシャータ率いる私設研究機関パール・パーティーが、統合打撃装甲騎計画の一環として建造した機体。元々は神聖ブリタニア帝国のナイトメア技術を研究するためにロイドが残した資料を基に再現されたが、ラクシャータの持つ技術も加えられたため、紅蓮聖天八極式と同等のスペックを持つに至った。 ⏎ 　シュナイゼルの意向により、ゼロの搭乗機としてカラーリングは黒と紫で塗り上げられた。機体名は開発機体コードからゼロが名付けたもの。高い戦闘力を誇るが、過剰な武力として使用は控えられる事となった。
> EN (odniesienie oficjalne, NIE polski): Zero's (which is to say, Suzaku Kururugi's) personal KMF. ⏎  ⏎ A KMF designed by Rakshata's private foundation, the Pearl Party, for the Joint Strike Knights Program. It is based on designs from Lloyd's research on the Holy Britannian Empire's Knightmare technology, but with the addition of Rakshata's know-how, it operates on par with the Guren S.E.I.T.E.N. Eight Elements. ⏎  ⏎ With Schneizel's approval, Suzaku-Zero had it repainted into a black and purple color scheme for his personal use. Zero named the unit himself based on its development codename. It is extremely powerful, but Zero elected not to use it too aggressively. ⏎ 

### dic\_robot\_GKEK\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b024`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b024\]
> JP (źródło tłumaczenia): 　指揮官用の複座式大型ＫＭＦ（ナイトメアフレーム）。 ⏎ 　超合集国の世界科学委員会会長ラクシャータとその私設研究機関パール・パーティーによって開発された。 ⏎ 　かつてルルーシュが搭乗したガウェイン、蜃気楼の流れを汲む。 ⏎ 　本来、電子戦闘用の機体であった「月虹影」に、ルルーシュが最前線で戦えるようガウェインなどの大型ナイトメアフレームの技術を転用した脚部、そして、多くの武装を実装して「月虹影帥（げっこうえい すい）」として完成した。 ⏎ 　装備は統合打撃装甲騎計画によって得られた技術を盛り込んであり、防御機構「絶対守護領域」だけではなく、超拡散構造相転移重砲（通称：真ゼロビーム）やハドロンブラスターなどを備える。
> EN (odniesienie oficjalne, NIE polski): A large dual-seat KMF (Knightmare Frame) for commander-use. ⏎  ⏎ It was jointly developed by Rakshata, as Chairman of the United Federations of Nations' Scientific Committee, and by her own private foundation, the Pearl Party. ⏎  ⏎ This KMF is considered to be part of the same development line as the Gawain and the Shinkiro, which were also piloted by Lelouch. The Gekkoei was intended to be an electronic warfare unit, but since Lelouch needed to be on the front lines, it was equipped with leg segments developed from the Gawain line and its arsenal was expanded, becoming the Gekkoei Sui. ⏎  ⏎ It has a full loadout of offensive weaponry from the technological resources of the Joint Strike Knights Program, including the Diffusion Structure Phase Transition Cannon, dubbed the Absolute Zero Beam, and the Hadron Blaster.

### dic\_robot\_RRSN\_WFG\_00\_0

Adres: `dic\_text\_robot/014d369b:9aa0b026`

> \[BRAK PL: dic\_text\_robot/014d369b:9aa0b026\]
> JP (źródło tłumaczenia): 　ランスロットsiNが拠点攻略・防衛用の追加兵装であるフレームコートを装備した状態。 ⏎ 　多数の敵との遠距離戦闘に向いている。 ⏎ 　火力と防御力が大幅に強化されている反面、機動力には劣るため、運動性能の高い敵に近接戦闘に持ち込まれると不利を強いられる。
> EN (odniesienie oficjalne, NIE polski): The Lancelot siN when equipped with a Frame Coat meant for defense and capturing positions. Well-adapted for long-range combat against multiple enemy units. ⏎  ⏎ However, while the equipment does greatly improve its offensive and defensive capabilities, it also reduces its mobility, making it disadvantageous in close-quarters combat against swift opponents.

### dic\_robot\_RRSN\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b001\]
> JP (źródło tłumaczenia): 　ＫＭＦランスロットシリーズの次世代機体。 ⏎ 　部隊を先陣で導く嚮導（きょうどう）兵器としての原点に立ち戻って設計された。 ⏎ 　最大の特徴は、ブリタニア系と黒の騎士団系の技術を融合させた二丁のC7-anti-materiel-V.A.R.I.S.（シーセブン・アンチマテリアル・ヴァリス）と、左肩から腕部にかけて装備されたコクーン。 ⏎ 　コクーンは物理防御壁にもなる巨大バッテリーで、稼働時間の大幅な延長を可能にした。 ⏎ 　エナジー・ウイングの出力も向上しており、ブレイズ・ルミナスによる防御がより強固となった他、エネルギーをブレード状にして放つ技の威力も増大した。 ⏎ 　また、フレームコートを装備する事で対多数の敵に対応する事も可能。
> EN (odniesienie oficjalne, NIE polski): A next-generation KMF in the Lancelot series. ⏎  ⏎ It was designed to return this model to its roots as a leading weapon, guiding the troops into the front line. ⏎  ⏎ Its most distinctive features are the dual C7-anti-materiel-VARIS rifles, a fusion of Britannian and Black Knights technology, and the Cocoon mounted on the left shoulder. ⏎  ⏎ The Cocoon is a large battery that also doubles as a physical shield, providing a significant increase in operational time. ⏎  ⏎ The output of the energy wings has been increased, which in turn improved the defensive power of the Blaze Luminous, as well as the cutting power of its energy blades. ⏎  ⏎ Furthermore, the Lancelot siN can equip the Frame Coat, a device designed for combat against multiple enemy units.

### dic\_robot\_GRES\_FMH\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b003`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b003\]
> JP (źródło tłumaczenia): 　紅蓮特式が、拠点攻略・防衛用の追加兵装であるフレームコートを装備した状態。 ⏎ 　多数の敵との遠距離戦闘に向いている。 ⏎ 　防御面での機能の拡充も図られ、輻射障壁は機体全面への展開が可能となっている。 ⏎ 　攻撃力・防御力の両面が大幅に強化されている反面、機動力や運動性能は低下するため、一対一の戦闘には向いていない場合もある。
> EN (odniesienie oficjalne, NIE polski): The Guren Type Special when equipped with a Frame Coat meant for defense and capturing fortified positions. Well-adapted for long-range combat against multiple enemy units. As part of its enhanced defensive capabilities, it can also deploy a full-body radiation barrier. ⏎  ⏎ However, while the equipment does greatly improve its offensive and defensive capabilities, it also reduces its mobility and maneuverability, making it ill-suited for one-on-one combat in some cases.

### dic\_robot\_GRES\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b005`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b005\]
> JP (źródło tłumaczenia): 　ＫＭＦ紅蓮シリーズの次世代機体。 ⏎ 　これまでの紅蓮の特徴を継承しつつ、十分な補給環境下での運用を前提に開発され、エネルギー出力と消費率は前世代機に比べて１割ほど増大した。 ⏎ 　飛行システムには、ブリタニア系のフロートユニットの技術も取り入れた飛翔滑走翼改を採用し、機動力と旋回性能を大幅に向上させた。 ⏎ 　防御面での機能の拡充も図られ、輻射障壁は機体全面への展開が可能となった。 ⏎ 　輻射推進型自在可動有線式徹甲砲撃右腕部による輻射波動は、さらに威力を増して広範囲に放射可能となった他、輻射回転衝角防御壁をドリル状に展開して武装としても使用する。 ⏎ 　近接戦闘用の武器として、改良型スラッシュハーケンの複合誘導飛燕爪牙や短刀の試製一號熱斬刀なども装備している。 ⏎ 　また、フレームコートを装備する事で対多数の敵に対応する事も可能。
> EN (odniesienie oficjalne, NIE polski): A next-generation KMF in the Guren series. ⏎  ⏎ Inheriting the unique traits of its predecessors, this Guren was designed to be used in environments with adequate fuel supplies; for this reason, both its energy output and consumption have been increased by about 10% compared to the previous generation. ⏎  ⏎ It flies on Enhanced Glider Wings that incorporate Britannian Float Unit technology, sensibly improving mobility and turning performance. ⏎  ⏎ Its defensive functions have also been upgraded, with the Radiant Shield now able to fully cover the KMF. ⏎  ⏎ Its right arm built-in, armor-piercing, wired, free-moving Radiation Wave Surger has been enhanced to affect a wider area. Moreover, the defensive rotating radiation wave unit can also be deployed as a veritable drill and used as a piercing weapon. ⏎  ⏎ Additional close-ranged weapons include the Composite Guidance Hien Soga (improved Slash Harkens), as well as the Test-Model \#1 Heat Sword. ⏎  ⏎ Furthermore, the Guren Type Special can equip the Frame Coat, a device designed for combat against multiple enemy units.

### dic\_robot\_GEDB\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b007\]
> JP (źródło tłumaczenia): 　ジルクスタン王国の主力機動兵器。 ⏎ 　前後対称形状の機体構造を採用し、軌道修正や旋回時のロスを失くす事に成功した。 ⏎ 　専用のヘッドマウントディスプレイを装着して操縦を行い、コックピット内のモニターは緊急時用の簡易仕様で、視認性は低い。 ⏎ 　両腕から発射可能な近距離用のスラッシュハーケンの他、肩部には大型キャノン砲を備える。
> EN (odniesienie oficjalne, NIE polski): A mass-produced KMF of the Kingdom of Zilkhstan. ⏎  ⏎ By adopting an anteroposterior symmetrical design, the Ged Bakha virtually negates any time loss caused by course correction and turning. ⏎  ⏎ The pilot wears a special head-mounted display during operations; while there are monitors in the cockpit, they have been implemented for emergency-use only, providing extremely low visibility. ⏎  ⏎ In addition to arm-mounted Slash Harkens for short-range combat, this KMF is also equipped with a pair of large cannons, mounted on its shoulders.

### dic\_robot\_BTRD\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b009`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b009\]
> JP (źródło tłumaczenia): 　ジルクスタン王国のビトゥルがカスタムメイドで建造したＫＧＦ（ナイトギガフォートレス）。 ⏎ 　フロートシステムを、飛行ではなく本体の駆動系に割り振ることで結果的に陸上での機動力を上げている。主な武装は、尻尾にも見えるキュラ・ラ熱線、ドレッドノートハーケン、メッサー光波弾、対空ミサイルなど豊富。フロートシステムを応用して対象を捕まえるキャプチャーフィールドなども装備しており、機体性能は世界トップクラスを誇る。
> EN (odniesienie oficjalne, NIE polski): A new-generation KGF (Knight Gigafortress) of the Kingdom of Zilkhstan. ⏎  ⏎ It uses a Float System for mobility rather than flight. Its multitude of weapons includes the Cura-la Heat Ray mounted on its tail, Dreadnought Harkens, Messer laser-guided missiles, and anti-air missiles. It can also use its Float System to trap targets in a Capture Field. Its combat potential is absolutely top-of-the-line.

### dic\_robot\_NGSM\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b00b\]
> JP (źródło tłumaczenia): 　ジルクスタン国王シャリオの専用ＫＭＦ。 ⏎ 　身体の自由が利かないシャリオにとって自由に動かせる第二の身体とも呼べる。 ⏎ 　機体各部にフロートユニットを内蔵しており、高い反応速度と運動性能を持つ。専属の操縦者であるシャリオが薬物投与による強化措置を行って使用できるメギストスオメガモードは、各部のフロートユニットを限界まで作動させ、機体質量を最小限にする。その結果、残像が見えるほどの高速移動を可能とし、圧倒的な戦闘力を誇る。 ⏎ 　軟質金属の刃を用いたウルミ型の剣とアサルトライフルを主武装とし、近接戦闘を得意とする。
> EN (odniesienie oficjalne, NIE polski): The personal KMF of King Shalio of Zilkhstan. ⏎  ⏎ Since Shalio himself has limited mobility, the KMF functions as a second body that allows him to move freely—an important quality for a king of warriors. ⏎  ⏎ Float Units are mounted around the unit's body, giving it high reaction speed and mobility. ⏎ As Shalio is its sole pilot, he can have it administer performance-enhancing drugs to him. He can then push the unit into Megistos Omega Mode, using the Float Units to their full potential to minimize the unit's mass. This allows the unit to move so fast it leaves afterimages, making it an overwhelming force on the battlefield. ⏎  ⏎ It is armed with a lightweight urumi-shaped blade and an assault rifle, a ⏎ close-quarters-focused loadout.

### dic\_robot\_RED5\_00\_0

Adres: `dic\_text\_robot/014d369b:9b20b00d`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b00d\]
> JP (źródło tłumaczenia): 　ＭＪＰが開発した指揮汎用型アッシュ。 ⏎ 　ヒタチ・イズル専用のリーダー機。 ⏎ 　指揮管制機能の強化のため、アッシュの基本型となった汎用戦闘タイプのブルーワンをベースにしつつ、主計算機の改良などがなされた。 ⏎ 　主武装は複合武器の８９式Ｂ型荷電粒子砲（ＨＥＰビームキャノン）で、近接用のチェーンソー、射撃用のビームライフル、高威力のレールガンなどに使い分けが可能。 ⏎ 　武装バリエーションは豊富で、腕部に装着して複数の実弾やエレキガンを発射できる９０式重多目的複合砲ＨＭランチャーや、２門の砲を肩にマウントする９０式遠距離多目的複合砲ロングボウなどがある。
> EN (odniesienie oficjalne, NIE polski): An all-range capable multipurpose AHSMB developed by the MJP. ⏎  ⏎ This is a command unit designated for Izuru Hitachi. ⏎  ⏎ It's based on the multipurpose Blue 1, but with an improved processor to boost its command support features. ⏎  ⏎ Its strongest weapon is the compound Type 89 Variant B Charged Particle Cannon (AKA the HEP Beam Cannon). It is a highly versatile combat unit, equipped with a chainsaw for close combat, a beam rifle for shooting, and a railgun for bombardment. ⏎  ⏎ It has a number of loadouts, including a Type 90 "HM Launcher" Heavy Multitarget Compound Cannon on its arms that can fire both bullets and shock rounds, and a Type 90 "Longbow" Long Range Multitarget Compound Cannon mounted on its shoulders.

### dic\_robot\_RED5\_00\_1

Adres: `dic\_text\_robot/014d369b:9b20b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9b20b00e\]
> JP (źródło tłumaczenia): 　また、爆発的に上昇したイズルのハーモニックレベルに呼応して覚醒し、フルバーストモードに変形する。パイロットとアッシュの意識が混じり合って全能力が飛躍的に向上した結果、最終的には動かそうと思う前に機体が動くという圧倒的な反応速度を見せるまで進化した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ When Izuru's Harmonic Level spiked, it awakened and transformed into Full Burst Mode. The consciousnesses of the pilot and AHSMB began to merge, unlocking vastly improved performance. In this state, its reaction speed is unparalleled due to the unit taking action on the subconscious level, before the pilot is even consciously aware of their actions.

### dic\_robot\_BLU1\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b000\]
> JP (źródło tłumaczenia): 　ＭＪＰが開発した汎用全戦域対応型アッシュ。 ⏎ 　アサギ・トシカズ専用機。 ⏎ 　全アッシュの基本型となった機体で、前衛での近接格闘や中距離射撃に適している。 ⏎ 　武装交換を行えば遠距離戦闘も可能ではあるが、アサギの戦闘スタイルに合わせて瞬間加速力を重視したセッティングがなされている。 ⏎ 　多様な局面に対応した標準武装を持ち、日本刀タイプの８８式突撃刀アサルトブレードをはじめ、射撃用のビーム銃や格闘用の斧槍としても使える複合武器の８８式可変斧槍銃ガンハルバート、携行ミサイルランチャーの８７式高機動誘導弾マジックワンドなどを装備する。 ⏎ 　また、両腕に巻きつけた形で装備しているシールドでビームを受け流す事も出来る。
> EN (odniesienie oficjalne, NIE polski): An all-range capable multipurpose AHSMB developed by the MJP. ⏎  ⏎ The unit is designated for Toshikazu Asagi. ⏎  ⏎ It is the baseline model the entire AHSMB line is based on, and is equipped for frontline combat at close and mid-ranges. ⏎  ⏎ It is capable of altering its loadout for long-range combat, but its defaults are set to prioritize bursts of acceleration to suit Asagi's combat style. ⏎  ⏎ It carries a variety of equipment to handle different situations, starting with the basic Type 88 Assault Blade. It also carries a Type 88 Variable Hafted Axe Gun, or "Gun Halberd", that can convert into a beam gun for ranged combat or a poleaxe for close range, and a Type 87 "Magic Wand" High-Mobility Guided Missile Launcher. ⏎  ⏎ It is also capable of blocking beam weaponry with the shields mounted on each arm.

### dic\_robot\_BLU1\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b001\]
> JP (źródło tłumaczenia): 　ケレス大戦時には、大型レールガンの９０式重電磁加速砲イレイザーを装備した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ A large railgun called the Type 90 "Eraser" Heavy Electromagnetic Accelerator Cannon was added to its loadout for the Battle of Ceres.

### dic\_robot\_PUR2\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b002\]
> JP (źródło tłumaczenia): 　ＭＪＰが開発した広域戦術警戒管制型アッシュ。 ⏎ 　クギミヤ・ケイ専用機。 ⏎ 　データリンク機能によって常にチーム全機体のモニタリングができる仕様になっている。 ⏎ 　周囲の状況が把握できる三次元複合センサーや広域超分解能レーダー、母艦や偵察衛星とリンクした情報から、戦況における最適な行動パターンを算出する。 ⏎ 　また、多元電子支援機器を搭載しており、主計算機の２基と予備を合わせて最大１０機までのアッシュのデータ処理を代行することが可能となっている。 ⏎ 　一方で、戦闘能力は自衛できる最低限のレベルしか持ち合わせていない。 ⏎ 　被弾時には、９１式機動粒子防御機アクティブガーダーでシールドを発生させて衝撃を緩和させる。
> EN (odniesienie oficjalne, NIE polski): A wide-range strategic recon/control AHSMB developed by the MJP. ⏎  ⏎ The unit is designated for Kei Kugimiya. ⏎  ⏎ Its datalink allows it to continuously monitor every unit on the team. ⏎  ⏎ It is equipped with a 3D multisensor and a wide-area super-analytic radar to gather information from its surroundings. By combining this with data from ships and recon satellites, it can calculate the most effective courses of action based on battlefield conditions. ⏎  ⏎ It also mounts a multipurpose electronic support unit, two main processors, and enough subprocessors to manage the data of up to 10 AHSMB units simultaneously. ⏎  ⏎ However, its combat equipment is the bare minimum necessary to defend itself. ⏎  ⏎ It blunts the impact of incoming hits using a Type 91 "Active Guard" Mobile Particle Defense Unit. ⏎ 

### dic\_robot\_ROS3\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b004\]
> JP (źródło tłumaczenia): 　ＭＪＰが開発したアッシュの高機動遊撃型。 ⏎ 　イリエ・タマキ専用機。 ⏎ 　スピードに特化した機体で、艦艇に使われる動力部をブースターとして装備している。多重高加速偏向推進器と重力抑制機の搭載により、２０Ｇを超える加速力を誇る。 ⏎ 　大出力を制御するために主計算機は２基使われている。 ⏎ 　主武器は腰部に装備されたレンズと腕部から発射するビーム砲の８８式内蔵式重粒子砲や、ブースター部上面のコンテナと先端部から発射される８９式重粒子投射機メガビームランチャーなどがあり、他にも多様な誘導ミサイルを搭載する。 ⏎ 　その出力を活かし、他のアッシュを牽引する事も可能。
> EN (odniesienie oficjalne, NIE polski): A high mobility assault AHSMB developed by the MJP. ⏎  ⏎ The unit is designated for Tamaki Irie. ⏎  ⏎ It is specialized for speed, using a warship-class engine as a booster unit. It achieves upwards of 20 g of acceleration using a gravitational accelerator and g-suppressor. ⏎  ⏎ Two main processors are utilized to manage its tremendous output. ⏎  ⏎ Its main weapons include a Type 88 Internal Particle Cannon which incorporates a ⏎ chest-mounted lens and arm-mounted beam cannons, Type 89 "Mega Beam Launcher" Heavy Particle Emitter units embedded in the booster's wingtips, and missile containers mounted on the dorsal side of the booster. The unit can also fire volleys of guided missiles. ⏎  ⏎ Its thrust is strong enough to pull other AHSMBs behind it.

### dic\_robot\_GLD4\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b006\]
> JP (źródło tłumaczenia): 　ＭＪＰが開発した超遠距離支援砲撃型アッシュ。 ⏎ 　スルガ・アタル専用機。 ⏎ 　射撃に特化して開発され、頭部自体が高度な砲撃用センサーになっているのが特徴。 ⏎ 　砲撃と砲撃管制装置用の動力として、副機は４基搭載されている。 ⏎ 　基本兵装として、高位荷電粒子砲と輻射誘導光子共振式速射砲を装備しているが、アタッチメント部分にはＧＤＦとＭＪＰのほぼ全ての射撃用武器を装着できる。 ⏎ 　また、パープルツーとのリンクにより、視認不可能な超長距離の精密射撃も可能。
> EN (odniesienie oficjalne, NIE polski): A long-range support bombardment AHSMB developed by the MJP. ⏎  ⏎ The unit is designated for Ataru Suruga. ⏎  ⏎ It was developed as a gunner unit, and its entire head is a highly precise targeting sensor. ⏎  ⏎ It has four sub-engines to power its weapons and firing control systems. ⏎  ⏎ Its basic weaponry is a high energy charged particle cannon and a radiation-guided photon resonance rapid-fire cannon. However, it can mount almost any GDF or MJP ranged armament as external equipment. ⏎  ⏎ By linking up with Purple 2 and utilizing its sensor package, it is even capable of hitting targets far outside its own visual range.

### dic\_robot\_GLD4\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b007\]
> JP (źródło tłumaczenia): 　グランツェーレ都市学園防衛の際には、パープルツーと管制をつなげて宇宙から地上へ９０式超長距離狙撃用重集束ビーム砲フライシュッツによる狙撃を行い、ゲート攻防戦では、ゴディニオンの先端部と操作系統をリンクさせ、主砲をコントロールした。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During the attack on Glanzehre Cosmopolitan Academy, it linked with Purple 2 to fire a Type 90 "Freischütz" Extreme Range Heavy Focused Beam Cannon at the Earth's surface from space. During the gate assault, it interfaced with the Godinion's bow module and control systems and took over its main cannon.

### dic\_robot\_BRK6\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b008\]
> JP (źródło tłumaczenia): 　量産化を想定して開発された次世代汎用型アッシュ。 ⏎ 　クロキ・アンジュ専用機。 ⏎ 　ブルーワンからレッドファイブまでの戦闘データと、レッドファイブの機体を基に、生産性を考慮して、装甲形状や各部を簡略化している。 ⏎ 　各武装はユニット化され、短時間での整備と再出撃が可能。 ⏎ 　また、メンテナンスも自動化されており、運用に必要な人員の減少も図られた。 ⏎ 　多数の火器を装備可能で、９１式肩部短距離高機動誘導弾サイドアーム、９１式脚部多連装高機動誘導弾ブラックファイアなどの一斉発射により大火力を発揮する。
> EN (odniesienie oficjalne, NIE polski): A next-generation multipurpose AHSMB intended for mass-production. ⏎  ⏎ This unit was designated for Ange Kuroki. ⏎  ⏎ The unit incorporates combat data from all five earlier AHSMBs. It is based on Red 5, and it simplifies armor and many other features in the interest of easier mass production. ⏎  ⏎ Its weapons are modularized for rapid maintenance and redeployment. ⏎  ⏎ The unit's maintenance has also been automated to reduce staffing needs. ⏎  ⏎ It can equip a variety of armaments. The Type 91 "Sidearm" Shoulder-Mounted Short-Range High Mobility Guided Missile and Type 91 "Black Fire" Leg-Mounted Linked High Mobility Guided Missile systems can be combined for heavy focused firepower. ⏎ 

### dic\_robot\_LYNS\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b00a\]
> JP (źródło tłumaczenia): 　チームドーベルマンが搭乗する高機動多用途戦闘デバイス。 ⏎ 　アッシュ向けパーツのテスト機体として運用され、外宇宙科学と従来のアイオネス理論を融合させて開発された。 ⏎ 　アッシュと同様にジュリアシステムを搭載する。 ⏎ 　メイン武装は腕部側面のマウントに接続して使用するレールガンと副腕の近接格闘武器ビームフィンガー。
> EN (odniesienie oficjalne, NIE polski): A High-Mobility Multipurpose Device model piloted by Team Doberman. ⏎  ⏎ The units are used to test equipment intended for AHSMBs. Their development integrates extraterrestrial technology with the well-known principles of Ioness Theory. ⏎  ⏎ They are equipped with the same Juria System as AHSMBs. ⏎  ⏎ Their primary weapons are rapid-fire railguns mounted on the arms and the Beam Finger close-range melee weapon. ⏎ 

### dic\_robot\_LYNS\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b00b\]
> JP (źródło tłumaczenia): 　オペレーション・イーグルランデッドでは、腕部マウントに装備する格闘武器の８８式重突撃衝撃剣ツインクレイモアが使用された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ For Operation Eagle Landed, they were equipped with Type 88 "Twin Claymore" Heavy Assault Impact Blade units mounted on their arms for close combat.

### dic\_robot\_GDNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b00c\]
> JP (źródło tłumaczenia): 　ＭＪＰの大型機動戦闘空母。 ⏎ 　高出力機関の搭載によって強固なシールドを展開可能で、アッシュに使われる新型装甲の採用と合わせて高い防御力を誇る。 ⏎ 　艦体はモジュール構造で設計され、前部、ブリッジユニット、エンジンユニット、ウイングユニットなどへの各部分離が可能となっている。 ⏎ 　ウイングユニット下部にある二基のソーラーセイルを回転させることにより、太陽光を吸収して機体の推進エネルギーに変換することが出来る。 ⏎ 　艦前方には、チームラビッツの支援艦艇であるピット艦を搭載している。
> EN (odniesienie oficjalne, NIE polski): The MJP's large mobile battle carrier. ⏎  ⏎ Its high-output engine lets it deploy a powerful shield, on top of the same next-generation armor used by the AHSMBs, giving it a strong overall defense. ⏎  ⏎ The ship is divided into bow, bridge, engine, and wing modules that can separate individually. ⏎  ⏎ A pair of solar sails are mounted under the wing modules. These can be rotated to absorb sunlight and convert it into power. ⏎  ⏎ The pits, support craft for Team Rabbits' AHSMB units, are docked to the bow. ⏎ 

### dic\_robot\_MZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b00e\]
> JP (źródło tłumaczenia): 　ジアート専用の機動兵器。 ⏎ 　皇族のみに許された白の特殊機体色をまとう。 ⏎ 　運動性能や反応速度に優れており、近接格闘において天賦の才を持つジアートが操縦することで性能を最大限に発揮する。
> EN (odniesienie oficjalne, NIE polski): Jiart's personal mobile weapon. ⏎  ⏎ Its white coloring may only be used by the Wulgaru imperial family. ⏎  ⏎ Its mobility and response times are extremely high, and Jiart's skill in close combat allows him to use it to its full potential.

### dic\_robot\_MZIAT\_00\_1

Adres: `dic\_text\_robot/014d369b:9b60b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b00f\]
> JP (źródło tłumaczenia): 　パイロットの感情に応じて出力が向上するシステムが搭載されており、レッドファイブとの対戦時にはオーバーロードモードとなって激戦を繰り広げた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It is equipped with a system that increases output according to the pilot's emotional state. It transformed into Overlord Mode in the final duel with Red 5.

### dic\_robot\_MCLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9b60b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9b60b010\]
> JP (źródło tłumaczenia): 　ウルガル軍団長のクレイン専用機。 ⏎ 　機動力と加速力に特化した機体で、一撃離脱戦法を得意とする。 ⏎ 　右腕は巨大なクローになっており、両手両足にはビーム砲を内蔵している。 ⏎ 　クレイン指揮下の部隊の機体と同じくカラーリングはパープルを基調とする。
> EN (odniesienie oficjalne, NIE polski): Wulgaru commander Klein's personal mobile weapon. ⏎  ⏎ It focuses on speed and acceleration to carry out hit-and-run maneuvers. ⏎  ⏎ The unit's right arm has massive claws attached, and all four of its limbs contain embedded beam cannons. ⏎  ⏎ Klein's soldiers' units have been colored in his own purple.

### dic\_robot\_MCLIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b000\]
> JP (źródło tłumaczenia): 　後に敗北を経て、強化改造された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After its previous defeats, it has been enhanced.

### dic\_robot\_MLTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b001\]
> JP (źródło tłumaczenia): 　ウルガル軍団長のルティエル専用機。 ⏎ 　スピードを活かした一点集中の突破攻撃を得意とする。 ⏎ 　ビームを放つ事も出来る両翼を盾とし、両手に内蔵されたビーム砲を形状変化させたサーベルで近接格闘戦を展開する。 ⏎ 　ルティエル指揮下の部隊の機体と同じくカラーリングはイエローを基調とする。
> EN (odniesienie oficjalne, NIE polski): Wulgaru commander Lutiel's personal mobile weapon. ⏎  ⏎ It focuses on speed and is used for charging attacks. ⏎  ⏎ Its wing shields can also fire beams, and the beam cannons in its arms can become blades for close range combat. ⏎  ⏎ Lutiel's soldiers' units have been colored in her own yellow.

### dic\_robot\_MDLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b003`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b003\]
> JP (źródło tłumaczenia): 　ウルガル軍団長のドルガナ専用機。 ⏎ 　重攻撃型の機体で、正面突破による戦いを得意とする。 ⏎ 　大出力の砲火と圧倒的な装甲で攻防に優れながら、機動性も兼ね備えている。 ⏎ 　ドルガナ指揮下の部隊の機体と同じくカラーリングはレッドを基調とする。
> EN (odniesienie oficjalne, NIE polski): Wulgaru commander Dolgana's personal mobile weapon. ⏎  ⏎ It is a heavy assault unit specialized for direct combat. ⏎  ⏎ It has high weapons output and strong armor, as well as respectable mobility. ⏎  ⏎ Dolgana's soldiers' units have been colored in his own red.

### dic\_robot\_UMM\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b005`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b005\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、このグリーンのカラーリングはラダ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The green color scheme depicted represents Rada's division.

### dic\_robot\_UMM\_RADA\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b006\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes. ⏎ 

### dic\_robot\_UMM\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b007\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、このパープルのカラーリングはクレイン部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The purple color scheme depicted represents Klein's division.

### dic\_robot\_UMM\_CLIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b008\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes.

### dic\_robot\_UMM\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b009`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b009\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、このイエローのカラーリングはルティエル部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The yellow color scheme depicted represents Lutiel's division.

### dic\_robot\_UMM\_LTEL\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00a\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes. ⏎ 

### dic\_robot\_UMM\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00b\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、このレッドのカラーリングはドルガナ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The red color scheme depicted represents Dolgana's division.

### dic\_robot\_UMM\_DLGN\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00c\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes. ⏎ 

### dic\_robot\_UMM\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00d`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00d\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、このオレンジのカラーリングはルメス部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The orange color scheme depicted represents Lumes' division.

### dic\_robot\_UMM\_RMES\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00e\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes. ⏎ 

### dic\_robot\_UMM\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b00f\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器。 ⏎ 　ＧＤＦの既存兵器を凌駕する性能で、ウルガルの脅威を知らしめた存在。 ⏎ 　手のひらに内蔵するビーム砲と、腕部のクローをまとめて形成するソードで戦う。 ⏎ 　所属する部隊によって、ボディの配色と機体性能が異なり、この水色のカラーリングはジアート部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru biological mobile weapon. ⏎  ⏎ It outperforms the GDF's existing technology in all respects and clearly demonstrated the extent of the Wulgaru threat. ⏎  ⏎ It can fire a beam cannon from its palm and the claws on its hand can join into a sword blade. ⏎  ⏎ Its outer coloring varies according to which Wulgaru army group a unit is affiliated with. The light blue color scheme depicted represents Jiart's division. ⏎ 

### dic\_robot\_UMM\_ZIAT\_00\_1

Adres: `dic\_text\_robot/014d369b:9ba0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b010\]
> JP (źródło tłumaczenia): 　機体は兵士と共にクローンで造られ、優秀な遺伝子を基に量産されている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ This mobile weapon is cloned together with its pilot. They are mass-produced using strong genes. ⏎ 

### dic\_robot\_UAM\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ba0b011`

> \[BRAK PL: dic\_text\_robot/014d369b:9ba0b011\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このグリーンのカラーリングはラダ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The green depicted represents Rada's division.

### dic\_robot\_UAM\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b000\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このパープルのカラーリングはクレイン部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The purple depicted represents Klein's division.

### dic\_robot\_UAM\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b002\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このイエローのカラーリングはルティエル部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The yellow depicted represents Lutiel's division.

### dic\_robot\_UAM\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b004\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このレッドのカラーリングはドルガナ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The red depicted represents Dolgana's division.

### dic\_robot\_UAM\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b006\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このオレンジのカラーリングはルメス部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The orange depicted represents Lumes' division.

### dic\_robot\_UAM\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b008\]
> JP (źródło tłumaczenia): 　ウルガルの生体機動兵器の強化タイプ。 ⏎ 　一般部隊機より機体性能がアップし、ビームの出力もより強大になった。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、この水色のカラーリングはジアート部隊のもの。
> EN (odniesienie oficjalne, NIE polski): An improved model of the Wulgaru's biological mobile weapon. ⏎  ⏎ Its mobility is improved over the regular model. Its beam output is also increased. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The light blue depicted represents Jiart's division.

### dic\_robot\_UBS\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b00a\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このグリーンのカラーリングはラダ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The green depicted represents Rada's division.

### dic\_robot\_UBS\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b00c\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このパープルのカラーリングはクレイン部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The purple depicted represents Klein's division.

### dic\_robot\_UBS\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b00e\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このイエローのカラーリングはルティエル部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The yellow depicted represents Lutiel's division.

### dic\_robot\_UBS\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b010\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このレッドのカラーリングはドルガナ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The red depicted represents Dolgana's division.

### dic\_robot\_UBS\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b012\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このオレンジのカラーリングはルメス部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The orange depicted represents Lumes' division.

### dic\_robot\_UBS\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b014`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b014\]
> JP (źródło tłumaczenia): 　ウルガル各軍団の旗艦となる大型母艦。 ⏎ 　荷電粒子砲を容易に弾くほどの防御シールドを備える。 ⏎ 　多数の機動兵器を搭載することが可能。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、この水色のカラーリングはジアート部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A large mothership that serves as the flagship of its respective Wulgaru army. ⏎  ⏎ It's equipped with a defensive shield that can easily deflect a blast from a charged particle cannon. ⏎  ⏎ It can carry a large number of mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The light blue depicted represents Jiart's division.

### dic\_robot\_UMS\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b016`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b016\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このグリーンのカラーリングはラダ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The green depicted represents Rada's division.

### dic\_robot\_UMS\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9be0b018`

> \[BRAK PL: dic\_text\_robot/014d369b:9be0b018\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このパープルのカラーリングはクレイン部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The purple depicted represents Klein's division.

### dic\_robot\_UMS\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b000\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このイエローのカラーリングはルティエル部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The yellow depicted represents Lutiel's division.

### dic\_robot\_UMS\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b002\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このレッドのカラーリングはドルガナ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The red depicted represents Dolgana's division.

### dic\_robot\_UMS\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b004\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このオレンジのカラーリングはルメス部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The orange depicted represents Lumes' division.

### dic\_robot\_UMS\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b006\]
> JP (źródło tłumaczenia): 　ウルガルの中型艦艇。 ⏎ 　攻撃力と防御力だけでなく、機動性もバランスよく兼ね備えている。 ⏎ 　一般部隊機動兵器の母艦としても機能する。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、この水色のカラーリングはジアート部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A Wulgaru mid-size craft. ⏎  ⏎ It's a well-balanced unit that boasts respectable mobility in addition to its impressive offense and defense. ⏎  ⏎ It can also function as a carrier for squads of infantry-class mobile weapons. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The light blue depicted represents Jiart's division.

### dic\_robot\_UBF\_RADA\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b008\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このグリーンのカラーリングはラダ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The green depicted represents Rada's division.

### dic\_robot\_UBF\_CLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b00a\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このパープルのカラーリングはクレイン部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The purple depicted represents Klein's division.

### dic\_robot\_UBF\_LTEL\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b00c\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このイエローのカラーリングはルティエル部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The yellow depicted represents Lutiel's division.

### dic\_robot\_UBF\_DLGN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b00e\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このレッドのカラーリングはドルガナ部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The red depicted represents Dolgana's division.

### dic\_robot\_UBF\_RMES\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b010\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、このオレンジのカラーリングはルメス部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The orange depicted represents Lumes' division.

### dic\_robot\_UBF\_ZIAT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b012\]
> JP (źródło tłumaczenia): 　ウルガル一般兵が搭乗する戦闘機。 ⏎ 　中級兵用、上級兵用の機体も存在し、搭乗者の等級が高いほど機体の形状は複雑になる。 ⏎ 　ボディの配色は他のウルガル兵器同様、所属する部隊によって異なり、この水色のカラーリングはジアート部隊のもの。
> EN (odniesienie oficjalne, NIE polski): A fighter for use by Wulgaru infantry. ⏎  ⏎ Models for advanced and elite soldiers also exist. The higher the pilot's rank, the more complex the unit's construction. ⏎  ⏎ Like all Wulgaru weaponry, its outer coloring varies according to the army group the unit is assigned to. The light blue depicted represents Jiart's division.

### dic\_robot\_JDJGR\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b014`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b014\]
> JP (źródło tłumaczenia): 　オオタキファクトリーの社長・大滝が開発したロボット。 ⏎ 　開発当初は有人機であったが、怪獣との戦闘を経て、AI搭載型の無人機に改修された。それを機に搭載された対話型インターフェースには、有川ユンの開発したコミュニケーション支援ＡＩ「ナラタケ」から生まれた「ユング」が組み込まれている。 ⏎ 　怪獣アンギラスとの戦いで手に入れたツノを使用した「アンギラスの槍」を武器に戦う。
> EN (odniesienie oficjalne, NIE polski): A robot built by Otaki, the CEO of the Otaki Factory. Originally a manned robot, it was converted into an AI autonomous unit as the battles with kaiju went on. The speech interface loaded into it is Yung, an instance of the communication assistance AI Naratake developed by Yun Arikawa. ⏎  ⏎ He fights with the Lance of Anguirus, a weapon made of the horn looted in the battle with the kaiju Anguirus.

### dic\_robot\_JDJGR\_00\_1

Adres: `dic\_text\_robot/014d369b:9c20b015`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b015\]
> JP (źródło tłumaczenia): 　ゴジラとの最終決戦では飛行ユニットを装備したが、一度は墜落して機能を停止する。 ⏎ 　その後、ペロ２が発見した「ジェットジャガーを最強にするプロトコル」によってペロ２と一体化し「ジェットジャガーＰＰ」として巨大化を果たす。激闘の末、突如発生した爆発の中ゴジラとともに消失した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ He was equipped with a flight pack for the final battle with Godzilla, but fell, shutting down in the process. ⏎  ⏎ Then the protocol to make Jet Jaguar invincible, unearthed by Pelops II, caused him to merge with Pelops II and transform into the gigantic Jet Jaguar PP. In the climactic battle, he disappeared with Godzilla in a sudden explosion.

### dic\_robot\_GZLULTM\_00\_0

Adres: `dic\_text\_robot/014d369b:9c20b016`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b016\]
> JP (źródło tłumaczenia): 　海から上陸してきた超巨大生命体。 ⏎ 　これまでに三度の形態変化を経ており、現在も成長を続けている。 ⏎ 　逃尾市に古くから伝わる伝承から「ゴジラ」と命名された。 ⏎ 　大量の紅塵を発生させ、周囲の環境に大きな影響を与える。 ⏎ 　全身が鎧のような外皮に覆われており、背ビレが大きく発達している他、形態変化によって二足歩行となった。 ⏎ 　背ビレの発光と共に複数のリングを発生させ、それらを収縮させた原子ビームを発射して東京を火の海へと変えた。
> EN (odniesienie oficjalne, NIE polski): A gargantuan organism that came from the ocean. ⏎  ⏎ It has already evolved through three distinct forms and continues to grow. It has been told of since ancient times in Nigashio as "Gojira". ⏎  ⏎ It emanates Red Dust in huge quantities, warping the space and landscape around its body. Its entire body is covered in thick skin as hard as any armor. Its back fins have grown to a substantial size, and it can now walk upright on its hind legs. ⏎  ⏎ When its back fins glow, it creates multiple rings and fires a compressed Heat Ray that can bathe cities—such as Tokyo—in flame.

### dic\_robot\_GZLULTM\_00\_1

Adres: `dic\_text\_robot/014d369b:9c20b017`

> \[BRAK PL: dic\_text\_robot/014d369b:9c20b017\]
> JP (źródło tłumaczenia): 　世界を破局へ導く「特異点」と考えられている。 ⏎ 　ジェットジャガーとの激闘の末、突如発生した爆発の中青い結晶を残し消失した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It is believed to be the Singular Point that will bring about the Catastrophe. ⏎  ⏎ In a climactic battle with Jet Jaguar, it disappeared in a sudden explosion, leaving blue crystals behind.

### dic\_robot\_KMNGA\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b000\]
> JP (źródło tłumaczenia): 　海辺の造船所に現れた怪獣。 ⏎ 　８本の脚を持ったクモを想起させる見た目から、工場の作業員が使用していた呼び名がそのまま定着した。 ⏎ 　他の個体と群生する習性を持つ他、身体を切断しても活動を続け、再生する能力が特徴。 ⏎ 　口から粘液を糸状にして放出し、人間に襲い掛かる。
> EN (odniesienie oficjalne, NIE polski): A kaiju species that appeared at a shipyard on the coast. ⏎  ⏎ It was named by the workers on site for its arachnid appearance, and the name went into mainstream use. ⏎  ⏎ It is capable of working with others of its species, and any part of it severed from its body can continue moving and even regenerate. It attacks humans by spitting sticky string from its mouth.

### dic\_robot\_LADON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b002\]
> JP (źródło tłumaczenia): 　世界各地に現れた怪獣。 ⏎ 　逃尾市に現れた最初の個体の細胞内から放射性物質ラドンが発見された事に由来して命名された。 ⏎ 　翼竜のケツァルコアトルスと外見が似ていると指摘されているが、胃に対応する器官が見つからず、これまでの地球上の生物とは別物と考えられている。 ⏎ 　電波を発してコミュニケーションを取っている事が判明している他、海中から出現したという報告も確認された。 ⏎ 　紅塵の広がりと共に出現するようになったタイプは逃尾に現れたものとは体色が異なっている。
> EN (odniesienie oficjalne, NIE polski): A kaiju species that appeared around the world. The element radon was discovered in the cells of the individual that initially appeared in Nigashio, leading to its name. ⏎  ⏎ It was observed that it resembles the mythical Quetzalcoatlus. It contains no organ that could serve the function of a stomach, so it's believed to be of a separate kind altogether from any Earthly life-form. ⏎  ⏎ It was later found that they communicate using radio signals and that they come from beneath the ocean. The ones that seemed to follow the spread of Red Dust are a different color from the Nigashio specimen.

### dic\_robot\_DYNZNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b004\]
> JP (źródło tłumaczenia): 　ダイナソルジャー、ダイナウイング、ダイナストライカー、ダイナダイバーの４機が合体した巨大ロボット。 ⏎ 　初めて姿を現した時にはガウマが持っていた副葬品の竜のオブジェから招喚されたが、以降は４機に分離した。 ⏎ 　構成する各機は普段は手の平サイズになっており、蓬、夢芽、暦、ガウマがそれぞれ所有している。「アクセスモード」の掛け声で巨大化が可能。 ⏎ 　各機の合体の仕方を変える事で合体強竜ダイナレックスとなる事も出来る。 ⏎ 　戦闘開始時の合図は、ガウマが発する「ダイナゼノン・バトルゴー！」。 ⏎ 　両肩に装備されたキャノン砲・ペネトレーターガンやバーストミサイル等の火器の他、肉弾戦で怪獣と戦う。
> EN (odniesienie oficjalne, NIE polski): A giant robot formed by the combination of Dyna Soldier, Dyna Wing, Dyna Striker, and Dyna Diver. ⏎  ⏎ It was first summoned through the dragon statue left as an offering in Gauma's sarcophagus. Afterward, it divided into its four components. ⏎  ⏎ The component machines are normally small enough to fit in the palm of a hand. They are kept with Yomogi, Yume, Koyomi, and Gauma, respectively. ⏎  ⏎ The four components can also combine in a different configuration to form Super Dragon Dynarex. ⏎  ⏎ When it enters combat, Gauma calls out "Dynazenon! Battle, Go!" When it's not firing its plethora of weapons, including the Burst Missiles and the shoulder-mounted Penetrator Gun cannons, it beats up kaiju hand-to-hand.

### dic\_robot\_GRID\_KT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b006\]
> JP (źródło tłumaczenia): 　ナイトが巨人に変身した姿。 ⏎ 　身軽さを活かした格闘戦を行い、多彩な武器を使って怪獣と戦う。 ⏎ 　光輪を投げつけるグリッドナイトサーキュラー、右腕から光線を放つ必殺技・グリッドナイトストーム等の技を持つ。
> EN (odniesienie oficjalne, NIE polski): The giant form Knight transforms into. He fights kaiju using agile maneuvers and a variety of weapons. ⏎  ⏎ He wields a number of offensive techniques, including throwing a ring of light called the Gridknight Circular and firing a beam from his right arm called the Gridknight Storm.

### dic\_robot\_GRID\_KT\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b007\]
> JP (źródło tłumaczenia): 　カイゼルグリッドナイトへの合体時には、その胴体となる。 ⏎ 
> EN (odniesienie oficjalne, NIE polski):  ⏎ He forms the torso of Kaiser Gridknight.

### dic\_robot\_KZLGRID\_KT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b008\]
> JP (źródło tłumaczenia): 　グリッドナイト、ダイナゼノン、ゴルドバーンが合体した姿。 ⏎ 　余剰エネルギーにより、両翼からは光のマントが形成される。 ⏎ 　超巨大な光輪で敵を斬り裂くカイゼルナイトサーキュラーの他、右肩のダイナミックキャノンから光線を放つ必殺技・レックスグリッドファイヤー等で戦う。
> EN (odniesienie oficjalne, NIE polski): The combined form of Gridknight, Dynazenon, and Goldburn. ⏎  ⏎ The combination's excess energy is vented from the wings in the form of a luminous cape. ⏎  ⏎ They can tear through a kaiju with a massive light ring called the Kaiser Knight Circular and fire a beam from the Dynamic Cannon on their right shoulder, a maneuver dubbed Rex Grid Fire.

### dic\_robot\_SLBNDS\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00a\]
> JP (źródło tłumaczenia): 　物体を浮遊させる力を持つ怪獣。 ⏎ 　背中の振動波器官からカオスブリンガーと呼ばれる光の粒子を放つ事でビルや車を空中に浮き上がらせる。 ⏎ 　首を蛇のように伸ばし、剣状に伸びた鼻先で敵を攻撃する他、口から稲妻のような光線を放つ。
> EN (odniesienie oficjalne, NIE polski): A kaiju with the power to levitate matter. Chaosbringers, particles of light emanated from the vibrating organ on its back, cause buildings and cars to float up into the air. ⏎  ⏎ It can extend its neck like a snake, which allows it to strike with its blade-like snout. It can also emit lightning-like beams from its mouth.

### dic\_robot\_SLBNDS\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00b\]
> JP (źródło tłumaczenia): 　ダイナレックスの必焼大火炎レックスロアーで倒された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It was defeated by Dynarex's Great Conflagration: Rex Roar.

### dic\_robot\_GLJOM\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00c\]
> JP (źródło tłumaczenia): 　ワープ能力を持つ怪獣。 ⏎ 　怪獣優生思想のジュウガのインスタンス・ドミネーションにより巨大化した。 ⏎ 　額のツノと背中の羽にある振動波器官から光の粒子・カオスブリンガーを放つ事で近距離を瞬間移動する。 ⏎ 　胸部から光線を放つ。
> EN (odniesienie oficjalne, NIE polski): A kaiju with the power of teleportation. Kaiju Club member Juuga used Instance Domination to make it giant-sized. ⏎  ⏎ The vibrating organs on its jaw horns and its wings release particles of light called Chaosbringers that allow it to move short distances instantaneously. It can fire beams from its chest.

### dic\_robot\_GLJOM\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00d`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00d\]
> JP (źródło tłumaczenia): 　羽を広げなければワープが出来ない事を暦が見抜き、ダイナソルジャーウイングコンバインが動きを封じた後、ガウマの乗るダイナダイバーによって倒された。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Yomogi realized that it needs to spread its wings to teleport. He and Yume used Dyna Soldier Wing Combine to immobilize it, and then Gauma finished it off from the Dyna Diver.

### dic\_robot\_BLBAIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00e\]
> JP (źródło tłumaczenia): 　物体を押し潰す能力を持つ怪獣。 ⏎ 　怪獣優生思想のオニジャとムジナによって操られた。 ⏎ 　振動波器官からカオスブリンガーを放つ事で重力を増大させる。 ⏎ 　タテガミのような触手や翼から光線を放つ他、ドリルのように回転するツノを使った攻撃も行う。
> EN (odniesienie oficjalne, NIE polski): A kaiju with the power to flatten physical objects. ⏎  ⏎ It was dominated by the Kaiju Club members Onija and Mujina. ⏎  ⏎ It emanates Chaosbringers from its vibrating organ to amplify the effect of gravity. It can also shoot beams from the tentacles forming its mane and from its wings, or attack by making its horns spin like drills.

### dic\_robot\_BLBAIN\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b00f`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b00f\]
> JP (źródło tłumaczenia): 　一度はダイナゼノンを追い詰めるが、グリッドナイトの登場により撤退する。 ⏎ 　その後、再び街に現れるが、ダイナゼノンとグリッドナイトの連携に敗れた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It nearly defeated Dynazenon at first before Gridknight's arrival forced it to retreat. ⏎  ⏎ It then attacked the city again, but Dynazenon and Gridknight defeated it by working together.

### dic\_robot\_GBZORG\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b010\]
> JP (źródło tłumaczenia): 　物体を波状化させる能力を持つ怪獣。 ⏎ 　怪獣優生思想のジュウガのインスタンス・ドミネーションにより巨大化した。 ⏎ 　背面の振動波器官や両手と口からカオスブリンガーを放出し、鉄塔を屈曲させたり地面を液状化させたりする。 ⏎ 　両手と口から発生させた重力レンズから、ビームに似た強力な衝撃波を放つ。
> EN (odniesienie oficjalne, NIE polski): A kaiju with the power to liquefy matter. ⏎  ⏎ Kaiju Club member Juuga used Instance Domination to make it giant-sized. ⏎  ⏎ It scatters Chaosbringers from the vibrating organ on its back which can warp buildings or turn the ground into liquid. By forming gravity lenses from its mouth and hands, it can fire a deadly shockwave that acts like a beam.

### dic\_robot\_GBZORG\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b011`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b011\]
> JP (źródło tłumaczenia): 　グリッドナイト達の足場を呑み込んで動きを封じるが、ゴルドバーンによって形勢を逆転され、合体したカイゼルグリッドナイトの前に敗れ去った。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It trapped Gridknight and Dynazenon's machines by liquefying the ground beneath their feet, but Goldburn's arrival turned the tide, and the newly-formed Kaiser Gridknight overpowered it.

### dic\_robot\_GGYRA\_1\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b012`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b012\]
> JP (źródło tłumaczenia): 　シズムが体内に宿していた怪獣にインスタンス・ドミネーションして巨大化させた怪獣。 ⏎ 　背中にある振動波器官からカオスブリンガーを放つ事で対象を弾き飛ばす。
> EN (odniesienie oficjalne, NIE polski): The kaiju within Sizumu's body, enlarged by Instance Domination. ⏎  ⏎ The Chaosbringers from the vibrating organ on its back send its target flying away.

### dic\_robot\_GGYRA\_2\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b014`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b014\]
> JP (źródło tłumaczenia): 　シズムが体内に宿していた怪獣にインスタンス・ドミネーションして巨大化させた怪獣が、怪獣優生思想のオニジャ、ジュウガ、ムジナを取り込む事で進化を遂げた姿。 ⏎ 　背中にある振動波器官からカオスブリンガーを放つ事で対象を弾き飛ばす。 ⏎ 　ツノから光線を放つ他、口や胸部から強力なビームを発射する。
> EN (odniesienie oficjalne, NIE polski): The kaiju within Sizumu's body, enlarged by Instance Domination and evolved further by absorbing the other Kaiju Club members, Onija, Juuga, and Mujina. ⏎  ⏎ The Chaosbringers from the vibrating organ on its back send its target flying away. In addition, it can emit rays from its horns and powerful beams from its mouth and chest.

### dic\_robot\_GGYRA\_2\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b015`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b015\]
> JP (źródło tłumaczenia): 　圧倒的なパワーによってカイゼルグリッドナイトを追い詰めるが、合体を解除した蓬の怪獣使いとしての力で隙を作られ、ダイナゼノンとグリッドナイトの猛攻を受けて敗北した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Its overwhelming power was nearly too much for Kaiser Gridknight, but Yomogi separated and used his kaiju user abilities to open it up for Dynazenon and Gridknight to push back their assault.

### dic\_robot\_W\_DYNZNON\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b016`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b016\]
> JP (źródło tłumaczenia): 　目に見えない程の小さなマイクロサイズの怪獣が試作型ダイナゼノンを乗っ取った状態。 ⏎ 　分離やダイナレックスへの再合体機構は搭載されていない。 ⏎ 　怪獣優生思想がインスタンス・ドミネーションで全身の怪獣を介して操縦する。
> EN (odniesienie oficjalne, NIE polski): The Dynazenon prototype, when hijacked by a microscopic kaiju, is smaller than the eye can see. ⏎  ⏎ It isn't equipped with the ability to separate, nor to reconfigure its components into Dynarex. ⏎  ⏎ The Kaiju Club uses Instance Domination to control the entire machine through the kaiju.

### dic\_robot\_MFCARDNT\_00\_0

Adres: `dic\_text\_robot/014d369b:9c60b018`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b018\]
> JP (źródło tłumaczenia): 　東京都下の八神市の地下で建造されていた機動要塞都市。 ⏎ 　甲板のドーム内に八神市とその周辺の街が収容されている。 ⏎ 　超長距離移民船と同様の機構を持ち、居住区は完全に独立した都市として機能する。 ⏎ 　主機関であるシステム・ニーラカナイは都市を稼働させるだけに止まらない莫大なエネルギーを生み出す事が可能であるが、その機能はブラックボックス化されており、完全に制御が出来ているとは言いがたい状況にある。 ⏎ 　各種武装も装備しており、ニーラカナイの生み出す出力により高い火力を持つが、戦艦としては機動性に欠け、戦闘力は高くはない。しかし、都市を守るドームの防御力は破格のものであり、住民の安全が最優先された設計となっている。
> EN (odniesienie oficjalne, NIE polski): A Mobile Fortification built in the underground of Yagami City (Tokyo Metropolitan Area). Yagami City and its surroundings are contained within the dome on its deck. ⏎  ⏎ Developed with the same mechanisms as a super long-range emigration ship, its residential area can function as a completely independent city. ⏎  ⏎ Its main engine, called System Nira-Kana-I, is capable of generating an enormous amount of energy, enough to power both Yagami City and the ship's operations with energy to spare; however, its intricacies are a black box, and it cannot be said to be fully under control. ⏎  ⏎ The A. Advent is equipped with a variety of high-powered weapons thanks to the output generated by the Nira-Kana-I; however, since it lacks the mobility of a battleship, its military power is not particularly high. Nevertheless, the dome's defensive capabilities are exceptional, as it was designed to prioritize the safety of its citizens.

### dic\_robot\_MFCARDNT\_00\_1

Adres: `dic\_text\_robot/014d369b:9c60b019`

> \[BRAK PL: dic\_text\_robot/014d369b:9c60b019\]
> JP (źródło tłumaczenia): 　その主目的は、超古代文明人・怨の一族の残留思念であるヴィルの制御にあったが、所有者であるエチカ・Ｙ・フランバーネットの意思により、エーアデントに集う人々の想いをエネルギーに変えて運用される事となった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Its primary purpose was to control the Willforce, the lingering psyches of the supercivilization known as the Animus Clan; however, in accordance with Echika Y. Franburnett's decision, the A. Advent now converts the feelings of the ship's inhabitants into energy.

### dic\_robot\_RNDRAH\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b000\]
> JP (źródło tłumaczenia): 　特戦隠密・朧の頭領用の機動忍鎧。 ⏎ 　柔軟なフレームと人工筋肉を使った駆動システムにより、他に類を見ない高い運動性能を誇る。操縦は搭乗者の身体の動きと各種操作の組み合わせによるセミ・スレイブシステムを採用しており、非常にデリケートな仕上がりとなっている。加えて、機体と搭乗者は神経接続されているため、ダメージのフィードバックもあり、ＮＩＮＪＡとして訓練を受けた人間以外では歩かせる事さえ難しい。 ⏎ 　背部に装備されたマフラー状のパーツはナノマシンの集合体であり、攻撃手段としてだけでなく、隠密・幻惑といった戦術に応じて様々な形で使用される。 ⏎ 　頭領用のカスタム機であるルーンドラッヘは、量産機モーントとは異なる動力機関を搭載しており、爆発的な出力を有する。 ⏎ 　なお、「ルーンドラッヘ」の名は、代々の朧の頭領が使用するマシンにつけられるものであり、現頭領用のルーンドラッヘは、そのコードネームから正式な名称は「Ｘ（クロス）ルーンドラッヘ」という。
> EN (odniesienie oficjalne, NIE polski): The Mobile Armored Ninja used by the Head of the Special Stealth Forces "Haze". ⏎  ⏎ It boasts unprecedented mobility thanks to a propulsion system that combines a flexible frame with artificial muscles. It is operated via a "semi-capture" control system, which combines the pilot's own physical movements with various on-board controls, allowing for extremely delicate and subtle movements. Since the machine and the pilot are neurally linked, the pilot also experiences damage feedback. Even something as simple as walking would be extremely difficult for someone who hasn't been trained as NINJA. ⏎  ⏎ The scarf-like gear on its back is made of a swarm of nanomachines. It can be used not only for offensive purposes, but also for stealth and decoy tactics. ⏎  ⏎ The Lunedrache is a custom-made machine for Heads; it is fitted with a different engine from the one used in the mass-produced Mond, capable of generating an explosive energy output. ⏎  ⏎ The designation "Lunedrache" is given to the machines used by the Heads of Haze over the generations. The official codename of this particular machine is "X-Lunedrache" (where the X is pronounced "Cross", after the current Head).

### dic\_robot\_RNDRAH\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b001\]
> JP (źródło tłumaczenia): 　各部にヴィル・メタルが使用されており、搭乗者の精神エネルギーを力に変える機能を持つ。 ⏎ 　また、設計時からエーアデントとの連係を前提としており、そのエネルギーの一部を利用するリンクシステムを搭載している。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Each part of the Lunedrache is lined with Willforce Metal, capable of converting the pilot's mental energy into raw power. ⏎  ⏎ It should be noted that the Lunedrache was designed to interface with the A. Advent from its conceptual stage, with a portion of its energy output specifically dedicated to powering the Link System.

### dic\_robot\_RNDRAH2\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b002\]
> JP (źródło tłumaczenia): 　特戦隠密・朧の頭領用の機動忍鎧「ルーンドラッヘ」の予備パーツで組み上げられた２号機。 ⏎ 　柔軟なフレームと人工筋肉を使った駆動システムにより、他に類を見ない高い運動性能を誇る。操縦は搭乗者の身体の動きと各種操作の組み合わせによるセミ・スレイブシステムを採用しており、非常にデリケートな仕上がりとなっている。加えて、機体と搭乗者は神経接続されているため、ダメージのフィードバックもあり、ＮＩＮＪＡとして訓練を受けた人間以外では歩かせる事さえ難しい。 ⏎ 　背部に装備されたマフラー状のパーツはナノマシンの集合体であり、攻撃手段としてだけでなく、隠密・幻惑といった戦術に応じて様々な形で使用される。 ⏎ 　頭領用のカスタム機であるルーンドラッヘは、量産機モーントとは異なる動力機関を搭載しており、爆発的な出力を有する。 ⏎ 　なお、「ルーンドラッヘ」の名は、代々の朧の頭領が使用するマシンにつけられるものであり、現頭領用のルーンドラッヘは、そのコードネームから正式な名称は「Ｘ（クロス）ルーンドラッヘ」という。
> EN (odniesienie oficjalne, NIE polski): The second unit of the Lunedrache, the Mobile Armored Ninja intended to be used by the Head of the Special Stealth Forces "Haze". This Lunedrache is assembled from the original's spare parts. ⏎  ⏎ It boasts unprecedented mobility thanks to a propulsion system that combines a flexible frame with artificial muscles. It is operated via a "semi-capture" control system, which combines the pilot's own physical movements with various on-board controls, allowing for extremely delicate and subtle movements. Since the machine and the pilot are neurally linked, the pilot also experiences damage feedback. Even something as simple as walking would be extremely difficult for someone who hasn't been trained as NINJA. ⏎  ⏎ The scarf-like gear on its back is made of a swarm of nanomachines. It can be used not only for offensive purposes, but also for stealth and decoy tactics. The Lunedrache is a custom-made machine for Heads; it is fitted with a different engine from the one used in the mass-produced Mond, capable of generating an explosive energy output. ⏎  ⏎ The designation "Lunedrache" is given to the machines used by the Heads of Haze over the generations. The official codename of this particular machine is "X-Lunedrache" (where the X is pronounced "Cross", after the current Head).

### dic\_robot\_RNDRAH2\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b003`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b003\]
> JP (źródło tłumaczenia): 　各部にヴィル・メタルが使用されており、搭乗者の精神エネルギーを力に変える機能を持つ。 ⏎ 　また、設計時からエーアデントとの連係を前提としており、そのエネルギーの一部を利用するリンクシステムを搭載している。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Each part of the Lunedrache is lined with Willforce Metal, capable of converting the pilot's mental energy into raw power. ⏎  ⏎ It should be noted that the Lunedrache was designed to interface with the A. Advent from its conceptual stage, with a portion of its energy output specifically dedicated to powering the Link System.

### dic\_robot\_RNDRAH\_NCT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b004\]
> JP (źródło tłumaczenia): 　ルーンドラッヘをベースとする最新の機動忍鎧。 ⏎ 　開発は八神テツロウによるものであるが、その詳しい経緯は明かされていない。 ⏎ 　隠密を主眼としたルーンドラッヘと比較して、戦闘を重視しており、攻撃力が大きく向上している。搭載するナノマシンの量も二倍となり、ルーンドラッヘ以上に多彩な戦術が展開可能である。しかし、それを十全に引き出すためには、より多くのエネルギーが必要であり、搭乗者への負担も比べものにならないほど大きくなっている。 ⏎ 　なお、完全に実戦での使用想定を無視した実験機であり、過剰であったり、不必要であったりするようなスペックや装備を持たされている。
> EN (odniesienie oficjalne, NIE polski): A state-of-the-art Mobile Armored Ninja based on the Lunedrache. ⏎ It was designed by Tetsuro Yagami, though little else is known about the circumstances of its development. ⏎  ⏎ While the previous Lunedrache was designed for stealth operations, this version focuses on combat capabilities, greatly increasing its attack power. With twice the volume of nanomachines, it can employ a wider variety of tactics than its predecessor; as a trade-off, it requires a greater amount of energy to operate, placing a greater burden on the pilot. ⏎  ⏎ This design was intended to be completely theoretical, an experimental machine that would never see actual combat, hence its excessive specifications and armament.

### dic\_robot\_RNDRAH\_NCT\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b005`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b005\]
> JP (źródło tłumaczenia): 　エーアデントとのエネルギーリンクを稼働させた事で、本来想定していた機体性能が発揮できるようになる。しかし、全身のヴィル・メタルが生み出す力は未知数であり、極忍技「フルムーン・クラッシュ」のように開発者の想定を超えた何かを生み出す可能性を秘めている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ By activating the energy link with the A. Advent, this machine displays the performance theorized in its conceptual stage. It should be noted that the amount of power generated by the Willforce Metal that makes up the entire body is an unknown quantity, and the ability to unleash the Super Ninja Art "Full Moon Crush" was not predicted by its developer.

### dic\_robot\_RNDRAH\_BRM\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b006\]
> JP (źródło tłumaczenia): 　ルーンドラッヘをベースとする最新の機動忍鎧。 ⏎ 　開発は八神テツロウによるものであるが、その詳しい経緯は明かされていない。 ⏎ 　隠密を主眼としたルーンドラッヘと比較して、戦闘を重視しており、攻撃力が大きく向上している。搭載するナノマシンの量も二倍となり、ルーンドラッヘ以上に多彩な戦術が展開可能である。しかし、それを十全に引き出すためには、より多くのエネルギーが必要であり、搭乗者への負担も比べものにならないほど大きくなっている。 ⏎ 　なお、完全に実戦での使用想定を無視した実験機であり、過剰であったり、不必要であったりするようなスペックや装備を持たされている。
> EN (odniesienie oficjalne, NIE polski): A state-of-the-art Mobile Armored Ninja based on the Lunedrache. ⏎ It was designed by Tetsuro Yagami, though little else is known about the circumstances of its development. ⏎  ⏎ While the previous Lunedrache was designed for stealth operations, this version focuses on combat capabilities, greatly increasing its attack power. With twice the volume of nanomachines, it can employ a wider variety of tactics than its predecessor; as a trade-off, it requires a greater amount of energy to operate, placing a greater burden on the pilot. ⏎  ⏎ This design was intended to be completely theoretical, an experimental machine that would never see actual combat, hence its excessive specifications and armament.

### dic\_robot\_RNDRAH\_BRM\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b007`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b007\]
> JP (źródło tłumaczenia): 　エーアデントとのエネルギーリンクを稼働させた事で、本来想定していた機体性能が発揮できるようになる。しかし、全身のヴィル・メタルが生み出す力は未知数であり、極忍技「フルムーン・クラッシュ」のように開発者の想定を超えた何かを生み出す可能性を秘めている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ By activating the energy link with the A. Advent, this machine displays the performance theorized in its conceptual stage. It should be noted that the amount of power generated by the Willforce Metal that makes up the entire body is an unknown quantity, and the ability to unleash the Super Ninja Art "Full Moon Crush" was not predicted by its developer.

### dic\_robot\_RUMINA\_C1\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b008\]
> JP (źródło tłumaczenia): 　革命戦争後に完成した機動兵器。 ⏎ 　安定した出力、良好な操縦性、高い整備性と量産性によって各機関で採用され、短期間の内に普及していった。 ⏎ 　このカラーは新地球連邦軍とその協賛機関で使用されているタイプであり、世界各地で運用されている。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon developed after the Revolutionary War. ⏎  ⏎ It was quickly adopted worldwide due to its stable performance, simplified controls, ease of maintenance, and standardized mass production. ⏎  ⏎ This specific color scheme indicates use by the New Earth Federation Forces and its sanctioned organizations, with widespread use throughout the world.

### dic\_robot\_RUMINA\_C1\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b009`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b009\]
> JP (źródło tłumaczenia): 　ラー・ヴァル軍のヴァイ・ルーミナのモンキーモデルであり、最大の特徴であるプロフォトン・エフェクト・ドライブは装備していない。そのため、戦闘力はオリジナルより数段劣っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ A simplified version of the Ra Val military Vi Lumenus, this model does not incorporate the distinctive Prophoton Effect Drive; as a result, its combat power is several degrees lower than the original.

### dic\_robot\_RUMINA\_C2\_00\_0

Adres: `dic\_text\_robot/014d369b:9ca0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b00a\]
> JP (źródło tłumaczenia): 　革命戦争後に完成した機動兵器。 ⏎ 　安定した出力、良好な操縦性、高い整備性と量産性によって各機関で採用され、短期間の内に普及していった。 ⏎ 　このカラーは民間に販売されたものであり、私設の武装組織などで運用されている。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon developed after the Revolutionary War. ⏎  ⏎ It was quickly adopted worldwide due to its stable performance, simplified controls, ease of maintenance, and standardized mass production. ⏎  ⏎ This specific color scheme indicates models sold to civilians, often for use by private military organizations.

### dic\_robot\_RUMINA\_C2\_00\_1

Adres: `dic\_text\_robot/014d369b:9ca0b00b`

> \[BRAK PL: dic\_text\_robot/014d369b:9ca0b00b\]
> JP (źródło tłumaczenia): 　ラー・ヴァル軍のヴァイ・ルーミナのモンキーモデルであり、最大の特徴であるプロフォトン・エフェクト・ドライブは装備していない。そのため、戦闘力はオリジナルより数段劣っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ A simplified version of the Ra Val military Vi Lumenus, this model does not incorporate the distinctive Prophoton Effect Drive; as a result, its combat power is several degrees lower than the original.

### dic\_robot\_RUMINA\_C3\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b000\]
> JP (źródło tłumaczenia): 　革命戦争後に完成した機動兵器。 ⏎ 　安定した出力、良好な操縦性、高い整備性と量産性によって各機関で採用され、短期間の内に普及していった。 ⏎ 　このカラーは各スペースコロニー軍とその協賛機関で使用されているタイプであり、主に宇宙空間で運用されている。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon developed after the Revolutionary War. ⏎  ⏎ It was quickly adopted worldwide due to its stable performance, simplified controls, ease of maintenance, and standardized mass production. ⏎  ⏎ This specific color scheme indicates use by the Space Colonies and their sanctioned organizations, operating primarily in space.

### dic\_robot\_RUMINA\_C3\_00\_1

Adres: `dic\_text\_robot/014d369b:9ce0b001`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b001\]
> JP (źródło tłumaczenia): 　ラー・ヴァル軍のヴァイ・ルーミナのモンキーモデルであり、最大の特徴であるプロフォトン・エフェクト・ドライブは装備していない。そのため、戦闘力はオリジナルより数段劣っている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ A simplified version of the Ra Val military Vi Lumenus, this model does not incorporate the distinctive Prophoton Effect Drive; as a result, its combat power is several degrees lower than the original.

### dic\_robot\_VAY\_RUMINA\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b002\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの使用する機動兵器。 ⏎ 　主機関プロフォトン・エフェクト・ドライブの生み出す出力により、高い火力と機動力を有する。 ⏎ 　本来のルーミナ系は用途に応じて様々なバリエーションを持っていたが、生産性と汎用性を重視した結果、現在はヴァイ・タイプのみが量産されている。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon used by the Pan-Stellar Empire Ra Val. ⏎ Its Prophoton Effect Drive is a powerful engine that provides remarkable firepower and mobility. ⏎  ⏎ Originally, the Lumenus series included numerous specialized variants, but currently only the general-purpose Vi-type is in mass production.

### dic\_robot\_STERA\_VRS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b004\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝親衛隊（天騎士）用の機体「ステーラ」のカスタム機。 ⏎ 　天騎士レー・セイヴァースが搭乗する。 ⏎ 　最高速度重視のセッティングがされており、ラー・ヴァル最速の機体と呼ばれる。 ⏎ 　三基のプロフォトン・エフェクト・ドライブを搭載し、高い戦闘力を誇るが、扱いが難しく、操縦には高い技量を必要とする。
> EN (odniesienie oficjalne, NIE polski): A custom Stella for the exclusive use of the Celestial Knights, the elite guards of the ⏎ Pan-Stellar Empire Ra Val. ⏎  ⏎ This model is piloted by Celestial Knight Re Seivas. ⏎  ⏎ Finely tuned for maximum speed, it is considered the fastest machine in Ra Val. ⏎  ⏎ Loaded with three Prophoton Effect Drives, it boasts exceptional combat power; at the same time, it is extremely difficult to operate, requiring the skills of only the most talented pilots.

### dic\_robot\_STERA\_BLS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b006\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝親衛隊（天騎士）用の機体「ステーラ」のカスタム機。 ⏎ 　天騎士レー・システィスが搭乗する。 ⏎ 　各部の装甲が増強されており、高い防御力を誇る。 ⏎ 　また大隊を指揮する機体として通信機能と索敵能力が大幅に強化されている。
> EN (odniesienie oficjalne, NIE polski): A custom Stella for the exclusive use of the Celestial Knights, the elite guards of the ⏎ Pan-Stellar Empire Ra Val. ⏎  ⏎ This model is piloted by Celestial Knight Re Sistis. ⏎  ⏎ Geared for high defense, all sections have been reinforced with additional armor. ⏎  ⏎ As a model designed to lead a battalion, it is equipped with enhanced communication and surveillance devices.

### dic\_robot\_STERA\_FLS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b008\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝親衛隊（天騎士）用の機体「ステーラ」のレプリカ機。 ⏎ 　本来のステーラは天騎士にのみ与えられる機体であるが、地球漂着後、戦力の増強として天闘士も搭乗する事となった。 ⏎ 　ステーラ・ブルスをベースに開発されており、最高出力は抑えられているが、良好な操縦性を実現している。
> EN (odniesienie oficjalne, NIE polski): A replica of the Stella, a mobile weapon intended for use by the Celestial Knights, the elite guards of the Pan-Stellar Empire Ra Val. ⏎  ⏎ Originally, Stellas were only given to Celestial Knights, but after landing on Earth, it was determined that assigning them to Celestial Warriors would be an effective way to increase the military power of the army. ⏎  ⏎ Based on the Stella Blus, its performance is reduced compared to the original model, but it still exhibits excellent maneuverability.

### dic\_robot\_STERA\_KKN\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b00a\]
> JP (źródło tłumaczenia): 　ステーラ・フォルスがヴィルによって複製された機体。 ⏎ 　機体色が変わっただけでなく、ヴィルをエネルギーとして使用する事で戦闘力も大幅に向上している。 ⏎ 　その存在は、ステーラに強い誇りを持つラー・ヴァル人から憎まれている。
> EN (odniesienie oficjalne, NIE polski): A Stella Force model, duplicated by the Willforce. ⏎  ⏎ It is not a simple change of color: fueled by the Willforce, its combat abilities are drastically enhanced. ⏎  ⏎ Ra Valians are known to harbor an intense hatred for these duplicates, as they take great pride in their personal Stellas.

### dic\_robot\_ENDNOS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b00c\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの天帝騎。 ⏎ 　天帝ラー・ヴァルベルムが自らの専用機として開発させたものであり、ラー・ヴァル最強の機体と呼ばれる。 ⏎ 　ヴァルベルムが天帝の座について以来の愛機であり、ラー・ヴァル勝利の象徴として、公式には一度の敗北も記録されていない。 ⏎ 　７基のプロフォトン・エフェクト・ドライブを装備し、あらゆる局面で高い戦闘力を発揮する。中でも巨大な戦斧「天怒ゲラウノス」は、敵対する星間国家の旗艦を一撃で真っ二つにしたという逸話を持つ。
> EN (odniesienie oficjalne, NIE polski): The personal machine of the Celestial Emperor of the Pan-Stellar Empire Ra Val. ⏎  ⏎ Designed for the exclusive use of Ra Valbelm, it is considered the most powerful mobile weapon of the Ra Val. ⏎  ⏎ Valbelm has favored the machine since his ascension to the throne. It is the symbol of Ra Val's absolute supremacy, and there is no official record of any defeat it has ever suffered in battle. ⏎  ⏎ Fitted with seven Prophoton Effect Drives, it displays exceptional combat prowess in any situation. Its colossal battleaxe, the Celestial Wrath Qeraunos, is said to have split the flagship of a hostile interstellar nation in half with a single swing.

### dic\_robot\_GGENDNOS\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b00e\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの最終兵器。 ⏎ 　エンディーノスを核とし、無人機のステーラ・フォルス部隊の制御中枢として機能する。 ⏎ 　大量のプロフォトン・エフェクト・ドライブに加え、ヴィルをエネルギー源とした事で単体の機動兵器としても破格の戦闘力を持つ。 ⏎ 　デバイスの補助があってもヴィルの制御には膨大な精神力を必要とするため、搭乗者であるヴァルベルムは常にギリギリの状態を強いられる。操縦者の精神バランスが崩壊すれば、暴走ならびに大爆発するという危険性がつきまとうが、そのリスクを呑み込むだけの力を生み出し、ヴァルベルムの銀河制覇計画の中核を成す。
> EN (odniesienie oficjalne, NIE polski): The ultimate weapon of the Pan-Stellar Empire of Ra Val. ⏎  ⏎ With the Endenos at its core, it serves as the control center for the unmanned Stella Force platoon. ⏎  ⏎ In addition to its numerous Prophoton Effect Drives, it is also powered by the Willforce; this amount of pure raw power is unheard of in a single mobile weapon. ⏎  ⏎ Even with the aid of the Will Device, controlling the Willforce requires a great deal of mental fortitude; the pilot, Valbelm, is constantly pushed to the limits of his mental capacity. If he were to lose focus, his mental balance would collapse, with a definite risk of system failure and explosion. Nevertheless, Valbelm has deemed the risk worth the reward, and the system has become the centerpiece of his plan to conquer the galaxy.

### dic\_robot\_IZNORT\_00\_0

Adres: `dic\_text\_robot/014d369b:9ce0b010`

> \[BRAK PL: dic\_text\_robot/014d369b:9ce0b010\]
> JP (źródło tłumaczenia): 　イヴォルバーの意思であるヴィルによって生み出された機動兵器。 ⏎ 　超人類イザナを核とし、肉体を失ったヴィルの新たな器として、彼等の銀河制覇計画の中核を成す。 ⏎ 　ステーラ・コクエン、怨獣ミドロなど、ヴィルの支配下にある機体の制御中枢としても機能するだけでなく、怨獣ミドロを遙かに上回る戦闘力を有する。 ⏎ 　その戦力の限界は未知数であるが、ヴィルと超人類の力が融合すれば、惑星すらも破壊可能であるとされる。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon created by the will of the Evolvers, the Willforce. ⏎  ⏎ With Izana the Superhuman, the Willforce's new physical vessel, at its core, it is the centerpiece of their plan to assume dominion over the galaxy. ⏎  ⏎ In addition to serving as the control center for all entities powered by the Willforce, such as the Stella Kokuen legion and the Animus Beast Midollo, its own combat capabilities are immensely high, surpassing even those of Midollo itself. ⏎  ⏎ The limits of its abilities are unknown, but it is theorized that if the Willforce and the Superhuman fully merge, they would develop a power capable of easily destroying planets.

### dic\_robot\_GRVLIN\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b000\]
> JP (źródło tłumaczenia): 　クエスターズの実行部隊隊長カールレウムの乗機。 ⏎ 　単機で多数の敵を殲滅するコンセプトの下、圧倒的な攻撃力を持ち、その性能は量産機動兵器オルクスーラ・シリーズとは一線を画する。 ⏎ 　高い戦闘力に加え、指揮系統の中枢を担う機能を備え、理論上では６５５３５機のオルクスーラ・シリーズを同時にコントロールする事が可能。 ⏎ 　「新たな地球の王」の証として与えられた機体であり、カールレウムのアイデンティティとも言える存在。 ⏎ 　クエスターズが制圧した星の王となる者に与える機体「ヴァリン」シリーズの最上位機であり、特別に高い攻撃力が与えられている。 ⏎ 　これは制圧対象である地球文明の危険性によるものであり、グラヴァリンを中核としたクエスターズの戦力は、最悪の場合、地球文明を根こそぎ破壊する事も想定されていた。
> EN (odniesienie oficjalne, NIE polski): The personal machine of Caruleum, the captain of the execution team of the Quaestors. ⏎  ⏎ Designed as a one-machine army, the Gravalin possesses overwhelming offensive abilities that set it apart from the Orcusula-series mass-produced mobile weapons. ⏎ In addition to its own incredible combat potential, it is a critical command-and-control unit; it is capable of commanding 65,535 Orcusula-series units simultaneously. ⏎  ⏎ Controlling this machine is proof of the pilot's status as the new King of Earth; for this reason, it has become an integral part of Caruleum's own identity. ⏎  ⏎ The Valin-series are machines given only to those appointed as the king of a planet conquered by the Quaestors. This particular machine is the most advanced unit of the series, and thus possesses particularly high offensive abilities. ⏎  ⏎ Selecting this unit was a deliberate choice due to the risk posed by Earth's civilization; in the worst case scenario, the Gravalin is expected to lead the Quaestors' forces and annihilate humanity.

### dic\_robot\_ARKDIA\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b002\]
> JP (źródło tłumaczenia): 　ネバンリンナが自らのボディとして造り上げた機動兵器。 ⏎ 　超文明ガーディムのテクノロジーと、スレイブナンバー２０４４ことナインが収集した様々な世界の技術が融合している。 ⏎ 　上腕部や腰部、大腿部に見られるエネルギー流はフレームに当たり、それを装甲が覆う形で全身が構成されており、余剰エネルギーは背面に浮かぶプレート状のエネルギー・クリスタルを形成している。 ⏎ 　その戦術思想は、艦隊戦を基本とする旧来のガーディムのものとは異なり、高い機動力と火力の組み合わせによる。これはスピードと高火力という相反する要素を機動兵器と戦艦の連携で行なう地球式の戦術を単独で完結させたものであり、ナインの制作したヴァング・シリーズの究極の型であるとも言える。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon constructed by Nevanlinna for use as her own physical body. ⏎  ⏎ It is an amalgamation of technology from the Super Civilization Gardim and data from various worlds collected by Slave 2044 (Nine). ⏎  ⏎ Energy flows through its entire body, visible in the arms, waist, and leg blocks. The main frame is covered in armor, and the excess energy takes the form of a plate-like energy crystal floating on its back. ⏎  ⏎ Unlike the old Gardim, whose battle doctrine was oriented towards fleet combat, this mobile weapon focuses on the combination of high mobility and firepower. ⏎  ⏎ A single unit that combines two opposing elements: high speed and high power, a sort of amalgamation of the Earthling tactic of coordinating mobile weapons with battleships; in a sense, this could be considered the ultimate form of Nine's Vang-series.

### dic\_robot\_ENDE\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b004\]
> JP (źródło tłumaczenia): 　高次元生物である魔獣エンデの肉体。 ⏎ 　オドそのもので構成されており、エンデの意思をドグマへと変える。 ⏎ 　その背中に生えている樹は、魔従教団の聖地「真実の世界樹」とリンクしており、アル・ワースに生る知恵の実に宿った人々の想いが集まるようになっている。 ⏎ 　エンデの本体は前頭部にあり、その下部の巨大な口や四肢は、以前にエンデが乗っ取った別の高次元生物のものである。
> EN (odniesienie oficjalne, NIE polski): The body of the higher dimensional being, Ende the Devourer. ⏎  ⏎ It is made up of Od itself and converts Ende's intent into Dogma. ⏎  ⏎ The tree growing on its back is connected to the sacred ground of the Keepers of Order, the Tree of World Truth. It collects the thoughts of the people contained within the Fruit of Wisdom that grows on Al-Warth. ⏎  ⏎ Ende's main body is in the front; the giant mouth and limbs that constitute the lower portion belong to another higher dimensional being that Ende has taken over.

### dic\_robot\_DIGIA\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b006`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b006\]
> JP (źródło tłumaczenia): 　ダイマ・ゴードウィンの進める銀河統一計画の中核となる絶対決戦兵器。 ⏎ 　機動要塞ＶＴＸのコントロールユニットも兼ねており、ダイガイアンのコックピットから全ての機能の制御が可能。 ⏎ 　開発には、黄金の時代の遺産を含む地球文明、太陽系先史文明、ラミィとＵＮＤのもたらした異星人文明が融合した科学技術とＶＴＸユニオンの豊富な資金が惜しげもなくつぎ込まれてた。 ⏎ 　機体のコンセプトは、新宇宙歴１８０年代にダイマが搭乗して活躍したスーパーロボット「ガイアーン」を継承している。 ⏎ 　ダイマの操縦技術と合わせた戦闘力は、単機でＵＮＤの第零番艦隊に匹敵する。 ⏎ 　なお、完成時にはオミットされたが、設計段階では単独で宇宙戦艦への変形機構が搭載されており、各部にはそのなごりを見て取れる。
> EN (odniesienie oficjalne, NIE polski): The ultimate weapon at the core of Dyma Goldwin's Galactic Unification Project. ⏎ In addition to serving as the control unit for the Mobile Fortress VTX, several other functions can be accessed from the DyGaian's cockpit. ⏎  ⏎ The DyGaian was developed by combining science from Earth's Golden Age, relics from ancient solar system civilizations, and alien technology brought by Rami and the UND, as well as "creative" use of VTX Union funds. ⏎  ⏎ Its design is based on the Super Robot "Gaian" piloted by Dyma during his active service around New Universal Era (NUE) 180. ⏎  ⏎ Combined with Dyma's piloting skills, its combat capabilities are comparable to the entirety of the UND's Zero Fleet. ⏎  ⏎ Though it was eventually scrapped before completion, during its design phase the DyGaian was equipped with a transformation mechanism that would allow it to transform into a space battleship on its own; remnants of this mechanism can still be seen in various segments.

### dic\_robot\_FTBNFROBO\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b008`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b008\]
> JP (źródło tłumaczenia): 　１万２０００年前に栄えた超古代文明・怨の一族が使用していた兵器。 ⏎ 　人間の精神の中でも怒りや憎しみ、怨みなどのマイナス思念をエネルギーとしており、それらを肉体を失った存在（いわゆる悪霊や怨霊と呼ばれる類）から得ている。 ⏎ 　知性や理性というものは持っていないが、取り込んだマイナス思念の影響によって憎悪と破壊の化身として活動する。
> EN (odniesienie oficjalne, NIE polski): An ancient weapon used by the Animus Clan, a supercivilization that flourished 12,000 years ago. It is fueled by human negative thoughts such as anger, hatred, and resentment, which it absorbs from beings who have lost their physical bodies (the so-called evil spirits and vengeful ghosts). ⏎  ⏎ Although it lacks true intelligence or reason, it is influenced by negative thoughts that fuel it to act on destructive and hateful urges.

### dic\_robot\_CYBSTER\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00a`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b00a\]
> JP (źródło tłumaczenia): 　地底世界ラ・ギアスの神聖ラングラン王国で開発された機体。 ⏎ 　風の精霊サイフィスの加護を受け、「風の魔装機神」の異名を持つ。 ⏎ 　メイン動力はフルカネルリ式永久機関。 ⏎ 　そのパワー効率を高めるため、操者（パイロット）の「プラーナ」が必要とされる。プラーナとは「気」や「オーラ」と呼ばれるものと基本的に同じで、操者によって供給される。そのため、パワーは操者の資質に多大な影響を受けてしまう。 ⏎ 　機体の気密性は高く、水中や宇宙空間での行動も可能。内部に自己循環システムがあるため、操者の生理機能は守られ、長時間の行動が可能。 ⏎ 　また、エーテル（質量を持たず、絶対座標に対して静止しているエネルギー）を魔術的媒体として推進に利用している。 ⏎ 　装甲材質はオリハルコニウムで、呪符的効果のある数秘学を元にした幾何学模様が金属粒子レベルで封じ込められており、魔術的防御も高い。 ⏎ 　メインコンピューターはラプラスデモンタイプで、因果律を計算し、様々な事象を予測することが出来る。ただし、その機能は操者自身の魔力によって著しく左右される。 ⏎ 　なお、サイバスターは真の名前ではなく、魔術的な攻撃を避けるための守護名である。
> EN (odniesienie oficjalne, NIE polski): A machine developed by the Holy Kingdom of Langran in the subterranean world of La Gias. ⏎  ⏎ It has received the blessing of Cyphis, the spirit of the wind, granting it the title of Elemental Lord of Wind. ⏎  ⏎ Its main power source is a Fulcanelli-type perpetual motion machine, with the prana of its herald (that is, its pilot) required to increase its power efficiency. ⏎  ⏎ Prana is a form of energy derived from the pilot, essentially the same as concepts like ki or Auras. For this reason, the power of an Elemental Lord is heavily influenced by the aptitude of its herald. ⏎  ⏎ Cybaster is airtight, allowing it to operate both underwater and in the vacuum of space. It has an internal self-circulation system that maintains the herald's physiological functions, allowing Cybaster to operate for extended periods of time. ⏎  ⏎ It also uses ether (massless energy that remains stationary relative to absolute coordinates) as a magical propulsion medium. ⏎  ⏎ Its armor is comprised of orichalconium, with geometric patterns based on numerology imbued at the metallic particle level, providing considerable defense against magic. ⏎  ⏎ Its main computer is a Laplace's Demon-type, which can calculate the laws of causality to predict a variety of phenomena and events, to a degree influenced by the herald's own magical power. ⏎  ⏎ It should be noted that Cybaster is not its true name, but a ward to protect it from magical attacks.

### dic\_robot\_VANX\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00c`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b00c\]
> JP (źródło tłumaczenia): 　ナインがサンプルとして組み上げた機動兵器ヴァングレイの後継機。 ⏎ 　寄せ集めの資材で造られたヴァングレイと異なり、様々な世界の技術を学んだナインによって新規に設計されている。 ⏎ 　なお設計段階では意識されていなかったが、ナインの持つガーディムの技術も導入されており、三つの世界とガーディムのテクノロジーが融合した機体と言える。 ⏎ 　ヴァングレイのコンセプトを発展させた機体であり、戦術や武装はヴァングレイのものを踏襲、または強化している。在りものの資材の寄せ集めではなく、各パーツ類も新造されており、ヴァングレイが抱えていた問題の多くは解消されている。 ⏎ 　ロールアウト当初は想定していた出力に達しておらず、様々な不備があったが、ガーディムに捕獲された際、その資材を利用して改修された事で真の完成へと至った。 ⏎ 　また、ヴァングレイ以上にギリギリのバランスで制御系が成立しているため、ナインも同乗して、機体状況を肌で感じながら各種コントロールを補佐する必要がある。 ⏎ 　同時に、「大切な人と共に戦う」という意識がナインの機能を向上させたため、ヴァングネクスは設計段階での想定を大幅に上回る力を発揮した。
> EN (odniesienie oficjalne, NIE polski): The successor to the mobile weapon VangRay, assembled by Nine as a sample model. ⏎  ⏎ Unlike the VangRay, which was built from a variety of materials, it has been developed from the ground up using Nine's knowledge of technology from other worlds. ⏎  ⏎ Although not part of the original design, Nine incorporated Gardim engineering, making this machine an amalgamation of technology from three worlds and Gardim. ⏎  ⏎ The VangNex is an extension of the concept behind the VangRay: its tactics and weapons are based on those of its predecessor, adapted and improved upon. Unlike the VangRay, which was assembled from existing components, every part of the VangNex has been newly manufactured with the goal of solving many of the VangRay's issues. ⏎  ⏎ During its first deployment, it was unable to achieve the expected performance and had a multitude of shortcomings; after being seized by Gardim, it was modified with new materials, bringing the VangNex to true perfection. ⏎  ⏎ Because the control system requires precise on-the-fly fine-tuning, even more so than the VangRay, Nine must be physically on board to assist with operations, while experiencing the machine's condition firsthand. ⏎  ⏎ As Nine has come to understand the meaning of "fighting alongside your loved ones", her own functions have improved; as a result, the VangNex demonstrates much greater performance than was estimated in its design phase.

### dic\_robot\_GRNVNG\_00\_0

Adres: `dic\_text\_robot/014d369b:9d20b00e`

> \[BRAK PL: dic\_text\_robot/014d369b:9d20b00e\]
> JP (źródło tłumaczenia): 　ナインがサンプルとして組み上げた機動兵器ヴァングレイの後継機。 ⏎ 　寄せ集めの資材で造られたヴァングレイと異なり、様々な世界の技術を学んだナインによって新規に設計された。 ⏎ 　その際、ナインの趣味により、いわゆる「スーパーロボット」的な要素が多分に盛り込まれており、そのマスクはナインの「理想の男性像」がモチーフになっている。 ⏎ 　なお設計段階では意識されていなかったが、ナインの持つガーディムの技術も導入されており、三つの世界とガーディムのテクノロジーが融合した機体と言える。 ⏎ 　ヴァングレイのコンセプトであった高機動と高火力の両立の内、火力の強化を優先した機体であり、出力の向上のため機体サイズはヴァングレイよりもかなり大きくなっている。また、それだけの出力を受け止めるために機体剛性も大幅に強化されており、ヴァングレイ以上の重装甲を誇る。 ⏎ 　ロールアウト当初は想定していた出力に達しておらず、様々な不備があったが、ガーディムに捕獲された際、その資材を利用して改修された事で真の完成へと至った。 ⏎ 　また、ヴァングレイ以上にギリギリのバランスで制御系が成立しているため、ナインも同乗して、機体状況を肌で感じながら各種コントロールを補佐する必要がある。 ⏎ 　同時に、「大切な人と共に戦う」という意識がナインの機能を向上させたため、グランヴァングは設計段階での想定を大幅に上回る力を発揮した。
> EN (odniesienie oficjalne, NIE polski): The successor to the mobile weapon VangRay, assembled by Nine as a sample model. ⏎  ⏎ Unlike the VangRay, which was built by assembling available parts, it has been developed from the ground up using Nine's knowledge of technology from other worlds. ⏎  ⏎ Designed to Nine's own tastes, the GranVang incorporates many super-robot-like elements; in particular, the face mask is based on her perception of the "ideal man". ⏎  ⏎ Although not part of the original design, Nine incorporated Gardim engineering, making this machine an amalgamation of technology from three worlds and Gardim. ⏎  ⏎ While the VangRay was based on the concept of high mobility and high firepower, the GranVang places the emphasis on firepower. It is larger than its predecessor to maximize energy output. To support the increased power, the rigidity of the frame has been increased with heavier, sturdier armor plates. ⏎  ⏎ During its first deployment, it was unable to achieve the expected performance and had a multitude of shortcomings; after being seized by Gardim, it was modified with new materials, bringing the GranVang to true perfection. ⏎  ⏎ Because the control system requires precise on-the-fly fine-tuning, even more so than the VangRay, Nine must be physically on board to assist with operations, while experiencing the machine's condition firsthand. ⏎  ⏎ As Nine has come to understand the meaning of "fighting alongside your loved ones", her own functions have improved; as a result, the GranVang demonstrates much greater performance than was estimated in its design phase.

### dic\_robot\_XELGD\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b000`

> \[BRAK PL: dic\_text\_robot/014d369b:9da0b000\]
> JP (źródło tłumaczenia): 　魔従教団が開発したオート・ウォーロック。 ⏎ 　教団の倉庫の片隅に放置されており、少なくとも１００年以上前の機体と推測されているが、これは教主専用の機体として開発された本機の乗り手が１００年以上、現れなかった事を意味する。 ⏎ 　前腕部に機械式の魔法陣が装備されており、素速くドグマを使用する事が出来るが、強力なドグマを使用する場合は空間魔法陣を必要とする。 ⏎ 　教団の制式採用機であるディーンベルと比較して扱いづらく、現行の機体の仕様と比較すると各部が非効率的である。 ⏎ 　魔力の増幅率も不安定であり、乗り手の術士のコンディションや魔力によって、ダイレクトに戦闘力が変化する。 ⏎ 　これらの不都合はゼルガードの設計思想が、ディーンベルと異なるためである。 ⏎ 　オート・ウォーロックの魔力の増幅は、術士の魔力を無理矢理引き出すようなものであり、やり過ぎれば精神を破壊する可能性もある。そのため、ディーンベルの魔力増幅は弱い魔力を増幅し、上限にもリミッターを設けているが、ゼルガードはこの制限が存在しておらず、低い魔力では増幅機構も稼働しないようになっている。 ⏎ 　その代わりにゼルガードは、搭乗者の魔力次第では無限とも言える力を発揮し、同時に術士に自らの魔力の存在を意識させ、その力を伸ばす働きがある。 ⏎ 　真の力を発揮する際は、各部が展開し、折りたたまれた翼が開かれる。 ⏎ 　魔獣エンデが転生する際の「肉体（＝器）」となるべき存在であり、生命・精神と共にエンデと融合した際は、その姿を大きく変える事が推測される。
> EN (odniesienie oficjalne, NIE polski): An Autowarlock designed by the Keepers of the Order. ⏎  ⏎ Abandoned in a corner of the Order's warehouse, it is estimated to be at least 100 years old. Designed for the Founder's exclusive use, it is believed that no one worthy of operating it has appeared in the last 100 years. ⏎  ⏎ It is equipped with mechanical magic circles on its forearms, allowing it to quickly cast simpler Dogmas; however, it still requires the drawing of a spatial magic circle to cast more powerful spells. ⏎  ⏎ The Xelguard is more difficult to operate than the Deenbell, the Order's mainline Autowarlock; there are several components that are considered inefficient and outdated by modern standards. In addition, its magical amplification rate is unstable, and its combat power is directly affected by the condition and magic power of the sorcerer. These drawbacks stem from the difference in design concept between the Xelguard and the modern Deenbell. ⏎  ⏎ An Autowarlock's magical amplification forcefully drains a sorcerer's magic power. If used carelessly, the sorcerer's own soul could be shattered. For this reason, the Deenbell only amplifies weak magic, with a safety limiter set at a certain threshold. ⏎  ⏎ The Xelguard, on the other hand, has no such limiter; in fact, its amplification mechanism does not activate at low magic levels at all. As a result, the Xelguard can exhibit virtually unlimited power. ⏎  ⏎ The sorcerer has full awareness of their magic, which they can control to harness its power. ⏎  ⏎ When the Xelguard unleashes its true potential, several parts of its body open up and it unfolds its wings. ⏎  ⏎ It was conceived to serve as the vessel of Ende the Devourer. Supposedly, its physical appearance would change drastically upon fusion with Ende's life and soul.

### dic\_robot\_TRNED\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b002`

> \[BRAK PL: dic\_text\_robot/014d369b:9da0b002\]
> JP (źródło tłumaczenia): 　ＶＴＸユニオンのプロジェクトＴＮＤ（Ｔｅｒｒｅｓｔｒｉａｌ　Ｎｅｘｔ Ｄｒｅａｍ）で開発された試作機の先行量産バージョン。 ⏎ 　その名は「ＴＮＤ」と最強の肉食恐竜「ティラノサウルス」に由来する。 ⏎ 　従来の機動兵器を凌駕する高出力、それを利用した大推力を特徴とし、空戦能力に優れた機体。しかし、最高速度では小回りが利かず、使いこなすためには相応の操縦技術が必要とされる。 ⏎ 　また、統合戦術支援機「キャリアクス」との連携を前提としており、携行が困難なサイズの火器はキャリアクスから射出してもらう。 ⏎ 　次期量産機選定コンペに向けて、新設部署である特務三課によって実戦テストとデータ収集が行われていた。 ⏎ 　その高出力は惑星ダーブネスで開発されたクォーク・ドライブを搭載した事によるものであり、各部に異星人と地球の技術が融合が見られる。 ⏎ 　なお、制式採用時にはティラネード５機とキャリアクス１機で部隊は構成される事が前提とされており、特務三課による両機の連携戦術は想定外のものである。
> EN (odniesienie oficjalne, NIE polski): The pre-production version of the prototype mobile weapon developed as part of VTX Union's Project TND (Terrestrial Next Dream). ⏎  ⏎ Its name is derived from both the acronym TND and the Tyrannosaurus, popularly known as the most powerful predator to walk the planet. ⏎  ⏎ Its output far exceeds that of conventional mobile weapons. The Tyranado uses this force to generate its signature high thrust, granting it excellent aerial combat capabilities. However, maneuverability is drastically reduced at maximum speed, requiring a highly skilled pilot to operate it effectively. ⏎  ⏎ The Tyranado is designed to work in conjunction with the Carriax, the integrated tactics and support vehicle, which delivers any ordinance too large for direct transport. It was one of the mobile weapons eligible for the competition to select the next mass production model. Special Section 3 was established for the purpose of field testing and data collection. ⏎  ⏎ The reason for its high power output is the Quark Drive, an engine developed on Planet Darbnes; in fact, many of the Tyranado's parts combine human and alien technology. ⏎  ⏎ It should be noted that the original proposal was for one Carriax to support five Tyranado units; the joint operation of the Carriax with a single Tyranado by Special Section 3 was completely unforeseen.

### dic\_robot\_TRNEDREX\_00\_0

Adres: `dic\_text\_robot/014d369b:9da0b004`

> \[BRAK PL: dic\_text\_robot/014d369b:9da0b004\]
> JP (źródło tłumaczenia): 　試作機であったティラネードの強化発展型。 ⏎ 　その名は、「未知の可能性を秘めた改修『Ｒｅ：Ｘ』」と「ティラノサウルス・レックス」からつけられた。 ⏎ 　ティラネードの基本フレームを流用しつつ、これまでに特務三課が集めたデータがフィードバックされた各部パーツを換装し、短期間の改修ながら外観は大きく変わり、各性能も大幅に向上した。 ⏎ 　誰が乗っても性能が引き出せる量産機とは正反対のコンセプトになったが、これは搭乗者のポテンシャルをどれだけ引き出せるかに興味を持った技術部の探究心（一説では悪ノリ）の結果である。 ⏎ 　キャリアクスとの連携による戦術はティラネードと同様であるが、クォーク・ドライブの解析が進んだ結果、稼働効率が大幅に向上して各武装をより高い出力で使用できるようになり火力もアップしている。 ⏎ 　後追いではあるが、プロジェクトＴＮＤは「ＶＴＸユニオンのフラッグシップ機の開発」という新たな目標が設定され、その成果物となる本機は随時バージョンアップが加えられた。異星文明の産物であるクォーク・ドライブの改良も進み、最終的には破格の機動力と火力、キャリアクスとの連携による戦術運用などにより、フラッグシップ機と呼ぶに相応しい機体として完成した。
> EN (odniesienie oficjalne, NIE polski): The revised model of the Tyranado, further improved from the original prototype. ⏎  ⏎ Its new name is derived from the improvement plan "Revision concealing unknown potential, Re: X" and Tyrannosaurus Rex. ⏎  ⏎ While sharing the basic frame of the Tyranado, all parts have been replaced with new ones developed using feedback from data collected by Special Section 3. Despite the fact that these modifications were made in a short period of time, the Tyranado's appearance changed significantly and its performance improved drastically. ⏎  ⏎ Rather than following the original concept of a mass-produced machine with stable average performance regardless of its pilot, the Tyranado Rex is the result of Engineering's (some would say "unhealthy") interest in how much potential they could harness from a particular pilot. ⏎  ⏎ The combat tactics used in conjunction with the Carriax are inherited from those used by the Tyranado; after a more in-depth analysis of the Quark Drive, the operational efficiency has been improved, allowing each weapon to be used at a consistently higher output. ⏎  ⏎ Although a later decision, Project TND set a new goal, the development of VTX Union's flagship model. The Tyranado Rex, the main product of the project, received additional upgrades as needed. With improvements to the Quark Drive, legacy of an alien civilization, unprecedented mobility and firepower, and its coordinated tactical operations with the Carriax, the Tyranado Rex is undoubtedly worthy of the title of flagship model.

### dic\_robot\_BIGO\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f4e0b000`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f4e0b000\]
> JP (źródło tłumaczenia): 　ロジャー・スミスが搭乗する黒いメガデウス。 ⏎ 　ロジャーが左腕のリストウォッチに「ビッグオー！ショウタイム！」と叫ぶ事で地下より現れ、彼と共に敵へと立ち向かう。 ⏎ 　ロジャーの搭乗時、正面モニターに「CAST IN THE NAME OF GOD YE NOT GUILTY（我、神の名においてこれを鋳造する。汝ら罪なし）」のスペルが表示される。 ⏎ 　普段はロジャーの屋敷の地下に収容されているが、ひとたびロジャーから召喚がかかると、使われなくなった地下交通機関を専用トランスポーター「プレイリードッグ」で疾走し、目的地へと運ばれる。 ⏎ 　目から放つ光線「アーク・ライン」、胸部と腹部から放つ「キャノン・パーティー」「ミサイル・パーティー」などの内蔵火器を秘めているが、最大の決め技は腕のストライク・パイルを打ち込む一撃必殺の打撃技「サドン・インパクト」である。 ⏎ 　謎が多く、いつ、どこで、誰が何のために製造したかの答えは、搭乗者であるロジャーですら知らない。
> EN (odniesienie oficjalne, NIE polski): The black Megadeus piloted by Roger Smith. ⏎  ⏎ It appears from underground to face Roger's foes alongside him when Roger calls "Big O, showtime!" into the wristwatch on his left wrist. ⏎  ⏎ Upon boarding, the main monitor displays the words "CAST IN THE NAME OF GOD, YE NOT GUILTY". ⏎  ⏎ When not in active use, Big O is stored beneath Roger's mansion, and when called by Roger, it uses a transport vehicle called the Prairie Dog to quickly traverse the unused underground rail system to reach him. ⏎  ⏎ While it possesses some internal firepower with the Arc Line beam emitters in its eyes and the Cannon Party and Missile Party attacks launched from its torso, its single most devastating weapon is a blast from the Strike Pilebunkers in its arms, which is called "Sudden Impact". ⏎  ⏎ A deeply mysterious machine, no one knows who made it, when, where, or for what purpose—not even Roger, its pilot.

### dic\_robot\_BBDX\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b001`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b001\]
> JP (źródło tłumaczenia): 　ベック所有のメガデウス。別名「スーパーベック」。 ⏎ 　部下のＴボーンとダヴが、ワイズカンパニーから奪ったヘヴィメタル・ユニットのパーツを用いて製造したロボット。 ⏎ 　武器として、両胸に収納されたミサイルと指先から放つビームがある。ビームはモビーディック・アンカーの鎖を切る威力を持つが、ビッグオーの頭部クリスタルに命中した際は跳ね返されてしまった。 ⏎ 　逃げ足が速く、上半身が１８０度回転するのが特徴で、その機能を使いビッグオーに不意打ちを仕掛ける場面も見られた。
> EN (odniesienie oficjalne, NIE polski): Beck's own Megadeus. ⏎ Also simply called Super Beck. ⏎  ⏎ T-Bone and Dove constructed it using heavy industrial unit parts stolen from the Wise Company. ⏎  ⏎ It has missiles in its chest plate, as well as finger lasers to use as weapons. The beams have enough force to break Big O's Mobydick Anchors, but reflects off of its crystalline head plate. ⏎  ⏎ It is uniquely fast when running away and is able to twist its torso one hundred and eighty degrees, which ends up being used to trick Big O.

### dic\_robot\_BIGD\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b003`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b003\]
> JP (źródło tłumaczenia): 　シュバルツが発見したメガデウス。 ⏎ 　ビッグオーが陸のザ・ビッグならば、ビッグデュオは空のザ・ビッグとも言える性能を持つ。 ⏎ 　両腕から主翼を展開し、４本の指をプロペラに変形させ、強力なエンジンにより飛行を行う。 ⏎ 　武装は目から放つ光線「アーク・ライン」、胸部から放つ「ガトリングミサイル」、両下脚に収納されている「メガトンミサイル」がある。 ⏎ 　ドミュナス（操縦者）が乗っていない状態でもひとりでに動き出す事もあり、不可解な点が多い。
> EN (odniesienie oficjalne, NIE polski): The Megadeus excavated by Schwarz. ⏎  ⏎ If Big O is a land machine, then Big Duo is the master of the sky amongst the Bigs. It has wings on both arms and the ability to turn its four fingers into propellers, which combined with the afterburner of its powerful engine, allows Big Duo to fly. ⏎  ⏎ For weaponry, it has the Arc Line beam shot from its eyes, Gatling Missiles fired from its chest, and the two Megaton Missiles secured in its lower legs. It can also use its propellers at full spin to cut into an enemy. ⏎  ⏎ It sometimes acts without a Dominus aboard. It is, in many ways, a total enigma.

### dic\_robot\_BRIGER\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b005`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b005\]
> JP (źródło tłumaczenia): 　ブライ・シンクロン・マキシムによってブライスターから変形するスライド変形の最終形態。ブライサンダー・ブライスター・ブライガーの３形態の中で最強の戦闘力を持つ。 ⏎ 　操縦は他の２形態同様にボウィーが担当するが、新たにキッドが頭部のブラスター・ピットに移動し、攻撃を一手に引き受ける。 ⏎ 　プラズマ破壊ガン・ブライショットスペシャル（普段はＪ９のメンバーがサイドカーとして使用）、ブライソード等の強力な武装に加えて、ポンチョ操縦のブライ・キャリアが輸送するブライ・カノンによって絶大な攻撃力を誇る。 ⏎ 　開発者はシンクロン理論の発案者であり、その才能は世界を１００年進歩させると言われた天才科学者エドモン博士。
> EN (odniesienie oficjalne, NIE polski): The Brai-Star's final form achieved through a sliding transformation, using Brai-synchron-maximum. ⏎  ⏎ Between the three possible forms—the Brai-Thunder, Brai-Star, and Braiger, it is the most powerful. Like the other forms, Bowie handles the piloting. Kid is shifted to the Blaster Pit in the head and takes control of attacking. ⏎  ⏎ Along with the destructive plasma gun, the Brai-Shot Special (which is normally used by the J9 members as a side-car), and the Brai-Sword, it is also capable of wielding the incredibly powerful Brai-Cannon, which is transported by the Brai-Carrier, piloted by Poncho. ⏎  ⏎ It was created by Doc Edmond, the same man who discovered the synchron principle and whose genius was said to propel the world forward one hundred years in scientific development.

### dic\_robot\_KRDWCJ\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b007`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b007\]
> JP (źródło tłumaczenia): 　左翔太郎とフィリップが、ダブルドライバーとサイクロンメモリ、ジョーカーメモリで変身した姿。 ⏎ 　使用するメモリから「サイクロンジョーカー」と呼ばれる形態であり、スピードと格闘能力に優れる。素早い格闘攻撃を繰り出しながら、風を取り込んでスタミナを回復させられる。 ⏎ 　ドライバー左右のメモリを入れ替える事によって別の形態へと再変身する事が可能であり、それに応じて特性とカラーが変化する。 ⏎ 　変身時には片方の意識は肉体のベースとなる身体に憑依する形となっている。サイクロンジョーカーの場合、翔太郎の身体にフィリップの意識が融合している。
> EN (odniesienie oficjalne, NIE polski): The form Shotaro and Philip take when they load the Cyclone Memory and the Joker Memory into the W Driver. ⏎  ⏎ This form is named Cyclone Joker, based on the Memories that access it. It vastly improves the users' speed and striking power, allowing them to fight with a rapid onslaught of punches and kicks, while absorbing the power of the wind to restore their energy. ⏎  ⏎ Other Memories can be loaded into the Drivers' respective left and right slots to change forms, each with different colors and powers. ⏎  ⏎ When the two become Double, one of their bodies actually transforms, while the other's consciousness is transferred into it. Cyclone Joker uses Shotaro's body, with Philip's mind sharing it.

### dic\_robot\_KRDWCAXEL\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b009`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b009\]
> JP (źródło tłumaczenia): 　照井竜がアクセルドライバーとアクセルメモリで変身した姿。 ⏎ 　アクセルメモリによる加速力の記憶と、それを引き出すアクセルドライバーにより、超加速と高い身体能力を誇る。
> EN (odniesienie oficjalne, NIE polski): The form Ryu Terui takes when he loads the Accel Memory into the Acceldriver. ⏎  ⏎ The Acceldriver harnesses and channels the memory of acceleration, giving its user superhuman strength and incredible speed.

### dic\_robot\_KRDWSCULL\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00b`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b00b\]
> JP (źródło tłumaczenia): 　鳴海荘吉がロストドライバーとスカルメモリを使用して変身した姿。 ⏎ 　「骸骨」の記憶を持つメモリの力により、肉体が強化されているほか、変身中は不死身となる。 ⏎ 　その身体は冷たく、死者同然といえる。
> EN (odniesienie oficjalne, NIE polski): The form Sokichi Narumi assumes when he loads the Skull Memory into the Lostdriver. ⏎  ⏎ The skeletal power not only increases his physical strength, but makes him immortal while in that form. ⏎  ⏎ He becomes cold to the touch, as if dead.

### dic\_robot\_RDDOPNT\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00d`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b00d\]
> JP (źródło tłumaczenia): 　ロードメモリを用いて変身したドーパント。 ⏎ 　スピードと熱によって別次元の裏風都への道を作り出す能力を持つ。 ⏎ 　裏風都には複数の個体が存在しており、街を生成し拡大させる役割を担っている。
> EN (odniesienie oficjalne, NIE polski): The Dopant form taken by using the Road Memory. ⏎  ⏎ It can use its speed and heat generation to create a road into the alternate dimension of Shadow Fuuto. ⏎  ⏎ Several Dopants stay in Shadow Fuuto, where they are tasked with building and expanding the city.

### dic\_robot\_DLCBST\_00\_0

Adres: `dic\_text\_robot-DLC1/00000312:f560b00f`

> \[BRAK PL: dic\_text\_robot-DLC1/00000312:f560b00f\]
> JP (źródło tłumaczenia): 　アルフコートが別世界から召喚した巨大ゴーレム。 ⏎ 　人間がもたらす悪意の蒸気を動力としている。 ⏎ 　蒸気機関のようなものを持っており、外部から吸収した悪意の蒸気でピストンを動かし、機体の馬力を跳ね上げる。 ⏎ 　武器は、取り外し可能な腕部にドッキングする歯車型チェーンソーの他、両腕部に格納された自走式の歯車。 ⏎ 　非常に重い機体のため、動きは遅い。
> EN (odniesienie oficjalne, NIE polski): A massive golem summoned by Alfcourt from a parallel world. It's powered by evil steam created by human malice. ⏎  ⏎ It incorporates a component analogous to a steam engine, engaging pistons with evil steam absorbed from its surroundings to boost the machine's power to unprecedented levels. ⏎  ⏎ It's armed with a detachable gear-powered chainsaw that mounts on its arm, as well as self-propelled gears stored within the arms. ⏎  ⏎ Its tremendous weight makes it extremely slow.

### dic\_robot\_RNGLM\_00\_0

Adres: `dic\_text\_robot-DLC1/00202c8e:5560b000`

> \[BRAK PL: dic\_text\_robot-DLC1/00202c8e:5560b000\]
> JP (źródło tłumaczenia): 　魔従教団が使用する岩人形。 ⏎ 　オドが宿った玄武岩にドグマを注入する事で素体を制作し、そこに機械的な制御機構と魔力を組み込んで完成する。 ⏎ 　内部には制御頭脳代わりの人工生命体「ウォルンタス」が搭載されており、命令を与える術士が周囲にいなくても、ある程度の自律的な行動が可能。 ⏎ 　武装を使用する際は内部に蓄えられた魔力を使用するが、周囲に継続して魔力を供給する術士がいない場合、戦闘力は激減する。
> EN (odniesienie oficjalne, NIE polski): An earthen automaton employed by the Keepers of Order. ⏎  ⏎ Made by infusing Dogma into Od-rich basalt rock, and incorporating mechanical components and magical energy. ⏎  ⏎ An artificial life form called a Voluntas serves as its control unit, allowing it to take some independent actions even without a nearby sorcerer to issue commands. ⏎  ⏎ It draws upon its internal stores of magical power to use weapons, but its combat abilities decrease greatly without a sorcerer nearby replenishing it.

### dic\_robot\_DENBEL\_00\_0

Adres: `dic\_text\_robot-DLC1/00202c8e:5620b001`

> \[BRAK PL: dic\_text\_robot-DLC1/00202c8e:5620b001\]
> JP (źródło tłumaczenia): 　魔従教団が開発したオート・ウォーロック。 ⏎ 　オート・ウォーロックの完成型と呼ばれるに値する高い信頼性と安定した魔力増幅を誇り、約３０年に渡り、教団の制式採用機として第一線で使用されている。 ⏎ 　また、その高い戦闘力は、法と秩序の番人である魔従教団の力の象徴であり、実際に目撃された例は少ないながらもアル・ワースの住民達には畏敬の念を以て迎えられている。 ⏎ 　戦場では一機のディーンベルが複数のルーン・ゴーレムを制御し、ディーンベルとその術士は小隊長的な役割を果たす。 ⏎ 　しかし、使いやすさを優先させた設計になっており、高い魔力を持つ術士にとっては自身の魔力を活かしきれない可能性もある。
> EN (odniesienie oficjalne, NIE polski): An Autowarlock designed by the Keepers of Order. ⏎  ⏎ With its reliability and stable magical amplification, it's regarded as a perfected Autowarlock design, and has served as the Keepers' main frontline unit for around 30 years. ⏎  ⏎ Its high performance makes it a symbol of the Keepers' role as guardians of law and order. Despite being deployed only rarely, it commands the respect of citizens all over Al-Warth. ⏎  ⏎ A single Deenbell can command several Rune Golems in battle, so they and the sorcerers operating them act as squad leaders in the field. ⏎  ⏎ Their only flaw is that they were designed with ease of use in mind, so extremely powerful sorcerers can't use their own magical powers to their fullest extent.

### dic\_robot\_ISTLJEEG\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:5220b000`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:5220b000\]
> JP (źródło tłumaczenia): 　司馬博士が対邪魔大王国用に開発したマグネロボット。 ⏎ 　司馬宙が変身したジーグヘッドにビッグシューターから発射された各種ジーグパーツが合体して完成する。 ⏎ 　磁流波エネルギーを動力源とし、出力は７５万馬力を誇る。 ⏎ 　ダイナマイトキック、ジーグブリーカーなどの格闘攻撃のほか、ナックルボンバー、スピンストームなどの武器を装備するが、最大の特徴はマグネットパワーで各種パーツを換装して戦うことである。マッハドリルやジーグバズーカだけでなく、物語の後半ではジーグバックラーやスカイパーツ、アースパーツ、マリンパーツといったパーツを状況に応じて使い分けるようになった。
> EN (odniesienie oficjalne, NIE polski): The Magnetic Robot developed by Dr. Shiba to counter the Jamatai Kingdom. ⏎  ⏎ Steel Jeeg is formed when the Jeeg Parts, launched from the Big Shooter, combine with the Jeeg Head (which Hiroshi Shiba transforms into). ⏎ Powered by magnetic current energy, it boasts an impressive output of 750,000 horsepower. ⏎  ⏎ In addition to close-quarters combat techniques like the Dynamite Kick and Jeeg Breaker, it is equipped with ranged weapons such as the Knuckle Bomber and Spin Storm. Its most distinctive feature, however, is the Magnet Power, which allows Jeeg to easily swap parts during battle. ⏎  ⏎ Jeeg initially has access to the Mach Drill and the Jeeg Bazooka, but his arsenal is expanded throughout the story to include additional equipment such as the Jeeg Buckler, the Sky Parts, the Earth Parts, and the Marine Parts, enabling Hiroshi to adapt to any combat situation.

### dic\_robot\_ISTLJEEG\_H\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b001`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b001\]
> JP (źródło tłumaczenia): 　サイボーグ宙が変身したジーグの頭部パーツ。 ⏎ 　この状態ではジーグビームと体当たりくらいしか攻撃方法がなく、ビッグシューターがいないと鋼鉄ジーグはまさに手足をもがれた状態となる。 ⏎ 　一応、単独で空を飛べる。
> EN (odniesienie oficjalne, NIE polski): The head component of Kotetsu Jeeg, which Cyborg Hiroshi transforms into. ⏎  ⏎ In this state, its combat options are limited to the Jeeg Beam and ramming attacks; without the Big Shooter to launch its parts, Kotetsu Jeeg is, quite literally, disarmed. ⏎ With that said, it is capable of independent flight.

### dic\_robot\_GTENOIR1\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b003`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b003\]
> JP (źródło tłumaczenia): 　異なる時空で作られたゲッターロボ・ノワールシリーズの１号機。 ⏎ 　リョウマ専用の機体で、ゲッター１の同種の武装以外に２丁拳銃のゲッタードラグーン7000を持ち、近接、遠距離戦闘をこなす。
> EN (odniesienie oficjalne, NIE polski): Unit 1 of the Getter Robo Noir-series, created in an alternate space-time. ⏎  ⏎ Designed exclusively for Ryoma, it is equipped for both melee and ranged combat. ⏎ In addition to armaments similar to those of the original Getter 1, it carries a pair of pistols, the Getter Dragoon 7000.

### dic\_robot\_GTENOIRG\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b005`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b005\]
> JP (źródło tłumaczenia): 　ゲットマシンに変形したゲッターノワール１号機、２号機、３号機が合体した姿。 ⏎ 　リョウマがメインパイロットを、ハヤトとムサシがサポートを務める。 ⏎ 　各ゲッターノワールそれぞれの特徴的な武装を受け継ぎ、圧倒的な攻撃力を誇る。
> EN (odniesienie oficjalne, NIE polski): The combination of Getter Noir 1, Noir 2, and Noir 3 after changing into their Get Machine forms. ⏎  ⏎ Ryoma serves as the primary pilot, with Hayato and Musashi providing support. ⏎  ⏎ Inheriting the distinctive armaments of the individual Getter Noir units, this form boasts overwhelming offensive capabilities.

### dic\_robot\_DGANX\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b007`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b007\]
> JP (źródło tłumaczenia): 　地球が生み出した勇者ダ・ガーンが、サポートメカのアースファイター、アースライナーと合体した巨大ロボ。 ⏎ 　アースファイターが上半身、アースライナーが下半身を形成し、ダ・ガーンを挟み込む形で完成する。 ⏎ 　胸部の地球をかたどったパーツからエネルギーを撃ち出すブレストアースバスターが最大の必殺技。
> EN (odniesienie oficjalne, NIE polski): A giant robot formed when Da-Garn, the Brave Fighter birthed by the Earth, combines with his support mecha, the Earth Fighter and the Earth Liner. ⏎  ⏎ In this form, the Earth Fighter serves as the upper body, the Earth Liner as the lower body, and Da-Garn is positioned between them. ⏎  ⏎ His ultimate finishing move is the Breast Earth Buster, which fires a beam of energy from his Earth-shaped chest piece.

### dic\_robot\_DGANGX\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b009`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b009\]
> JP (źródło tłumaczenia): 　ダ・ガーンＸとガ・オーンが伝説合体した姿。 ⏎ 　ガ・オーンのパーツがダ・ガーンＸの各部にパーツとして装着される形で構成される。 ⏎ 　ＧキャノンとＧバルカンを連結させたＧＸバスターが最強の武装。なお、ＧＸバスターは組み替える事でＧＸバスターバルカンとしても使用できる。
> EN (odniesienie oficjalne, NIE polski): The "Legend Combined" form of Da-Garn X and Ga-Orn. ⏎  ⏎ This form is created by attaching parts of Ga-Orn to various sections of Da-Garn X as additional components. ⏎  ⏎ His most powerful weapon is the GX Buster, formed by linking the G-Cannon and G-Vulcan together. ⏎  ⏎ Additionally, the GX Buster can be reconfigured and used as the GX Buster Vulcan.

### dic\_robot\_REDGIST\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00b`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b00b\]
> JP (źródło tłumaczenia): 　レッドロンが搭乗する兵器。 ⏎ 　人型形態からドラゴン形態への変形が可能。 ⏎ 　手持ちのライフルと、そこに収納されている剣で戦う。
> EN (odniesienie oficjalne, NIE polski): The combat robot piloted by Redlone. ⏎  ⏎ It can change between a humanoid form and a dragon form. ⏎ Its rifle also serves as the sheath for its sword.

### dic\_robot\_VOLFG140\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00d`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b00d\]
> JP (źródło tłumaczenia): 　レッドロン軍団の戦闘ロボット。 ⏎ 　偵察ロボット・リーケンα部隊を引き連れて現れた。 ⏎ 　巨体から繰り出すパワーでダ・ガーンを圧倒したが、合体したダ・ガーンＸに一刀両断された。
> EN (odniesienie oficjalne, NIE polski): One of the combat robots of the Redlone Army. ⏎  ⏎ It appeared alongside a squadron of Riken Alpha reconnaissance robots. ⏎  ⏎ At first, it overwhelmed Da-Garn with its large frame and raw power, but was ultimately cloven in half by Da-Garn's combined form, Da-Garn X.

### dic\_robot\_IGZIS\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b00f`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b00f\]
> JP (źródło tłumaczenia): 　現在の地球以外の文明によって創られたロボット。 ⏎ 　永久機関に近い機能を持つ動力炉から生み出される高エネルギーにより、圧倒的な戦闘力と継戦能力を誇る。 ⏎ 　テクノロジーの詳細は不明であるが、自律的な意思と心と呼べるものを持っており、自らの判断に従って行動する。 ⏎ 　その性格は、いい意味で実直、悪い意味で頑固であり、自らの使命である正義の遂行に全てを懸けている。同時に自らのアイデンティティに強い思い入れがあり、エチカにもらった「イグジス」の名を大切にしている。
> EN (odniesienie oficjalne, NIE polski): A robot created with technology far surpassing that of modern Earth. ⏎ Equipped with a power reactor that grants him nigh-infinite energy, he boasts overwhelming combat prowess and fighting capabilities. ⏎  ⏎ Though the details of the technology are unknown, he appears to possess autonomous will, allowing him to act based on his own judgment. ⏎  ⏎ His personality is honest and forthright—at its best, though he can be quite stubborn. He throws everything he has into fulfilling his mission of justice. At the same time, he thinks deeply about his identity and cherishes the name Exis that Echika bestowed on him.

### dic\_robot\_IBIT\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b011`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b011\]
> JP (źródło tłumaczenia): 　ＵＮＤの統合戦術機動兵器。 ⏎ 　イービットαのレイ・クレイヴァーとイービットβのレイ・フォーカスの両方を装備している。 ⏎ 　戦術に応じて各機の分担が明確に区分されているＵＮＤにおいて、本機の存在は異端であり、高コストもあって運用例は多くない。しかし、地球人の戦術に対応するために全領域での戦闘が求められ、戦線に投入される事となった。 ⏎ 　特性の異なる二種類の武装を状況に応じて選択するため搭乗者の負担が大きい事が問題視される中、それらを難なくこなす地球人類の異質さが浮き彫りとなった。
> EN (odniesienie oficjalne, NIE polski): 　The UND's comprehensive tactical mobile weapon, equipping both the E-Bit Alpha's Ray Cleaver and the Beta's Ray Focus. ⏎  ⏎ The UND typically assigns units based on strict and distinct roles. This design is, therefore, unusual for them, as well as expensive, so not many are in service. ⏎ However, they were deployed to Earth when the Earthlings' tactics demanded adaptability to different combat conditions. The need to switch between two very different weapons became a notable strain on its pilots. This led to the innovation of employing Earthlings, who could adapt to this with much less difficulty.

### dic\_robot\_IFAS\_00\_0

Adres: `dic\_text\_robot-DLC2/0000025c:52e0b013`

> \[BRAK PL: dic\_text\_robot-DLC2/0000025c:52e0b013\]
> JP (źródło tłumaczenia): 　ＵＮＤの最新型統合戦術機動兵器。 ⏎ 　設計プランのみで実機の開発は延び延びになっていたが、機動兵器を中心とする地球人の戦術に対応すべく完成が前倒しされた経緯を持つ。 ⏎ 　全領域に対応する武装を持つために搭乗者への負担が大きいが、現行のイービットシリーズを凌駕する戦闘力を誇る。
> EN (odniesienie oficjalne, NIE polski): The UND's latest tactical mobile weapon. ⏎  ⏎ It was stuck in development hell for a long time before finally being pushed to completion in the campaign against the Earth, which used mobile weaponry as the center of its combat practices. ⏎  ⏎ It carries weaponry suitable for a variety of combat conditions, which puts a greater strain on the pilot, but its performance dwarfs that of its predecessors, the E-Bit line.

### dic\_robot\_IDEON\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4d20b000`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4d20b000\]
> JP (źródło tłumaczenia): 　ソロ星の第１発掘現場から発見された、第６文明人の遺産。 ⏎ 　史料の中から唯一読み取れたギリシャ文字風のパターンからイデオンと名付けられる。 ⏎ 　Ａメカ・Ｂメカ・Ｃメカという３台の車両型メカが合体することによって、イデオンとなる。各メカも変形及び戦闘を行うことができる。名称はそれぞれ、Ａメカはソル・アンバー／イデオ・デル ⏎ タ、Ｂメカはソル・バニアー／イデオ・ノバ、Ｃメカはソル・コンバー／イデオ・バスタ。 ⏎ 　地球人が取り付けたグレン・キャノン、５４９門のミサイルが主武装。戦いの中、本来の武器である惑星をも真っ二つにするイデオンソード、出力によっては通常空間から亜空間の敵も狙い撃ちでき、惑星を吹き飛ばすほどの威力を持つイデオンガンが使えるようになったが、明確な制御方法はわかっていない。 ⏎ 　バッフ・クラン星に伝わる伝説「イデの英雄（他にもイデの巨神など、さまざまな呼び方がある）」と何らかの関係があると推測されている。また、伝説の通りであれば、無限の力を持っているとされる。
> EN (odniesienie oficjalne, NIE polski): A relic of the Sixth Civilization, discovered at the first excavation site on Planet Solo. ⏎  ⏎ It was named "Ideon" based on the only legible pattern found among the historical records—a sequence resembling Greek letters. ⏎  ⏎ Ideon is formed by the combination of three vehicle-type machines: the A Mecha, the B Mecha, and the C Mecha. Each unit is capable of independent transformation and combat. Their respective names are: Sol Amber/Ideo Delta (A Mecha); Sol Vainer/Ideo Nova (B Mecha); Sol Conver/Ideo Buster (C Mecha). ⏎  ⏎ Initially, its primary weapons consisted of the Glenn Cannons (installed by the surviving Solo colonists) and 549 missile launchers. ⏎  ⏎ During the course of the war, its true armaments were revealed: the Ideon Sword—capable of cleaving entire planets in half; and the Ideon Gun—a weapon that can strike enemies both in normal space and in hyperspace depending on its output, powerful enough to annihilate planets. However, no clear method of controlling these weapons was ever discovered. ⏎  ⏎ It is believed to be connected to a certain myth passed down on the Buff Clan's homeworld: the legend of the "Hero of Ide" (at times referred to as the "Legendary Giant of Ide"). According to this legend, Ideon is said to possess infinite energy.

### dic\_robot\_JIGMACK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b001`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4de0b001\]
> JP (źródło tłumaczenia): 　バッフ・クラン軍の重機動メカ。 ⏎ 　亜空間戦闘用のギラン・ドウ、局地戦用のドグ・マックを経て、開発された。 ⏎ 　クローはイデオンの装甲をひしゃげさせるほどのパワーを持つと同時に、人を掴むほどの精密動作も可能である。 ⏎ 　重機動メカは一般的にコックピットが脱出ポッドになっているが、ジグ・マックは脚部を切り離した後に胴体部分全てを脱出ポッドとする。 ⏎ 　後発の機体が完成した後も多数量産され、安定した性能で主戦力として運用された。
> EN (odniesienie oficjalne, NIE polski): One of the Heavy Mobile Mechas used by the Buff Clan. ⏎  ⏎ It was developed as a successor to both the Giran Dou (designed for hyperspace combat) and the Dogg Mack (designed for local-volume combat), inheriting and refining their specializations. ⏎  ⏎ Its claws are powerful enough to crush Ideon's armor while also precise enough to grasp a human without causing injury. ⏎  ⏎ While most Heavy Mobile Mecha cockpits double as escape pods, the Zigg Mack is unique in that it ejects its top half after detaching its legs. ⏎  ⏎ Even after newer models were developed, the Zigg Mack remained in mass production due to its stable performance, continuing to serve as a reliable mainstay of the Buff Clan forces.

### dic\_robot\_HNGD\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b003`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4de0b003\]
> JP (źródło tłumaczenia): 　アナハイム・エレクトロニクス社が開発したニュータイプ用モビルスーツ。 ⏎ 　一撃で戦艦を撃破できる大出力のハイパー・メガ・バズーカ・ランチャー、バックパックのファンネルポッドで再充電可能なフィン・ファンネルなどを装備し、高い攻撃力を誇る。
> EN (odniesienie oficjalne, NIE polski): A Newtype Mobile Suit developed at Anaheim Electronics Co. ⏎  ⏎ Equipped with a Hyper Mega Bazooka Launcher that can destroy a warship in one shot and Fin Funnels that can recharge via a back-mounted funnel pod, it boasts a high degree of offensive power.

### dic\_robot\_NCNGL\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b005`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4de0b005\]
> JP (źródło tłumaczenia): 　ネオ・ジオンのニュータイプ専用モビルスーツ。 ⏎ 　両肩には小型軽量化されたα・アジールタイプのファンネルを１０基搭載し、スカート部には隠し腕が仕込まれている。
> EN (odniesienie oficjalne, NIE polski): A Neo Zeon Mobile Suit developed for Newtypes. ⏎  ⏎ Ten miniaturized, lightweight Alpha Azieru-type Funnels are housed in the shoulders, while the skirt pieces hide an extra arm.

### dic\_robot\_INBEL\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4de0b007`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4de0b007\]
> JP (źródło tłumaczenia): 　隕石除去人型重機「iDOL」の一機。 ⏎ 　通称・プロメテウス１。 ⏎ 　iDOLは「immortal defender of legatee（遺産相続人の永遠の守護者）」の意味を持ち、無限とも言えるエネルギーを持つシリコン構造体こそが本体である。これをコアとした人型インターフェイスが、iDOLである。 ⏎ 　インベルは過去のマスターを拒絶してから16年もの間、稼働していなかったが、天海春香をマスターとする事で再起動する。 ⏎ 　月崩壊による災害「ロスト・アルテミス」からの復興を目的とする組織「モンデンキント」に所属し、敵対組織「トゥリアビータ」と戦っていたが、鹵獲されて改良パーツ「ファウストシュラーク」を装備させられた。 ⏎ 　なお、胸部装甲のピンクはマスターである春香の好みに合わせて用意された。 ⏎ 　心とも呼べるものを持っており、春香に対しては恋愛感情を持っている。 ⏎ 　別宇宙へと続くゲート「アウリン」から地球を守るため、春香と他のiDOLと共に突入作戦に参加した。
> EN (odniesienie oficjalne, NIE polski): One of the humanoid anti-meteorite machines known as iDOLs. ⏎  ⏎ Its callsign is Prometheus 1. As the acronym iDOL (Immortal Defender of the Legatee) indicates, it has an almost infinite supply of energy and a body formed of silicon dendrites. This body together with the humanoid interface that makes up its core is what makes an iDOL unit. ⏎  ⏎ Imber remained dormant for sixteen years after losing its previous master, but reactivated when Haruka Amami was brought on as its new master. ⏎  ⏎ Under the flag of Mondenkind, an organization focused on rebuilding society after the destruction of the moon and the resulting Lost Artemis disaster, Imber is used in the fight against the enemy organization Turiavita. ⏎  ⏎ In the course of this conflict, though, Imber was captured and forced to equip an upgrade parts unit known as the Faustschlag. The pink coloration of its chest armor was implemented to suit the taste of Haruka, its master. ⏎  ⏎ As Imber came to develop its own heart, it began to feel true love toward Haruka. Finally, to protect the Earth from AULYN, a gate to another universe, it participated in a mission to enter the gate along with Haruka and her allies.

### dic\_robot\_TUBRNCMPT\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b001`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b001\]
> JP (źródło tłumaczenia): 　古代銀河文明の遺した人型ロボット・サイバディの一体。 ⏎ 　キング・ザメクとの戦いでダメージを受けたタウバーン・オーディナリーがタクトのリビドーによって復活した姿。 ⏎ 　サイバディは通常の時間軸から隔離されたゼロ時間内でのみ活動可能であったが、王のサイバディ「キング・ザメク」との戦いの中でゼロ時間から解放される事となった。 ⏎ 　それにより現実世界に侵攻を開始したサイバディに対して、タクトと共に立ち向かった。
> EN (odniesienie oficjalne, NIE polski): One of the giant robots known as Cybodies, artifacts of an ancient galactic civilization. ⏎  ⏎ This is its form after Tauburn Ordinary was damaged in battle with King Samekh and repaired using Takuto's libido. ⏎  ⏎ Cybodies were originally only capable of operating within zero-time, a temporal axis separate from our own, but they were unsealed as a result of the battle with the king Cybody, King Samekh. ⏎  ⏎ After that, Tauburn continues to serve with Takuto, opposing the Cybodies' invasion of the real world.

### dic\_robot\_VRKS\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b003`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b003\]
> JP (źródło tłumaczenia): 　アルゼナルの格納庫に保管されていた旧式のパラメイル。 ⏎ 　機体は白と青色に塗装され、頭部に女神像がつけられているのが特徴。 ⏎ 　アルゼナルが所有するパラメイルの基本武装である対ドラゴン用アサルトライフルや凍結バレットはもちろん、独自の武器としてドラゴンの硬い皮膚や鱗でさえ深く切り裂く零式超硬度斬鱗刀「ラツィーエル」を装備する。 ⏎ 　旧式であるにもかかわらず他のパラメイルを凌駕する高い性能を持っていたが、出力や制御に問題があるために操縦者が見つからず放置されていた。 ⏎ 　アンジュがドラゴンとの戦いで死に直面した際、彼女の血が斑鳩王家の指輪に反応した事で、戦闘で損傷した箇所を含め老朽化した機体が瞬時に修復し覚醒した。 ⏎ 　以後はアンジュの乗機となり、パラメイル第一中隊の中核戦力として、活躍する。 ⏎ 　その存在には数々の秘密が隠されており、それを知る者は、アルゼナルの中ではジルを含む数名しかいない。
> EN (odniesienie oficjalne, NIE polski): An old Para-Mail that was stored in Arzenal's hangar. ⏎  ⏎ This machine features a white and blue paint scheme as well as a goddess statue on its head. ⏎  ⏎ Not only does it come equipped with essential Para-Mail weapons such as an anti-Dragon assault rifle and freezing bullets, it also features a unique weapon called the Type Zero Super Density Blade "Raziel", which can cut deeply even into the tough armor and scales of Dragons. ⏎  ⏎ Despite being an older type, the Villkiss had high enough specs to match other Para-Mails, but because of its output and control issues, no suitable pilot was ever found, and it was left to sit. ⏎  ⏎ When Ange was about to die in a battle against a Dragon, her blood reacted to her ring of the Imperial House of Ikaruga, and the machine—having deteriorated and taken damage in combat—instantly reawakened and repaired itself. ⏎  ⏎ From then on, Ange became its pilot and served as the backbone of the First Para-Mail Squadron. ⏎  ⏎ The Villkiss hides many secrets, and only a select few at Arzenal know of them, including Jill.

### dic\_robot\_VRKS\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b004`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b004\]
> JP (źródło tłumaczenia): 　アンジュの持つ指輪に反応する形で、戦いの中で徐々にその力を解放し、状況に応じて様々な特性をもったモードを見せる。光速を越えた次元跳躍を可能にする「アリエル・モード」では機体は青く染まり、空間位相エネルギーを取り込みラツィーエルから巨大エネルギーブレードを生み出す「ミカエル・モード」では赤に染まる。 ⏎ 　さらにアンジュの歌う「永遠語り」によってリミッターが解除された「ウリエル・モード」では、機体が黄金に輝き、両肩に内蔵されている次元兵器「ディスコード・フェイザー」を発射する。 ⏎ 　その正体は、終末戦争時に造られた絶対兵器ラグナメイルの一機「ビルキス」で、古の民がリベルタスのためにエンブリヲから奪った機体である。その際にエンブリヲからの解放と訣別を願って、「ヴィルキス」と名を変えられた。 ⏎ 　アンジュによって真の力が解放され、最終決戦時には、アリエル、ミカエル、ウリエルの全ての特性を併せ持った姿となり、エンブリヲのヒステリカを倒した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ By reacting to Ange's ring, the Villkiss can gradually unleash its power in battle, giving it access to a variety of different modes to handle any situation. ⏎ In Ariel Mode, the machine becomes blue and it gains access to dimensional jumps that can exceed the speed of light. ⏎ In Michael Mode, it turns red and can produce a huge energy blade from Raziel by incorporating spatial-phase energy. ⏎ In addition, when Ange sings Eternal Storyteller, the Villkiss transforms into Uriel Mode, which disengages its limiters. In this mode, the machine glows golden and can fire Discord Phasers, a dimensional weapon stored in the shoulders. ⏎  ⏎ The Villkiss's true name is Bilkis, an absolute weapon Ragna-Mail created during the Endwar, which the Ancient Folks stole from Embryo for Libertas. To denote their wish of liberation and parting from Embryo, they changed its name to "Villkiss". ⏎  ⏎ During the final battle, Ange unleashed the Villkiss's true abilities, gaining access to a form combining Ariel, Michael, and Uriel to defeat Embryo's Hysterica.

### dic\_robot\_HSTLK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b005`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b005\]
> JP (źródło tłumaczenia): 　最初に開発されたラグナメイルであり、調律者を名乗るエンブリヲの専用機。 ⏎ 　基本構造は他のラグナメイルと共通しているが、頭部のツインアイが露出していたり、ウイングが複数存在していたりと独自の機構を持つ。 ⏎ 　腕部に接近戦用のビームサーベルが装備されている他、両肩とウイングの付け根付近にディスコード・フェイザーを内蔵している。
> EN (odniesienie oficjalne, NIE polski): The first Ragna-Mail ever developed and the exclusive machine of Embryo, a man who calls himself the Tuner. ⏎  ⏎ It shares its basic construction with other Ragna-Mails, but with unique mechanisms, such as a pair of exposed eyes on the head and several pairs of wings. ⏎  ⏎ Its arms store beam sabers for close-quarters combat, while its shoulders and the base of its wings are equipped with Discord Phasers.

### dic\_robot\_HSTLK\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b006`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b006\]
> JP (źródło tłumaczenia): 　その真の役目は有人次元観測機であり、さらに次元跳躍によってエンブリヲの精神と融合した彼のもう一つの肉体であった。 ⏎ 　最終決戦では、アンジュによって真の力を解放したヴィルキスに撃破され、さらに生身のエンブリヲもタスクに倒され、エンブリヲは完全に消滅した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Its true purpose was to observe parallel dimensions containing life. Having fused with Embryo's mind by way of a dimensional jump, it served as a second body for him. ⏎  ⏎ When Ange unleashed the Villkiss's true power in their final battle, she shot down the Hysterica, and with Tusk defeating Embryo's physical form, Embryo was fully destroyed.

### dic\_robot\_PLOID\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b007`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b007\]
> JP (źródło tłumaczenia): 　アルゼナル攻撃のためにジュリオが投入した無人兵器。 ⏎ 　円盤状の機体で、内蔵されているチェーンソーを露出させ、高速回転しながら突撃し、目標を切り裂く。 ⏎ 　本体にワイヤーが内蔵されており、ターニャやイルマ機を捕獲するなど、攻撃以外の用途でも運用可能。
> EN (odniesienie oficjalne, NIE polski): An unmanned weapon deployed by Julio for his attack on Arzenal. ⏎  ⏎ Saucer-shaped, it can deploy onboard chainsaws and spin at a high speed to charge at its targets and slice them apart. ⏎  ⏎ They can also be applied to purposes other than assaults, such as when they were loaded with wires to capture Tanya and Irma's machines.

### dic\_robot\_PLOID\_00\_1

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b008`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b008\]
> JP (źródło tłumaczenia): 　ミスルギ皇国での戦闘でも相当数が投入され、アウローラを苦しめた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Many Pyrethroids were deployed in the battle in the Empire of Misurugi as well, causing issues for the Aurora.

### dic\_robot\_ULSKGNA\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b009`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b009\]
> JP (źródło tłumaczenia): 　高い機動性を誇るプライムドレス（強攻防護機械化装甲歩兵）。 ⏎ 　ジェットボードによる立体的な機動を駆使する事で高い空戦性能を発揮する。 ⏎ 　本機は強襲強化型に分類され、このカラーリングは「鋼鉄の魔女」と呼ばれるエースパイロットのもの。 ⏎ 　ウルスラグナにはその他にも統合歩兵型、支援電子戦型などのバリエーションが存在する。
> EN (odniesienie oficjalne, NIE polski): A Pr.A.I.M.D.Re.S.S. (an assault/defense mechanized armored foot soldier) featuring high mobility. ⏎  ⏎ Its jet board enables three-dimensional maneuvers, giving it excellent aerial combat capabilities. ⏎  ⏎ This Urs Ragnar is classified as a powered assault type, and its coloration belongs to the ace pilot known as the Steel Witch. ⏎  ⏎ Other variations of the Urs Ragnar exist, such as an integrated foot soldier type and a support/electronic warfare type.

### dic\_robot\_NLVASHUZ\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00b`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b00b\]
> JP (źródło tłumaczenia): 　封印から解き放たれたニルヴァーシュＺの最終形態。 ⏎ 　圧倒的な力を持つと同時に、その存在はレントン・サーストン生存の証でもあり、エウレカとレントンを結ぶものである。
> EN (odniesienie oficjalne, NIE polski): The final form of Nirvash Z when released from its seal. ⏎  ⏎ Possessing incredible strength, its existence is both proof of Renton Thurston's survival and the link between Eureka and Renton.

### dic\_robot\_SHINK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00d`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b00d\]
> JP (źródło tłumaczenia): 　ゼロ専用のＫＭＦ。 ⏎ 　可変機構を搭載し、フォートレスモードへと変形可能になっており、高速飛行だけでなく水中航行も可能。 ⏎ 　黒の騎士団用の機体からの派生機ではあるが、ガウェインのドルイドシステムを転用した事で驚異的な演算能力を誇る。世界最高の防御力を誇ると言われる強力な防御フィールド「絶対守護領域」を最適な状態で使用するためには、周囲の状況を瞬時、かつ的確にドルイドシステムに入力する必要がある。 ⏎ 　また、胸部には固体状の液体金属を発射し、そこに粒子砲を照射する事で液体金属が粒子を拡散させる拡散構造相転移砲が装備されている。 ⏎ 　この特徴的な二つの攻防の装備を使いこなすには、ドルイドシステムの力を引き出すだけの高度な情報処理能力が必要とされる。そのため、ルルーシュ以外の者では、操縦する事が出来ても性能を十分に引き出す事は出来ないとされている。 ⏎ 　ゼロが黒の騎士団から追われた際、ロロが逃亡用として奪ったため、最後までルルーシュの乗機となり、ブリタニア皇帝としても搭乗した。 ⏎ 　最終決戦ではフレイヤの爆発を止めるため、フレイヤ・エリミネーターを搭載して出撃。爆発までの１９秒の間に環境データを打ち込み、スザクとの共同プレイでフレイヤの阻止に成功した。 ⏎ 　最後はダモクレス内でジノの乗るトリスタン・ディバイダーに撃破された。
> EN (odniesienie oficjalne, NIE polski): A KMF built specifically for Zero. ⏎  ⏎ Equipped with transforming capabilities, it can change into Fortress Mode, allowing it to move at high speed in the air and even when submerged in water. ⏎  ⏎ While technically developed from the machines of the Order of the Black Knights, it inherits Gawain's Druid System, giving it overwhelming processing power. Using its trump card, the defensive field "Absolute Defense System" which is supposedly the strongest defensive system in the world, requires instantly and accurately inputting the surrounding environment into the Druid System. ⏎  ⏎ Furthermore, it possesses a chest-mounted weapon called the Diffusion Structure Phase Transition Cannon, which fires a liquid metal structure that is then struck with particles, with the metal dispersing the particles as an offensive system. ⏎  ⏎ Both of these emblematic tools for offense and defense require extremely advanced information processing skills to use the Druid System to its full capabilities. As a result, while the machine can technically be piloted by someone other than Lelouch, it's generally thought that no one else could meaningfully bring out its true capabilities. ⏎  ⏎ While originally stolen by Rolo to use in his escape, it eventually ended up in Lelouch's hands, and he continued to use it even after being crowned the Britannian Emperor. ⏎ In the final battle, it carried a F.L.E.I.J.A. Eliminator to prevent the detonation of a F.L.E.I.J.A. Inputting the necessary data in the nineteen seconds leading up to its explosion, it was able to prevent the F.L.E.I.J.A.'s detonation with Suzaku's help. ⏎  ⏎ It would meet its ultimate end at the hands of the Tristan Divider piloted by Gino.

### dic\_robot\_RANSAR\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b00f`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b00f\]
> JP (źródło tłumaczenia): 　スザクの専用機としてキャメロットで開発された機体。 ⏎ 　先行して開発された紅蓮聖天八極式と共に第九世代に相当するＫＭＦで、この世代のＫＭＦは、この二機しか存在しないため、あらゆる面で他の機体を圧倒した。 ⏎ 　最大の特徴は、エナジー・ウイングを備えた事で飛躍的に機動性、運動性が向上した事である。さらにエナジー・ウイングは、ブレード状のエネルギーを放出する事で攻撃面で使用したり、ブレイズ・ルミナスのように機体を覆う事で防御面で使用したりする事も可能となっている。 ⏎ 　その優れた機体性能とスザクの能力とを合わせる事でラウンズ専用機さえも一撃で粉砕。皇帝ルルーシュの力の象徴として全世界の恐怖と憎しみの対象となった。 ⏎ 　最終決戦では藤堂の乗る斬月、星刻の乗る神虎等のエース機を相手に一歩も退かず、フレイヤ・エリミネーター完成までの時間を稼ぎ、さらにはコンマ０４秒しかない時間でフレイヤ・エリミネーターを投擲し、フレイヤの爆発を止めている。 ⏎ 　ダモクレス突入後は宿敵カレンと対峙。互いに死力を尽くしての戦いは相討ちとなり、紅蓮聖天八極式の拳をコックピットに受けて爆発した。
> EN (odniesienie oficjalne, NIE polski): A machine developed by Camelot for Suzaku's sole use. ⏎  ⏎ Together with the extant Guren S.E.I.T.E.N. Eight Elements, these machines represent the entirety of the ninth generation of KMF development—no other ninth-generation machines exist. ⏎  ⏎ The biggest transformation compared to older models is the addition of the Energy Wing system, which significantly improved the KMF's aerial speed and mobility. The Energy Wing can also be fired out in the shape of blades, as well as deployed about the machine to protect it similarly to the Blaze Luminous. ⏎  ⏎ This capable machine, in Suzaku's equally capable hands, proved a combination strong enough to destroy one of the Knight of the Round's personal machines in a single blow. It eventually became a symbol of fear across the world as it was associated with the power of Emperor Lelouch. ⏎  ⏎ In the final battle, it matched off against Tohdoh in the Zangetsu and Xingke in an ace model of the Shen Hu, buying time to complete the F.L.E.I.J.A. Eliminator, and also was able to toss the Eliminator to stop the F.L.E.I.J.A.'s detonation with only .04 seconds left. ⏎  ⏎ After breaking into Damocles, he faced off against his long-time rival Kallen. Both fought to the utmost of their ability and struck a simultaneous finishing blow to each other, but the Guren S.E.I.T.E.N. Eight Elements' fist landed on the Lancelot Albion's cockpit, causing it to explode.

### dic\_robot\_RANSR\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b011`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b011\]
> JP (źródło tłumaczenia): 　Ｃ．Ｃ．の搭乗機としてロイドとセシルがランスロットの予備パーツから組み上げたＫＭＦ。 ⏎ 　武装は旧ランスロットと同様で、カラーリング、パーシヴァルのミサイルシールドが追加された事、脱出機構が装備された事が主な違いとなる。 ⏎ 　最終決戦でカレンの乗る紅蓮聖天八極式と戦闘。ルルーシュを逃がすだけの時間は稼ぐも、その圧倒的な機体性能差とパイロットの技量の差から全く歯が立たずに撃墜された。
> EN (odniesienie oficjalne, NIE polski): A KMF made by Lloyd and Cecile out of spare Lancelot parts for C.C.'s use. ⏎  ⏎ Its equipment is essentially the same as previous Lancelot generations, with the addition of unique coloring, Percival's missile shield, and an escape system. ⏎  ⏎ In the final battle, it faced off against Kallen's Guren S.E.I.T.E.N. Eight Elements to buy time for Lelouch to escape, though it would ultimately be unable to overcome both the tremendous difference in machine quality and pilot skill, leading to its inevitable defeat.

### dic\_robot\_SZRNDZK\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e20b013`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e20b013\]
> JP (źródło tłumaczenia): 　ジークフリートのシステムをベースに開発された、ジェレミア専用のナイトギガフォートレス。 ⏎ 　機体下部に大型リニアライフル、上面にミサイルポッド、さらに各部に５つの大型スラッシュハーケンを装備し、全領域に対応する高い攻撃力を持つ。 ⏎ 　ただし、操縦には神経電位接続が必要なため、操縦者はジェレミアに限られている。 ⏎ 　なお、コックピット部分は下半身を簡易型可翔ユニットに換装したサザーランドＪとなっている。 ⏎ 　最終決戦でアーニャの乗るモルドレッドと戦い、シュタルクハドロン砲の直撃を受ける。しかし、残ったサザーランドＪでモルドレッドに取り付き、自爆によって中破に追い込んだ。
> EN (odniesienie oficjalne, NIE polski): A Knight Gigafortress made for Jeremiah's own use, based on the systems of the Siegfried. ⏎  ⏎ It carries an enormous Linear Rifle mounted below it, with missile pods on the top and five upscaled Slash Harkens distributed evenly, allowing it to engage enemies from any angle. ⏎ However, it must be controlled through a direct neural connection, and thus only Jeremiah is able to pilot it. Its cockpit is a Sutherland J with a stand-in flight unit equipped. ⏎  ⏎ It faced off against the Mordred piloted by Anya in the final battle, where it suffered a direct blow from the Stark Hadron cannon. ⏎  ⏎ However, the Sutherland J cockpit module remained intact, which Jeremiah used to grab onto the Mordred and self destruct, crippling it.

### dic\_robot\_GURENSE\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b000`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b000\]
> JP (źródło tłumaczenia): 　中華連邦の戦いで鹵獲されブリタニアに引き渡された後、ロイドとセシルによって全面的に改造を施された紅蓮。 ⏎ 　ロイド曰く、ラクシャータの機体だったからいじりやすかったとの事で、二人共、気付くと趣味が全開になり、使いこなせる者がほとんどいない程の高性能な機体を造り上げてしまった。 ⏎ 　スザク以外は乗りこなせないと思われていた機体だったが、咲世子に救い出されたカレンが搭乗。６０％の出力でランスロット・コンクエスターを圧倒している。その機体性能は第九世代に相当し、スペックでは同じ第九世代ＫＭＦランスロット・アルビオンすら凌駕している。 ⏎ 　飛翔滑走翼に代わり、エナジー・ウイングを装備。その翼で全身を覆い、防御姿勢を維持したまま高速飛行する事も可能となっている。 ⏎ 　徹甲砲撃右腕部にも改良が加えられ、スラッシュハーケンのように射出し、有線で軌道をコントロールする事で遠距離の相手にも輻射波動を使う事ができる。また、輻射波動を円盤状にして投げつける事も可能。 ⏎ 　聖天八極という名は初出撃の際に咲世子が起動画面に表示された文字の「Ｓｕｐｅｒｌａｔｉｖｅ　Ｅｘｔｒｕｄｅｒ　Ｉｎｔｅｒｌｏｃｋｅｄ　Ｔｅｃｈｎｏｌｏｇｙ　Ｅｘｃｌｕｓｉｖｅ　Ｎｅｘｕｓ　ＥＩＧＨＴ　ＥＬＥＭＥＮＴＳ」を日本語に変えた事から付けられている。 ⏎ 　最終決戦ではスザクの乗るランスロット・アルビオンと死闘を演じるも、両者の力は拮抗。最後は両者相討ちの格好となるが、紅蓮の拳はランスロット・アルビオンのコックピットを破壊した。アルビオンは爆発し、因縁の対決はカレンと紅蓮の勝利によって幕を閉じるのであった。
> EN (odniesienie oficjalne, NIE polski): A version of the Guren that benefits from an overall upgrade provided by Lloyd and Cecile after its capture during battle in the Chinese Federation, where it was given over to Britannia. ⏎  ⏎ As one of Rakshata's machines, they found it easy to rework, eventually ending up with them transforming the machine without any concern except their own amusement. As a result, it became so incredibly powerful that there was essentially no one left who could actually pilot it. ⏎  ⏎ At first it was believed only Suzaku could pilot it, but Kallen proved up to the task after being rescued by Sayoko. At sixty percent of its potential it overwhelmed the Lancelot Conquista. ⏎  ⏎ Its capabilities make it the ninth generation of KMF development, and on paper it should outperform the other ninth-generation machine, the Lancelot Albion. In place of its original Air Glide system it has an Energy Wing, which can be deployed across the machine's entire body to allow high-speed flight in a defensive stance. ⏎  ⏎ The armament in its right arm was upgraded to allow it to be fired out like a Slash Harken, where it could then be controlled by wire in midair to fire the Wave Surger remotely. Said Wave Surger also gained the ability to be thrown in a circular shape. ⏎  ⏎ Its name S.E.I.T.E.N. EIGHT ELEMENTS means "Superlative Extruder Interlocked Technology Exclusive Nexus EIGHT ELEMENTS", according to the bootup screen seen by Sayoko during its first outing, simply translated to Japanese. ⏎  ⏎ In the final battle it fought an all-out battle against Suzaku in the Lancelot Albion, where they proved equally matched. The two struck what seemed to be a simultaneous finisher to the other, but Guren's fist connected with the Lancelot Albion's cockpit. With the resulting explosion of the Albion, Kallen ended up the victor in their long rivalry.

### dic\_robot\_YzCLOWN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b002`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b002\]
> JP (źródło tłumaczenia): 　ユザーパーの駆る機動兵器。 ⏎ 　Ｙｚルーンドラッヘと同じく搭乗者の精神エネルギーを動力とする事に加え、エーアデントへの挑発もあり、「Ｙｚ」の名を冠している。 ⏎ 　基礎設計には八神テツロウも関与しているが、「黒の英知」を手に入れたユザーパーの手により、既存のテクノロジーとは全く異なるシステムも組み込まれている。その正体不明の動力機関が生み出す圧倒的な出力と解明不能の力により、計り知れない戦闘力を持つ。
> EN (odniesienie oficjalne, NIE polski): The mobile weapon piloted by Usurper. ⏎  ⏎ As it can convert the pilot's mental energy into power—just like the Yz-Lunedrache—and as a direct challenger to the A. Advent, he has given it the same "Yz" moniker. ⏎  ⏎ While Tetsuro Yagami was involved in the basic design, Usurper was able to put together a completely original system unlike anything modern technology can make after getting his hands on the Dark Wisdom. ⏎  ⏎ Its combat capabilities are impossible to calculate thanks to the overwhelming output of its mysterious power source and its unfathomable abilities.

### dic\_robot\_RYAB\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b004`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b004\]
> JP (źródło tłumaczenia): 　ガーディムの攻撃機。 ⏎ 　主に一般兵士や制御ＡＩが搭乗する。 ⏎ 　複数の機体による連係攻撃を基本戦術とするが、単独でも高い戦闘力を有する。 ⏎ 　なお、用途に応じて腕部は換装可能であり、上級攻撃機ブラーマグも主機関が搭載されている胴体部は共通である。
> EN (odniesienie oficjalne, NIE polski): An advanced Gardim assault unit. Generally piloted by a grunt soldier or an AI. ⏎  ⏎ It's deployed chiefly in groups for coordinated tactics, but it's powerful enough on its own. ⏎  ⏎ Its arm equipment can be swapped out to adapt to different use cases. The more advanced assault model, Blarmag, uses the same chest section that houses its main engine.

### dic\_robot\_ORCDN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b006`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b006\]
> JP (źródło tłumaczenia): 　クエスターズの機動兵器。 ⏎ 　オルクスーラ素体に格闘戦用の腕部を装備させている。 ⏎ 　砲撃戦用のオルクスーラ・インとの連係戦術を基本とする。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon employed by the Quaestors. ⏎  ⏎ This Orcusula frame has been equipped with arms designed for melee combat. ⏎  ⏎ Usually deployed as a team with the long-range-focused Orcusula In.

### dic\_robot\_ORCIN\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b008`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b008\]
> JP (źródło tłumaczenia): 　クエスターズの機動兵器。 ⏎ 　オルクスーラ素体に砲撃戦用装備を加えている。 ⏎ 　格闘戦用のオルクスーラ・ダンとの連係戦術を基本とする。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon employed by the Quaestors. ⏎  ⏎ This Orcusula frame has been equipped with long-range weaponry. ⏎  ⏎ Usually deployed as a team with the melee-focused Orcusula Dan.

### dic\_robot\_ORCZNG\_00\_0

Adres: `dic\_text\_robot-DLC3/000013a2:4e60b00a`

> \[BRAK PL: dic\_text\_robot-DLC3/000013a2:4e60b00a\]
> JP (źródło tłumaczenia): 　クエスターズの機動兵器。 ⏎ 　オルクスーラ・ダインのカスタム機であり、実行部隊隊員クェーサーの搭乗を前提としており、自律システムで稼働する友軍機の指揮を執る。 ⏎ 　各部も強化されており、戦闘力はオルクスーラ・ダインの１３０％を計測する。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon employed by the Quaestors. ⏎  ⏎ A customized Orcusula Dyne model, this machine is built under the presumption it will be piloted by the executor team members of the Quasars, and is capable of commanding the automated systems loaded into nearby allies. ⏎  ⏎ Enhanced on every level, this model has an estimated 130% the power of a standard Orcusula Dyne.

### dic\_robot\_YCLOWN\_00\_0

Adres: `dic\_text\_robot-DLC3/000b6d41:ab20b000`

> \[BRAK PL: dic\_text\_robot-DLC3/000b6d41:ab20b000\]
> JP (źródło tłumaczenia): 　Ｙｚクラウンの量産タイプ。 ⏎ 　瞬間最大出力はＹｚクラウンに及ばないものの、解析不能の動力機関から生み出す高出力により、高い戦闘力を持つ。 ⏎ 　同時に機体サイズにそぐわない高い耐久力を持ち、互いをカバーする集団戦において真価を発揮する。
> EN (odniesienie oficjalne, NIE polski): The mass-produced Yz-Clown. ⏎  ⏎ Though it can't match the burst output of the real Yz-Clown, its mysterious power source gives it more than enough energy to be highly dangerous in a fight. ⏎  ⏎ Despite its size, it also possesses incredible durability and uses crowd tactics to cover its comrades, making it perform best in a team.

### dic\_robot\_BRMAG\_00\_0

Adres: `dic\_text\_robot-DLC3/000b6d41:ace0b001`

> \[BRAK PL: dic\_text\_robot-DLC3/000b6d41:ace0b001\]
> JP (źródło tłumaczenia): 　ガーディムの上級攻撃機。 ⏎ 　主に二等武官（部隊長クラス）が搭乗する。 ⏎ 　下級攻撃機アールヤブと主機関は共通であるが、機動力と運動性能は大きく向上しており、一撃離脱戦法を得意とする。 ⏎ 　また、火力においてもアールヤブを凌駕し、主兵装のサイド・インパルサーはアールヤブのフォトン・インパクター以上の出力と速射性を誇る。
> EN (odniesienie oficjalne, NIE polski): An advanced Gardim assault unit. Generally piloted by a second class officer, equivalent to a squad captain. ⏎  ⏎ It shares its primary engine system with the inferior Arlyabu, but its mobility and maneuverability are vastly improved, making it better suited for hit-and-run tactics. ⏎  ⏎ Its firepower also eclipses the Arlyabu. Its primary weapon, the Side Impulser, completely outclasses the Arlyabu's Photon Impactor in both destructive power and projectile speed.

### dic\_robot\_CALIBARN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:96c28000`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:96c28000\]
> JP (źródło tłumaczenia): 　オックス・アース社とヴァナディース機関が開発した試作機。 ⏎ 　GUND-ARMの性能を最大限に引き出す事を目的に設計されている一方、データストームの軽減フィルターが搭載されていないため、パイロットはダイレクトにデータストームを浴びるため苦痛と命の危険に晒される。 ⏎ 　主武装は、高威力を誇るバリアブルロッドライフル。 ⏎ 　後端部には４基の推進ユニット「クアドラ・スラスター」が接続されており、追加推進装置としても運用することが可能。 ⏎ 　ヴァナディース事変の際に宇宙議会連合が押収し、極秘裏に保管されていた。
> EN (odniesienie oficjalne, NIE polski): A prototype unit developed by Ochs Earth and the Vanadis Institute. ⏎  ⏎ Although it was designed to maximize the performance of a GUND-ARM, it lacks a defense against data storms. Consequently, the pilot is directly exposed to data storms, which subjects them to mortal danger and intense pain. ⏎  ⏎ Its main armament is the Variable Rod Rifle, which boasts high firepower. ⏎ Four propulsion units, called Quadra Thrusters, are connected to the rear section and can be used as additional propulsion devices. ⏎  ⏎ It was confiscated by the Space Assembly League during the Vanadis Incident and stored in secret.

### dic\_robot\_DEMIBARD\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828000`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828000\]
> JP (źródło tłumaczenia): 　ブリオン社が企画開発中のデミシリーズ新型コンセプトモデル。 ⏎ 　採算度外視のスペックながら、シリーズの特徴である設計や優秀な整備性は確保されている。 ⏎ 　フライトユニット機能を備えた「バオリパック」を背面に装備できる。
> EN (odniesienie oficjalne, NIE polski): A new concept model in the Demi series, currently being planned and developed by Burion Company. ⏎  ⏎ Although its specifications disregard profitability, the design and ease of maintenance that are hallmarks of the series have been preserved. ⏎  ⏎ It can equip the Baori Pack on its back, providing the unit with flight capabilities.

### dic\_robot\_LFRITH\_UR\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828002`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828002\]
> JP (źródło tłumaczenia): 　GUND-ARM搭載型のモビルスーツ。 ⏎ 　ヴァナディース事変以前にオックス・アース社が開発したガンダム・ルブリス量産試作モデルをベースに、各種の改良が加えられている。 ⏎ 　反スペーシアン組織「フォルドの夜明け」に提供された。 ⏎ 　主武装は、高速連射が可能なビームガトリングガン。 ⏎ 　背面に装備したユニット「フェーズドアレイキャノン」はパーメットスコアの上昇に合わせて展開し、モビルスーツ型ガンビット「ガンヴォルヴァ」の制御に使用される。
> EN (odniesienie oficjalne, NIE polski): A GUND-ARM-type Mobile Suit. ⏎  ⏎ Based on the mass-production prototype model of the Gundam Lfrith developed by Ochs Earth before the Vanadis Incident, it has undergone various improvements. ⏎  ⏎ It was provided to the anti-Spacian organization Dawn of Fold. ⏎  ⏎ Its main armament is a Beam Gatling Gun capable of high-speed rapid fire. The Phased Array Cannon mounted on its back deploys in accordance with an increase in Permet Score and controls Gundvolvas, GUND-Bits in Mobile Suit form.

### dic\_robot\_LFRITH\_TH\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828004`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828004\]
> JP (źródło tłumaczenia): 　GUND-ARM搭載型のモビルスーツ。 ⏎ 　兄弟機であるルブリス・ウルと同様にルブリス量産試作モデルをベースに開発されている。 ⏎ 　反スペーシアン組織「フォルドの夜明け」に提供された。 ⏎ 　主武装は、大型ビーム兵器のビームディフューズガン。 ⏎ 　パーメットスコアの上昇に合わせて背面に装備したユニット「フェーズドアレイキャノン」が展開し、モビルスーツ型ガンビット「ガンヴォルヴァ」の制御が可能となる。
> EN (odniesienie oficjalne, NIE polski): A GUND-ARM-type Mobile Suit. ⏎  ⏎ Like its sibling unit, the Lfrith Ur, it was developed based on the Lfrith mass-production prototype. ⏎  ⏎ It was provided to the anti-Spacian organization Dawn of Fold. Its main armament is the Beam Diffuse Gun, a large beam weapon. As Permet Score rises, the Phased Array Cannon mounted on its back deploys, enabling control of the Gundvolvas, GUND-Bits in Mobile Suit form.

### dic\_robot\_GUNDVOLVA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828006`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828006\]
> JP (źródło tłumaczenia): 　モビルスーツ型ガンビット。 ⏎ 　GUNDフォーマットが組み込まれた無人機であり、ガンダム・ルブリス・ウルとガンダム・ルブリス・ソーンによって制御される。
> EN (odniesienie oficjalne, NIE polski): A GUND-Bit in Mobile Suit Form. ⏎  ⏎ It is an unmanned unit integrated with the GUND Format and controlled by the Gundam Lfrith Ur and the Gundam Lfrith Thorn.

### dic\_robot\_DRLBLDE\_2S\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828008`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828008\]
> JP (źródło tłumaczenia): 　ジェターク社が開発した第５世代実証機。 ⏎ 　意思拡張AIによって自律行動を行う新型ドローン兵器を装備している。 ⏎ 　ガンダム・エアリアルとの再度の決闘の際に改修され、ドローン機能を有する攻撃ユニット「グスサー・イーシュヴァラ」と大型シールド形状の防御用ドローンユニット「ダヤ・アンビカー」を装備し、ビームショットライフルと折り畳み式のビームカタナに分離可能な新型携行装備「コンポジットアームズ」を携行するようになった。
> EN (odniesienie oficjalne, NIE polski): A fifth-generation demonstration machine developed by Jeturk Heavy Machinery. ⏎  ⏎ It is equipped with new drone weaponry that operates autonomously via a Decision Making Extension AI. ⏎  ⏎ Modified for a renewed duel with the Gundam Aerial, it is now equipped with the "Gussa Isvara" attack unit, which has drone functions; the large, shield-shaped "Daya Ambika" defensive drone unit; and a handheld armament called the Composite Arms, which separates into a Beam Shot Rifle and a folding Beam Katana.

### dic\_robot\_GDPHARCT\_5GO\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800a`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782800a\]
> JP (źródło tłumaczenia): 　ペイル社が秘密裏に開発したGUNDフォーマット搭載機 ⏎ 　ブラストブースターの採用や、GUNDフォーマットによる慣性制御の高次化により、飛行性能が大幅に向上している。 ⏎ 　主武装である二挺のビームガン「ビームカリヴァ」は、連結する事で高火力な「ビームマスケット」としても使用可能。
> EN (odniesienie oficjalne, NIE polski): A GUND Format-equipped unit secretly developed by Peil Technologies. ⏎  ⏎ Its flight performance has been greatly improved through the adoption of Blast Boosters and the high dimensional inertial control enabled by the GUND Format. ⏎  ⏎ Its main armament, a pair of beam guns known as Beam Calivers, can be linked together to form the high-output Beam Musket.

### dic\_robot\_SCHWARZ\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800c`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782800c\]
> JP (źródło tłumaczenia): 　ジェターク社が開発していた次世代コンセプトモデル「シュバルゼッテ」にGUNDフォーマットを組み込んだモビルスーツ。 ⏎ 　開発は凍結状態が続いていたが、プロスペラ・マーキュリーからの技術提供によって、GUND-ARMとして完成した。 ⏎ 　多目的攻防プラットフォーム「ガーディアン」は、エアリアルのエスカッシャンと同様にガンビットで構成されており、状況に応じて三種のモードに切り替えて使用される。
> EN (odniesienie oficjalne, NIE polski): A Mobile Suit incorporating the GUND Format into the next-generation concept model, the Schwarzette, that Jeturk Heavy Machinery had been developing. ⏎  ⏎ Although development had stalled, Prospera Mercury provided the technical support needed to complete it as a GUND-ARM. ⏎  ⏎ It is equipped with the Guardian, a multipurpose offensive/defensive platform modeled after the Aerial's Escutcheon. The Guardian is composed of GUND-Bits and can switch between three configurations depending on the situation.

### dic\_robot\_GDARRALRB\_E\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782800e`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782800e\]
> JP (źródło tłumaczenia): 　シン・セー開発公社によって改修されたガンダム・エアリアル。 ⏎ 　グラスレー寮との決闘で負ったダメージを修繕しつつ、外部装甲や装備類の刷新・追加が行われた。 ⏎ 　装甲形状の更新によって、シェルユニットの露出範囲が拡大し、専用フライトユニットには回転式展開翼が採用され、飛行時の旋回能力が大幅に向上。
> EN (odniesienie oficjalne, NIE polski): The Gundam Aerial after it was improved by Shin Sei Development Corporation. ⏎  ⏎ In addition to repairing the damage it sustained in the duel with Grassley House, its external armor and equipment were renewed and augmented. ⏎  ⏎ The updated armor configuration expands the exposed area of the shell units, and the dedicated flight unit's adoption of rotating deployable wings greatly improves its turning capability during flight.

### dic\_robot\_GUNDNODE\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828010`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828010\]
> JP (źródło tłumaczenia): 　モビルスーツ型ガンビット。 ⏎ 　プロスペラ・マーキュリー主導のもと、クワイエット・ゼロと並行して開発され、データストーム空間を増幅させる中継器としての役割を持つ。 ⏎ 　アーマーパックを装備することでモビルアーマーとしても運用される。
> EN (odniesienie oficjalne, NIE polski): A GUND-Bit in Mobile Suit Form. ⏎  ⏎ Developed under the leadership of Prospera Mercury in parallel with Quiet Zero, it serves as a relay that amplifies the data storm space. ⏎  ⏎ With an armor pack, it can also be operated as a Mobile Armor.

### dic\_robot\_GKEK2\_WN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828012`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828012\]
> JP (źródło tłumaczenia): 　指揮官用の複座式大型ＫＭＦ（ナイトメアフレーム）。 ⏎ 　月虹影帥を開発者である超合集国の世界科学委員会会長ラクシャータとその私設研究機関パール・パーティーがアップデートした機体。
> EN (odniesienie oficjalne, NIE polski): A large dual-seat Knightmare Frame for commander-use. ⏎  ⏎ An upgraded version of the Gekkoei Sui, the upgrade project was designed by its original developer Rakshata, chairman of the United Federations of Nations' Scientific Committee, and by her own private foundation, the Pearl Party.

### dic\_robot\_MAGDA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828014`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828014\]
> JP (źródło tłumaczenia): 　「ウツロ」の一部が三次元世界でとる姿。 ⏎ 　「ウツロ」は全てが一つであり、グーゴル・プレックスも虚獣マグダも根本的には同一の存在であるが、その中で知性から切り離された部分が虚獣マグダとなる。 ⏎ 　そのため目的や意思といったものはなく、ただひたすらに「ウツロ」以外の存在に対して攻撃を仕掛ける。 ⏎ 　三次元世界においてサイズや形状は不定であるが、人類との戦いの際に最も効率的な形状として、この姿を取ることが多い。 ⏎ 　「ウツロ」の知性とも言えるグーゴル・プレックス（に擬態した部分）は姿を現す事がなかったため、人類にとって「ウツロ」とは、主にこの虚獣マグダを指す事になる。
> EN (odniesienie oficjalne, NIE polski): The form that a part of the Void assumed within the three-dimensional world. ⏎  ⏎ The Void is a single entity, and both Googolplex and the Void Beast Magudda are fundamentally the same existence. However, the portion of the Void separated from intellect becomes the Void Beast Magudda. ⏎  ⏎ For this reason, it has no purpose or will and simply attacks any existence other than the Void. ⏎  ⏎ Its size and shape in the three-dimensional world are indefinite; however, in battles with humanity, it often assumes this form, deemed the most efficient. ⏎  ⏎ As this form lacks the intellect of the Void manifested in Googolplex, in the eyes of the general public, the Void Beast Magudda represents the Void.

### dic\_robot\_RAGMADOC\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828016`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828016\]
> JP (źródło tłumaczenia): 　「ウツロ」の三次元世界での姿。 ⏎ 　高次元にある「ウツロ」の本体とも言える存在は形を持たないが、三次元世界に物理的な干渉をするため、このような形態を取る。 ⏎ 　「個」という概念を持たない「ウツロ」には他者との識別のための名前も不要であったが、人類との接触により、この名を名乗るに至った。なお、「神」という概念を正確に理解しているわけではなく、「巨大な存在」ぐらいのニュアンスで使っている。 ⏎ 　三次元世界においてもサイズや形状は自在ではあるが、この姿はエーアデントとの戦いのために最適なサイズと形状を選択した結果である。
> EN (odniesienie oficjalne, NIE polski): The form assumed by the Void in the three-dimensional world. ⏎  ⏎ Although the true body of the entity known as the Void has no definite shape in a higher dimension, it has taken on this form to interact with the three-dimensional world. ⏎  ⏎ The Void has no concept of individuality and had no need for a name to distinguish itself from others. However, through contact with humanity, it came to call itself by this name. It does not fully understand the concept of gods and uses the word broadly to refer to a gigantic being. ⏎  ⏎ While it can freely alter its size and shape in the three-dimensional world, it has chosen this appearance as the optimal form to fight the A. Advent.

### dic\_robot\_RE\_BLASTA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828018`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828018\]
> JP (źródło tłumaczenia): 　格闘戦用の「レッド」と射撃戦用の「ブルー」を統合したリ・ブラスタの最終完成形であり、全く新しいアプローチを試みた実験機。 ⏎ 　名称の「Ｔ」は、「Ｔｒｉａｌ」の意味。なお、この名称については、「Ｔ」が開発者のトライア・スコートのイニシャルであるとして、逆恨み的に不機嫌になる者が若干一名いた。 ⏎ 　基本的な戦術コンセプトは射撃戦用のブルーを踏襲しているため、小型化した「ＳＰＩＧＯＴ（物体の移動と変換のための空間確率領域干渉器）」を装備した「ＡＸ－９９ＲＡＰＴＯＲ（次世代兵器研究向け新型電磁加速銃精度試験モデル）」を主装備とする。 ⏎ 　同時に「レッド」で得たデータを活かすために前面の装甲と関節部を強化し、格闘戦にも対応する。 ⏎ 　これは戦術用途を絞り込む事で戦闘力を強化するという前バージョンのコンセプトに反するが、スフィアの事象制御を積極的に武装に反映させる事とオールラウンダーであるクロウの戦闘スタイルを積極的に活かす方向性の融合であり、結果として、スペック上では、あらゆる局面でレッド、ブルーを上回る戦闘力を発揮する機体として完成した。 ⏎ 　しかし、ブルーと比較して増加した重量をカバーするために出力を増大させるという対処を行なったため、速度は向上したが軌道変更が困難になったという扱いづらい機体となっており、クロウにはより高度な操縦能力が求められる事となった。 ⏎ 　超時空修復後は、失われたスフィアの代わりにハイ・プラズマバッテリーを主動力としている。
> EN (odniesienie oficjalne, NIE polski): The final form of the Li-Brasta, integrating the close-combat Red and ranged-combat Blue variants, representing a new design approach. ⏎  ⏎ The "T" stands for "Trial", though a certain resentful and displeased individual claims it stands for the initial of the developer, Tria Scott. ⏎  ⏎ Since its basic tactical concept follows the ranged-combat Blue variant, its main equipment is the AX-99 RAPTOR (Research-type Advanced Precision Testing Originative Railgun), fitted with a downsized SPIGOT (Sphere Probability-region Interference Gear for Object Transfer/Transform). To make use of the data obtained from the Red variant, the front armor and joints were reinforced to allow for close-combat capabilities. ⏎  ⏎ This contradicts the previous version's concept of strengthening combat power by narrowing tactical applications; instead, it embodies the fusion of two approaches: actively incorporating the Sphere's phenomenon control into its armaments and proactively leveraging Crowe's versatile combat style. As a result, it is a unit that outperforms the Red and Blue variants in every situation. ⏎  ⏎ It deals with the increased weight compared to the Blue variant by increasing its power output, which improves its speed but makes it difficult to handle. Once committed to a trajectory, it's difficult to deviate from it, so Crowe had to improve his piloting abilities to compensate. ⏎  ⏎ After time and space were fully mended, a high plasma battery was installed as its primary power source to replace the missing Sphere.

### dic\_robot\_MADIVIA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801a`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782801a\]
> JP (źródło tłumaczenia): 　ガーディムの指揮官用攻撃機であるマーダヴァのカスタム機。 ⏎ 　「デグ」は、ガーディムの言語で「秀でた、優れた」の意味を持つ。 ⏎ 　指揮官機としての索敵・通信機能はオミットされたが、追加されたフレキシブル・ウイングにより圧倒的な機動力を誇る。 ⏎ 　完成型であるマーダヴァにさらなる改良が加えられた経緯は、ガーディム以外の文明の技術の採用によるものであり、ガーディムを含む複数の文明の技術融合という点においてはヴァング・シリーズの兄弟機であるとも言える。
> EN (odniesienie oficjalne, NIE polski): A customization of the Madivia, the Gardim command unit. ⏎  ⏎ In the language of Gardim, "Degg" means "superior" or "excellent". ⏎  ⏎ Although the commander unit's search and communication functions have been omitted, the added flexible wings provide overwhelming mobility. ⏎  ⏎ Further improvements were added to the completed Madivia due to the adoption of technology from civilizations other than Gardim. In terms of being a fusion of technologies from multiple civilizations, including Gardim, it can also be considered a sibling unit of the Vang series.

### dic\_robot\_W\_DEENBELL\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801c`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782801c\]
> JP (źródło tłumaczenia): 　法師セルリック用に調整されたディーンベルのカスタム機。 ⏎ 　アル・ワースの名を冠しており、魔従教団にとって象徴とも言える機体。 ⏎ 　ディーンベルに設けられていた魔力増幅のリミッターは解除されており、搭乗者の魔力をダイレクトに増幅する。 ⏎ 　ディーンベルの長所である使いやすさにゼルガードの持つ無限の可能性を加えた形であり、その戦闘力はすさまじく、搭乗者であるセルリックの魔力も合わさり、圧倒的な力で教団の敵を葬ってきた。 ⏎ 　また、異界の門を開くドグマ「ＦＯＲＵＳ」を単独で使用する事も出来る。
> EN (odniesienie oficjalne, NIE polski): A custom version of the Deenbell tuned specifically for Celric. ⏎  ⏎ Bearing the name of Al-Warth, this unit is considered a symbol of the Keepers of Order. ⏎  ⏎ The original Deenbell's magical amplification limiter has been removed, allowing it to directly amplify the magical power of the priest piloting it. ⏎  ⏎ It combines the Deenbell's ease of use with the infinite potential of the Xelguard. Its combat power is immense, and with Celric's magical power, it has vanquished the enemies of the Keepers of Order with overwhelming force. ⏎  ⏎ Furthermore, it has the ability to independently invoke the Dogma FORUS, which opens gates to other worlds.

### dic\_robot\_EFAS\_OMEGA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782801e`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782801e\]
> JP (źródło tłumaczenia): 　エイム・プレズバンド搭乗を前提にカスタマイズされたイーファス。 ⏎ 　全艦隊司令ラグナヤル・ディンハーリッシュとの友情の証として、アールオールと同じく黒を基調としたカラーリングで塗装された。 ⏎ 　エイムの技量によって最大限の力を引き出され、他のＵＮＤの量産機動兵器とは一線を画す戦闘力を発揮する。
> EN (odniesienie oficjalne, NIE polski): The E-Phas customized for Ame Presbund. ⏎  ⏎ As proof of their friendship, Commander of Fleets Ragnayael Dynharish made this unit black to match his own A-Ruol. ⏎  ⏎ Its full power is drawn out by Ame's skills, making its combat performance markedly different from other UND mass-produced models.

### dic\_robot\_ORCUS\_BA\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828020`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828020\]
> JP (źródło tłumaczenia): 　クエスターズの機動兵器。 ⏎ 　オルクスーラ・ザングをオルキダケア用にカスタムしたものであり、意識を同機のシステムに移植させている彼女にとって肉体とも言える。 ⏎ 　一部は神文明エーオスの技術を導入しており、オルクスーラ・ザング以上の性能を誇るが、「先生」の意向によって外観はオルクスーラ・シリーズのままである事が強いられた。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon employed by the Quaestors. ⏎  ⏎ A further customization of the Orcusula Zang for Orchidacea's purposes, this system allows her to transfer her consciousness to all similar machines, essentially making them her body. ⏎  ⏎ Portions of it use technology from the Divine Civilization Aos, allowing it to perform even better than the Orcusula Zang, but by the Magister's command, its appearance is mandated to be the same as the rest of the Orcusula series.

### dic\_robot\_TIAMAT\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828022`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828022\]
> JP (źródło tłumaczenia): 　真理に到達しかけた地球人類「御使い」の組織した星間軍事連合サイデリアルが使用する機動兵器。 ⏎ 　基本的には無人機で、ＡＩによりコントロールされる。 ⏎ 　同コンセプトのデイモーンと比較して、火力と耐久力が大きく向上しており、総合的な戦闘力は通常配備型のアンゲロイに匹敵する。 ⏎ 　基本的にはデイモーンと共に戦場に投入されるが、量による戦術に高性能な本機の質が加わる事で陣形は厚みを増す事となる。
> EN (odniesienie oficjalne, NIE polski): Mobile weapons employed by Sidereal, an interstellar military alliance formed by the Heralds—Earthlings who sought the truth of all things. ⏎  ⏎ Fundamentally unmanned and AI controlled, the Tiamaht has considerably greater firepower and durability compared to the Daimon, with overall combat capabilities on par with the conventionally deployed Angeloi. ⏎  ⏎ Though traditionally deployed to combat zones alongside Daimons, their high-spec design provided a major impact, leading to their fielding in ever greater numbers.

### dic\_robot\_ANGELOI\_AL\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828024`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828024\]
> JP (źródło tłumaczenia): 　真理に到達しかけた地球人類「御使い」直轄の機動兵器。 ⏎ 　黒い装甲以外はアンゲロイと変わらない外観だが、源理の力（＝次元力）をダイレクトに使う事で圧倒的な堅牢さを誇る。 ⏎ 　通常配備のアンゲロイは、本機の安価なコピーでしかない。 ⏎ 　その宇宙の歴史において、サイデリアルが苦戦する戦場に現れ、圧倒的な力で抵抗勢力を蹂躙してきた伝説の機体であり、本機の存在を知る者は極めて少ない。同時にその者は、この機体の所有者である圧倒的な存在を感じ、限りない畏怖に永遠に襲われる事になると言われていた。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon in the direct service of the Heralds—Earthlings who sought the truth of all things. ⏎  ⏎ Aside from its black plating, it looks no different than other Angeloi units, but it utilizes Origin Law (dimensional power) directly to give itself tremendous durability. ⏎  ⏎ Angeloi units with standard loadouts are cheap imitations that pale in comparison to this model. ⏎  ⏎ In the history of its own universe, it is a legendary machine that crushed all opposition with overwhelming might when Sidereal appeared in the midst of an otherwise losing battle. ⏎  ⏎ Precious few even know of this machine's existence, and those who do know of it are said to have been left forever awestruck by the overwhelming being that possesses it.

### dic\_robot\_EL\_MILLEN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828026`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828026\]
> JP (źródło tłumaczenia): 　真理に到達しかけた地球人類「御使い」直轄の機動兵器。 ⏎ 　全身がＤＥＣ（ディメンション・エナジー・クリスタル／次元結晶）で構成されており、駆動、武装の全てが源理の力によるものである。 ⏎ 　主に霊体であるイドムが搭乗し、肉体や生への渇望をそのまま力に変え、生きているものを攻撃する。 ⏎ 　また、御使いが監視する星に１～３体が送り込まれ、御使いの意に反する進化の道を進みかけると目覚め、その文明を滅ぼす役目を持ち、銀河の伝承では「審判の巨獣」の名で恐れられている。 ⏎ 
> EN (odniesienie oficjalne, NIE polski): A mobile weapon in the direct service of the Heralds—Earthlings who sought the truth of all things. ⏎  ⏎ Its body is comprised of DEC, a.k.a. dimensional energy crystals, with dimensional energy providing power for its drive systems and weapons. ⏎  ⏎ They are generally controlled by spirits known as Idoms, whose thirst for life and physical form are converted into energy to attack the living. ⏎  ⏎ Planets under Herald surveillance are seeded with one to three El Millenniums. When a civilization begins pursuing a path of evolution in opposition to the Heralds, the El Millenniums awaken to annihilate it, making them feared throughout the galaxy as "Behemoths of Retribution". ⏎ 

### dic\_robot\_ZEL\_BILLEN\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:97828028`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:97828028\]
> JP (źródło tłumaczenia): 　真理に到達しかけた地球人類「御使い」直轄の機動兵器。 ⏎ 　全身がＤＥＣ（ディメンション・エナジー・クリスタル／次元結晶）で構成されており、駆動、武装の全てが源理の力によるものである。 ⏎ 　その堅牢な装甲と攻撃力により、天の川銀河における恒星間航行が可能な平均的な文明の惑星の軍ならば、２機程度で壊滅させる事も可能。 ⏎ 　アンゲロイ・アルカ、エル・ミレニウム以上に通常宇宙の戦線に投入される事は希であり、この１万２０００年の間に通常宇宙に派遣された事は３回しかない。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon in the direct service of the Heralds—Earthlings who sought the truth of all things. ⏎  ⏎ Its body is comprised of DEC, a.k.a. dimensional energy crystals, with dimensional energy providing power for its drive systems and weapons. ⏎  ⏎ With their formidable armor and weaponry, two Zel Billenniums are more than enough to send an average spacefaring civilization in the Milky Way back to the stone age. ⏎  ⏎ They are deployed in standard space battlefields with far less regularity than Angeloi Arcas and El Millenniums. In fact, Zel Billenniums have been fielded to normal space only three times in the past 12,000 years.

### dic\_robot\_STAMEN\_BI\_00\_0

Adres: `dic\_text\_robot-DLC4/000dfdee:9782802a`

> \[BRAK PL: dic\_text\_robot-DLC4/000dfdee:9782802a\]
> JP (źródło tłumaczenia): 　ＤＢＤ（次元境界線歪曲現象）を発生させる機動兵器。 ⏎ 　人間の精神をエネルギーとする事で次元を制御する技術は、現在の地球のテクノロジーとは全く異質のアプローチによるものであり、その正体は過去の高度な文明の遺物と推測されている。 ⏎ 　次元境界線が不安定な状態となった地球において、強い思念を持つ者の怨念を拾い、ＤＢＤを発生させ、結果として次元の壁を越えた敵『エトランゼ』を招いている。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon with the ability to cause DBDs (Dimensional Boundary Distortions). ⏎  ⏎ Its dimensional control technology, which operates by converting the human spirit into energy, represents a methodology entirely alien to all modern terrestrial weapons development. It is theorized to be an artifact of a highly advanced civilization from a past era. ⏎  ⏎ When the dimensional boundaries on Earth became unstable, they responded to the grudge of a being with tremendous mental power, triggering the DBDs that would bring the enemies from across dimensions known as the Etrangers.

## Seria / nazwa własna

### dic\_name\_BRVRDN\_00\_0

Adres: `dic\_text\_name/014d371a:c020b000`

> \[BRAK PL: dic\_text\_name/014d371a:c020b000\]
> JP (źródło tłumaczenia): 　悪魔世紀の復活を目論む妖魔帝国が１万２０００年の眠りから復活した。 ⏎ 　臨海学園でサッカー部キャプテンを務める少年・ひびき洸は、神秘の声に導かれ、神面岩に眠るライディーンへと向かう。 ⏎ 　導かれるままライディーンに「フェードイン」して乗り込んだ洸はムトロポリスのコープランダー隊と力を合わせ、妖魔帝国との戦いに身を投じる。 ⏎ 　妖魔帝国の指揮官、プリンス・シャーキンを打ち倒した洸であったが、石像に封印されていた妖魔大帝バラオが復活する。 ⏎ 　自らが古代ムー帝国の血を引く人間であり、母親がその皇女レムリアである事を知った洸は、バラオの送り込む恐るべき敵と戦っていく。
> EN (odniesienie oficjalne, NIE polski): After a sleep of 12,000 years, the Yoma Empire awakens to bring about a new Age of Demons. ⏎  ⏎ Akira Hibiki, captain of Seaside Academy's soccer team, is guided by a mysterious voice to Reideen, sleeping beneath the God Face Rock. After following the voice's directions to Fade In to Reideen, Akira throws himself into battle with the Yoma Empire, aiding the Co-oplanders of Mutropolis. ⏎  ⏎ Though Hibiki was able to defeat Prince Sharkin, commander of the Yoma Empire forces, he was unable to prevent Barao, the Yoma Emperor, from breaking free from the stone statue in which he was sealed.  ⏎  ⏎ After learning that he is a descendant of the ancient Empire of Mu, and that his mother was Empress Lemuria of Mu, Hibiki faces the terrifying foes sent his way by Barao.

### dic\_name\_BRVRDN\_00\_1

Adres: `dic\_text\_name/014d371a:c1e0b000`

> \[BRAK PL: dic\_text\_name/014d371a:c1e0b000\]
> JP (źródło tłumaczenia): 　コープランダー隊で共に戦ってきた神宮寺を失いながらも、ついに妖魔大帝バラオとの決戦を迎える洸。バラオの圧倒的な力の前に窮地に追い込まれるライディーンであったが、レムリアがその身を犠牲にして解放した神秘のエネルギー・ムートロンによって勝利をつかみ、世界は救われるのであった。
> EN (odniesienie oficjalne, NIE polski): After losing Jinguji, a member of the Co-oplanders who fought by his side, Akira finally arrives at his final battle with Yoma Emperor Barao. Reideen is pushed to its limits by Barao's overwhelming power, but is able to claim victory thanks to the mysterious mutron energy released when Lemuria sacrifices herself for her son. With Barao defeated, the world is saved.

### dic\_name\_CONV\_00\_0

Adres: `dic\_text\_name/014d371a:c220b000`

> \[BRAK PL: dic\_text\_name/014d371a:c220b000\]
> JP (źródło tłumaczenia): 　先史以来、長らく地底に潜んでいたキャンベル星人が地球侵略を開始した。 ⏎ 　この日を予見していた南原博士は、超電磁の力で５体のマシンが合体する巨大ロボのコン・バトラーＶを建造。日本全国から集めた葵豹馬、浪花十三、西川大作、北小介の４人に孫娘の南原ちずるを加えた「バトルチーム」を結成する。 ⏎ 　しかし、戦いの中で南原博士は生命を落とし、後は博士の友人であった四ッ谷博士に託される。 ⏎ 　キャンベル星人の大将軍ガルーダが送り込む敵を次々と退けたコン・バトラーＶは、アンドロイドであったガルーダを作り上げた女帝オレアナを打倒する。 ⏎ 　しかし、オレアナの死により、新たにキャンベル星から女帝ジャネラ、総統ワルキメデス、将軍ダンゲルらが地球に送り込まれる。 ⏎ 　キャンベル星で平和主義者による反乱が起きる中、コン・バトラーＶはジャネラとの決戦に勝利し、地球に平和をもたらすのであった。
> EN (odniesienie oficjalne, NIE polski): Aliens from Planet Campbell have been lurking deep inside the Earth since prehistoric times. As the new millennium approached, they were ready to begin their invasion of the planet. ⏎  ⏎ One man anticipated these events: Dr. Takeshi Nambara. He decided to stand against the Campbellian menace by developing five machines that would combine into a single, giant robot through the power of superelectromagnetism: Combattler V. He then selected five people from all over Japan who would form the Battle Team: Hyoma Aoi, Juzo Naniwa, Daisaku Nishikawa, Kosuke Kita, as well as his own granddaughter Chizuru Nambara. ⏎  ⏎ However, Dr. Nambara was critically injured during one of the early Campbellian assaults, entrusting the battle against Campbell to his best friend, Dr. Yotsuya, before passing away. ⏎  ⏎ After suffering repeated losses, the Great General Garuda of Campbell eventually discovered the truth: he was not the son of the Empress Oleana, but in fact an android she created. Feeling betrayed, Garuda killed Oleana, and then challenged Combattler V to mortal combat. In the end, the Battle Team stood victorious. ⏎  ⏎ However, after Oleana's demise, new threats came from Planet Campbell: the Empress Janera and her followers, Minister Warchimedes and General Dungele. ⏎  ⏎ Ultimately, Combattler V defeated Janera, and with Planet Campbell being led by a new pacifist faction, the war was over: Earth had earned its peace.

### dic\_name\_ZGN\_00\_0

Adres: `dic\_text\_name/014d371a:c220b002`

> \[BRAK PL: dic\_text\_name/014d371a:c220b002\]
> JP (źródło tłumaczenia): 　宇宙世紀００８７年。 ⏎ 　地球連邦軍がジオン公国軍と戦い、勝利した一年戦争から７年の月日が流れていた。 ⏎ 　連邦軍内で新たに台頭したエリート部隊・ティターンズは、コロニーや月面に住むスペースノイドへの弾圧を強行していた。 ⏎ 　勢力を拡大させるティターンズに反発する者達は、反地球連邦組織・エゥーゴを結成。その中には、かつてのジオン公国のエースパイロットであり、連邦に「赤い彗星」と呼ばれて恐れられたシャア・アズナブルもクワトロ・バジーナと名を変えて、参加していた。 ⏎ 　エゥーゴがティターンズの拠点であるコロニー・グリーンオアシスを襲撃した際、その争いに巻き込まれた少年カミーユ・ビダンは、ティターンズへの反発からエゥーゴに参加。パイロットとしてティターンズとの戦いに身を投じたカミーユは、ニュータイプとしての素質を開花させていく。 ⏎ 　戦局はエゥーゴとティターンズとの戦いにジオンの残党であるアクシズが加わった事で、三つ巴となっていった。 ⏎ 　状況を打破するためにエゥーゴは、制圧したコロニーレーザーの使用を画策する。 ⏎ 　その照射を阻止せんとするティターンズのパプテマス・シロッコと、アクシズのハマーン・カーンを相手にカミーユとクワトロは激闘をくり広げる。 ⏎ 　結果、コロニーレーザーは発射され、後に「グリプス戦役」と呼ばれるこの戦いは、大きな犠牲を払いながらもエゥーゴの勝利に終わる。 ⏎ 　しかし、ハマーンとの戦いの中でクワトロは行方不明となり、カミーユもシロッコとの激闘に勝利したものの、シロッコの最後の執念により精神を崩壊させてしまうのであった。
> EN (odniesienie oficjalne, NIE polski): Universal Century, Year 0087.  ⏎  ⏎ 7 years have passed since the One Year War, in which the Earth Federation Forces fought and emerged victorious against the troops of the Principality of Zeon. A new elite force within the Federation called the Titans now oppresses the Spacenoids living in the colonies and on the Moon's surface.  ⏎  ⏎ Those who oppose the Titans' expanding power have established the Anti Earth United Government, or AEUG. It includes ace pilots from the former Principality, and the feared Char Aznable, known as the "Red Comet", has joined under the alias "Quattro Bajeena". ⏎  ⏎ When AEUG attacks the Titans' base Colony Green Oasis, teenager Kamille Bidan is caught up in the battle and joins the AEUG rebellion against the Titans. Kamille throws himself into the fight as a pilot, and his natural talent as a Newtype blossoms.  ⏎  ⏎ A third group, the Zeon remnant faction Axis, eventually enters the war between AEUG and the Titans. AEUG schemes to use the powerful Colony Laser to gain an advantage in the war. Kamille and Quattro wage a fierce fight against Titans' Paptimus Scirocco and Axis' Haman Karn, who are trying to prevent the plan from coming to fruition. In the end, the Colony Laser is fired and AEUG emerges victorious, but this act also results in a large number of casualties. This war came to be known as the Gryps Conflict.  ⏎  ⏎ Quattro goes missing in action during a fight with Haman, and even though Kamille defeats Scirocco, he is psychologically broken by Scirocco's final blow.

### dic\_name\_GNCC\_00\_0

Adres: `dic\_text\_name/014d371a:c260b001`

> \[BRAK PL: dic\_text\_name/014d371a:c260b001\]
> JP (źródło tłumaczenia): 　宇宙世紀００９３年。 ⏎ 　グリプス戦役以降、行方不明となっていたシャア・アズナブルがネオ・ジオンの総帥に就任した。 ⏎ 　宇宙移民を抑圧して地球にしがみつく人類を粛清するため地球連邦に宣戦布告したシャアは、小惑星５ｔｈルナを地球に落下させようとする。アムロの所属する連邦軍の外郭部隊ロンド・ベルは、その阻止に奮戦するも、５ｔｈルナは地球に落下してしまう。 ⏎ 　その後、シャアは地球政府高官と裏取引を行い、ネオ・ジオンの武装解除を条件に、かつてのネオ・ジオンの小惑星要塞アクシズを手に入れる。しかし、シャアはその協定を破り、今度はアクシズを地球に衝突させるべく行動を開始する。 ⏎ 　その作戦を阻止するため、そしてシャアとの決着をつけるため、アムロは最新鋭モビルスーツ・νガンダムに搭乗し、アクシズを目指す。 ⏎ 　アクシズ上で激突するアムロとシャア。 ⏎ 　アムロは勝利するものの、ロンド・ベルは地球に落下していくアクシズの破壊に失敗する。 ⏎ 　既に大気圏に突入しつつあったアクシズを食い止めるため、アムロはνガンダムでアクシズに取りつき、これを押し返そうとする。 ⏎ 　νガンダムから発せられたサイコ・フレームの光はアクシズの落下を防ぎ、その温かな光は目撃した人達の心に何かを残していく。 ⏎ 　この戦いでアムロとシャアは共に行方不明となり、歴史から姿を消すのであった。
> EN (odniesienie oficjalne, NIE polski): Universal Century, Year 0093.  ⏎  ⏎ After the Gryps Conflict, Char Aznable, who had been missing in action, is appointed commander of Neo Zeon. He declares war on the Earth Federation, wanting to purge those that clung to Earth and held back the Space Colonies. He plans to drop an Asteroid called 5th Luna on Earth. Special force Londo Bell of the Earth Federation, of which Amuro is a member, fights to thwart his plans. It is in vain and 5th Luna eventually collides with Earth.  ⏎  ⏎ Later, Char makes a secret agreement with the Earth Federation government officials, in which the asteroid stronghold Axis would be transferred to Neo Zeon on the condition that Neo Zeon disarms.  ⏎  ⏎ However, Char breaks the agreement and prepares to launch Axis towards Earth.  ⏎  ⏎ Amuro pilots the cutting-edge Mobile Suit Nu Gundam on a course for Axis to stop Char's plan and finally bring an end to the conflict. ⏎  ⏎ After a fierce battle with Char on Axis, Amuro emerges victorious, but Londo Bell fails to destroy Axis as it plummets to Earth. ⏎   ⏎ As Axis enters the Earth's atmosphere, Amuro uses the Nu Gundam to stop and attempt to push it back. The Nu Gundam's Psycho-frame prevents Axis colliding with Earth in a glorious flash of light which leaves a lasting an impression on all who witnessed it. ⏎   ⏎ Amuro and Char go missing after the battle, never to be seen again...

### dic\_name\_GODGN\_00\_0

Adres: `dic\_text\_name/014d371a:c260b003`

> \[BRAK PL: dic\_text\_name/014d371a:c260b003\]
> JP (źródło tłumaczenia): 　未来世紀。 ⏎ 　荒廃した地球に見切りをつけた人類は、宇宙にスペースコロニー国家を作り、そこで生活していた。 ⏎ 　また各国は全面戦争を避けるため、地球をリング（戦場）に各国代表のガンダムを戦わせ、それを勝ち抜いた国に四年間の政治主導権を与えるガンダムファイトを開催していた。 ⏎ 　そして未来世紀６０年、ネオジャパンはガンダムファイト第１３回大会にガンダムファイター、ドモン・カッシュを送り込んだ。幼なじみでありクルーでもあるレインと共に各地を旅するドモンは、各国のガンダムと戦いながら、最強最悪の兵器、デビルガンダムに搭乗して地球へ逃亡した兄キョウジを追っていた。 ⏎ 　その旅の中、ドモンはライバル達と拳を交える事で互いを認め合い、かけがえのない友情を築いていった。 ⏎ 　また、師匠にして前大会の優勝者である東方不敗と再会を果たすが、東方不敗はデビルガンダムと結託しており、人類の敵として立ちはだかる。 ⏎ 　苛烈を極めた戦いの中、ドモンはついにデビルガンダムを打ち倒す。さらに東方不敗との激闘を制し、第１３回ガンダムファイトの覇者となる。 ⏎ 　全ての決着がついたと思われたが、ネオジャパンのウルベの策略によって、レインを生体コアにしてデビルガンダムが復活してしまう。さらにデビルガンダムは周辺のコロニーまでも吸収し、以前よりも強大な姿に成長をとげる。しかし、愛するレインを救い出したドモンにより、デビルガンダムはコアを破壊され完全に消滅する。 ⏎ 　世界に平和を取り戻したガンダムファイター達は、４年後の第１４回大会での再会を誓い合うのであった。
> EN (odniesienie oficjalne, NIE polski): The Future Century. ⏎  ⏎ Having given up on their ruined planet, humanity forsakes Earth to live inside colonies out in space. ⏎  ⏎ To avoid war among the colony nations, a competition is held every four years. One representative from each nation pilots a Gundam and takes part in a tournament called the "Gundam Fight", where Earth is the ring. The pilots fight until the nation represented by the last standing Gundam earns the right to rule all the colony nations. ⏎  ⏎ In year 60 of the Future Century, Neo Japan sends Domon Kasshu as its 13th Gundam Fight representative. Traveling with Rain, his childhood friend and crew, Domon fights against the Gundams of the other nations while searching for his older brother Kyoji, who has fled to Earth with the most powerful and evil weapon, the Dark Gundam. ⏎  ⏎ Through the exchange of fists, Domon and his rivals come to understand each other, forming an irreplaceable bond of friendship. ⏎  ⏎ Domon also reunites with Master Asia, his teacher and winner of the previous Gundam Fight. However, his master has sided with the Dark Gundam and is now an enemy of humanity. ⏎  ⏎ After an intense battle, Domon finally defeats the Dark Gundam. He also bests Master Asia, emerging as the champion of the 13th Gundam Fight. ⏎  ⏎ Everything seems to be over until Urube of Neo Japan kidnaps Rain, forcing her to act as the Dark Gundam's bio-unit. Furthermore, the Dark Gundam absorbs the surrounding colonies, becoming stronger than ever. However, Domon is able to rescue his beloved Rain. with its core destroyed, the Dark Gundam disintegrates. ⏎  ⏎ Having restored peace to the world, the Gundam Fighters vow to meet again four years later, at the 14th Gundam Fight.

### dic\_name\_GNWEW\_00\_0

Adres: `dic\_text\_name/014d371a:c260b005`

> \[BRAK PL: dic\_text\_name/014d371a:c260b005\]
> JP (źródło tłumaczenia): 　Ａ．Ｃ．１９６年。 ⏎ 　５機のガンダムの地球降下によるオペレーション・メテオに端を発した戦いが終結して１年が経ち、世界は平和への道を歩んでいた。 ⏎ 　レディ・アンらが組織した情報機関「プリベンター」に所属する、かつてのガンダムパイロット達は、通称「マリーメイア軍」の活動を追う。組織の首領である少女・マリーメイアは、かつての戦いで戦死した世界国家元首のトレーズ・クシュリナーダの娘を名乗り、バートン財団総帥のデキム・バートンと共に密かに戦力を用意していた。 ⏎ 　さらにそこにはガンダムのパイロットである五飛もいた。 ⏎ 　そして、マリーメイア軍は平和の象徴でもあるリリーナ・ドーリアン外務次官を拉致して世界へと宣戦を布告し、コロニーを地上へと落下させる「真のオペレーション・メテオ」を実行に移す。
> EN (odniesienie oficjalne, NIE polski): A.C. 196, Christmas. ⏎  ⏎ One year has passed since the end of the battle of Operation Meteor that began with 5 Gundams descending to Earth, and the world is on the road to peace. ⏎  ⏎ The Gundam pilots are now part of the Preventers, an intelligence agency run by Lady Une. They track the activities of an organization known as the Mariemaia Army, led by a young girl named Mariemaia. She claims to be the daughter of Treize Khushrenada, the now-deceased ruler of the world's countries, and has gathered strength in secret along with the head of Barton Foundation, Dekim Barton. Wufei, the Gundam pilot, is also with her. ⏎  ⏎ The Mariemaia Army kidnaps Vice Foreign Minister Relena Darlian, the symbol of peace, declaring war on the world, and sets True Operation Meteor to drop a colony onto Earth into action.

### dic\_name\_GNWEW\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b000`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b000\]
> JP (źródło tłumaczenia): 　ヒイロ達ガンダムパイロットとリリーナの兄・ゼクス・マーキスの活躍によってコロニーの落下作戦は阻止されたものの、その隙をついてマリーメイア軍は大規模なモビルスーツ部隊を地上へと降下させ、大統領府を制圧する。 ⏎ 　後を追って降下したゼクス、ノイン、そしてガンダムパイロットのデュオ、カトル、トロワはパイロットを殺さない不殺の戦いを行うも、圧倒的な物量差に苦戦を強いられる。 ⏎ 　そこへ到着したヒイロは、五飛との戦いで半壊したウイングガンダムゼロを駆り、ツインバスターライフルで大統領府を守るシェルターを狙撃し、機体を大破させながらもリリーナを救出すべく内部への侵入を成功させる。 ⏎ 　ヒイロの攻撃に対して初めて戦いの恐怖を知り、自らの過ちを認識したマリーメイアは、リリーナをかばってデキムの凶弾に倒れる。 ⏎ 　しかし、デキムのその行動は兵士達の怒りを買い、デキムは逆賊として味方の兵士に射殺され、戦いは終結する。 ⏎ 　戦争がなくなった世界に不要となったガンダムは、パイロットの手によって破壊され、彼らは各々の道を歩み始めるのであった。
> EN (odniesienie oficjalne, NIE polski): Heero and the other Gundam pilots, along with Relena's brother Zechs Merquise, successfully stop the fall of the colony. The Mariemaia Army takes advantage of that gap to send a large Mobile Suit squadron down to Earth, taking over the Presidential Office. Zechs, Noin, and the Gundam pilots Duo, Quatre, and Trowa follow after. They fight without killing, but are forced into a close battle due to the sheer difference in resources. ⏎  ⏎ Heero arrives in his Wing Gundam Zero, already half-destroyed during the fight against Wufei. He uses his Twin Buster Rifles to attack the unit guarding the Presidential Office, and succeeds in breaking through in order to save Relena, despite great damage to his unit. Mariemaia learns of the horrors of war after witnessing Heero's attacks, and realizes her own mistake. Dekim fires a bullet, and Mariemaia takes it in order to protect Relena. However, Dekim's actions angered their forces and he is branded a traitor. He is killed by his own forces, bringing an end to the fighting. ⏎  ⏎ With the end of all fighting, Gundams no longer have a place in the world. The Gundams are destroyed by Heero, and each of them continue down their own path in life.

### dic\_name\_GNDE\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b001`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b001\]
> JP (źródło tłumaczenia): 　コズミック・イラ（Ｃ．Ｅ）７１年。 ⏎ 　遺伝子操作された新人類「コーディネイター」と遺伝子操作されていない通常の人類「ナチュラル」との確執から起こった地球連合軍とプラントの争いの中、地球連合軍は中立国であるオーブに侵攻する。民間人にも多大な被害をもたらしたこの戦いで、シン・アスカは両親と妹を失う。 ⏎ 　それから２年。ザフトに入隊したシンは、新型モビルスーツ・インパルスガンダムのパイロットとなり、強奪された３機の新型モビルスーツの奪還作戦に参加する。また、その任務を与えられた戦艦ミネルバにはプラント最高評議会議長ギルバート・デュランダルと２年前の戦いの英雄アスラン・ザラも乗船していた。 ⏎ 　その任務の最中、シン達はナチュラル根絶を訴えるザフトの脱走兵達が起こしたユニウス・セブン落下事件に遭遇する。ミネルバの活躍により、ユニウス・セブンは分断されたものの破片は地上に降り注ぎ、各地に多大な被害をもたらす。 ⏎ 　それが原因となり、再び地球連合とプラントとの争いが勃発する。 ⏎ 　戦いが激化する中、前大戦の英雄、キラ・ヤマトも戦いに介入し、戦局は混迷の一途をたどる。 ⏎ 　次第にデュランダルを盲信していくシンは、アスランと反目し、さらに戦いを止めようとするキラを撃破する。 ⏎ 　一方、デュランダルは人類を適正に管理するシステム「デスティニープラン」を提唱。人の運命を管理するその構想に反対するキラやアスランは、デュランダル率いるザフト艦隊やシンと激突する。 ⏎ 　最後の戦いでシンはアスランに破れ、デュランダルも死亡し、人類の未来と自由は守られるのであった。
> EN (odniesienie oficjalne, NIE polski): Year 71 of the Cosmic Era. ⏎  ⏎ During a war between the Earth Alliance Forces and PLANT, brought about by the feuding between the Coordinators—the new, genetically-enhanced humanity—and the Naturals—normal humans without genetic modification—the Earth Alliance invades Orb, a neutral nation. The conflict takes the lives of many civilians, including Shinn Asuka's parents and younger sister. ⏎  ⏎ Two years later, Shinn, having joined ZAFT, becomes the pilot of a new Mobile Suit called the Impulse Gundam. With the battleship Minerva, he takes part in a mission to capture three other new Mobile Suits stolen from ZAFT. Also on board the Minerva is PLANT Supreme Council Chairman Gilbert Dullindal and Athrun Zala, a hero from the war two years prior. ⏎  ⏎ During their mission, Shinn and the others encounter Junius Seven, which is being pulled down by ZAFT deserters advocating the eradication of all Naturals. Through the Minerva's actions, Junius Seven is split into pieces; however, those fragments still rain down on Earth, causing massive damage and casualties all over the world. ⏎  ⏎ The incident causes a second war to break out between the Earth Alliance and PLANT. ⏎  ⏎ As the fighting intensifies, Kira Yamato, another hero from the previous war, intervenes, bringing even more chaos to the conflict. ⏎  ⏎ Shinn, his blind faith in Dullindal gradually growing, rebels against Athrun and goes on to defeat Kira, who tried to stop further warfare. ⏎  ⏎ Meanwhile, Dullindal announces his Destiny Plan, a system to properly supervise humankind. Kira and Athrun are in opposition to the way it would control people's fates, and clash with the ZAFT fleets led by Dullindal, as well as with Shinn. ⏎  ⏎ In the final battle, Shinn loses to Athrun, Dullindal perishes, and the future and freedom of mankind are preserved.

### dic\_name\_GNWOM\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b003`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b003\]
> JP (źródło tłumaczenia): 　Ａ．Ｓ．（アド・ステラ）１２２。 ⏎ 　宇宙へ進出した数多の企業が巨大な経済圏を構築する時代。 ⏎ 　経済格差から宇宙居住者スペーシアンが地球居住者アーシアンを搾取する構造により、両者の対立が続いていた。 ⏎ 　辺境の地・水星で育った少女、スレッタ・マーキュリーは、モビルスーツ産業最大手「ベネリットグループ」が運営するアスティカシア高等専門学園に編入する。学園では、学生同士が互いに望むものをかけてモビルスーツで戦う「決闘」が行われていた。 ⏎ 　編入初日、ベネリットグループ総裁の娘であるミオリネ・レンブランと出会ったスレッタは、学園ナンバーワンパイロット「ホルダー」であり、ミオリネの婚約者候補の筆頭であるグエル・ジェタークの横暴な態度を見かねて、グエルとの「決闘」に臨むのであった。
> EN (odniesienie oficjalne, NIE polski): A.S. (Ad Stella) 122. An era of space travel in which myriad corporations have formed one enormous economic sphere. In this era, there exists ongoing antagonism between impoverished Earthians and wealthy Spacians (those who live on colonies and otherwise in space) who exploit them. ⏎  ⏎ Suletta Mercury, a girl raised on the remote planet of Mercury, is admitted into Asticassia School of Technology, run by the Benerit Group, leaders of the Mobile Suit industry. At this school, students engage in formal Mobile Suit duels with their own desires and dreams on the line as wagers. ⏎  ⏎ On her first day at school, Suletta encounters Miorine Rembran, daughter of the Benerit Group's president, and subsequently faces Guel Jeturk, the Holder (the number one pilot in the school) and leading candidate to marry Miorine, in a duel to protect Miorine after seeing Guel's violent behavior.

### dic\_name\_GNWOM\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b004`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b004\]
> JP (źródło tłumaczenia): 　グエルに勝利したスレッタは、「ホルダー」となると同時にミオリネの婚約者候補の筆頭となる。しかし、決闘に使用したモビルスーツ「エアリアル」が生命倫理の問題から禁忌とされている「GUND-ARM」であるとの疑念が浮上する。 ⏎ 　エアリアルの廃棄と自身の退学を突きつけられた窮地を、ミオリネに救われたスレッタ。スレッタはグエルとの再戦、エラン・ケレスとの「決闘」で勝利を重ねる。しかし、「エアリアル」は再び「GUND-ARM」であることを疑われ、廃棄の危機に陥る。ミオリネはスレッタとエアリアルを守るため、「株式会社ガンダム」を設立し、GUNDを医療技術として研究開発する事業を起こすのであった。 ⏎ 　様々な障害や困難を仲間と共に乗り越えていくスレッタとミオリネ。だが、スレッタの母・プロスペラには秘めたる思惑があるのであった。
> EN (odniesienie oficjalne, NIE polski): After defeating Guel, Suletta becomes the school's Holder and the top candidate to be Miorine's groom. However, the Mobile Suit she used in the duel, Aerial, is suspected of being a GUND-ARM, a type of Mobile Suit banned for bioethical issues. ⏎  ⏎ When Suletta is faced with the prospect of Aerial's disposal and her own expulsion from the school, Miorine saves her. Suletta and Guel have a rematch, and Suletta goes on to defeat Elan Ceres in a duel as well. However, Aerial is once again suspected to be a GUND-ARM, leading to a crisis that could end with its dismantlement. In order to protect Suletta and Aerial, Miorine establishes GUND-ARM Inc., which is ostensibly focused on researching and developing GUND technology for medical applications (and also becomes a way for Miorine to gain freedom from her father, Delling). ⏎  ⏎ Suletta and Miorine overcome various roadblocks and challenges together, all while Suletta's secretly scheming mother, Prospera, watches over them.

### dic\_name\_ABDV\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b005`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b005\]
> JP (źródło tłumaczenia): 　家庭を省みない両親に反抗するようにモトクロスに明け暮れる少年、ショウ・ザマは、ある夜、ハイウェイを疾走していたところで突然謎の世界へと転移してしまう。 ⏎ 　そこは海と陸の間にある異世界「バイストン・ウェル」だった。 ⏎ 　同じくアの国へと召喚された地上人であるトッド達と共に、ショウは地方領主ドレイクの下で人型兵器「オーラバトラー」を操る「聖戦士」として歓迎される。 ⏎ 　オーラバトラー「ダンバイン」の操縦者となったショウだったが、ドレイクがバイストン・ウェルを支配する野望を持っていることを地上人マーベル達から知らされ、ダンバインと共に反ドレイク勢力に合流する。 ⏎ 　オーラバトラーを用いた戦争が拡大し、混迷の一途をたどる中、フェラリオの長ジャコバ・アオンはその力をもってオーラマシンとその関係者すべてをショウたちが元いた世界、地上界へと放逐する。 ⏎ 　ナの国の若き女王シーラとラウの国のエレ王女率いる連合軍へと参加したショウとマーベル達は、オーラマシンの力で地上界の支配を目論むドレイクと、その協力者であるクの国の王・ビショットを相手に戦う。 ⏎ 　戦いは世界各国を巻き込んだ全面戦争へと発展していく。
> EN (odniesienie oficjalne, NIE polski): Ignored and neglected by his parents, Show Zama spends all his time immersed in motocross. As he was racing down the highway one night, Show is suddenly whisked away to a mysterious world. ⏎  ⏎ That world is Byston Well, located in the space between sea and land. ⏎  ⏎ Along with Tod and other people who have been summoned to this world, Show is welcomed by Drake, lord of the land, as a Battler piloting humanoid weapons called Aura Battlers. Upon learning from Marvel and the other Upper Earth people that Drake intends to rule all of Byston Well, Show teams up with anti-Drake forces along with the Dunbine, the Aura Battler he pilots. ⏎  ⏎ The battle between Aura Battlers spreads. Amidst the turmoil, Jacoba Aon, the Ferario leader, sends the Aura Machines and everyone involved to Show's original world, the Upper Earth. ⏎  ⏎ The young Queen Ciela of the Land of Na, Queen Elle of the Land of Rau, Show, Marvel, and the rest join forces. Their goal is to take down Drake, who aims to use the power of Aura Machines to control Upper Earth as well. Aiding Drake is King Bishot of the Kingdom of Ku. Their war engulfs many countries.

### dic\_name\_ABDV\_00\_1

Adres: `dic\_text\_name/014d371a:c2a0b006`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b006\]
> JP (źródło tłumaczenia): 　激闘の中、元凶であったドレイクが討たれ、ショウも宿敵であった黒騎士バーンと相打ちとなる。 ⏎ 　そしてシーラは、全ての憎しみを浄化するためにバイストン・ウェルへの道オーラロードを開いた。 ⏎ 　戦いの場にいたバイストン・ウェルから来た者たちは全て地上から消滅し、後にはチャム・ファウ独りが残されるのであった。
> EN (odniesienie oficjalne, NIE polski): In the midst of the fierce fighting, Show is beset by the Black Knight Bern and the ringleader Drake. ⏎  ⏎ In order to purify all hatred, Ciela opens Aura Road, the path to Byston Well. Those who have come to Byston Well to stand on the battlefield are annihilated, leaving only Chum Huau.

### dic\_name\_DBOVA\_00\_0

Adres: `dic\_text\_name/014d371a:c2a0b007`

> \[BRAK PL: dic\_text\_name/014d371a:c2a0b007\]
> JP (źródło tłumaczenia): 　バイストン・ウェルと地上を巻き込んだ戦乱が終結し、７００年の時が流れた。 ⏎ 　アの国のバランバランの地に住む狩人の少年シオン・ザバは、ある日、オーラバトラー「ズワウス」を駆る黒騎士ラバーン・ザラマンド率いる部隊の攻撃を受ける。 ⏎ 　シオンは伝説の「バランバランの秘宝」を守護する一族の姫、レムルと共にラバーンの手に堕ち、彼の城へ捕らえられてしまう。 ⏎ 　襲撃の中で救い出したフェラリオのシルキーの手を借りて牢から脱走したシオンは、レムルと共にラバーンの城を脱出する。 ⏎ 　しかし、ラバーン軍に後をつけられており、バランバランの秘宝である古のオーラバトラー「サーバイン」の在処に彼らを招いてしまう結果となる。 ⏎ 　危機に陥ったレムルを前にしてシオンはサーバインへと搭乗し、ラバーンのズワウスを撃退することに成功する。 ⏎ 　シオンは、類まれなるオーラ力を持つ「聖戦士」であった。
> EN (odniesienie oficjalne, NIE polski): 700 years have passed since the war that broke out across Byston Well and Upper Earth. ⏎  ⏎ Shion Zaba is a young hunter living in Baran-Baran in the Land of Ah. One day, he is attacked by the Aura Battler Zwauth piloted by the Black Knight Rabaan Zaramand and his troops. He is captured and taken to Rabaan's castle, along with Remul, princess of the noble house tasked with guarding the Treasure of Baran-Baran. The two of them rescue a Ferario named Silky in the confusion, and she helps them escape the castle. ⏎  ⏎ However, they are pursued by Rabaan's troops and unintentionally lead them to where the Treasure of Baran-Baran, an ancient Aura Battler named Sirbine, was hidden. Shion pilots the Sirbine to protect Remul from danger, successfully driving away Rabaan in his Zwauth. ⏎  ⏎ Shion has become a Battler; one who possesses the rare Aura Power.

### dic\_name\_DBOVA\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b000`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b000\]
> JP (źródło tłumaczenia): 　サーバインに乗って逃げ延びた先の砂漠でシオンは、聖戦士の出現を待ちわびていたロズン家を名乗る者たちに救われる。 ⏎ 　彼らの城で歓迎を受けるシオンだったが、そこへラバーン軍が再び強襲をかけ、ラバーンはレムルを拉致して撤退する。 ⏎ 　レムルを救うべくロズン家の騎士たちとラバーンの城に襲撃をかけるシオンだったがこれに失敗、絶体絶命の危機へと陥る。 ⏎ 　しかしそこで、ラバーン配下のミイラのような謎の老人に生命を救われる。 ⏎ 　ラバーンとシオンのオーラバトラー同士の死闘の最中、謎の老人はオーラロードを開くためにＩＣＢＭの発射スイッチを入れる。 ⏎ 　老人の正体は、魂だけが７００年の時を生き永らえ、自らの死を望むショット・ウェポンだった。 ⏎ 　ＩＣＢＭの爆発により城が崩壊し、ラバーンとショットが光へと消えていく中、シオン、レムル、シルキーの三人はサーバインのオーラバリアに守られて生き延びる。 ⏎ 　こうしてラバーンとの戦いは終わりを迎え、バイストン・ウェルに再び平穏が戻るのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Shion escapes to the desert in the Sirbine. His appearance saves the Rozon family, who had grown tired of waiting for a Battler. He is welcomed into their castle, but Rabaan's troops attack once more, capturing Remul before making a hasty retreat. ⏎  ⏎ Shion heads to Rabaan's castle along with some of the Rozon family knights to rescue Remul, but their attack fails and he is driven into a desperate situation. At that very moment, he is saved by Rabaan's subordinate, a mummy-like mysterious old man. ⏎  ⏎ In the ensuing fight between both Aura Battlers, the mysterious old man flicks the switch to fire the ICBM to open the Aura Road. His true identity is Shot Weapon, the soul that has survived a long 700 years yearning for death. ⏎  ⏎ The ICBM explodes, destroying the castle. Rabaan and Shot disappear into the light, but Shion, Remul, and Silky are protected by Sirbine's Aura Barrier and thus survive. ⏎  ⏎ The battle against Rabaan comes to an end, and peace returns to Byston Well once again.

### dic\_name\_ELGIM\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b001`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b001\]
> JP (źródło tłumaczenia): 　二重太陽サンズと５つの惑星からなるペンタゴナ・ワールド。 ⏎ 　世界はオルドナ・ポセイダルによって統治されていたが、各地では反乱軍との小競り合いが続き、戦乱が絶えなかった。 ⏎ 　辺境の惑星コアムで青雲の志と共に故郷を後にしたダバ・マイロードとミラウー・キャオは、元山賊のファンネリア・アムと出会う。 ⏎ 　武器商人アマンダラ・カマンダラと関わった事から、ダバは父の形見のヘビーメタル・エルガイムでポセイダル軍と戦う事となり、その中で元１３人衆ガウ・ハ・レッシィも合流する。 ⏎ 　ミズン星の大規模な反乱軍の一員となったダバは、同じく志を抱いて地方から出て来たギャブレット・ギャブレーと何度も戦う。 ⏎ 　しかし、正規軍の力は強大であり、敗北したダバ達はミズン星を後にする。
> EN (odniesienie oficjalne, NIE polski): Pentagona World: a star system consisting of two binary stars, the Sunz, and its five orbiting planets.  ⏎  ⏎ This world, filled with constant strife and rebellions, lay under the dictatorship of Emperor Oldna Posaydal and the great armed forces of Posaydal's empire.  ⏎  ⏎ On the remote planet Coam, Daba Myroad and Mirawoo Kyao left their hometown to seek out their fortune. During their journey, they were joined by the former bandit Fannaria Amm.  ⏎  ⏎ As he got involved with the arms dealer Amandra Kamandra, Daba began a battle against the Posaydal Forces using the Heavy Metal his father left him, the L-Gaim. Along the way, he joined forces with one of Posaydal's elite Extra Thirteen, Gaw Ha Leccee.  ⏎  ⏎ Daba ended up becoming part of a large-scale rebellion army on planet Mizun. During this time, he repeatedly fought against Gavlet Gablae, who had perhaps even greater ambitions (in his own mind).  ⏎  ⏎ Posaydal's regular army was, however, too powerful for the rebels, and Daba was forced to flee Mizun.

### dic\_name\_ELGIM\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b002`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b002\]
> JP (źródło tłumaczenia): 　その後、様々な出会いと別れを経たダバは、真の名であるカモン・マイロードを名乗り、各星の反乱軍を束ねるリーダーとなっていく。 ⏎ 　やがて戦況はダバ率いる反乱軍とポセイダル正規軍、ポセイダルに反旗を翻したギワザ・ロワウ一派による三つ巴に発展していった。 ⏎ 　戦いの果てに真のポセイダルはアマンダラ・カマンダラである事がわかる。 ⏎ 　正体を現した真のポセイダルとギワザを倒したダバは、ペンタゴナ・ワールドを支配者の手から解放する。 ⏎ 　戦いの後、ポセイダルによって精神を破壊された義妹クワサン・オリビーを介護するため、ダバは仲間達と別れ、故郷へと帰るのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Later on, following a series of new meetings and partings, Daba embraced his real name of Camen Myroad, and became the leader of the interplanetary rebel army.  ⏎  ⏎ Eventually, the conflict evolved into a three-way battle between Daba's rebel forces, Posaydal's regular army, and the faction led by Giwaza Lowaw, Posaydal's former second-in-command who sought to fulfill his own ambition.  ⏎  ⏎ During the climax of the battle, it was revealed that the true Posaydal was actually Amandra Kamandra, the same "arms dealer" who had set Daba on his path.  ⏎  ⏎ After defeating the true Posaydal and Giwaza, Daba liberated Pentagona World from the control of any single ruler. In the end, Daba parted with his friends in order to return to his hometown and take care of his sister Quwasan Olibee, whose mind had been brought to the breaking point by Posaydal.

### dic\_name\_MZKZRDSDG\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b003`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b003\]
> JP (źródło tłumaczenia): 　数千年の間、地底深くに潜伏していたミケーネ帝国が地球侵略を開始した。 ⏎ 　七つの戦闘獣軍団を率いる暗黒大将軍は、全人類の抹殺を宣言し、世界各地を防衛するマジンガー軍団を次々と壊滅へ追いやる。 ⏎ 　マジンカイザーの操縦者・兜甲児は、世界の危機に駆けつけるべく、視察旅行先のパリから日本へ向かうが、戦闘獣の襲撃に遭ってしまう。 ⏎ 　仲間の尊い犠牲により、何とか日本に到着した甲児は、ボスボロットの操縦者・ボスと合流を果たし、光子力研究所へと向かう。 ⏎ 　しかし、そこに待ち受けていたのは、壊滅した光子力研究所と戦闘獣軍団の姿であった。
> EN (odniesienie oficjalne, NIE polski): The Mycenae Empire, which has bided its time underground for thousands of years, has launched its invasion of the surface. ⏎  ⏎ The Great General of Darkness declares death upon humanity and sends his Seven Battle Beast Armies to various regions of the world, defeating the members of the Mazinger Army one by one. ⏎  ⏎ Koji Kabuto, the pilot of Mazinkaiser, was on a trip to Paris when this occurred. When the invasion begins, he rushes back to Japan, but the Mycenaeans attack him at every turn. ⏎  ⏎ Thanks to the sacrifices of his comrades, Koji makes it to Japan, where he reunites with his friend Boss, pilot of Boss Robot, who takes him to the Photon Power Laboratory. ⏎  ⏎ But when he reaches his destination, he finds only the ruins of the laboratory and the Battle Beast army.

### dic\_name\_MZKZRDSDG\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b004`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b004\]
> JP (źródło tłumaczenia): 　ボスの手引きでカイザーパイルダーに乗り込んだ甲児は、宇宙にいる弓教授から送り届けられたマジンカイザーにパイルダーオンする。 ⏎ 　マジンカイザーの力で戦闘獣軍団を蹴散らす甲児であったが、そこにさらなる強敵・暗黒大将軍が現れる。 ⏎ 　仲間の想いを背負った甲児は激闘の果てに暗黒大将軍を打ち倒し、再び世界に平和が訪れるのであった。
> EN (odniesienie oficjalne, NIE polski): With Boss's help, Koji boards the Kaiser Pilder and flies into space, docking with Mazinkaiser after Professor Yumi sends it down. ⏎  ⏎ The super robot quickly dispatches the Battle Beasts until the Great General of Darkness himself enters the fray. ⏎  ⏎ Carrying the hopes and dreams of his fallen comrades, Koji and Mazinkaiser take down the Great General of Darkness at the end of a fierce battle, restoring peace to the world.

### dic\_name\_GTRARK\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b005`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b005\]
> JP (źródło tłumaczenia): 　１９年前、流竜馬や一文字號達の活躍により、人類と強大な敵との戦いは終止符が打たれ、世界は救われた。 ⏎ 　時は流れ、竜馬の息子・流拓馬は、母親を殺害した人物を探し出すために仲間の山岸獏と共に早乙女研究所を訪れる。早乙女研究所では、かつてのゲッターチームのメンバー・神隼人が新たな敵との戦いに備えていた。 ⏎ 　拓馬は運命に導かれるようにゲッターアークに乗り、カムイ・ショウ、獏と共に戦いに身を投じる。
> EN (odniesienie oficjalne, NIE polski): Nineteen years ago, the war between humanity and a powerful enemy was brought to an end thanks to the efforts of Ryoma Nagare, Go Ichimonji, and their comrades. ⏎  ⏎ Time passes, and Takuma Nagare, Ryoma's son, arrives at the Saotome Laboratory with his friend Baku Yamagishi to find the person who killed his mother. At the laboratory, former Getter Team member Hayato Jin is making preparations to face a new threat. ⏎  ⏎ As if guided by fate, Takuma boards Getter Arc, heading for battle alongside Show Kamui and Baku.

### dic\_name\_GTRARK\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b006`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b006\]
> JP (źródło tłumaczenia): 　人類の敵・アンドロメダ流国の一員に母の仇がいる事を知った拓馬は仲間達と共に恐竜帝国と協力し、亜空間から敵の本拠地へ直接乗り込む「ジュラ・デッド作戦」を決行する。 ⏎ 　その転移先となった遥か未来で待ち受けていたのは、ゲッターエンペラーとそれを生み出した人類による宇宙を巻き込む巨大な戦いであった。拓馬達は戸惑いながらも、母の仇であるマクドナルドを打ち倒し、アンドロメダ流国を壊滅へと追い込む。 ⏎ 　しかし、マクドナルドから最終兵器・バグを託されたカムイは元の世界に戻った後、未来を変えるべく決起し、恐竜帝国を率いて人類の前に立ち塞がる。 ⏎ 　拓馬はカムイを止めるべく激闘を繰り広げるが、その最中にゲッター聖ドラゴンが現れるのであった。
> EN (odniesienie oficjalne, NIE polski): When Takuma learns that his mother's murderer is a member of the Andromeda Stellaration, the enemy of humanity, he and his comrades cooperate with the Dinosaur Empire to execute Operation Jura Dead, a plan to attack the enemy's stronghold directly through a hyperspace jump. ⏎  ⏎ However, the jump flings them to the far future, into a galactic conflict between Getter Emperor and the humans responsible for its creation. Though perplexed by this turn of events, Takuma is able to kill McDonald, avenging his mother and leading the Andromeda Stellaration to ruin. ⏎  ⏎ However, McDonald had entrusted Kamui with the BUG, the ultimate weapon to annihilate humanity. Thus, Kamui decides to assume control of the Dinosaur Empire and stand against humanity to change the future. ⏎  ⏎ Takuma fiercely stands against Kamui, but during their battle, Getter Saint Dragon makes its appearance.

### dic\_name\_MCRSDLPW\_00\_0

Adres: `dic\_text\_name/014d371a:c2e0b007`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b007\]
> JP (źródło tłumaczenia): 　西暦２０６７年。 ⏎ 　地球人類が播種計画の下に銀河に進出して数十年後の時代、ブリージンガル球状星団では前触れもなく人々が凶暴化する奇病・ヴァールシンドロームの脅威が広がっていた。 ⏎ 　それに対して星間複合企業ケイオスのラグナ支部に所属する戦術音楽ユニット・ワルキューレの歌は、ヴァールシンドロームを鎮静化させる力を持っていた。可変戦闘機「VF-31 ジークフリード」を駆るデルタ小隊に護衛された彼女たちは、各地でライブ活動を展開する。 ⏎ 　ワルキューレに憧れる少女、フレイア・ヴィオンは、 ⏎ ワルキューレのオーディションに向かう途中、ヴァールたちの暴動のさなか ⏎ デルタ小隊の新人パイロット・ハヤテ・インメルマンと出会う。 ⏎ 　暴徒化した人間を歌で鎮静化した事で、その素質を認められたフレイアはワルキューレに加入し、ハヤテと共にヴァールシンドロームを巡る戦いに身を投じていく。
> EN (odniesienie oficjalne, NIE polski): 2067 A.D. ⏎  ⏎ It is an age where Earthnoids have spread across the stars, driven by a galactic colonization plan. One of these colonized areas, the Brisingr Globular Cluster was suddenly struck by a strange disease that turned people berserk: Vár Syndrome. ⏎  ⏎ In response, the interstellar conglomerate Xaos (pronounced "chaos") established the Tactical Sound Unit Walküre, whose songs were able to quell outbreaks of Vár Syndrome. Escorted on their duties by Delta Squadron, in their transforming VF-31 Siegfried variable fighters, Walküre held live concerts across the region. ⏎  ⏎ One young woman, Freyja Wion, was going to attend an audition to join Walküre, who she was greatly inspired by. While traveling to the audition, she instead found herself in the midst of a Vár Syndrome outbreak, where she would meet Delta Flight's newest pilot, Hayate Immelmann. ⏎  ⏎ In the thick of this chaos, she was able to calm the outbreak with her singing. As such, she was recognized for her abilities and joined Walküre, standing with Hayate in the battle against Vár Syndrome...and what ultimately caused it.

### dic\_name\_MCRSDLPW\_00\_1

Adres: `dic\_text\_name/014d371a:c2e0b008`

> \[BRAK PL: dic\_text\_name/014d371a:c2e0b008\]
> JP (źródło tłumaczenia): 　ついにデビューライブを迎えたフレイアであったが、その最中に謎の可変戦闘機部隊の襲撃を受ける。可変戦闘機部隊はウィンダミア王国を名乗り、その宰相であるロイドは新統合政府に対して宣戦布告を行う。 ⏎ 　戦いの中、ウィンダミア王国に捕らえられたワルキューレを救出するため、デルタ小隊の母体であるケイオスは、奇襲作戦「オペレーション・ラグナロク」を発動する。 ⏎ 　ウィンダミアの伝説にある「星の歌い手」の力を持つ美雲を手に入れたロイドは、「星の歌」とプロトカルチャーシステムを連動させて銀河を支配しようとする。しかし、ワルキューレとデルタ小隊、さらにはロイドと道を違えたウィンダミアの空中騎士団の活躍により、その野望は打ち砕かれる。 ⏎ 　戦いが終わった後、デルタ小隊とワルキューレは戦死した仲間・メッサーの魂を送るのであった。
> EN (odniesienie oficjalne, NIE polski): Just as Freyja was about to perform her debut live show, their group was attacked by an unknown team of Variable Fighters. These fighters declared themselves a force of the Kingdom of Windermere, and the kingdom's prime minister, Roid, declared war against the New United Nations Government.  ⏎  ⏎ Walküre was captured in battle, leading to the mothership of Delta Flight, the Xaos, to execute a surprise attack titled Operation Ragnarok. It was then revealed that Walküre member Mikumo had the power of the Singer of the Stars, a Windermerian legend. Roid intended to use the power of her Star Song, together with the Protoculture system, to attempt to "unify the peoples of the galaxy" and rule.  ⏎  ⏎ However, Walküre and Delta Flight, along with the Windermerian Aerial Knights whom Roid had managed to alienate, were able to defeat his ambitions. With the war ended, Walküre and Delta Flight sent off the soul of their comrade who perished in the battle, Messer.

### dic\_name\_CGRRR\_00\_0

Adres: `dic\_text\_name/014d371a:c320b000`

> \[BRAK PL: dic\_text\_name/014d371a:c320b000\]
> JP (źródło tłumaczenia): 　皇暦２０１０年。 ⏎ 　超大国「神聖ブリタニア帝国」は日本へ侵攻し、人型兵器「ＫＭＦ（ナイトメアフレーム）」による圧倒的な戦力差でその全土を属領とした。 ⏎ 　「エリア１１」と呼ばれた日本に住むルルーシュは、謎の少女Ｃ．Ｃ．と契約し、他人に命令を強制する力を持つ「ギアス」を得る。 ⏎ 　ブリタニア帝国の第１１皇子でありながら、政治の道具として利用した父である皇帝シャルルに憎しみを抱くルルーシュは、天才的な知略とギアスの力を使い、仮面の男「ゼロ」としてレジスタンス組織「黒の騎士団」を創設。日本独立を掲げ、妹ナナリーの平穏と自らの復讐のためにブリタニア帝国に対して反逆を開始する。 ⏎ 　かつてのルルーシュの親友で今は帝国の一員の枢木スザクが立ちふさがるも、協力者達を集めて勢力を拡大するゼロは、連合国家「超合集国」を発足。 ⏎ 　やがてルルーシュは、父シャルルと意識体となった母マリアンヌの真の目的を知り、世界を作り変えようとするその野望を砕き、自らの復讐を終える。 ⏎ 　全てを知って同志となった枢木スザクとＣ．Ｃ．らの協力の下、ルルーシュはブリタニア帝国を乗っ取り、皇帝ルルーシュ・ヴィ・ブリタニアとして即位。 ⏎ 　ブリタニアの体制を全て破壊し、黒の騎士団と手を組んだシュナイゼルを倒して世界を征服後、世界中の憎しみを集めた。そして、世界中の人達が注目するパレードで、ゼロに扮したスザクに討たれる。 ⏎ 　世界征服からゼロ（＝スザク）による粛清までの全ては、ルルーシュが自らの命を犠牲とした計画「ゼロ・レクイエム」であった。悪の象徴となったルルーシュが討たれた事で、世界は憎しみの連鎖を断ち切り新しい時代を迎えた。 ⏎ 　ゼロ・レクイエムから１年後の光和２年。世界は超合集国を中心に再編成され、平和な時が流れていた。しかし、難民キャンプの視察に訪れていた世界人道支援機関名誉顧問ナナリーと黒の騎士団の首席顧問ゼロ（＝スザク）が、正体不明の武装勢力に拉致されるという事件が発生。 ⏎ 　事件解決のため、「戦士の国」と呼ばれるジルクスタン王国に潜入したカレン達は、そこで謎のギアス使いに襲撃される。 ⏎ 　その場には、命を落としたはずのルルーシュとＣ．Ｃ．の姿があった。
> EN (odniesienie oficjalne, NIE polski): The date was August 10, in the year 2010 of the Imperial Calendar. ⏎  ⏎ The superpower known as the Holy Britannian Empire had declared war on Japan. In an overwhelming display of power, they quickly conquered the entire nation using their humanoid weapons, the Knightmare Frames (or KMFs). ⏎  ⏎ Lelouch, a young man living in Area 11 (the area formerly known as Japan), made a contract with the mysterious woman C.C., receiving the power of absolute control over others: the Geass. ⏎  ⏎ Lelouch was actually the 11th crown prince of Britannia, but he hated being used as a political tool; thus, he decided to combine his genius intellect with the power of the Geass. ⏎  ⏎ He became the masked man "Zero" and founded the "Black Knights", a resistance organization fighting against Britannia. Though publicly he was fighting to free Japan from the oppressive rule of the Empire, in truth he was only trying to create a peaceful world for his sister Nunnally, as well as achieve his personal vengeance. ⏎  ⏎ While Suzaku Kururugi, once a close friend of Lelouch, stood in his way as a soldier of Britannia, the Black Knights managed to establish the "United Federation of Nations", countries joined together in their opposition to the Empire. ⏎  ⏎ Eventually, Lelouch learned the true objective of his father Charles and his mother Marianne: mercilessly reshaping the world into a place without lies. He then crushed their ambition, thus achieving his vengeance.  ⏎  ⏎ With the help of Suzaku Kururugi and C.C., the only people in the world who knew the truth of what would be happening, Lelouch ascended to the throne of the Britannian Empire as Emperor Lelouch vi Britannia. After tearing down the original Britannian government and defeating the combined efforts of the Black Knights and Schneizel, Lelouch managed to conquer the entire world. He then proceeded to act like the worst of tyrants, gathering all the hatred of the people of the world onto him. Finally, during a parade broadcast to the entire world, he was killed by Zero (this time with Suzaku wearing the costume). ⏎  ⏎ Everything, from world conquest to being killed by Zero, was part of Lelouch's final gambit: the Zero Requiem. With the death of the "Evil Emperor Lelouch", the world would finally enter a new era, free from hatred. ⏎  ⏎ And then...Year 2 of the Kowa era. It had been one year since the Zero Requiem. ⏎  ⏎ Thanks to the reorganized United Federation of Nations, the world was celebrating an unprecedented time of peace. However, Nunnally, honorary advisor for the World Humanism Agency, and Zero (actually Suzaku), chief counselor of the Order of the Black Knights, were kidnapped by a mysterious armed group while visiting a refugee camp. In order to solve the case, Kallen and her team infiltrated the Kingdom of Zilkhstan, known as the Nation of Warriors, where they were attacked by a mysterious Geass user. ⏎  ⏎ That's when they happened upon C.C., who was traveling with none other than Lelouch, who was supposed to be dead...

### dic\_name\_CGRRR\_00\_1

Adres: `dic\_text\_name/014d371a:c320b001`

> \[BRAK PL: dic\_text\_name/014d371a:c320b001\]
> JP (źródło tłumaczenia): 　カレン達の協力を得て潜入したジルクスタンの大監獄で、ルルーシュはＣの世界から意識を取り戻す。ルルーシュは囚われていたスザクを救出し、かつての仲間を率いて大監獄を脱出後、ナナリー救出のための作戦を決行する。 ⏎ 　ルルーシュはジルクスタンの指導者である聖神官シャムナを追い詰めるが、彼女の時を遡るギアス・無限新生により時間は巻き戻される。 ⏎ 　シャムナのギアスによって全ての策を見抜かれ、作戦を封じられるルルーシュだったが、Ｃ．Ｃ．に叱咤され、膨大な作戦プランからシャムナの能力を絞り込み、逆に彼女を追い込む。 ⏎ 　ルルーシュは、自国のために世界を再び戦火に包もうとしたシャムナを否定し、彼女を永遠に眠らせた。 ⏎ 　Ｃの世界からナナリーの意識を救出して全てを終えたルルーシュは、かつての仲間達の下を去り、Ｃ．Ｃ．と共にギアスの欠片を探す旅に出るのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ With the help of Kallen, they were able to infiltrate the Zilkhstan Prison and allow Lelouch to reclaim his consciousness from C's World. He then proceeded to rescue Suzaku, and lead his former comrades in a rescue operation to save Nunnally.  ⏎  ⏎ Lelouch went after Shamna the Divine, the priestess of Zilkhstan, but each time he came close to defeating her, time rewound due to Shamna's Geass power of endless rebirth.  ⏎  ⏎ At first, Shamna used her Geass to "predict" every single one of Lelouch's plans, almost bringing him to a breaking point; it was only thanks to C.C.'s heartfelt rebuke that Lelouch returned to his former self, allowing him to come up with a grand plan that would force Shamna to reveal her power, and turn it back against her.  ⏎  ⏎ Once he came face to face with her, Lelouch rejected Shamna's wish to create a world of endless conflict for the sake of her warrior nation, and used his own Geass to let her sleep for eternity.  ⏎  ⏎ After rescuing Nunnally's consciousness from C's World, Lelouch bid farewell to his old friends and left on a journey alongside C.C. in order to look for Geass fragments throughout the world.

### dic\_name\_MJP\_00\_0

Adres: `dic\_text\_name/014d371a:c320b002`

> \[BRAK PL: dic\_text\_name/014d371a:c320b002\]
> JP (źródło tłumaczenia): 　地球歴２１１０年。 ⏎ 　宇宙に進出した人類は、木星圏にて汎銀河統一帝国を名乗る謎の勢力ウルガルの襲撃に遭い、存亡の危機に直面していた。 ⏎ 　一方、地球では遺伝子操作で宇宙に適応できる人類を生み出そうとするプロジェクトが特務機関ＭＪＰによって進められていた。 ⏎ 　ＭＪＰに所属するヒタチ・イズルら５人で編成されたチームラビッツは、個々の能力は高いが、チームワークがとれない事から戦績は最低ランクで「ザンネンファイブ」と呼ばれている。しかし、彼等は最新鋭戦闘デバイス「ＡＨＳＭ（アッシュ）」への搭乗を命じられ、ウルガルとの戦いに身を投じていく事となる。
> EN (odniesienie oficjalne, NIE polski): 2110 A.D.  ⏎  ⏎ Mankind's advance into outer space was halted when they reached the Jupiter Sphere, and fell under the attack of the United Pan-Galactic Empire Wulgaru.  ⏎  ⏎ Meanwhile on Earth, the military organization MJP was moving forward with a project to breed genetically altered humans better suited to operate in space.  ⏎  ⏎ Izuru Hitachi was part of Team Rabbits, a five-man group affiliated with MJP. Individually, they were highly talented; however, their inability to work together as a team had earned them the moniker of "the Fail Five". ⏎  ⏎ Even so, they were ordered to board the state-of-the-art Combat Devices known as AHSMB (pronounced "Ashemby"), and were sent to fight against the Wulgaru.

### dic\_name\_MJP\_00\_1

Adres: `dic\_text\_name/014d371a:c320b003`

> \[BRAK PL: dic\_text\_name/014d371a:c320b003\]
> JP (źródło tłumaczenia): 　慣れないながらも何とか戦い続けるチームラビッツは、ウルガルから亡命してきた皇女テオーリアから彼等の真の目的を聞く。それは種族存続のために優秀な遺伝子を回収する事であり、その戦いは彼等にとって「狩り」と呼ばれる行為であった。 ⏎ 　後輩のアンジュを加えて戦い続けるチームラビッツであったが、イズルは宿敵ジアートとの激戦を経て身体に異常をきたし、ついには出撃を禁じられる。ウルガルの太陽系侵攻の通路となる次元移送ゲート破壊作戦の中、イズルは不利な戦況を覆すため、また仲間を守るために出撃する。 ⏎ 　激闘の末、ＭＪＰのシモン司令による宇宙ステーション・スターローズの突撃でゲートは破壊され、真の覚醒を果たしたイズルはジアートに勝利する。全てを終えたイズルは、ヒーローとして仲間達に迎え入れられるのであった。
> EN (odniesienie oficjalne, NIE polski): Despite their paucity of initial experience, Team Rabbits continued to fight and rack up victories. Eventually, they learned the true objective of the Wulgaru from a defector, Princess Teoria.  ⏎  ⏎ Apparently, for the Wulgaru, the entire conflict was but a "hunt". Their goal was to recover superior genetic material to ensure the survival of their own species.  ⏎  ⏎ As the war continued, Ange Kuroki was added to the members of Team Rabbits; however, after a series of battles with the enemy commander Jiart, Izuru's health began to deteriorate, and was thus forbidden from further combat operations.  ⏎  ⏎ During one of the operations to destroy the Wulgaru's dimensional gate, their path into the Solar System, Izuru ignored his orders and deployed into battle again in order to protect his friends.  ⏎  ⏎ After a fierce battle, the gate was finally destroyed when MJP Commander Simon set the space station Star Rose on a collision course with the gate; meanwhile, Izuru achieved his true awakening in order to defeat Jiart.  ⏎  ⏎ Ultimately, Izuru survived the confrontation, and was welcomed back by his friends as the hero he always wanted to be.

### dic\_name\_GZLSP\_00\_0

Adres: `dic\_text\_name/014d371a:c320b004`

> \[BRAK PL: dic\_text\_name/014d371a:c320b004\]
> JP (źródło tłumaczenia): 　２０３０年、千葉県逃尾市。 ⏎ 　町工場・オオタキファクトリーに勤める有川ユンは、幽霊騒ぎの調査依頼を受け、無人の洋館を訪れる。 ⏎ 　一方、幻想生物を研究する大学院生の神野銘は、旧嗣野地区管理局・ミサキオクで受信された信号の調査に向かっていた。 ⏎ 　互いを知らぬ二人は異なる場所でそれぞれ同じ歌を耳にし、怪獣をめぐる世界の異変に巻き込まれていく。 ⏎ 　突如として街に現れた怪獣に対し、ユンはオオタキファクトリーの面々と共にロボット・ジェットジャガーで対処し、メイは相棒の犬型人工知能「ペロ２」と共に世界の謎に迫る。
> EN (odniesienie oficjalne, NIE polski): Nigashio, Chiba prefecture, 2030. ⏎  ⏎ Yun Arikawa, an engineer working for a car and robotics garage called the Otaki Factory, investigates a mansion on a deserted island due to reports of hauntings. Meanwhile, graduate student Mei Kamino's research on imaginary creatures leads her to a mysterious radio transmission from the old Misakioku city center. ⏎  ⏎ Each of them, working separately and in different locations, hear the same song and find themselves facing a series of kaiju phenomena that threaten to change the world as we know it. Yun and his coworkers at the Otaki Factory activate their robot, Jet Jaguar, to fight off the kaiju attacking the city, while Mei and her canine partner AI Pelops II delve into the mysteries of their world.

### dic\_name\_GZLSP\_00\_1

Adres: `dic\_text\_name/014d371a:c320b005`

> \[BRAK PL: dic\_text\_name/014d371a:c320b005\]
> JP (źródło tłumaczenia): 　チャットで情報を交換しあうメイとユン。 ⏎ 　世界中に怪獣が現れ、紅塵と呼ばれる物質が世界に広がる中、メイとペロ２は新素材・アーキタイプの謎を解明していく。その過程でメイは、世界が破局へ向かっている事と、その特異点となるのは東京に出現した巨大怪獣「ゴジラ」である事を知る。 ⏎ 　一方、ジェットジャガーとユン達は、東京へゴジラ退治に向かっていた。 ⏎ 　破局を止めるため、メイ達は超時間計算機による解析を行い、ペロ２は破局回避に必要なプロトコルを発見する。そのプロトコルを受信したジェットジャガーはペロ２と一体となり巨大化し、激闘の末ゴジラとともに消失。破局を食い止める事に成功した。 ⏎ 　事態の後、世界を救った二人の天才・ユンとメイは対面を果たすのであった。
> EN (odniesienie oficjalne, NIE polski): Mei and Yun collaborate by text message. ⏎  ⏎ Kaiju continue appearing around the world as the substance known as Red Dust spreads. Mei and Pelops II unveil the true nature of the newly developed Archetype material, revealing the oncoming "Catastrophe" facing the world—and that it centers on the Singularity that is the massive kaiju Godzilla which has appeared in Tokyo. ⏎  ⏎ In order to stop the Catastrophe, Mei and her new allies use the Super Dimension Calculator to analyze it, and Pelops II discovers the necessary protocols for avoiding it. That protocol is transmitted to Jet Jaguar, who merges with Pelops II before disappearing with Godzilla in a climactic battle, thus preventing the Catastrophe from occurring. In the aftermath, Yun and Mei, the two geniuses who saved the world, finally meet face to face.

### dic\_name\_DYNZNN\_00\_0

Adres: `dic\_text\_name/014d371a:c320b006`

> \[BRAK PL: dic\_text\_name/014d371a:c320b006\]
> JP (źródło tłumaczenia): 　都立フジヨキ台高等学校に通う麻中蓬は、学校の帰り道に空腹で倒れていた「怪獣使い」を名乗る男・ガウマと出会う。 ⏎ 　その翌日、街に突如として怪獣が現れ、ガウマは巨大ロボット・ダイナゼノンを呼び出す。そこへ居合わせた蓬、クラスメイトの南夢芽、怪獣騒ぎを聞きつけ見物に来ていた無職の青年・山中暦は、ガウマと共にダイナゼノンに搭乗する事になり、暦の従妹・飛鳥川ちせを含めた５人で怪獣と戦っていく。
> EN (odniesienie oficjalne, NIE polski): One day, on his way back from school at Fujiyokidai High School, Yomogi Asanaka happens upon a starving man named Gauma, who claims to be a "kaiju user". ⏎  ⏎ The next day, a kaiju suddenly attacks the city, and Gauma summons a giant robot called Dynazenon. Yomogi is made to pilot the robot alongside Gauma, along with Yume Minami, the girl he was meeting, and Koyomi Yamanaka, an unemployed man trying to get a look at the kaiju. ⏎  ⏎ The four, together with Koyomi's cousin Chise Asukagawa, team up to fight against further kaiju.

### dic\_name\_DYNZNN\_00\_1

Adres: `dic\_text\_name/014d371a:c320b007`

> \[BRAK PL: dic\_text\_name/014d371a:c320b007\]
> JP (źródło tłumaczenia): 　戦いを重ねていく中、蓬達の前にガウマのかつての仲間である怪獣優生思想が現れる。彼等四人は怪獣を必要とする世の中を作るべく、その怪獣を操る力を使って街に被害をもたらしていた。 ⏎ 　グリッドナイト同盟やちせが拾った種から成長した怪獣・ゴルドバーンを仲間に迎えた蓬達はそれぞれが成長を果たし、怪獣優生思想を取り込んだ最後の怪獣・ガギュラと激突する。 ⏎ 　激闘の末に勝利した蓬達は、ガウマやゴルドバーンと別れ、これまでとは少し変化した日常へと帰っていくのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ As they continue to fight together, the team cross paths with Gauma's former allies, now calling themselves the Kaiju Club. They are a group of four who seek to create a world that needs kaiju, and proceed to control kaiju to wreak destruction in the city. ⏎  ⏎ Gauma's team joins forces with the Gridknight Alliance and Goldburn, a kaiju formed from a seed Chise found. As the team members develop individually, they clash with the final Kaiju of the Kaiju Club: Gagula. ⏎  ⏎ After they finally win a grueling war, the team part ways with Gauma and Goldburn and return to their old lives, now with new outlooks.

### dic\_name\_BIGO\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a7a0b000`

> \[BRAK PL: dic\_text\_name-DLC1/000003b7:a7a0b000\]
> JP (źródło tłumaczenia): 　記憶喪失の街「パラダイムシティ」。 ⏎ 　４０年より前に起こった記憶（メモリー）が失われた街には、ネゴシエイター（交渉人）、ロジャー・スミスがいた。 ⏎ 　持ち込まれた様々なトラブルをアンドロイドのドロシーと共に巧みな弁舌と行動力で解決していくロジャー。相手が暴力に訴える時、ロジャーは黒いメガデウス・ビッグオーを駆り、力には力で応える。 ⏎ 　日々の依頼の中、ロジャーはパラダイムシティの記憶（メモリー）の謎に迫っていく。
> EN (odniesienie oficjalne, NIE polski): Paradigm City is a city of amnesia. ⏎  ⏎ In this city, where every person lost their Memories forty years ago, lives the negotiator Roger Smith. ⏎  ⏎ Roger solves the problems people bring to his doorstep alongside his android companion Dorothy, using eloquence and action in equal measure and with equal skill. ⏎  ⏎ When he requires brute force, Roger calls upon his black Megadeus, Big O, and from there, it's showtime. ⏎  ⏎ As he solves the city's requests, Roger also investigates the mysteries surrounding Paradigm City's Memories.

### dic\_name\_GWBRGR\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a860b001`

> \[BRAK PL: dic\_text\_name-DLC1/000003b7:a860b001\]
> JP (źródło tłumaczenia): 　太陽系全域に人類が進出した時代。 ⏎ 　犯罪組織「コネクション」は社会の裏側で、その魔手を広げていた。 ⏎ 　「かみそり」の異名を持つアイザックは、ブラスター・キッド、飛ばし屋・ボウィー、エンジェル・お町と共に、莫大な報酬と引き換えに悪を討つ始末屋「コズモレンジャーＪ９」を結成する。 ⏎ 　彼等はブライシンクロン理論によって変形・巨大化するブライガーを駆り、星々を股に掛け、様々な敵と戦っていく。 ⏎ 　そして、姿を現す最大の敵、ヌビア・コネクションのカーメン・カーメン。 ⏎ 　Ｊ９は、太陽系を造りかえるカーメンの野望「大アトゥーム計画」に立ち向かっていく。
> EN (odniesienie oficjalne, NIE polski): Humanity has spread throughout the solar system, but the insidious hand of the criminal organization Connection also spreads in the shadows of society. ⏎  ⏎ Isaac the Razor, together with Blaster Kid, Speedy Bowie, and Angel Omachi have formed the Cosmo Rangers J9, a troubleshooter organization that eliminates evil in exchange for hefty rewards. ⏎  ⏎ In Braiger, which can change form and grow massive thanks to the Brai-synchron principle, they travel from star to star facing various enemies. Standing against them is Khamen Khamen, head of the Nubia Connection and the greatest of their foes. ⏎  ⏎ It is up to J9 to stop Khamen Khamen's evil plan to reshape the solar system through the Great Atum Project.

### dic\_name\_FTDKRS\_00\_0

Adres: `dic\_text\_name-DLC1/000003b7:a8a0b000`

> \[BRAK PL: dic\_text\_name-DLC1/000003b7:a8a0b000\]
> JP (źródło tłumaczenia): 　左翔太郎は、探偵の師匠である鳴海荘吉との出会いと別れについて語る。 ⏎ 　かつて、風の街「風都」でガイアメモリを使う怪人・ドーパントが暗躍し始めた頃、少年・翔太郎は荘吉の背中を追い、探偵助手として働いていた。 ⏎ 　荘吉は探偵稼業の傍ら、仮面ライダースカルとして秘密裏に活動していたが、その彼の下に一本の依頼が入る。 ⏎ 　依頼を受けた荘吉は、謎の組織「ミュージアム」の施設から少年を救出し、フィリップと名付けるも、凶弾に倒れてしまう。 ⏎ 　依頼人からの「切り札」を荘吉に届けるため、その跡を追っていた翔太郎は失意の底で出会ったフィリップと共に仮面ライダーＷに変身し、荘吉の意志を受け継ぐのであった。 ⏎ 　そして彼等は、荘吉の娘・鳴海亜樹子と共に鳴海探偵事務所を引き継ぎ、風都の平和を守って戦っている。
> EN (odniesienie oficjalne, NIE polski): Shotaro's story of how he first met—and ultimately lost—his mentor, Sokichi Narumi. ⏎  ⏎ As Dopants—monsters using the powers of Gaia Memories—began to spread through the underbelly of the Windy City of Fuuto, a young Shotaro grew up trying to follow Sokichi's example, ultimately becoming his assistant. ⏎  ⏎ Sokichi ran his detective agency while secretly fighting as Kamen Rider Skull, until a fateful case came to him. He was tasked with rescuing a boy from the organization known as the Museum. He gave the boy the name Phillip, but Sokichi was shot dead before he could make his escape. ⏎  ⏎ However, Shotaro had followed him, hoping to bring him the "Joker" supplied by the client. In Sokichi's final moments, he passed on his business to Shotaro, and together with Philip, the pair would fulfil his wish. At this low point of Shotaro's life, he transforms into Kamen Rider Double with Philip. ⏎  ⏎ Sokichi's daughter Akiko joins them, so the three carry on his private investigation business, the Narumi Detective Agency, protecting Fuuto from threats both supernatural and everyday.

### dic\_name\_STLJEEG\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:72e0b000`

> \[BRAK PL: dic\_text\_name-DLC2/0000020f:72e0b000\]
> JP (źródło tłumaczenia): 　邪魔大王国の復活を察知した父・司馬遷次郎にサイボーグに改造された司馬宙（ひろし）は鋼鉄ジーグへとビルドアップする力を手にした。 ⏎ 　宙は、自らの意識をコンピュータに移植してマシンファーザーとなった遷次郎、パートナーの美和と共に邪魔大王国を迎え撃つ。 ⏎ 　邪魔大王国の女王ヒミカを退けた宙達の前に新たな敵、竜魔帝王が現れる。 ⏎ 　宙達はマシンファーザーという尊い犠牲を払いながらも竜魔帝王を倒し、平和を守り抜くのであった。 ⏎ 　
> EN (odniesienie oficjalne, NIE polski): Anticipating the resurrection of the Jamatai Kingdom, Senjiro Shiba transformed his son, Hiroshi, into a cyborg with the power to Build Up into Kotetsu Jeeg. ⏎ Together with Senjiro—who transferred his consciousness into a computer to become the Machine Father—and his partner, Miwa Uzuki, Hiroshi stood against the Jamatai Kingdom. ⏎  ⏎ After defeating Queen Himika of the Jamatai Kingdom, Hiroshi faced a new threat: Emperor Ryuma. ⏎  ⏎ Through the ultimate sacrifice of the Machine Father, Hiroshi succeeded in defeating Emperor Ryuma and preserving peace.　

### dic\_name\_GTERJBC\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:7360b001`

> \[BRAK PL: dic\_text\_name-DLC2/0000020f:7360b001\]
> JP (źródło tłumaczenia): 　ゲッターエンペラーは自らの目的のために新たなゲッターロボ・ノワールシリーズとそのパイロットであるリョウマ、ハヤト、ムサシを生み出す。 ⏎ 　彼等は異時空ブレーンワールドに送り込まれ、高次元意識体ブラフマーと戦っていた。
> EN (odniesienie oficjalne, NIE polski): For reasons known only to itself, Getter Emperor has spawned a new line of Getter Robos, the Noir-series, to be piloted by clones of Ryoma, Hayato, and Musashi. ⏎  ⏎ Their sole purpose is to be sent to the alternate space-time "braneworld", where they engage in an endless war against the higher-dimensional discarnate entity known as Brahma.

### dic\_name\_LGNHDGN\_00\_0

Adres: `dic\_text\_name-DLC2/0000020f:7360b003`

> \[BRAK PL: dic\_text\_name-DLC2/0000020f:7360b003\]
> JP (źródło tłumaczenia): 　小学生の高杉星史は、プラネットエナジーが生み出した勇者ダ・ガーンと出会う。 ⏎ 　地球の生命力「プラネットエナジー」を狙う宇宙からの侵略者に対して、星史は勇者達の隊長となり、彼等と共に敵に立ち向かっていく。 ⏎ 　両親にも友達にも正体を明かせない中、星史は時に悩み、時に傷つきながらもダ・ガーンたちとの絆を深め、悪の手から地球を守るために戦い続けるのであった。
> EN (odniesienie oficjalne, NIE polski): Seiji Takasugi, a fifth grader, encounters Da-Garn, a Brave Fighter birthed by Planet Energy. ⏎  ⏎ When unidentified aliens from outer space target the Planet Energy, which is Earth's own life force, Seiji becomes the Captain of the Brave Fighters, standing with them against the cosmic threat! ⏎  ⏎ Unable to reveal his duty to his parents or friends, Seiji must deal with his struggles in secret; nevertheless, he continues to fight to protect Earth from the hands of evil, while deepening his bond with Da-Garn and the other Braves.

### dic\_name\_LGNGIDEON\_00\_0

Adres: `dic\_text\_name-DLC3/00001546:ec20b000`

> \[BRAK PL: dic\_text\_name-DLC3/00001546:ec20b000\]
> JP (źródło tłumaczenia): 　地球の植民惑星であるソロ星。 ⏎ 　そこで地球人類は古代遺跡から巨大ロボット・イデオンと宇宙船ソロシップを発見する。それは異星人バッフ・クランの伝説に謳われる巨神であった。 ⏎ 　巨神の力を恐れるバッフ・クランの攻撃に対して、コスモ達はイデオンの力で抵抗する。彼等は追撃を逃れるため、ソロシップでソロ星を脱出する。 ⏎ 　誤解と愛憎の果て、そこで生まれた絆や想いも呑み込んで戦いは激化していき、ついには銀河全体を巻き込むまでに拡大していった。 ⏎ 　絶望的な逃避行の中、コスモ達は全てはイデオンに宿る第６文明人の意思「イデ」の導きによるものである事を知る。 ⏎ 　イデの試しに翻弄される人間達に待つ結末は……。 ⏎ 　
> EN (odniesienie oficjalne, NIE polski): Planet Solo—an Earth colony. ⏎  ⏎ On this distant planet, humanity uncovers the remnants of an ancient civilization: the Solo Ship, a space vessel, and the colossal robot Ideon—the Legendary Giant of Ide spoken of in the folklore of the alien race known as the Buff Clan. ⏎  ⏎ Fearing the power of the legendary giant, the Buff Clan launches a fierce assault on the settlement. Desperate to survive, Cosmo and a group of survivors fight back using Ideon. As the Buff Clan's relentless attacks continue, they have no choice but to flee Planet Solo aboard the Solo Ship. Amid misunderstandings, love, and hatred, the conflict escalates, eventually engulfing the entire galaxy. ⏎  ⏎ During their hopeless search for safety, Cosmo and the other survivors come to realize that they are being guided by the "Ide", the will of the Sixth Civilization that resides within Ideon. ⏎  ⏎ But what fate awaits humanity, at the end of the Ide's trials...?　

### dic\_name\_IDOLMXEN\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ee20b000`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ee20b000\]
> JP (źródło tłumaczenia): 　月崩壊とそれによる大災害「ロスト・アルテミス」から１００年余りが経過した復興歴１０７年。 ⏎ 　隕石除去人型重機「iDOL」とその操縦者「アイドルマスター」は、巨大多国籍企業「モンデンキント」に所属し、地球へと落ちてくる月の欠片（ドロップ）の迎撃に当たっていた。 ⏎ 　新たにインベルのアイドルマスターに選ばれた天海春香は、初めて触れるiDOLにとまどいながらも仲間達と共にiDOL奪取を目論む「トゥリアビータ」との戦いに巻き込まれていく。 ⏎ 　愛憎渦巻く戦いの末、別宇宙へと続くゲート「アウリン」から地球を守るため、春香とインベルは仲間達と共にアウリンへと突入するのであった。
> EN (odniesienie oficjalne, NIE polski): It is Restoration Year 107, over a hundred years since the destruction of the moon triggered the disaster known as Lost Artemis on Earth. ⏎  ⏎ To protect the planet from the remaining pieces of the moon that fall as Drops, idolmasters pilot their iDOLs, humanoid anti-meteorite machines, under the flag of the massive international corporation Mondenkind. ⏎  ⏎ After being chosen as the idolmaster for Imber, one of the iDOLs, Haruka Amami struggles to find her way as a pilot. Together with her companions she is dragged into battle against Turiavita, an organization seeking to seize control of the iDOLs. ⏎  ⏎ After a conflict that can be described as a whirlpool of hatred and passion, the Earth is faced with a new crisis, as Aulyn, a gate to another dimension, threatens to swallow it. To save the Earth, Haruka pilots the Imber alongside her comrades and dives headfirst into the gate.

### dic\_name\_STRDVRMVE\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b001`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ef20b001\]
> JP (źródło tłumaczenia): 　日本の南東に浮かぶ南十字島に現れたツナシ・タクト。南十字学園高等部に入学したタクトは、アゲマキ・ワコやシンドウ・スガタと友達になる。 ⏎ 　だが、その裏で秘密結社「綺羅星十字団」のメンバー達は、巨大人型ロボット「サイバディ」を使い、己の野望を果たそうとしていた。 ⏎ 　そして、タクトもまたサイバディ「タウバーン」のスタードライバーであり、サイバディの力を引き出す「銀河美少年」となり、綺羅星十字団に立ち向かっていく。 ⏎ 　サイバディを封印する宿命を持つ四方（よも）の巫女の一人であるワコ、王のサイバディ「キング・ザメク」のスタードライバーであるスガタ、そしてタクトは戦いながらも恋あり夢あり友情ありの青春を過ごす。 ⏎ 　激闘の果て、島の宿命から解放されたワコとスガタと共にタクトは、同じく解放されたサイバディで悪事を働く者達を止めるため、タウバーン・コンパートメントで戦い続ける。 ⏎ 　
> EN (odniesienie oficjalne, NIE polski): Takuto Tsunashi arrives on Southern Cross Island, a small island to the southeast of Japan. He begins school at Southern Cross High School and befriends Wako Agemaki and Sugata Shindo. ⏎  ⏎ Unbeknownst to them, the Kiraboshi Order of Cross is conspiring to use the Cybodies, giant robots sealed on the island, for their own ends. ⏎  ⏎ Takuto turns out to be not only the Star Driver of his own Cybody, Tauburn, but a Ginga Bishonen that can draw out their full potential, which he uses to fight against the Order. ⏎  ⏎ As Takuto fights though many battles, he's drawn into a whirlwind of love, adventure, and friendship with Wako, one of the four shrine maidens destined to unseal the Cybodies, and Sugata, the Star Driver of the king Cybody, King Samekh. ⏎  ⏎ Takuto succeeds in freeing Wako and Sugata from being trapped on the island at the end of a long, hard-fought conflict. Afterward, he continues fighting using Tauburn Compartment to prevent other unsealed Cybodies from being used for evil.　

### dic\_name\_CRSAGAD\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b003`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ef20b003\]
> JP (źródło tłumaczenia): 　高度に進化した情報技術「マナ」を手にした人類は、その魔法のごとき力で豊かな理想郷を手に入れた。 ⏎ 　その世界の大国であるミスルギ皇国の第一皇女・アンジュリーゼも、何不自由なく育ち、１６歳の洗礼の儀も無事終えるはずだった。 ⏎ 　しかし、儀式の最中にアンジュリーゼが、マナの使えない反社会的な人ならざる存在「ノーマ」である事が発覚。 ⏎ 　アンジュリーゼがノーマだとわかった人々は、掌を返して彼女を罵倒し、絶海の孤島アルゼナルに追放する。そこは人類の敵であるドラゴンと戦い続けなければ、生き残れない過酷な地。 ⏎ 　地位も権利も、そして名前すらも奪われ、アンジュリーゼからただの「アンジュ」となった彼女は、人型機動兵器パラメイル・ヴィルキスのメイルライダーとして生きていく事を決意する。 ⏎ 　戦いの中、アルゼナルのメイルライダー達や、古の民の末裔であるタスクと絆を深めていくアンジュ。 ⏎ 　だがその最中、今まで戦ってきたドラゴンが実は並行世界の地球に住む人間・竜の民であることが発覚する。それと共に、アンジュは世界を裏で操り、自らを調律者と名乗るエンブリヲこそが真の敵である事を知る。
> EN (odniesienie oficjalne, NIE polski): Humankind has acquired Mana, a highly evolved information technology, and with the magic-like power, they've created a bounteous utopia. ⏎  ⏎ Angelise, first princess of the Empire of Misurugi, one of the world's major powers, was raised without want for anything, and thought her Rite of Baptism on her sixteenth birthday would go off without a hitch. But in the middle of the ceremony, Angelise was revealed to be a Norma, an anti-societal sub-human without the ability to use Mana at all. ⏎  ⏎ Those who found out she was Norma turned on her, exiling her to Arzenal, a solitary island in distant seas—a cruel land where none could survive without keeping up the fight against the Dragons, the enemies of humanity. ⏎  ⏎ Stripped of her position, authority, and even her name, Angelise became simply Ange and resolved herself to living as the Mail Rider of the Villkiss, a Para-Mail humanoid mobile weapon. ⏎  ⏎ During the fighting, she deepened her bond with Tusk, a man born of the union between an Arzenal Mail Rider and a member of the Ancient Folk. However, Ange then discovered that the Dragons they'd been constantly fighting were actually humans known as the Dragon People who lived on a parallel Earth. Ange also discovered her true enemy: Embryo, a man calling himself the Tuner and manipulating the world from the shadows.

### dic\_name\_CRSAGAD\_00\_1

Adres: `dic\_text\_name-DLC3/001462c6:ef20b004`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ef20b004\]
> JP (źródło tłumaczenia): 　超常の力を持つエンブリヲに苦戦し、アンジュは次元の狭間に閉じ込められるも、愛するタスクや仲間達の助けとヴィルキスに秘められた力を解放することで、エンブリヲを倒すことに成功する。 ⏎ 　エンブリヲに支配された世界を破壊したアンジュは、支配者のいない新たな世界で仲間と共に夢であった喫茶店を開店するのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ During an arduous battle, Embryo used his supernatural abilities to trap Ange in the gap between dimensions.  ⏎  ⏎ However, after getting help from her beloved Tusk and her other allies, and by unleashing the Villkiss's hidden powers, she successfully defeated Embryo. ⏎  ⏎ Having destroyed the world ruled by Embryo and created a world without a ruler, Ange and her friends fulfilled their dream of opening a cafe.

### dic\_name\_ERKSPESHE\_00\_0

Adres: `dic\_text\_name-DLC3/001462c6:ef20b005`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ef20b005\]
> JP (źródło tłumaczenia): 　１０年前、スカブコーラルの中にある仮想世界が崩壊し、その中に生きる人々が現実の地球に出現する「大融合」が発生した。突如出現した仮想世界「グリーンアース」と現実世界「ブルーアース」の人類はいきなりの共存を迫られ、そこには根深い対立が生まれていた。 ⏎ 　エウレカは愛するレントンを失いながらも、「大融合」を引き起こした世界への贖罪のため戦い続けている。 ⏎ 　その中でエウレカは、かつての自分のようにスカブコーラルを操る力を持つ少女・アイリスの保護を命じられる。 ⏎ 　アイリスを狙うデューイ・ノヴァクの襲撃により孤立したエウレカとアイリスは、逃避行の中で自らの使命と存在に向き合っていく。
> EN (odniesienie oficjalne, NIE polski): Ten years ago, the virtual world inside the Scab Corals collapsed, causing those who lived there to appear on the real Earth in an event known as the Great Merging. Suddenly forced to coexist, the humans from the virtual world and those from the real world—Green Earth and Blue Earth respectively—have developed a deeply ingrained antagonism. ⏎  ⏎ Eureka herself had triggered the Great Merging. Despite losing her beloved Renton, she fought on to atone for what she did to the world. ⏎ During this time, Eureka received orders to protect Iris; a girl who can control Scab Corals like Eureka once could. However, the pair was isolated by Dewey Novak's attacks targeted against Iris and forced to go on the run. Their journey led them to confront their responsibilities and accept who they are.

### dic\_name\_ERKSPESHE\_00\_1

Adres: `dic\_text\_name-DLC3/001462c6:ef20b006`

> \[BRAK PL: dic\_text\_name-DLC3/001462c6:ef20b006\]
> JP (źródło tłumaczenia): 　エウレカは捕らえられたアイリスを救うためにデューイと戦う。エウレカは勝利を収めたものの、デューイはかつてグリーンアース人類が使用した旧星間宇宙移民船を爆破し、地球へと落下させる。 ⏎ 　崩壊が迫る中、エウレカは現れたニルヴァーシュＺに乗り込み、世界を救うために戦う。 ⏎ 　エウレカは世界を包み込むスカブコーラルの光の中、愛するレントンと再会し、世界は救われるのであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ After Iris was captured, Eureka brought the fight to Dewey to rescue her. Though Eureka emerged victorious, Dewey then destroyed the old interstellar immigration spaceship once used by the people of Green Earth, sending it plummeting toward the planet. ⏎  ⏎ With total ruin imminent, Eureka boarded the newly appeared Nirvash Z and fought to save the world. In the light of the Scab Corals engulfing the planet, Eureka reunited with her beloved Renton, and the world was saved.

### dic\_name\_GNWOM\_00\_2

Adres: `dic\_text\_name-DLC4/000005b2:11c28005`

> \[BRAK PL: dic\_text\_name-DLC4/000005b2:11c28005\]
> JP (źródło tłumaczenia): 　プロスペラの計画に翻弄されるミオリネとスレッタ、そしてスペーシアンとアーシアン。 ⏎ 　スレッタは自身がエアリアルに宿るエリクト・サマヤのリプリチャイルドである事を知り、計画を始動させたプロスペラから切り捨てられる。一方のミオリネは意識不明となった父・デリングの後を継ぐべくベネリットグループ総裁になろうとするが、プロスペラによって宇宙と地球の戦いの火種となってしまい、失意の底へと叩き込まれる。 ⏎ 　しかし、スレッタは自らのやるべきことを見つけ、その真っ直ぐな気持ちに救われたミオリネも再び立ち上がる。 ⏎ 　プロスペラはデータストームの中でしか生きられないエリクトのために巨大要塞「クワイエット・ゼロ」を起動させる。スレッタとミオリネは地球寮の仲間やグエルたちと共にクワイエット・ゼロに向かい、その阻止に成功する。 ⏎ 　ミオリネはベネリットグループの解散を発表し、ガンダムはクワイエット・ゼロと共に消失したが、エリクトは新たな姿を得ることになる。 ⏎ 　３年後、それぞれが自分の道を進む中、スレッタとミオリネはお互いの手を取り合い、今できることに向けてともに歩いていく。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Both Miorine and Suletta, as well as the Spacians and the Earthians, are at the mercy of Prospera's plan. ⏎  ⏎ Suletta learns that she is a repli-child of Ericht Samaya, whose consciousness resides within the Aerial. Prospera casts Suletta aside after setting the plan in motion. Miorine tries to become president of the Benerit Group to succeed her unconscious father, Delling. Despite this, Prospera turns Miorine into the catalyst for a conflict between space and Earth, driving her into despair. However, Suletta discovers her purpose, and Miorine, saved by Suletta's sincerity, is able to rise again. ⏎  ⏎ Prospera activates the giant fortress Quiet Zero for Ericht, who can only live within the data storm. Suletta and Miorine, along with their friends from Earth House and Guel's group, head for Quiet Zero and succeed in stopping it. ⏎  ⏎ Miorine announces the dissolution of the Benerit Group. The Gundams vanish along with Quiet Zero, and Ericht takes on a new form. ⏎  ⏎ Three years later, with each of them having followed their own path, Suletta and Miorine take each other's hands and promise to walk forward together toward what they can do now.

## Słownik pojęć

### dic\_word\_zinguji\_title

Adres: `dic\_text\_word/00000826:db60b000`

> \[BRAK PL: dic\_text\_word/00000826:db60b000\]
> JP (źródło tłumaczenia): 神宮寺
> EN (odniesienie oficjalne, NIE polski): Jinguji

### dic\_word\_zinguji\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b000`

> \[BRAK PL: dic\_text\_word/00000826:dbe0b000\]
> JP (źródło tłumaczenia): 　コープランダー隊の隊員で、ブルーガーのメインパイロット。 ⏎ 　フルネームは神宮寺力（じんぐうじ・ちから）。 ⏎ 　クールなリアリストで当初は洸と対立する事もあったが、互いの力を認めた後は良き仲間となった。 ⏎ 　妖魔巨烈獣バラゴーンとの戦いにおいて、窮地に陥った洸を助けるため、爆弾を搭載したブルーガーで敵に突撃し、自らの生命と引き換えに勝機をもたらした。
> EN (odniesienie oficjalne, NIE polski): One of the members of the Co-oplanders and the main pilot of the Bluegar. ⏎ His full name is Chikara Jinguji. ⏎  ⏎ A no-nonsense man who approached life with logic and reason, he tended to lock horns with Akira at first, but eventually they recognized each other's strengths and became good friends. ⏎  ⏎ When the Yoma Fury Beast Baragorn proved too much for Reideen, he realized that the only way to defeat it would be with a powerful explosive triggered from within the beast. He loaded a bomb onto the Bluegar and dove inside Baragorn, sacrificing his life to give Akira a chance at victory.

### dic\_word\_yoma\_em\_title

Adres: `dic\_text\_word/00000826:dbe0b002`

> \[BRAK PL: dic\_text\_word/00000826:dbe0b002\]
> JP (źródło tłumaczenia): 妖魔帝国
> EN (odniesienie oficjalne, NIE polski): Yoma Empire

### dic\_word\_yoma\_em\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b003`

> \[BRAK PL: dic\_text\_word/00000826:dbe0b003\]
> JP (źródło tłumaczenia): 　１万２０００年の間、眠りについていた悪魔達の帝国。 ⏎ 　かつて栄えたムー帝国と共に滅んだが、悪魔世紀の実現のために現代に復活した。
> EN (odniesienie oficjalne, NIE polski): 　An empire of demons that recently awoke from a 12,000-year slumber. ⏎ It was destroyed along with the prosperous Empire of Mu ages ago. They have returned in the modern era to usher in the Age of Demons once more.

### dic\_word\_barao\_title

Adres: `dic\_text\_word/00000826:dbe0b005`

> \[BRAK PL: dic\_text\_word/00000826:dbe0b005\]
> JP (źródło tłumaczenia): バラオ
> EN (odniesienie oficjalne, NIE polski): Barao

### dic\_word\_barao\_00\_0

Adres: `dic\_text\_word/00000826:dbe0b006`

> \[BRAK PL: dic\_text\_word/00000826:dbe0b006\]
> JP (źródło tłumaczenia): 　妖魔帝国の支配者であり、妖魔大帝の名を持つ。 ⏎ 　地下神殿の石像の中で眠っていたが、妖魔帝国の前線指揮官プリンス・シャーキンが討たれた後に復活を果たした。 ⏎ 　ライディーンをはるかにしのぐ巨体を持っており、その下半身は妖魔島に埋まっている。 ⏎ 　悪魔世紀の実現のため、神秘のエネルギー・ムートロンを奪おうとして巨烈獣をライディーンに送り込んだ。
> EN (odniesienie oficjalne, NIE polski): The ruler of the Yoma Empire, usually referred to as the Yoma Emperor. ⏎  ⏎ He was sealed in a stone statue in his underground temple, but eventually broke free after Prince Sharkin, the frontline commander of the Yoma Empire, died in battle against Reideen. ⏎  ⏎ He has a massive body that far exceeds Reideen in size, with his lower body rooted to Yoma Island itself. ⏎  ⏎ To usher in the Age of Demons, he sends a series of Fury Beasts to defeat Reideen and steal the mystical energy known as Mutron that powers it.

### dic\_word\_barao\_00\_1

Adres: `dic\_text\_word/00000826:dc20b000`

> \[BRAK PL: dic\_text\_word/00000826:dc20b000\]
> JP (źródło tłumaczenia): 　全ての配下を失った後、自ら出陣して驚異的な力で洸を苦しめたが、洸の母・玲子の生命を懸けた祈りによってムートロンの力を得たライディーンの前に敗北した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ With all his subordinates felled, he finally took to battle himself, overpowering Akira with his incredible might. He was finally defeated when Reiko, Akira's mother, sacrificed her life to grant Reideen the full power of Mutron.

### dic\_word\_canvel\_ali\_title

Adres: `dic\_text\_word/00000826:dc20b001`

> \[BRAK PL: dic\_text\_word/00000826:dc20b001\]
> JP (źródło tłumaczenia): キャンベル星人
> EN (odniesienie oficjalne, NIE polski): Campbellians

### dic\_word\_canvel\_ali\_00\_0

Adres: `dic\_text\_word/00000826:dc20b002`

> \[BRAK PL: dic\_text\_word/00000826:dc20b002\]
> JP (źródło tłumaczenia): 　地球侵略を企む異星人。 ⏎ 　大将軍ガルーダや女帝ジャネラの指揮の下、マグマ獣が地球に送り込まれるが、コン・バトラーＶの活躍により、その野望は阻止された。 ⏎ 　女帝ジャネラとの最終決戦後、キャンベル星の本星では平和主義者が実権を握り、地球侵略は終息した。
> EN (odniesienie oficjalne, NIE polski): An alien race that invaded Earth. ⏎  ⏎ They sent their Magma Beasts into battle, first under the command of the Great General Garuda, and later Empress Janera herself, but Combattler V managed to foil their plans at every turn. ⏎  ⏎ After Empress Janera's ultimate defeat, the pacifist faction rose to power on Planet Campbell, ending the senseless war.

### dic\_word\_aeug\_title

Adres: `dic\_text\_word/00000826:dc20b004`

> \[BRAK PL: dic\_text\_word/00000826:dc20b004\]
> JP (źródło tłumaczenia): エゥーゴ
> EN (odniesienie oficjalne, NIE polski): AEUG

### dic\_word\_aeug\_00\_0

Adres: `dic\_text\_word/00000826:dc20b005`

> \[BRAK PL: dic\_text\_word/00000826:dc20b005\]
> JP (źródło tłumaczenia): 　地球連邦軍を私物化するティターンズに対抗するために結成された組織。 ⏎ 　正式名称はＡｎｔｉ　Ｅａｒｔｈ　Ｕｎｉｏｎ　Ｇｒｏｕｐ（反地球連邦組織）。 ⏎ 　アナハイム・エレクトロニクスやルオ商会のような企業とも手を組み、政財界との繋がりが深い地球連邦軍准将ブレックス・フォーラが指導者であることから軍事、政治面でもそれなりの力を持っている。 ⏎ 　元々はティターンズと同じく地球連邦軍の一部であったため、その構成員である軍人の大半は連邦軍所属であるが、クワトロ・バジーナ大尉など、元ジオン軍の人間も参加している。 ⏎ 　グリプスでのガンダムＭｋ－Ⅱ強奪事件を契機に、それまで小競り合い程度あったティターンズとの対立は決定的なものとなった。 ⏎ 　グリプス戦役以降は、地球連邦軍の一部としてハマーン率いるネオ・ジオン軍と戦った。
> EN (odniesienie oficjalne, NIE polski): An organization formed to resist the Titans, the appropriators of the Earth Federation Forces. Its official name is Anti Earth Union Group. ⏎  ⏎ Created from mergers between Anaheim Electronics and other corporations such as Luio &amp; Co. and headed by Blex Forer, an EFF commodore with deep ties to the political world, the AEUG has formidable military and political influence. ⏎  ⏎ Because it was originally a part of the EFF like the Titans, most of the AEUG's soldiers officially belong to the EFF, but it also counts former Zeon soldiers such as Lieutenant Quattro Bajeena among its ranks. ⏎  ⏎ After the theft of a Gundam Mk-II at Gryps, its minor squabble with the Titans escalated into full-on hostilities. ⏎  ⏎ After the Gryps Conflict, it fought as part of the EFF against Neo Zeon forces led by Haman.

### dic\_word\_nt\_title

Adres: `dic\_text\_word/00000826:dc20b007`

> \[BRAK PL: dic\_text\_word/00000826:dc20b007\]
> JP (źródło tłumaczenia): ニュータイプ
> EN (odniesienie oficjalne, NIE polski): Newtype

### dic\_word\_nt\_00\_0

Adres: `dic\_text\_word/00000826:dc20b008`

> \[BRAK PL: dic\_text\_word/00000826:dc20b008\]
> JP (źródło tłumaczenia): 　宇宙という新しい環境に適応した人類の進化の形とされる人々。 ⏎ 　直観力と洞察力に優れ、認識力の拡大により誤解なき相互理解が可能であるとされる。 ⏎ 　また、その力を使う事でパイロットとしても高い適性を見せる。
> EN (odniesienie oficjalne, NIE polski): People who have adapted to the new environment of outer space, said to be an evolved form of humanity. ⏎  ⏎ Newtypes possess excellent intuition and insight, and some say their expanded awareness allows them to mutually understand one another without misinterpretation. ⏎  ⏎ They can also use these abilities to vastly improve their performance while piloting.

### dic\_word\_g\_fight\_title

Adres: `dic\_text\_word/00000826:dc20b00a`

> \[BRAK PL: dic\_text\_word/00000826:dc20b00a\]
> JP (źródło tłumaczenia): ガンダムファイト
> EN (odniesienie oficjalne, NIE polski): Gundam Fight

### dic\_word\_g\_fight\_00\_0

Adres: `dic\_text\_word/00000826:dc20b00b`

> \[BRAK PL: dic\_text\_word/00000826:dc20b00b\]
> JP (źródło tłumaczenia): 　地球圏の政治的主導権をかけ、各スペースコロニー国家が選出したガンダムファイターがモビルファイター「ガンダム」に搭乗して戦う大会。 ⏎ 　四年に一度、地球全土をリングに予選が開催され、そこに勝ち残った者が決勝大会に進出する。 ⏎ 　これまでに１３回の大会が開かれている。 ⏎ 　優勝したガンダムファイターは、「ガンダム・ザ・ガンダム」と呼ばれ、勝利国は次の四年間、政治的実権を得る。 ⏎ 　人類間の戦争を避ける目的で提唱されたものであり、「理想的な戦争」とも呼ばれる。
> EN (odniesienie oficjalne, NIE polski): A competition in which Gundam Fighters representing each colony nation battle each other using unique Mobile Fighters known as "Gundams". The winning nation wins the right to political leadership of the Earth Sphere until the next tournament. ⏎  ⏎ Once every four years, a preliminary round is held inside a ring that covers the entire planet (making Earth itself the ring), with the winners advancing to the final round. ⏎ Thirteen tournaments have been held to date. ⏎  ⏎ The champion of the tournament earns the title of "Gundam of Gundams", and the nation they represent gains political authority over the other nations for the next four years, until the next tournament. ⏎  ⏎ The Gundam Fight was proposed as an alternative to military conflict, and many refer to it as the "ideal war".

### dic\_word\_shuffle\_title

Adres: `dic\_text\_word/00000826:dc20b00d`

> \[BRAK PL: dic\_text\_word/00000826:dc20b00d\]
> JP (źródło tłumaczenia): シャッフル同盟
> EN (odniesienie oficjalne, NIE polski): Shuffle Alliance

### dic\_word\_shuffle\_00\_0

Adres: `dic\_text\_word/00000826:dc20b00e`

> \[BRAK PL: dic\_text\_word/00000826:dc20b00e\]
> JP (źródło tłumaczenia): 　古来より戦いの秩序を守り続け、歴史の影で人類滅亡を阻止してきた一団。 ⏎ 　「キング・オブ・ハート」「クイーン・ザ・スペード」「ジャック・イン・ダイヤ」「クラブ・エース」「ブラック・ジョーカー」の五つの称号がある。 ⏎ 　それぞれ称号を持つ者の証として、メンバーの手の甲にはシャッフルの紋章が浮かび上がる。 ⏎ 　デビルガンダムとの戦いの中でドモンをはじめとする五人のファイターが、その称号を先代から受け継いだ。
> EN (odniesienie oficjalne, NIE polski): A group of people who, since ancient times, have upheld the principles of warfare and prevented the extinction of the human race from within the shadows of history. ⏎  ⏎ The Shuffle Alliance always consists of five individuals: the King of Hearts, the Queen of Spades, the Jack of Diamonds, the Ace of Clubs, and the Black Joker. ⏎ The Shuffle Crest appears on the back of each member's hand as proof of their title. ⏎  ⏎ Five Fighters, including Domon, inherited these titles from their predecessors during the battle against the Dark Gundam.

### dic\_word\_koh\_title

Adres: `dic\_text\_word/00000826:dc20b010`

> \[BRAK PL: dic\_text\_word/00000826:dc20b010\]
> JP (źródło tłumaczenia): キング・オブ・ハート
> EN (odniesienie oficjalne, NIE polski): King of Hearts

### dic\_word\_koh\_00\_0

Adres: `dic\_text\_word/00000826:dc20b011`

> \[BRAK PL: dic\_text\_word/00000826:dc20b011\]
> JP (źródło tłumaczenia): 　シャッフル同盟の中の一名が受け継ぐ称号。 ⏎ 　この称号を持つ者は、右手の甲に深紅のハートの紋章が浮かび上がる。 ⏎ 　師匠である東方不敗から、ドモンが受け継いだ。
> EN (odniesienie oficjalne, NIE polski): One of the titles passed down from one generation of the Shuffle Alliance to the next. ⏎  ⏎ The holder of this title is marked with a crimson heart crest on the back of their right hand. ⏎  ⏎ Domon inherited this title from his martial arts teacher, Master Asia, the Undefeated of the East.

### dic\_word\_toho\_title

Adres: `dic\_text\_word/00000826:dc20b013`

> \[BRAK PL: dic\_text\_word/00000826:dc20b013\]
> JP (źródło tłumaczenia): 東方不敗
> EN (odniesienie oficjalne, NIE polski): Master Asia

### dic\_word\_toho\_00\_0

Adres: `dic\_text\_word/00000826:dc20b014`

> \[BRAK PL: dic\_text\_word/00000826:dc20b014\]
> JP (źródło tłumaczenia): 　ドモンの師匠であり、ガンダムファイト第１２回大会の優勝者。 ⏎ 　素手でモビルスーツを倒すほどの常人離れした力を持ち、流派東方不敗と呼ばれる武術を編み出した。 ⏎ 　旧シャッフル同盟の「キング・オブ・ハート」であったが、その称号は弟子のドモンに受け渡している。 ⏎ 　デビルガンダムを利用して愛すべき地球の再生を目論んでいたが、ドモンとの激闘の末に敗北し、自らの過ちを認め、ドモンの腕の中で息を引き取った。
> EN (odniesienie oficjalne, NIE polski): Domon's martial arts teacher and champion of the 12th Gundam Fight tournament. He is also known as the Undefeated of the East. ⏎  ⏎ The founder of his own martial arts style, known as the School of Master Asia, he possesses superhuman strength and is able to destroy Mobile Suits with his bare hands. ⏎ Master Asia was the King of Hearts of the previous generation of the Shuffle Alliance. He passed his title to his pupil, Domon Kasshu. ⏎  ⏎ He planned to use the Dark Gundam to restore the nature of his beloved Earth, but he was defeated at the end of a climactic battle with Domon. Admitting the error of his ways, he dies in the arms of his pupil.

### dic\_word\_dg\_title

Adres: `dic\_text\_word/00000826:dc20b016`

> \[BRAK PL: dic\_text\_word/00000826:dc20b016\]
> JP (źródło tłumaczenia): デビルガンダム
> EN (odniesienie oficjalne, NIE polski): Dark Gundam

### dic\_word\_dg\_00\_0

Adres: `dic\_text\_word/00000826:dc20b017`

> \[BRAK PL: dic\_text\_word/00000826:dc20b017\]
> JP (źródło tłumaczenia): 　「自己再生」「自己進化」「自己増殖」の三つの特徴を備えた機動兵器。 ⏎ 　元々は「アルティメットガンダム」と呼ばれ、地球再生を目的に開発されたものであったが、その力をめぐる思惑の中でプログラムに変化が生じ、人類の敵となった。 ⏎ 　機体の制御は、コアとなる生体ユニットの精神エネルギーによって行われている。 ⏎ 　ネオジャパンの軍人であるウルベ少佐の策略により、レインを生体コアに周辺のコロニーを吸収して成長を続けたが、レインを救出したドモンによって打倒された。
> EN (odniesienie oficjalne, NIE polski): A mobile weapon that possesses the three principles of self-regeneration, self-evolution, and self-replication. ⏎  ⏎ It was originally designated as the Ultimate Gundam, developed with the goal of restoring Earth's environment, but due to a malfunction in its programming, it identified humanity as a target for elimination. ⏎ The Dark Gundam is controlled by the mental energy of a living bio-unit in its core. ⏎  ⏎ Through the machinations of Major Urube of Neo Japan's military, Rain was forced to become the Dark Gundam's bio-unit, causing the Dark Gundam to grow and absorb the surrounding colony. Eventually, Domon was able to free her from these bonds, and together they defeated the Dark Gundam.

### dic\_word\_kyral\_title

Adres: `dic\_text\_word/00000826:dc20b019`

> \[BRAK PL: dic\_text\_word/00000826:dc20b019\]
> JP (źródło tłumaczenia): キラル・メキレル
> EN (odniesienie oficjalne, NIE polski): Kyral Mekirel

### dic\_word\_kyral\_00\_0

Adres: `dic\_text\_word/00000826:dc20b01a`

> \[BRAK PL: dic\_text\_word/00000826:dc20b01a\]
> JP (źródło tłumaczenia): 　ネオネパール代表で、盲目のガンダムファイター。 ⏎ 　一流の殺し屋であり、第１３回ガンダムファイトでは対戦相手を暗殺する事で不戦勝を重ねていたが、ドモンとの闘いで敗北した。 ⏎ 　その後、ウルベ少佐がデビルガンダムを利用して全世界に宣戦布告した際には、地球を防衛するガンダム連合を率いて戦った。
> EN (odniesienie oficjalne, NIE polski): The blind Gundam Fighter representing Neo Nepal. ⏎  ⏎ A first-rate assassin, he won several rounds in the 13th Gundam Fight by default by secretly murdering his upcoming opponents. He was eventually stopped by Domon, who survived his assassination attempt and then defeated him in battle. ⏎  ⏎ After Major Urube declared war on the world using the power of the Dark Gundam, he leads the World Gundam Federation to protect the Earth from his threat.

### dic\_word\_love\_title

Adres: `dic\_text\_word/00000826:dc20b01c`

> \[BRAK PL: dic\_text\_word/00000826:dc20b01c\]
> JP (źródło tłumaczenia): 世紀の大告白
> EN (odniesienie oficjalne, NIE polski): Greatest Confession of Love

### dic\_word\_love\_00\_0

Adres: `dic\_text\_word/00000826:dc20b01d`

> \[BRAK PL: dic\_text\_word/00000826:dc20b01d\]
> JP (źródło tłumaczenia): 　デビルガンダムの生体ユニットと化したレインを救い出すためにドモンの放った熱い叫びを指す。 ⏎ 　父・ミカムラ博士が犯した罪への負い目からドモンを拒み続けていたレインに対してドモンは愛を叫び、その想いによってレインのかたくなだった心は氷解し、デビルガンダムの支配から抜け出す事に成功した。 ⏎ 　その後、二人の愛の力は石破ラブラブ天驚拳を生み出し、デビルガンダムを葬り去った。
> EN (odniesienie oficjalne, NIE polski): This refers to Domon's passionate declaration to Rain, who had been turned into the bio-unit of the Dark Gundam. ⏎  ⏎ Rain had closed her heart, overwhelmed with guilt for the crimes committed by her father, Dr. Mikamura. Domon's heartfelt confession managed to tear down the wall she had built around her heart, freeing her from the control of the Dark Gundam. ⏎  ⏎ Emboldened by the power of their love, they destroy the core of the Dark Gundam together with the Sekiha Love Love Tenkyoken.

### dic\_word\_w\_fang\_title

Adres: `dic\_text\_word/00000826:dc20b01f`

> \[BRAK PL: dic\_text\_word/00000826:dc20b01f\]
> JP (źródło tłumaczenia): ホワイトファング
> EN (odniesienie oficjalne, NIE polski): White Fang

### dic\_word\_w\_fang\_00\_0

Adres: `dic\_text\_word/00000826:dc20b020`

> \[BRAK PL: dic\_text\_word/00000826:dc20b020\]
> JP (źródło tłumaczenia): 　コロニー居住者が地球の干渉を排除する目的で設立した武力組織。 ⏎ 　設立者はカーンズであったが、彼からの誘いによりサンクキングダムの王族であったミリアルド・ピースクラフト（＝ゼクス）が指導者となった。 ⏎ 　ＯＺによって実権を握られた地球に対してミリアルドが宣戦布告をして、全面戦争となったが、それはトレーズと同じく、戦争の悲惨さを全ての人に伝える事が目的であった。 ⏎ 　ミリアルドがヒイロとの一騎打ちに敗れた事で、その戦いは終結した。
> EN (odniesienie oficjalne, NIE polski): An armed organization formed by the inhabitants of the colonies to free themselves from any interference from Earth. ⏎  ⏎ It was founded by Quinze, but he later offered the leadership position to Milliardo Peacecraft (Zechs), a member of the royal family of the Sanc Kingdom. ⏎  ⏎ Milliardo declared war on Earth, which had been occupied by OZ, and a full-scale conflict soon ensued; however, Milliardo's true goal was the same as Treize's, to teach all humans the misery and futility of war. ⏎  ⏎ The conflict ended with Milliardo's defeat in a heated duel with Heero.

### dic\_word\_treize\_title

Adres: `dic\_text\_word/00000826:dc20b022`

> \[BRAK PL: dic\_text\_word/00000826:dc20b022\]
> JP (źródło tłumaczenia): トレーズ
> EN (odniesienie oficjalne, NIE polski): Treize

### dic\_word\_treize\_00\_0

Adres: `dic\_text\_word/00000826:dc20b023`

> \[BRAK PL: dic\_text\_word/00000826:dc20b023\]
> JP (źródło tłumaczenia): 　ロームフェラ財団の幹部であり、秘密結社ＯＺの総帥。 ⏎ 　フルネームはトレーズ・クシュリナーダ。 ⏎ 　絶対的なカリスマと天才的な頭脳を持つ野心家で、腐敗した世界の改革と倦怠する時代の変革を策謀する。 ⏎ 　ＭＳパイロットとしても一流であり、戦争や戦いに対して独自の哲学と美学を持っている。 ⏎ 　また、戦争に対する罪の意識も強く、戦いの中で散っていった人間の数と名前を全て記憶している。 ⏎ 　ＯＺのクーデター後、ロームフェラ財団の方針に公然と異を唱えたため一度は失脚、反逆者として幽閉されるが、後に再びＯＺ総帥へ返り咲いた。 ⏎ 　彼に一度敗北した五飛にとって宿敵とも言える存在であり、最後の戦いでは彼と一騎打ちに持ち込む。戦いは五飛の勝利に終わるが、それ自体がトレーズの望みであり、想いの行き場を失った五飛は以降も苦しむ事となった。
> EN (odniesienie oficjalne, NIE polski): An executive of the Romefeller Foundation, as well as the head of the secret society known as OZ. ⏎  ⏎ His full name is Treize Khushrenada. ⏎  ⏎ A man of ambition, genius, and absolute charisma, he plans to reform the corrupt world and bring revolution to the current, stagnant era. ⏎  ⏎ He is a top-class Mobile Suit pilot, always following his personal philosophy and aesthetics of war and combat. ⏎  ⏎ He is acutely aware of the sins of war, so much so that he remembers the exact number and every single name of the soldiers who have died in battle, for or against him. ⏎  ⏎ After OZ's military coup, he was placed under house arrest for openly opposing the policies of the Romefeller Foundation, but eventually returned to his position as head of the organization. ⏎  ⏎ Following his defeat in a sword fight, Wufei considered him his mortal enemy. In the final battle, Wufei once again challenges Treize in Mobile Suit combat, achieving his long-sought victory; however, dying in this duel was part of Treize's plan all along, leaving Wufei with a strong sense of frustration and dissatisfaction.

### dic\_word\_cinq\_k\_title

Adres: `dic\_text\_word/00000826:dc20b025`

> \[BRAK PL: dic\_text\_word/00000826:dc20b025\]
> JP (źródło tłumaczenia): サンクキングダム
> EN (odniesienie oficjalne, NIE polski): Sanc Kingdom

### dic\_word\_cinq\_k\_00\_0

Adres: `dic\_text\_word/00000826:dc20b026`

> \[BRAK PL: dic\_text\_word/00000826:dc20b026\]
> JP (źródło tłumaczenia): 　かつて北欧に存在した、完全平和主義を提唱する国家。 ⏎ 　王家であるピースクラフト家の統治により繁栄するが、その存在を地球圏統一連合に危険視された事で滅ぼされた。 ⏎ 　王女であるリリーナ・ピースクラフトが元首に就任した事で一時は復興を遂げたが、再び戦火に巻き込まれ、彼女により解体が宣言された。
> EN (odniesienie oficjalne, NIE polski): A nation in Northern Europe which advocated a philosophy of total pacifism. ⏎  ⏎ It once flourished under the rule of the Peacecraft family, but the United Earth Sphere Alliance deemed its ideology as dangerous and ordered its destruction. ⏎  ⏎ The Sanc Kingdom was temporarily restored when Princess Relena Peacecraft assumed the position of Chief Representative (refusing to call herself "Queen"). As the kingdom was once again engulfed in the flames of war, Relena declared its surrender and dissolution.

### dic\_word\_puppy\_title

Adres: `dic\_text\_word/00000826:dc20b028`

> \[BRAK PL: dic\_text\_word/00000826:dc20b028\]
> JP (źródło tłumaczenia): 子犬
> EN (odniesienie oficjalne, NIE polski): Puppy

### dic\_word\_puppy\_00\_0

Adres: `dic\_text\_word/00000826:dc20b029`

> \[BRAK PL: dic\_text\_word/00000826:dc20b029\]
> JP (źródło tłumaczenia): 　ヒイロが任務を遂行する過程で犠牲となった子犬を指す。 ⏎ 　子犬と共に無関係な少女の生命までも奪ってしまった事は、その後のヒイロの思考や行動に影響を与えている。
> EN (odniesienie oficjalne, NIE polski): A puppy that died as a result of Heero's actions during one of his missions. ⏎  ⏎ The death of that girl and her dog haunts Heero to this day, influencing his thoughts and actions ever since.

### dic\_word\_natak\_title

Adres: `dic\_text\_word/00000826:dca0b001`

> \[BRAK PL: dic\_text\_word/00000826:dca0b001\]
> JP (źródło tłumaczenia): ナタク
> EN (odniesienie oficjalne, NIE polski): Nataku

### dic\_word\_natak\_00\_0

Adres: `dic\_text\_word/00000826:dca0b002`

> \[BRAK PL: dic\_text\_word/00000826:dca0b002\]
> JP (źródło tłumaczenia): 　張五飛の妻を指す。故人。 ⏎ 　五飛は自らの搭乗するガンダムに妻の魂が宿っていると考えており、自機を「ナタク」と呼んでいる。
> EN (odniesienie oficjalne, NIE polski): The nickname of Chang Wufei's wife, who died after being mortally wounded in battle. ⏎  ⏎ Wufei believes that his wife's spirit resides in his Gundam, which is why he always refers to his Mobile Suit as "Nataku".

### dic\_word\_op\_meteor\_title

Adres: `dic\_text\_word/00000826:dca0b004`

> \[BRAK PL: dic\_text\_word/00000826:dca0b004\]
> JP (źródło tłumaczenia): オペレーション・メテオ
> EN (odniesienie oficjalne, NIE polski): Operation Meteor

### dic\_word\_op\_meteor\_00\_0

Adres: `dic\_text\_word/00000826:dca0b005`

> \[BRAK PL: dic\_text\_word/00000826:dca0b005\]
> JP (źródło tłumaczenia): 　各スペースコロニーから五機のガンダムを隕石に偽装して地球に送り込んだ作戦。 ⏎ 　地球圏統一連合の支配を目論んでいた秘密結社ＯＺを阻止するために実行された。 ⏎ 　五機のガンダムパイロットとして、ヒイロ、デュオ、トロワ、カトル、五飛が参加した。
> EN (odniesienie oficjalne, NIE polski): A plan to send five Gundams from different colonies to Earth disguised as meteorites. ⏎  ⏎ The plan was set in motion to prevent the secret society OZ from taking control of the United Earth Sphere Alliance. ⏎  ⏎ The five Gundam pilots involved in the operation were Heero, Duo, Trowa, Quatre, and Wufei.

### dic\_word\_op\_meteor\_00\_1

Adres: `dic\_text\_word/00000826:dca0b006`

> \[BRAK PL: dic\_text\_word/00000826:dca0b006\]
> JP (źródło tłumaczenia): 　しかし、デキム・バートンが発案した本来の作戦は全くの別物であり、コロニーを落下させる事によって地球を混乱に落とし入れ、その隙を突いてガンダムで地球を制圧するものであった。
> EN (odniesienie oficjalne, NIE polski):  ⏎ However, the original plan devised by Dekim Barton was to plunge Earth into chaos by dropping colonies on it, and then using the Gundams to gain control of the planet.

### dic\_word\_logos\_title

Adres: `dic\_text\_word/00000826:dca0b007`

> \[BRAK PL: dic\_text\_word/00000826:dca0b007\]
> JP (źródło tłumaczenia): ロゴス
> EN (odniesienie oficjalne, NIE polski): Logos

### dic\_word\_logos\_00\_0

Adres: `dic\_text\_word/00000826:dca0b008`

> \[BRAK PL: dic\_text\_word/00000826:dca0b008\]
> JP (źródło tłumaczenia): 　有史以来存在するとも言われている軍需産業複合体で、強い政治への介入力を持っている。戦争と復興を裏で操り、莫大な利益を獲得してきた死の商人達によって構成される。 ⏎ 　ブルーコスモスの支援母体であり、地球連合とコーディネイターの戦争を仕向けるべく世論を誘導していた。ブルーコスモスの前盟主ムルタ・アズラエルと現盟主ロード・ジブリールもロゴスのメンバーである。ロゴスとしては戦争を継続して利益を追求することこそが目的であり、ブルーコスモスがコーディネイター根絶を掲げるのは、彼ら２名の個人的感情による部分が大きい。 ⏎ 　独自の戦力を持たないため、前大戦時には地球連合軍を動かしてコーディネイターを殲滅しようとした。そして戦後は、より直接的に力を行使するべくファントムペインを組織させている。 ⏎ 　のちにデュランダルによって存在と所業を明らかにされたため、怒る市民の暴動によって大半のメンバーが逮捕、またはリンチを受けて死亡している。最後まで生き残っていたジブリールも、切り札のレクイエムを奪われた後、逃亡する艦ごと撃墜された。
> EN (odniesienie oficjalne, NIE polski): A military-industrial complex said to have existed since the dawn of history that possesses significant political intervention power. Manipulating war and reconstruction from behind the curtain, it comprises of arms dealers who have come to acquire vast profits. ⏎  ⏎ As the supporting parent organization of Blue Cosmos, Logos guided popular opinion in order to induce the war between the Earth Alliance and Coordinators. Multa Azrael, the previous leader of Blue Cosmos, and Lord Djibril, its current leader, are both members. Logos's mission is to seek profits by prolonging wars, and the personal feelings of those two members played a large part in Blue Cosmos advocating for the eradication of Coordinators. ⏎  ⏎ Because Logos doesn't have an independent military force of its own, they attempted to manipulate the Earth Alliance's military into wiping out the Coordinators in the previous war. Once the war was over, they organized Phantom Pain in order to more directly wield military force. ⏎  ⏎ Later, when its existence and deeds were revealed by Dullindal, many of its members were arrested or outright killed by angry civilian mobs and riots. Djibril, the last survivor, went down with his ship as he fled his stolen trump card, Requiem.

### dic\_word\_dullindal\_title

Adres: `dic\_text\_word/00000826:dca0b00a`

> \[BRAK PL: dic\_text\_word/00000826:dca0b00a\]
> JP (źródło tłumaczenia): デュランダル
> EN (odniesienie oficjalne, NIE polski): Dullindal

### dic\_word\_dullindal\_00\_0

Adres: `dic\_text\_word/00000826:dca0b00b`

> \[BRAK PL: dic\_text\_word/00000826:dca0b00b\]
> JP (źródło tłumaczenia): 　前プラント最高評議会議長。 ⏎ 　フルネームはギルバート・デュランダル。 ⏎ 　前議長パトリック・ザラとは異なり、ナチュラルとの共存・平和への道を模索した穏健派。ユニウスセブン落下事件や、その後の地球連合軍との戦いの際には、常に冷静で的確な判断を下し、優れたリーダーシップを見せた。 ⏎ 　ミーア・キャンベルをラクス・クラインの替え玉として担ぎ上げ、プラント全体の戦意高揚を図ろうとするが、裏でラクス本人の暗殺を目論んだことが露見し、キラ達の不信を買うことになった。 ⏎ 　その最終目的は、人類を遺伝子レベルで統制する管理社会を構築することであり、それを「デスティニープラン」と称した。ロゴスを壊滅させた後、世界に向けてプランの導入・実行を宣言するも、進化の止まってしまう世界を拒むキラ達によって阻止された。 ⏎ 　最期は息子のように信頼を寄せていたレイに撃たれる。そして、かつては恋人同士であり、別れてもなお想いを寄せ続けていたタリアの腕の中で、その生涯の幕を下ろした。
> EN (odniesienie oficjalne, NIE polski): The former chairman of the PLANT Supreme Council. His full name is Gilbert Dullindal. ⏎  ⏎ Unlike the chairman before him, Patrick Zala, Dullindal was an advocate of peace and searched for a way to live alongside Naturals in harmony. He showed his excellent leadership abilities during the Junius Seven incident and during the war with the Earth Alliance after that by always staying calm and issuing clear orders. ⏎  ⏎ He attempted to raise morale in the PLANTs by promoting Meer Campbell, a stand-in for Lacus Clyne, but after his covert assassination attempt on the real Lacus was revealed, he lost the trust of Kira and others. ⏎  ⏎ His ultimate objective was to create a managed society that controlled humankind down to the genetic level, which he dubbed the Destiny Plan. After destroying Logos, introducing his plans to the world, and announcing he would put them into effect, Kira and the others stopped him, not wanting to end natural evolution on Earth. ⏎  ⏎ In his final moments, he is shot by Ray, whom Dullindal trusted like a son. Then, in the arms of Talia—the erstwhile lover he still had feelings for—he passed on.

### dic\_word\_gora\_gyre\_title

Adres: `dic\_text\_word/00000826:dca0b00d`

> \[BRAK PL: dic\_text\_word/00000826:dca0b00d\]
> JP (źródło tłumaczenia): ゴラオンとゲア・ガリング
> EN (odniesienie oficjalne, NIE polski): Goraon and Gyre-Garing

### dic\_word\_gora\_gyre\_00\_0

Adres: `dic\_text\_word/00000826:dca0b00e`

> \[BRAK PL: dic\_text\_word/00000826:dca0b00e\]
> JP (źródło tłumaczenia): 　いずれもバイストン・ウェルのオーラバトルシップ。 ⏎ 　ゴラオンは、ラウの国の国王フォイゾン・ゴウの孫娘であるエレ・ハンムが率いた反ドレイク陣営の戦力であり、ゲア・ガリングは、ドレイクと軍事同盟を結んだクの国の国王ビショット・ハッタの座乗艦。 ⏎ 　太平洋を舞台にした決戦において、ゴラオンはゲア・ガリングに特攻し、両艦は地上より消滅した。
> EN (odniesienie oficjalne, NIE polski): Two Aura Battleships from Byston Well. ⏎  ⏎ The Goraon, one of the main forces of the anti-Drake faction, was captained by Elle Hunm, granddaughter of Foizon Gow, king of the Land of Rau; the Gyre-Garing was the warship of king Bishot Hatta, King of the Land of Ku, who had formed a military alliance with Drake. ⏎  ⏎ During the decisive battle that took place over the Pacific Ocean, the Goraon rammed the Gyre-Garing in a suicide strike, causing both ships to disappear from the face of Upper Earth.

### dic\_word\_hyper\_title

Adres: `dic\_text\_word/00000826:dca0b010`

> \[BRAK PL: dic\_text\_word/00000826:dca0b010\]
> JP (źródło tłumaczenia): ハイパー化
> EN (odniesienie oficjalne, NIE polski): Going Hyper

### dic\_word\_hyper\_00\_0

Adres: `dic\_text\_word/00000826:dca0b011`

> \[BRAK PL: dic\_text\_word/00000826:dca0b011\]
> JP (źródło tłumaczenia): 　オーラ・マシンに乗る人間のオーラ力が極度に肥大化した時に起こる現象。 ⏎ 　怒り・悲しみ・憎しみなどのマイナスの感情に支配された時、人のオーラの力が拡大し、オーラ・マシンや肉体を巨大化させる。巨大化した姿は、バリアーがマシンの形に実体化したものと考えられている。 ⏎ 　絶大な力を生み出すものの、そこまで肥大化したオーラ力をコントロールする事は不可能であり、ハイパー化を引き起こした人間の精神と肉体は、最終的には崩壊してしまう。
> EN (odniesienie oficjalne, NIE polski): A phenomenon that occurs when a Battler's Aura Power causes their Aura Machine to increase in size. ⏎  ⏎ When a person is overcome by negative emotions such as anger, sadness, or hatred, their Aura Power expands, causing the Aura Machine to grow in size. This Hyper form is believed to be the physical manifestation of their barrier, taking the form of the original machine. ⏎  ⏎ Although the Hyper form can wield immense power, such a large amount of Aura Power is impossible to control, and the body and mind of the Battler who has gone Hyper will eventually collapse.

### dic\_word\_byston\_title

Adres: `dic\_text\_word/00000826:dca0b013`

> \[BRAK PL: dic\_text\_word/00000826:dca0b013\]
> JP (źródło tłumaczenia): バイストン・ウェル
> EN (odniesienie oficjalne, NIE polski): Byston Well

### dic\_word\_byston\_00\_0

Adres: `dic\_text\_word/00000826:dca0b014`

> \[BRAK PL: dic\_text\_word/00000826:dca0b014\]
> JP (źródło tłumaczenia): 　地上の海と陸の狭間にあると言われている異世界。魂の安息の地と呼ばれる。 ⏎ 　二つの世界は本来互いに不可侵の立場にあり、目に見えない境界線で厳密に区切られている。しかし、これら二つの世界は「オーラ・ロード」と呼ばれる転移空間でつながれており、魂のみが行き来を許されている。肉体を伴った生者たる地上の人間がバイストン・ウェルに赴くこと、逆にバイストン・ウェルの人間が地上へ向かう事は重大な禁忌とされている。 ⏎ 　バイストン・ウェルの世界は大別して三層に隔てられている。一つは水の国ウォ・ランドン、フェラリオ達が統べる天界である。中部に位置するのがコモン界。ごく一般的な人々が生活を送るが、その生活レベルは地上での中世欧州程度であり、オーラ・マシンによる戦乱の拡大までは、斬撃戦が戦いの基本だった。最下層は闇の蛮人ガロウ・ランの支配するボッブ・レッスである。 ⏎ 　禁忌を破ってコモン界に地上人が召喚されてオーラ・マシンが開発された事により、バイストン・ウェルと地上は大きな戦いに包まれる事となった。
> EN (odniesienie oficjalne, NIE polski): Another world said to exist "between the sea and the shore of Earth". It is also known as the resting place of souls. ⏎  ⏎ Earth and Byston Well are strictly separated by an invisible boundary; however, they are connected by a transitional space called Aura Road, which only souls are allowed to cross. It is forbidden for a living person from Earth to go to Byston Well and for a resident of Byston Well to go to Earth. ⏎  ⏎ Byston Well is divided into three levels. The top layer is Wa Landon, the Kingdom of Water, a celestial realm ruled by the Ferario; the middle layer is the World of the Commoners, which used to have a level of technology similar to that of medieval Europe until the introduction of the Aura Machines, which escalated the level of conflict; the lowest layer is Bobhless, ruled by savages known as Garow Ran. ⏎  ⏎ The summoning of living Upper Earthers to the World of the Commoners and the subsequent development of the Aura Machines led to a great conflict in Byston Well, which eventually spread to Earth.

### dic\_word\_13cro\_title

Adres: `dic\_text\_word/00000826:dce0b001`

> \[BRAK PL: dic\_text\_word/00000826:dce0b001\]
> JP (źródło tłumaczenia): １３人衆
> EN (odniesienie oficjalne, NIE polski): The Extra Thirteen

### dic\_word\_13cro\_00\_0

Adres: `dic\_text\_word/00000826:dce0b002`

> \[BRAK PL: dic\_text\_word/00000826:dce0b002\]
> JP (źródło tłumaczenia): 　ギワザ・ロワウが指揮するポセイダル軍の精鋭。 ⏎ 　ＥＸ１３とも呼ばれる。 ⏎ 　それぞれが部隊を率いる指揮権を有すると同時に、ヘビーメタルのヘッドライナーとしても高い戦闘力を持つ。
> EN (odniesienie oficjalne, NIE polski): The elite soldiers of Posaydal Forces led by Giwaza Lowaw. ⏎  ⏎ They are sometimes referred to as "EX13". ⏎  ⏎ They were all granted the authority to lead their own squadrons; they are also, naturally, highly talented Heavy Metal Headliners.

### dic\_word\_13cro\_00\_1

Adres: `dic\_text\_word/00000826:dce0b003`

> \[BRAK PL: dic\_text\_word/00000826:dce0b003\]
> JP (źródło tłumaczenia): 　その多くはギワザに共鳴し、ポセイダルに反旗を翻した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Many of them joined Giwaza in his rebellion against Posaydal.

### dic\_word\_pent\_world\_title

Adres: `dic\_text\_word/00000826:dce0b004`

> \[BRAK PL: dic\_text\_word/00000826:dce0b004\]
> JP (źródło tłumaczenia): ペンタゴナ・ワールド
> EN (odniesienie oficjalne, NIE polski): Pentagona World

### dic\_word\_pent\_world\_00\_0

Adres: `dic\_text\_word/00000826:dce0b005`

> \[BRAK PL: dic\_text\_word/00000826:dce0b005\]
> JP (źródło tłumaczenia): 　二重太陽サンズと５つの惑星からなる恒星系。 ⏎ 　長い戦乱の後、オルドナ・ポセイダルによって統一されたが、各地では今も反乱活動が続き、戦火が絶えない。
> EN (odniesienie oficjalne, NIE polski): A star system consisting of two binary stars, the Sunz, and its five orbiting planets. ⏎  ⏎ Though it was unified by Oldna Posaydal following the conclusion of a long war, the flames of conflict were never truly extinguished and acts of insurrection and rebellions occur to this day.

### dic\_word\_hell\_title

Adres: `dic\_text\_word/00000826:dce0b007`

> \[BRAK PL: dic\_text\_word/00000826:dce0b007\]
> JP (źródło tłumaczenia): Ｄｒ．ヘル
> EN (odniesienie oficjalne, NIE polski): Dr. Hell

### dic\_word\_hell\_00\_0

Adres: `dic\_text\_word/00000826:dce0b008`

> \[BRAK PL: dic\_text\_word/00000826:dce0b008\]
> JP (źródło tłumaczenia): 　かつて世界征服を企て、世界を恐怖に陥れたマッドサイエンティスト。 ⏎ 　バードス島で発見した古代ミケーネの遺跡から機械獣軍団を組織するも、マジンカイザーを駆る兜甲児との戦いの果てに死亡した。
> EN (odniesienie oficjalne, NIE polski): A mad scientist who once terrorized society in his quest for world domination. ⏎  ⏎ He prepared an army of "Kikaiju", mechanical beasts he discovered in ancient Mycenaean ruins on Bardos Island, to take over the world, but was ultimately killed at the end of a long conflict by Koji Kabuto's Mazinkaiser.

### dic\_word\_thayir\_title

Adres: `dic\_text\_word/00000826:dce0b00a`

> \[BRAK PL: dic\_text\_word/00000826:dce0b00a\]
> JP (źródło tłumaczenia): タイール
> EN (odniesienie oficjalne, NIE polski): Tahir

### dic\_word\_thayir\_00\_0

Adres: `dic\_text\_word/00000826:dce0b00b`

> \[BRAK PL: dic\_text\_word/00000826:dce0b00b\]
> JP (źródło tłumaczenia): 　山岸獏の兄。 ⏎ 　新興宗教「グリーンアース教」の元教主であり、「ゲッターの意思」を理解する超能力のようなものを備えていた。 ⏎ 　１９年前のシベリア戦線で流竜馬、一文字號と共に真ゲッターロボに搭乗し、核の脅威から世界を救った。それ以降は、竜馬や號と同じく消息不明となっている。
> EN (odniesienie oficjalne, NIE polski): Baku Yamagishi's older brother. ⏎  ⏎ He was the founder and leader of the Green Earth Religion faith, and he possessed the gift of extra-sensory perception which allowed him to understand the "Will of Getter". ⏎  ⏎ 19 years ago, he piloted Shin Getter Robo alongside Ryoma Nagare and Go Ichimonji during the battle in Siberia, saving the world from a nuclear apocalypse. He went missing along with his two comrades following that incident.

### dic\_word\_em\_lelouch\_title

Adres: `dic\_text\_word/00000826:dce0b00d`

> \[BRAK PL: dic\_text\_word/00000826:dce0b00d\]
> JP (źródło tłumaczenia): 皇帝ルルーシュ
> EN (odniesienie oficjalne, NIE polski): Emperor Lelouch

### dic\_word\_em\_lelouch\_00\_0

Adres: `dic\_text\_word/00000826:dce0b00e`

> \[BRAK PL: dic\_text\_word/00000826:dce0b00e\]
> JP (źródło tłumaczenia): 　神聖ブリタニア帝国の第９９代皇帝。 ⏎ 　フルネームはルルーシュ・ヴィ・ブリタニア。 ⏎ 　暴虐の限りを尽くして世界を恐怖に陥れた事で、悪逆皇帝として知られる。 ⏎ 　黒の騎士団と兄シュナイゼルとの戦いに勝利して全権を得るが、最後は黒の騎士団のゼロによって討たれて生命を落とした。
> EN (odniesienie oficjalne, NIE polski): The 99th Emperor of the Holy Britannian Empire. ⏎  ⏎ His full name was Lelouch vi Britannia. ⏎  ⏎ He went down in history as the "Evil Emperor" who brought misery and terror to the world with his tyranny. ⏎  ⏎ He rose to power by defeating the combined forces of the Order of the Black Knights and his brother Schneizel, but in the end he was struck down by the leader of the Black Knights, Zero himself.

### dic\_word\_shirley\_title

Adres: `dic\_text\_word/00000826:dce0b010`

> \[BRAK PL: dic\_text\_word/00000826:dce0b010\]
> JP (źródło tłumaczenia): シャーリー
> EN (odniesienie oficjalne, NIE polski): Shirley

### dic\_word\_shirley\_00\_0

Adres: `dic\_text\_word/00000826:dce0b011`

> \[BRAK PL: dic\_text\_word/00000826:dce0b011\]
> JP (źródło tłumaczenia): 　ルルーシュの通っていたアッシュフォード学園の生徒。 ⏎ 　フルネームはシャーリー・フェネット。 ⏎ 　ルルーシュとは友人以上の関係であり、ルルーシュが黒の騎士団のゼロである事に気づいていながらも、彼を支える覚悟を決めていた。 ⏎ 　ゼロ・レクイエムの真実についても知っており、Ｃ．Ｃ．に秘密裏に協力をした。
> EN (odniesienie oficjalne, NIE polski): One of Lelouch's classmates at Ashford Academy. ⏎  ⏎ Her full name is Shirley Fenette. ⏎  ⏎ Feeling more than simple friendship towards Lelouch, she was ready to support him even after finding out his alternate identity as Zero, leader of the Order of the Black Knights. ⏎  ⏎ She is one of the few people who knows the truth behind the Zero Requiem, and has been secretly assisting C.C. as best she can.

### dic\_word\_charles\_title

Adres: `dic\_text\_word/00000826:dce0b013`

> \[BRAK PL: dic\_text\_word/00000826:dce0b013\]
> JP (źródło tłumaczenia): シャルル
> EN (odniesienie oficjalne, NIE polski): Charles

### dic\_word\_charles\_00\_0

Adres: `dic\_text\_word/00000826:dce0b014`

> \[BRAK PL: dic\_text\_word/00000826:dce0b014\]
> JP (źródło tłumaczenia): 　神聖ブリタニア帝国の第９８代皇帝。 ⏎ 　フルネームはシャルル・ジ・ブリタニア。 ⏎ 　ルルーシュとナナリーの実父であり、彼等の実母であり妻のマリアンヌ・ヴィ・ブリタニアと共に嘘のない世界を創るために全人類の思考を一つにする「ラグナレクの接続」を行おうとした。 ⏎ 　その試みはルルーシュによって阻止され、マリアンヌと共に人間の意識が集まる「Ｃの世界」に取り込まれて消滅した。
> EN (odniesienie oficjalne, NIE polski): The 98th Emperor of the Holy Britannian Empire. ⏎  ⏎ His full name was Charles zi Britannia. ⏎  ⏎ He was the biological father of Lelouch and Nunnally. He was working with their mother, his (fifth) wife Marianne vi Britannia to achieve the "Ragnarok Connection", the creation of a world without lies by merging together the thoughts of all of humanity. ⏎  ⏎ After Lelouch thwarted their plan, he and Marianne vanished within "C's World", the gathering place of mankind's consciousness.

### dic\_word\_c\_world\_title

Adres: `dic\_text\_word/00000826:dce0b016`

> \[BRAK PL: dic\_text\_word/00000826:dce0b016\]
> JP (źródło tłumaczenia): Ｃの世界
> EN (odniesienie oficjalne, NIE polski): C's World

### dic\_word\_c\_world\_00\_0

Adres: `dic\_text\_word/00000826:dce0b017`

> \[BRAK PL: dic\_text\_word/00000826:dce0b017\]
> JP (źródło tłumaczenia): 　人間の意識や思考、記憶が集まる空間。 ⏎ 　そこに存在する集合無意識こそが、Ｃの世界そのものとも言える。
> EN (odniesienie oficjalne, NIE polski): The place where human consciousness, thoughts, and memories gather. ⏎  ⏎ It could be said that the collective unconscious that resides in there is C's World itself.

### dic\_word\_god\_title

Adres: `dic\_text\_word/00000826:dce0b019`

> \[BRAK PL: dic\_text\_word/00000826:dce0b019\]
> JP (źródło tłumaczenia): 神
> EN (odniesienie oficjalne, NIE polski): God

### dic\_word\_god\_00\_0

Adres: `dic\_text\_word/00000826:dce0b01a`

> \[BRAK PL: dic\_text\_word/00000826:dce0b01a\]
> JP (źródło tłumaczenia): 　Ｃの世界に存在する集合無意識を指す。 ⏎ 　全ての人間の時間を超越した意識や記憶の集合体であるため、世界の全てとも言える存在。
> EN (odniesienie oficjalne, NIE polski): This refers to the collective unconscious that resides within C's World. ⏎  ⏎ As it is the aggregation of the entirety of mankind's consciousness and memories across all time, such a being is effectively the world in its entirety.

### dic\_word\_b\_knights\_title

Adres: `dic\_text\_word/00000826:dce0b01c`

> \[BRAK PL: dic\_text\_word/00000826:dce0b01c\]
> JP (źródło tłumaczenia): 黒の騎士団
> EN (odniesienie oficjalne, NIE polski): Order of the Black Knights

### dic\_word\_b\_knights\_00\_0

Adres: `dic\_text\_word/00000826:dce0b01d`

> \[BRAK PL: dic\_text\_word/00000826:dce0b01d\]
> JP (źródło tłumaczenia): 　仮面の男・ゼロが結成した組織。 ⏎ 　レジスタンスグループとして神聖ブリタニア帝国の支配に抵抗するだけでなく、正義の味方としてエリア１１における不正行為を断罪し、人々の支持を集めていった。 ⏎ 　各地のブリタニア抵抗勢力を吸収し、一大軍事組織へと成長していき、ルルーシュがブリタニア皇帝に即位した後も最後まで抵抗を続けた。 ⏎ 　皇帝ルルーシュ暗殺後は、超合集国内の軍事組織として、各地の治安維持を担当している。
> EN (odniesienie oficjalne, NIE polski): An organization created by the masked man Zero. ⏎  ⏎ Primarily a resistance group against the dominion of the Holy Britannian Empire, they also acted in the name of justice to punish criminals and villains, earning them broad support in Area Eleven. ⏎  ⏎ Over time they began to absorb global resistance groups fighting Britannian rule, and would fight to the end even after Lelouch took the Britannian throne. ⏎  ⏎ Following the assassination of Emperor Lelouch, they became a formal military organization for the new United Federation of Nations, tasked with maintaining peace across the world.

### dic\_word\_ash\_school\_title

Adres: `dic\_text\_word/00000826:dce0b01f`

> \[BRAK PL: dic\_text\_word/00000826:dce0b01f\]
> JP (źródło tłumaczenia): アッシュフォード学園
> EN (odniesienie oficjalne, NIE polski): Ashford Academy

### dic\_word\_ash\_school\_00\_0

Adres: `dic\_text\_word/00000826:dce0b020`

> \[BRAK PL: dic\_text\_word/00000826:dce0b020\]
> JP (źródło tłumaczenia): 　かつてのエリア１１に存在した学校。 ⏎ 　ブリタニア貴族のアッシュフォード家が経営している。 ⏎ 　リベラルな校風で、名誉ブリタニア人にも門戸が開かれていた。 ⏎ 　ルルーシュとスザク、カレンが通っていた学校であり、彼等にとって思い出の場所となっている。
> EN (odniesienie oficjalne, NIE polski): An academy that existed in the former Area Eleven. ⏎  ⏎ The academy was managed by the Ashfords, a noble family from Britannia. ⏎  ⏎ The academy had a distinctly liberal school atmosphere, even allowing honorary Britannian citizens to attend. ⏎  ⏎ Notably the alma mater of Lelouch, Suzaku, and Kallen, making it a very nostalgic place for them.

### dic\_word\_h\_britannia\_title

Adres: `dic\_text\_word/00000826:dd20b001`

> \[BRAK PL: dic\_text\_word/00000826:dd20b001\]
> JP (źródło tłumaczenia): 神聖ブリタニア帝国
> EN (odniesienie oficjalne, NIE polski): Holy Britannian Empire

### dic\_word\_h\_britannia\_00\_0

Adres: `dic\_text\_word/00000826:dd20b002`

> \[BRAK PL: dic\_text\_word/00000826:dd20b002\]
> JP (źródło tłumaczenia): 　旧来の貴族制度と最新の技術力からなる強大な軍事力を誇る大帝国。 ⏎ 　皇歴２０００年代に入り、第９８代皇帝シャルルは世界各地に対する武力侵攻を開始した。属領とした国は、かつての国名を名乗らせずに「エリア○○」と数字で呼称し、被征服民を「ナンバーズ」と呼んだ。 ⏎ 　その侵略や徹底した差別政策は、多数の抵抗勢力を生んだ。 ⏎ 　第９９代皇帝としてルルーシュ・ヴィ・ブリタニアが即位したが、彼の暗殺を契機に国家はブリタニア公国に再編され、超合集国に加盟した。
> EN (odniesienie oficjalne, NIE polski): An enormous empire that combined ancient traditions of nobility with cutting edge modern technology. ⏎  ⏎ In the year 2000, the 98th emperor Charles set out on a path of global military conquest. Subject nations had their name taken away upon conquest and were given a number, i.e. "Area \#\#", leading to the term "numbers" being used for citizens of these occupied territories. ⏎  ⏎ Britannia's invasions, and the discriminatory policies implemented following them, brought about many resistance movements opposing them. ⏎  ⏎ Lelouch vi Britannia was crowned as the 99th emperor, but after his assassination, the empire was reformed into the Principality of Britannia, which then became part of the United Federation of Nations.

### dic\_word\_shikhara\_title

Adres: `dic\_text\_word/00000826:dd20b004`

> \[BRAK PL: dic\_text\_word/00000826:dd20b004\]
> JP (źródło tłumaczenia): シカーラ
> EN (odniesienie oficjalne, NIE polski): Shikaara

### dic\_word\_shikhara\_00\_0

Adres: `dic\_text\_word/00000826:dd20b005`

> \[BRAK PL: dic\_text\_word/00000826:dd20b005\]
> JP (źródło tłumaczenia): 　ウルガルの言語で「狩り」を意味する。
> EN (odniesienie oficjalne, NIE polski): The Wulgaru word for "hunt".

### dic\_word\_shikhara\_00\_1

Adres: `dic\_text\_word/00000826:dd20b006`

> \[BRAK PL: dic\_text\_word/00000826:dd20b006\]
> JP (źródło tłumaczenia): 　ウルガルにとって種の存続のための遺伝子採取であると同時に習性や文化と言うべき行為となっている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ For the Wulgaru, the shikaara is both a way to harvest genes for the survival of their species and a form of culture.

### dic\_word\_lamata\_title

Adres: `dic\_text\_word/00000826:dd20b007`

> \[BRAK PL: dic\_text\_word/00000826:dd20b007\]
> JP (źródło tłumaczenia): ラマタ
> EN (odniesienie oficjalne, NIE polski): Lamata

### dic\_word\_lamata\_00\_0

Adres: `dic\_text\_word/00000826:dd20b008`

> \[BRAK PL: dic\_text\_word/00000826:dd20b008\]
> JP (źródło tłumaczenia): 　ウルガルの言語で狩りの「獲物」を意味する。 ⏎ 　単純な攻撃対象として以上の意味を持ち、自らのラマタと定めた相手には強い執着を示す。
> EN (odniesienie oficjalne, NIE polski): The Wulgaru word for "prey". ⏎  ⏎ It means more than simply a target of attack, however. Once a Wulgaru decides someone is their lamata, the Wulgaru displays a powerful, persistent fixation toward them.

### dic\_word\_urgal\_title

Adres: `dic\_text\_word/00000826:dd20b00a`

> \[BRAK PL: dic\_text\_word/00000826:dd20b00a\]
> JP (źródło tłumaczenia): ウルガル
> EN (odniesienie oficjalne, NIE polski): Wulgaru

### dic\_word\_urgal\_00\_0

Adres: `dic\_text\_word/00000826:dd20b00b`

> \[BRAK PL: dic\_text\_word/00000826:dd20b00b\]
> JP (źródło tłumaczenia): 　汎銀河統一帝国を名乗る謎の異星人。 ⏎ 　木星圏で人類と接触した事をきっかけに交戦状態に突入する。 ⏎ 　その生態、戦力規模や侵攻目的など、あらゆる面が謎に包まれている。
> EN (odniesienie oficjalne, NIE polski): Mysterious aliens calling themselves the United Pan-Galactic Empire Wulgaru. ⏎  ⏎ After making contact with mankind in the Jupiter Sphere, the Wulgaru began skirmishing with humans. ⏎  ⏎ Everything about them is shrouded in mystery; their true forms, the extent of their military capacity, and even their objectives for their invasion.

### dic\_word\_urgal\_00\_1

Adres: `dic\_text\_word/00000826:dd20b00c`

> \[BRAK PL: dic\_text\_word/00000826:dd20b00c\]
> JP (źródło tłumaczenia): 　後にウルガルから亡命した皇女テオーリアによって、彼らの侵略の目的が種族存続のための優良な遺伝子の採取にある事が明かされた。
> EN (odniesienie oficjalne, NIE polski):  ⏎ Later, after deserting the Wulgaru, Princess Teoria reveals that their invasion's aim is to harvest superior genes to ensure the survival of their race.

### dic\_word\_garukier\_title

Adres: `dic\_text\_word/00000826:dd20b00d`

> \[BRAK PL: dic\_text\_word/00000826:dd20b00d\]
> JP (źródło tłumaczenia): ガルキエ
> EN (odniesienie oficjalne, NIE polski): Galkie

### dic\_word\_garukier\_00\_0

Adres: `dic\_text\_word/00000826:dd20b00e`

> \[BRAK PL: dic\_text\_word/00000826:dd20b00e\]
> JP (źródło tłumaczenia): 　ウルガルの皇帝。 ⏎ 　ジアートの異母兄にあたる。 ⏎ 　前皇帝の父を暗殺して実権を握り、レガトゥス（軍団長）を取りまとめる。 ⏎ 　３００年に一度の宣託を受け、地球への侵攻を決定した。
> EN (odniesienie oficjalne, NIE polski): Emperor of the Wulgaru and Jiart's half-brother. ⏎  ⏎ He rose to power after assassinating his father, the former emperor, and now leads the Legatus, the Wulgaru army commanders. ⏎  ⏎ He began his invasion of Earth after receiving his first premonition in 300 years.

### dic\_word\_ceres\_w\_title

Adres: `dic\_text\_word/00000826:dd20b010`

> \[BRAK PL: dic\_text\_word/00000826:dd20b010\]
> JP (źródło tłumaczenia): ケレス大戦
> EN (odniesienie oficjalne, NIE polski): The Battle of Ceres

### dic\_word\_ceres\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd20b011`

> \[BRAK PL: dic\_text\_word/00000826:dd20b011\]
> JP (źródło tłumaczenia): 　準惑星ケレス周辺で展開されたＧＤＦの一大反攻作戦。 ⏎ 「オペレーション・サンダーボルト」の名で呼ばれ、コミネ参謀次長が総指揮を執った。 ⏎ 　作戦開始前にウルガルの奇襲を受けた事で混戦となり、ＧＤＦの被害は壊滅的なものであった。 ⏎ 　戦闘はウルガルの退却で終了したが、事実上はＧＤＦの敗北と言える。しかし、ＧＤＦ上層部の思惑もあり、世間では地球側の大勝利とその立役者としてチームラビッツの活躍が大々的に報じられた。
> EN (odniesienie oficjalne, NIE polski): A major counteroffensive by the GDF deployed near the dwarf planet Ceres, referred to as Operation Thunderbolt and led by Vice-Chief Komine. ⏎  ⏎ A Wulgaru surprise attack before the operation could begin threw all the plans into chaos, and the GDF took grievous losses in the resultant skirmishing. ⏎  ⏎ Though the battle ended with a Wulgaru retreat, it was, for all intents and purposes, a defeat for the GDF. However, GDF leadership told the public that Earth had won a crucial victory and held up Team Rabbits as key contributors.

### dic\_word\_h\_earth\_title

Adres: `dic\_text\_word/00000826:dd20b013`

> \[BRAK PL: dic\_text\_word/00000826:dd20b013\]
> JP (źródło tłumaczenia): 地球の歴史
> EN (odniesienie oficjalne, NIE polski): The History of Earth

### dic\_word\_h\_earth\_00\_0

Adres: `dic\_text\_word/00000826:dd20b014`

> \[BRAK PL: dic\_text\_word/00000826:dd20b014\]
> JP (źródło tłumaczenia): 　新宇宙正暦（New Universal Correct-Century：NUCC)制定後の約６０年間の激動の時代を指す。 ⏎ 　新宇宙正暦０００年 ⏎ 　　・人類初の異星種族との戦いである新銀河大戦勃発 ⏎ 　　・新銀河大戦終結後、新統合政府樹立と新宇宙正暦制定 ⏎ 　新宇宙正暦００３年 ⏎ 　　・人類播種計画が開始され、地球人類は銀河に進出 ⏎ 　　・地球圏の統一政体として地球連邦政府樹立 ⏎ 　新宇宙正暦００６年 ⏎ 　　・地球連邦内の政権代理戦争としてガンダムファイト開始 ⏎ 　新宇宙正暦０２３年 ⏎ 　　・恐竜帝国・百鬼帝国との戦い ⏎ 　新宇宙正暦０３０年代 ⏎ 　　・銀河に進出した人類と異星種族との戦いが地球にも影響 ⏎ 　新宇宙正暦０３８年 ⏎ 　　・恐竜帝国との戦い（シベリア戦線） ⏎ 　新宇宙正暦０４８年 ⏎ 　　・ジオン公国の独立宣言からの一年戦争 ⏎ 　　　以降、地球居住者と宇宙移民者の対立が続く ⏎ 　新宇宙正暦０５０年 ⏎ 　　・ウルガルとの初戦闘（非公式） ⏎ 　新宇宙正暦０５５年 ⏎ 　　・コーディネイターとナチュラルの対立による第一次プラント大戦 ⏎ 　新宇宙正暦０５６年 ⏎ 　　・ウルガルとの初戦闘（公式） ⏎ 　新宇宙正暦０５７年 ⏎ 　　・革命戦争 ⏎ 　　　同時に様々な戦いが勃発し、地球圏は大きな混乱に包まれる ⏎ 　新宇宙正暦０５８年 ⏎ 　　・新地球連邦政府樹立
> EN (odniesienie oficjalne, NIE polski): The history of Earth's last sixty or so years is an era of upheaval taking place in what is known as the New Universal Calendar, or NUC. ⏎  ⏎ NUC 000 ⏎ ・Humanity fights an alien race for the first time in the New Galactic War ⏎ ・After the war ends, the New United Nations Government is established, and the New Universal Calendar is enacted ⏎  ⏎ NUC 003 ⏎ ・The Humanity Seeding Project begins as humanity forges into the wider galaxy ⏎ ・The Earth Federation is established to govern the entire Earth Sphere ⏎  ⏎ NUC 006 ⏎ ・The Gundam Fight begins, serving as a proxy war for member nations to gain political authority ⏎  ⏎ NUC 023 ⏎ ・Conflicts against the Dinosaur Empire and the Hyakki Empire ⏎  ⏎ NUC 030 ⏎ ・War between galactic humans and extraterrestrials begins to affect Earth ⏎  ⏎ NUC 038 ⏎ ・Conflict against the Dinosaur Empire (the battle in Siberia) ⏎  ⏎ NUC 048 ⏎ ・The Principality of Zeon declares independence, sparking the One Year War. Hostilities between residents of Earth and space immigrants continue to the present day ⏎  ⏎ NUC 050 ⏎ ・First combat with the Wulgaru (unofficial) ⏎  ⏎ NUC 055 ⏎ ・The First PLANT War occurs between Coordinators and Naturals ⏎  ⏎ NUC 056 ⏎ ・First combat with the Wulgaru (official) ⏎  ⏎ NUC 057 ⏎ ・The Revolutionary War occurs. Many conflicts break out simultaneously and the Earth is engulfed in major chaos ⏎  ⏎ NUC 058 ⏎ ・The New Earth Federation is established

### dic\_word\_galactic\_w\_title

Adres: `dic\_text\_word/00000826:dd20b016`

> \[BRAK PL: dic\_text\_word/00000826:dd20b016\]
> JP (źródło tłumaczenia): 新銀河大戦
> EN (odniesienie oficjalne, NIE polski): New Galactic War

### dic\_word\_galactic\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd20b017`

> \[BRAK PL: dic\_text\_word/00000826:dd20b017\]
> JP (źródło tłumaczenia): 　地球人類が遭遇した初の異星種族との星間戦争。 ⏎ 　巨人型異星人ゼントラーディとの接触に端を発したこの戦いは、一気に拡大し、最終的には複数の異星人間の戦争に地球が巻き込まれた形となった。 ⏎ 　この戦いで地球は壊滅的な打撃を受け、地球人類は存続が危ぶまれるレベルまで追い込まれたが、異星種族との講和によって大戦は終結し、人類は絶滅を免れた。 ⏎ 　地球人類は講和した異星種族と共に新たな政体・新統合政府を樹立し、短期間で復興を成し遂げる。 ⏎ 　この新銀河大戦は地球人類のあり方を大きく変えたものとして新宇宙正暦が制定され、地球人類は新たな時代を歩んでいく事となった。
> EN (odniesienie oficjalne, NIE polski): An interstellar war against the first alien race humanity encountered. ⏎  ⏎ This war, which broke out after first contact with the Zentradi, a race of giants, spread very quickly. Ultimately, Earth was embroiled in a war between several alien races. ⏎  ⏎ The conflict dealt a critical blow to the planet, driving humanity to the brink of destruction. However, it ended with the signing of a peace treaty, and humankind avoided extinction. ⏎  ⏎ Humanity formed a new government, the New United Nations Government, in conjunction with the alien races they made peace with, and reconstruction efforts were swift. ⏎  ⏎ Because the New Galactic War changed every facet of human life, the New Universal Calendar was adopted and humanity stepped forward into a new era.

### dic\_word\_revol\_w\_title

Adres: `dic\_text\_word/00000826:dd20b019`

> \[BRAK PL: dic\_text\_word/00000826:dd20b019\]
> JP (źródło tłumaczenia): 革命戦争
> EN (odniesienie oficjalne, NIE polski): Revolutionary War

### dic\_word\_revol\_w\_00\_0

Adres: `dic\_text\_word/00000826:dd60b000`

> \[BRAK PL: dic\_text\_word/00000826:dd60b000\]
> JP (źródło tłumaczenia): 　新宇宙正暦０５８年に勃発した大戦。 ⏎ 　地球居住者アースノイドと宇宙居住者スペースノイド、ナチュラルとコーディネイター、古い権力者と新たな力、といった複数の対立構造からの戦いが同時に勃発し、新銀河大戦以来の大規模な戦争となった。 ⏎ 　加えて、異世界バイストン・ウェルからの来訪者の引き起こした戦い、デビルガンダムの暴走、Ｄｒ．ヘルによる大規模テロなども同時発生し、一時は地球人類の存続も危ぶまれた。 ⏎ 　激戦の中、各陣営の指導者であったジャミトフ・ハイマン、パプテマス・シロッコ、ギルバート・デュランダル、ハマーン・カーン、ミリアルド・ピースクラフト、シャルル・ジ・ブリタニア、シュナイゼル・エル・ブリタニア、トレーズ・クシュリナーダが倒れ、最終的には地球側の指導者としてルルーシュ・ヴィ・ブリタニア、宇宙側の指導者としてシャア・アズナブルが残った。 ⏎ 　両者による最終決戦が迫る中、皇帝ルルーシュが衆人環視の状況で暗殺され、戦いは終結した。これは戦争を望む指導者の死によるものだけでなく、悲惨な戦いを目の当たりにしてきた事で多くの人々が憎しみを捨てて平和を望んだ結果とされている。 ⏎ 　人々の意識を変革させたという事で、この一連の戦いは革命戦争（レヴォル・ウォー）の名で呼ばれる事となり、世界は再編されて新地球連邦政府が誕生した。
> EN (odniesienie oficjalne, NIE polski): A war that broke out in NUC 058. ⏎  ⏎ Several conflicts arose at the same time between various factions—between the Earthnoids living on earth and the Spacenoids who immigrated to space, the Naturals and the Coordinators, and the old authorities and new powers. These hostilities escalated into the biggest conflict since the New Galactic War. ⏎  ⏎ At the same time, visitors from another world called Byston Well caused more warfare, the Dark Gundam went berserk, and Dr. Hell enacted his wide-scale terrorism activities. For a while, the very existence of mankind was called into question. ⏎  ⏎ During the brutal warfare, the leaders of each faction—Jamitov Hymem, Paptimus Scirocco, Gilbert Dullindal, Haman Karn, Milliardo Peacecraft, Charles zi Britannia, Schneizel el Britannia, and Treize Khushrenada—all fell. Ultimately, this left Lelouch vi Britannia in control of Earth and Char Aznable in control of space. ⏎  ⏎ With one final conflict between the two approaching, Emperor Lelouch was assassinated in full view of the public, bringing the war to an end. It is said that this end came about not through the deaths of the leaders who desired war, but rather through the people, who had witnessed horrible tragedies and had thrown away their hatred out of a desire for peace. ⏎  ⏎ With the mindset of the people having changed so drastically, the string of conflicts came to be known as the Revolutionary War. As the New Earth Federation was formed, the world entered a new chapter.

### dic\_word\_nef\_title

Adres: `dic\_text\_word/00000826:dd60b002`

> \[BRAK PL: dic\_text\_word/00000826:dd60b002\]
> JP (źródło tłumaczenia): 新地球連邦
> EN (odniesienie oficjalne, NIE polski): New Earth Federation

### dic\_word\_nef\_00\_0

Adres: `dic\_text\_word/00000826:dd60b003`

> \[BRAK PL: dic\_text\_word/00000826:dd60b003\]
> JP (źródło tłumaczenia): 　革命戦争後に樹立した地球人類の意思統一機関。 ⏎ 　地球連邦政府を母体としているが、地球居住者と宇宙居住者の融和、平和的な手段による問題解決を掲げている。 ⏎ 　地球連邦の集権機構の抱えていた問題の反省から、第二行政単位と呼ばれる旧国家と各スペースコロニーに多くの権限を与えている事が特徴。しかし、それによって新地球連邦政府の権力は制限され、革命戦争によって変革を迎えた世界において指導者的な役割を果たせるかについては疑問を呈されている。
> EN (odniesienie oficjalne, NIE polski): An organization representing the will of humankind, established in the aftermath of the Revolutionary War. ⏎  ⏎ While the New Earth Federation is a descendant of the Earth Federation government, it advocates for harmony between Earth residents and space immigrants and seeks to resolve issues with peaceful methods. ⏎  ⏎ Learning from the problems caused by the Earth Federation's centralized power structure, the NEF is unique in that it granted authority to many groups, calling them second-level political organizations, such as former nations and space colonies. However, doing so limited the NEF's authority, and concerns have been raised over how well those in leadership roles can carry out their duties now that the world has been reformed through the Revolutionary War.

### dic\_word\_oboro\_title

Adres: `dic\_text\_word/00000826:dd60b005`

> \[BRAK PL: dic\_text\_word/00000826:dd60b005\]
> JP (źródło tłumaczenia): 朧
> EN (odniesienie oficjalne, NIE polski): Haze

### dic\_word\_oboro\_00\_0

Adres: `dic\_text\_word/00000826:dd60b006`

> \[BRAK PL: dic\_text\_word/00000826:dd60b006\]
> JP (źródło tłumaczenia): 　ＮＩＮＪＡによる戦闘集団「特戦隠密」の一つ。 ⏎ 　その源流は、日本の戦国時代に活躍した忍者の流派にある。 ⏎ 　事情を知る人間達にとっては最強の特戦隠密として知られているが、規模や構成員、本拠地など、全ては謎に包まれている。 ⏎ 　諜報や破壊活動だけでなく、ＮＩＮＪＡ専用の機動兵器「機動忍鎧」を用いての戦闘も引き受ける。
> EN (odniesienie oficjalne, NIE polski): A unit of the Special Stealth Forces, a militant group of NINJAs. ⏎  ⏎ They originate with the various schools of ninjas active during Japan's Warring States period. ⏎  ⏎ Only a select few know them as the most powerful special stealth forces unit, and even then, their scope, membership, and headquarters are all shrouded in mystery. ⏎  ⏎ Haze not only engages in espionage and sabotage, but also takes on combat jobs using unique NINJA mobile weapons called Mobile Armored Ninjas.

### dic\_word\_ninja\_title

Adres: `dic\_text\_word/00000826:dd60b008`

> \[BRAK PL: dic\_text\_word/00000826:dd60b008\]
> JP (źródło tłumaczenia): ＮＩＮＪＡ
> EN (odniesienie oficjalne, NIE polski): NINJA

### dic\_word\_ninja\_00\_0

Adres: `dic\_text\_word/00000826:dd60b009`

> \[BRAK PL: dic\_text\_word/00000826:dd60b009\]
> JP (źródło tłumaczenia): 　日本古来の忍者を源流とする特殊戦闘員。 ⏎ 　その名は「New Infinity Neuron - Japanese Assassin」から取られており、常人では使う事の出来ない神経回路を鍛錬によって覚醒させ、瞬間的ではあるが、人間の持つ潜在能力を引き出す事を可能としている。 ⏎ 　この能力についての研究は長い歴史を持ち、独自の鍛錬法を持つＮＩＮＪＡの集団「特戦隠密」は複数存在している。彼等は政府や各種機関に雇われ、エージェントとして様々な活動に従事する。
> EN (odniesienie oficjalne, NIE polski): A special forces operative originating in the ancient Japanese ninja tradition. ⏎  ⏎ Their name is taken from "New Infinity Neuron Japanese Assassin". Through training, they learn to use neural circuits no normal person can, which allow them to bring out latent human abilities, albeit only momentarily. ⏎  ⏎ The research behind these abilities has a long history, and there are several NINJA Special Stealth Forces units, each with its own training methods. They take on jobs from governments and various other organizations, engaging in a variety of activities as agents.

### dic\_word\_ninja\_armor\_title

Adres: `dic\_text\_word/00000826:dd60b00b`

> \[BRAK PL: dic\_text\_word/00000826:dd60b00b\]
> JP (źródło tłumaczenia): 機動忍鎧
> EN (odniesienie oficjalne, NIE polski): Mobile Armored Ninja

### dic\_word\_ninja\_armor\_00\_0

Adres: `dic\_text\_word/00000826:dd60b00c`

> \[BRAK PL: dic\_text\_word/00000826:dd60b00c\]
> JP (źródło tłumaczenia): 　ＮＩＮＪＡ専用の機動兵器。 ⏎ 　柔軟なフレームと人工筋肉を使った駆動システムにより、他に類を見ない高い運動性能を誇る。操縦は搭乗者の身体の動きと各種操作の組み合わせによるセミ・スレイブシステムを採用しており、非常にデリケートな仕上がりとなっている。加えて、機体と搭乗者は神経接続されているため、ダメージのフィードバックもあり、ＮＩＮＪＡとして訓練を受けた人間以外では歩かせる事さえ難しい。 ⏎ 　基本的には隠密偵察、あるいは強行偵察を任務とするため、戦闘力よりも機動性を重視している。
> EN (odniesienie oficjalne, NIE polski): A type of mobile weapon used by NINJAs. ⏎  ⏎ These weapons boast unprecedented mobility thanks to propulsion systems that use flexible frames and artificial muscles. They adopt a semi-capture control system, which combines the pilot's own physical movements with the various onboard controls, allowing for extremely delicate and subtle movements. Furthermore, because the machine and pilot are neurally linked, the pilot experiences damage feedback. Even making one walk would be difficult for anyone who hasn't received training as a NINJA. ⏎  ⏎ Because they are generally used for recon missions—both covert and overt—mobility is valued over combat potential.

### dic\_word\_mont\_title

Adres: `dic\_text\_word/00000826:dd60b00e`

> \[BRAK PL: dic\_text\_word/00000826:dd60b00e\]
> JP (źródło tłumaczenia): モーント
> EN (odniesienie oficjalne, NIE polski): Mond

### dic\_word\_mont\_00\_0

Adres: `dic\_text\_word/00000826:dd60b00f`

> \[BRAK PL: dic\_text\_word/00000826:dd60b00f\]
> JP (źródło tłumaczenia): 　特戦隠密・朧の隊員が使用する機動忍鎧。 ⏎ 　開発には八神テツロウも関係しており、他組織の使う機動忍鎧よりも操縦者との一体感が重視されている。それは同時に操縦者に強い負担を強いる事を意味しており、関係者からは「モーントが強いのではなく、モーントを使いこなせる朧が強い」と評価されている。
> EN (odniesienie oficjalne, NIE polski): A Mobile Armored Ninja used by members of the Special Stealth Forces group Haze. ⏎  ⏎ Tetsuro Yagami was involved in its development, which emphasized the machine's unity with the pilot even more than the Mobile Armored Ninjas used by other groups. This also means it places a very heavy burden on its pilot, and some in the know claim that it's not the Mond that's powerful, but the members of Haze that are capable of wielding it.

### dic\_word\_ninja\_fang\_title

Adres: `dic\_text\_word/00000826:dd60b011`

> \[BRAK PL: dic\_text\_word/00000826:dd60b011\]
> JP (źródło tłumaczenia): 忍牙
> EN (odniesienie oficjalne, NIE polski): Ninja Fangs

### dic\_word\_ninja\_fang\_00\_0

Adres: `dic\_text\_word/00000826:dd60b012`

> \[BRAK PL: dic\_text\_word/00000826:dd60b012\]
> JP (źródło tłumaczenia): 　ＮＩＮＪＡが使用する体術以外の技。 ⏎ 　一般的には「忍術」と呼ばれる効果を指す事が多い。 ⏎ 　化学物質や特殊な忍具による雷撃や火炎といった攻撃手段だけでなく、スタングレネード的な効果や集団幻覚を発生させる忍牙もある。 ⏎ 　小型のバッテリーなどをエネルギー源とする事が多いが、特戦隠密・朧の場合、忍牙の発動は他組織とは別の手段を用いているとされている。
> EN (odniesienie oficjalne, NIE polski): Any technique outside the martial arts used by NINJAs. ⏎  ⏎ Most people refer to their effects as "ninjutsu". ⏎  ⏎ Ninja Fangs include not only means of attacking, such as lightning strikes and flames created by chemical substances or special ninja tools, but also indirect techniques, like ones that produce stun grenade-like effects or cause collective hallucinations. ⏎  ⏎ Many of them utilize small batteries as a power source, but it's said that the Special Stealth Forces unit Haze has a different means of activating Ninja Fangs than other groups.

### dic\_word\_ninja\_tool\_title

Adres: `dic\_text\_word/00000826:dd60b014`

> \[BRAK PL: dic\_text\_word/00000826:dd60b014\]
> JP (źródło tłumaczenia): 忍具
> EN (odniesienie oficjalne, NIE polski): Ninja Tools

### dic\_word\_ninja\_tool\_00\_0

Adres: `dic\_text\_word/00000826:dd60b015`

> \[BRAK PL: dic\_text\_word/00000826:dd60b015\]
> JP (źródło tłumaczenia): 　ＮＩＮＪＡが使用する器具・道具。 ⏎ 　武装に加え、忍牙を発動させるための機材・素材も含む。 ⏎ 　幾つかはＮＩＮＪＡでなくても使用できるものであるため、ＮＩＮＪＡ発の忍具が普及した例もある。
> EN (odniesienie oficjalne, NIE polski): A tool or implement used by NINJAs. ⏎  ⏎ This includes both armaments as well as devices and materials for activating Ninja Fangs. ⏎  ⏎ Several can be used even by non-NINJAs, so certain ninja tools originating with NINJA have become popularized.

### dic\_word\_val\_x\_title

Adres: `dic\_text\_word/00000826:dd60b017`

> \[BRAK PL: dic\_text\_word/00000826:dd60b017\]
> JP (źródło tłumaczenia): ＶＡＬ－Ｘ
> EN (odniesienie oficjalne, NIE polski): VAL-X

### dic\_word\_val\_x\_00\_0

Adres: `dic\_text\_word/00000826:dd60b018`

> \[BRAK PL: dic\_text\_word/00000826:dd60b018\]
> JP (źródło tłumaczenia): 　革命戦争後に活動を開始したテロ組織。 ⏎ 　その名は「Victory・Anarchy・Liberation - X」から取られているとされているが、組織としての主義や主張はあいまいであり、一部ではテロリズムではなく社会に不満を持つ者達による暴力行動と認識されている。 ⏎ 　革命戦争後に放出された兵器を無人機として使用しており、その戦力には何らかの後ろ盾があると考えられている。
> EN (odniesienie oficjalne, NIE polski): A terrorist organization that first became active during the Revolutionary War. ⏎  ⏎ The name is said to be taken from "Victory, Anarchy, Liberation X", but the actual doctrine and claims of the group are vague, which has fostered a perception of them as violent rioters dissatisfied with the status quo rather than terrorists. ⏎  ⏎ They retrofit weapons left over from the Revolutionary War for use as unmanned drones, and a backer of some sort seems to be supporting their combat forces.

### dic\_word\_heaven\_w\_title

Adres: `dic\_text\_word/00000826:dda0b000`

> \[BRAK PL: dic\_text\_word/00000826:dda0b000\]
> JP (źródło tłumaczenia): 天闘士
> EN (odniesienie oficjalne, NIE polski): Celestial Warriors

### dic\_word\_heaven\_w\_00\_0

Adres: `dic\_text\_word/00000826:dda0b001`

> \[BRAK PL: dic\_text\_word/00000826:dda0b001\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの一般兵士。 ⏎ 　戦闘に関する能力を司る「生存戦略遺伝子」が発達した者達で構成されており、地球人類と比較して、あらゆる面において高い戦闘力を持つ。
> EN (odniesienie oficjalne, NIE polski): The regular soldiers of the Pan-Stellar Empire Ra Val. ⏎  ⏎ They are comprised of those whose survival strategy genes have developed for battle. Compared to humans, they possess higher combat capabilities in all areas.

### dic\_word\_indigo\_c\_title

Adres: `dic\_text\_word/00000826:dda0b003`

> \[BRAK PL: dic\_text\_word/00000826:dda0b003\]
> JP (źródło tłumaczenia): インディゴ・チェイサー
> EN (odniesienie oficjalne, NIE polski): Indigo Chasers

### dic\_word\_indigo\_c\_00\_0

Adres: `dic\_text\_word/00000826:dda0b004`

> \[BRAK PL: dic\_text\_word/00000826:dda0b004\]
> JP (źródło tłumaczenia): 　地球連邦軍第３１独立部隊の愛称。 ⏎ 　「ＩＣ部隊」とも呼ばれる。 ⏎ 　主に地球圏外縁部で外宇宙からの敵対勢力の調査・迎撃を担当しており、害虫を寄せ付けない藍（インディゴ）をイメージカラーとしていた。 ⏎ 　革命戦争の最中、遭遇したアンノウンにより部隊は壊滅し、生き残ったメンバーも最終的には軍を退役する事となった。
> EN (odniesienie oficjalne, NIE polski): The nickname for the Earth Federation Forces 31st Autonomous Corps. Also called the IC Corps. ⏎  ⏎ The 31st's mission was the investigation and interception of hostile forces from outer space near the fringes of the Earth Sphere. They represent themselves with the color indigo, from the dye that was once thought to repel bugs from paper. ⏎  ⏎ During the Revolutionary War, the corps was wiped out by unknowns, with the surviving members ultimately resigning from the military.

### dic\_word\_divine\_title

Adres: `dic\_text\_word/00000826:dda0b006`

> \[BRAK PL: dic\_text\_word/00000826:dda0b006\]
> JP (źródło tłumaczenia): 神束
> EN (odniesienie oficjalne, NIE polski): Gracetufts

### dic\_word\_divine\_00\_0

Adres: `dic\_text\_word/00000826:dda0b007`

> \[BRAK PL: dic\_text\_word/00000826:dda0b007\]
> JP (źródło tłumaczenia): 　汎星間帝国ラー・ヴァルの民の証。 ⏎ 　戦闘に関する能力を司る「生存戦略遺伝子」の発露によって変色した前髪を指す。感情の高まりによって、この部分はさらに発光する。
> EN (odniesienie oficjalne, NIE polski): Proof that one is a citizen of the Pan-Stellar Empire Ra Val.  ⏎  ⏎ The term refers to a Ra Valian's bangs, which change color due to the expression of their survival strategy genes, which govern their combat-related abilities.  ⏎  ⏎ These bangs can also glow if the person's emotions are intense enough.

### dic\_word\_aad\_ch\_title

Adres: `dic\_text\_word/00000826:dda0b009`

> \[BRAK PL: dic\_text\_word/00000826:dda0b009\]
> JP (źródło tłumaczenia): ＡＡＤチャンネル
> EN (odniesienie oficjalne, NIE polski): AAD Channel

### dic\_word\_aad\_ch\_00\_0

Adres: `dic\_text\_word/00000826:dda0b00a`

> \[BRAK PL: dic\_text\_word/00000826:dda0b00a\]
> JP (źródło tłumaczenia): 　エーアデントの公共放送局。 ⏎ 　政府からのお知らせの他に独自の娯楽番組も放送しており、人気が高い。 ⏎ 　将来的には全世界展開も可能なコンテンツの作成を目標としている。
> EN (odniesienie oficjalne, NIE polski): The A. Advent's public broadcasting station. ⏎  ⏎ It is highly popular, airing both government announcements and independent entertainment programs. ⏎  ⏎ Its goal for the future is to create content they can roll out to the entire world.

### dic\_word\_astccl\_title

Adres: `dic\_text\_word/006b53c9:0ae0b000`

> \[BRAK PL: dic\_text\_word/006b53c9:0ae0b000\]
> JP (źródło tłumaczenia): アスティカシア高等専門学園
> EN (odniesienie oficjalne, NIE polski): Asticassia School of Technology

### dic\_word\_astccl\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b000`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b000\]
> JP (źródło tłumaczenia): 　モビルスーツ産業最大手のベネリットグループが運営する高等教育機関。 ⏎ 　独立したフロント（宇宙空間に浮かぶ人工居住施設）であり、生徒はそこで暮らしている。 ⏎ 　パイロット科、メカニック科、経営戦略科の３つの専科があり、入学条件としてベネリットグループ傘下企業の推薦が必要とされる。 ⏎ 　学内には決闘委員会と呼ばれる組織が存在しており、生徒間の問題解決の手段である「決闘」を取り仕切っている。
> EN (odniesienie oficjalne, NIE polski): A secondary education facility run by the Benerit Group, a major Mobile Suit manufacturing conglomerate. ⏎  ⏎ It operates as an independent Front (a spaceborne, fully artificial residential facility) that houses its students aboard. ⏎  ⏎ It's divided into three departments: piloting, mechanical, and management strategy. ⏎ The student body includes a Dueling Committee which oversees the duels by which students resolve problems between them.

### dic\_word\_pamet\_title

Adres: `dic\_text\_word/006b53c9:0ba0b002`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b002\]
> JP (źródło tłumaczenia): パーメット
> EN (odniesienie oficjalne, NIE polski): Permet

### dic\_word\_pamet\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b003`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b003\]
> JP (źródło tłumaczenia): 　太陽系内の各所から採掘される鉱物に含まれる元素。 ⏎ 　個々のパーメット間で情報を共有する性質を利用して様々な技術が開発され、現在の世界の根幹を支えている。
> EN (odniesienie oficjalne, NIE polski): A substance found in ore mined around the solar system. ⏎  ⏎ Two samples of Permet can be used to transfer information. This has been used as the basis for all kinds of technology, making it key to modern life.

### dic\_word\_gundarm\_title

Adres: `dic\_text\_word/006b53c9:0ba0b005`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b005\]
> JP (źródło tłumaczenia): GUND-ARM
> EN (odniesienie oficjalne, NIE polski): GUND-ARM

### dic\_word\_gundarm\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b006`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b006\]
> JP (źródło tłumaczenia): 　パーメットを利用した身体機能拡張技術「GUND」を軍事転用したシステム「GUNDフォーマット」を搭載したモビルスーツの総称。 ⏎ 　より高度な機体制御が可能になった事により、既存の機体を凌駕する性能を発揮したが、搭乗者の身体への悪影響によって人道に反する兵器とされ、その開発ならびに運用は禁止される事となった。
> EN (odniesienie oficjalne, NIE polski): The name used to describe a Mobile Suit that incorporates the GUND Format, a system that repurposes the Permet-based physical augmentation technology GUND for military use. ⏎  ⏎ The improved control precision allows these MS to outperform others by leaps and bounds, but it puts a strain on pilots using it. This caused opposition to its use, ending in all development and deployment being forbidden. 

### dic\_word\_detastm\_title

Adres: `dic\_text\_word/006b53c9:0ba0b008`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b008\]
> JP (źródło tłumaczenia): データストーム
> EN (odniesienie oficjalne, NIE polski): Data Storm

### dic\_word\_detastm\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b009`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b009\]
> JP (źródło tłumaczenia): 　「GUNDフォーマット」を介したMSの操縦の際に発生する弊害。 ⏎ 　パイロットと機体との間で膨大な情報のやりとりが行われ、パイロットへフィードバックされることで発生する。 ⏎ 　その負荷はパイロットの身体に様々な症状として現れ、死に至るケースもある。
> EN (odniesienie oficjalne, NIE polski): A detrimental phenomenon that occurs when piloting an MS using the GUND Format. ⏎  ⏎ The information exchange between pilot and MS spirals out of control and feeds back into the pilot's side. The resulting strain causes a slew of damaging side-effects to the pilot's body and can even result in death.

### dic\_word\_vanadis\_title

Adres: `dic\_text\_word/006b53c9:0ba0b00b`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b00b\]
> JP (źródło tłumaczenia): ヴァナディース
> EN (odniesienie oficjalne, NIE polski): Vanadis

### dic\_word\_vanadis\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b00c`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b00c\]
> JP (źródło tłumaczenia): 　かつて「GUND」を研究していた機関。 ⏎ 　当初は宇宙環境における身体の補助の研究を目的としていたが、資金難による研究凍結を回避するためモビルスーツ製造企業のオックス・アース社から援助を受けたことで、その技術を軍事転用することとなった。 ⏎ 　それを危険視するモビルスーツ開発評議会の強制執行により、多数の犠牲者と共に機関は制圧された。
> EN (odniesienie oficjalne, NIE polski): An organization that used to research GUND. ⏎  ⏎ They were originally founded to try to help human bodies become suited to space. However, they were forced to accept assistance from the Mobile Suit manufacturer Ochs Earth, ultimately leading to their technology being turned to military use. ⏎ In turn, its perceived danger led to the formation of the Mobile Suit Development Council, and the organization was shut down with considerable loss of life.

### dic\_word\_dmncs\_title

Adres: `dic\_text\_word/006b53c9:0ba0b00e`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b00e\]
> JP (źródło tłumaczenia): ドミニコス
> EN (odniesienie oficjalne, NIE polski): Dominicus

### dic\_word\_dmncs\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b00f`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b00f\]
> JP (źródło tłumaczenia): 　元は、モビルスーツ開発評議会直轄の特殊部隊。 ⏎ 　現在では、モビルスーツ開発の秩序と倫理を守る事を目的とする監査組織カテドラルの管理下に置かれている。 ⏎ 　ヴァナディース事変で大きな戦果を挙げたケナンジ・アベリーが司令を務める。
> EN (odniesienie oficjalne, NIE polski): A special forces team originally reporting directly to the Mobile Suit Development Council. ⏎  ⏎ They now operate under the auditing organization Cathedra, which maintains order and principles with respect to Mobile Suit development. ⏎  ⏎ They are commanded by Kenanji Avery, a major ace of the Vanadis Incident.

### dic\_word\_zentradi\_title

Adres: `dic\_text\_word/006b53c9:0ba0b011`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b011\]
> JP (źródło tłumaczenia): ゼントラーディ
> EN (odniesienie oficjalne, NIE polski): Zentradi

### dic\_word\_zentradi\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b012`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b012\]
> JP (źródło tłumaczenia): 　遙か古代に高度な文明と科学技術を持っていた星間種族プロトカルチャーによって生み出された巨人型生物兵器。 ⏎ 　１０メートルを超す巨躯と高い戦闘力、生存能力を持つが、戦闘以外の文化的な活動とは一切無縁であった。 ⏎ 　プロトカルチャーが滅んだ後も製造時の目的のまま、幾世代にも渡って戦いを続けてきたが、第一次星間大戦で地球人類に接触した一部のゼントラーディが文化に目覚めた事から、他種族との交流を始める。 ⏎ 　マイクローン化により地球人類と同サイズとなる事も選択でき、他種族との星間結婚も実現した。
> EN (odniesienie oficjalne, NIE polski): A species of enormous humanoids created by the galaxy-spanning Protoculture's advanced technology. ⏎  ⏎ At over ten meters in height, they possess tremendous combat and survival abilities, but independently possess no cultural drives of their own. ⏎  ⏎ After the Protoculture came to an end, they followed their original design directives and continued to fight. However, their encounter with humanity during Space War 1 enabled a portion of the Zentradi to open up to their long-buried desire for culture, and they began to pursue peaceful interactions with other intelligent life. ⏎  ⏎ They can change size freely via a process called Miclonization, which renders them the same size as a standard human, and there have even been cases of intermarrying with other Protoculture-derived species.

### dic\_word\_ulri\_fleet\_title

Adres: `dic\_text\_word/006b53c9:0ba0b014`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b014\]
> JP (źródło tłumaczenia): 超長距離移民船団
> EN (odniesienie oficjalne, NIE polski): Super Long-Range Emigration Fleet

### dic\_word\_ulri\_fleet\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b015`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b015\]
> JP (źródło tłumaczenia): 　第一次星間大戦後、銀河播種計画の実行のため派遣された移民船団。 ⏎ 　現在は新マクロス級を旗艦とした艦隊で構成されており、居住可能な惑星を求めて銀河を旅している。 ⏎ 　移民船団ごとに参加する種族や企業が異なるため、それぞれに特色を持ち、文化やテクノロジーも船団独自のものが生み出されている。
> EN (odniesienie oficjalne, NIE polski): An emigration fleet assembled to execute the Galaxy Seeding Project proposed following Space War 1. ⏎  ⏎ In the current age, these fleets, led by New Macross class flagships, travel the galaxy to reach planets capable of sustained colonization. Each immigration fleet has its own cultural and meta-humanoid composition; as a result, they can be significantly different from one another culturally and even technologically.

### dic\_word\_mr\_ship\_title

Adres: `dic\_text\_word/006b53c9:0ba0b017`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b017\]
> JP (źródło tłumaczenia): 移民居住艦
> EN (odniesienie oficjalne, NIE polski): Emigration Fleet Ship

### dic\_word\_mr\_ship\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b018`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b018\]
> JP (źródło tłumaczenia): 　超長距離移民船団において、居住を目的とした艦。 ⏎ 　新マクロス級移民船では、居住施設をドームで覆った居住艦などが知られ、バトル級可変ステルス攻撃宇宙空母とともに船団を構成している。
> EN (odniesienie oficjalne, NIE polski): A ship in a Super Long-Range Emigration Fleet built to host said immigrants. ⏎  ⏎ In a New Macross emigration fleet, the domed ships are built solely for habitation, with the fleet comprising of some number of dome ships and Battle-class transforming stealth battleships.

### dic\_word\_linn\_m\_title

Adres: `dic\_text\_word/006b53c9:0ba0b01a`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b01a\]
> JP (źródło tłumaczenia): リン・ミンメイ
> EN (odniesienie oficjalne, NIE polski): Lynn Minmay

### dic\_word\_linn\_m\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b01b`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b01b\]
> JP (źródło tłumaczenia): 　第一次星間大戦において、歌で戦争を終結させた地球人のアイドル歌手。 ⏎ 　彼女の歌によって動揺した敵戦闘艦隊を突破する戦術は、ミンメイ・アタックと呼ばれた。 ⏎ 　戦後は巨大移民船メガロード－０１で銀河へと旅立ったが、以降の消息については不明となっている。
> EN (odniesienie oficjalne, NIE polski): An Earthling idol who put an end to Space War 1 with her singing. ⏎  ⏎ The tactics developed to take advantage of the disruption caused among Zentran and Meltran forces by her performances would eventually be known as "the Minmay Attack". ⏎  ⏎ After the war, she headed out into the galaxy aboard the enormous emigration ship Megaroad-01 and, like the rest of that vessel's crew, has been missing ever since.

### dic\_word\_fb\_title

Adres: `dic\_text\_word/006b53c9:0ba0b01d`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b01d\]
> JP (źródło tłumaczenia): Fire Bomber
> EN (odniesienie oficjalne, NIE polski): Fire Bomber

### dic\_word\_fb\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b01e`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b01e\]
> JP (źródło tłumaczenia): 　マクロス７船団で活動したロックバンド。 ⏎ 　メンバーはギター＆ボーカルの熱気バサラ、ベース＆ボーカルのミレーヌ・フレア・ジーナス、キーボードのレイ・ラブロック、ドラムのビヒーダ・フィーズの４人。 ⏎ 　バロータ戦役の際、戦場に飛び出し敵であるプロトデビルンに対しても歌い続けたバサラ。 ⏎ 　その歌が発するエネルギーは戦いを終結させるための大きな力となった。
> EN (odniesienie oficjalne, NIE polski): A rock band originating from emigration ship Macross Seven. ⏎  ⏎ It consists of Nekki Basara on vocals and lead guitar, Mylene Flare Jenius on bass guitar and vocals, Ray Lovelock on keyboard, and Veffidas Feaze on drums. ⏎  ⏎ During the Varauta Conflict, Basara took to the battlefield to deliver his song to Macross Seven's enemies, the Protodeviln. ⏎  ⏎ The energy created by their singing proved key to putting an end to that conflict.

### dic\_word\_sheryl\_n\_title

Adres: `dic\_text\_word/006b53c9:0ba0b020`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b020\]
> JP (źródło tłumaczenia): シェリル・ノーム
> EN (odniesienie oficjalne, NIE polski): Sheryl Nome

### dic\_word\_sheryl\_n\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b021`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b021\]
> JP (źródło tłumaczenia): 　マクロス・フロンティア船団などで活躍した「銀河の妖精」として知られるトップシンガー。 ⏎ 　バジュラ戦役では、ギャラクシー船団の陰謀と謎の宇宙生物バジュラの攻撃にさらされるフロンティア船団をランカ・リーとともに歌の力で救った。
> EN (odniesienie oficjalne, NIE polski): The number one singer aboard the Macross Frontier emigration fleet whose singing career earned her the nickname "the Galactic Fairy". ⏎  ⏎ She and Ranka Lee saved the Frontier with the power of their singing from the threats of the Galaxy Fleet and the then-unknown space-based lifeform called the Vajra.

### dic\_word\_ranka\_l\_title

Adres: `dic\_text\_word/006b53c9:0ba0b023`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b023\]
> JP (źródło tłumaczenia): ランカ・リー
> EN (odniesienie oficjalne, NIE polski): Ranka Lee

### dic\_word\_ranka\_l\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b024`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b024\]
> JP (źródło tłumaczenia): 　マクロス・フロンティア船団などで活躍し「超時空シンデレラ」と呼ばれるようになった少女。 ⏎ 　バジュラ戦役では、ギャラクシー船団の陰謀と謎の宇宙生物バジュラの攻撃にさらされるフロンティア船団をシェリル・ノームとともに歌の力で救った。
> EN (odniesienie oficjalne, NIE polski): A girl aboard the Macross Frontier emigration fleet whose singing career earned her the nickname "Super-Dimension Cinderella". ⏎  ⏎ She and Sheryl Nome saved the Frontier with the power of their singing from the threats of the Galaxy Fleet and the then-unknown space-based lifeform called the Vajra.

### dic\_word\_chaos\_title

Adres: `dic\_text\_word/006b53c9:0ba0b026`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b026\]
> JP (źródło tłumaczenia): ケイオス
> EN (odniesienie oficjalne, NIE polski): Xaos

### dic\_word\_chaos\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b027`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b027\]
> JP (źródło tłumaczenia): 　戦術音楽ユニット「ワルキューレ」を組織した星間複合企業体。 ⏎ 　元々はフォールド技術関連のベンチャー企業であったが、この１０年で急速に成長し、芸能部門や軍事部門をも含む様々な事業を傘下に収める。 ⏎ 　デルタ小隊はブリージンガル球状星団の惑星ラグナを拠点とする「ケイオス・ラグナ支部」の所属である。 ⏎ 　ケイオスとつながる「レディ・Ｍ」がワルキューレとデルタ小隊の設立に深くかかわっているとされるが、その正体は謎に包まれている。
> EN (odniesienie oficjalne, NIE polski): The interstellar conglomerate behind Tactical Sound Unit Walküre. ⏎  ⏎ At its core, it is a venture business specializing in Fold technology. Their rapid growth over the last ten years has seen them expand into the entertainment and military sectors. ⏎  ⏎ Delta Flight is assigned to the branch located on the planet Ragna, in the Brisingr Globular Cluster; this is called, simply, the Xaos Ragna Branch. ⏎  ⏎ Lady M, affiliated with Xaos, was supposedly deeply involved in the creation of Delta Flight and Walküre but her identity remains a mystery to most.

### dic\_word\_misakioku\_title

Adres: `dic\_text\_word/006b53c9:0ba0b029`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b029\]
> JP (źródło tłumaczenia): ミサキオク
> EN (odniesienie oficjalne, NIE polski): Misakioku

### dic\_word\_misakioku\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b02a`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b02a\]
> JP (źródło tłumaczenia): 　「旧嗣野（つぐの）地区管理局」の通称。 ⏎ 　逃尾（にがしお）市に戦前に建設された電波観測所で、創設者は葦原道幸（あしはらみちゆき）とされている。 ⏎ 　過去には、オオタキファクトリーが通信機材の設置工事で訪れている。 ⏎ 　この施設で受信した謎の電波を調べるため、神野銘が派遣された。
> EN (odniesienie oficjalne, NIE polski): The common name of the Tsuguno district administrative building. ⏎  ⏎ Originally built as Nigashio's radio observatory before the war, it was supposedly founded by Michiyuki Ashihara. ⏎  ⏎ The Otaki Factory staff were once employed to install transmission equipment there. ⏎  ⏎ Mei Kamino is sent to investigate a mysterious transmission originating from the building.

### dic\_word\_naratake\_title

Adres: `dic\_text\_word/006b53c9:0ba0b02c`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b02c\]
> JP (źródło tłumaczenia): ナラタケ
> EN (odniesienie oficjalne, NIE polski): Naratake

### dic\_word\_naratake\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b02d`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b02d\]
> JP (źródło tłumaczenia): 　有川ユンが開発したコミュニケーション支援ＡＩ。 ⏎ 　ＰＣや携帯端末にインストールして使用するソフトウェアで、簡易な指示を出すだけで自律的にあらゆる情報を収集・計算してくれる。 ⏎ 　人格のようなものを備えており、神野銘の相棒であるペロ２とジェットジャガーのＡＩには、このナラタケが使われている。 ⏎ 　なお、オオタキファクトリーの公式ホームページから期間限定で無料ダウンロードする事が出来る。
> EN (odniesienie oficjalne, NIE polski): Communication support AI software developed by Yun Arikawa. ⏎  ⏎ It can be installed on a PC or a phone, and organizes and processes any form of data with simple, intuitive commands. ⏎  ⏎ Each instance also has a personality, in its own fashion. Mei Kamino's partner Pelops II and the AI on board Jet Jaguar are both powered by Naratake. ⏎  ⏎ The Otaki Factory public website offers free downloads of the program for a limited time.

### dic\_word\_kamimusi\_title

Adres: `dic\_text\_word/006b53c9:0ba0b02f`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b02f\]
> JP (źródło tłumaczenia): カミムシ
> EN (odniesienie oficjalne, NIE polski): Kamimushi

### dic\_word\_kamimusi\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b030`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b030\]
> JP (źródło tłumaczenia): 　有川ユンのチャット相手のハンドルネーム。 ⏎ 　その素性は不明であるものの、ユンと会話が成り立つだけの頭脳と知識を持った人物。
> EN (odniesienie oficjalne, NIE polski): The screen name of the person Yun Arikawa exchanges texts with. ⏎  ⏎ Their identity is unknown, but they are intelligent and educated enough to hold a conversation with Yun.

### dic\_word\_kamimusi\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b031`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b031\]
> JP (źródło tłumaczenia): 　後に、その正体は神野銘である事が判明した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ They're ultimately revealed to be Mei Kamino.

### dic\_word\_rd\_title

Adres: `dic\_text\_word/006b53c9:0ba0b032`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b032\]
> JP (źródło tłumaczenia): 紅塵
> EN (odniesienie oficjalne, NIE polski): Red Dust

### dic\_word\_rd\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b033`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b033\]
> JP (źródło tłumaczenia): 　怪獣の身体から発見された紅色の物質。 ⏎ 　怪獣の発生と共に空気中や水中に生じて、空や海を紅く染める事が確認されている。 ⏎ 　複雑な構造を持った分子の集まりで、怪獣との関係性が指摘されるが、詳しい事はわかっていない。
> EN (odniesienie oficjalne, NIE polski): A bright red substance discovered in the bodies of kaiju. ⏎  ⏎ It appears in the air or water whenever kaiju manifest, coloring the entire environment red. ⏎  ⏎ It's made of particles with a highly intricate structure, and is theorized to be related to kaiju somehow, though how exactly is unclear.

### dic\_word\_rd\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b034`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b034\]
> JP (źródło tłumaczenia): 　後に、アーキタイプが持つ１３のフェーズのうち、フェーズ１の段階のものである事が判明した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It was later discovered to be the first of thirteen phases of Archetype.

### dic\_word\_arche\_t\_title

Adres: `dic\_text\_word/006b53c9:0ba0b035`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b035\]
> JP (źródło tłumaczenia): アーキタイプ
> EN (odniesienie oficjalne, NIE polski): Archetype

### dic\_word\_arche\_t\_00\_0

Adres: `dic\_text\_word/006b53c9:0ba0b036`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b036\]
> JP (źródło tłumaczenia): 　既存の物理法則では説明できない新素材。 ⏎ 　軽量性や強靭性に優れ、時には自己再生さえもする。 ⏎ 　光を閉じ込めたり、閉じ込めたエネルギーを増幅したりする性質を持っているなど、エネルギー保存の法則を越えたメカニズムが発見されている。 ⏎ 　これまではシミュレーションの中でしか存在していなかったが、ドバイで行われた李博士の講演にて、実在する事が発表された。
> EN (odniesienie oficjalne, NIE polski): A newly discovered substance that cannot be explained by current physics. ⏎  ⏎ To begin with, it's extremely light and durable, and can even regenerate itself spontaneously. ⏎ It's also been found to have properties that can violate conservation of energy, such as trapping light within itself and amplifying it until released. ⏎  ⏎ It was previously only theorized in simulations, but Professor Li revealed that she had successfully produced it in her lecture in Dubai.

### dic\_word\_arche\_t\_00\_1

Adres: `dic\_text\_word/006b53c9:0ba0b037`

> \[BRAK PL: dic\_text\_word/006b53c9:0ba0b037\]
> JP (źródło tłumaczenia): 　１３のフェーズを持ち、その１３番目のフェーズは触媒のように働き、他のアーキタイプを変質させる性質を持つ「オーソゴナル・ダイアゴナライザー」と呼ばれる。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It exists in thirteen phases. The thirteenth functions as a catalyst that can alter other forms of Archetype. This phase is known as the "Orthogonal Diagonalizer".

### dic\_word\_ashihara\_m\_title

Adres: `dic\_text\_word/006b53c9:0be0b000`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b000\]
> JP (źródło tłumaczenia): 葦原道幸
> EN (odniesienie oficjalne, NIE polski): Michiyuki Ashihara

### dic\_word\_ashihara\_m\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b001`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b001\]
> JP (źródło tłumaczenia): 　ミサキオクの創設者。 ⏎ 　アーキタイプ研究の中心人物だが、その正体は謎に包まれている。 ⏎ 　難解な論文を多数残しており、未来予測を行っていたとされる。
> EN (odniesienie oficjalne, NIE polski): The founder of Misakioku. ⏎  ⏎ Despite being a key figure in Archetype research, almost nothing is known about the man himself. ⏎  ⏎ He published a number of cryptic papers. It's suspected he was working on seeing the future.

### dic\_word\_ashihara\_m\_00\_1

Adres: `dic\_text\_word/006b53c9:0be0b002`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b002\]
> JP (źródło tłumaczenia): 　８０年ほど前、大規模な赤潮の調査で新種のクラゲを発見し、その身体の中からアーキタイプを発見した。 ⏎ 　その後は、時間屈折を利用した超時間計算機を開発し、アーキタイプ研究を進める過程で未来に起こる「破局」を回避する方法を調べていたとされている。
> EN (odniesienie oficjalne, NIE polski):  ⏎ In an investigation into a mass red tide phenomenon around eighty years ago, he discovered a new species of jellyfish and extracted Archetype from their bodies. ⏎  ⏎ He used this discovery to develop time distortion technology and build the Super Dimension Calculator. It appears that he was trying to find a way to avert the Catastrophe that continued Archetype research would ultimately lead to.

### dic\_word\_ashihara\_c\_title

Adres: `dic\_text\_word/006b53c9:0be0b003`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b003\]
> JP (źródło tłumaczenia): 葦原カスケード
> EN (odniesienie oficjalne, NIE polski): Ashihara Cascade

### dic\_word\_ashihara\_c\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b004`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b004\]
> JP (źródło tłumaczenia): 　アーキタイプのエネルギー増幅現象を説明する理論。 ⏎ 　エネルギー保存の法則を越えるメカニズムを媒質の中での時間逆行現象を認める事で解釈しようとするアプローチが取られている。 ⏎ 　李博士達が葦原道幸の論文を参考にして長い年月をかけて導き出した結論に、神野銘は手がかりのない状態からごく短い時間でたどり着いた。
> EN (odniesienie oficjalne, NIE polski): The theory that attempts to explain Archetype's energy-amplifying properties. ⏎  ⏎ It's understood to suggest that the way it skirts the law of conservation of energy is by inducing a time regression phenomenon within the substance's mass. ⏎  ⏎ Professor Li's team took months to reach this conclusion with the aid of Michiyuki Ashihara's notes, but Mei Kamino arrived at it in a short time and with no leads.

### dic\_word\_salunga\_title

Adres: `dic\_text\_word/006b53c9:0be0b006`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b006\]
> JP (źródło tłumaczenia): サルンガ
> EN (odniesienie oficjalne, NIE polski): Salunga

### dic\_word\_salunga\_00\_0

Adres: `dic\_text\_word/006b53c9:0be0b007`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b007\]
> JP (źródło tłumaczenia): 　インドのアーキタイプの研究施設に現れた怪獣。 ⏎ 　二足歩行型で、高い俊敏性と紅塵をコントロールする力を持っている。 ⏎ 　ＢＢの開発した試作型のオーソゴナル・ダイアゴナライザーによって、一度は活動停止に追い込まれたものの、その後に復活し、研究施設の地下にある特異点「シヴァ」へと侵攻する。
> EN (odniesienie oficjalne, NIE polski): The kaiju that attacked the Archetype research facility in India. ⏎  ⏎ It's bipedal and highly agile, and it can also control Archetype. ⏎  ⏎ It was temporarily contained by the prototype Orthogonal Diagonalizer developed by BB, but later broke free and made a charge for Shiva, the Singular Point beneath the facility.

### dic\_word\_salunga\_00\_1

Adres: `dic\_text\_word/006b53c9:0be0b008`

> \[BRAK PL: dic\_text\_word/006b53c9:0be0b008\]
> JP (źródło tłumaczenia): 　オーソゴナル・ダイアゴナライザーの効果が完全に発動した事により、紅塵の消滅と合わせて活動を停止した。
> EN (odniesienie oficjalne, NIE polski):  ⏎ It was erased along with the Red Dust when the Orthogonal Diagonalizer was fully activated.

