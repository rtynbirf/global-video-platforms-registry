# Security Policy

## Reporting a vulnerability

Use GitHub **Private vulnerability reporting** (Security tab → Report a vulnerability)
for anything exploitable. Public issues are fine for non-exploitable hygiene problems.

## Scope

In scope:
- Pipeline scripts in `scripts/` (probe, audit, export) and the CI workflow `.github/workflows/validate.yml`
- Accidentally committed credentials or session cookies in any tracked file or history

Out of scope:
- Availability of third-party platform domains listed in the dataset (we list URLs, we don't operate them)
- The dataset files themselves — for factual errors use the `Data correction` issue form instead

## Data license note

The registry is data (CC BY 4.0). Security policy covers the *code and repository*, not
the availability of the platforms it describes.
