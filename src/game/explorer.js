// src/game/explorer.js
// System eksploracji — ruch gracza, encountery, logika tury

import { discoverArea, getBiomeAt, isDiscovered } from './world.js';
import { generateEnemies } from './combat.js';
import { getRandomCard } from '../data/card_registry.js';

// Typy encounterów i ich prawdopodobieństwa
const ENCOUNTER_TYPES = {
    COMBAT:    { chance: 0.40, label: "⚔️ Walka" },
    NEUTRAL:   { chance: 0.25, label: "🤝 Spotkanie neutralne" },
    TRAP:      { chance: 0.10, label: "⚠️ Pułapka" },
    TREASURE:  { chance: 0.10, label: "💎 Skarb" },
    STORY:     { chance: 0.15, label: "📖 Wydarzenie fabularne" }
};

/**
 * Przesuwa gracza na nowe pole.
 */
export function movePlayer(world, dx, dy) {
    const newX = world.player.x + dx;
    const newY = world.player.y + dy;
    const result = {
        success: false,
        newPosition: null,
        biome: null,
        encounter: null,
        log: []
    };
    
    if (newX < 0 || newX >= 30 || newY < 0 || newY >= 30) {
        result.log.push("🚫 Nie możesz wyjść poza granice świata.");
        return result;
    }
    
    world.player.x = newX;
    world.player.y = newY;
    world.turn += 1;
    result.success = true;
    result.newPosition = { x: newX, y: newY };
    
    // Regeneracja many co 5 tur
    if (world.turn % 5 === 0 && world.player.mana < world.player.maxMana) {
        world.player.mana = Math.min(world.player.maxMana, world.player.mana + 1);
        result.log.push("✨ Czujesz przypływ many. (+1 many)");
    }
    
    const wasUndiscovered = !world.discovered[newY][newX];
    discoverArea(world.discovered, newX, newY, 1);
    
    const biome = getBiomeAt(world, newX, newY);
    result.biome = biome;
    
    if (wasUndiscovered) {
        result.log.push(`🗺️ Odkrywasz nowy teren: **${biome.name}**.`);
        result.log.push(`📜 ${biome.description}`);
        // Statystyka
    } else {
        result.log.push(`🚶 Przechodzisz przez ${biome.name}.`);
    }
    
    // Generuj encounter (60% szans)
    if (Math.random() < 0.60) {
        const encounter = generateEncounter(world, biome);
        if (encounter) {
            result.encounter = encounter;
            result.log.push(encounter.description);
        }
    } else {
        result.log.push(generatePeacefulNarrative(biome));
    }
    
    return result;
}

function generateEncounter(world, biome) {
    const roll = Math.random();
    let cumulative = 0;
    
    for (const [type, config] of Object.entries(ENCOUNTER_TYPES)) {
        cumulative += config.chance;
        if (roll <= cumulative) {
            return createEncounter(type, biome, world);
        }
    }
    
    return createEncounter("STORY", biome, world);
}

function createEncounter(type, biome, world) {
    switch (type) {
        case "COMBAT": {
            const difficulty = 1 + Math.floor(world.turn / 10);
            const enemies = generateEnemies(biome, difficulty);
            return {
                type: "COMBAT",
                label: "⚔️ Walka",
                description: `Z cienia ${biome.name} wyłania ${enemies.length > 1 ? 'się grupa wrogów' : 'się wróg'}!`,
                enemies,
                biomeId: world.map[world.player.y][world.player.x],
                difficulty
            };
        }
        
        case "NEUTRAL": {
            const card = getRandomCard();
            const recruitCost = Math.floor(Math.random() * 3) + 2;
            return {
                type: "NEUTRAL",
                label: "🤝 Spotkanie",
                description: `Spotykasz **${card.unit.name}** w ${biome.name}. Nie jest wrogo nastawiona — może uda się ją przekonać do współpracy?`,
                creature: card,
                recruitCost
            };
        }
        
        case "TRAP":
            return {
                type: "TRAP",
                label: "⚠️ Pułapka",
                description: `Wpadłeś w pułapkę! ${getRandomTrapDescription()}`,
                effect: "lose_mana"
            };
        
        case "TREASURE": {
            const manaFound = Math.floor(Math.random() * 3) + 1;
            return {
                type: "TREASURE",
                label: "💎 Skarb",
                description: `Odkrywasz ukryty schowek w ${biome.name}! Znajdujesz **${manaFound} many**.`,
                reward: { mana: manaFound }
            };
        }
        
        case "STORY":
            return {
                type: "STORY",
                label: "📖 Wydarzenie",
                description: getRandomStoryEvent(biome),
                choices: [
                    { text: "Zbadaj bliżej", effect: "explore" },
                    { text: "Idź dalej", effect: "ignore" }
                ]
            };
        
        default:
            return null;
    }
}

// === HELPERY TEKSTOWE ===

function generatePeacefulNarrative(biome) {
    const narratives = [
        `Wiatr szepcze cicho między ${biome.name.toLowerCase()}. Droga wydaje się bezpieczna.`,
        `Spokojna wędrówka przez ${biome.name.toLowerCase()}. Słyszysz odległe odgłosy natury.`,
        `${biome.name} otacza Cię swoim charakterystycznym klimatem. Nic nie zakłóca ciszy.`,
        `Krok za krokiem przemierzasz ${biome.name.toLowerCase()}. Świat czeka na Twoje odkrycia.`,
        `Twoje kroki niosą się echem przez ${biome.name.toLowerCase()}. Czujesz obecność magii w powietrzu.`,
        `Krajobraz ${biome.name} zmienia się powoli, ale nieubłaganie. Każdy krok to nowa historia.`
    ];
    return narratives[Math.floor(Math.random() * narratives.length)];
}

function getRandomTrapDescription() {
    const traps = [
        "Zapadłeś się w ukrytą jamę przykrytą liśćmi.",
        "Magiczna runa eksplodowała pod Twoimi stopami!",
        "Sidła zacisnęły się na Twojej kostce!",
        "Strzały wystrzelone z ukrytych pułapek świszczą wokół!",
        "Ziemia rozstąpiła się pod Tobą — ledwo uniknąłeś upadku!"
    ];
    return traps[Math.floor(Math.random() * traps.length)];
}

function getRandomStoryEvent(biome) {
    const events = [
        `Na skraju ${biome.name} zauważasz dziwne, świecące runy wyryte w kamieniu. Wyglądają na starożytne.`,
        `Spotykasz wędrownego handlarza, który oferuje Ci tajemniczy artefakt w zamian za opowieść o Twoich przygodach.`,
        `Znajdujesz porzucony dziennik innego maga. Zapiski urywają się nagle...`,
        `Stary dąb zdaje się do Ciebie przemawiać szeptem wiatru. Coś tu jest nie tak.`,
        `Odkrywasz ślady obozowiska. Ktoś tu był niedawno — może inny Mag?`,
        `W oddali widzisz sylwetkę innej postaci. Znika za horyzontem, zanim zdążysz ją dogonić.`,
        `Znajdujesz resztki starożytnej biblioteki. Większość ksiąg jest zniszczona, ale kilka ocalało.`
    ];
    return events[Math.floor(Math.random() * events.length)];
}
