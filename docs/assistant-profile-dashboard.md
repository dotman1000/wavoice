# Assistant profile and dashboard

WAVoice includes a mobile-friendly dashboard at `/dashboard` for configuring the default Gemini Live assistant.

## Configure access

Set these values in the private server environment (never commit real values):

- `WAVOICE_DASHBOARD_TOKEN`: a long, random bearer token required by the profile API.
- `WAVOICE_ASSISTANT_PROFILE_FILE`: optional path to the private JSON profile file. It defaults to `data/assistant-profile.json`.

The server creates the parent directory when saving. On POSIX systems it writes the file with owner-only permissions (0600), using an atomic replacement to avoid partially written profiles. The file contains only the allowlisted assistant profile fields, not Meta credentials or provider API keys. The default file is ignored by Git.

## Use the dashboard

1. Start the WAVoice server and open `https://YOUR_SERVER/dashboard`.
2. Enter the dashboard token.
3. Choose **Load from server** to load the current profile.
4. Edit the assistant name, greeting, role, approved knowledge, safety rules, language, Gemini voice, speaking style and handover guidance.
5. Choose **Save to server**. The server confirms only after the profile file has been written.

The saved profile is loaded when the server starts and applies to new calls. Existing calls keep the instructions with which they started. Keep the configured profile file on persistent storage: some hosting platforms erase local files when an instance is replaced or redeployed. For multiple server instances, configure a shared persistent store or keep instances synchronized.

## Security

- Use HTTPS. Treat the dashboard token like a password and never paste it into chat or commit it to Git.
- Keep Meta access tokens, app secrets and AI provider keys in environment variables or a managed secret store.
- Restrict dashboard access at the network or identity-provider layer where possible. The bearer token protects the API, but it is not a substitute for HTTPS, CSRF defenses, rate limiting or per-user authorization in a public multi-user deployment.
- Do not place passwords, payment card details, verification codes or unnecessary personal data in assistant knowledge.
- The assistant should identify itself as AI, use only approved knowledge for business-specific facts and offer a human handover when uncertain.

## Assistant behavior

The default Gemini Live handler uses this profile to construct its system instruction and opening greeting. Automatic language matching is an instruction to the model, not a guarantee of perfect detection. Test every language and voice with real calls before relying on them. Voice availability depends on the selected Gemini Live model.

Custom handlers registered with `@app.on_call` remain under the application developer's control and do not automatically consume this default profile.
