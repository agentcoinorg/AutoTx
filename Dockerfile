FROM ghcr.io/foundry-rs/foundry

WORKDIR /anvil
EXPOSE 8545
ENTRYPOINT anvil --fork-url $CHAIN_RPC_URL --host 0.0.0.0
