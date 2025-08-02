# DevLoop Meta-Project — Plan v0.1 (2025-08-02)

## Purpose

Harness existing codebases + hosted GPU (RunPod) to create a lean automation core that can eventually orchestrate _all_ other projects. Keep scope tight; evolve in clear, versioned phases.

---

## Phase 0 – Environment & Knowledge Base **(YOU ARE HERE)**

1. Create `DEV_MAN/` directory (planning hub, version-controlled). ✅
2. Capture project rules (already in `.cursor/rules/*.mdc`).
3. Collect RunPod account details & generate first GPU endpoint.
4. List candidate LangChain agent repos in your GitHub org.
5. Decide which agent repo will be the starting point (reuse; no green-field).

**Deliverables**

- `plan_runpod_endpoint_v0.1.md` (this doc)
- `runpod_notes.mdc` (endpoint specs & lifecycle policy)
- `agent_candidates.md` (shortlist of repos)

---

## Phase 1 – RunPod Endpoint & Cost Gate

Goal: fast, ephemeral 4090 endpoint accessible via HTTP; auto-shutdown ≤ 10 min idle.

Steps:

1. Pick template (Ollama or PyTorch base) in RunPod.
2. Pull `mistral:7b-instruct-q5_K_M` as default model (≈2–3 GB).
3. Expose `11434` (Ollama) or `8000` (FastAPI) depending on agent code.
4. Write webhook that:
   – `POST /control/start` → spins pod.
   – Polls until RUNNING.
   – `POST /control/stop` after idle timer.
5. Store endpoint + API key in `.env` (git-ignored).

---

## Phase 2 – LangChain Agent Integration

Goal: Adapt an existing repo; point it at `$RUNPOD_URL`; run a hello-world task.

Steps:

1. Fork selected repo into `devloop/agent/` (submodule or subtree).
2. Patch config: remote model URL & smaller model name.
3. Smoke-test locally on CPU.
4. CI job (GitHub Action) triggers pod, runs agent unit test, then shuts pod.

---

## Phase 3 – Tracking UI (Lightweight)

Goal: simple dashboard showing pod uptime, cost, and last 10 jobs.

Ideas:

- Start with Markdown log pushed to repo → rendered by GitHub Pages.
- Later swap for Streamlit hosted on cheap VPS.

---

## Versioning & Branch Strategy

- Main branch: `main` (always green).
- Planning docs evolve with `plan_vX.Y.md`; bump minor when phase completes.
- Implementation work under feature branches: `phase-1/runpod-endpoint`, etc.

---

## Out-of-Scope (for now)

- n8n flows
- CI test generation
- Multi-model routing (Bronze/Gold tiers)
- Fancy UI beyond MVP dashboard

---

## Next Actions

1. Finish `runpod_notes.mdc` – capture pod template & API key fields.
2. Generate list of LangChain agent repos (`agent_candidates.md`).
3. Decide on one repo → record decision here.

---

_Last updated: 2025-08-02_
