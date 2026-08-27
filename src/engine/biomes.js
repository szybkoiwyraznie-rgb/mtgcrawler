// src/engine/biomes.js
// Biomy i ich modyfikatory — port z Monster Engine 6.0

/**
 * 15 typów biomów lądowych.
 * Każde pole mapy ma przypisany biom, który modyfikuje BAC zdolności.
 *
 * bonus_20  → +20% BAC dla tej domeny
 * penalty_20 → -20% BAC dla tej domeny
 * bonus_10  → +10% BAC dla tych domen
 * penalty_10 → -10% BAC dla tych domen
 */
export const BIOMES = {
    "L01": {
        name: "Łąki",
        color: "#76c893",
        bonus_20: "Natura",
        penalty_20: "Mrok",
        bonus_10: ["Światło"],
        penalty_10: [],
        description: "Rozległe, falujące łąki porośnięte dzikimi kwiatami i wysokimi trawami."
    },
    "L02": {
        name: "Las (Rzadki)",
        color: "#52b788",
        bonus_20: "Natura",
        penalty_20: "Ogień",
        bonus_10: ["Powietrze"],
        penalty_10: [],
        description: "Świetlisty las z wysokimi drzewami, między którymi swobodnie przepływa wiatr."
    },
    "L03": {
        name: "Las (Gęsty)",
        color: "#2d6a4f",
        bonus_20: "Natura",
        penalty_20: "Metal",
        bonus_10: ["Mrok"],
        penalty_10: ["Powietrze"],
        description: "Gęsta, mroczna puszcza. Korony drzew splatają się, blokując niemal całe światło."
    },
    "L04": {
        name: "Dżungla",
        color: "#1b4332",
        bonus_20: "Zaraza",
        penalty_20: "Lód",
        bonus_10: ["Natura"],
        penalty_10: ["Metal"],
        description: "Parująca wilgocią dżungla. Każda powierzchnia porośnięta jest mchem i lianami."
    },
    "L05": {
        name: "Pogórze",
        color: "#a5a58d",
        bonus_20: "Ziemia",
        penalty_20: "Powietrze",
        bonus_10: ["Metal"],
        penalty_10: ["Woda"],
        description: "Skaliste, zarośnięte wzgórza z licznymi jaskiniami i wychodniami skał."
    },
    "L06": {
        name: "Wysokie Góry",
        color: "#ced4da",
        bonus_20: "Powietrze",
        penalty_20: "Ziemia",
        bonus_10: ["Elektryczność", "Lód"],
        penalty_10: [],
        description: "Ośnieżone szczyty i ostre grzbiety. Wiatr wieje tu z siłą, która zwala z nóg."
    },
    "L07": {
        name: "Bagna",
        color: "#6c757d",
        bonus_20: "Woda",
        penalty_20: "Ogień",
        bonus_10: ["Zaraza"],
        penalty_10: ["Powietrze"],
        description: "Ciemne, cuchnące bagna. Gaz błędny tańczy nad powierzchnią mulistej wody."
    },
    "L08": {
        name: "Moczary",
        color: "#495057",
        bonus_20: "Mrok",
        penalty_20: "Światło",
        bonus_10: ["Zaraza", "Woda"],
        penalty_10: [],
        description: "Ponure moczary spowite wieczną mgłą. Nic tu nie rośnie, nic tu nie żyje długo."
    },
    "L09": {
        name: "Step",
        color: "#ddb892",
        bonus_20: "Powietrze",
        penalty_20: "Ziemia",
        bonus_10: ["Ogień"],
        penalty_10: [],
        description: "Bezkresny, suchy step. Trawy falują jak morze pod nieustającym wiatrem."
    },
    "L10": {
        name: "Pustynia",
        color: "#faedcd",
        bonus_20: "Ogień",
        penalty_20: "Woda",
        bonus_10: ["Światło", "Ziemia"],
        penalty_10: [],
        description: "Żar lejący się z nieba i piasek po horyzont. Życie tu to akt desperacji."
    },
    "L11": {
        name: "Lądolód",
        color: "#e0fbfc",
        bonus_20: "Lód",
        penalty_20: "Ogień",
        bonus_10: ["Woda"],
        penalty_10: ["Natura"],
        description: "Nieskończona tafla lodu. Mróz przeszywa kości, a cisza jest absolutna."
    },
    "L12": {
        name: "Pustynia Bazaltowa",
        color: "#343a40",
        bonus_20: "Metal",
        penalty_20: "Natura",
        bonus_10: ["Ogień", "Ziemia"],
        penalty_10: [],
        description: "Czarne, poszarpane skały bazaltowe. Ziemia tu jest twarda jak stal i gorąca od żaru."
    },
    "L13": {
        name: "Ruiny",
        color: "#6d6875",
        bonus_20: "Eter",
        penalty_20: "Natura",
        bonus_10: ["Metal", "Mrok"],
        penalty_10: [],
        description: "Pozostałości zapomnianej cywilizacji. Eteryczna energia wciąż pulsuje w murach."
    },
    "L14": {
        name: "Wrzosowiska",
        color: "#b5838d",
        bonus_20: "Światło",
        penalty_20: "Metal",
        bonus_10: ["Powietrze", "Eter"],
        penalty_10: [],
        description: "Fioletowe wrzosy falują na wietrze. Miejsce mocy, gdzie granice światów się истонczają."
    },
    "L15": {
        name: "Pola Uprawne",
        color: "#e6beae",
        bonus_20: "Ziemia",
        penalty_20: "Zaraza",
        bonus_10: ["Natura", "Woda"],
        penalty_10: [],
        description: "Zadbane pola i sady. Cywilizowany krajobraz, gdzie natura służy człowiekowi."
    }
};

/**
 * Generuje biom dla nowego pola na podstawie sąsiadów.
 * Algorytm dziedziczenia: 70% szans na typ sąsiada, 30% na losowy.
 *
 * @param {Array} discoveredNeighbors - odkryte sąsiednie pola [{biomeId, x, y}, ...]
 * @returns {string} ID biomu (L01-L15)
 */
export function generateBiome(discoveredNeighbors = []) {
    const roll = Math.random() * 100;
    
    if (discoveredNeighbors.length > 0 && roll <= 70) {
        // Dziedzicz od losowego sąsiada
        const neighbor = discoveredNeighbors[Math.floor(Math.random() * discoveredNeighbors.length)];
        return neighbor;
    }
    
    // Losowy biom
    return randomBiome();
}

/**
 * Zwraca losowy biom.
 * @returns {string} ID biomu
 */
export function randomBiome() {
    const ids = Object.keys(BIOMES);
    return ids[Math.floor(Math.random() * ids.length)];
}

/**
 * Zwraca dane biomu po ID.
 * @param {string} biomeId
 * @returns {Object|null}
 */
export function getBiome(biomeId) {
    return BIOMES[biomeId] || null;
}
