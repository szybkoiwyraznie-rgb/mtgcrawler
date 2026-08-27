// src/data/card_registry.js
// Centralny rejestr wszystkich kart w grze
// Ładuje dane z cards.json (439 prawdziwych kart MTG)

/**
 * Rejestr wszystkich kart w grze.
 * Klucz = cardId, wartość = { raw, unit }
 */
export const CARD_REGISTRY = {};

let isLoaded = false;

/**
 * Ładuje karty z pliku JSON.
 * Musi być wywołane przed użyciem rejestru.
 */
export async function loadCards() {
    if (isLoaded) return;
    
    try {
        const response = await fetch('./src/data/cards.json');
        const cardsData = await response.json();
        
        // Załaduj wszystkie karty z JSON
        for (const card of cardsData) {
            // Stwórz strukturę raw (dane z bazy)
            const raw = {
                id: card.id,
                name: card.name,
                set: card.set,
                setting: card.setting,
                mv: card.mv,
                colors: card.colors,
                prompt: card.prompt,
                narrative: card.narrative
            };
            
            // Stwórz strukturę unit (dla gry)
            // Na razie używamy narrative jako bio
            const unit = {
                name: card.name,
                bio: card.narrative || card.prompt || 'Brak opisu.',
                cardId: card.id,
                // Domeny będą generowane dynamicznie na podstawie kolorów
                // Na razie placeholder
                domains: {
                    A: 'Ogień',
                    B: 'Woda',
                    C: 'Mag',
                    D: 'Kapłanka'
                },
                abilities: {
                    A: { name: 'Atak podstawowy', type: 'CON_DMG', damage: 1.0, range: 0 },
                    B: { name: 'Zdolność B', type: 'CON_DMG', damage: 0.5, range: 1 },
                    C: { name: 'Zdolność C', type: 'HEAL', value: 1, delay: 0 },
                    D: { name: 'Zdolność D', type: 'CON_DMG', damage: 0.5, range: 0 }
                }
            };
            
            CARD_REGISTRY[card.id] = { raw, unit };
        }
        
        isLoaded = true;
        console.log(`✅ Załadowano ${Object.keys(CARD_REGISTRY).length} kart z bazy`);
    } catch (error) {
        console.error('❌ Błąd ładowania kart:', error);
    }
}

/**
 * Zwraca listę wszystkich cardIds.
 */
export function getAllCardIds() {
    return Object.keys(CARD_REGISTRY);
}

/**
 * Zwraca dane karty po ID.
 */
export function getCard(cardId) {
    return CARD_REGISTRY[cardId] || null;
}

/**
 * Zwraca losową kartę z rejestru.
 */
export function getRandomCard() {
    const ids = getAllCardIds();
    const randomId = ids[Math.floor(Math.random() * ids.length)];
    return { id: randomId, ...CARD_REGISTRY[randomId] };
}

/**
 * Zwraca karty pasujące do biomu (na podstawie kolorów/domen).
 * Placeholder — w przyszłości bardziej zaawansowane filtrowanie.
 */
export function getCardsForBiome(biome) {
    // Na razie zwracamy wszystkie karty
    // W przyszłości: filtrowanie po kolorach, domenach, settingu
    return getAllCardIds().map(id => ({ id, ...CARD_REGISTRY[id] }));
}

/**
 * Zwraca liczbę kart w rejestrze.
 */
export function getCardCount() {
    return Object.keys(CARD_REGISTRY).length;
}
