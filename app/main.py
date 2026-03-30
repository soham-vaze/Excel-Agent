from agent.controller import run_agent

if __name__ == "__main__":
    while True:
        user_input = input("\n>> ")

        if user_input.lower() == "exit()":
            break

        response = run_agent(user_input)
        print("🤖:", response)