import express, { Express, NextFunction, Request, Response } from "express";
import dotenv from "dotenv";
import { Hex, Transaction } from "@biconomy/account";
import { initClientWithAccount } from "./account-abstraction";
import { SMART_ACCOUNT_OWNER_PK } from "./constants";
import { privateKeyToAccount } from "viem/accounts";

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 7080;

app.use(express.json());

app.all('*', handleError(async (req: Request, res: Response, next: NextFunction) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

  //Trim and redirect multiple slashes in URL
  if (req.url.match(/[/]{2,}/g)) {
    req.url = req.url.replace(/[/]+/g, '/');
    res.redirect(req.url);
    return;
  }

  if (req.method === 'OPTIONS') {
    res.send(200);
  } else {
    console.log(`Request:  ${req.method} --- ${req.url}`);
    next();
  }
}));

app.use((req: Request, res: Response, next: NextFunction) => {
  res.on('finish', () => {
    console.log(`Response: ${req.method} ${res.statusCode} ${req.url}`);
  });
  next();
});

app.get("/api/v1/account/address", handleError(async (req: Request, res: Response) => {
  const chainId = parseInt(req.query.chainId as string);
  if (!chainId) {
    res.status(400).json({ error: "chainId is required" });
    return;
  }

  const { smartAccount } = await initClientWithAccount(SMART_ACCOUNT_OWNER_PK, chainId);

  const smartAccountAddress = await smartAccount.getAccountAddress();

  const result = smartAccountAddress;

  res.json(result);
}));

app.post("/api/v1/account/deploy", handleError(async (req: Request, res: Response) => {
  const chainId = parseInt(req.query.chainId as string);
  if (!chainId) {
    res.status(400).json({ error: "chainId is required" });
    return;
  }

  const { smartAccount } = await initClientWithAccount(SMART_ACCOUNT_OWNER_PK, chainId);

  const response = await smartAccount.deploy();

  const receipt = await response.wait();
  
  res.json(receipt.receipt.transactionHash)
}));

app.post("/api/v1/account/transactions", handleError(async (req: Request, res: Response, next: NextFunction) => {
  const chainId = parseInt(req.query.chainId as string);
  if (!chainId) {
    res.status(400).json({ error: "chainId is required" });
    return;
  }

  const transactions: TransactionDto[] = req.body;

  const { smartAccount } = await initClientWithAccount(SMART_ACCOUNT_OWNER_PK, chainId);

  const txs: Transaction[] = transactions.map((tx) => {
    return {
      to: tx.params.to,
      value: tx.params.value,
      data: tx.params.data,
    };
  });

  console.log(txs);

  const response = await smartAccount.sendTransaction(txs);

  console.log(response);

  const receipt = await response.wait();

  res.json(receipt.receipt.transactionHash);
}));

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});

type TransactionType = "send" | "approve" | "swap";
type TransactionDto = {
  type: TransactionType;
  summary: string;
  params: {
    from: string;
    to: string;
    value: string;
    data: string;
  };
};

export function handleError(callback: (req: Request<{}>, res: Response, next: NextFunction) => Promise<void>) {
  return function (req: Request<{}>, res: Response, next: NextFunction) {
    callback(req, res, next)
      .catch(next)
  }
}
