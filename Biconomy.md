# Biconomy Smart Accounts

## Description
AutoTx can be used with a Biconomy Smart Account.

## Getting started
First, add the private key of the account you want to use as the owner to the `.env` file. Use the variable `SMART_ACCOUNT_OWNER_PK`.
Since the private key is stored as plain text, it is recommended to use a test account.

Next, start the `smart_account_api`, run: `poetry run start-smart-account-api`. This API server will be used to interact with the Biconomy Smart Account.
You can run `poetry run stop-smart-account-api` to stop the server.

To start AutoTx, you can now run: `poetry run ask "my-prompt-here"`.

When running for the first time, you will be prompted to send funds to your new Biconomy Smart Account in order to pay for the gas fees.
```
Using Biconomy smart account: {SMART-ACCOUNT-ADDRESS}
Detected empty account balance.
To use your new smart account, please top it up with some native currency.
Send the funds to: {SMART-ACCOUNT-ADDRESS} on {NETWORK-NAME}
Waiting...
```
After sending the funds, AutoTx will automatically detect the balance and continue with the transaction.