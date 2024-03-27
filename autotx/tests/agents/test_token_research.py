from autotx.agents.TokenResearchAgent import TokenResearchAgent


def test_token_research_agent():
    agent = TokenResearchAgent().agent_executor
    response = agent.run("What's the top gainer token in defi")
    print(response)