"""
Collection Tool for MTG Agent

This module provides tools for accessing and querying the user's MTG card collection
within the context of an AI agent.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
import json
from decimal import Decimal

from models.card_collection import CardCollection, load_collection_from_csv

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
