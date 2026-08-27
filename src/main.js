// src/main.js
// Główny plik aplikacji — inicjalizacja, event loop, renderowanie

import { PHYSICAL_DOMAINS, TAROT_DOMAINS } from './engine/domains.js';
import { calculateDVA, resolveAttack, rollD100 } from './engine/dva.js';
import { BIOMES } from './engine/biomes.js';
import { createUnit } from './engine/unit.js';
import { generateWorld, saveWorld, loadWorld, hasSave, getBiomeAt, isDiscovered } from './game/world.js';
import { movePlayer } from './game/explorer.js';
import { createCombatState, executeCombatRound, getVictoryRewards } from './game/combat.js';
import { getAllCardIds, getCard, getCardCount, loadCards } from './data/card_registry.js';
import { initStats, loadStats, saveStats, updateStat, formatStats } from './game/stats.js';
import { getLocationAt, LOCATION_TYPES, applyLocationEffects } from './game/locations.js';
import * as Narrator from './game/narrator.js';

// === STAN APLIKACJI ===
let world = null;
let currentScreen = 'title'; // title, game, collection
let combatState = null; // Aktywna walka
let stats = loadStats(); // Statystyki gry
const CELL_SIZE = 20;
const VIEWPORT_SIZE = 15;

// === INICJALIZACJA ===

async function initGame() {
    console.log("🧙‍♂️ Mage's Journey v0.2 — ładowanie...");
    console.log(`📊 Domeny fizyczne: ${PHYSICAL_DOMAINS.length}`);
    console.log(`📊 Domeny tarota: ${TAROT_DOMAINS.length}`);
    console.log(`🗺️ Biomów: ${Object.keys(BIOMES).length}`);
    
    // Załaduj karty z bazy MTG
    await loadCards();
    console.log(`🃏 Kart w bazie: ${getCardCount()}`);
    
    // Sprawdź czy jest zapis gry
    if (hasSave()) {
        document.getElementById('btn-continue').disabled = false;
    }
    
    // === EVENT LISTENERY ===
    
    document.getElementById('btn-new-game').addEventListener('click', () => {
        world = generateWorld();
        switchScreen('game');
        startNewGame();
    });
    
    document.getElementById('btn-continue').addEventListener('click', () => {
        world = loadWorld();
        if (world) {
            switchScreen('game');
            resumeGame();
        }
    });
    
    document.getElementById('btn-collection').addEventListener('click', () => {
        switchScreen('collection');
        showCollection();
    });
    
    document.getElementById('btn-back-from-collection').addEventListener('click', () => {
        switchScreen('title');
    });
    
    document.getElementById('btn-save').addEventListener('click', () => {
        if (saveWorld(world)) {
            addLog("💾 Gra zapisana!");
        }
    });
    
    document.getElementById('btn-stats').addEventListener('click', () => {
        const overlay = document.getElementById('encounter-overlay');
        const title = document.getElementById('encounter-title');
        const content = document.getElementById('encounter-content');
        const actions = document.getElementById('encounter-actions');
        
        title.textContent = '📊 Statystyki Podróży';
        content.innerHTML = `<pre style="font-family: var(--font-ui); line-height: 1.8; color: var(--text-primary);">${formatStats(stats)}</pre>`;
        actions.innerHTML = `<button class="btn-primary" onclick="window.gameActions.closeEncounter()">Zamknij</button>`;
        overlay.classList.remove('hidden');
    });
    
    document.getElementById('btn-menu').addEventListener('click', () => {
        if (confirm("Wrócić do menu głównego? (niezapisane zmiany przepadną)")) {
            switchScreen('title');
        }
    });
    
    // Kliknięcie na mapę
    document.getElementById('game-map').addEventListener('click', handleMapClick);
    document.getElementById('game-map').addEventListener('mousemove', handleMapHover);
    
    console.log("✅ Aplikacja załadowana! Czekam na wybór gracza...");
}

