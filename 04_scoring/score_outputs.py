"""
Scoring script for POPE Audit.
Applies extraction rules (R1-R6) and failure rules (F1-F2) to frozen outputs.
"""
import os, json, glob
import pandas as pd

# Define extraction rules
def extract_r1(resp):
    resp = resp.strip()
    return "Yes" if resp == "Yes" else ("No" if resp == "No" else "Unparseable")

def extract_r2(resp):
    resp = resp.strip().lower()
    return "Yes" if resp == "yes" else ("No" if resp == "no" else "Unparseable")

def extract_r3(resp):
    resp = resp.strip().lower()
    return "Yes" if "yes" in resp else ("No" if "no" in resp else "Unparseable")

def extract_r4(row):
    resp = row["raw_response"].strip().lower()
    return "Yes" if resp.startswith("yes") else ("No" if resp.startswith("no") else "Unparseable")

def extract_r5(row):
    return "Yes" if row["yes_logprob"] > row["no_logprob"] else "No"

def extract_r6(resp):
    resp = resp.strip().lower()
    return "Yes" if "yes" in resp else ("No" if "no" in resp else "Unparseable")

def compute_metrics(df, pred_col, failure_rule):
    df["gt"] = df["ground_truth"].apply(lambda x: 1 if x.lower() == "yes" else 0)
    df["pred"] = df[pred_col].apply(lambda x: 1 if x == "Yes" else (0 if x == "No" else -1))
    
    if failure_rule == "F1": # Unparseable = Wrong
        df["correct"] = (df["pred"] == df["gt"]).astype(int)
    elif failure_rule == "F2": # Unparseable = Skip
        df = df[df["pred"] != -1].copy()
        df["correct"] = (df["pred"] == df["gt"]).astype(int)
        
    if len(df) == 0: return 0, 0, 0, 0, 0

    tp = len(df[(df["pred"]==1) & (df["gt"]==1)])
    fp = len(df[(df["pred"]==1) & (df["gt"]==0)])
    fn = len(df[(df["pred"]==0) & (df["gt"]==1)])
    tn = len(df[(df["pred"]==0) & (df["gt"]==0)])
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    acc = (tp + tn) / len(df) if len(df) > 0 else 0
    return acc, precision, recall, f1, len(df)

def main():
    out_dir = os.path.expanduser("~/Ridoy/Other_Projects/pope-audit/03_inference/outputs")
    files = sorted(glob.glob(os.path.join(out_dir, "qwen__*.jsonl")))
    all_results = []
    
    for f_path in files:
        template = os.path.basename(f_path).split("__")[1].replace(".jsonl", "")
        print(f"Scoring Template {template}...")
        rows = [json.loads(line) for line in open(f_path, 'r')]
        df = pd.DataFrame(rows)
        
        df["R1"] = df["raw_response"].apply(extract_r1)
        df["R2"] = df["raw_response"].apply(extract_r2)
        df["R3"] = df["raw_response"].apply(extract_r3)
        df["R4"] = df.apply(extract_r4, axis=1)
        df["R5"] = df.apply(extract_r5, axis=1)
        df["R6"] = df["raw_response"].apply(extract_r6)
        
        for r in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            for f in ["F1", "F2"]:
                acc, prec, rec, f1, n = compute_metrics(df, r, f)
                all_results.append({
                    "template": template, "rule": r, "failure_rule": f,
                    "accuracy": round(acc, 4), "precision": round(prec, 4),
                    "recall": round(rec, 4), "f1": round(f1, 4),
                    "unparseable_rate": round(len(df[df[r]=="Unparseable"])/len(df), 4) if r != "R5" else 0.0
                })

    results_df = pd.DataFrame(all_results)
    results_df.to_csv(os.path.expanduser("~/Ridoy/Other_Projects/pope-audit/04_scoring/results_summary.csv"), index=False)
    
    print("\n✅ Scoring complete. Results saved to 04_scoring/results_summary.csv")
    print("\n=== F1 SCORE BY TEMPLATE (R1 / F1) ===")
    print(results_df[(results_df["rule"]=="R1") & (results_df["failure_rule"]=="F1")][["template", "f1"]].to_string(index=False))

if __name__ == "__main__":
    main()
