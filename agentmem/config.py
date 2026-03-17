"""Configuration management for agentmem."""

import json
from pathlib import Path
from dataclasses import dataclass, field

DEFAULT_MEMORY_DIR = "memory"
CONFIG_FILE = ".agentmem.json"


@dataclass
class AgentMemConfig:
    """Configuration for agentmem."""

    memory_dir: str = DEFAULT_MEMORY_DIR
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 100
    search_top_k: int = 5
    search_min_score: float = 0.3
    correction_confidence_threshold: float = 0.70
    freshness_rules: dict = field(default_factory=lambda: {
        "fresh_days": 7,
        "aging_days": 14,
        "stale_days": 30,
    })

    def save(self, path: Path | None = None):
        """Save config to JSON file."""
        target = path or Path.cwd() / CONFIG_FILE
        target.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | None = None) -> "AgentMemConfig":
        """Load config from JSON file, falling back to defaults."""
        target = path or Path.cwd() / CONFIG_FILE
        if target.exists():
            data = json.loads(target.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()

    @classmethod
    def find(cls, start: Path | None = None) -> "AgentMemConfig":
        """Walk up from start looking for .agentmem.json."""
        current = start or Path.cwd()
        for parent in [current, *current.parents]:
            config_path = parent / CONFIG_FILE
            if config_path.exists():
                return cls.load(config_path)
        return cls()


def find_memory_dir(start: Path | None = None) -> Path:
    """Find the memory directory by walking up from start."""
    config = AgentMemConfig.find(start)
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / config.memory_dir
        if candidate.is_dir():
            return candidate
    return Path.cwd() / config.memory_dir
