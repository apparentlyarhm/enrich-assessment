# enrich-assessment

This repo contains two main applications:

- **Python (FastAPI) Web Service**
- **Node.js Worker**
- **RabbitMQ** server (runs from a pre-made Docker image)
- **MongoDB** database (hosted on Atlas for convenience)

The `src` directory contains the Python code and its own virtual environment. The Node.js app is located in the `node-worker` directory and also uses its own environment.

## Getting Started- not using `compose.yaml`

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd enrich-assessment
   ```

2. **Set up environment variables:**

   - Copy `.env.example` to `.env` in both `src` and `node-worker` directories.
   - Fill in the required values (MongoDB URI, RabbitMQ connection, etc.).

3a. **Start RabbitMQ (Docker):**

```bash
docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

3b. **Start MongoDB (Docker):**

```bash
docker run -d --name mongo_db -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=example -v mongo_local_data:/data/db mongo:latest
```

The above 2 steps are intentionally kept straigtforward

4. **Install dependencies:**

   - **Python (from `src`):**
     ```bash
     cd src
     python -m venv venv
     source venv/bin/activate  # or venv\Scripts\activate on Windows
     pip install -r req.txt # or whatever I change the name into
     ```
   - **Node.js (from `node-worker`):**
     ```bash
     cd ../node-worker
     npm install
     ```

5. **Run the applications:**
   - **Start FastAPI service:**
     ```bash
     cd src
     uvicorn main:app --reload  # or we can also use the . notation for modules
     ```
   - **Start Node.js worker:**
     ```bash
     cd node-worker
     npm start
     ```

## Start the stack- using compose

Lucky if you are on windows. There is a handy `build.ps1` file that sets up the env for you. so just run it:

```bash
.\build.ps1
```

This assumes that a valid .env is created.

## Notes

- Ensure you have Python 3.8+ and Node.js 14+ installed.
- Docker should be installed
- We do not create users and access roles in both RMQ and Mongo for the sake of convenience.
- URIs are hardcoded in the compose because we are not deploying on cloud. If done that, then the URIs will be populated by something like terraform and used in CI/CD pipelines

---

**Disclaimer:**  
Load test is WIP
