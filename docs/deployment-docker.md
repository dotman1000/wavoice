# Docker deployment

This guide prepares WAVoice for a persistent HTTPS hosting service. A phone or laptop is not required to keep the server running once it is deployed.

## Important before deploying

WhatsApp voice calling requires more than a web page:
- A Meta Developer app and eligible WhatsApp Business phone number with calling enabled.
- A valid Meta System User access token and the required WhatsApp permissions.
- A public, stable HTTPS URL that Meta can reach.
- Working WebRTC media networking. A host that only supports inbound HTTP may not be sufficient; confirm its UDP/WebRTC networking and outbound connectivity before paying for it.
- A Gemini API key for the built-in assistant.

The service is not guaranteed to be free. Persistent disks, always-on compute, network egress, and AI usage may be billed.

## Build and run

Build from the repository root:

```bash
docker build -t wavoice .
```

Run locally (replace placeholder values; never publish real secrets):

```bash
docker run --rm -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e PUBLIC_URL=https://voice.example.com \
  -e WHATSAPP_TOKEN=your_meta_token \
  -e WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id \
  -e WHATSAPP_WABA_ID=your_waba_id \
  -e WHATSAPP_APP_SECRET=your_meta_app_secret \
  -e GEMINI_API_KEY=your_gemini_key \
  -e WAVOICE_DASHBOARD_TOKEN=replace_with_a_long_random_secret \
  -e WAVOICE_ASSISTANT_PROFILE_FILE=/app/data/assistant-profile.json \
  -v wavoice-data:/app/data \
  wavoice
```

Use the host's equivalent of a persistent volume mounted at `/app/data`. Do not rely on a container's writable layer for assistant profile persistence; many platforms replace it during redeploys.

## Hosting platform settings

Configure these values in the hosting provider's private environment-variable/secret settings, not in Git:

| Variable | Required | Purpose |
| --- | --- | --- |
| `HOST` | Yes | Set to `0.0.0.0` so the platform can reach the server |
| `PORT` | Yes | Use the port assigned by the platform |
| `PUBLIC_URL` | Yes | Stable public HTTPS base URL, with no trailing slash |
| `WHATSAPP_TOKEN` | Yes | Meta System User access token |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes | WhatsApp Business phone-number ID |
| `WHATSAPP_WABA_ID` | Recommended | WhatsApp Business Account ID |
| `WHATSAPP_APP_SECRET` | Recommended | Enables webhook signature verification |
| `GEMINI_API_KEY` | Yes for built-in agent | Google AI API key |
| `WAVOICE_DASHBOARD_TOKEN` | Yes for remote dashboard saves | Long, random, private bearer token |
| `WAVOICE_ASSISTANT_PROFILE_FILE` | Yes | Set to `/app/data/assistant-profile.json` |

The provider must preserve the mounted volume across restarts and deployments. The app writes the profile file with restrictive permissions when the filesystem supports them.

## First start checklist

1. Deploy the Docker image with the variables above and a persistent volume.
2. Confirm the provider reports the service healthy and that `https://YOUR_DOMAIN/dashboard` loads.
3. In the dashboard, enter the private dashboard token and use **Load from server**. Save your profile.
4. Run `wavoice doctor` in the container or inspect startup logs to verify Meta credentials, calling status, and webhook registration.
5. Confirm Meta's webhook callback URL is exactly `https://YOUR_DOMAIN/webhook` and that the app is subscribed to the call events required by the current WhatsApp Calling API.
6. Make a controlled test call from a permitted test account. Check both audio directions, interruption handling, language detection, and disconnect behavior.
7. Restart/redeploy once and confirm the dashboard profile remains saved.

## Security

- Never commit `.env`, Meta tokens, Gemini keys, or dashboard tokens.
- Do not paste credentials into ChatGPT messages. Enter them only in your host's private secret manager.
- Use HTTPS only. Keep the dashboard token private and rotate it if exposed.
- Restrict access to the dashboard URL where possible. The token protects profile API reads/writes; it is not a substitute for network-level access controls.
- Do not store payment-card data, passwords, verification codes, or unnecessary sensitive caller information in assistant knowledge.
- Tell callers they are speaking with an AI assistant. Do not clone or imitate another person's voice without their explicit permission.

## WebRTC/networking warning

A successful HTTP health check does not prove that WhatsApp audio can flow. Before selecting a host, verify that it supports the UDP/WebRTC media behavior required by the WAVoice/Meta integration, plus outbound HTTPS access to Meta and Google. If the platform only proxies HTTP/TCP and blocks the required media traffic, the app may receive webhooks but calls can fail to establish or carry audio.

This deployment template does not create accounts, obtain Meta approval, generate credentials, purchase hosting, or place a live call. Those steps require the account owner's explicit actions.
