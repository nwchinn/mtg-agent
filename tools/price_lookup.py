"""
Price lookup tools for MTG cards.

This module provides functions to look up current market prices for MTG cards
using the Scryfall API.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
import re
import json
from dataclasses import dataclass
import urllib.parse

from models.card_collection import CardEntry

@dataclass
class CardPrice:
    """Price information for a card"""
    card_name: str
    set_name: str
    set_code: str
    collector_number: str
    foil: bool
    price: float
    price_source: str = "Scryfall"
    url: Optional[str] = None
    timestamp: Optional[str] = None
    image_url: Optional[str] = None
    usd_price: Optional[float] = None
    usd_foil_price: Optional[float] = None
    eur_price: Optional[float] = None
    tix_price: Optional[float] = None

async def get_scryfall_price(card: Union[CardEntry, Dict[str, Any]]) -> Optional[CardPrice]:
    """
    Get the current market price for a card from Scryfall API
    
    Args:
        card: Either a CardEntry object or a dictionary with card details
        
    Returns:
        CardPrice object with current price information or None if not found
    """
    # Extract card details
    if isinstance(card, CardEntry):
        card_name = card.name
        set_code = card.set_code
        collector_number = card.collector_number
        foil = card.foil
        set_name = card.set_name
        scryfall_id = card.scryfall_id
    else:
        card_name = card.get("name", "")
        set_code = card.get("set_code", "")
        collector_number = card.get("collector_number", "")
        foil = card.get("foil", False)
        set_name = card.get("set", "")
        scryfall_id = card.get("scryfall_id", "")
    
    # First try to look up by Scryfall ID if available
    if scryfall_id:
        return await get_card_by_scryfall_id(scryfall_id, foil)
    
    # Otherwise, try to look up by set code and collector number
    if set_code and collector_number:
        return await get_card_by_set_and_number(set_code, collector_number, foil)
    
    # Fallback to name search
    return await get_card_by_name(card_name, set_code, foil)

async def get_card_by_scryfall_id(scryfall_id: str, foil: bool) -> Optional[CardPrice]:
    """Get card price from Scryfall by Scryfall ID"""
    url = f"https://api.scryfall.com/cards/{scryfall_id}"
    return await fetch_scryfall_card(url, foil)

async def get_card_by_set_and_number(set_code: str, collector_number: str, foil: bool) -> Optional[CardPrice]:
    """Get card price from Scryfall by set code and collector number"""
    url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
    return await fetch_scryfall_card(url, foil)

async def get_card_by_name(name: str, set_code: Optional[str] = None, foil: bool = False) -> Optional[CardPrice]:
    """Get card price from Scryfall by name"""
    encoded_name = urllib.parse.quote(name)
    url = f"https://api.scryfall.com/cards/named?exact={encoded_name}"
    if set_code:
        url += f"&set={set_code}"
    return await fetch_scryfall_card(url, foil)

async def fetch_scryfall_card(url: str, foil: bool) -> Optional[CardPrice]:
    """Fetch card data from Scryfall API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Get the appropriate price based on foil status
                price = None
                if foil and data.get("prices", {}).get("usd_foil"):
                    price = float(data["prices"]["usd_foil"])
                elif data.get("prices", {}).get("usd"):
                    price = float(data["prices"]["usd"])
                else:
                    # Fallback to MTGO price if no USD price
                    tix_price = data.get("prices", {}).get("tix")
                    if tix_price:
                        price = float(tix_price) * 1.0  # Conversion factor
                
                # If we still don't have a price, return None
                if price is None:
                    return None
                
                # Extract price data
                usd_price = None
                if data.get("prices", {}).get("usd"):
                    usd_price = float(data["prices"]["usd"])
                
                usd_foil_price = None
                if data.get("prices", {}).get("usd_foil"):
                    usd_foil_price = float(data["prices"]["usd_foil"])
                
                eur_price = None
                if data.get("prices", {}).get("eur"):
                    eur_price = float(data["prices"]["eur"])
                
                tix_price = None
                if data.get("prices", {}).get("tix"):
                    tix_price = float(data["prices"]["tix"])
                
                return CardPrice(
                    card_name=data.get("name", ""),
                    set_name=data.get("set_name", ""),
                    set_code=data.get("set", ""),
                    collector_number=data.get("collector_number", ""),
                    foil=foil,
                    price=price,
                    price_source="Scryfall",
                    url=data.get("scryfall_uri", ""),
                    timestamp="2025-05-26",  # Use current date in real implementation
                    image_url=data.get("image_uris", {}).get("normal", ""),
                    usd_price=usd_price,
                    usd_foil_price=usd_foil_price,
                    eur_price=eur_price,
                    tix_price=tix_price
                )
    except Exception as e:
        print(f"Error fetching card data from Scryfall: {e}")
        return None

