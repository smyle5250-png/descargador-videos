# Descargador de Videos 🎵📸📘

Descargador propio de TikTok, Instagram y Facebook. Sin redirigir a otras páginas.

---

## Cómo subir a Render (gratis)

### Paso 1 — Crear cuenta en GitHub
Si no tenés, creá una en https://github.com (es gratis)

### Paso 2 — Subir este proyecto a GitHub
1. Entrá a https://github.com/new
2. Poné cualquier nombre, ej: `descargador-videos`
3. Hacé clic en "Create repository"
4. Subí todos los archivos de esta carpeta ahí
   (podés arrastrarlos directo en el navegador)

### Paso 3 — Crear cuenta en Render
1. Entrá a https://render.com
2. Registrate con tu cuenta de GitHub

### Paso 4 — Crear el servicio web
1. En Render, hacé clic en "New +" → "Web Service"
2. Conectá tu repositorio de GitHub
3. Render detecta el `render.yaml` automáticamente
4. Hacé clic en "Create Web Service"
5. Esperá unos minutos mientras despliega

### Paso 5 — ¡Listo!
Render te da una URL tipo:
`https://descargador-videos.onrender.com`

Esa es tu página, andá ahí y pegá cualquier link de TikTok, Instagram o Facebook.

---

## Archivos del proyecto

```
descargador/
├── app.py              ← el servidor (cerebro del proyecto)
├── requirements.txt    ← librerías necesarias
├── render.yaml         ← configuración para Render
└── templates/
    └── index.html      ← la página web
```

---

## Nota importante
- Solo funciona con videos **públicos**
- En el plan gratis de Render, el servidor "duerme" si no lo usás por 15 minutos.
  La primera vez que entrés puede tardar ~30 segundos en despertar.
