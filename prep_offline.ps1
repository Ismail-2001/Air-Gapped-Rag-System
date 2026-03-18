# PREPARACIÓN PARA ENTORNO AISLADO (AIR-GAPPED)
# Use este script en una máquina CON internet antes de transferir por USB.

$Images = @("fortaleza-app:latest", "fortaleza-ollama:latest", "ollama/ollama:latest")

Write-Host "`n[FORTALEZA] Iniciando exportación para entorno aislado...`n" -ForegroundColor Cyan

# Asegurarse de que las imágenes están construidas y tienen los modelos precargados.
Write-Host "[1/3] Construyendo imágenes locales..."
docker compose build

# Exportar imágenes a archivos .tar.gz
Write-Host "[2/3] Exportando imágenes a .tar.gz..."
foreach ($image in $Images) {
    $filename = $image.Replace("/", "_").Replace(":", "_") + ".tar.gz"
    Write-Host "... Exportando $image..."
    docker save $image | gzip > $filename
}

Write-Host "[3/3] Exportación completada." -ForegroundColor Green
Write-Host "Transfiera los archivos .tar.gz y el repositorio completo a su hardware aislado."
Write-Host "En el hardware aislado ejecute: 'docker load < [archivo].tar.gz' para cada imagen.`n"

pause
