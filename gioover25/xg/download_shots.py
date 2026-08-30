from __future__ import annotations

import argparse
import json
from pathlib import Path

from .providers import UnderstatProvider

OUT_DIR = Path('data/xg/shots/understat')


def main() -> None:
    parser = argparse.ArgumentParser(description='Scarica shot-level xG da Understat per una partita')
    parser.add_argument('match_id', help='ID partita Understat')
    args = parser.parse_args()

    payload = UnderstatProvider().download_match_shots(args.match_id)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f'{args.match_id}.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    home = payload.get('h', []) if isinstance(payload, dict) else []
    away = payload.get('a', []) if isinstance(payload, dict) else []
    print(f'[OK] shots home={len(home)} away={len(away)} -> {out}')


if __name__ == '__main__':
    main()
