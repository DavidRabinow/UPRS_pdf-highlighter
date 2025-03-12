exports.handler = async function(event, context) {
    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
            success: true,
            visitors: [
                {
                    ip: event.headers['x-nf-client-connection-ip'],
                    userAgent: event.headers['user-agent'],
                    timestamp: new Date().toISOString()
                }
            ]
        })
    };
}
