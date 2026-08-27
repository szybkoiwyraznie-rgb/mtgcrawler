// src/engine/dva.js
// Algorytm DVA (Defensive Valuation Algorithm) — port z Monster Engine 6.0
//
// DVA oblicza szansę trafienia ataku na podstawie interakcji domen
// atakującego i obrońcy, z uwzględnieniem:
// - Macierzy wpływu (fizycznej lub tarota)
// - Slotu ataku (główny A/C = 100%, wspomagający B/D = obrona +50%)
// - Modyfikatorów terenu
// - RES modyfikatorów (buffy/debuffy)

import { getDefenseValue, PHYSICAL_DOMAINS, TAROT_DOMAINS } from './domains.js';

/**
 * Oblicza szansę trafienia ataku (DVA).
 *
 * @param {Object} attacker - Jednostka atakująca
 * @param {Object} defender - Jednostka broniąca
 * @param {string} abilitySlot - Slot zdolności: "A", "B", "C", "D"
 * @param {Object|null} terrain - Biom (opcjonalnie, z BIOMES)
 * @returns {Object} { hitChance, defenseChance, breakdown }
 */
export function calculateDVA(attacker, defender, abilitySlot, terrain = null) {
    // 1. Określ typ konfliktu
    const isPhysical = abilitySlot === "A" || abilitySlot === "B";
    const isMainSlot = abilitySlot === "A" || abilitySlot === "C";

    // 2. Domena atakująca
    const attackDomain = attacker.domains[abilitySlot];

    // 3. Domeny obronne
    const mainDefDomain = isPhysical ? defender.domains.A : defender.domains.C;
    const supportDefDomain = isPhysical ? defender.domains.B : defender.domains.D;

    // 4. Wartości bazowe z macierzy
    let d1 = getDefenseValue(attackDomain, mainDefDomain, isPhysical);
    let d2Raw = getDefenseValue(attackDomain, supportDefDomain, isPhysical);

    // 4b. RES modyfikatory (TODO: implementacja z res_modifiers)
    const resDelta = getResDefenseDelta(attacker, defender, attackDomain, isPhysical);
    if (resDelta !== 0) {
        d1 = clamp(d1 + resDelta, 0, 100);
        d2Raw = clamp(d2Raw + resDelta, 0, 100);
    }

    // 5. Domena wspomagająca obrońcy = 50% wartości
    const d2 = d2Raw * 0.5;

    // 6. Baza obrony
    const defenseBase = (d1 + d2) / 2;

    // 7. Modyfikator slotu ataku
    let defenseFinal;
    if (isMainSlot) {
        // Slot główny: obrona bez zmian
        defenseFinal = defenseBase;
    } else {
        // Slot wspomagający: obrona podwyższona o połowę brakującej wartości
        defenseFinal = defenseBase + (100 - defenseBase) / 2;
    }

    // 8. Modyfikatory terenu
    let terrainMod = 0;
    let terrainDesc = "";
    if (terrain) {
        if (attackDomain === terrain.bonus_20) {
            terrainMod += 20;
            terrainDesc += `+20% (${terrain.name} → ${attackDomain})`;
        }
        if (attackDomain === terrain.penalty_20) {
            terrainMod -= 20;
            terrainDesc += `-20% (${terrain.name} → ${attackDomain})`;
        }
        if (terrain.bonus_10 && terrain.bonus_10.includes(attackDomain)) {
            terrainMod += 10;
            terrainDesc += `+10% (${terrain.name} → ${attackDomain})`;
        }
        if (terrain.penalty_10 && terrain.penalty_10.includes(attackDomain)) {
            terrainMod -= 10;
            terrainDesc += `-10% (${terrain.name} → ${attackDomain})`;
        }
    }

    // 9. Finalna szansa trafienia
    let hitChance = 100 - defenseFinal + terrainMod;
    hitChance = clamp(hitChance, 0, 100);

    // 10. Breakdown (do narracji / debugu)
    const slotType = isMainSlot ? "główny" : "wspomagający";
    const attackType = isPhysical ? "fizyczny" : "niefizyczny";
    
    const breakdown = [
        `${attackDomain} (${slotType}, ${attackType}) vs ${mainDefDomain}/${supportDefDomain}`,
        resDelta !== 0 ? `RES: ${resDelta > 0 ? '+' : ''}${resDelta}%` : null,
        `Obrona: (${r(d1)} + ${r(d2Raw)}×0.5) / 2 = ${r(defenseBase)}%`,
        !isMainSlot ? `Slot wspomagający: ${r(defenseBase)} + (100-${r(defenseBase)})/2 = ${r(defenseFinal)}%` : null,
        `Szansa trafienia: 100 - ${r(defenseFinal)} = ${r(100 - defenseFinal)}%`,
        terrainDesc ? `Teren: ${terrainDesc}` : null,
        terrainMod !== 0 ? `Po terenie: ${r(hitChance)}%` : null
    ].filter(Boolean).join("\n");

    return {
        hitChance: Math.round(hitChance),
        defenseChance: Math.round(defenseFinal),
        breakdown,
        attackDomain,
        mainDefDomain,
        supportDefDomain
    };
}

/**
 * Rozstrzyga atak — rzut k100 z krytykami.
 *
 * @param {Object} attacker
 * @param {Object} defender
 * @param {string} abilitySlot
 * @param {number} roll - Rzut k100 (1-100)
 * @param {Object|null} terrain
 * @returns {Object} { success, hitChance, roll, isCritical, breakdown }
 */
export function resolveAttack(attacker, defender, abilitySlot, roll, terrain = null) {
    const dva = calculateDVA(attacker, defender, abilitySlot, terrain);

    // Krytyki: 1-5 = zawsze trafienie, 96-100 = zawsze pudło
    let isCritical = false;
    let success;

    if (roll <= 5) {
        success = true;
        isCritical = true;
    } else if (roll >= 96) {
        success = false;
        isCritical = true;
    } else {
        success = roll <= dva.hitChance;
    }

    return {
        success,
        hitChance: dva.hitChance,
        roll,
        isCritical,
        breakdown: dva.breakdown,
        attackDomain: dva.attackDomain,
        mainDefDomain: dva.mainDefDomain,
        supportDefDomain: dva.supportDefDomain
    };
}

/**
 * Rzut k100.
 * @returns {number} 1-100
 */
export function rollD100() {
    return Math.floor(Math.random() * 100) + 1;
}

// === HELPERY ===

function clamp(val, min, max) {
    return Math.max(min, Math.min(max, val));
}

function r(val) {
    return Math.round(val * 100) / 100;
}

/**
 * Oblicza deltę RES do obrony (placeholder — pełna implementacja w payloads.js).
 * Na razie zwraca 0.
 */
function getResDefenseDelta(attacker, defender, attackDomain, isPhysical) {
    // TODO: Implementacja z res_modifiers jednostek
    return 0;
}
