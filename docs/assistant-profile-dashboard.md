# Assistant profile and dashboard

The first personalization milestone adds a static, mobile-friendly dashboard at `dashboard/index.html`.

## What it does

- Edits the assistant name, opening greeting, role, approved knowledge and safety rules.
- Selects a preferred language or automatic caller-language matching.
- Selects one of the built-in Gemini voice names and a speaking style.
- Defines when the assistant should offer a human handover.
- Builds a complete instruction preview that can be copied.
- Saves a local draft in the browser only when the user taps **Save draft on this device**.

## Important limitations

This dashboard is a configuration editor, not a live control panel yet. It does not write settings to the Python server, connect to Meta, answer calls, or store API credentials. Browser-local drafts do not sync between devices.

The current Gemini Live agent in `src/wavoice/agents/gemini_live.py` accepts `system_instruction`, `voice`, and `greeting` parameters, but the current server startup path must be wired to a trusted server-side profile store before dashboard changes can affect real calls.

## Security and deployment

- Never put Meta access tokens, app secrets, or provider API keys in browser code or commit them to Git.
- Keep credentials in server environment variables or a managed secret store.
- Before public deployment, add authentication, CSRF protection for write endpoints, server-side validation, and per-account authorization.
- Do not expose caller audio, phone numbers, or conversation transcripts in a public dashboard.
- Tell callers they are speaking with an AI assistant. Offer a human callback for unknown, sensitive, or disputed matters.

## Open locally

Open `dashboard/index.html` in a modern browser. It is designed to work on mobile screens and does not require a build step.
