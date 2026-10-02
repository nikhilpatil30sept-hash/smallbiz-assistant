"""Phase 4: QLoRA (4-bit) fine-tune of Llama 3.1 8B Instruct on the Phase 3 training data,
via Unsloth. This is BEHAVIOR-ONLY fine-tuning - RAG stays in production unchanged. The goal
is a LoRA adapter that makes the base chat model cite correctly, hedge only when the sources
actually don't cover something, refer to the right professional/agency, and stay concise -
using the exact (system prompt + retrieved sources + question) shape it already sees in
production, because that's exactly what data/train/train.jsonl contains (built by
build_training_set.py from real retrieval, not hand-written).

THIS SCRIPT DOES NOT RUN ON THE MAC. The Mac (8-16GB unified memory) can't fit even a 4-bit
QLoRA fine-tune of an 8B model comfortably. Run this on a rented GPU instead - a single
RunPod pod or Google Colab session with a T4/L4/A10 (16GB+ VRAM) is enough; the whole run
should take well under an hour for ~300 examples over a few epochs.

Setup on the rented GPU (once):
    pip install -r requirements-train.txt

Usage (on the rented GPU, after uploading data/train/train.jsonl + dev.jsonl and this repo):
    python train_qlora.py \
        --train data/train/train.jsonl \
        --dev data/train/dev.jsonl \
        --out lora_out \
        --epochs 3

Writes:
    <out>/                - the LoRA adapter (adapter_model.safetensors + config), NOT a
                             merged model - small (a few hundred MB), download this back to
                             the Mac when done.
Then, back on the Mac / wherever Ollama runs:
    - merge the adapter into the base weights (or use Unsloth's save_pretrained_gguf to
      export straight to GGUF - see the comment at the bottom of this file) and build an
      Ollama Modelfile from it, so evaluate.py can point CHAT_MODEL at the fine-tuned model
      exactly the way it already points at llama3.1:8b.
"""
import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
                     help="Unsloth's pre-quantized 4-bit mirror of Llama 3.1 8B Instruct - "
                          "same base weights as the llama3.1:8b Ollama model uses, ungated.")
    ap.add_argument("--train", default="data/train/train.jsonl")
    ap.add_argument("--dev", default="data/train/dev.jsonl")
    ap.add_argument("--out", default="lora_out")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--max-seq-len", type=int, default=2048,
                     help="Training examples include real retrieved sources in the prompt, "
                          "which can run long - raise this if you see truncation warnings.")
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--lora-alpha", type=int, default=16)
    ap.add_argument("--learning-rate", type=float, default=2e-4)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--gguf-quant", default="q4_k_m",
                     help="Quantization method for the merged GGUF export that runs "
                          "automatically after training (e.g. q4_k_m, q8_0, f16). Pass "
                          "--no-gguf to skip this step and only save the LoRA adapter.")
    ap.add_argument("--no-gguf", action="store_true",
                     help="Skip the merged-GGUF export and only save the LoRA adapter "
                          "(the old behavior).")
    args = ap.parse_args()

    # Imports deliberately live inside main(): this file needs to be readable/reviewable
    # (and its --help usable) even in an environment without unsloth/torch/trl installed -
    # e.g. Claude's own sandbox, which never runs this script, only writes/reviews it.
    import torch
    from datasets import Dataset
    from unsloth import FastLanguageModel, is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print(f"Loading base model: {args.base_model}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.base_model,
        max_seq_length=args.max_seq_len,
        dtype=None,  # auto-detect
        load_in_4bit=True,
    )
    tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0,  # 0 is optimized in Unsloth
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                         "gate_proj", "up_proj", "down_proj"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
    )

    def to_text(example: dict) -> dict:
        # tokenizer.apply_chat_template needs the raw messages list; we keep id/category
        # around only for our own bookkeeping, not passed to the trainer.
        text = tokenizer.apply_chat_template(example["messages"], tokenize=False,
                                              add_generation_prompt=False)
        return {"text": text}

    train_rows = load_jsonl(Path(args.train))
    dev_rows = load_jsonl(Path(args.dev))
    print(f"Loaded {len(train_rows)} train examples, {len(dev_rows)} dev examples")

    train_ds = Dataset.from_list(train_rows).map(to_text)
    dev_ds = Dataset.from_list(dev_rows).map(to_text)

    training_args = TrainingArguments(
        output_dir=f"{args.out}_checkpoints",
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        seed=args.seed,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        dataset_text_field="text",
        max_seq_length=args.max_seq_len,
        packing=False,
        args=training_args,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving LoRA adapter to {args.out}")
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    print("Done. Download the adapter folder back and see the module docstring for the "
          "GGUF-export / Ollama Modelfile steps that follow.")

    # To export straight to a Modelfile-ready GGUF instead of merging by hand, Unsloth
    # provides a one-liner (uncomment on the GPU box, needs llama.cpp available):
    #   model.save_pretrained_gguf(args.out + "_gguf", tokenizer, quantization_method="q4_k_m")
    # That produces a .gguf file you can point an Ollama Modelfile's FROM line at directly.


if __name__ == "__main__":
    main()
