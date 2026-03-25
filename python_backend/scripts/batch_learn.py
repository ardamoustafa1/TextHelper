"""
Batch learning script to pre-fill TextHelper with your existing texts.

Kullanım:
    cd python_backend
    python -m scripts.batch_learn path/to/texts.txt --user-id my-user

Dosya formatı:
    - Her satır bir cümle / mesaj
    - Örnek:
        Merhaba, size nasıl yardımcı olabilirim?
        Siparişimin durumunu öğrenmek istiyorum.
"""

import argparse
import os
import sys
from typing import Optional

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402


client = TestClient(app)


def send_learn(text: str, user_id: str) -> None:
    payload = {
        "text": text,
        "selected_suggestion": "",
        "user_id": user_id,
    }
    try:
        client.post("/api/v1/learn", json=payload)
    except Exception:
        # Batch sürecini durdurmamak için hataları yutuyoruz
        pass


def run(file_path: str, user_id: str) -> None:
    total = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            if not text:
                continue
            send_learn(text, user_id)
            total += 1
    print(f"Batch learn tamamlandı. Toplam {total} satır işlendi.")


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(description="Batch learn existing texts into TextHelper.")
    parser.add_argument("file", help="Satır satır metin içeren dosya yolu")
    parser.add_argument(
        "--user-id",
        dest="user_id",
        default="batch",
        help="Öğrenme için kullanılacak kullanıcı ID (default: batch)",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.file):
        print(f"Dosya bulunamadı: {args.file}")
        sys.exit(1)

    run(args.file, args.user_id)


if __name__ == "__main__":
    main()

