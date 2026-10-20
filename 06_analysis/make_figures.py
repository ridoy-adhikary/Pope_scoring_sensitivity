import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
out_dir = os.path.expanduser("~/Ridoy/Other_Projects/pope-audit/06_analysis")
df = pd.read_csv(os.path.expanduser("~/Ridoy/Other_Projects/pope-audit/04_scoring/results_summary.csv"))
df = df[df['failure_rule'] == 'F1'] # Focus on F1 for now

# Figure 1: Prompt Sensitivity by Rule
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='template', y='f1', hue='rule', marker='o', palette='tab10')
plt.title("Prompt Sensitivity across Extraction Rules (Qwen2.5-VL-7B)", fontsize=14)
plt.ylabel("F1 Score")
plt.xlabel("Prompt Template")
plt.ylim(-0.05, 1.05)
plt.legend(title="Extraction Rule", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig1_prompt_sensitivity.png"), dpi=300)
plt.close()
print("Saved Fig 1: Prompt Sensitivity")

# Figure 2: Extraction Rule Attribution (Focus on P1)
plt.figure(figsize=(10, 6))
df_p1 = df[df['template'] == 'P1']
sns.barplot(data=df_p1, x='rule', y='f1', palette='viridis')
plt.title("Impact of Extraction Rule on P1 (F1 Score)", fontsize=14)
plt.ylabel("F1 Score")
plt.xlabel("Extraction Rule")
plt.ylim(0, 1.0)
for i, val in enumerate(df_p1['f1']):
    plt.text(i, val + 0.02, f"{val:.3f}", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig2_extraction_attribution.png"), dpi=300)
plt.close()
print("Saved Fig 2: Extraction Rule Attribution")

# Table 1: Full Results CSV to Markdown
pivot_all = df.pivot(index='template', columns='rule', values='f1').round(3)
with open(os.path.join(out_dir, "table1_results.md"), "w") as f:
    f.write("# Table 1: F1 Scores by Template and Extraction Rule\n\n")
    f.write(pivot_all.to_markdown())
print("Saved Table 1: table1_results.md")
