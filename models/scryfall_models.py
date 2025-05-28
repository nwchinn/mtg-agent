"""
Scryfall API data models.
This module provides Pydantic models for the Scryfall API responses.
"""

from typing import Dict, List, Optional, Union, Any, Set
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class CardLayout(str, Enum):
    """Card layout as defined by Scryfall"""
    NORMAL = "normal"
    SPLIT = "split"
    FLIP = "flip"
    TRANSFORM = "transform"
    MODAL_DFC = "modal_dfc"
    MELD = "meld"
    LEVELER = "leveler"
    CLASS = "class"
    SAGA = "saga"
    ADVENTURE = "adventure"
    PLANAR = "planar"
    SCHEME = "scheme"
    VANGUARD = "vanguard"
    TOKEN = "token"
    DOUBLE_FACED_TOKEN = "double_faced_token"
    EMBLEM = "emblem"
    AUGMENT = "augment"
    HOST = "host"
    ART_SERIES = "art_series"
    REVERSIBLE_CARD = "reversible_card"

class CardFinish(str, Enum):
    """Card finish types"""
    FOIL = "foil"
    NONFOIL = "nonfoil"
    ETCHED = "etched"
    GLOSSY = "glossy"

class CardFrame(str, Enum):
    """Card frame styles"""
    LEGACY = "1993"
    MODERN = "2003"
    M15 = "2015"
    FUTURE = "future"