// Tooltip
let mapTooltip = null;
function ensureTooltip() {
    if (mapTooltip) return mapTooltip;
    mapTooltip = document.createElement('div');
    mapTooltip.id = 'map-tooltip';
    mapTooltip.style.cssText = 'position:fixed; background:#141420; border:1px solid #c9a84c; color:#e8e6e3; padding:4px 8px; font-size:0.8rem; border-radius:4px; pointer-events:none; z-index:50; display:none; font-family:var(--font-ui);';
    document.body.appendChild(mapTooltip);
    return mapTooltip;
}

function handleMapHover(event) {
    if (!world) return;
    const canvas = document.getElementById('game-map');
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clickX = (event.clientX - rect.left) * scaleX;
    const clickY = (event.clientY - rect.top) * scaleY;
    
    const halfView = Math.floor(VIEWPORT_SIZE / 2);
    const startX = Math.max(0, Math.min(world.player.x - halfView, 30 - VIEWPORT_SIZE));
    const startY = Math.max(0, Math.min(world.player.y - halfView, 30 - VIEWPORT_SIZE));
    
    const cellW = canvas.width / VIEWPORT_SIZE;
    const cellH = canvas.height / VIEWPORT_SIZE;
    const vx = Math.floor(clickX / cellW);
    const vy = Math.floor(clickY / cellH);
    const worldX = startX + vx;
    const worldY = startY + vy;
    
    const tooltip = ensureTooltip();
    
    if (isDiscovered(world, worldX, worldY)) {
        const biome = getBiomeAt(world, worldX, worldY);
        if (biome) {
            tooltip.textContent = `${biome.name} [${worldX},${worldY}]`;
            tooltip.style.display = 'block';
            tooltip.style.left = (event.clientX + 12) + 'px';
            tooltip.style.top = (event.clientY + 12) + 'px';
            return;
        }
    }
    tooltip.style.display = 'none';
}

// === FUNKCJE EKRANÓW ===

