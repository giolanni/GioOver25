$source = Join-Path $PSScriptRoot '..\data\storico'
$dest = "C:\Temp\StoriciRanking"

New-Item -ItemType Directory -Force -Path $dest | Out-Null

Get-ChildItem $source -Recurse -File -Filter "storico_ranking*.csv" |
    Copy-Item -Destination $dest -Force

Compress-Archive -Path "$dest\*" -DestinationPath "C:\Temp\StoriciRanking.zip" -Force