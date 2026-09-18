"""日本語LMへのLoRAファインチューニングCLI。

使い方:
    python -m ml.train.train_lora --config ml/configs/train_default.yaml

学習データは ml.preprocess.clean が出力するJSONL(CleanedTitle)を用いる。
語尾は「〜な奴」「〜する奴」など様々なため固定接尾辞はプロンプト側に置かず、
正規化済みの完全なタイトル(奴で終わる)をそのまま causal LM として学習する。
生成後に「奴」で終わっているかは後処理(ml.generate.filters)で確認する。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_titles(path: Path) -> list[str]:
    titles = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            titles.append(json.loads(line)["title"])
    return titles


def split_holdout(titles_with_dates: list[tuple[str, str]], holdout_days: int) -> tuple[list[str], list[str]]:
    """直近holdout_days日分を評価用に分離する(品質確認用)。published_atはISO8601文字列。"""
    if holdout_days <= 0:
        return [title for title, _ in titles_with_dates], []
    sorted_items = sorted(titles_with_dates, key=lambda item: item[1])
    from datetime import datetime, timedelta

    latest = datetime.fromisoformat(sorted_items[-1][1].replace("Z", "+00:00"))
    cutoff = latest - timedelta(days=holdout_days)
    train, holdout = [], []
    for title, published_at in sorted_items:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        (holdout if dt > cutoff else train).append(title)
    return train, holdout


def run_training(config: dict, data_path: Path, output_dir: Path) -> None:
    """LoRA学習を実行する。重い依存(torch/transformers/peft)は遅延importする。"""
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        DataCollatorForLanguageModeling,
        Trainer,
        TrainingArguments,
    )

    titles = load_titles(data_path)
    dataset = Dataset.from_dict({"text": titles})

    tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize(batch):
        # EOSがないと文末を学習できず「の奴の奴の奴...」と繰り返し続けてしまう
        texts = [text + tokenizer.eos_token for text in batch["text"]]
        return tokenizer(texts, truncation=True, max_length=config.get("max_length", 64))

    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])

    model = AutoModelForCausalLM.from_pretrained(config["base_model"])
    lora_config = LoraConfig(
        r=config.get("lora_r", 8),
        lora_alpha=config.get("lora_alpha", 16),
        lora_dropout=config.get("lora_dropout", 0.05),
        target_modules=config.get("target_modules", ["q_proj", "v_proj"]),
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.get("num_train_epochs", 3),
        per_device_train_batch_size=config.get("batch_size", 4),
        learning_rate=config.get("learning_rate", 2e-4),
        logging_steps=config.get("logging_steps", 10),
        save_strategy="no",  # 最終アダプタのみコミットするので中間チェックポイントは不要
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    trainer.train()

    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    version_file = output_dir / "model_version.txt"
    version_file.write_text(config.get("model_version", "unknown"), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with args.config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_path = Path(config["data_path"])
    output_dir = Path(config["output_dir"]).expanduser()
    run_training(config, data_path, output_dir)
    print(f"モデル({config.get('model_version', 'unknown')})を {output_dir} に保存しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
