import os
import sys

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import asyncio

from mlx_use import Agent, ClaudeCLI
from pydantic import SecretStr
from mlx_use.controller.service import Controller


def set_llm(llm_provider:str = None):
	if not llm_provider:
		raise ValueError("No llm provider was set")

	if llm_provider == "claude-cli":
		return ClaudeCLI()

	if llm_provider == "OAI":
		api_key = os.getenv('OPENAI_API_KEY')
		return ChatOpenAI(model='gpt-4o', api_key=SecretStr(api_key))

	if llm_provider == "google":
		api_key = os.getenv('GEMINI_API_KEY')
		return ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp',  api_key=SecretStr(api_key))

# Try to set LLM based on environment variable or fallback to API providers
llm_provider = os.getenv('LLM_PROVIDER', '').lower()
if llm_provider == 'claude-cli':
	llm = set_llm('claude-cli')
elif llm_provider == 'google' and os.getenv('GEMINI_API_KEY'):
	llm = set_llm('google')
elif llm_provider == 'oai' and os.getenv('OPENAI_API_KEY'):
	llm = set_llm('OAI')
else:
	# Fallback to available API providers
	if os.getenv('GEMINI_API_KEY'):
		llm = set_llm('google')
	elif os.getenv('OPENAI_API_KEY'):
		llm = set_llm('OAI')
	else:
		raise ValueError("No LLM provider configured. Please set LLM_PROVIDER=claude-cli or provide API keys.")


controller = Controller()

task = 'calculate how much is 5 X 4 and return the result, then call done.'


agent = Agent(
	task=task,
	llm=llm,
	controller=controller,
	use_vision=False,
	max_actions_per_step=10,
)


async def main():
	await agent.run(max_steps=25)


asyncio.run(main())
