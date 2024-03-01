# # conftest.py
# import pytest
# from unittest.mock import patch, MagicMock
# from sage_agent.agents.erc20 import Erc20Agent

# @pytest.fixture
# def erc20_agent_mock():
#     with patch('sage_agent.agents.erc20.get_information', new_callable=MagicMock) as mock_get_information:
#         # Configure the MagicMock to return a specific value or to behave in a certain way
#         mock_get_information.return_value = '{"decimals": 8, "name": "MOCKED TOKEN", "symbol": "MTK"}'
#         yield Erc20Agent()  # Provide an instance of the mocked Erc20Agent