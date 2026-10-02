param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $taskPython)) { throw 'Crea el entorno e instala requirements.txt según README.' }
if (Test-Path (Join-Path $PSScriptRoot '.runtime\pgdata\PG_VERSION')) {
    & (Join-Path $PSScriptRoot 'scripts\postgresql.ps1') start
}
& $taskPython manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar migraciones.' }
& $taskPython manage.py runserver "127.0.0.1:$Port"
