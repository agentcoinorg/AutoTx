import { BiconomySmartAccountV2, createSmartAccountClient } from "@biconomy/account";
import { WalletClient, createWalletClient, Hex, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { getNetwork } from "./networks";

export async function initClientWithAccount(ownerPk: string, chainId: number): Promise<{
  client: WalletClient;
  smartAccount: BiconomySmartAccountV2;
  }> {
  const { chain, bundlerUrl } = getNetwork(chainId);
  
  const client = createWalletClient({
    account: privateKeyToAccount(ownerPk as Hex),
    chain: chain,
    transport: http(),
  });

  const smartAccount = await createSmartAccountClient({
    signer: client,
    bundlerUrl,
  });

  return {
    client,
    smartAccount,
  }
};