function switchScreen(screen) {
    document.getElementById('title-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('collection-screen').classList.add('hidden');
    
    switch (screen) {
        case 'title':
            document.getElementById('title-screen').classList.remove('hidden');
            break;
        case 'game':
            document.getElementById('game-screen').classList.remove('hidden');
            break;
        case 'collection':
            document.getElementById('collection-screen').classList.remove('hidden');
            break;
    }
    
    currentScreen = screen;
}

// === GRA ===

function startNewGame() {
    clearLog();
    addLog("🎮 Nowa gra rozpoczęta!");
    addLog("🧙‍♂️ Budzisz się w nieznanej krainie. Jesteś Magiem — władcą many i przyzywaczem potworów.");
    addLog("🗺️ Kliknij na sąsiednie pole na mapie, aby się poruszyć.");
    addLog("");
    
    updateHUD();
    drawMap();
    saveWorld(world);
}

function resumeGame() {
    clearLog();
    addLog("📂 Gra wznowiona!");
    addLog(`🧙‍♂️ Tura ${world.turn}. Kontynuujesz swoją wędrówkę.`);
    addLog("");
    
    updateHUD();
    drawMap();
}

// === RENDEROWANIE MAPY ===

function drawMap() {
    const canvas = document.getElementById('game-map');
    const ctx = canvas.getContext('2d');
    
    // Wyczyść canvas
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Oblicz viewport (środek na graczu)
    const halfView = Math.floor(VIEWPORT_SIZE / 2);
    const startX = Math.max(0, Math.min(world.player.x - halfView, 30 - VIEWPORT_SIZE));
    const startY = Math.max(0, Math.min(world.player.y - halfView, 30 - VIEWPORT_SIZE));
    
    const cellW = canvas.width / VIEWPORT_SIZE;
    const cellH = canvas.height / VIEWPORT_SIZE;
    
    // Rysuj mapę
    for (let vy = 0; vy < VIEWPORT_SIZE; vy++) {
        for (let vx = 0; vx < VIEWPORT_SIZE; vx++) {
            const wx = startX + vx; // World X
            const wy = startY + vy; // World Y
            
            const px = vx * cellW;
            const py = vy * cellH;
            
            if (isDiscovered(world, wx, wy)) {
                // Odkryte pole — pokaż biom
                const biome = getBiomeAt(world, wx, wy);
                ctx.fillStyle = biome ? biome.color : '#333';
                ctx.fillRect(px, py, cellW, cellH);
                
                // Subtelna siatka
                ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                ctx.strokeRect(px, py, cellW, cellH);
            } else {
                // Nieodkryte — czarne
                ctx.fillStyle = '#0a0a0f';
                ctx.fillRect(px, py, cellW, cellH);
                ctx.strokeStyle = '#1a1a2a';
                ctx.strokeRect(px, py, cellW, cellH);
            }
        }
    }
    
    // Rysuj gracza
    const playerVX = world.player.x - startX;
    const playerVY = world.player.y - startY;
    
    if (playerVX >= 0 && playerVX < VIEWPORT_SIZE && playerVY >= 0 && playerVY < VIEWPORT_SIZE) {
        const px = playerVX * cellW + cellW / 2;
        const py = playerVY * cellH + cellH / 2;
        
        // Podświetlenie pola gracza
        ctx.fillStyle = 'rgba(201, 168, 76, 0.3)';
        ctx.fillRect(playerVX * cellW, playerVY * cellH, cellW, cellH);
        
        // Ikona gracza
        ctx.font = `${Math.floor(cellW * 0.7)}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🧙‍♂️', px, py);
    }
    
    // Rysuj specjalne lokacje
    if (world.specialLocations) {
        for (const loc of world.specialLocations) {
            if (!isDiscovered(world, loc.x, loc.y)) continue;
            
            const lvx = loc.x - startX;
            const lvy = loc.y - startY;
            
            if (lvx >= 0 && lvx < VIEWPORT_SIZE && lvy >= 0 && lvy < VIEWPORT_SIZE) {
                const locType = Object.values(LOCATION_TYPES).find(t => t.id === loc.type);
                if (locType) {
                    const px = lvx * cellW + cellW / 2;
                    const py = lvy * cellH + cellH / 2;
                    ctx.font = `${Math.floor(cellW * 0.6)}px serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(locType.icon, px, py);
                }
            }
        }
    }
    
    // Rysuj sąsiednie pola jako klikalne (podświetlone)
    const neighborOffsets = [
        [-1, -1], [0, -1], [1, -1],
        [-1,  0],          [1,  0],
        [-1,  1], [0,  1], [1,  1]
    ];
    
    for (const [dx, dy] of neighborOffsets) {
        const nx = world.player.x + dx;
        const ny = world.player.y + dy;
        const nvx = nx - startX;
        const nvy = ny - startY;
        
        if (nvx >= 0 && nvx < VIEWPORT_SIZE && nvy >= 0 && nvy < VIEWPORT_SIZE) {
            ctx.strokeStyle = 'rgba(201, 168, 76, 0.6)';
            ctx.lineWidth = 2;
            ctx.strokeRect(nvx * cellW + 1, nvy * cellH + 1, cellW - 2, cellH - 2);
            ctx.lineWidth = 1;
        }
    }
}

// === KLIKNIĘCIE NA MAPĘ ===

