# Master Plan — DevLoop Automation Core (v1)

_Last updated: 2025-08-02_

This master plan consolidates **what** we are building and **how** we will build it, using RunPod for GPU inference and a controller-API pattern so multiple agents (Cursor, CLI, future Slack bots) can cooperate safely.

---

## 0 High-Level Vision

Build a parent repository `devloop/` that:

1. Spins up GPU pods on RunPod **only when needed**.
2. Exposes a small REST controller so every agent talks through the same gateway.
3. Re-uses an existing LangChain agent repo (no green-field) for inference logic.
4. Tracks cost / uptime with a lightweight dashboard.
5. Enforces collaboration rules so multiple AI agents follow the same branching, review, and cost policies.

References:
• Personal profile & preferences — `MARK/WHoIam.md`
• Cursor rule set — `.cursor/rules/*.mdc`

---

## 1 Repository Structure (monorepo)

```
 devloop/
 ├── DEV_MAN/            # planning + governance (this folder)
 │   ├── active/         # exactly ONE live plan file
 │   └── completed/      # archive
 ├── infra/
 │   └── controller/     # RunPod API proxy (FastAPI)
 ├── agent/              # fork of chosen LangChain repo (submodule)
 ├── n8n/                # workflow JSON (added later)
 ├── docs/               # diagrams & public docs
 └── .github/workflows/  # CI pipelines
```

---

## 2 RunPod Setup (Phase 1)

### SSH vs API Usage

• **API** (preferred for agents) – All tooling (Cursor, CLI, Slack bot) interacts via the Controller REST API. Human developers rarely need direct RunPod API calls.
• **SSH** – Only used for one-off maintenance (e.g., inspecting logs, manual updates inside the container). Add your public key once; daily operations rely on HTTP.

### Template Recommendation _(added 2025-08-02)_

Start with the community **"ollama template"** (simple, CUDA-ready, minimal footprint). Alternative templates like "Local Lab Ollama API and OpenWebUI" add a GUI you don’t need for automated agents.

After confidence grows, you can switch the controller to spawn serverless Flex endpoints or a custom Dockerfile.

1. **Create Pod Template**
   • GPU : RTX 4090 (24 GB)
   • Template : "Ollama" or PyTorch 2.8 base
   • Disk : 80 GB
   • Expose : Port 11434 (Ollama)
   • Pricing : On-Demand $0.69/hr (switch to Flex in Phase 2)
2. **Account Prereqs**
   □ GitHub linked (done)
   □ Payment method ($25 credit OK)
   □ Add SSH public key
   □ Generate `RUNPOD_API_KEY`
3. **Controller API**
   • Endpoint routes:
   - `POST /infer` {prompt, model}
   - `GET  /status` returns pod state & cost metrics
   - `POST /shutdown` manual stop
     • Auto-shutdown timer: 10 min idle
4. **Secrets**
   • `.env` (git-ignored):
   ```env
   RUNPOD_API_KEY=...
   CONTROLLER_URL=https://controller.my.domain
   ```

---

## 3 LangChain Agent Integration (Phase 2)

1. **Select Repo**
   • Use `significant-gravitas/Auto-GPT` **or** your own agent repo.
2. **Fork or Submodule** into `agent/`.
3. Patch config to hit `$CONTROLLER_URL/infer` instead of local model.
4. Add minimal `tasks.py` that sends prompts + receives JSON result.

---

## 4 Branching & Workflow

• `main` — always green, protected.
• `dev` — staging branch; autos from CI.
• `phase-X/feature-name` — short-lived feature branches.
• PR rules enforced by GitHub:
– CI green gate (`ruff`, `pytest`, idle-spend unit test)
– At least one human or senior-agent review.
• **Exactly one** active plan file enforced by pre-commit hook + CI script.

---

## 5 Metrics & Guardrails

| Metric                  | Target         | Source                     |
| ----------------------- | -------------- | -------------------------- |
| Idle-Spend Ratio        | ≤ 10 %         | controller logs            |
| Pod Spin-Up Latency     | ≤ 60 s         | controller → RunPod status |
| Inference RTT (256 tok) | ≤ 3 s p95      | agent timing               |
| Plan-Drift              | 0              | CI script                  |
| $/Job                   | downward trend | monthly summary            |

---

## 6 Roadmap Checklist

✅ Phase 0 — Planning artefacts committed
⏳ Phase 1 — Controller skeleton & first pod spin-up (test pod running: jizx51pkriengc)
⬜ Phase 2 — Agent fork & integration test
⬜ Phase 3 — Metrics dashboard & cost gate
⬜ Phase 4 — n8n orchestration

---

## 7 Next Immediate Tasks

1. Finish `infra/controller/` FastAPI scaffold
2. Complete `DEV_MAN/runpod_notes.mdc` (mark SSH/key steps)
3. Create `agent_candidates.md` list & choose starter repo
4. Write pre-commit hook enforcing single active plan

---

End of file
