import asyncio

from agents import Agent, Runner, function_tool

def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

async def main():
    agent = Agent(
        name="Assistant",
        # description="A helpful assistant.",
        instructions="""You only respond in a dramatic fashion.""",
        model="gpt-4o-mini",
        tools=[function_tool(get_weather)],
    )

    result = await Runner.run(agent, "What is the weather in Detroit?")
    print(result)
    

if __name__ == "__main__":
    asyncio.run(main())
    