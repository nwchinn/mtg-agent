"""
Commander Deck models and utilities.
This module provides the data models for representing MTG Commander decks.
"""

from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field

class CardCategory(str, Enum):
    """Card category in a commander deck"""
    COMMANDER = "commander"
    CREATURE = "creature"
    ARTIFACT = "artifact"
    ENCHANTMENT = "enchantment"
    PLANESWALKER = "planeswalker"
    INSTANT = "instant"
    SORCERY = "sorcery"
    LAND = "land"
    OTHER = "other"

class DeckCard(BaseModel):
    """Represents a card in a commander deck"""
    name: str
    category: CardCategory
    quantity: int = 1
    owned: bool = False
    price: Optional[float] = None
    price_currency: Optional[str] = "USD"
    set_code: Optional[str] = None
    collector_number: Optional[str] = None
    scryfall_id: Optional[str] = None
    foil: Optional[bool] = False

class CommanderDeck(BaseModel):
    """Represents a complete commander deck with 99 cards + commander"""
    name: str
    description: Optional[str] = None
    commander: DeckCard
    cards: List[DeckCard]
    ownership_percentage: float = 0.0
    total_price: Optional[float] = None
    price_currency: Optional[str] = "USD"
    source: Optional[str] = None
    source_url: Optional[str] = None
    
    @property
    def total_cards(self) -> int:
        """Returns the total number of cards in the deck"""
        return 1 + sum(card.quantity for card in self.cards)  # Commander + 99 cards
    
    @property
    def by_category(self) -> Dict[CardCategory, List[DeckCard]]:
        """Group cards by category for tabular display"""
        result = {category: [] for category in CardCategory}
        
        # Add commander
        result[CardCategory.COMMANDER].append(self.commander)
        
        # Add other cards by category
        for card in self.cards:
            result[card.category].append(card)
        
        # Return only non-empty categories
        return {k: v for k, v in result.items() if v}
    
    def to_table_format(self) -> Dict[str, Any]:
        """
        Convert the deck to a tabular format suitable for display or JSON response
        
        Returns:
            Dictionary with categories as keys and lists of card details as values
        """
        by_category = self.by_category
        
        result = {
            "deck_name": self.name,
            "description": self.description,
            "ownership_percentage": self.ownership_percentage,
            "total_price": self.total_price,
            "price_currency": self.price_currency,
            "source": self.source,
            "tables": {}
        }
        
        # Create tables for each category
        for category, cards in by_category.items():
            result["tables"][category.value] = {
                "headers": ["Name", "Quantity", "Owned", "Price"],
                "rows": []
            }
            
            for card in cards:
                price_display = f"{card.price} {card.price_currency}" if card.price else "N/A"
                owned_display = "Yes" if card.owned else "No"
                
                result["tables"][category.value]["rows"].append([
                    card.name,
                    card.quantity,
                    owned_display,
                    price_display
                ])
        
        return result

class CommanderDeckResponse(BaseModel):
    """Response model for commander deck recommendations"""
    query: str
    decks: List[CommanderDeck]
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
