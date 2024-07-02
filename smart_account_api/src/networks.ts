import { createGasEstimator } from "entry-point-gas-estimations";
import { GasEstimator } from "entry-point-gas-estimations/dist/gas-estimator/entry-point-v6/GasEstimator/GasEstimator";
import { CHAIN_RPC_URL } from "./constants";
import { getChain } from "@biconomy/account";

export function getNetwork(chainId: number): {
    bundlerUrl: string;
    rpcUrl: string;
    gasEstimator: GasEstimator;
    chain: any;
  } {
    return {
      bundlerUrl: getBundlerUrl(chainId),
      rpcUrl: CHAIN_RPC_URL,
      gasEstimator: createGasEstimator({
        rpcUrl: CHAIN_RPC_URL,
      }),
      chain: getChain(chainId),
    };
  }
  
function getBundlerUrl(chainId: number): string {
  return `https://bundler.biconomy.io/api/v2/${chainId}/dicj2189.wh1269hU-7Z42-45ic-af42-h7VjQ2wNs`;
}
