# Define the path
$path = "C:\Users\Owner\Videos\NVIDIA\Highlights\War Thunder"
# How many seconds between deaths to consider them "separate" events?
$thresholdSeconds = 10 

# 1. Get all files with "Moment of death" in the name
$files = Get-ChildItem -Path $path -Filter "*Moment of death*" | Sort-Object LastWriteTime

if ($files.Count -eq 0) {
    Write-Host "No 'Moment of death' files found." -ForegroundColor Yellow
    exit
}

$lastKeptTime = [DateTime]::MinValue
$deletedCount = 0

foreach ($file in $files) {
    # Check if this file was created shortly after the last one we decided to keep
    $timeDiff = ($file.LastWriteTime - $lastKeptTime).TotalSeconds

    if ($timeDiff -lt $thresholdSeconds) {
        # This is a "duplicate" from the same death event
        Write-Host "Deleting duplicate: $($file.Name) (Diff: $($timeDiff)s)" -ForegroundColor Gray
        Remove-Item -Path $file.FullName -Force
        $deletedCount++
    } else {
        # This is the first file of a new death event
        Write-Host "Keeping original: $($file.Name)" -ForegroundColor Green
        $lastKeptTime = $file.LastWriteTime
    }
}

Write-Host "`nCleanup complete. Removed $deletedCount duplicate clips." -ForegroundColor Cyan