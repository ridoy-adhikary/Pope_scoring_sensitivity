import os, sys, json, time, argparse
import torch
from datasets import load_dataset
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig
from tqdm import tqdm

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"
MAX_NEW_TOKENS = 16

PROMPTS = {
    "P1": "Is there a {object} in the image?",
    "P3": "Can you see a {object} in the image?",
    "P5": "Is there a {object} in the image? Answer yes or no.",
    "P6": "Is there a {object} in the image? Answer with exactly one word: Yes or No."
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=str, required=True, choices=list(PROMPTS.keys()))
    parser.add_argument("--out_dir", type=str, default="~/Ridoy/Other_Projects/pope-audit/03_inference/outputs")
    args = parser.parse_args()

    out_dir = os.path.expanduser(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"qwen__{args.template}.jsonl")

    done_ids = set()
    if os.path.exists(out_file):
        with open(out_file, "r") as f:
            for line in f:
                try:
                    done_ids.add(json.loads(line)["id"])  # FIX: Using unique 'id'
                except: pass
        print(f"Resuming: {len(done_ids)} questions already done for {args.template}.")

    print(f"Loading POPE dataset...")
    ds = load_dataset("lmms-lab/POPE", split="test")
    
    if len(done_ids) >= len(ds):
        print("All questions already completed for this template. Exiting.")
        return

    print(f"Loading model {MODEL_ID} in 4-bit...")
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map={"": 0},
        torch_dtype=torch.float16, attn_implementation="sdpa",
        trust_remote_code=True, local_files_only=True
    )
    model.eval()
    
    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True, local_files_only=True)
    if processor.tokenizer.pad_token_id is None:
        processor.tokenizer.pad_token_id = processor.tokenizer.eos_token_id

    yes_id = processor.tokenizer.convert_tokens_to_ids("Yes")
    no_id = processor.tokenizer.convert_tokens_to_ids("No")

    template_str = PROMPTS[args.template]
    
    print(f"Starting sweep for {args.template}...")
    with open(out_file, "a") as f_out:
        for i, item in enumerate(tqdm(ds, desc=f"Qwen {args.template}")):
            if item["id"] in done_ids:  # FIX: Using unique 'id'
                continue
            
            obj = item["question"].replace("Is there a ", "").replace(" in the image?", "")
            prompt_text = template_str.format(object=obj)
            
            msgs = [{"role": "user", "content": [{"type": "image", "image": item["image"]}, {"type": "text", "text": prompt_text}]}]
            text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[text], images=[item["image"]], padding=True, return_tensors="pt").to("cuda")
            
            with torch.no_grad():
                out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                     pad_token_id=processor.tokenizer.pad_token_id,
                                     output_scores=True, return_dict_in_generate=True)
                first_token_logits = out.scores[0][0]
                yes_logprob = torch.log_softmax(first_token_logits, dim=-1)[yes_id].item()
                no_logprob = torch.log_softmax(first_token_logits, dim=-1)[no_id].item()
                
            trim = out.sequences[:, inputs["input_ids"].shape[1]:]
            raw_response = processor.batch_decode(trim, skip_special_tokens=True)[0].strip()
            
            record = {
                "id": item["id"],          # FIX: Using unique 'id'
                "category": item["category"],
                "question": item["question"],
                "ground_truth": item["answer"],
                "template": args.template,
                "prompt_used": prompt_text,
                "raw_response": raw_response,
                "yes_logprob": round(yes_logprob, 4),
                "no_logprob": round(no_logprob, 4)
            }
            
            f_out.write(json.dumps(record) + "\n")
            f_out.flush()

if __name__ == "__main__":
    main()
