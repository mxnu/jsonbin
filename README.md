# JSONBin Clone

A simple JSON repository service built with FastAPI and Docker.

## Setup

1.  Clone this repository.
2.  Create a `.env` file from `.env.example`:
    ```bash
    cp .env.example .env
    ```
3.  Set your `API_TOKEN` in the `.env` file.

## Run with Docker

To build the image:
```bash
docker build -t jsonbin .
```

To run the container with a local volume for JSON storage:
```bash
docker run -d \
  --name jsonbin \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/my_data:/app/data \
  jsonbin
```

This will link the local `my_data` directory to the container's `/app/data` directory, making your JSON files persistent and accessible from outside the container.

## API Usage

All requests require the `Authorization` header: `Authorization: Bearer <YOUR_TOKEN>`.

### Create a new bin (Auto-generated ID)
```bash
curl -X POST http://localhost:8000/ \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Create a new bin (Custom ID)
```bash
curl -X POST http://localhost:8000/my-custom-id \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Get a bin
```bash
curl -X GET http://localhost:8000/my-custom-id \
  -H "Authorization: Bearer your-secret-token-here"
```

### Update a bin
```bash
curl -X PUT http://localhost:8000/my-custom-id \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"key": "new-value"}'
```

## Validation Rules
- `POST /{id}` will fail if the ID already exists (409 Conflict).
- IDs must be alphanumeric or contain hyphens (`^[a-zA-Z0-9\-]+$`).
- Bodies must be valid JSON.
