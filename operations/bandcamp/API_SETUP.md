# Official Bandcamp API integration

Source: https://bandcamp.com/developer

## State
- Artist registered: https://auxkalo.bandcamp.com/
- API access: NOT CONFIRMED
- Client ID / secret: NOT PROVIDED
- Service deployed: NO
- Upload/publishing via API: NOT DOCUMENTED

## Approval
Bandcamp says labels and merchandise fulfillment partners must contact Bandcamp and briefly describe intended API usage. Once approved, API Access appears under Settings. Bandcamp issues the client ID and client secret; developers do not generate them themselves.

Suggested request (only send with user approval):

Subject: API access request — BANNED 21 RECORDS

Hello Bandcamp team,

I manage BANNED 21 RECORDS, an independent music label with the artist AUXkalo! (https://auxkalo.bandcamp.com/) and additional artists in development. I would like to request official API access to integrate account information and sales reporting into a private catalog management tool. We also want to understand whether an approved bulk-delivery method is available for digital album uploads.

Please let me know the eligibility requirements, supported endpoints and any costs or conditions.

Thank you,
BANNED 21 RECORDS

## Implementation
- `bandcamp_api.py`: Python standard-library OAuth token client using the documented client_credentials and refresh_token flows.
- Do not run initial_token more than once per grant: Bandcamp documents possible duplicate_grant errors.
- Store tokens and credentials only in secure environment variables/secret storage, never in GitHub.
- No paid infrastructure is required to keep code in GitHub.
- No audio uploads or releases are performed by this module.
