param(
    [ValidateSet('case-study','smoke','full')][string]$Suite = 'case-study',
    [switch]$Headless
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw 'Run powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 first.'
}
$arguments = @('-m', 'pytest')
$selection = switch ($Suite) {
    'case-study' { @{ Marker = 'case_study'; Report = 'case-study'; Xml = 'case-study-junit'; Count = 25 } }
    'smoke' { @{ Marker = 'smoke'; Report = 'smoke'; Xml = 'smoke-junit'; Count = 12 } }
    'full' { @{ Marker = 'regression'; Report = 'functional'; Xml = 'junit'; Count = 157 } }
}
$arguments += @('-m', $selection.Marker, "--html=reports/$($selection.Report).html",
                "--junitxml=reports/$($selection.Xml).xml",
                '-o', "log_file=reports/logs/$($selection.Report).log")
Write-Host "Running $Suite suite: $($selection.Count) cases."
if (-not $Headless) {
    $arguments += '--headed'
}
& '.\.venv\Scripts\python.exe' @arguments
$testExit = $LASTEXITCODE
$report = "reports\$($selection.Report).html"
& '.\.venv\Scripts\python.exe' 'scripts\build_dashboard.py' '--report' $report.Replace('\', '/')
if ($LASTEXITCODE -eq 0 -and (Test-Path 'reports\dashboard.html')) {
    Start-Process (Resolve-Path 'OPEN_DASHBOARD.cmd').Path
}
elseif (Test-Path $report) {
    Write-Warning 'Dashboard generation failed; opening the detailed test report.'
    Start-Process (Resolve-Path $report).Path
}
exit $testExit
