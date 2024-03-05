from textwrap import dedent
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.agents.uniswap import UniswapAgent
from sage_agent.sage import Sage
from sage_agent.patch import patch_langchain

patch_langchain()

def test_encode_transfer_and_sign_safe_transaction():
    prompt_simple = dedent(
        """
        Create transaction to send 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da)
        Then, you must sign and create a safe transaction
        """
    )

    prompt = dedent(
        """
        Create and sign a transaction in my safe to send 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da)
        to 0x1816d5Dd8a4081D64bd1518532440125438c79A6
        """
    )

    multiple_send_prompt = dedent(
        """
        I want to create a transaction in my safe which sends 10 CoolToken (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da) to 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 and 5 DAI to 0xAC39C85F4E54797e4909f70a302d9e11E428135D
        """
    )

    swap_prompt = dedent(
        """
        I want to swap 10 USDC to DAI and send 3 DAI to 0x1816d5Dd8a4081D64bd1518532440125438c79A6 from my safe with address 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da
        """
    )
    erc20_agent = Erc20Agent()
    safe_agent = SafeAgent()
    uniswap_agent = UniswapAgent()
    # {
    #     "erc20": Erc20Agent
    # }
    sage = Sage([erc20_agent, safe_agent, uniswap_agent], None)
    sage.run(swap_prompt)



