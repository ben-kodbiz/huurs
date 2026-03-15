from modules.llm.llm_engine import LMStudioLLM

llm = LMStudioLLM()

response = llm.ask("Explain sabr in Islam in 2 sentences.")

print(response)