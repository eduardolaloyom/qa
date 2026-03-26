# APP Smoke Tests — YOM

Smoke tests automatizados para la APP de vendedores usando [Maestro](https://maestro.mobile.dev/).

## Requisitos

1. **Maestro CLI**
2. **Android SDK** con emulador configurado (o dispositivo físico conectado)
3. **APK de la app** (debug o release)
4. **Cliente de prueba** configurado en producción con datos fijos

## Setup

### 1. Instalar Maestro

```bash
# macOS / Linux
curl -Ls "https://get.maestro.mobile.dev" | bash

# Verificar instalación
maestro --version
```

### 2. Emulador Android

```bash
# Si ya tienes Android Studio, crear un AVD:
# Android Studio → Device Manager → Create Device → Pixel 6 → API 33+

# O desde CLI:
sdkmanager "system-images;android-33;google_apis;arm64-v8a"
avdmanager create avd -n yom_test -k "system-images;android-33;google_apis;arm64-v8a" -d pixel_6

# Iniciar emulador
emulator -avd yom_test
```

### 3. Instalar APK en emulador

```bash
adb install path/to/yom-app.apk
```

### 4. Configurar variables

Copiar `config/env.example.yaml` a `config/env.yaml` y completar con datos del cliente de prueba.

## Ejecutar tests

```bash
# Todos los flujos
./scripts/run-all.sh

# Un flujo específico
maestro test flows/01-login.yaml

# Con grabación de video
maestro record flows/01-login.yaml
```

## Estructura

```
tests/app/
├── flows/           # Flujos de test en YAML
│   ├── 01-login.yaml
│   ├── 02-sync.yaml
│   ├── 03-comercios.yaml
│   ├── 04-catalogo.yaml
│   ├── 05-pedido.yaml
│   ├── 06-precios.yaml
│   ├── 07-offline.yaml
│   └── helpers/
│       └── login.yaml
├── config/
│   ├── env.example.yaml
│   └── env.yaml        # (gitignored)
└── scripts/
    └── run-all.sh
```
