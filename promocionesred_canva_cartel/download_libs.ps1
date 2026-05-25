# download_libs.ps1
# Script PowerShell para descargar las librerías externas necesarias para el módulo
# Ejecutar una sola vez desde este directorio

$libDir = "$PSScriptRoot\static\lib"

# Crear directorio si no existe
if (-not (Test-Path $libDir)) {
    New-Item -ItemType Directory -Path $libDir -Force | Out-Null
    Write-Host "[OK] Directorio creado: $libDir" -ForegroundColor Green
}

$libs = @(
    @{
        name = "html2canvas.min.js"
        url  = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
    },
    @{
        name = "jspdf.umd.min.js"
        url  = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"
    },
    @{
        name = "qrious.min.js"
        url  = "https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"
    }
)

foreach ($lib in $libs) {
    $dest = Join-Path $libDir $lib.name
    if (Test-Path $dest) {
        Write-Host "[SKIP] Ya existe: $($lib.name)" -ForegroundColor Yellow
    } else {
        Write-Host "[DL] Descargando $($lib.name)..." -ForegroundColor Cyan
        try {
            Invoke-WebRequest -Uri $lib.url -OutFile $dest -UseBasicParsing
            $size = (Get-Item $dest).Length
            Write-Host "      -> OK ($size bytes)" -ForegroundColor Green
        } catch {
            Write-Host "      -> ERROR: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Librerías listas en: $libDir" -ForegroundColor Green
Write-Host "Próximo paso: instalar el módulo en Odoo con:" -ForegroundColor White
Write-Host "  docker exec -it <container> odoo -d <db> -i promocionesred_canva_cartel" -ForegroundColor Cyan
