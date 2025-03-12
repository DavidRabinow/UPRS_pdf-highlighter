// Add this to your website
fetch('/.netlify/functions/getIp')
    .then(response => response.json())
    .then(data => {
        console.log('Visitor IP:', data.ip);
        // You can send this to your own server or database if needed
    });
