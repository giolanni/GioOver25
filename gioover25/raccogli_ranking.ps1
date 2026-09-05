$source = Join-Path $PSScriptRoot '..\data\output_ranking'
$dest = "C:\Temp\previsioni"
$zip = "C:\Temp\previsioni.zip"

# Elimina completamente la vecchia cartella temporanea
if (Test-Path -Path $dest) {
    Remove-Item -Path $dest -Recurse -Force
}

# Ricrea la cartella vuota
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# Cerca i file ranking*.csv ed esclude le cartelle old, old_ranking, old_csv, ecc.
Get-ChildItem -Path $source -Recurse -File -Filter "ranking*.csv" |
    Where-Object {
        $partiPercorso = $_.FullName -split '[\\/]'

        -not (
            $partiPercorso |
            Where-Object {
                $_ -like "old*"
            }
        )
    } |
    ForEach-Object {
        Write-Host "Copio: $($_.FullName)"
        Copy-Item -Path $_.FullName -Destination $dest -Force
    }

# Ricrea lo ZIP
Compress-Archive `
    -Path "$dest\*" `
    -DestinationPath $zip `
    -Force

Write-Host ""
Write-Host "Archivio creato: $zip"