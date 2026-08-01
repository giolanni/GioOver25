$source = Join-Path $PSScriptRoot '..\data\storico'
$dest = "C:\Temp\StoriciRanking"
$zip = "C:\Temp\StoriciRanking.zip"

# Elimina completamente la vecchia cartella temporanea
if (Test-Path $dest) {
    Remove-Item $dest -Recurse -Force
}

# Ricrea la cartella vuota
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# Copia soltanto i file attualmente presenti nella sorgente
Get-ChildItem $source -Recurse -File -Filter "storico_ranking*.csv" |
    Copy-Item -Destination $dest -Force

# Ricrea lo ZIP
Compress-Archive -Path "$dest\*" -DestinationPath $zip -Force