"""Download the pinned inference files; Hugging Face resumes and reuses its cache."""
from pathlib import Path
import os
import json
ROOT = Path(__file__).resolve().parent
os.environ['HF_ENDPOINT'] = 'https://huggingface.co'
os.environ['HF_HOME'] = str(ROOT / 'models')
os.environ['HF_HUB_CACHE'] = str(ROOT / 'models/hub')
os.environ['HUGGINGFACE_HUB_CACHE'] = str(ROOT / 'models/hub')
os.environ['HF_HUB_OFFLINE'] = '0'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
from huggingface_hub import snapshot_download

manifest = json.loads((ROOT / 'app/yumemita_voice_manifest.json').read_text(encoding='utf-8'))
items = [
    ('model', ['model.safetensors', 'README.md', 'EMOJI_ANNOTATIONS.md']),
    ('codec', ['weights.pth', 'README.md']),
    ('tokenizer', ['config.json', 'generation_config.json', 'special_tokens_map.json', 'tokenizer_config.json', 'tokenizer.json']),
]
for key, files in items:
    repo, revision = manifest[key], manifest[key + '_revision']
    print('Downloading', repo, revision, flush=True)
    snapshot_download(repo_id=repo, revision=revision, allow_patterns=files, cache_dir=ROOT / 'models/hub')
    # The pinned Irodori codec/tokenizer loaders request main; resolve it to our selected snapshot.
    ref = ROOT / 'models/hub' / ('models--' + repo.replace('/', '--')) / 'refs/main'
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text(revision, encoding='utf-8')
print('All pinned inference files are ready.')
