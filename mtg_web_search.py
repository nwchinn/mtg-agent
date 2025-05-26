import asyncio

from agents import Agent, Runner, trace
from agents.tool import WebSearchTool
from openai.types.responses import ResponseTextDeltaEvent

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
    Only use information from:
    1. https://www.tcgplayer.com/
    
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
    model="gpt-4o-mini",
    handoffs=[cedh_agent, standard_pioneer_agent, modern_legacy_agent, rules_agent, finance_agent],
)

async def main():
    # Example using the triage system
    with trace("MTG Agent System"):
        # Streaming Response 
        # result = Runner.run_streamed(
        #     triage_agent,
        #     "List cards that have risen over 20% in value the last month."
        # )
        # async for event in result.stream_events():
        #     if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
        #         print(event.data.delta, end="", flush=True)
        
        # Final Output Response
        question_result = await Runner.run(
            triage_agent,
            "List cards that have risen over 20% in value the last month."
        )
        print("\nTriage Result:\n")
        print(question_result.final_output)
        
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