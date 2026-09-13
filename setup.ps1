param(
    [ValidateSet('cu128', 'cpu')][string]$Backend = 'cu128'
)
$ErrorActionPreference = 'Stop'
$voiceRoot = $PSScriptRoot
$voiceEngine = Join-Path $voiceRoot '.runtime/Irodori-TTS'
$voiceCommit = 'eaf74d6a19138f743acb5b71a445fd25a57db987'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Install Git first: https://git-scm.com/downloads/win' }
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' }
if (-not (Test-Path -LiteralPath (Join-Path $voiceEngine '.git'))) {
    New-Item -ItemType Directory -Force -Path $voiceEngine | Out-Null
    & git -C $voiceEngine init
    if ($LASTEXITCODE) { throw 'git init failed' }
    & git -C $voiceEngine remote add origin 'https://github.com/Aratako/Irodori-TTS.git'
    if ($LASTEXITCODE) { throw 'git remote setup failed' }
}
$voiceHead = & git -C $voiceEngine rev-parse --verify --quiet HEAD
if ($voiceHead -ne $voiceCommit) {
    & git -C $voiceEngine fetch --depth 1 origin $voiceCommit
    if ($LASTEXITCODE) { throw 'Download failed. Rerun setup.ps1 to resume.' }
    & git -C $voiceEngine checkout --detach $voiceCommit
    if ($LASTEXITCODE) { throw 'Checkout failed; inspect .runtime/Irodori-TTS before retrying.' }
}
Push-Location $voiceEngine
try {
    & uv sync --frozen --python 3.10 --extra $Backend
    if ($LASTEXITCODE) { throw 'Dependency install failed. Rerun setup.ps1 to resume.' }
} finally { Pop-Location }
$voicePython = Join-Path $voiceEngine '.venv/Scripts/python.exe'
& $voicePython -X utf8 (Join-Path $voiceRoot 'download_models.py')
if ($LASTEXITCODE) { throw 'Model download failed. Rerun setup.ps1 to resume.' }
Write-Host 'Ready. Double-click START_YUMEMITA.bat.'
