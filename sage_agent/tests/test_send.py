from textwrap import dedent
from sage_agent.agents.erc20 import Erc20Agent
from sage_agent.agents.safe import SafeAgent
from sage_agent.sage import Sage
from sage_agent.sage_temp import SageAgent

def test_encode_and_sign():
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
    erc20_agent = Erc20Agent()
    safe_agent = SafeAgent()
    sage = Sage([erc20_agent, safe_agent], None)
    response = sage.run(prompt)
    print(response)
