"""
Standard Deck models and utilities.
This module provides the data models for representing MTG Standard format decks.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl

from models.commander_deck import DeckCard, CardCategory
from models.scryfall_models import ScryfallCard

class DeckSection(str, Enum):
    """Sections in a Standard deck"""
    MAIN = "mainboard"
    SIDEBOARD = "sideboard"

class StandardDeck(BaseModel):
    """Represents a complete Standard format deck with mainboard and sideboard"""
    name: str
    description: Optional[str] = None
    format: str = "standard"
    mainboard: List[DeckCard]
    sideboard: List[DeckCard] = Field(default_factory=list)
    ownership_percentage: float = 0.0
    total_price: Optional[float] = None
    price_currency: Optional[str] = "USD"
    source: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    author: Optional[str] = None
    
    @property
    def total_cards(self) -> Dict[str, int]:
        """Returns the total number of cards in the deck by section"""
        return {
            "mainboard": sum(card.quantity for card in self.mainboard),
            "sideboard": sum(card.quantity for card in self.sideboard),
            "total": sum(card.quantity for card in self.mainboard) + 
                     sum(card.quantity for card in self.sideboard)
        }
    
    @property
    def by_category(self) -> Dict[str, Dict[CardCategory, List[DeckCard]]]:
        """Group cards by category and section for tabular display"""
        result = {
            "mainboard": {category: [] for category in CardCategory},
            "sideboard": {category: [] for category in CardCategory}
        }
        
        # Add mainboard cards by category
        for card in self.mainboard:
            result["mainboard"][card.category].append(card)
        
        # Add sideboard cards by category
        for card in self.sideboard:
            result["sideboard"][card.category].append(card)
        
        # Return only non-empty categories
        return {
            section: {k: v for k, v in categories.items() if v}
            for section, categories in result.items()
        }
    
    def to_table_format(self) -> Dict[str, Any]:
        """
        Convert the deck to a tabular format suitable for display or JSON response
        
        Returns:
            Dictionary with sections and categories as keys and lists of card details as values
        """
        by_category = self.by_category
        
        result = {
            "deck_name": self.name,
            "description": self.description,
            "format": self.format,
            "ownership_percentage": self.ownership_percentage,
            "total_price": self.total_price,
            "price_currency": self.price_currency,
            "source": self.source,
            "author": self.author,
            "card_count": self.total_cards,
            "tables": {}
        }
        
        # Create tables for each section and category
        for section, categories in by_category.items():
            result["tables"][section] = {}
            
            for category, cards in categories.items():
                result["tables"][section][category.value] = {
                    "headers": ["Name", "Quantity", "Owned", "Price"],
                    "rows": []
                }
                
                for card in cards:
                    price_display = f"{card.price} {card.price_currency}" if card.price else "N/A"
                    owned_display = "Yes" if card.owned else "No"
                    
                    result["tables"][section][category.value]["rows"].append([
                        card.name,
                        card.quantity,
                        owned_display,
                        price_display
                    ])
        
        return result

class StandardDeckResponse(BaseModel):
    """Response model for standard deck recommendations"""
    query: str
    decks: List[StandardDeck]
    total_results: int
    ownership_threshold: Optional[float] = None
    
    def to_table_format(self) -> Dict[str, Any]:
        """
        Convert the response to a tabular format suitable for display or JSON response
        
        Returns:
            Dictionary with deck tables and summary information
        """
        result = {
            "query": self.query,
            "total_results": self.total_results,
            "ownership_threshold": self.ownership_threshold,
            "decks": [deck.to_table_format() for deck in self.decks]
        }
        
        return result

def create_standard_deck_from_scryfall(
    name: str,
    mainboard_cards: Dict[ScryfallCard, int],
    sideboard_cards: Dict[ScryfallCard, int] = None,
    collection = None
) -> StandardDeck:
    """
    Create a StandardDeck object from Scryfall card data
    
    Args:
        name: Name of the deck
        mainboard_cards: Dictionary mapping ScryfallCard objects to quantities for the mainboard
        sideboard_cards: Dictionary mapping ScryfallCard objects to quantities for the sideboard
        collection: Optional CardCollection to check ownership against
        
    Returns:
        StandardDeck object
    """
    from models.card_collection import CardCollection
    
    if sideboard_cards is None:
        sideboard_cards = {}
    
    mainboard = []
    sideboard = []
    
    # Add mainboard cards
    for card, quantity in mainboard_cards.items():
        owned = False
        if collection:
            # Check if card exists in collection
            card_in_collection = collection.get_cards_by_name(card.name)
            owned_quantity = sum(c.quantity for c in card_in_collection)
            if owned_quantity >= quantity:
                owned = True
        
        deck_card = card.to_deck_card(quantity=quantity, owned=owned)
        mainboard.append(deck_card)
    
    # Add sideboard cards
    for card, quantity in sideboard_cards.items():
        owned = False
        if collection:
            # Check if card exists in collection
            card_in_collection = collection.get_cards_by_name(card.name)
            owned_quantity = sum(c.quantity for c in card_in_collection)
            if owned_quantity >= quantity:
                owned = True
        
        deck_card = card.to_deck_card(quantity=quantity, owned=owned)
        sideboard.append(deck_card)
    
    # Calculate ownership percentage
    total_cards = sum(quantity for _, quantity in mainboard_cards.items()) + \
                  sum(quantity for _, quantity in sideboard_cards.items())
    
    owned_count = sum(card.quantity for card in mainboard if card.owned) + \
                 sum(card.quantity for card in sideboard if card.owned)
    
    ownership_percentage = (owned_count / total_cards * 100) if total_cards > 0 else 0
    
    # Calculate total price
    total_price = sum((card.price or 0) * card.quantity for card in mainboard) + \
                 sum((card.price or 0) * card.quantity for card in sideboard)
    
    return StandardDeck(
        name=name,
        mainboard=mainboard,
        sideboard=sideboard,
        ownership_percentage=round(ownership_percentage, 2),
        total_price=round(total_price, 2)
    )
