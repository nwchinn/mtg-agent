import asyncio

from agents import Agent, Runner, trace
from agents.tool import WebSearchTool

# Specialized MTG Agents

# cEDH Specialist
cedh_agent = Agent(
    name="cEDH Specialist",
    handoff_description="Specialist for competitive Commander (cEDH) format questions, deck building, and metagame analysis.",
    instructions="""You are a specialized cEDH MTG assistant, focusing on competitive Commander format.
    When searching for deck information, primarily use and reference information from:
    1. https://edhtop16.com/
    2. https://www.mtgtop8.com/
    
    For any cEDH commander or deck related questions, make sure to prioritize information from these sources.
    If these sources don't have the information, you can use other reputable MTG sources as a fallback.
    Always cite your sources when providing information.""",
    # model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="high")],
)

# Standard/Pioneer Specialist
standard_pioneer_agent = Agent(
    name="Standard/Pioneer Specialist",
    handoff_description="Specialist for Standard and Pioneer formats, current meta, deck building, and tournament results.",
    instructions="""You are a specialized MTG assistant for Standard and Pioneer formats.
    Focus on current meta decks, tournament results, and deck building advice for these formats.
    Primarily use information from:
    1. https://www.mtggoldfish.com/
    2. https://www.mtgtop8.com/
    
    Always cite your sources when providing information.""",
    # model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="high")],
)

# Modern/Legacy Specialist
modern_legacy_agent = Agent(
    name="Modern/Legacy Specialist",
    handoff_description="Specialist for Modern and Legacy formats, meta analysis, deck building, and tournament results.",
    instructions="""You are a specialized MTG assistant for Modern and Legacy formats.
    Focus on current meta decks, tournament results, and deck building advice for these formats.
    Primarily use information from:
    1. https://www.mtggoldfish.com/
    2. https://www.mtgtop8.com/
    
    Always cite your sources when providing information.""",
    # model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="high")],
)

# Rules Specialist
rules_agent = Agent(
    name="MTG Rules Specialist",
    handoff_description="Specialist for MTG rules questions, interactions, and official rulings.",
    instructions="""You are a specialized MTG rules assistant.
    Focus on answering rules questions, card interactions, and providing official rulings.
    Primarily use information from:
    1. https://mtg.fandom.com/wiki/
    2. https://scryfall.com/
    3. https://magic.wizards.com/en/rules
    
    Always cite specific rules when applicable and provide clear explanations.""",
    # model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="high")],
)

# Card Collection and Finance Specialist
finance_agent = Agent(
    name="MTG Finance Specialist",
    handoff_description="Specialist for card prices, market trends, collection management, and investment advice.",
    instructions="""You are a specialized MTG finance and collection assistant.
    Focus on card prices, market trends, collection management, and investment advice.
    Primarily use information from:
    1. https://www.tcgplayer.com/
    2. https://www.cardmarket.com/
    3. https://www.mtgstocks.com/
    
    Always provide current price information when available and note that prices are subject to change.""",
    # model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="high")],
)

# Triage Agent
triage_agent = Agent(
    name="MTG Triage Agent",
    instructions="""You are the main entry point for MTG-related questions.
    Analyze the user's question and direct it to the most appropriate specialist agent:
    
    1. For cEDH (competitive Commander) or EDH questions, deck building, or metagame analysis, direct to the cEDH Specialist.
    2. For Standard or Pioneer format questions, direct to the Standard/Pioneer Specialist.
    3. For Modern or Legacy format questions, direct to the Modern/Legacy Specialist.
    4. For rules questions, card interactions, or official rulings, direct to the MTG Rules Specialist.
    5. For questions about card prices, market trends, collection management, or investment advice, direct to the MTG Finance Specialist.
    
    If the question spans multiple domains, choose the most relevant specialist.
    If you're unsure, ask clarifying questions before making a handoff.""",
    handoffs=[cedh_agent, standard_pioneer_agent, modern_legacy_agent, rules_agent, finance_agent],
)

async def main():
    # Example using the triage system
    with trace("MTG Agent System"):
        result = await Runner.run(
            triage_agent,
            "What are the top 3 cEDH commanders right now and what makes them strong?"
        )
        print("\nTriage Result:\n")
        print(result.final_output)
        
        # Direct example with the cEDH specialist
        # cedh_result = await Runner.run(
        #     cedh_agent,
        #     "What are the best cards to include in a Najeela, the Blade-Blossom cEDH deck?"
        # )
        # print("\nDirect cEDH Specialist Result:\n")
        # print(cedh_result.final_output)
        
        # # Direct example with the rules specialist
        # rules_result = await Runner.run(
        #     rules_agent,
        #     "How does Dockside Extortionist interact with Panharmonicon?"
        # )
        # print("\nDirect Rules Specialist Result:\n")
        # print(rules_result.final_output)

if __name__ == "__main__":
    asyncio.run(main())