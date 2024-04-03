def test_auto_tx_research_default_network(auto_tx):
    prompt = "What are the top 5 meme coins"
    response = auto_tx.run(prompt, non_interactive=True)
    print(response)


def test_auto_tx_research_optimism(auto_tx):
    prompt = "What are the top 5 meme coins in optimism"
    response = auto_tx.run(prompt, non_interactive=True)
    print(response)

def test_auto_tx_research_polygon(auto_tx):
    prompt = "What are the top 5 meme coins in polygon"
    response = auto_tx.run(prompt, non_interactive=True)
    print(response)
