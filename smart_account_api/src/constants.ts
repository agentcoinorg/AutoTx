export const CHAIN_RPC_URL = process.env.CHAIN_RPC_URL as string;
export const SMART_ACCOUNT_OWNER_PK = process.env.SMART_ACCOUNT_OWNER_PK as string;
if (!CHAIN_RPC_URL) {
  throw new Error("CHAIN_RPC_URL is not set");
}

if (!SMART_ACCOUNT_OWNER_PK) {
  throw new Error("SMART_ACCOUNT_OWNER_PK is not set");
}
