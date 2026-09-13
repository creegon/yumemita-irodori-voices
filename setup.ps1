param(
    [ValidateSet('cu128', 'cpu')][string]$Backend = 'cu128'
)
$ErrorActionPreference = 'Stop'
$voiceRoot = $PSScriptRoot
$voiceEngine = Join-Path $voiceRoot '.runtime/Irodori-TTS'
$voiceCommit = 'eaf74d6a19138f743acb5b71a445fd25a57db987'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Install Git first: https://git-scm.com/downloads/win' }
$voiceUv = Join-Path $voiceRoot '.tools/uv/uv.exe'
if (-not (Test-Path -LiteralPath $voiceUv)) {
    $voiceInstalledUv = Get-Command uv -ErrorAction SilentlyContinue
    if ($voiceInstalledUv) {
        $voiceUv = $voiceInstalledUv.Source
    } else {
        Write-Host 'Installing uv from its official source into this folder...'
        $voiceDownload = @{ Uri = 'https://astral.sh/uv/install.ps1'; UserAgent = 'yumemita-voice-setup' }
        if ($env:HTTPS_PROXY) { $voiceDownload.Proxy = $env:HTTPS_PROXY }
        $voiceInstaller = Invoke-RestMethod @voiceDownload
        $voicePreviousUvDir = $env:UV_UNMANAGED_INSTALL
        try {
            $env:UV_UNMANAGED_INSTALL = Split-Path -Parent $voiceUv
            & ([scriptblock]::Create($voiceInstaller))
        } finally { $env:UV_UNMANAGED_INSTALL = $voicePreviousUvDir }
        if (-not (Test-Path -LiteralPath $voiceUv)) { throw 'uv install failed. Run SETUP_YUMEMITA.bat to retry.' }
    }
}
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
    & $voiceUv sync --frozen --python 3.10 --extra $Backend
    if ($LASTEXITCODE) { throw 'Dependency install failed. Rerun setup.ps1 to resume.' }
} finally { Pop-Location }
$voicePython = Join-Path $voiceEngine '.venv/Scripts/python.exe'
& $voicePython -X utf8 (Join-Path $voiceRoot 'download_models.py')
if ($LASTEXITCODE) { throw 'Model download failed. Rerun setup.ps1 to resume.' }
Write-Host 'Ready. Double-click START_YUMEMITA.bat.'
