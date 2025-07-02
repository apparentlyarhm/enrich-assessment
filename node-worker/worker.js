import amqp from "amqplib";
import { MongoClient, UUID } from "mongodb";
import { config } from "./config.js";
import { callSyncVendor, callAsyncVendor } from "./vendors.js";

// --- Helper Functions ---
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const cleanData = (data) => {
  const PII_KEYS = ["personal_id", "user_email", "ssn"];
  const cleanedData = { ...data };

  PII_KEYS.forEach((key) => delete cleanedData[key]);

  for (const key in cleanedData) {
    if (typeof cleanedData[key] === "string") {
      cleanedData[key] = cleanedData[key].trim();
    }
  }

  console.log("Data cleaned successfully.");
  return cleanedData;
};

/**
 * So we dont really have much context as to what the worker is supposed to do, so we just mock a small logic i guess
 */
async function main() {
  console.log("Worker starting...");

  // Connect to MongoDB
  console.log("CS :: " + config.mongo.uri);
  const mongoClient = new MongoClient(config.mongo.uri);
  await mongoClient.connect();

  const db = mongoClient.db(config.mongo.dbName);
  const jobsCollection = db.collection(config.mongo.collectionName);

  console.log("Connected to MongoDB.");

  // Connect to RabbitMQ
  const rabbitConnection = await amqp.connect(config.rabbitmq.url);
  const channel = await rabbitConnection.createChannel();
  await channel.assertQueue(config.rabbitmq.queueName, { durable: true });
  // This ensures the worker only processes one message at a time.
  channel.prefetch(1);
  console.log(
    `Connected to RabbitMQ. Waiting for messages in queue: ${config.rabbitmq.queueName}`
  );

  // The main consumer function
  channel.consume(config.rabbitmq.queueName, async (msg) => {
    if (msg === null) {
      return;
    }

    let jobData;
    try {
      const messageBody = JSON.parse(msg.content.toString());
      const requestId = new UUID(messageBody.request_id); // Convert string to BSON UUID
      console.log(`Received job: ${requestId}`);

      jobData = JSON.parse(msg.content.toString());
      // Convert the string ID back into a BSON UUID for later use.
      jobData._id = new UUID(jobData._id);

      // Update status to PROCESSING
      await jobsCollection.updateOne(
        { _id: jobData._id },
        { $set: { status: "processing" } }
      );

      // Apply Rate Limit
      const rateLimit =
        config.vendorConfig[jobData.vendor]?.rate_limit_seconds || 1;
      console.log(
        `Applying rate limit of ${rateLimit}s for vendor '${jobData.vendor}'`
      );
      await sleep(rateLimit * 1000);

      if (jobData.vendor_type === "sync") {
        // we wait for the vendor then use its result
        const vendorResponse = await callSyncVendor(jobData.payload);

        const finalResult = cleanData(vendorResponse);

        await jobsCollection.updateOne(
          { _id: jobData._id },
          { $set: { status: "complete", result: finalResult } }
        );

        console.log(
          `Job ${jobData._id} [sync] completed successfully by worker.`
        );
      } else if (jobData.vendor_type === "async") {
        // This vendor uses a callback. The worker's only job is to submit the task.
        // We run this in the background (don't await it here) because the worker's
        // job is done once the submission is acknowledged.
        callAsyncVendor(jobData); // This function will later call our API
        console.log(
          `Job ${jobData._id} [webhook] submitted. Worker is finished with this message.`
        );
        // The job status remains "processing" until the webhook is called.
      } else {
        throw new Error(`Unknown vendor type: ${jobData.vendor_type}`);
      }

      // Acknowledge
      channel.ack(msg);
    } catch (error) {
      console.error(`Job ${jobData?._id || "unknown"} FAILED:`, error.message);

      if (jobData?._id) {
        await jobsCollection.updateOne(
          { _id: jobData._id },
          { $set: { status: "failed", result: { error: error.message } } }
        );
      }

      // dead-letter-queue when?
      channel.ack(msg);
    }
  });

  // Handle graceful shutdown
  process.on("SIGINT", async () => {
    console.log("Shutting down...");

    await channel.close();
    await rabbitConnection.close();
    await mongoClient.close();

    process.exit(0);
  });
}

main().catch((err) => {
  console.error("Worker failed to start:", err);
  process.exit(1);
});
