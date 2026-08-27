// src/engine/unit.js
// Definicja jednostki (Bytu) — port z Monster Engine 6.0

/**
 * Tworzy nową jednostkę (Byt) na podstawie zmaterializowanej karty MTG.
 *
 * @param {Object} config
 * @param {string} config.name - Nazwa bytu
 * @param {string} config.bio - Opis fabularny (3-5 zdań)
 * @param {string} config.cardId - ID karty MTG (np. "1LTR")
 * @param {Object} config.domains - { A: "Ogień", B: "Metal", C: "Śmierć", D: "Kapłanka" }
 * @param {Object} config.abilities - { A: {...}, B: {...}, C: {...}, D: {...} }
 * @returns {Object} Pełna jednostka gotowa do walki
 */
export function createUnit({ name, bio, cardId, domains, abilities }) {
    return {
        // Tożsamość
        name,
        bio,
        cardId,
        
        // Domeny (4 sztuki)
        domains: { ...domains },
        
        // Zdolności (4 sztuki)
        abilities: { ...abilities },
        
        // Stan bojowy
        con: 5.0,           // Kondycja (float HP)
        maxCon: 5.0,
        tempHp: 0.0,        // Tymczasowe HP
        
        // Pozycja na mapie
        position: [0, 0],
        
        // Cooldowny (0 = gotowa, >0 = tury do odnowienia)
        cooldowns: { A: 0, B: 0, C: 0, D: 0 },
        
        // Setup stacks (dla EMPOWERED, cap 3)
        setupStacks: 0,
        
        // Statusy aktywne
        statuses: [],        // [{type: "ROOT", duration: 2, source: "Nazwa", abilityName: "..."}]
        
        // RES modyfikatory
        resModifiers: [],   // [{abilityName, mode, kind, axis, domain, value, duration}]
        
        // Efekty okresowe (DOT/HOT/DRAIN_DOT)
        otEffects: [],       // [{abilityName, type, tick, duration, source}]
        
        // Odroczone leczenia
        pendingHeals: [],    // [{abilityName, targetName, healAmount, bac, remaining}]
        
        // Tymczasowe HP ze zdolności (trackowane z duration)
        tempHpEffects: [],   // [{abilityName, source, value, duration}]
        
        // Lustrzane tarcze (REFLECT)
        reflectShields: [],  // [{abilityName, source, slots, bacPerSlot}]
        
        // System Argos (kolejność aktywacji)
        turnsSinceAction: 0,
        entropyCounter: 0,
        
        // Relacje z innymi jednostkami
        relationships: {},   // {"Nazwa": number (-100..100)}
        
        // Renoma
        renown: 0.0,
        lastRenownMilestone: 0
    };
}

/**
 * Sprawdza czy jednostka jest żywa.
 * @param {Object} unit
 * @returns {boolean}
 */
export function isAlive(unit) {
    return unit.con > 0;
}

/**
 * Zadaje obrażenia jednostce (przez warstwy TEMP_HP).
 * @param {Object} unit
 * @param {number} damage
 * @returns {Object} { braceAbsorbed, effectsAbsorbed, realDamage, died }
 */
export function dealDamage(unit, damage) {
    let remaining = damage;
    let braceAbsorbed = 0;
    let effectsAbsorbed = 0;
    
    // Warstwa 1: BRACE TEMP_HP (nie trackowane w tempHpEffects)
    const effectsTemp = unit.tempHpEffects.reduce((sum, e) => sum + e.value, 0);
    const braceTemp = Math.max(0, unit.tempHp - effectsTemp);
    
    braceAbsorbed = Math.min(braceTemp, remaining);
    remaining -= braceAbsorbed;
    
    // Warstwa 2: TEMP_HP efekty (od najstarszego)
    for (const eff of unit.tempHpEffects) {
        if (remaining <= 0) break;
        const absorbed = Math.min(eff.value, remaining);
        eff.value -= absorbed;
        remaining -= absorbed;
        effectsAbsorbed += absorbed;
    }
    
    // Usuń efekty z zerową wartością
    unit.tempHpEffects = unit.tempHpEffects.filter(e => e.value > 0);
    
    // Aktualizuj temp_hp i CON
    const totalAbsorbed = braceAbsorbed + effectsAbsorbed;
    unit.tempHp = Math.max(0, unit.tempHp - totalAbsorbed);
    unit.con = Math.max(0, unit.con - damage);
    
    return {
        braceAbsorbed: Math.round(braceAbsorbed * 100) / 100,
        effectsAbsorbed: Math.round(effectsAbsorbed * 100) / 100,
        realDamage: Math.round((damage - totalAbsorbed) * 100) / 100,
        died: unit.con <= 0
    };
}

/**
 * Leczy jednostkę (cap do maxCon).
 * @param {Object} unit
 * @param {number} amount
 * @returns {number} Faktycznie uleczone HP
 */
export function healUnit(unit, amount) {
    const realCon = unit.con - unit.tempHp;
    const maxReal = unit.maxCon;
    const actualHeal = Math.min(amount, maxReal - realCon);
    unit.con = Math.min(unit.maxCon + unit.tempHp, unit.con + actualHeal);
    return Math.round(actualHeal * 100) / 100;
}
