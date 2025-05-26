from agents import Agent, Runner, enable_verbose_stdout_logging
from pydantic import BaseModel
import asyncio

# Turn on for verbose logging
enable_verbose_stdout_logging()

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

math_tutor_agent = Agent(
    name="Math tutor",
    handoff_description="""Specialist agent for math questions.""",
    instructions="""You provide help with math problems. Explain your reasoning at each step and include examples.""",
    output_type=HomeworkOutput,
)

history_tutor_agent = Agent(
    name="History tutor",
    handoff_description="""Specialist agent for history questions.""",
    instructions="""You provide help with history questions. Explain important events and include examples.""",
    output_type=HomeworkOutput,
)
    
triage_agent = Agent(
    name="Triage agent",
    instructions="""Handoff to the appropriate agent based on the type of question from the user's homework question.""",
    handoffs=[math_tutor_agent, history_tutor_agent],
)
    
async def main():
    output = await Runner.run(triage_agent, "What is 5 x 5?")
    print(output.final_output)
    
if __name__ == "__main__":
    asyncio.run(main())