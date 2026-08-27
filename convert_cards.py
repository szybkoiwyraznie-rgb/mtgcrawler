#!/usr/bin/env python3
# Konwerter TSV do JSON dla bazy kart MTG

import json
import csv

def convert_tsv_to_json(tsv_file, json_file):
    cards = []
    
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            # Pobierz ID z kolumny Ilustracja
            card_id = row.get('Ilustracja', '').strip()
            if not card_id:
                continue
            
            # Parse colors (może być "WUBRG" lub puste)
            colors_str = row.get('Colors', '').strip()
            colors = list(colors_str) if colors_str else []
            
            # Parse MV (Mana Value)
            try:
                mv = int(row.get('MV', '0').strip())
            except:
                mv = 0
            
            card = {
                'id': card_id,
                'name': row.get('Nazwa Karty', '').strip(),
                'set': row.get('Set / Fusion / Story', '').strip(),
                'setting': row.get('Plan / Setting', '').strip(),
                'mv': mv,
                'colors': colors,
                'prompt': row.get('Prompt', '').strip(),
                'narrative': row.get('Narracja', '').strip(),
                'lore': row.get('Lore', '').strip(),
                'bestiary': row.get('Bestiariusz', '').strip()
            }
            
            cards.append(card)
    
    # Zapisz do JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Zaimportowano {len(cards)} kart do {json_file}")

if __name__ == '__main__':
    convert_tsv_to_json(
        'KartyMtGKolekcja27082026.txt',
        'src/data/cards.json'
    )
