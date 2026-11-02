# VoteHub 2026 Early Vote Tracker data, retrieved 2026-11-02 ~21:45 UTC

The tracker page (https://votehub.com/2026-early-vote-tracker?state=wisconsin) is drawn by a script that loads public JSON
from https://cdn.votehub.com/early-vote-tracker/ (no login). Each file carries its own `updated_at`. VoteHub's modeled
2024 vote, primary history, race and turnout come from its voter-file models (methodology:
https://votehub.com/2026-early-vote-methodology/, saved as `methodology.html`). Not used by the model.

| File | URL |
|---|---|
| `catalog.json` | https://cdn.votehub.com/early-vote-tracker/catalog.json (the 16 states covered) |
| `wi_config.json` | https://cdn.votehub.com/early-vote-tracker/2026-general/wisconsin/config.json |
| `wi_toplines.json` | https://cdn.votehub.com/early-vote-tracker/2026-general/wisconsin/toplines.json |
| `wi_components.json` | https://cdn.votehub.com/early-vote-tracker/2026-general/wisconsin/components.json |
| `wi_gov_estimate.json` | https://cdn.votehub.com/early-vote-tracker/2026-general/wisconsin/races/G2026WI00/estimate.json |
| `states/<slug>_toplines.json` | https://cdn.votehub.com/early-vote-tracker/2026-general/<slug>/toplines.json for all 16 states |
| `methodology.html` | https://votehub.com/2026-early-vote-methodology/ |
