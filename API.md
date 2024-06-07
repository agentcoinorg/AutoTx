# API server

## Description
The API server can be used by applications to create and retrieve tasks, and send transactions. The server is responsible for managing the tasks and transactions, and for interacting with the blockchain.

## Getting started
To start the supabase database, run: `npx supabase db start`
You can run `npx supabase stop` to stop the database at any time.

Run the below command to create a new application record in the db and get the API key:
`poetry run new_app -n <app_name>`

To start the API server, run: `poetry run serve`

## Routes

### Public routes
Below is a list of the public routes that can be accessed without authentication.

- `GET /api/v1/networks`: Retrieves a list of supported networks.
- `GET /api/v1/version`: Retrieves the current version of the API.

### Authenticated routes
Below is a list of the authenticated routes that can be accessed by applications that have been authorized.
To make authenticated requests, you need to include the `Authorization` header with the value `Bearer <application_api_key>`.

- `POST /api/v1/tasks`: Creates a new task and starts it in the background.
- `POST /api/v1/connect`: Connects a user to the application, creating a new user if necessary.
- `GET /api/v1/tasks`: Retrieves all tasks for the authorized application.
- `GET /api/v1/tasks/{task_id}`: Retrieves a task by its ID.
- `GET /api/v1/tasks/{task_id}/transactions`: Retrieves the transactions associated with a specific task.
- `POST /api/v1/tasks/{task_id}/transactions`: Sends the transactions of a completed task.