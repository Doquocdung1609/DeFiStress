param([Parameter(Mandatory = $true)][string] $PackageRoot)

$ErrorActionPreference = 'Stop'
$files = Get-ChildItem -LiteralPath $PackageRoot -Recurse -File -Filter '*.docx'
foreach ($file in $files) {
    $pdf = [IO.Path]::ChangeExtension($file.FullName, '.pdf')
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    try {
        $document = $null
        try {
            $document = $word.Documents.Open($file.FullName, $false, $false)
            $document.Fields.Update() | Out-Null
            foreach ($toc in $document.TablesOfContents) { $toc.Update() | Out-Null }
            $document.Save()
            $document.ExportAsFixedFormat($pdf, 17)
            Write-Output "EXPORTED $pdf pages=$($document.ComputeStatistics(2))"
        }
        finally {
            if ($null -ne $document) { try { $document.Close($false) } catch { } }
        }
    }
    finally {
        try { $word.Quit() } catch { }
    }
}
