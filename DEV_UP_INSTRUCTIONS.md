# DEV_UP_INSTRUCTIONS — implementation receipt

**Repository:** `GlacierEQ/vercel-deploy-preview-authority`  
**Company lens:** Vercel (independent; no affiliation)  
**Innovation:** Deploy Preview Authority

## Completed implementation

The generic scaffold has been replaced by a deterministic deployment-promotion authority with environment isolation, project/subject/deployment binding, expiration, revocation, and explicit transition scopes.

### Shipped boundaries

- preview → staging can be granted
- staging → production requires its own grant transition
- preview → production is structurally forbidden
- expired and revoked grants fail closed
- project, subject, and source deployment mismatches fail closed
- decisions emit deterministic receipts

## Verification contract

`python -m pytest -q` and `python scripts/operate.py` must pass for the current head. Those tests prove this reference model only, not control of a Vercel deployment.

## Remaining next gate

Bind the model to a disposable Vercel project and prove preview/staging isolation, revocation, and production promotion against real deployment metadata without changing the non-affiliation claim boundary.
