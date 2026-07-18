param(
	[int]$TimeoutSeconds = 60
)

$ErrorActionPreference = 'Stop'
$steam = Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $steam) {
	$path = (Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamExe
	if (-not (Test-Path -LiteralPath $path)) {
		throw "Steam executable is missing: $path"
	}
	$steam = Start-Process -FilePath $path -WindowStyle Hidden -PassThru
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
do {
	Start-Sleep -Milliseconds 500
	$running = Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1
	if ($running -and $running.Responding) {
		Write-Output "Steam ready (PID $($running.Id))"
		exit 0
	}
} while ((Get-Date) -lt $deadline)

throw "Steam did not become responsive in $TimeoutSeconds seconds"
