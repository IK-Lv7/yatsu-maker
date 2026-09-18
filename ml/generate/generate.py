"""LoRA適用済みモデルでのタイトル生成・後処理・ランキングCLI。

使い方(ローカルファイルでのドライラン):
    python -m ml.generate.generate --config ml/configs/generate_default.yaml \
        --corpus data/cleaned.jsonl --output data/predictions.jsonl

使い方(Supabaseから既存タイトルを取得し、結果もSupabaseへ保存する日次バッチ):
    python -m ml.generate.generate --config ml/configs/generate_default.yaml \
        --publish-to-supabase

処理の流れ(AGENTS.md「生成と後処理」に対応):
    1. 形式チェック(「奴」で終わるか、長さが範囲内か)
    2. 既存タイトルとの重複除去(完全一致・埋め込み類似)
    3. 不適切表現フィルタ
    4. 尤度と多様性(MMR)で上位K件を選択
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path

import yaml

from ml.generate.dedup import filter_duplicates
from ml.generate.filters import is_appropriate, load_ng_words, matches_format
from ml.generate.rank import ScoredCandidate, mmr_rank
from ml.preprocess.clean import clean_videos


def load_corpus_titles(path: Path) -> list[str]:
    titles = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            titles.append(json.loads(line)["title"])
    return titles


def load_corpus_titles_from_supabase() -> list[str]:
    """Supabaseの`videos`テーブルから既存の「奴」タイトルを取得する(重複除去の比較対象)。"""
    from ml.common.schema import Video
    from ml.common.supabase_client import select

    rows = select("videos", {"select": "video_id,title,published_at"})
    videos = [Video.from_dict(row) for row in rows]
    return [c.title for c in clean_videos(videos)]


def publish_predictions_to_supabase(
    ranked: list[ScoredCandidate], target_date: str, model_version: str
) -> None:
    from ml.common.supabase_client import upsert

    rows = [
        {
            "target_date": target_date,
            "title": candidate.title,
            "rank": rank,
            "score": candidate.likelihood,
            "model_version": model_version,
        }
        for rank, candidate in enumerate(ranked, start=1)
    ]
    upsert("predictions", rows, on_conflict="target_date,rank")


def generate_raw_candidates(
    model_dir: str,
    adapter_dir: str,
    num_candidates: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    dtype: str = "float32",
) -> list[ScoredCandidate]:
    """ベースモデル+LoRAアダプタでN件の候補を生成する。

    実行にはGPUまたはCPU上のtransformers/peftが必要なため、
    ここでは遅延importする(後処理ロジックのみのユニットテストを軽量に保つため)。
    """
    import os

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    adapter_dir = os.path.expanduser(adapter_dir)
    torch_dtype = getattr(torch, dtype)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    base_model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch_dtype)
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    prompt = tokenizer.bos_token or ""
    inputs = tokenizer(prompt, return_tensors="pt")

    candidates: list[ScoredCandidate] = []
    with torch.no_grad():
        for _ in range(num_candidates):
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                output_scores=True,
            )
            sequence = output.sequences[0]
            text = tokenizer.decode(sequence, skip_special_tokens=True).strip()
            scores = output.scores or []
            log_prob = 0.0
            for step, score in enumerate(scores):
                token_id = sequence[len(sequence) - len(scores) + step]
                log_prob += torch.log_softmax(score[0], dim=-1)[token_id].item()
            candidates.append(ScoredCandidate(title=text, likelihood=log_prob))
    return candidates


def postprocess(
    candidates: list[ScoredCandidate],
    existing_titles: list[str],
    top_k: int,
    mmr_lambda: float,
    suffix: str = "奴",
    min_len: int = 3,
    max_len: int = 40,
    lexical_dup_threshold: float = 0.9,
) -> list[ScoredCandidate]:
    format_ok = [c for c in candidates if matches_format(c.title, suffix, min_len, max_len)]

    ng_words = load_ng_words()
    appropriate = [c for c in format_ok if is_appropriate(c.title, ng_words)]

    deduped_titles = filter_duplicates(
        [c.title for c in appropriate],
        existing_titles,
        lexical_threshold=lexical_dup_threshold,
    )
    deduped_set = set(deduped_titles)
    deduped = [c for c in appropriate if c.title in deduped_set]

    return mmr_rank(deduped, k=top_k, lambda_param=mmr_lambda)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--corpus", type=Path, default=None,
        help="既存タイトルのJSONL。省略時はSupabaseの videos テーブルから取得する",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="結果を保存するローカルJSONL(省略可、動作確認用)",
    )
    parser.add_argument(
        "--publish-to-supabase", action="store_true",
        help="結果をSupabaseの predictions テーブルに保存する(日次バッチ用)",
    )
    parser.add_argument(
        "--target-date", default=None,
        help="predictions.target_date に使う日付(YYYY-MM-DD)。省略時は今日の日付",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with args.config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    existing_titles = (
        load_corpus_titles(args.corpus) if args.corpus else load_corpus_titles_from_supabase()
    )

    raw_candidates = generate_raw_candidates(
        model_dir=config["base_model"],
        adapter_dir=config["adapter_dir"],
        num_candidates=config.get("num_candidates", 100),
        max_new_tokens=config.get("max_new_tokens", 30),
        temperature=config.get("temperature", 1.0),
        top_p=config.get("top_p", 0.95),
        dtype=config.get("dtype", "float32"),
    )

    ranked = postprocess(
        raw_candidates,
        existing_titles,
        top_k=config.get("top_k", 10),
        mmr_lambda=config.get("mmr_lambda", 0.7),
        suffix=config.get("suffix", "奴"),
        min_len=config.get("min_len", 3),
        max_len=config.get("max_len", 40),
        lexical_dup_threshold=config.get("lexical_dup_threshold", 0.9),
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            for rank, candidate in enumerate(ranked, start=1):
                f.write(
                    json.dumps(
                        {"title": candidate.title, "rank": rank, "score": candidate.likelihood},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"{len(ranked)} 件の予想を {args.output} に保存しました")

    if args.publish_to_supabase:
        target_date = args.target_date or datetime.date.today().isoformat()
        model_version_path = Path(config["adapter_dir"]).expanduser() / "model_version.txt"
        model_version = (
            model_version_path.read_text(encoding="utf-8").strip()
            if model_version_path.exists()
            else "unknown"
        )
        publish_predictions_to_supabase(ranked, target_date, model_version)
        print(f"{len(ranked)} 件の予想を Supabase({target_date})に保存しました")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
