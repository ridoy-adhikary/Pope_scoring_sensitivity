import os
from datasets import load_dataset

# Enforce the mirror
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

print("Downloading POPE dataset from HuggingFace mirror...")
print("This will download the images and annotations.")
print("It may take 5-10 minutes depending on connection...")

try:
    ds = load_dataset("lmms-lab/POPE")
    print("\n✅ POPE Dataset downloaded and cached successfully!")
    print(ds)
    
    # Quick check to ensure it has the splits we need
    splits = list(ds.keys())
    print(f"\nSplits found: {splits}")
    
except Exception as e:
    print(f"\n❌ Failed to download POPE: {e}")
