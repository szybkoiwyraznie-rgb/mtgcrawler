// src/game/stats.js
// System statystyk i osiągnięć

const STATS_KEY = 'mages_journey_stats';

/**
 * Inicjalizuje statystyki.
 */
export function initStats() {
    return {
        tilesDiscovered: 0,
        battlesWon: 0,
        battlesLost: 0,
        monstersRecruited: 0,
        monstersDefeated: 0,
        trapsTriggered: 0,
        treasuresFound: 0,
        maxPartySize: 0,
        maxRenown: 0,
        longestStreak: 0, // Najdłuższa seria bez porażki
        currentStreak: 0
    };
}

/**
 * Zapisuje statystyki.
 */
export function saveStats(stats) {
    try {
        localStorage.setItem(STATS_KEY, JSON.stringify(stats));
    } catch (e) {
        console.error('Błąd zapisu statystyk:', e);
    }
}

/**
 * Ładuje statystyki.
 */
export function loadStats() {
    try {
        const data = localStorage.getItem(STATS_KEY);
        if (data) return JSON.parse(data);
    } catch (e) {
        console.error('Błąd ładowania statystyk:', e);
    }
    return initStats();
}

/**
 * Aktualizuje statystykę.
 */
export function updateStat(stats, key, value = 1) {
    if (stats[key] !== undefined) {
        stats[key] += value;
    }
    saveStats(stats);
    return stats;
}

/**
 * Formatuje statystyki do wyświetlenia.
 */
export function formatStats(stats) {
    return [
        `🗺️ Odkryte pola: ${stats.tilesDiscovered}`,
        `⚔️ Wygrane walki: ${stats.battlesWon}`,
        `💀 Przegrane walki: ${stats.battlesLost}`,
        `🤝 Zrekrutowani sojusznicy: ${stats.monstersRecruited}`,
        `🏆 Pokonani wrogowie: ${stats.monstersDefeated}`,
        `⚠️ Aktywowane pułapki: ${stats.trapsTriggered}`,
        `💎 Znalezione skarby: ${stats.treasuresFound}`,
        `🌟 Najwyższa renoma: ${stats.maxRenown}`,
        `🔥 Najdłuższa seria: ${stats.longestStreak} zwycięstw`
    ].join('\n');
}
