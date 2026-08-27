// src/game/narrator.js
// Narrator — generuje tekstowe opisy wydarzeń w grze

import { BIOMES } from '../engine/biomes.js';

/**
 * Generuje narrację początku walki.
 */
export function narrateCombatStart(playerParty, enemies, biome) {
    const enemyNames = enemies.map(e => e.name).join(', ');
    const biomeName = biome ? biome.name : 'nieznanej krainie';
    
    const openings = [
        `Z cieni ${biomeName} wyłaniają się wrogie istoty: **${enemyNames}**. Nie ma odwrotu — czas na walkę!`,
        `Gdy przekraczasz granicę ${biomeName}, drogę zagradzają Ci **${enemyNames}**. Ich zamiary są jasne — chcą Twojej krwi.`,
        `Niespodziewany atak! **${enemyNames}** wyskakują z ukrycia pośród ${biomeName}. Twoja drużyna przyjmuje pozycje bojowe.`,
        `Ziemia drży pod stopami, gdy **${enemyNames}** stają na Twojej drodze. ${biomeName} zdaje się sprzyjać tym stworzeniom.`
    ];
    
    return openings[Math.floor(Math.random() * openings.length)];
}

/**
 * Generuje narrację zwycięstwa.
 */
export function narrateVictory(enemies, playerParty) {
    const survivors = playerParty.filter(u => u.con > 0).length;
    
    const narrations = [
        `Ostatni wróg pada z głuchym odgłosem. Pole bitwy cichnie. Twoja drużyna (${survivors} ocalałych) stoi victorious wśród ciał pokonanych.`,
        `Zwycięstwo! Wrogowie leżą pokonani, a ich esencja rozpływa się w powietrzu. Twoja drużyna zbiera siły po ciężkiej walce.`,
        `Ostatni cios przesądza o wyniku starcia. Cisza zapada nad polem walki. Jesteś zwycięzcą.`,
        `Kurz bitewny opada. Twoi wrogowie zostali pokonani, a Ty стоisz dumnie pośród ${biomeOrNot()} pokonanych istot.`
    ];
    
    return narrations[Math.floor(Math.random() * narrations.length)];
}

/**
 * Generuje narrację porażki.
 */
export function narrateDefeat(playerParty) {
    const narrations = [
        `Twoja drużyna pada na kolana. Ciemność zamyka się wokół Ciebie. To jeszcze nie koniec — ale tym razem przegrałeś.`,
        `Ostatni cios wroga trafia cel. Twoja drużyna zostaje pokonana. Budzisz się w Wieży Magów, słaby ale żywy.`,
        `Siły Cię opuszczają. Wrogowie stoją nad Tobą triumfująco. Magia teleportacji ratuje Cię w ostatniej chwili.`
    ];
    
    return narrations[Math.floor(Math.random() * narrations.length)];
}

/**
 * Generuje narrację rekrutacji.
 */
export function narrateRecruitment(creature) {
    const narrations = [
        `**${creature.name}** pochyla głowę w geście poddaństwa. Od teraz będzie wiernym towarzyszem Twojej podróży.`,
        `Więź między Wami zostaje nawiązana. **${creature.name}** dołącza do Twojej drużyny, gotów walczyć u Twego boku.`,
        `Z szacunkiem i podziwem, **${creature.name}** przyjmuje Twoją ofertę sojuszu. Nowy rozdział Waszej wspólnej podróży właśnie się zaczyna.`,
        `Magiczna nić łączy Wasze umysły. **${creature.name}** staje się częścią Twojej drużyny — sługą, przyjacielem, towarzyszem broni.`
    ];
    
    return narrations[Math.floor(Math.random() * narrations.length)];
}

/**
 * Generuje narrację odkrycia nowej krainy.
 */
export function narrateDiscovery(biome, turn) {
    const biomeAdj = getBiomeAdjective(biome.name);
    
    if (turn <= 3) {
        return `Stawiasz pierwsze kroki w tej ${biomeAdj} krainie. Wszystko tu jest nowe i nieznane. ${biome.description}`;
    }
    
    const discoveries = [
        `Twoja wędrówka prowadzi Cię przez ${biomeAdj} tereny. ${biome.description}`,
        `Krajobraz zmienia się — teraz otacza Cię ${biome.name}. ${biome.description}`,
        `Nowa kraina rozpościera się przed Tobą. ${biome.description}`
    ];
    
    return discoveries[Math.floor(Math.random() * discoveries.length)];
}

/**
 * Generuje narrację znalezienia skarbu.
 */
export function narrateTreasure(manaFound, biome) {
    const treasures = [
        `W szczelinie między kamieniami dostrzegasz błysk magicznej energii. To **${manaFound} many** — cenny zasób dla każdego maga!`,
        `Porzucony sakiewka innego wędrowca kryje **${manaFound} many**. Szczęście Ci dziś sprzyja.`,
        `Między korzeniami starego drzewa znajdujesz skrzącą się kulę mocy — **${manaFound} many** do Twojej kolekcji.`
    ];
    
    return treasures[Math.floor(Math.random() * treasures.length)];
}

/**
 * Generuje narrację pułapki.
 */
export function narrateTrap(biome) {
    const traps = [
        `Ziemia usuwa się spod Twoich stóp! Ledwo unikasz upadku w ukrytą jamę.`,
        `Magiczna runa eksploduje pod Twoimi stopami, wysysając część Twojej many.`,
        `Sidła zaciskają się na nodze! Uwalniając się, tracisz cenną energię.`,
        `Ukryte ostrze tnie powietrze tuż obok Twojej głowy. Ktoś tu zastawił pułapkę.`
    ];
    
    return traps[Math.floor(Math.random() * traps.length)];
}

// Helper
function getBiomeAdjective(name) {
    const adj = {
        "Łąki": "falujące",
        "Las (Rzadki)": "świetliste",
        "Las (Gęsty)": "mroczne",
        "Dżungla": "parne",
        "Pogórze": "skaliste",
        "Wysokie Góry": "ośnieżone",
        "Bagna": "cuchnące",
        "Moczary": "ponure",
        "Step": "bezkresne",
        "Pustynia": "żarzące się",
        "Lądolód": "lodowate",
        "Pustynia Bazaltowa": "czarne",
        "Ruiny": "zapomniane",
        "Wrzosowiska": "fioletowe",
        "Pola Uprawne": "spokojne"
    };
    return adj[name] || "tajemnicze";
}

function biomeOrNot() {
    return '';
}
