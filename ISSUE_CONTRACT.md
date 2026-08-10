# Issue contract — Deploy Preview Authority

## Problem
Durable workflows, safe code execution, least-privilege tool access, and full-stack observability.

## Desired outcome
A bounded, open, testable implementation of **Deploy Preview Authority** that demonstrates Mint preview deploy grants with env scopes and auto-expire; revoke on policy break.

## Non-goals
- Vercel affiliation or proprietary integration
- Portfolio-wide scale/performance claims
- UI marketing site

## Acceptance
1. Mechanism module implements allow + refuse with structured receipts
2. pytest behavioral suite green
3. operate.py cold-start produces JSON receipt
4. Non-affiliation disclaimer preserved
