// src/game/world.js
// System generowania i zarządzania światem gry

import { BIOMES, generateBiome, randomBiome } from '../engine/biomes.js';
import { generateSpecialLocations } from './locations.js';

const WORLD_SIZE = 30; // 30x30 grid
const SAVE_KEY = 'mages_journey_save';

/**
 * Generuje nowy świat gry.
 * @returns {Object} Świat z mapą, pozycją gracza, etc.
 */
export function generateWorld() {
    const map = [];
    const discovered = [];
    
    // Najpierw zainicjalizuj całą tablicę discovered z false
    for (let y = 0; y < WORLD_SIZE; y++) {
        const discoveredRow = [];
        for (let x = 0; x < WORLD_SIZE; x++) {
            discoveredRow.push(false);
        }
        discovered.push(discoveredRow);
    }
    
    // Teraz generuj mapę z algorytmem dziedziczenia
    for (let y = 0; y < WORLD_SIZE; y++) {
        const row = [];
        for (let x = 0; x < WORLD_SIZE; x++) {
            // Zbierz odkrytych sąsiadów (na początku puste)
            const neighbors = getDiscoveredNeighbors(map, discovered, x, y);
            const biomeId = generateBiome(neighbors);
            row.push(biomeId);
        }
        map.push(row);
    }
    
    // Pozycja startowa gracza (środek mapy)
    const startX = Math.floor(WORLD_SIZE / 2);
    const startY = Math.floor(WORLD_SIZE / 2);
    
    // Odkryj obszar startowy (3x3 wokół gracza)
    discoverArea(discovered, startX, startY, 1);
    
    // Generuj specjalne lokacje
    const specialLocations = generateSpecialLocations(WORLD_SIZE);
    
    return {
        map,
        discovered,
        specialLocations,
        player: {
            x: startX,
            y: startY,
            mana: 5,
            maxMana: 5,
            renown: 0,
            lore: 0
        },
        party: [], // Drużyna potworów
        maxPartySize: 3,
        turn: 0,
        log: []
    };
}

/**
 * Zwraca odkrytych sąsiadów danego pola.
 */
function getDiscoveredNeighbors(map, discovered, x, y) {
    const neighbors = [];
    const offsets = [
        [-1, -1], [0, -1], [1, -1],
        [-1,  0],          [1,  0],
        [-1,  1], [0,  1], [1,  1]
    ];
    
    for (const [dx, dy] of offsets) {
        const nx = x + dx;
        const ny = y + dy;
        
        if (nx >= 0 && nx < WORLD_SIZE && ny >= 0 && ny < WORLD_SIZE) {
            if (discovered[ny][nx]) {
                neighbors.push(map[ny][nx]);
            }
        }
    }
    
    return neighbors;
}

/**
 * Odkrywa obszar wokół punktu (zasięg radius).
 */
export function discoverArea(discovered, x, y, radius = 1) {
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            const nx = x + dx;
            const ny = y + dy;
            
            if (nx >= 0 && nx < WORLD_SIZE && ny >= 0 && ny < WORLD_SIZE) {
                discovered[ny][nx] = true;
            }
        }
    }
}

/**
 * Sprawdza czy pole jest odkryte.
 */
export function isDiscovered(world, x, y) {
    if (x < 0 || x >= WORLD_SIZE || y < 0 || y >= WORLD_SIZE) {
        return false;
    }
    return world.discovered[y][x];
}

/**
 * Zwraca biom na danym polu.
 */
export function getBiomeAt(world, x, y) {
    if (x < 0 || x >= WORLD_SIZE || y < 0 || y >= WORLD_SIZE) {
        return null;
    }
    const biomeId = world.map[y][x];
    return BIOMES[biomeId] || null;
}

/**
 * Zapisuje świat do localStorage.
 */
export function saveWorld(world) {
    try {
        const data = JSON.stringify(world);
        localStorage.setItem(SAVE_KEY, data);
        console.log('💾 Świat zapisany!');
        return true;
    } catch (e) {
        console.error('❌ Błąd zapisu:', e);
        return false;
    }
}

/**
 * Ładuje świat z localStorage.
 */
export function loadWorld() {
    try {
        const data = localStorage.getItem(SAVE_KEY);
        if (!data) return null;
        
        const world = JSON.parse(data);
        console.log('📂 Świat załadowany!');
        return world;
    } catch (e) {
        console.error('❌ Błąd ładowania:', e);
        return null;
    }
}

/**
 * Usuwa zapis gry.
 */
export function clearSave() {
    localStorage.removeItem(SAVE_KEY);
    console.log('🗑️ Zapis usunięty!');
}

/**
 * Sprawdza czy istnieje zapis gry.
 */
export function hasSave() {
    return localStorage.getItem(SAVE_KEY) !== null;
}