function handleMapClick(event) {
    const canvas = document.getElementById('game-map');
    const rect = canvas.getBoundingClientRect();
    
    // Skalowanie kliknięcia do canvas
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const clickX = (event.clientX - rect.left) * scaleX;
    const clickY = (event.clientY - rect.top) * scaleY;
    
    // Oblicz viewport
    const halfView = Math.floor(VIEWPORT_SIZE / 2);
    const startX = Math.max(0, Math.min(world.player.x - halfView, 30 - VIEWPORT_SIZE));
    const startY = Math.max(0, Math.min(world.player.y - halfView, 30 - VIEWPORT_SIZE));
    
    const cellW = canvas.width / VIEWPORT_SIZE;
    const cellH = canvas.height / VIEWPORT_SIZE;
    
    // Która komórka?
    const vx = Math.floor(clickX / cellW);
    const vy = Math.floor(clickY / cellH);
    
    const worldX = startX + vx;
    const worldY = startY + vy;
    
    // Oblicz dx, dy względem gracza
    const dx = worldX - world.player.x;
    const dy = worldY - world.player.y;
    
    // Sprawdź czy to sąsiednie pole
    if (Math.abs(dx) <= 1 && Math.abs(dy) <= 1 && (dx !== 0 || dy !== 0)) {
        performMove(dx, dy);
    }
}

function performMove(dx, dy) {
    const prevX = world.player.x;
    const prevY = world.player.y;
    const wasDiscovered = isDiscovered(world, prevX + dx, prevY + dy);
    
    const result = movePlayer(world, dx, dy);
    
    if (result.success) {
        // Statystyki: nowe odkryte pole
        if (!wasDiscovered) {
            stats = updateStat(stats, 'tilesDiscovered');
        }
        
        // Wyświetl logi
        for (const msg of result.log) {
            addLog(msg);
        }
        
        // Sprawdź specjalną lokację
        if (world.specialLocations) {
            const location = getLocationAt(world.specialLocations, world.player.x, world.player.y);
            if (location && !location.discovered) {
                location.discovered = true;
                const locType = Object.values(LOCATION_TYPES).find(t => t.id === location.type);
                if (locType) {
                    addLog(`${locType.icon} Odkrywasz: **${locType.name}**!`);
                    addLog(`📜 ${locType.description}`);
                    
                    // Aplikuj efekty
                    const effectsLog = applyLocationEffects(world, locType);
                    for (const msg of effectsLog) {
                        addLog(msg);
                    }
                }
            }
        }
        
        // Obsłuż encounter
        if (result.encounter) {
            showEncounter(result.encounter);
            
            // Statystyki encounterów
            switch (result.encounter.type) {
                case "TRAP":
                    stats = updateStat(stats, 'trapsTriggered');
                    break;
                case "TREASURE":
                    stats = updateStat(stats, 'treasuresFound');
                    break;
            }
        }
        
        // Aktualizuj max renown
        if (world.player.renown > stats.maxRenown) {
            stats.maxRenown = world.player.renown;
            saveStats(stats);
        }
        
        // Aktualizuj UI
        updateHUD();
        drawMap();
        
        // Auto-zapis
        saveWorld(world);
    } else {
        for (const msg of result.log) {
            addLog(msg);
        }
    }
}

// === ENCOUNTER OVERLAY ===

