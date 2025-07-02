// Helper to simulate waiting
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// More vendors can be added or "registered" here

/**
 * Simulates a slow, synchronous vendor call.
 */
export async function callSyncVendor(payload) {
  console.log(`Calling SLOW SYNC VENDOR with payload:`, payload);

  await sleep(10000); // Lets say this method is doing something and takes 10s. this is vendor's logic

  console.log("Sync vendor call finished.");

  return {
    source: "sync_vendor_a",
    raw_data: `  Processed: ${payload.data}  `,
    personal_id: "ssn_123-45-6789", // PII to be removed
  };
}

/**
 * Simulates a modern, non-blocking asynchronous vendor call.
 */
export async function callAsyncVendor(jobData) {
  console.log(`Submitting job ${jobData._id} to WEBHOOK VENDOR.`);

  // The vendor instantly acknowledges the request.
  console.log(
    `Vendor acknowledged job ${jobData._id}. The worker is now free.`
  );

  // --- The Vendor's "Background" Process ---
  // we'll simulate the vendor taking 10 seconds to do its work- this will happen on the vendor's side.
  await sleep(10000); // some logic is taking 10s

  // now the vendor is done. it has a result.
  const finalData = {
    request_id: jobData._id.toString(), // The vendor must send our ID back
    data: {
      final_output: `Webhook result for payload: ${jobData.payload.data}`,
      vendor_metadata: "some-info-from-vendor",
    },
  };

  // The vendor makes a POST request to our FastAPI webhook endpoint.
  // For this to work, your FastAPI app must be running.
  try {
    const webhookUrl = `http://localhost:1234/vendor-webhook/${jobData.vendor}`;

    await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(finalData),
    });

    console.log(
      `[VENDOR SIMULATION] Successfully called webhook for job ${jobData._id}`
    );
  } catch (error) {
    console.error(
      `[VENDOR SIMULATION] FAILED to call webhook for job ${jobData._id}:`,
      error.message
    );
    // In a real system, the vendor would have its own retry logic here.
  }
}
