// src/game/combat.js
// System walki taktycznej — prototyp

import { createUnit, dealDamage, isAlive } from '../engine/unit.js';
import { resolveAttack, rollD100 } from '../engine/dva.js';
import { getRandomCard } from '../data/card_registry.js';
import { BIOMES } from '../engine/biomes.js';

/**
 * Stan walki.
 */
export function createCombatState(playerParty, enemies, biomeId) {
    return {
        active: true,
        turn: 0,
        round: 1,
        playerParty: playerParty.map(u => ({ ...u, isPlayer: true })),
        enemies: enemies.map(u => ({ ...u, isPlayer: false })),
        biome: BIOMES[biomeId] || null,
        log: [],
        result: null // 'victory', 'defeat', 'fled'
    };
}

/**
 * Generuje wrogów na podstawie biomu i trudności.
 */
export function generateEnemies(biomeId, difficulty = 1) {
    const count = Math.min(1 + Math.floor(difficulty / 2), 3); // 1-3 wrogów
    const enemies = [];
    
    for (let i = 0; i < count; i++) {
        const card = getRandomCard();
        const unit = createUnit({
            name: card.unit.name,
            bio: card.unit.bio,
            cardId: card.id,
            domains: card.unit.domains,
            abilities: card.unit.abilities
        });
        unit.name = `${unit.name} #${i + 1}`; // Rozróżnij wrogów
        enemies.push(unit);
    }
    
    return enemies;
}

/**
 * Generuje narrację walki dla pojedynczej akcji.
 */
function narrateAttack(attacker, defender, abilitySlot, result) {
    const ability = attacker.abilities[abilitySlot];
    const lines = [];
    
    if (result.success) {
        if (result.isCritical) {
            lines.push(`💥 **KRYTYK!** ${attacker.name} używa *${ability.name}*!`);
        } else {
            lines.push(`⚔️ ${attacker.name} używa *${ability.name}* na ${defender.name}.`);
        }
        lines.push(`> ${ability.lore}`);
        
        if (ability.type === 'CON_DMG') {
            const dmg = ability.damage || 1.0;
            lines.push(`🩸 ${defender.name} traci **${dmg} CON**. (Stan: ${defender.con.toFixed(1)}/${defender.maxCon})`);
        } else if (ability.type === 'DRAINLIFE') {
            lines.push(`🧛 ${defender.name} traci życie, a ${attacker.name} się regeneruje.`);
        } else if (['ROOT', 'STUN', 'SILENCE', 'DISARM'].includes(ability.type)) {
            lines.push(`⛓️ ${defender.name} zostaje objęty efektem **${ability.type}** na ${ability.duration} tur.`);
        } else if (ability.type === 'FEAR') {
            lines.push(`😱 ${defender.name} wpada w panikę!`);
        } else if (ability.type === 'HEAL') {
            lines.push(`💚 ${defender.name} zostaje uleczony.`);
        }
    } else {
        if (result.isCritical) {
            lines.push(`💨 **KRYTYCZNE PUDŁO!** ${attacker.name} próbuje *${ability.name}*, ale całkowicie chybia!`);
        } else {
            lines.push(`🛡️ ${attacker.name} używa *${ability.name}*, ale ${defender.name} unika ataku.`);
        }
        lines.push(`(Rzut: ${result.roll} vs ${result.hitChance}%)`);
    }
    
    return lines;
}

/**
 * Wykonuje jedną turę walki — AI wybiera akcje dla wszystkich jednostek.
 * @param {Object} combat - Stan walki
 * @returns {Object} { lines, combatOver, result }
 */
