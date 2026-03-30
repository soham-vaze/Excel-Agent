from llm.ollama import call_ollama_json
from llm.prompt import INTENT_PROMPT
from agent.controller import run_agent

def build_prompt(user_input: str) -> str:
    return f"{INTENT_PROMPT}\nUser: {user_input}\nOutput:"

if __name__ == "__main__":
    # user_input = "What is id of Somesh?"

    # prompt = build_prompt(user_input)
    # response = call_ollama_json(prompt)

    # print("JSON RESPONSE:", response)

    while True:
        user_input = input("\n>> ")
        if user_input == "exit()":
            exit()
        response = run_agent(user_input)
        print("🤖:", response)