"""Opt-in live call. Run from repository root; no network without --live."""
import argparse
import getpass
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.contracts import AnalyzeRequest
from backend.service import analyze, AnalysisError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Send the synthetic sample to the configured provider; pricing depends on model.')
    args = parser.parse_args()
    if not args.live:
        parser.error('No request sent. Add --live to explicitly run a provider test.')
    if not os.getenv('OPENROUTER_MODEL', '').strip():
        parser.error('Set OPENROUTER_MODEL first. No request sent.')
    if not os.getenv('OPENROUTER_API_KEY', '').strip():
        os.environ['OPENROUTER_API_KEY'] = getpass.getpass('OpenRouter API key (hidden): ')
    os.environ['ANALYSIS_MODE'] = 'ai'
    text = ('You retain ownership of your uploads. You grant us a perpetual license '
            'to sell your uploaded content to advertising partners.')
    started = time.monotonic()
    try:
        result = analyze(AnalyzeRequest(text=text))
    except AnalysisError as error:
        print(json.dumps({'error': error.code, 'message': error.message}))
        return 1
    print(json.dumps(result.model_dump(), indent=2))
    print(f'Elapsed seconds: {time.monotonic() - started:.2f}')
    print('Review interpretation manually. Configured model/router: ' + os.environ['OPENROUTER_MODEL'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
