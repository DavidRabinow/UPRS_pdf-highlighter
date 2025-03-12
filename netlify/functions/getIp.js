const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
    // Get the visitor's IP from Netlify's headers
    const ip = event.headers['x-nf-client-connection-ip'];
    const userAgent = event.headers['user-agent'];
    const timestamp = new Date().toISOString();
    
    const visitorData = {
        ip,
        userAgent,
        timestamp
    };

    // Store visitor data in a JSON file
    const filePath = path.join(__dirname, 'visitorData.json');
    const existingData = fs.existsSync(filePath) ? JSON.parse(fs.readFileSync(filePath)) : [];
    existingData.push(visitorData);
    fs.writeFileSync(filePath, JSON.stringify(existingData));

    // Return the visitor data
    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify(visitorData)
    };
}
