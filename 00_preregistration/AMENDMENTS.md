# Amendments to Instruction_v2

This file records every change to the locked protocol after Instruction_v2 was frozen.
Silent edits to PREREGISTRATION.md are forbidden; all changes go here.

---

## A1.1 — Environment = `ridoy` (not `pope-audit`)

- **Date:** 2026-10-20
- **Section changed:** Instruction_v2 §2.3.6
- **What changed:** Use existing `ridoy` Conda env instead of creating new `pope-audit` env.
- **Why:** `ridoy` already has torch 2.7.1+cu118, transformers 5.20.1, bitsandbytes 0.50.2, accelerate 1.15.0, verified CUDA matmul. A new env would need ~8 GB PyPI downloads over slow network for zero benefit.
- **Violates hypothesis?** No
- **Violates fixed variable?** No (pins updated below)
- **How reported:** Reproducibility statement lists exact versions.

### A1.1.pins (recorded)

- Python 3.10.22
- torch 2.7.1+cu118
- transformers 5.20.1
- bitsandbytes 0.50.2
- accelerate 1.15.0
- huggingface_hub 2.2.0
- datasets 5.1.0
- numpy 2.2.6

---

## A1.2 — Download route = hf-mirror.com

- **Date:** 2026-10-20
- **What changed:** `HF_ENDPOINT=https://hf-mirror.com` with retries.
- **Why:** huggingface.co and cdn-lfs.huggingface.co blocked (DNS/timeout). modelscope.cn blocked (DNS). hf-mirror.com returns HTTP 307 → 200 on file paths, root DNS intermittently flaky.
- **Mitigation:** `HF_HUB_DOWNLOAD_TIMEOUT=120`, `HF_HUB_ETAG_TIMEOUT=30`, huggingface_hub built-in retries.
- **How reported:** Reproducibility statement.

---

## A1.3 — Tier declared after smoke test, not before

- **Date:** 2026-10-20
- **What changed:** Tier (T0/T1/T2/T3) declared AFTER Qwen smoke test + optional LLaVA/InternVL download attempts.
- **Why:** Only Qwen2.5-VL-7B confirmed cached (16.60 GB, 5 valid shards). LLaVA/InternVL need flaky-network downloads.
- **How reported:** Limitations, §Scope.

---

## A1.4 — Session manager = nohup (no tmux/screen)

- **Date:** 2026-10-20
- **What changed:** Long jobs use `nohup python script.py > log 2>&1 &`.
- **Why:** tmux and screen both absent; installing needs sudo (forbidden by manual §9).
- **Impact:** No detach/reattach; monitor via `tail -f`. SSH disconnect survives. Server reboot kills job — resume via `--resume`.
- **Mitigation:** Every long script MUST support `--resume` + per-line append writes.

---

## A1.3 — Tier Declared: T0 (Full Sweep)

- **Date:** 2026-10-20
- **Smoke Test Results:** Qwen2.5-VL-7B loaded in 12.9s. Peak VRAM = 6.12 GB. Throughput = 220.7 req/min.
- **Decision:** Given the massive VRAM headroom (10+ GB free) and high throughput (5x conservative estimate), the project will proceed with **T0**.
- **Scope:** 3 models (Qwen2.5-VL-7B, LLaVA-1.5-7B, InternVL2-8B) × 4 templates (P1, P3, P5, P6) × 3 splits = 108,000 generations.
- **Estimated Compute:** ~8-12 hours total, feasible for a single A4000 GPU overnight run.

---

## A1.5 — Tier T0 Downgraded to Tier T2 (Network Restriction)

- **Date:** 2026-10-20
- **What changed:** The scope is reduced to a single model (Qwen2.5-VL-7B). LLaVA-1.5-7B and InternVL2-8B are excluded.
- **Why:** The shared server's firewall/DNS blocks `us.aws.cdn.hf.co` (HuggingFace's AWS storage backend). While `hf-mirror.com` works for small metadata files, large 15GB weight downloads stall completely at ~100MB. LLaVA and InternVL cannot be downloaded.
- **Violates hypothesis?** No. The hypotheses (H1-H4) test harness sensitivity. 
- **How reported:** Limitations section will explicitly state: "Due to shared server network restrictions, only Qwen2.5-VL-7B could be evaluated. LLaVA and InternVL were excluded."

---

## A1.5 — Tier T0 Downgraded to Tier T2 (Network Restriction)

- **Date:** 2026-10-20
- **What changed:** The scope is reduced to a single model (Qwen2.5-VL-7B). LLaVA-1.5-7B and InternVL2-8B are excluded.
- **Why:** The shared server's network actively blocks large model downloads. We attempted: Direct HF (blocked), HF-Mirror via Python API (AWS CDN blocked), HF-Mirror via Git LFS (git-lfs not installed), HF-Mirror bypassing Xet (DNS timeout at 82%), and ModelScope (API 404). Only Qwen2.5-VL-7B is available in the local cache.
- **Violates hypothesis?** No. H1-H4 test harness sensitivity, which is valid on a single model.
- **How reported:** Limitations section will state the exact network restrictions.
