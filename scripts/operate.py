#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deploy_preview_authority import (
    DeployPreviewAuthority,
    DeploymentPromotionRequest,
    Environment,
    PromotionGrant,
)


def main() -> int:
    authority = DeployPreviewAuthority()
    grant = PromotionGrant(
        grant_id="demo-grant",
        project_id="demo-project",
        subject_id="release-bot",
        allowed_transitions=("preview->staging",),
        issued_at=100.0,
        not_after=200.0,
        source_deployment_id="deploy-1",
    )
    request = DeploymentPromotionRequest(
        project_id="demo-project",
        deployment_id="deploy-1",
        source_environment=Environment.PREVIEW,
        target_environment=Environment.STAGING,
        subject_id="release-bot",
        now=150.0,
    )
    receipt = authority.evaluate(grant, request)
    print(json.dumps(receipt.as_dict(), sort_keys=True))
    return 0 if receipt.decision.value == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