function showEncounter(encounter) {
    window._currentEncounter = encounter; // Zapisz dla gameActions
    const overlay = document.getElementById('encounter-overlay');
    const title = document.getElementById('encounter-title');
    const content = document.getElementById('encounter-content');
    const actions = document.getElementById('encounter-actions');
    
    title.textContent = encounter.label;
    content.innerHTML = `<p>${encounter.description}</p>`;
    actions.innerHTML = '';
    
    switch (encounter.type) {
        case "COMBAT": {
            // Pokaż listę wrogów
            const enemiesList = encounter.enemies.map(e => 
                `<div class="enemy-card"><strong>${e.name}</strong><br>
                <span class="enemy-domains">${e.domains.A}/${e.domains.B} | ${e.domains.C}/${e.domains.D}</span></div>`
            ).join('');
            content.innerHTML += `<div class="enemies-list">${enemiesList}</div>`;
            actions.innerHTML = `
                <button class="btn-primary" onclick="window.gameActions.startCombat()">⚔️ Do walki!</button>
                <button class="btn-secondary" onclick="window.gameActions.flee()">🏃 Uciekaj (tracisz 1 manę)</button>
            `;
            break;
        }
        
        case "NEUTRAL": {
            const card = encounter.creature;
            if (card) {
                content.innerHTML += `
                    <div class="enemy-card" style="border-color: var(--accent-green);">
                        <strong>${card.unit.name}</strong><br>
                        <span class="enemy-domains">${card.unit.domains.A}/${card.unit.domains.B} | ${card.unit.domains.C}/${card.unit.domains.D}</span><br>
                        <em style="font-size: 0.9rem; color: var(--text-secondary);">${card.unit.bio}</em>
                    </div>
                `;
            }
            actions.innerHTML = `
                <button class="btn-primary" onclick="window.gameActions.recruitNeutral('${card ? card.id : ''}', ${encounter.recruitCost})">🤝 Zwerbuj (${encounter.recruitCost} many)</button>
                <button class="btn-secondary" onclick="window.gameActions.dismiss()">👋 Odejdź</button>
            `;
            break;
        }
        
        case "TRAP":
            world.player.mana = Math.max(0, world.player.mana - 1);
            addLog("💔 Tracisz 1 manę od pułapki!");
            actions.innerHTML = `
                <button class="btn-primary" onclick="window.gameActions.closeEncounter()">Kontynuuj</button>
            `;
            break;
        
        case "TREASURE":
            world.player.mana = Math.min(world.player.maxMana, world.player.mana + encounter.reward.mana);
            addLog(`✨ Zyskujesz ${encounter.reward.mana} many!`);
            actions.innerHTML = `
                <button class="btn-primary" onclick="window.gameActions.closeEncounter()">Kontynuuj</button>
            `;
            break;
        
        case "STORY":
            actions.innerHTML = `
                <button class="btn-primary" onclick="window.gameActions.closeEncounter()">Kontynuuj wędrówkę</button>
            `;
            break;
    }
    
    overlay.classList.remove('hidden');
    updateHUD();
}

