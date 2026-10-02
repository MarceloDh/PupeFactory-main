param([ValidateSet('start', 'stop', 'status')][string]$Action = 'start')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskBin = Join-Path $taskRoot '.runtime\postgres-windows\pgsql\bin'
$taskData = Join-Path $taskRoot '.runtime\pgdata'
if (-not (Test-Path (Join-Path $taskBin 'pg_ctl.exe'))) {
    throw 'No están los binarios locales. Instala PostgreSQL o prepara .runtime según README.'
}
if (-not (Test-Path (Join-Path $taskData 'PG_VERSION'))) {
    throw 'La base local no está inicializada. Revisa la instalación del README.'
}
switch ($Action) {
    'start' {
        # La disponibilidad TCP también funciona si el proceso fue iniciado por otra sesión.
        & (Join-Path $taskBin 'pg_isready.exe') -h 127.0.0.1 -p 5432 *> $null
        if ($LASTEXITCODE -ne 0) {
            & (Join-Path $taskBin 'pg_ctl.exe') -D $taskData -l (Join-Path $taskRoot '.runtime\postgresql.log') -w start
            if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL no pudo iniciar; consulta .runtime\postgresql.log.' }
        }
    }
    'stop' { & (Join-Path $taskBin 'pg_ctl.exe') -D $taskData -m fast -w stop }
    'status' { & (Join-Path $taskBin 'pg_isready.exe') -h 127.0.0.1 -p 5432 }
}
