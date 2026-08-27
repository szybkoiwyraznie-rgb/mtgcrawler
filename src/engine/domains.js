// src/engine/domains.js
// Domeny i macierze wpływu — port z Monster Engine 6.0

// === DOMENY FIZYCZNE (12 żywiołów) ===
export const PHYSICAL_DOMAINS = [
    "Ogień", "Woda", "Ziemia", "Powietrze", "Metal", "Elektryczność",
    "Lód", "Natura", "Światło", "Mrok", "Eter", "Zaraza"
];

// === DOMENY NIEFIZYCZNE (12 Wielkich Arkanów) ===
export const TAROT_DOMAINS = [
    "Mag", "Kapłanka", "Cesarz", "Kochankowie", "Rydwan", "Sprawiedliwość",
    "Pustelnik", "Koło Fortuny", "Wisielec", "Śmierć", "Diabeł", "Wieża"
];

// === MACIERZ FIZYCZNA 12×12 ===
// Wiersze = atakujący, Kolumny = obrońca
// Kolejność kolumn zgodna z PHYSICAL_DOMAINS
// Wartości = SSO (Sumaryczna Szansa Obrony) w %
export const PHYSICAL_MATRIX = {
    "Ogień":         [90, 90, 50, 40, 30, 50, 20, 10, 50, 50, 80, 40],
    "Woda":          [10, 90, 40, 50, 60, 90, 70, 60, 50, 40, 50, 50],
    "Ziemia":        [50, 60, 90, 90, 40, 10, 50, 70, 50, 50, 50, 50],
    "Powietrze":     [60, 50, 10, 90, 80, 50, 50, 40, 50, 50, 40, 50],
    "Metal":         [70, 40, 60, 20, 90, 80, 20, 30, 50, 10, 90, 90],
    "Elektryczność": [50, 10, 90, 50, 20, 90, 50, 50, 50, 50, 40, 50],
    "Lód":           [80, 30, 50, 80, 80, 50, 90, 40, 50, 50, 50, 50],
    "Natura":        [90, 40, 30, 60, 70, 50, 60, 90, 40, 60, 10, 80],
    "Światło":       [50, 50, 50, 50, 50, 50, 50, 60, 90, 10, 10, 90],
    "Mrok":          [50, 60, 50, 50, 90, 50, 50, 40, 10, 90, 30, 30],
    "Eter":          [20, 50, 50, 60, 10, 60, 50, 90, 90, 70, 90, 50],
    "Zaraza":        [60, 50, 50, 50, 10, 50, 50, 20, 10, 70, 50, 90]
};

// === MACIERZ TAROTA 12×12 ===
// Kolejność kolumn zgodna z TAROT_DOMAINS
export const TAROT_MATRIX = {
    "Mag":            [90, 30, 40, 50, 60, 50, 10, 50, 20, 50, 50, 90],
    "Kapłanka":       [10, 90, 50, 50, 50, 50, 80, 40, 60, 40, 10, 50],
    "Cesarz":         [60, 50, 90, 10, 40, 90, 50, 70, 30, 50, 50, 90],
    "Kochankowie":    [50, 50, 90, 90, 50, 10, 50, 40, 50, 80, 20, 50],
    "Rydwan":         [40, 50, 60, 50, 90, 60, 50, 90, 10, 40, 50, 80],
    "Sprawiedliwość": [50, 50, 10, 90, 40, 90, 50, 30, 90, 20, 70, 10],
    "Pustelnik":      [90, 20, 50, 50, 50, 50, 90, 10, 50, 90, 60, 50],
    "Koło Fortuny":   [50, 60, 30, 60, 10, 70, 90, 90, 40, 10, 50, 30],
    "Wisielec":       [80, 40, 70, 50, 90, 10, 50, 60, 90, 50, 10, 50],
    "Śmierć":         [50, 60, 50, 10, 60, 80, 10, 90, 50, 90, 50, 40],
    "Diabeł":         [50, 90, 50, 80, 50, 30, 40, 50, 90, 50, 90, 20],
    "Wieża":          [10, 50, 10, 50, 20, 90, 50, 70, 50, 60, 80, 90]
};

// === DOMENY PRZECIWSTAWNE ===
export const PHYSICAL_OPPOSITES = {
    "Ogień": "Woda",        "Woda": "Ogień",
    "Ziemia": "Powietrze",  "Powietrze": "Ziemia",
    "Metal": "Natura",      "Natura": "Metal",
    "Elektryczność": "Lód", "Lód": "Elektryczność",
    "Światło": "Mrok",      "Mrok": "Światło",
    "Eter": "Zaraza",       "Zaraza": "Eter"
};

export const TAROT_OPPOSITES = {
    "Mag": "Wieża",               "Wieża": "Mag",
    "Kapłanka": "Diabeł",         "Diabeł": "Kapłanka",
    "Cesarz": "Kochankowie",      "Kochankowie": "Cesarz",
    "Rydwan": "Wisielec",         "Wisielec": "Rydwan",
    "Sprawiedliwość": "Koło Fortuny", "Koło Fortuny": "Sprawiedliwość",
    "Pustelnik": "Śmierć",        "Śmierć": "Pustelnik"
};

/**
 * Pobiera wartość obrony z macierzy.
 * @param {string} attackDomain - Domena atakującego
 * @param {string} defenseDomain - Domena obrońcy
 * @param {boolean} isPhysical - true = macierz fizyczna, false = tarot
 * @returns {number} Szansa obrony (10-90)
 */
export function getDefenseValue(attackDomain, defenseDomain, isPhysical) {
    const matrix = isPhysical ? PHYSICAL_MATRIX : TAROT_MATRIX;
    const domainList = isPhysical ? PHYSICAL_DOMAINS : TAROT_DOMAINS;
    
    if (!(attackDomain in matrix)) return 50;
    
    const defIndex = domainList.indexOf(defenseDomain);
    if (defIndex === -1) return 50;
    
    return matrix[attackDomain][defIndex];
}

/**
 * Zwraca domenę przeciwstawną.
 * @param {string} domain
 * @returns {string|null}
 */
export function getOppositeDomain(domain) {
    return PHYSICAL_OPPOSITES[domain] || TAROT_OPPOSITES[domain] || null;
}

/**
 * Sprawdza czy domena jest fizyczna.
 * @param {string} domain
 * @returns {boolean}
 */
export function isPhysicalDomain(domain) {
    return PHYSICAL_DOMAINS.includes(domain);
}

/**
 * Sprawdza czy domena jest niefizyczna (tarot).
 * @param {string} domain
 * @returns {boolean}
 */
export function isTarotDomain(domain) {
    return TAROT_DOMAINS.includes(domain);
}
