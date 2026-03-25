"""
Türkçe kelime frekans dosyası oluşturucu.

Amaç:
  - Elindeki büyük .txt corpus'lardan kelime + frekans listesi çıkarıp
    `data/tr_frequencies.json` dosyasını oluşturmak / güncellemek.

Kullanım:
  cd python_backend
  python -m scripts.build_frequencies path/to/corpus1.txt path/to/corpus2.txt

Notlar:
  - Tüm dosyalar UTF-8 kabul edilir.
  - Sadece harf içeren token'lar (a–z, ç, ğ, ı, i, ö, ş, ü) sayılır.
  - Var olan `data/tr_frequencies.json` ile birleştirir (toplayarak).
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import List


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
FREQ_PATH = os.path.join(DATA_DIR, "tr_frequencies.json")

# Basit Türkçe kelime regex'i
WORD_RE = re.compile(r"[a-zA-ZçğıİöşüÇĞİÖŞÜ]+", re.UNICODE)


def tokenize(line: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(line)]


def load_existing() -> Counter:
    if not os.path.exists(FREQ_PATH):
        return Counter()
    try:
        with open(FREQ_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return Counter({k.lower(): int(v) for k, v in data.items()})
        # Eski format: [{"word": "...", "frequency": ...}, ...]
        if isinstance(data, list):
            return Counter(
                {
                    (item.get("word") or "").lower(): int(item.get("frequency", 1))
                    for item in data
                    if isinstance(item, dict) and item.get("word")
                }
            )
    except Exception as e:
        print(f"[WARN] Mevcut frekans dosyası okunamadı: {e}")
    return Counter()


def build_from_files(files: List[str]) -> Counter:
    counter: Counter = Counter()
    for path in files:
        if not os.path.exists(path):
            print(f"[WARN] Dosya bulunamadı, atlanıyor: {path}")
            continue
        print(f"[INFO] Okunuyor: {path}")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                tokens = tokenize(line)
                counter.update(tokens)
    return counter


def save(counter: Counter) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    # Basit dict formatı: { "kelime": frekans, ... }
    data = {word: int(freq) for word, freq in counter.most_common()}
    with open(FREQ_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(data):,} kelime yazıldı -> {FREQ_PATH}")


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Metin dosyalarından Türkçe kelime frekans listesi üretir."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Corpus .txt dosyaları (bir veya daha fazla)",
    )
    args = parser.parse_args(argv)

    existing = load_existing()
    print(f"[INFO] Mevcut frekanslar: {len(existing):,} kelime")

    new_counts = build_from_files(args.files)
    print(f"[INFO] Yeni corpus'tan gelen: {len(new_counts):,} kelime (farklı)")

    existing.update(new_counts)
    save(existing)


if __name__ == "__main__":
    main()

