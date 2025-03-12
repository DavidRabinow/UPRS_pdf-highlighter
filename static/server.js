import express from "express";
import axios from "axios";

const app = express();
const PORT = process.env.PORT || 3000;

// Your Discord webhook URL
const DISCORD_WEBHOOK_URL =
  "https://discord.com/api/webhooks/1349497349814222888/hQcS1dI_pFIdraXrpttg6c9DZhf19VsUNm1UVXoCF2o4wtsbcJrixqnwk0KXn7TIWu-3";

// Serve static files from the 'static' directory
app.use(express.static("static"));

// Endpoint to log visitor IP
app.get("/log", (req, res) => {
  const ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress;

  // Send IP information to Discord
  axios
    .post(DISCORD_WEBHOOK_URL, {
      content: `Visitor IP: ${ip}`,
    })
    .then(() => {
      console.log(`IP sent: ${ip}`);
      res.send("Your IP has been logged successfully.");
    })
    .catch((err) => {
      console.error("Error sending to Discord:", err);
      res.status(500).send("Error logging IP.");
    });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
