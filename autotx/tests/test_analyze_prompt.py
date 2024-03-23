from autotx.patch import patch_langchain
from autotx.utils.agent.build_goal import DefineGoalResponse, analyze_user_prompt

patch_langchain()

def test_with_missing_amount(auto_tx):
    response = analyze_prompt("Send ETH to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", auto_tx)
    assert response.type == "missing_info"

def test_with_missing_address(auto_tx):
    response = analyze_prompt("Send 1 ETH", auto_tx)
    assert response.type == "missing_info"

def test_invalid_goal(auto_tx):
    response = analyze_prompt("Hey", auto_tx)
    assert response.type == "unsupported" or response.type == "missing_info"

def test_not_yet_supported_goal(auto_tx):
    response = analyze_prompt("Send an NFT to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1", auto_tx)
    assert response.type == "unsupported"

def analyze_prompt(prompt, auto_tx) -> DefineGoalResponse:
    agents_information = auto_tx.get_agents_information()
    return analyze_user_prompt(prompt, agents_information)