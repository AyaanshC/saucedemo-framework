param([switch]$WithJMeter)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv .venv }
    else { & python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required.' }
}
& '.\.venv\Scripts\python.exe' -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
if ($LASTEXITCODE -ne 0) { throw 'Python version check failed.' }
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if ($WithJMeter) {
    New-Item -ItemType Directory -Force tools | Out-Null
    $url = 'https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.6.3.zip'
    $archive = Join-Path (Get-Location) 'tools\apache-jmeter-5.6.3.zip'
    Invoke-WebRequest $url -OutFile $archive -UseBasicParsing
    $checksum = (Invoke-WebRequest "$url.sha512" -UseBasicParsing).Content
    if ($checksum -is [byte[]]) { $checksum = [Text.Encoding]::UTF8.GetString($checksum) }
    $expected = ([regex]::Match($checksum, '[a-fA-F0-9]{128}')).Value
    if (-not $expected -or (Get-FileHash -LiteralPath $archive -Algorithm SHA512).Hash -ne $expected) {
        throw 'JMeter SHA-512 verification failed.'
    }
    Expand-Archive -LiteralPath $archive -DestinationPath tools -Force
    Write-Host 'JMeter 5.6.3 installed. Java 8+ must be on PATH.'
}
Write-Host 'Ready. Run: .\.venv\Scripts\python.exe -m pytest -m smoke --headed'
