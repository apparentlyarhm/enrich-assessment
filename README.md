# enrich-assessment

This repo contains two main applications:

- **Python (FastAPI) Web Service**
- **Node.js Worker**
- **RabbitMQ** server (runs from a pre-made Docker image)
- **MongoDB** database (hosted on Atlas for convenience)

The `src` directory contains the Python code and its own virtual environment. The Node.js app is located in the `node-worker` directory and also uses its own environment.

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd enrich-assessment
   ```

2. **Set up environment variables:**

   - Copy `.env.example` to `.env` in both `src` and `node-worker` directories.
   - Fill in the required values (MongoDB URI, RabbitMQ connection, etc.).

3. **Start RabbitMQ (Docker):**

   ```bash
   docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

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

## Notes

- Ensure you have Python 3.8+ and Node.js 14+ installed.
- MongoDB is expected to be available via the Atlas connection string you provide, but IPs might have to be added (Might make it public temporarily, lets see)
- RabbitMQ runs locally via Docker.

---

**Disclaimer:**  
Deployment to production is still in progress. However, the main functionality works offline if set up correctly as described above.
