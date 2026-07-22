$pptDir = "E:\note\考研\PPT"
$outputDir = "E:\note\考研\PPT\txt"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$powerpoint = New-Object -ComObject PowerPoint.Application
# Visible property skipped due to Chinese Office compatibility

Get-ChildItem -Path $pptDir -Filter "*.ppt" | ForEach-Object {
    Write-Output "Processing: $($_.Name)"
    try {
        $presentation = $powerpoint.Presentations.Open($_.FullName, $false, $false, $false)
        $lines = @()
        for ($i = 1; $i -le $presentation.Slides.Count; $i++) {
            $slide = $presentation.Slides.Item($i)
            $lines += "`n--- Slide $i ---"
            foreach ($shape in $slide.Shapes) {
                if ($shape.HasTextFrame -eq $true) {
                    $text = $shape.TextFrame.TextRange.Text.Trim()
                    if ($text -ne "") { $lines += $text }
                }
            }
        }
        $outPath = Join-Path $outputDir ($_.BaseName + ".txt")
        $lines -join "`n" | Out-File -FilePath $outPath -Encoding UTF8
        Write-Output "  -> Saved $($lines.Count) lines"
        $presentation.Close()
    } catch {
        Write-Output "  Error: $_"
    }
}

$powerpoint.Quit()
Write-Output "Done!"
