"""
Validation script for Scryfall models.
Downloads a sample of Scryfall data and validates it against our Pydantic models.
"""

import json
import requests
from typing import List, Dict, Any
import sys

from models.scryfall_models import ScryfallCard

# Get a small sample of cards from Scryfall API
def get_sample_cards(page_size: int = 10) -> List[Dict[str, Any]]:
    """Get a sample of cards from Scryfall's API"""
    url = f"https://api.scryfall.com/cards/search?q=set:one&page=1&unique=prints&order=name&include_extras=true&include_variations=true&include_multilingual=false"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []
    
    data = response.json()
    return data.get('data', [])[:page_size]

def validate_model(cards: List[Dict[str, Any]]) -> None:
    """Validate cards against our Pydantic model"""
    success_count = 0
    error_count = 0
    
    for i, card_data in enumerate(cards):
        try:
            # Try to parse the card data with our model
            card = ScryfallCard.parse_obj(card_data)
            success_count += 1
            print(f"✅ Successfully parsed card {i+1}: {card.name}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error parsing card {i+1}: {card_data.get('name', 'Unknown')}")
            print(f"  Error details: {str(e)}")
            
    print(f"\nValidation complete: {success_count} successes, {error_count} errors")
    if error_count > 0:
        print("Model needs adjustments to fully match Scryfall data.")
    else:
        print("Model appears compatible with Scryfall data!")

if __name__ == "__main__":
    print("Fetching sample cards from Scryfall...")
    cards = get_sample_cards(10)  # Get 10 sample cards
    
    if not cards:
        print("No cards retrieved. Exiting.")
        sys.exit(1)
    
    print(f"Retrieved {len(cards)} cards. Validating against model...\n")
    validate_model(cards)