class CardRarity(str, Enum):
    """Card rarity types"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"

class CardStatus(str, Enum):
    """Card legality status"""
    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    RESTRICTED = "restricted"
    BANNED = "banned"

class BorderColor(str, Enum):
    """Card border colors"""
    BLACK = "black"
    WHITE = "white"
    BORDERLESS = "borderless"
    SILVER = "silver"
    GOLD = "gold"

class ImageStatus(str, Enum):
    """Status of card images"""
    MISSING = "missing"
    PLACEHOLDER = "placeholder"
    LOWRES = "lowres"
    HIGHRES_SCAN = "highres_scan"

class CardFace(BaseModel):
    """Model for a single face of a card (for multi-faced cards)"""
    artist: Optional[str] = None
    cmc: Optional[float] = None
    color_indicator: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    flavor_text: Optional[str] = None
    illustration_id: Optional[str] = None
    image_uris: Optional[Dict[str, HttpUrl]] = None
    loyalty: Optional[str] = None
    mana_cost: Optional[str] = None
    name: str
    oracle_id: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    printed_name: Optional[str] = None
    printed_text: Optional[str] = None
    printed_type_line: Optional[str] = None
    toughness: Optional[str] = None
    type_line: Optional[str] = None
    watermark: Optional[str] = None

class RelatedCard(BaseModel):
    """Model for a related card object"""
    id: str
    object: str = "related_card"
    component: str
    name: str
    type_line: str
    uri: HttpUrl

class Legalities(BaseModel):
    """Card legality in various formats"""
    standard: CardStatus = CardStatus.NOT_LEGAL
    future: CardStatus = CardStatus.NOT_LEGAL
    historic: CardStatus = CardStatus.NOT_LEGAL
    gladiator: CardStatus = CardStatus.NOT_LEGAL
    pioneer: CardStatus = CardStatus.NOT_LEGAL
    explorer: CardStatus = CardStatus.NOT_LEGAL
    modern: CardStatus = CardStatus.NOT_LEGAL
    legacy: CardStatus = CardStatus.NOT_LEGAL
    pauper: CardStatus = CardStatus.NOT_LEGAL
    vintage: CardStatus = CardStatus.NOT_LEGAL
    penny: CardStatus = CardStatus.NOT_LEGAL
    commander: CardStatus = CardStatus.NOT_LEGAL
    brawl: CardStatus = CardStatus.NOT_LEGAL
    historicbrawl: CardStatus = CardStatus.NOT_LEGAL
    alchemy: CardStatus = CardStatus.NOT_LEGAL
    paupercommander: CardStatus = CardStatus.NOT_LEGAL
    duel: CardStatus = CardStatus.NOT_LEGAL
    oldschool: CardStatus = CardStatus.NOT_LEGAL
    premodern: CardStatus = CardStatus.NOT_LEGAL
    predh: CardStatus = CardStatus.NOT_LEGAL

class Price(BaseModel):
    """Price information for a card"""
    usd: Optional[str] = None
    usd_foil: Optional[str] = None
    usd_etched: Optional[str] = None
    eur: Optional[str] = None
    eur_foil: Optional[str] = None
    tix: Optional[str] = None

class PurchaseUris(BaseModel):
    """URIs for purchasing a card"""
    tcgplayer: Optional[HttpUrl] = None
    cardmarket: Optional[HttpUrl] = None
    cardhoarder: Optional[HttpUrl] = None

class RelatedUris(BaseModel):
    """Related URIs for a card"""
    gatherer: Optional[HttpUrl] = None
    tcgplayer_infinite_articles: Optional[HttpUrl] = None
    tcgplayer_infinite_decks: Optional[HttpUrl] = None
    edhrec: Optional[HttpUrl] = None

class ImageUris(BaseModel):
    """Card image URIs in various sizes and formats"""
    small: Optional[HttpUrl] = None
    normal: Optional[HttpUrl] = None
    large: Optional[HttpUrl] = None
    png: Optional[HttpUrl] = None
    art_crop: Optional[HttpUrl] = None
    border_crop: Optional[HttpUrl] = None

class ScryfallCard(BaseModel):
    """Complete Scryfall card model"""
    # Core card fields
    id: str
    oracle_id: str
    multiverse_ids: Optional[List[int]] = None
    mtgo_id: Optional[int] = None
    mtgo_foil_id: Optional[int] = None
    tcgplayer_id: Optional[int] = None
    cardmarket_id: Optional[int] = None
    name: str
    lang: str
    released_at: str
    uri: HttpUrl
    scryfall_uri: HttpUrl
    layout: CardLayout
    highres_image: bool
    image_status: ImageStatus
    image_uris: Optional[ImageUris] = None
    
    # Gameplay fields
    mana_cost: Optional[str] = None
    cmc: float
    type_line: str
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    colors: Optional[List[str]] = None
    color_identity: List[str]
    keywords: List[str] = Field(default_factory=list)
    all_parts: Optional[List[RelatedCard]] = None
    card_faces: Optional[List[CardFace]] = None
    legalities: Legalities
    
    # Print fields
    reserved: bool
    foil: bool
    nonfoil: bool
    finishes: List[CardFinish]
    oversized: bool
    promo: bool
    reprint: bool
    variation: bool
    set_id: str
    set: str  # set code
    set_name: str
    set_type: str
    set_uri: HttpUrl
    set_search_uri: HttpUrl
    scryfall_set_uri: HttpUrl
    rulings_uri: HttpUrl
    prints_search_uri: HttpUrl
    collector_number: str
    digital: bool
    rarity: CardRarity
    flavor_text: Optional[str] = None
    card_back_id: str
    artist: Optional[str] = None
    artist_ids: List[str]
    illustration_id: Optional[str] = None
    border_color: BorderColor
    frame: CardFrame
    full_art: bool
    textless: bool
    booster: bool
    story_spotlight: bool
    
    # Pricing and purchase fields
    prices: Price
    related_uris: RelatedUris
    purchase_uris: Optional[PurchaseUris] = None
    
    def to_deck_card(self, quantity: int = 1, owned: bool = False) -> 'DeckCard':
        """
        Convert this Scryfall card to a DeckCard model for use in decks
        
        Args:
            quantity: Number of this card in the deck
            owned: Whether the user owns this card
            
        Returns:
            DeckCard instance with data from this Scryfall card
        """
        from models.commander_deck import DeckCard, CardCategory
        
        # Determine card category
        category = CardCategory.OTHER
        type_line = self.type_line.lower()
        
        if "creature" in type_line:
            category = CardCategory.CREATURE
        elif "artifact" in type_line:
            category = CardCategory.ARTIFACT
        elif "enchantment" in type_line:
            category = CardCategory.ENCHANTMENT
        elif "planeswalker" in type_line:
            category = CardCategory.PLANESWALKER
        elif "instant" in type_line:
            category = CardCategory.INSTANT
        elif "sorcery" in type_line:
            category = CardCategory.SORCERY
        elif "land" in type_line:
            category = CardCategory.LAND
        
        # Extract price in USD
        price = None
        if self.prices.usd:
            price = float(self.prices.usd)
        elif self.prices.usd_foil and "foil" in self.finishes:
            price = float(self.prices.usd_foil)
        
        return DeckCard(
            name=self.name,
            category=category,
            quantity=quantity,
            owned=owned,
            price=price,
            price_currency="USD",
            set_code=self.set,
            collector_number=self.collector_number,
            scryfall_id=self.id,
            foil="foil" in self.finishes
        )
