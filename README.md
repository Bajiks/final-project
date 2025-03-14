# Exportar variables de entorno desde .env
set -o allexport && source .env && set +o allexport
