"""
MTG Collection Agent

This module integrates your MTG card collection with web search capabilities to provide
a powerful agent that can answer questions about your collection, recommend decks based on
owned cards, and analyze the market value of your collection.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional

from agents import Agent, Runner, trace
from agents.tool import WebSearchTool
from pydantic import BaseModel, Field

from tools.collection_tool import (
    load_collection,
    get_collection_summary,
    calculate_ownership_for_deck,
    get_collection_value,
    search_collection_by_name
)

class DeckList(BaseModel):
    """Model representing a deck list with card quantities"""
    name: str
    cards: Dict[str, int]
    description: Optional[str] = None
    format: Optional[str] = None
    source: Optional[str] = None

class CollectionQuery(BaseModel):
    """Model for querying the collection"""
    query_type: str = Field(..., description="Type of query (e.g., 'deck_ownership', 'card_search', 'collection_value')")
    card_name: Optional[str] = Field(None, description="Card name to search for in the collection")
    deck_list: Optional[DeckList] = Field(None, description="Deck list to check ownership against")

# Create specialized MTG agents with specific expertise

# Collection specialist
collection_specialist = Agent(
    name="Collection Specialist",
    handoff_description="Specialist for analyzing the user's MTG collection, checking card ownership, and calculating collection value.",
    instructions="""You are a specialized MTG collection assistant.
    You have access to the user's MTG card collection from ManaBox_Collection.csv.
    
    You can:
    1. Calculate the total value of the user's collection
    2. Search for specific cards in the collection
    3. Check how many copies of a card the user owns
    4. Provide statistics about the collection (total cards, rarities, etc.)
    
    Always provide accurate information based on the actual collection data.
    When asked about cards not in the collection, clearly state that they are not owned.""",
)

# cEDH deck specialist with preferred sources
cedh_specialist = Agent(
    name="cEDH Specialist",
    handoff_description="Specialist for competitive Commander (cEDH) format questions, deck building, and metagame analysis.",
    instructions="""You are a specialized cEDH MTG assistant, focusing on competitive Commander format.
    When searching for deck information, primarily use and reference information from:
    1. https://edhtop16.com/
    2. https://www.mtgtop8.com/
    
    For any cEDH commander or deck related questions, make sure to prioritize information from these sources.
    If these sources don't have the information, you can use other reputable MTG sources as a fallback.
    Always cite your sources when providing information.""",
    tools=[WebSearchTool(search_context_size="high")],
)

# Standard/Pioneer specialist
standard_pioneer_specialist = Agent(
    name="Standard/Pioneer Specialist",
    handoff_description="Specialist for Standard and Pioneer formats, current meta, deck building, and tournament results.",
    instructions="""You are a specialized MTG assistant for Standard and Pioneer formats.
    Focus on current meta decks, tournament results, and deck building advice for these formats.
    Primarily use information from:
    1. https://www.mtggoldfish.com/
    2. https://www.mtgtop8.com/
    
    Always cite your sources when providing information.""",
    tools=[WebSearchTool(search_context_size="high")],
)

# Rules specialist
rules_specialist = Agent(
    name="MTG Rules Specialist",
    handoff_description="Specialist for MTG rules questions, interactions, and official rulings.",
    instructions="""You are a specialized MTG rules assistant.
    Focus on answering rules questions, card interactions, and providing official rulings.
    Primarily use information from:
    1. https://mtg.fandom.com/wiki/
    2. https://scryfall.com/
    3. https://magic.wizards.com/en/rules
    
    Always cite specific rules when applicable and provide clear explanations.""",
    tools=[WebSearchTool(search_context_size="high")],
)

# Main triage agent that handles collection-related queries and delegates to specialists
main_agent = Agent(
    name="MTG Collection Assistant",
    instructions="""You are an MTG Collection Assistant with access to the user's card collection and web search capabilities.
    
    YOUR COLLECTION CONTEXT:
    - The user has a collection of MTG cards imported from ManaBox_Collection.csv
    - You can access details about the cards they own, quantities, values, etc.
    - You can calculate what percentage of a deck they already own
    
    For specialized queries:
    1. For questions about the user's collection, card ownership, or collection value, handle them directly.
    2. For cEDH (competitive Commander) questions or finding cEDH decks, delegate to the cEDH Specialist.
    3. For Standard or Pioneer format questions, delegate to the Standard/Pioneer Specialist.
    4. For rules questions, card interactions, or official rulings, delegate to the MTG Rules Specialist.
    
    When asked to find decks based on the user's collection (e.g., "Find cEDH decks with over 30% cards I own"):
    1. Delegate to the cEDH Specialist to find current top decks
    2. For each deck, calculate the ownership percentage
    3. Only recommend decks that meet the ownership threshold
    
    Always provide helpful, accurate information based on the user's collection and current MTG data.""",
    handoffs=[collection_specialist, cedh_specialist, standard_pioneer_specialist, rules_specialist],
    tools=[WebSearchTool(search_context_size="high")],
)

async def process_collection_query(query: str):
    """
    Process a query about the user's MTG collection
    
    Args:
        query: The user's natural language query
        
    Returns:
        The response from the agent
    """
    # Load collection data summary for context
    collection_summary = get_collection_summary()
    
    # Format collection context to inject into the conversation
    collection_context = f"""
    COLLECTION CONTEXT:
    - Total cards: {collection_summary.total_cards}
    - Unique cards: {collection_summary.unique_cards}
    - Total value: {', '.join([f"{float(value)} {currency}" for currency, value in collection_summary.total_value.items()])}
    - Rarity breakdown: {', '.join([f"{rarity}: {count}" for rarity, count in collection_summary.rarity_breakdown.items()])}
    
    Top valuable cards:
    {json.dumps(collection_summary.top_valuable_cards[:5], indent=2)}
    """
    
    # Prepare the prompt with collection context
    full_prompt = f"{collection_context}\n\nUser query: {query}"
    
    # Run the agent with the collection context and query
    with trace("MTG Collection Assistant"):
        result = await Runner.run(
            main_agent,
            full_prompt
        )
    
    return result.final_output

async def main():
    """
    Example usage of the MTG Collection Agent
    """
    # Example: Calculate collection value
    result1 = await process_collection_query("What is the total market value of my MTG collection?")
    print("\nCollection Value Query Result:")
    print(result1)
    
    # Example: Find cEDH decks with cards the user owns
    result2 = await process_collection_query(
        "Find cEDH decks where I already own at least 30% of the cards. Focus on information from edhtop16.com."
    )
    print("\nDeck Recommendation Query Result:")
    print(result2)
    
    # Example: Check if specific cards are in the collection
    result3 = await process_collection_query("Do I own any copies of Dockside Extortionist?")
    print("\nCard Ownership Query Result:")
    print(result3)

if __name__ == "__main__":
    asyncio.run(main())
