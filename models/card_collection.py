"""
MTG Card Collection models and utilities.
This module handles loading, parsing, and querying the user's MTG card collection.
"""

from pathlib import Path
import csv
from typing import Dict, List, Optional, Set, Union
from enum import Enum
from decimal import Decimal
import asyncio
from pydantic import BaseModel, Field

class Rarity(str, Enum):
    """Card rarity enum"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"

class Condition(str, Enum):
    """Card condition enum"""
    EXCELLENT = "excellent"
    MINT = "mint"
    GOOD = "good"
    LIGHT_PLAYED = "light_played"
    NEAR_MINT = "near_mint"
    LIGHTLY_PLAYED = "lightly_played"
    MODERATELY_PLAYED = "moderately_played"
    HEAVILY_PLAYED = "heavily_played"
    DAMAGED = "damaged"

class CardEntry(BaseModel):
    """Represents a single card entry in the collection"""
    binder_name: str
    binder_type: str
    name: str
    set_code: str
    set_name: str
    collector_number: str
    foil: bool
    rarity: Rarity
    quantity: int
    manabox_id: int
    scryfall_id: str
    purchase_price: Decimal
    misprint: bool
    altered: bool
    condition: Condition
    language: str
    purchase_price_currency: str
    
    class Config:
        """Pydantic model configuration"""
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class CardCollection(BaseModel):
    """Represents the user's entire MTG card collection"""
    cards: List[CardEntry] = Field(default_factory=list)
    
    @property
    def total_cards(self) -> int:
        """Returns the total number of physical cards in the collection"""
        return sum(card.quantity for card in self.cards)
    
    @property
    def unique_cards(self) -> int:
        """Returns the number of unique cards in the collection"""
        return len(self.cards)
    
    @property
    def total_value(self) -> Dict[str, Decimal]:
        """Returns the total value of the collection by currency"""
        values = {}
        for card in self.cards:
            currency = card.purchase_price_currency
            if currency not in values:
                values[currency] = Decimal('0')
            values[currency] += card.purchase_price * card.quantity
        return values
    
    def get_cards_by_name(self, name: str) -> List[CardEntry]:
        """Returns all cards with the given name"""
        return [card for card in self.cards if card.name.lower() == name.lower()]
    
    def get_unique_card_names(self) -> Set[str]:
        """Returns a set of all unique card names in the collection"""
        return {card.name for card in self.cards}
    
    def get_cards_by_set(self, set_code: str) -> List[CardEntry]:
        """Returns all cards from the given set"""
        return [card for card in self.cards if card.set_code.lower() == set_code.lower()]
    
    def get_cards_by_rarity(self, rarity: Rarity) -> List[CardEntry]:
        """Returns all cards of the given rarity"""
        return [card for card in self.cards if card.rarity == rarity]
    
    def get_foil_cards(self) -> List[CardEntry]:
        """Returns all foil cards in the collection"""
        return [card for card in self.cards if card.foil]
    
    def calculate_deck_ownership(self, deck_cards: Dict[str, int]) -> float:
        """
        Calculate what percentage of a deck the user owns
        
        Args:
            deck_cards: Dict mapping card names to quantities needed
            
        Returns:
            Float representing percentage of the deck owned (0-100)
        """
        if not deck_cards:
            return 0.0
            
        # Get a map of card name -> quantity owned
        owned_cards = {}
        for card in self.cards:
            if card.name not in owned_cards:
                owned_cards[card.name] = 0
            owned_cards[card.name] += card.quantity
        
        total_cards_needed = sum(deck_cards.values())
        total_cards_owned = 0
        
        for card_name, quantity_needed in deck_cards.items():
            quantity_owned = owned_cards.get(card_name, 0)
            # Only count up to the needed amount
            total_cards_owned += min(quantity_owned, quantity_needed)
        
        return (total_cards_owned / total_cards_needed) * 100

def load_collection_from_csv(file_path: Union[str, Path]) -> CardCollection:
    """
    Load a card collection from a ManaBox_Collection.csv file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        CardCollection object containing all the cards
    """
    collection = CardCollection()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert boolean strings to actual booleans
            foil = row['Foil'].lower() == 'foil'
            misprint = row['Misprint'].lower() == 'true'
            altered = row['Altered'].lower() == 'true'
            
            # Handle possible empty values
            purchase_price = Decimal(row['Purchase price'] or '0')
            
            card_entry = CardEntry(
                binder_name=row['Binder Name'],
                binder_type=row['Binder Type'],
                name=row['Name'],
                set_code=row['Set code'],
                set_name=row['Set name'],
                collector_number=row['Collector number'],
                foil=foil,
                rarity=row['Rarity'],
                quantity=int(row['Quantity']),
                manabox_id=int(row['ManaBox ID']),
                scryfall_id=row['Scryfall ID'],
                purchase_price=purchase_price,
                misprint=misprint,
                altered=altered,
                condition=row['Condition'],
                language=row['Language'],
                purchase_price_currency=row['Purchase price currency']
            )
            collection.cards.append(card_entry)
    
    return collection
