"""Shared data structures for the ML pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Video:
    video_id: str
    title: str
    published_at: str  # ISO 8601

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Video":
        return cls(
            video_id=data["video_id"],
            title=data["title"],
            published_at=data["published_at"],
        )


@dataclass
class CleanedTitle:
    video_id: str
    title: str  # 正規化・装飾除去済みの完全なタイトル(「奴」で終わる)
    published_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CleanedTitle":
        return cls(
            video_id=data["video_id"],
            title=data["title"],
            published_at=data["published_at"],
        )


@dataclass
class Prediction:
    title: str
    rank: int
    score: float

    def to_dict(self) -> dict:
        return asdict(self)
