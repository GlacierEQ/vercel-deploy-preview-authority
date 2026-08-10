# Deploy Preview Authority

Independent GlacierEQ portfolio exhibit aligned to **Vercel** operating themes.

> **Not affiliated.** This repository is not affiliated with, endorsed by, employed by, or deployed at Vercel. No proprietary access, production deployment, customer impact, or company partnership is claimed.

## Implemented mechanism

`DeployPreviewAuthority` models promotion as a scoped, expiring, revocable capability bound to a project, subject, source deployment, and explicit environment transition.

Hard boundaries:

- preview → production is always refused; production must be staged;
- grants expire and can be revoked immediately;
- project, subject, and deployment identity must match;
- transitions must be explicitly listed;
- same-environment promotion is refused;
- receipts bind decision, transition, deployment, authority, and reasons.

## Proof surface

- `src/deploy_preview_authority.py` — domain mechanism
- `tests/test_deploy_preview_authority.py` — isolation, staging, scope, expiry, revocation tests
- `scripts/operate.py` — direct preview → staging execution
- `.github/workflows/tests.yml` — pytest + operate CI

## Current boundary

This is a deterministic reference authority model using synthetic deployment identities. It does not call Vercel APIs or control a real project. A live disposable-project integration is the next evidence gate.
