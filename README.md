### Search For:

- Which emebedding
- internal indices
- Parallel validadtion

# Setup and Usage

## Prerequisites

- Python 3.12+
- `uv` (Python package manager)

2. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Application

1. Make sure the run script is executable:

   ```bash
   chmod +x ./run.sh
   ```

2. Start the server:
   ```bash
   ./run.sh
   ```

## API Documentation

Import `api.json` into Postman
set the base URL to `http://localhost:8000`

--
or

Once the server is running, you can access the Swagger UI at:
[http://localhost:8000/docs](http://localhost:8000/docs)

<img width="579" height="708" alt="Screenshot 2025-11-30 at 11 40 29 AM" src="https://github.com/user-attachments/assets/99fee51f-0bba-4b9a-91c3-2ae0af556da3" />


