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
		try:
			api_key = os.getenv('OPENAI_API_KEY')
		except Exception as e:
			print(f"Error while getting API key: {e}")
			api_key = None
		return ChatOpenAI(model='gpt-4o', api_key=SecretStr(api_key))

	if llm_provider == "google":
		try:
			api_key = os.getenv('GEMINI_API_KEY')
		except Exception as e:
			print(f"Error while getting API key: {e}")
			api_key = None
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
task = '''
open up the excel file called demo and add up all the numbers in column C, but only include them in the sum if the corresponding row in column B contains 'NY' AND the corresponding row in column A matches whatever value is in cell A2.
'''

agent = Agent(
	task=task,
	llm=llm,
	controller=controller,
	use_vision=False,
	max_actions_per_step=5,
	max_failures=5
)


async def main():
	await agent.run(max_steps=10)

	# input('Press Enter to close the browser...')


asyncio.run(main())
