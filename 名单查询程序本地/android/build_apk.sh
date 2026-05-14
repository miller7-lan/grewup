#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$ROOT_DIR/app"
SDK_DIR="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
PLATFORM_JAR="$SDK_DIR/platforms/android-36.1/android.jar"
BUILD_TOOLS="$SDK_DIR/build-tools/36.1.0"
JBR="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
JAVAC="$JBR/bin/javac"
JAR="$JBR/bin/jar"
KEYTOOL="$JBR/bin/keytool"
export JAVA_HOME="$JBR"
export PATH="$JBR/bin:$PATH"

OUT="$ROOT_DIR/out"
GEN="$OUT/gen"
RES_COMPILED="$OUT/compiled-res"
CLASSES="$OUT/classes"
DEX="$OUT/dex"
UNSIGNED="$OUT/dazzle-unsigned.apk"
ALIGNED="$OUT/dazzle-aligned.apk"
APK="$OUT/DazzleSecretary-debug.apk"
KEYSTORE="$OUT/debug.keystore"

rm -rf "$OUT"
mkdir -p "$GEN" "$RES_COMPILED" "$CLASSES" "$DEX"

"$BUILD_TOOLS/aapt2" compile --dir "$APP_DIR/src/main/res" -o "$RES_COMPILED/resources.zip"
"$BUILD_TOOLS/aapt2" link \
  -I "$PLATFORM_JAR" \
  --manifest "$APP_DIR/src/main/AndroidManifest.xml" \
  --java "$GEN" \
  -A "$APP_DIR/src/main/assets" \
  --auto-add-overlay \
  -o "$UNSIGNED" \
  "$RES_COMPILED/resources.zip"

find "$APP_DIR/src/main/java" "$GEN" -name "*.java" > "$OUT/sources.list"
"$JAVAC" -source 8 -target 8 -encoding UTF-8 \
  -bootclasspath "$PLATFORM_JAR" \
  -d "$CLASSES" \
  @"$OUT/sources.list"

"$JAR" cf "$OUT/classes.jar" -C "$CLASSES" .

"$BUILD_TOOLS/d8" \
  --lib "$PLATFORM_JAR" \
  --min-api 23 \
  --output "$DEX" \
  "$OUT/classes.jar"

cd "$DEX"
zip -q "$UNSIGNED" classes.dex
cd "$ROOT_DIR"

"$BUILD_TOOLS/zipalign" -f 4 "$UNSIGNED" "$ALIGNED"

if [ ! -f "$KEYSTORE" ]; then
  "$KEYTOOL" -genkeypair \
    -keystore "$KEYSTORE" \
    -storepass android \
    -keypass android \
    -alias androiddebugkey \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -dname "CN=Android Debug,O=Dazzle,C=CN" >/dev/null
fi

"$BUILD_TOOLS/apksigner" sign \
  --ks "$KEYSTORE" \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$APK" \
  "$ALIGNED"

"$BUILD_TOOLS/apksigner" verify "$APK"
echo "APK generated: $APK"
