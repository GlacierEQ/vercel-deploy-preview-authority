"""Deploy Preview Authority — independent reference implementation.

Models environment-isolated deployment promotion with explicit grants, expiry,
revocation, source-deployment binding, and a hard preview-to-production fence.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Decision(str, Enum):
    ALLOW = "ALLOW"
    REFUSE = "REFUSE"


class Environment(str, Enum):
    PREVIEW = "preview"
    STAGING = "staging"
    PRODUCTION = "production"


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class PromotionGrant:
    grant_id: str
    project_id: str
    subject_id: str
    allowed_transitions: tuple[str, ...]
    issued_at: float
    not_after: float
    source_deployment_id: str | None = None
    revoked: bool = False


@dataclass(frozen=True)
class DeploymentPromotionRequest:
    project_id: str
    deployment_id: str
    source_environment: Environment
    target_environment: Environment
    subject_id: str
    now: float


@dataclass(frozen=True)
class DeploymentAuthorityReceipt:
    decision: Decision
    reasons: tuple[str, ...]
    grant_id: str
    transition: str
    deployment_id: str
    digest: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "grant_id": self.grant_id,
            "transition": self.transition,
            "deployment_id": self.deployment_id,
            "digest": self.digest,
        }


class DeployPreviewAuthority:
    """Fail-closed authority for preview/staging/production transitions."""

    @staticmethod
    def transition_key(source: Environment, target: Environment) -> str:
        return f"{source.value}->{target.value}"

    def evaluate(self, grant: PromotionGrant, req: DeploymentPromotionRequest) -> DeploymentAuthorityReceipt:
        reasons: list[str] = []
        if not math.isfinite(req.now):
            raise ValueError("non_finite_now")
        if not all(math.isfinite(v) for v in (grant.issued_at, grant.not_after)):
            reasons.append("grant_time_invalid")
        if not grant.grant_id.strip() or not grant.subject_id.strip():
            reasons.append("grant_identity_missing")
        if grant.not_after <= grant.issued_at:
            reasons.append("grant_lifetime_invalid")
        if req.now < grant.issued_at:
            reasons.append("grant_not_active")
        if req.now > grant.not_after:
            reasons.append("grant_expired")
        if grant.revoked:
            reasons.append("grant_revoked")
        if req.project_id != grant.project_id:
            reasons.append("project_scope_mismatch")
        if req.subject_id != grant.subject_id:
            reasons.append("subject_scope_mismatch")
        if grant.source_deployment_id and req.deployment_id != grant.source_deployment_id:
            reasons.append("source_deployment_mismatch")
        if req.source_environment is req.target_environment:
            reasons.append("same_environment_transition")

        transition = self.transition_key(req.source_environment, req.target_environment)
        if transition not in grant.allowed_transitions:
            reasons.append("transition_not_authorized")

        # Production promotion must be staged. A preview grant can never jump the
        # isolation boundary directly into production, even if a malformed grant
        # claims that transition.
        if req.source_environment is Environment.PREVIEW and req.target_environment is Environment.PRODUCTION:
            reasons.append("preview_to_production_forbidden")

        body = {
            "grant_id": grant.grant_id,
            "project_id": req.project_id,
            "deployment_id": req.deployment_id,
            "subject_id": req.subject_id,
            "transition": transition,
            "issued_at": grant.issued_at,
            "not_after": grant.not_after,
            "revoked": grant.revoked,
            "decision": Decision.REFUSE.value if reasons else Decision.ALLOW.value,
            "reasons": reasons,
        }
        return DeploymentAuthorityReceipt(
            decision=Decision.REFUSE if reasons else Decision.ALLOW,
            reasons=tuple(reasons or ["transition_authorized"]),
            grant_id=grant.grant_id,
            transition=transition,
            deployment_id=req.deployment_id,
            digest=_digest(body),
        )

    @staticmethod
    def revoke(grant: PromotionGrant) -> PromotionGrant:
        return PromotionGrant(
            grant_id=grant.grant_id,
            project_id=grant.project_id,
            subject_id=grant.subject_id,
            allowed_transitions=grant.allowed_transitions,
            issued_at=grant.issued_at,
            not_after=grant.not_after,
            source_deployment_id=grant.source_deployment_id,
            revoked=True,
        )


Mechanism = DeployPreviewAuthority
