# Setup Maestro en Mac — Guía paso a paso

## 1. Instalar Android Studio

1. Descargar desde https://developer.android.com/studio
2. Instalar arrastrando a Aplicaciones
3. Abrir Android Studio → seguir el wizard de configuración
4. En el wizard, asegurarse de instalar:
   - Android SDK
   - Android SDK Platform-Tools (incluye adb)
   - Android Emulator

## 2. Crear emulador (AVD)

1. Android Studio → Tools → Device Manager
2. Click en "Create Virtual Device"
3. Seleccionar **Pixel 6** (o similar)
4. Seleccionar imagen del sistema: **API 33** (Android 13) o superior
   - Si no aparece, click en "Download" para bajar la imagen
   - Elegir la que diga **arm64-v8a** (Mac con Apple Silicon) o **x86_64** (Mac Intel)
5. Finish → el emulador queda creado

### Verificar que funciona
- En Device Manager, click en el botón Play del emulador
- Debe abrirse una ventana con un celular Android virtual

## 3. Configurar adb en el PATH

Agregar al final de `~/.zshrc`:

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator
```

Luego:
```bash
source ~/.zshrc
```

Verificar:
```bash
adb devices
# Debe mostrar el emulador si está corriendo
```

## 4. Instalar Maestro

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

Verificar:
```bash
maestro --version
```

## 5. Instalar el APK en el emulador

```bash
# Pedirle el APK a Rodrigo y luego:
adb install ruta/al/yom-app.apk
```

O arrastrar el archivo .apk directamente a la ventana del emulador.

## 6. Explorar la app con Maestro Studio

```bash
maestro studio
```

Esto abre un inspector visual en el browser donde puedes:
- Ver todos los elementos de la pantalla actual
- Copiar los IDs y textos de cada botón, campo, etc.
- Probar comandos de Maestro en vivo

Usa esto para ajustar los selectores de los flows en `flows/`.

## 7. Correr el primer test

```bash
cd ~/Desktop/YOM/qa/tests/app

# Copiar y completar la config
cp config/env.example.yaml config/env.yaml
# Editar env.yaml con los datos reales del cliente de prueba

# Correr el test de login
maestro test flows/01-login.yaml
```

## Checklist resumen

- [ ] Android Studio instalado
- [ ] Emulador creado y funcionando
- [ ] adb en el PATH (`adb devices` funciona)
- [ ] Maestro instalado (`maestro --version` funciona)
- [ ] APK instalado en el emulador
- [ ] `maestro studio` abre y muestra la app
- [ ] `env.yaml` configurado con datos del cliente de prueba
