from __future__ import annotations

import pytest

from deploy_preview_authority import (
    Decision,
    DeployPreviewAuthority,
    DeploymentPromotionRequest,
    Environment,
    PromotionGrant,
)


def grant(**overrides):
    data = dict(
        grant_id="g1", project_id="p1", subject_id="release-bot",
        allowed_transitions=("preview->staging", "staging->production"),
        issued_at=100.0, not_after=200.0, source_deployment_id="d1", revoked=False,
    )
    data.update(overrides)
    return PromotionGrant(**data)


def req(source=Environment.PREVIEW, target=Environment.STAGING, **overrides):
    data = dict(project_id="p1", deployment_id="d1", source_environment=source,
                target_environment=target, subject_id="release-bot", now=150.0)
    data.update(overrides)
    return DeploymentPromotionRequest(**data)


def test_preview_to_staging_with_bound_grant_allows():
    receipt = DeployPreviewAuthority().evaluate(grant(), req())
    assert receipt.decision is Decision.ALLOW
    assert len(receipt.digest) == 64


def test_preview_can_never_jump_directly_to_production_even_if_grant_claims_it():
    g = grant(allowed_transitions=("preview->production",))
    receipt = DeployPreviewAuthority().evaluate(g, req(Environment.PREVIEW, Environment.PRODUCTION))
    assert receipt.decision is Decision.REFUSE
    assert "preview_to_production_forbidden" in receipt.reasons


def test_staging_to_production_requires_explicit_transition():
    denied = DeployPreviewAuthority().evaluate(
        grant(allowed_transitions=("preview->staging",)),
        req(Environment.STAGING, Environment.PRODUCTION),
    )
    assert denied.decision is Decision.REFUSE
    assert "transition_not_authorized" in denied.reasons


def test_revocation_is_immediate_and_fail_closed():
    authority = DeployPreviewAuthority()
    revoked = authority.revoke(grant())
    receipt = authority.evaluate(revoked, req())
    assert receipt.decision is Decision.REFUSE
    assert "grant_revoked" in receipt.reasons


@pytest.mark.parametrize(
    "g,r,reason",
    [
        (grant(not_after=120.0), req(now=121.0), "grant_expired"),
        (grant(project_id="other"), req(), "project_scope_mismatch"),
        (grant(subject_id="other"), req(), "subject_scope_mismatch"),
        (grant(source_deployment_id="other"), req(), "source_deployment_mismatch"),
    ],
)
def test_scope_freshness_and_deployment_binding_fail_closed(g, r, reason):
    receipt = DeployPreviewAuthority().evaluate(g, r)
    assert receipt.decision is Decision.REFUSE
    assert reason in receipt.reasons


def test_non_finite_clock_is_rejected():
    with pytest.raises(ValueError, match="non_finite_now"):
        DeployPreviewAuthority().evaluate(grant(), req(now=float("nan")))
