// src/game/locations.js
// Specjalne lokacje na mapie — Wieże Magów, Lochy, Portale

/**
 * Typy specjalnych lokacji.
 */
export const LOCATION_TYPES = {
    MAGE_TOWER: {
        id: 'mage_tower',
        name: 'Wieża Magów',
        icon: '🏰',
        description: 'Starożytna wieża pełna magicznej energii. Miejsce odpoczynku i regeneracji dla wędrownych magów.',
        effects: {
            fullManaRestore: true,
            fullHeal: true,
            savePoint: true
        }
    },
    DUNGEON: {
        id: 'dungeon',
        name: 'Loch',
        icon: '⚔️',
        description: 'Mroczne podziemia kryjące potężne potwory i jeszcze potężniejsze skarby.',
        effects: {
            combatChallenge: true,
            bossFight: true
        }
    },
    PORTAL: {
        id: 'portal',
        name: 'Portal',
        icon: '🌀',
        description: 'Migoczący portal prowadzący do innego regionu świata. Kto wie, co czeka po drugiej stronie?',
        effects: {
            teleport: true,
            newRegion: true
        }
    },
    ALTAR: {
        id: 'altar',
        name: 'Ołtarz Przyzwania',
        icon: '🔮',
        description: 'Miejsce mocy, gdzie więź między światami jest najsilniejsza. Rekrutacja tutaj jest tańsza i pewniejsza.',
        effects: {
            cheaperRecruitment: true,
            guaranteedRecruit: true
        }
    },
    CAMPFIRE: {
        id: 'campfire',
        name: 'Obozowisko',
        icon: '🏕️',
        description: 'Porzucone obozowisko innego wędrowca. Bezpieczne miejsce na krótki odpoczynek.',
        effects: {
            smallManaRestore: true,
            smallHeal: true
        }
    }
};

/**
 * Generuje specjalne lokacje na mapie.
 * Rozmieszcza je w odległości 5-10 pól od siebie.
 */
export function generateSpecialLocations(mapSize) {
    const locations = [];
    const types = Object.values(LOCATION_TYPES);
    
    // Liczba lokacji: ~1 na 30 pól
    const numLocations = Math.floor((mapSize * mapSize) / 30);
    
    for (let i = 0; i < numLocations; i++) {
        const x = Math.floor(Math.random() * mapSize);
        const y = Math.floor(Math.random() * mapSize);
        const type = types[Math.floor(Math.random() * types.length)];
        
        // Sprawdź czy nie za blisko innej lokacji
        const tooClose = locations.some(loc => {
            const dist = Math.max(Math.abs(loc.x - x), Math.abs(loc.y - y));
            return dist < 4;
        });
        
        if (!tooClose && !(x === Math.floor(mapSize/2) && y === Math.floor(mapSize/2))) {
            locations.push({ x, y, type: type.id, discovered: false });
        }
    }
    
    return locations;
}

/**
 * Zwraca lokację na danym polu (lub null).
 */
export function getLocationAt(locations, x, y) {
    return locations.find(loc => loc.x === x && loc.y === y) || null;
}

/**
 * Aplikuje efekty lokacji na gracza.
 */
export function applyLocationEffects(world, locationType) {
    const effects = locationType.effects;
    const log = [];
    
    if (effects.fullManaRestore) {
        world.player.mana = world.player.maxMana;
        log.push(`✨ Mana w pełni odnowiona! (${world.player.mana}/${world.player.maxMana})`);
    }
    
    if (effects.smallManaRestore) {
        const restored = Math.min(2, world.player.maxMana - world.player.mana);
        world.player.mana += restored;
        if (restored > 0) {
            log.push(`✨ Odpoczynek przywraca ${restored} many.`);
        }
    }
    
    if (effects.fullHeal) {
        for (const member of world.party) {
            member.con = 5;
        }
        log.push(`💚 Cała drużyna w pełni uleczona!`);
    }
    
    if (effects.smallHeal) {
        for (const member of world.party) {
            member.con = Math.min(5, member.con + 1);
        }
        log.push(`💚 Drużyna lekko uleczona (+1 CON).`);
    }
    
    return log;
}
