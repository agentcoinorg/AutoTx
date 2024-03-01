from textwrap import dedent
from sage_agent.sage import Sage
from sage_agent.sage_temp import SageAgent
from sage_agent.agents.erc20 import get_information
from unittest.mock import create_autospec

def test_encode_and_sign():
    prompt = dedent(
        """
        Create transaction to send 0.4 Cool Token (token address: 0x57c94aa4a136506d3b88d84473bf3dc77f5b51da)
        Then, you must sign and create a safe transaction
        """
    )
    create_autospec(get_information, return_value='fishy')
    sage = Sage([SageAgent.erc_20_agent(), SageAgent.safe_agent()], None)
    response = sage.run(prompt)
    print(response)
