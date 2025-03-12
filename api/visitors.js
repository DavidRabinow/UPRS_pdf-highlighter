export default function(req, res) {
    const fs = require('fs');
    try {
        // Read the last 100 entries from the log file
        const logs = fs.readFileSync('visitors.log', 'utf8')
            .split('\n')
            .filter(line => line.trim())
            .slice(-100)
            .reverse();
        
        res.json({ success: true, logs });
    } catch (error) {
        res.status(500).json({ success: false, error: 'Failed to read visitor logs' });
    }
}
