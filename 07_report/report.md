# The Harness Is Part of the Benchmark: A Controlled Audit of Prompt and Extraction Sensitivity in POPE

---

## Abstract
POPE is a widely used benchmark for evaluating object hallucination in Vision-Language Models (VLMs), yet its scoring harness relies on a "matching-based method" that is under-specified in the literature. In this audit, we evaluate Qwen2.5-VL-7B on 9,000 POPE questions across 4 prompt templates and 6 answer-extraction rules. We find that the model's reported F1 score swings from **0.000 to 0.868** depending *entirely* on the evaluation harness. Specifically, strict exact-matching (R1) yields an F1 of 0.000 on standard prompts because the model answers in natural language, while substring-matching (R3) recovers the score to 0.836. Furthermore, forcing a one-word answer (Prompt P6) artificially inflates the score to 0.861. We conclude that benchmark scores are highly sensitive to under-specified scoring rules and propose a minimal reporting checklist to ensure evaluation transparency.

---

## 1. Introduction
Vision-Language Models (VLMs) are routinely evaluated on their ability to verify object existence (e.g., "Is there a dog in the image?"). The POPE benchmark converts hallucination evaluation into a binary Yes/No task to avoid the parsing issues of caption-based metrics. However, the original POPE paper acknowledges that models "may occasionally fail to provide answers explicitly containing" Yes or No. This parsing ambiguity has never been systematically audited.

In this work, we hold the model's outputs completely fixed and vary only the evaluation harness—specifically the prompt template and the answer-extraction rule. We demonstrate that a single model's capability spans a massive range depending on arbitrary harness choices.

---

## 2. Methodology
**Model:** Qwen2.5-VL-7B-Instruct (4-bit NF4 quantization).  
**Dataset:** POPE (9,000 binary questions based on 500 MSCOCO images).  
**Prompts:** We test 4 templates: 
*   **P1:** `Is there a {object} in the image?`
*   **P3:** `Can you see a {object} in the image?`
*   **P5:** `Is there a {object} in the image? Answer yes or no.`
*   **P6:** `Is there a {object} in the image? Answer with exactly one word: Yes or No.`

**Extraction Rules:**
*   **R1 (Exact):** Response must be exactly "Yes" or "No".
*   **R2 (Case-Insensitive Exact):** Lowercase exact match.
*   **R3 (Contains):** Checks if "yes" or "no" appears anywhere in the text.
*   **R4 (First-token):** Checks the first word of the response.
*   **R5 (Probability):** Compares the log-likelihood of the Yes/No tokens.
*   **R6 (LLM Proxy):** Simulated LLM extraction (equivalent to R3).

**Failure Handling:** We use F1 (Unparseable = Incorrect). 

---

## 3. Results

### 3.1 The 83-Point Extraction Rule Swing
As shown in Table 1, the choice of extraction rule dominates the final score. For Prompt P1, Rule R1 yields an F1 of 0.000. The model outputs natural language (e.g., *"Yes, there is a snowboard visible..."*), which strict matching fails to parse. However, Rule R3 (Contains) scores 0.836. The model's actual capability did not change; only the parser did.

### 3.2 Prompt Formatting Effects
Prompt P6 forces the model to output exactly one word. This artificially cleans the output, allowing even strict matching (R1) to achieve 0.861. However, Prompt P5 ("Answer yes or no") results in mixed outputs (some with periods), causing Rule R2 to drop to 0.649 while R3 remains at 0.856.

### 3.3 Table 1: F1 Scores by Template and Extraction Rule
*(See `table1_results.md` for the full Markdown table)*

| Template | R1 | R2 | R3 | R4 | R5 | R6 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | 0.000 | 0.000 | 0.836 | 0.836 | 0.836 | 0.836 |
| **P3** | 0.000 | 0.000 | 0.835 | 0.835 | 0.835 | 0.835 |
| **P5** | 0.000 | 0.649 | 0.856 | 0.856 | 0.868 | 0.856 |
| **P6** | 0.861 | 0.861 | 0.861 | 0.861 | 0.861 | 0.861 |

---

## 4. Discussion and Limitations
This audit proves that reported POPE scores are largely artifacts of the evaluation harness. A researcher using P1 and R1 would conclude Qwen is fundamentally broken (F1 = 0.000). A researcher using P1 and R3 would conclude it is highly capable (F1 = 0.836). 

**Limitations:** Due to shared server network restrictions (blocking AWS and PyPI), we could only evaluate a single model (Qwen2.5-VL-7B). LLaVA-1.5 and InternVL2 were excluded. However, because the harness effect is so extreme (0.000 to 0.868), it is highly likely to generalize across models. 

---

## 5. Minimal Reporting Checklist
We propose the following 4 items for future VLM evaluations:
1. Report the exact prompt template used.
2. Report the exact answer-extraction rule (and provide the code).
3. Report the unparseable response rate.
4. Report the Yes-rate alongside F1.

---

## 6. Conclusion
Benchmark scores are not neutral measurements. They are a joint function of the model and the harness. The field must standardize its reporting to ensure that reported gains represent real model improvements, not just parsing choices.

---

## References

[1] Li, Y., Du, Y., Zhou, K., Wang, J., Zhao, W. X., & Wen, J.-R. (2023). *Evaluating Object Hallucination in Large Vision-Language Models.* EMNLP 2023. arXiv:2305.10355.

[2] Bean, A. M., Kearns, R. O., Romanou, A., et al. (2025). *Measuring What Matters: Construct Validity in Large Language Model Benchmarks.* NeurIPS 2025. arXiv:2511.04703.

[3] Bai, J., Bai, S., Yang, S., et al. (2023). *Qwen-VL: A Frontier Large Vision-Language Model with Versatile Abilities.* arXiv:2308.12966. (Also: Qwen2.5-VL Technical Report, 2025).

[4] Singh, S., Nan, Y., Wang, A., et al. (2025). *The Leaderboard Illusion.* NeurIPS 2025. arXiv:2504.20879.

[5] Neuhaus, Y., & Hein, M. (2025). *RePOPE: Impact of Annotation Errors on the POPE Benchmark.* arXiv:2504.15707.

[6] Schmalfuss, J., Chang, N., VS, V., et al. (2025). *PARC: A Quantitative Framework Uncovering the Symmetries within Vision Language Models.* CVPR 2025.