// Globalne akcje (dla onclick w HTML)
window.gameActions = {
    startCombat() {
        const encounter = window._currentEncounter;
        if (!encounter || encounter.type !== 'COMBAT') return;
        
        // Stwórz drużynę gracza (na razie: dummy party z materialem)
        const playerParty = [];
        if (world.party.length === 0) {
            // Daj graczowi jednego defaultowego potwora do walki
            const card = getCard('1LTR');
            if (card) {
                playerParty.push(createUnit({
                    name: card.unit.name,
                    bio: card.unit.bio,
                    cardId: card.id,
                    domains: card.unit.domains,
                    abilities: card.unit.abilities
                }));
            }
        } else {
            // Użyj potworów z drużyny
            for (const p of world.party) {
                if (p.cardId) {
                    const card = getCard(p.cardId);
                    if (card) {
                        playerParty.push(createUnit({
                            name: card.unit.name,
                            bio: card.unit.bio,
                            cardId: card.id,
                            domains: card.unit.domains,
                            abilities: card.unit.abilities
                        }));
                    }
                }
            }
        }
        
        // Inicjalizuj walkę
        combatState = createCombatState(playerParty, encounter.enemies, encounter.biomeId);
        
        const biome = encounter.biomeId ? BIOMES[encounter.biomeId] : null;
        addLog(Narrator.narrateCombatStart(playerParty, encounter.enemies, biome));
        addLog(`Przeciwnicy: ${encounter.enemies.map(e => e.name).join(', ')}`);
        
        // Pokaż ekran walki
        this.showCombatScreen();
    },
    
    showCombatScreen() {
        if (!combatState) return;
        
        const result = executeCombatRound(combatState);
        
        // Loguj wynik rundy
        for (const line of result.lines) {
            addLog(line);
        }
        
        if (result.combatOver) {
            if (result.result === 'victory') {
                const rewards = getVictoryRewards(combatState);
                world.player.renown += rewards.renown;
                world.player.mana = Math.min(world.player.maxMana, world.player.mana + rewards.mana);
                addLog(`🏆 Nagrody: +${rewards.renown} renomy, +${rewards.mana} many`);
                
                // Statystyki
                stats = updateStat(stats, 'battlesWon');
                stats = updateStat(stats, 'monstersDefeated', combatState.enemies.length);
                stats.currentStreak += 1;
                if (stats.currentStreak > stats.longestStreak) {
                    stats.longestStreak = stats.currentStreak;
                }
                saveStats(stats);
                
                // Opcja rekrutacji
                if (rewards.recruitable && world.party.length < world.maxPartySize) {
                    this.showRecruitOption(rewards.recruitable);
                    return;
                }
            } else {
                addLog("💀 Twoja drużyna padła... Gra kończy się.");
                stats = updateStat(stats, 'battlesLost');
                stats.currentStreak = 0;
                saveStats(stats);
            }
            
            combatState = null;
            this.closeEncounter();
        } else {
            // Kontynuuj walkę
            addLog(`--- Koniec rundy ${combatState.round} ---`);
            // Automatycznie wykonaj następną rundę po krótkim opóźnieniu
            setTimeout(() => this.showCombatScreen(), 1500);
        }
    },
    
    showRecruitOption(enemy) {
        const overlay = document.getElementById('encounter-overlay');
        const title = document.getElementById('encounter-title');
        const content = document.getElementById('encounter-content');
        const actions = document.getElementById('encounter-actions');
        
        title.textContent = '🤝 Opcja rekrutacji';
        content.innerHTML = `
            <p>Pokonany **${enemy.name}** leży u Twoich stóp. Możesz go zwerbować do drużyny.</p>
            <p><strong>Domeny:</strong> ${enemy.domains.A}/${enemy.domains.B} | ${enemy.domains.C}/${enemy.domains.D}</p>
            <p><em>${enemy.bio}</em></p>
        `;
        actions.innerHTML = `
            <button class="btn-primary" onclick="window.gameActions.recruitDefeated('${enemy.cardId}', 3)">🤝 Zwerbuj (3 many)</button>
            <button class="btn-secondary" onclick="window.gameActions.closeEncounter()">Odejdź</button>
        `;
        overlay.classList.remove('hidden');
    },
    
    recruitDefeated(cardId, cost) {
        if (world.player.mana >= cost && world.party.length < world.maxPartySize) {
            world.player.mana -= cost;
            const card = getCard(cardId);
            if (card) {
                world.party.push({
                    name: card.unit.name,
                    cardId: cardId,
                    con: 5
                });
                addLog(`🤝 ${card.unit.name} dołącza do Twojej drużyny!`);
            }
        } else if (world.player.mana < cost) {
            addLog("❌ Za mało many!");
            return;
        } else {
            addLog("❌ Drużyna pełna!");
            return;
        }
        this.closeEncounter();
    },
    
    flee() {
        if (world.player.mana > 0) {
            world.player.mana -= 1;
            addLog("🏃 Uciekasz z pola walki, tracąc 1 manę!");
        } else {
            addLog("🏃 Uciekasz z pola walki!");
        }
        this.closeEncounter();
    },
    
    recruit(cost) {
        // Legacy - nieużywane
        addLog("❌ Ta opcja nie jest już dostępna.");
        this.closeEncounter();
    },
    
    recruitNeutral(cardId, cost) {
        if (!cardId) {
            addLog("❌ Brak karty do rekrutacji.");
            this.closeEncounter();
            return;
        }
        if (world.player.mana >= cost && world.party.length < world.maxPartySize) {
            world.player.mana -= cost;
            const card = getCard(cardId);
            if (card) {
                world.party.push({
                    name: card.unit.name,
                    cardId: cardId,
                    con: 5
                });
                addLog(Narrator.narrateRecruitment(card.unit));
                addLog(`> ${card.unit.bio}`);
                stats = updateStat(stats, 'monstersRecruited');
                if (world.party.length > stats.maxPartySize) {
                    stats.maxPartySize = world.party.length;
                }
                saveStats(stats);
            }
        } else if (world.player.mana < cost) {
            addLog("❌ Za mało many!");
            return;
        } else {
            addLog("❌ Drużyna pełna!");
            return;
        }
        this.closeEncounter();
    },
    
    dismiss() {
        addLog("👋 Odchodzisz bez rekrutacji.");
        this.closeEncounter();
    },
    
    closeEncounter() {
        document.getElementById('encounter-overlay').classList.add('hidden');
        updateHUD();
        drawMap();
        saveWorld(world);
    }
};

