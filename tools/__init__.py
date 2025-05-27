"""
MTG Agent Tools package
"""

from tools.collection_tool import (
    CollectionContext,
    get_collection_path,
    load_collection,
    get_collection_summary,
    calculate_ownership_for_deck,
    get_collection_value,
    search_collection_by_name,
    get_unique_card_names
)

from tools.price_lookup import (
    CardPrice,
    get_market_prices_for_cards,
    get_most_valuable_cards_by_market_price,
    calculate_collection_market_value
)

__all__ = [
    # Collection tools
    'CollectionContext',
    'get_collection_path',
    'load_collection',
    'get_collection_summary',
    'calculate_ownership_for_deck',
    'get_collection_value',
    'search_collection_by_name',
    'get_unique_card_names',
    
    # Price lookup tools
    'CardPrice',
    'get_market_prices_for_cards',
    'get_most_valuable_cards_by_market_price',
    'calculate_collection_market_value'
]
