# BANNED 21 RECORDS — Bandcamp publishing preparation

Status: PREPARATION ONLY. No Bandcamp authentication, uploads, purchases or releases have been performed.

## Artist
- Display name: AUXkalo!
- Artist page: https://auxkalo.bandcamp.com/
- Label: BANNED 21 RECORDS
- Genre: Subno-Txunta / electro-punk / dance-punk
- Location: Bilbao, Basque Country, Spain
- Members: DANBA, TXO!, KAR-KAR, NAI-NAI
- CONFIRMED debut album title: KALIMOTXO DA BIDE BAKARRA! (correct spelling, with exclamation mark). Previous title Askatasuna eta Kalimotxoa is superseded.
- CONFIRMED new cover supplied in conversation on 2026-10-24: square press-conference photograph of four masked members, blue background, embroidered kalimotxo on ikurriña, black label strips. The uploaded image is not yet in GitHub; do not reuse the former album cover. Need to transfer the approved original image into repository and Bandcamp.
- Artist photo: /assets/artists/auxkalo-band.webp

## Safe release pipeline
1. Collect and validate mastered WAV files, original high-resolution artwork, track titles/order, credits, explicit flags and rights holder.
2. Generate a local release manifest and a report of missing data.
3. Generate platform-ready descriptions and tags without inventing credits or rights.
4. Authenticate using Bandcamp-supported authorization; never commit passwords, OAuth secrets, FTP credentials or browser session cookies.
5. Check Bandcamp-supported upload permissions. Official DDEX/FTP requires explicit onboarding and account approval; ordinary API access does not imply publishing rights.
6. Dry-run and review proposed changes before publication. Publishing, pricing and availability are separate explicit actions.
7. Do not provision Render or any paid resource by default. A scheduled server is not required for offline manifest generation.

## Artist copy (draft)
AUXkalo! es un cuarteto de Bilbao que hace Subno-Txunta: electrónica de fiesta, actitud punk y una incapacidad crónica para comportarse como adultos. DANBA, TXO!, KAR-KAR y NAI-NAI siguen anclados en los doce años. Ni en el funeral de su tía abuela consiguieron ponerse serios.

## Other artists (not yet registered on Bandcamp)
- Moderately Alive — synthpop / Hi-NRG — Dressed for Disaster.
- Something Numbers — punk / skate / pop-punk — album details require release-level verification.

## Important
A Bandcamp artist profile and a verified Bandcamp developer integration are different things. Do not claim API upload capability until confirmed. No automatic public release is currently possible from this repository.
