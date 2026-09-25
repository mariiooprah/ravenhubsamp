# Ravenhub SA-MP files

Este repositorio es la raíz de archivos del launcher Ravenhub. Las carpetas como
`SAMP`, `data`, `models` y `texdb` se instalan respetando exactamente su ruta en:

`Android/data/com.ravenhub/files/`

## Publicar una actualización

1. Agregá, reemplazá o eliminá archivos normalmente.
2. Confirmá los cambios en la rama `main`.
3. GitHub Actions regenera `manifest.json` automáticamente.
4. La APK compara los SHA-256 y descarga solamente lo que cambió.

No edites `manifest.json` a mano. Las carpetas `.github`, `tools`, `logcat` y
`SAMP/screenshots`, junto con partidas guardadas y archivos locales, no se envían
a los jugadores.
