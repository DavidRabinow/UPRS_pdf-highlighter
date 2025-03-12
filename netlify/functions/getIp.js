exports.handler = async function(event, context) {
    // Get the visitor's IP from Netlify's headers
    const ip = event.headers['x-nf-client-connection-ip'];
    const userAgent = event.headers['user-agent'];
    
    return {
        statusCode: 200,
        body: JSON.stringify({
            ip: ip,
            userAgent: userAgent,
            timestamp: new Date().toISOString()
        })
    };
}