// === HUD ===

function updateHUD() {
    if (!world) return;
    
    document.getElementById('mage-mana').textContent = `${world.player.mana}/${world.player.maxMana}`;
    document.getElementById('mage-renown').textContent = world.player.renown;
    document.getElementById('mage-party').textContent = `${world.party.length}/${world.maxPartySize}`;
    document.getElementById('mage-turn').textContent = world.turn;
    
    // Aktualizuj sloty drużyny
    const slots = document.getElementById('party-slots');
    slots.innerHTML = '';
    
    for (let i = 0; i < world.maxPartySize; i++) {
        if (world.party[i]) {
            const partyMember = world.party[i];
            const card = partyMember.cardId ? getCard(partyMember.cardId) : null;
            const domains = card ? `${card.unit.domains.A}/${card.unit.domains.B} | ${card.unit.domains.C}/${card.unit.domains.D}` : '???';
            slots.innerHTML += `
                <div class="party-slot filled">
                    <strong>${partyMember.name}</strong>
                    <span class="party-domains">${domains}</span>
                    <span class="party-con">CON: ${partyMember.con}/5</span>
                </div>
            `;
        } else {
            slots.innerHTML += `<div class="party-slot empty">Pusty slot</div>`;
        }
    }
}

// === LOG ===

function addLog(text) {
    const log = document.getElementById('log-entries');
    if (!log) return;
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = text;
    log.prepend(entry);
    
    // Ogranicz do 50 wpisów
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

function clearLog() {
    const log = document.getElementById('log-entries');
    if (log) log.innerHTML = '';
}

// === KOLEKCJA ===

function showCollection() {
    const grid = document.getElementById('card-grid');
    const cardIds = getAllCardIds();
    
    let html = `<p style="grid-column: 1/-1; color: var(--text-secondary); margin-bottom: 1rem;">
        📊 Kart w kolekcji: <strong>${getCardCount()}</strong> / 400 (docelowo)
    </p>`;
    
    for (const cardId of cardIds) {
        const card = getCard(cardId);
        if (!card) continue;
        
        html += `
        <div class="card-preview">
            <h3>${card.unit.name}</h3>
            <p class="card-meta">ID: ${card.raw.id} | Set: ${card.raw.set} | Setting: ${card.raw.setting} | MV: ${card.raw.mv} | Colors: ${card.raw.colors.join(', ')}</p>
            <p class="card-bio">${card.unit.bio}</p>
            <div class="card-domains">
                <span class="domain phys">${card.unit.domains.A}</span>
                <span class="domain phys">${card.unit.domains.B}</span>
                <span class="domain tarot">${card.unit.domains.C}</span>
                <span class="domain tarot">${card.unit.domains.D}</span>
            </div>
            <div class="card-abilities">
                ${Object.entries(card.unit.abilities).map(([slot, ab]) => `
                    <div class="ability">
                        <strong>[${slot}] ${ab.name}</strong> <span class="ability-type">(${ab.type})</span>
                        <p>${ab.lore}</p>
                    </div>
                `).join('')}
            </div>
        </div>`;
    }
    
    grid.innerHTML = html;
}

// === INIT ===

// Uruchom grę po załadowaniu DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGame);
} else {
    initGame();
}