async def get_market_prices_for_cards(cards: List[Union[CardEntry, Dict[str, Any]]]) -> List[CardPrice]:
    """
    Get current market prices for a list of cards from Scryfall API
    
    Args:
        cards: List of CardEntry objects or dictionaries with card details
        
    Returns:
        List of CardPrice objects with current price information
    """
    prices = []
    for card in cards:
        price = await get_scryfall_price(card)
        if price:
            prices.append(price)
    
    return prices

async def get_most_valuable_cards_by_market_price(cards: List[CardEntry], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most valuable cards in a collection based on current market prices from Scryfall
    
    Args:
        cards: List of CardEntry objects
        limit: Maximum number of cards to return
        
    Returns:
        List of dictionaries with card details and current market prices
    """
    # Get current market prices for all cards
    prices = await get_market_prices_for_cards(cards)
    
    # Create a dictionary mapping card identifiers to prices
    card_prices = {}
    for price in prices:
        card_id = f"{price.card_name}|{price.set_code}|{price.collector_number}|{price.foil}"
        card_prices[card_id] = price
    
    # Create result dictionaries with both purchase and market prices
    result = []
    for card in cards:
        card_id = f"{card.name}|{card.set_code}|{card.collector_number}|{card.foil}"
        if card_id in card_prices:
            price_info = card_prices[card_id]
            result.append({
                "name": card.name,
                "set": card.set_name,
                "set_code": card.set_code,
                "collector_number": card.collector_number,
                "foil": card.foil,
                "purchase_price": float(card.purchase_price),
                "purchase_currency": card.purchase_price_currency,
                "market_price": price_info.price,
                "market_price_currency": "USD",  # Scryfall prices are in USD
                "price_source": "Scryfall",
                "price_url": price_info.url,
                "image_url": price_info.image_url
            })
    
    # Sort by market price, descending
    sorted_result = sorted(result, key=lambda x: x["market_price"] if x["market_price"] else 0, reverse=True)
    
    # Return top N cards
    return sorted_result[:limit]

async def calculate_collection_market_value(cards: List[CardEntry]) -> Dict[str, float]:
    """
    Calculate the total market value of a collection based on current market prices from Scryfall
    
    Args:
        cards: List of CardEntry objects
        
    Returns:
        Dictionary mapping currency codes to total values
    """
    # Get current market prices for all cards
    prices = await get_market_prices_for_cards(cards)
    
    # Create a dictionary mapping card identifiers to prices
    card_prices = {}
    for price in prices:
        card_id = f"{price.card_name}|{price.set_code}|{price.collector_number}|{price.foil}"
        card_prices[card_id] = price
    
    # Calculate total value for USD and EUR
    total_value = {"USD": 0.0, "EUR": 0.0}
    
    for card in cards:
        card_id = f"{card.name}|{card.set_code}|{card.collector_number}|{card.foil}"
        if card_id in card_prices:
            price_info = card_prices[card_id]
            if price_info.price:
                total_value["USD"] += price_info.price * card.quantity
            if price_info.eur_price:
                total_value["EUR"] += price_info.eur_price * card.quantity
    
    # Remove currencies with zero value
    return {k: v for k, v in total_value.items() if v > 0}
