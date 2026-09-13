"""Portable export of the production parameter contract; checked before synthesis."""
from dataclasses import asdict
from pathlib import Path
import json

APP = Path(__file__).resolve().parent
MANIFEST = json.loads((APP / 'yumemita_voice_manifest.json').read_text(encoding='utf-8'))
ROLES = MANIFEST['roles']
class ContractError(ValueError): pass

def compare(expected, actual, prefix=''):
    errors = []
    for key, value in expected.items():
        name = f'{prefix}.{key}' if prefix else key
        got = actual.get(key) if isinstance(actual, dict) else None
        if isinstance(value, dict): errors.extend(compare(value, got, name))
        elif got != value: errors.append(f'{name}: expected {value!r}; actual {got!r}')
    return errors

def require_match(expected, actual):
    errors = compare(expected, actual)
    if errors: raise ContractError('Production contract mismatch before generation:\n' + '\n'.join(errors))

def check_request(role, key, request, ui_values):
    expected = dict(ROLES[role]['config'])
    # These four controls are explicit choices in the sharing UI, not hidden defaults.
    expected.update(ui_values)
    require_match({k: expected[k] for k in ('model_precision', 'codec_precision')}, asdict(key))
    sampling = {k: v for k, v in expected.items() if k not in ('model_precision', 'codec_precision')}
    sampling['ref_embed'] = str(APP / ROLES[role]['embedding'])
    sampling['ref_wav'] = None
    require_match(sampling, asdict(request))
    overrides = {k: v for k, v in ui_values.items() if v != ROLES[role]['config'][k]}
    return {'role': role, 'model': MANIFEST['model'], 'model_revision': MANIFEST['model_revision'],
            'embedding_sha256': ROLES[role]['sha256'], 'parameters': expected,
            'text': request.text, 'caption': request.caption, 'requested_seed': request.seed,
            'overrides': overrides, 'override_reason': 'Explicit sharing UI controls' if overrides else None}
