---
name: deployment-drift-investigator
description: "Investigate why a deployed app, cluster, or environment no longer matches expected behavior. Use when an app is offline, pods or rollouts look wrong, a deployment changed but the live system did not, or local/deployed parity needs evidence-only diagnosis."
---

# Deployment Drift Investigator

## Overview

Use this skill for evidence-first diagnosis of deployment drift, app outages, and environment mismatch. The goal is a short root-cause report with concrete next actions, not a guess and not a blind fix.

## When To Use

- App is offline, degraded, or serving stale behavior after a deploy or cluster recovery.
- Pods, deployments, services, ingress, or ArgoCD state do not match the expected release.
- Local and deployed environments differ and you need to find the source of drift.
- A frontend/backend change appears correct in code but not in the live environment.

## Workflow

1. Define the symptom in one sentence.
2. Scope the blast radius: app, namespace, environment, and time window.
3. Check live state first:
   - deployment status
   - pod health and restarts
   - service and ingress routing
   - recent rollout or image changes
4. Compare runtime config to expected config:
   - env vars
   - secrets/config maps
   - image tag or version
   - feature flags and base URLs
5. Inspect logs around the failure window.
6. Classify the issue as one of:
   - code
   - configuration drift
   - cluster/platform failure
   - auth/networking/routing
7. Report:
   - most likely cause
   - supporting evidence
   - what to verify next
   - whether a fix is safe now or needs more evidence

## Output Format

Return a concise report:
- symptom
- evidence
- likely cause
- confidence
- next action
- what to avoid changing yet

## Guardrails

- Prefer read-only investigation.
- Do not restart, patch, scale, or delete anything unless the user explicitly asks.
- If evidence is inconclusive, say so and name the next check that would reduce uncertainty most.
