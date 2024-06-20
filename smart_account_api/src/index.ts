import express, { Express, Request, Response } from "express";
import dotenv from "dotenv";
import {
  Account,
  Address,
  Hex,
  WalletClient,
  createWalletClient,
  http,
} from "viem";
import { polygon, sepolia } from "viem/chains";
import { BiconomySmartAccountV2, createSmartAccountClient, Transaction } from "@biconomy/account";
import { createGasEstimator } from "entry-point-gas-estimations";
import { GasEstimator } from "entry-point-gas-estimations/dist/gas-estimator/entry-point-v6/GasEstimator/GasEstimator";

dotenv.config();

const bundlerUrl = process.env.BUNDLER_URL || "http://localhost:3001";

const app: Express = express();
const port = process.env.PORT || 3000;

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});

function getNetwork(chainId: string): {
  bundlerUrl: string;
  rpcUrl: string;
  gasEstimator: GasEstimator;
  chain: any;
} {
  switch (chainId) {
    case "137":
      return {
        bundlerUrl,
        rpcUrl: polygonRpcUrl,
        gasEstimator: createGasEstimator({
          rpcUrl: polygonRpcUrl,
        }),
        chain: polygon,
      };
    case "31337":
      return {
        bundlerUrl,
        rpcUrl: sepoliaRpcUrl,
        gasEstimator: createGasEstimator({
          rpcUrl: sepoliaRpcUrl,
        }),
        chain: sepolia,
      };
    default:
      throw new Error("Invalid network");
  }
}

type CustomTransactionType = "send" | "approve" | "swap";
type CustomTransaction = {
  type: CustomTransactionType;
  summary: string;
  params: {
    from: string;
    to: string;
    value: string;
    data: string;
  };
};

async function initAA(owner: Account | Address, chainId: string): Promise<{
  client: WalletClient;
  smartAccount: BiconomySmartAccountV2;
}> {
  const { chain, bundlerUrl } = getNetwork(chainId);
  
  const client = createWalletClient({
    account: owner,
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

app.get("/api/v1/account/address", async (req: Request, res: Response) => {
  const owner: Address = req.query.owner as Address;
  const chainId = req.query.chainId as string;

  const { smartAccount } = await initAA(owner, chainId);
  
  const smartAccountAddress = await smartAccount.getAccountAddress();

  const result = smartAccountAddress;

  res.json(result);
});

app.post("/api/v1/account/deploy", async (req: Request, res: Response) => {
  const owner: Address = req.query.owner as Address;
  const chainId = req.query.chainId as string;

  const { smartAccount } = await initAA(owner, chainId);

  const response = await smartAccount.deploy();

  const receipt = await response.waitForTxHash();
  
  res.json(receipt.transactionHash);
});

app.post("/api/v1/account/transactions", async (req: Request, res: Response) => {
  const owner: Address = req.query.owner as Address;
  const chainId = req.query.chainId as string;

  const transactions: CustomTransaction[] = req.body.transactions;

  const { smartAccount } = await initAA(owner, chainId);

  const txs: Transaction[] = transactions.map((tx) => {
    return {
      to: tx.params.to,
      value: tx.params.value,
      data: tx.params.data,
    };
  });

  const response = await smartAccount.sendTransaction(txs);
  const receipt = await response.waitForTxHash();
  
  res.json(receipt.transactionHash);
});
