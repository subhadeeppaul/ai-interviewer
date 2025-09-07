Param(
  [string]$Topic = "Python",
  [string]$Difficulty = "mixed",
  [int]$Questions = 1,
  [string]$Type = "mixed"
)

Set-Location -Path (Split-Path -Parent $PSCommandPath)

Write-Host "=== AI Interviewer Demo ===" -ForegroundColor Cyan
Write-Host "Topic: $Topic | Difficulty: $Difficulty | Questions: $Questions | Type: $Type"

python -m src.app ping Respond with exactly: pong | Out-Host

python -m src.app ask-one --topic $Topic --difficulty $Difficulty --type $Type | Out-Host


$logDir = "runs"
$newDir = New-Item -ItemType Directory -Force -Path $logDir
$log = Join-Path $logDir ("demo_{0}.json" -f (Get-Date).ToString("yyyyMMdd_HHmmss"))
python -m src.app interview --topic $Topic --difficulty $Difficulty --questions $Questions --type $Type --log-json $log

Write-Host "Saved session to $log" -ForegroundColor Green
