import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, ".env") });

// Centralized configuration object
export const config = {
  mongo: {
    uri: process.env.MONGO_URI,
    dbName: process.env.MONGO_DB_NAME,
    collectionName: process.env.MONGO_COLLECTION_NAME,
  },

  rabbitmq: {
    url: process.env.RABBITMQ_URL,
    queueName: process.env.RABBITMQ_QUEUE_NAME,
  },

  // Vendor-specific rate limits
  vendorConfig: {
    sync_vendor_a: { rate_limit_seconds: 5 },
    async_vendor_b: { rate_limit_seconds: 2 },
  },
};
