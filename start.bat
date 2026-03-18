@echo off
:: FORTALEZA DIGITAL - CONTROL DE LANZAMIENTO
:: Expert Version v1.0

echo [FORTALEZA] Iniciando orquestación de contenedores...
docker compose up -d

echo [FORTALEZA] Verificando estado de los servicios...
timeout /t 5 > nul

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [FINALIZADO] Sistema operativo en: http://localhost:8501
echo Para ver los logs del sistema, ejecute: docker compose logs -f
pause
