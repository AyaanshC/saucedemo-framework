param(
    [ValidateSet('smoke','full')][string]$Suite = 'smoke',
    [switch]$Headless,
    [ValidateScript({ $_ -ge 0 -and -not [double]::IsInfinity($_) })][double]$StepDelay = 2,
    [ValidateScript({ $_ -ge 0 -and -not [double]::IsInfinity($_) })][double]$EndPause = 3
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw 'Run powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 first.'
}
$arguments = @('-m', 'pytest')
if ($Suite -eq 'smoke') { $arguments += @('-m','smoke','--html=reports/smoke.html','--junitxml=reports/smoke-junit.xml') }
if (-not $Headless) {
    $arguments += @('--headed', '--slow-mo', $StepDelay.ToString([Globalization.CultureInfo]::InvariantCulture),
                    '--end-pause', $EndPause.ToString([Globalization.CultureInfo]::InvariantCulture))
    Write-Host "Presentation pace: $StepDelay seconds after each action; $EndPause seconds before closing each test browser."
}
& '.\.venv\Scripts\python.exe' @arguments
$testExit = $LASTEXITCODE
$report = if ($Suite -eq 'smoke') { 'reports\smoke.html' } else { 'reports\functional.html' }
if (Test-Path $report) { Start-Process (Resolve-Path $report).Path }
exit $testExit
