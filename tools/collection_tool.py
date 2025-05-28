"""
Collection Tool for MTG Agent

This module provides tools for accessing and querying the user's MTG card collection
within the context of an AI agent.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from dataclasses import dataclass
import json
from decimal import Decimal

from models.card_collection import CardCollection, load_collection_from_csv
from models.commander_deck import CommanderDeck, DeckCard, CardCategory, CommanderDeckResponse

@dataclass
class CollectionContext:
    """
    Context about the user's MTG collection to provide to the agent
    """
    total_cards: int
    unique_cards: int
    total_value: Dict[str, float]
    top_valuable_cards: List[Dict[str, Any]]
    rarity_breakdown: Dict[str, int]

def get_collection_path() -> Path:
    """
    Returns the path to the user's collection CSV file.
    Modify this if your collection is stored elsewhere.
    """
    base_dir = Path(__file__).parent.parent
    return base_dir / "data" / "ManaBox_Collection.csv"

def load_collection() -> CardCollection:
    """
    Load the user's MTG card collection
    """
    collection_path = get_collection_path()
    if not collection_path.exists():
        raise FileNotFoundError(f"Collection file not found at {collection_path}")
    
    return load_collection_from_csv(collection_path)

def get_collection_summary(collection: Optional[CardCollection] = None) -> CollectionContext:
    """
    Generate a summary of the collection for context
    """
    if collection is None:
        collection = load_collection()
    
    # Get total value and convert Decimal to float for JSON serialization
    total_value = {currency: float(value) for currency, value in collection.total_value.items()}
    
    # Get the top 10 most valuable cards by purchase price
    sorted_cards = sorted(
        collection.cards, 
        key=lambda card: float(card.purchase_price), 
        reverse=True
    )
    top_valuable = []
    for card in sorted_cards[:10]:
        top_valuable.append({
            "name": card.name,
            "set": card.set_name,
            "set_code": card.set_code,
            "collector_number": card.collector_number,
            "foil": card.foil,
            "purchase_price": float(card.purchase_price),
            "currency": card.purchase_price_currency,
            "scryfall_id": card.scryfall_id
        })
    
    # Get rarity breakdown
    rarity_counts = {}
    for card in collection.cards:
        rarity = card.rarity.value
        if rarity not in rarity_counts:
            rarity_counts[rarity] = 0
        rarity_counts[rarity] += card.quantity
    
    return CollectionContext(
        total_cards=collection.total_cards,
        unique_cards=collection.unique_cards,
        total_value=total_value,
        top_valuable_cards=top_valuable,
        rarity_breakdown=rarity_counts
    )

def calculate_ownership_for_deck(deck_list: Dict[str, int], 
                                 collection: Optional[CardCollection] = None) -> float:
    """
    Calculate what percentage of a deck the user already owns
    
    Args:
        deck_list: Dictionary mapping card names to quantities
        collection: Optional CardCollection object, will load from file if not provided
        
    Returns:
        Float representing percentage of the deck owned (0-100)
    """
    if collection is None:
        collection = load_collection()
    
    return collection.calculate_deck_ownership(deck_list)

def get_collection_value(collection: Optional[CardCollection] = None) -> Dict[str, float]:
    """
    Get the total value of the user's collection by currency
    
    Returns:
        Dictionary mapping currency codes to total values
    """
    if collection is None:
        collection = load_collection()
    
    return {currency: float(value) for currency, value in collection.total_value.items()}

def search_collection_by_name(card_name: str, 
                             collection: Optional[CardCollection] = None) -> List[Dict[str, Any]]:
    """
    Search for cards in the collection by name
    
    Args:
        card_name: Name of the card to search for (case-insensitive)
        collection: Optional CardCollection object, will load from file if not provided
        
    Returns:
        List of matching cards as dictionaries
    """
    if collection is None:
        collection = load_collection()
    
    matching_cards = collection.get_cards_by_name(card_name)
    result = []
    
    for card in matching_cards:
        result.append({
            "name": card.name,
            "set": card.set_name,
            "set_code": card.set_code,
            "collector_number": card.collector_number,
            "foil": card.foil,
            "quantity": card.quantity,
            "rarity": card.rarity.value,
            "price": float(card.purchase_price),
            "currency": card.purchase_price_currency
        })
    
    return result

def get_unique_card_names(collection: Optional[CardCollection] = None) -> List[str]:
    """
    Get a list of all unique card names in the collection
    
    Args:
        collection: Optional CardCollection object, will load from file if not provided
        
    Returns:
        List of unique card names
    """
    if collection is None:
        collection = load_collection()
    
    return sorted(list(collection.get_unique_card_names()))


def get_legendary_creatures(collection: Optional[CardCollection] = None) -> List[Dict[str, Any]]:
    """
    Get all legendary creatures from the collection
    
    Args:
        collection: Optional CardCollection object, will load from file if not provided
        
    Returns:
        List of legendary creatures as dictionaries
    """
    if collection is None:
        collection = load_collection()
    
    # Note: This is a simplified implementation that relies on the card name
    # A more comprehensive solution would check card type via Scryfall API
    legendary_creatures = []
    for card in collection.cards:
        # Most legendary creatures have "the" or ", " in their name, but this is an imperfect heuristic
        # This will need to be enhanced with proper type checking in the future
        if (" the " in card.name.lower() or ", " in card.name):
            legendary_creatures.append({
                "name": card.name,
                "set": card.set_name,
                "set_code": card.set_code,
                "collector_number": card.collector_number,
                "foil": card.foil,
                "quantity": card.quantity,
                "rarity": card.rarity.value,
                "price": float(card.purchase_price),
                "currency": card.purchase_price_currency,
                "scryfall_id": card.scryfall_id
            })
    
    return sorted(legendary_creatures, key=lambda x: x["name"])


def create_commander_deck(deck_name: str, commander_name: str, deck_list: Dict[str, int], 
                           collection: Optional[CardCollection] = None) -> CommanderDeck:
    """
    Create a commander deck model with ownership information
    
    Args:
        deck_name: Name of the deck
        commander_name: Name of the commander card
        deck_list: Dictionary mapping card names to quantities
        collection: Optional CardCollection object, will load from file if not provided
        
    Returns:
        CommanderDeck object with card information and ownership status
    """
    if collection is None:
        collection = load_collection()
    
    # Validate the deck structure
    total_cards = sum(deck_list.values())
    if total_cards != 99:
        raise ValueError(f"Commander deck must have exactly 99 cards (+ commander). Current count: {total_cards}")
    
    # Check if commander exists in collection
    commander_owned = False
    commander_cards = collection.get_cards_by_name(commander_name)
    commander_card = None
    
    if commander_cards:
        commander_owned = True
        # Use the first matching card as reference
        commander_card = commander_cards[0]
    
    # Create the commander card model
    commander = DeckCard(
        name=commander_name,
        category=CardCategory.COMMANDER,
        owned=commander_owned,
        price=float(commander_card.purchase_price) if commander_card else None,
        price_currency=commander_card.purchase_price_currency if commander_card else "USD",
        set_code=commander_card.set_code if commander_card else None,
        collector_number=commander_card.collector_number if commander_card else None,
        scryfall_id=commander_card.scryfall_id if commander_card else None,
        foil=commander_card.foil if commander_card else False
    )
    
    # Create deck cards with ownership information
    deck_cards = []
    owned_count = 0
    total_price = 0.0
    
    for card_name, quantity in deck_list.items():
        # Skip the commander, it's handled separately
        if card_name.lower() == commander_name.lower():
            continue
            
        # Get category (simplified for now, can be enhanced)
        category = CardCategory.OTHER
        if "land" in card_name.lower() or "island" in card_name.lower() or "mountain" in card_name.lower() or \
           "swamp" in card_name.lower() or "forest" in card_name.lower() or "plains" in card_name.lower():
            category = CardCategory.LAND
        
        # Check if card exists in collection
        owned = False
        card_in_collection = collection.get_cards_by_name(card_name)
        owned_quantity = 0
        card_ref = None
        
        if card_in_collection:
            card_ref = card_in_collection[0]  # Use first matching card as reference
            for card in card_in_collection:
                owned_quantity += card.quantity
            
            if owned_quantity >= quantity:
                owned = True
                owned_count += quantity
            else:
                # Partially owned
                owned_count += owned_quantity
        
        # Create the deck card model
        deck_card = DeckCard(
            name=card_name,
            category=category,
            quantity=quantity,
            owned=owned,
            price=float(card_ref.purchase_price) if card_ref else None,
            price_currency=card_ref.purchase_price_currency if card_ref else "USD",
            set_code=card_ref.set_code if card_ref else None,
            collector_number=card_ref.collector_number if card_ref else None,
            scryfall_id=card_ref.scryfall_id if card_ref else None,
            foil=card_ref.foil if card_ref else False
        )
        
        # Add to total price if available
        if card_ref and card_ref.purchase_price:
            total_price += float(card_ref.purchase_price) * quantity
        
        deck_cards.append(deck_card)
    
    # Add commander price if available
    if commander_card and commander_card.purchase_price:
        total_price += float(commander_card.purchase_price)
    
    # Calculate ownership percentage
    total_deck_cards = 100  # 99 + commander
    ownership_percentage = (owned_count + (1 if commander_owned else 0)) / total_deck_cards * 100
    
    # Create the commander deck model
    commander_deck = CommanderDeck(
        name=deck_name,
        commander=commander,
        cards=deck_cards,
        ownership_percentage=round(ownership_percentage, 2),
        total_price=round(total_price, 2),
        price_currency="USD"  # Assuming USD for now
    )
    
    return commander_deck


def create_commander_deck_response(query: str, decks: List[CommanderDeck], 
                                   ownership_threshold: Optional[float] = None) -> Dict[str, Any]:
    """
    Create a tabular response format for commander deck recommendations
    
    Args:
        query: The original query from the user
        decks: List of CommanderDeck objects
        ownership_threshold: Optional ownership threshold used for filtering
        
    Returns:
        Dictionary with tabular data format for displaying decks
    """
    response = CommanderDeckResponse(
        query=query,
        decks=decks,
        total_results=len(decks),
        ownership_threshold=ownership_threshold
    )
    
    return response.to_table_format()
