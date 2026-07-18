param(
	[string]$Config = (Join-Path $PSScriptRoot '..\config\local_paths.json')
)

$ErrorActionPreference = 'Stop'
$configPath = [System.IO.Path]::GetFullPath($Config)
$data = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$repo = [System.IO.Path]::GetFullPath([string]$data.repo_dir)
$relocated = [System.IO.Path]::GetFullPath([string]$data.candidate_relocated_user_dir)
$original = [System.IO.Path]::GetFullPath([string]$data.user_dir)

if (-not $repo.StartsWith(([System.IO.Path]::GetPathRoot($data.game_dir)), [StringComparison]::OrdinalIgnoreCase)) {
	throw "Repository is not on the game drive: $repo"
}

New-Item -ItemType Directory -Path $relocated -Force | Out-Null
$modParent = Join-Path $relocated 'mod'
New-Item -ItemType Directory -Path $modParent -Force | Out-Null
$link = Join-Path $modParent 'antiqvitas'

if (Test-Path -LiteralPath $link) {
	$item = Get-Item -LiteralPath $link -Force
	$target = @($item.Target)[0]
	if (-not $target -or ([System.IO.Path]::GetFullPath($target) -ne $repo)) {
		throw "Existing mod path does not point at the repository: $link"
	}
} else {
	New-Item -ItemType Junction -Path $link -Target $repo | Out-Null
}

$data | Add-Member -NotePropertyName original_user_dir -NotePropertyValue $original -Force
$data.user_dir = $relocated
$data.mod_dir = $link
$data.mod_visibility = 'user_dir_relocation+junction'
$json = ($data | ConvertTo-Json -Depth 8) + [Environment]::NewLine
[System.IO.File]::WriteAllText($configPath, $json, [System.Text.UTF8Encoding]::new($false))

Write-Output "USER_DIR=$relocated"
Write-Output "MOD_DIR=$link"
Write-Output "Launch argument: --user_dir=$relocated"
