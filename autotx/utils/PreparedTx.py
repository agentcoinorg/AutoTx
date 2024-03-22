from web3.types import TxParams

class PreparedTx:
    summary: str
    tx: TxParams
    
    def __init__(self, summary: str, tx: TxParams):
        self.summary = summary
        self.tx = tx
