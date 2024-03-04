FROM ghcr.io/foundry-rs/foundry

WORKDIR /anvil
EXPOSE 8545
ENTRYPOINT anvil --fork-url "https://mainnet.infura.io/v3/${INFURA_API_KEY}" --host 0.0.0.0