export function executeCombatRound(combat) {
    const lines = [];
    combat.round += 1;
    lines.push(`\n### === RUNDA ${combat.round} === ###`);
    
    // Zbierz wszystkie żywe jednostki
    const allUnits = [
        ...combat.playerParty.filter(u => isAlive(u)),
        ...combat.enemies.filter(u => isAlive(u))
    ];
    
    // Sortuj według Argos (na razie: losowo)
    const shuffled = [...allUnits].sort(() => Math.random() - 0.5);
    
    for (const unit of shuffled) {
        if (!isAlive(unit)) continue;
        
        // Wybierz cel
        let target = null;
        if (unit.isPlayer) {
            // Gracz atakuje wrogów
            const aliveEnemies = combat.enemies.filter(u => isAlive(u));
            if (aliveEnemies.length === 0) break;
            target = aliveEnemies[Math.floor(Math.random() * aliveEnemies.length)];
        } else {
            // Wróg atakuje drużynę gracza
            const aliveParty = combat.playerParty.filter(u => isAlive(u));
            if (aliveParty.length === 0) break;
            target = aliveParty[Math.floor(Math.random() * aliveParty.length)];
        }
        
        if (!target) continue;
        
        // Wybierz zdolność (na razie: losowa z A/B/C/D)
        const availableSlots = ['A', 'B', 'C', 'D'].filter(slot => {
            const cd = unit.cooldowns[slot] || 0;
            return cd === 0;
        });
        
        if (availableSlots.length === 0) {
            lines.push(`⏳ ${unit.name} nie ma dostępnych zdolności (wszystkie na cooldownie).`);
            continue;
        }
        
        const slot = availableSlots[Math.floor(Math.random() * availableSlots.length)];
        const ability = unit.abilities[slot];
        
        // Sprawdź czy zdolność ma sens (nie lecz wroga, nie atakuj sojusznika)
        if (['HEAL', 'RES_PROFILE_PHYS_SHIELD', 'RES_PROFILE_PHYS_PIERCE'].includes(ability.type)) {
            // Wsparcie — użyj na sobie lub sojuszniku
            // Na razie uprośczone: używamy na sobie
            target = unit;
        }
        
        // Rzut k100
        const roll = rollD100();
        const result = resolveAttack(unit, target, slot, roll, combat.biome);
        
        // Narracja
        const attackLines = narrateAttack(unit, target, slot, result);
        lines.push(...attackLines);
        
        // Aplikuj efekt
        if (result.success) {
            if (ability.type === 'CON_DMG') {
                const dmgResult = dealDamage(target, ability.damage || 1.0);
                if (dmgResult.died) {
                    lines.push(`💀 **${target.name} zostaje wyeliminowany!**`);
                }
            } else if (ability.type === 'DRAINLIFE') {
                dealDamage(target, ability.damage || 0.5);
                // Self heal (placeholder)
            } else if (ability.type === 'HEAL' && ability.value) {
                // Heal (placeholder)
            }
        }
        
        // Cooldown
        unit.cooldowns[slot] = (slot === 'A' || slot === 'C') ? 3 : 2;
        
        lines.push('');
    }
    
    // Tick cooldownów
    for (const unit of allUnits) {
        for (const slot of ['A', 'B', 'C', 'D']) {
            if (unit.cooldowns[slot] > 0) {
                unit.cooldowns[slot] -= 1;
            }
        }
    }
    
    // Sprawdź wynik walki
    const playerAlive = combat.playerParty.some(u => isAlive(u));
    const enemiesAlive = combat.enemies.some(u => isAlive(u));
    
    let combatOver = false;
    let result = null;
    
    if (!enemiesAlive) {
        lines.push(`\n🏆 **ZWYCIĘSTWO!** Wszyscy wrogowie pokonani!`);
        combatOver = true;
        result = 'victory';
    } else if (!playerAlive) {
        lines.push(`\n💀 **PORAŻKA!** Twoja drużyna została wyeliminowana...`);
        combatOver = true;
        result = 'defeat';
    }
    
    return { lines, combatOver, result };
}

/**
 * Generuje nagrody za zwycięstwo.
 */
export function getVictoryRewards(combat) {
    const renown = combat.enemies.length; // 1 renoma per wróg
    const mana = 1;
    
    // Szansa na rekrutację pokonanego wroga
    const recruitable = combat.enemies.length > 0 
        ? combat.enemies[Math.floor(Math.random() * combat.enemies.length)]
        : null;
    
    return { renown, mana, recruitable };
}
