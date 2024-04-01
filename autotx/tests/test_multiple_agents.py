def test_send_meme_coin(auto_tx):
    response = auto_tx.run(
        "Buy 1 eth of a memecoin with high trade volume",
        False,
    )

    print(response)


def test_buy_and_send_top_token_in_polygon(auto_tx):
    response = auto_tx.run(
        "Check the token with highest liquidity in Polygon, buy it using 1 eth and then send 20 percent of it to 0x61FfE691821291D02E9Ba5D33098ADcee71a3a17",
        False,
    )
    print(response)
