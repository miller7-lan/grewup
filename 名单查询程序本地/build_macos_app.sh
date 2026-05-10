#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$ROOT_DIR/dist-macos"
APP_NAME="Dazzle Secretary"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
CONTENTS="$APP_BUNDLE/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"
APP_RESOURCES="$RESOURCES/app"
ICON_SOURCE="/Users/chenzixuan/Library/Mobile Documents/com~apple~Automator/Documents/dazzle的行政助理.app/Contents/Resources/dazzle_icon.icns"

rm -rf "$DIST_DIR"
mkdir -p "$MACOS" "$APP_RESOURCES"

cp "$ROOT_DIR/secretary.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/agent.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/attendance.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/history.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/ocr.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/roster.py" "$APP_RESOURCES/"
cp "$ROOT_DIR/class_roster.json" "$APP_RESOURCES/"
cp "$ROOT_DIR/grade_roster.json" "$APP_RESOURCES/"
cp "$ROOT_DIR/requirements.txt" "$APP_RESOURCES/"
cp "$ROOT_DIR/requirements-macos.txt" "$APP_RESOURCES/"
cp "$ROOT_DIR/README.md" "$APP_RESOURCES/"

if [ -f "$ICON_SOURCE" ]; then
    cp "$ICON_SOURCE" "$RESOURCES/dazzle_icon.icns"
fi

cat > "$CONTENTS/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleExecutable</key>
    <string>dazzle-secretary</string>
    <key>CFBundleIconFile</key>
    <string>dazzle_icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.dazzle.secretary</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Dazzle Secretary</string>
    <key>CFBundleDisplayName</key>
    <string>Dazzle Secretary</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>3.5</string>
    <key>CFBundleVersion</key>
    <string>35</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$MACOS/dazzle-secretary" <<'LAUNCHER'
#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNNER="$SCRIPT_DIR/../Resources/run-dazzle.command"
chmod +x "$RUNNER"
open -a Terminal "$RUNNER"
LAUNCHER

cat > "$RESOURCES/run-dazzle.command" <<'RUNNER'
#!/bin/zsh
set -euo pipefail

RESOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
BUNDLED_APP="$RESOURCE_DIR/app"
SUPPORT_DIR="$HOME/Library/Application Support/Dazzle Secretary"
APP_DIR="$SUPPORT_DIR/app"
VENV_DIR="$SUPPORT_DIR/venv"
PORT="${DAZZLE_SECRETARY_PORT:-8501}"

echo "Dazzle Secretary 启动器"
echo "应用数据目录：$SUPPORT_DIR"
mkdir -p "$SUPPORT_DIR"

echo "同步应用文件..."
ditto "$BUNDLED_APP" "$APP_DIR"

if ! command -v python3 >/dev/null 2>&1; then
    echo ""
    echo "未找到 python3。请先安装 Python 3.10+，然后重新打开本应用。"
    echo "推荐安装地址：https://www.python.org/downloads/macos/"
    read -r "REPLY?按回车退出..."
    exit 1
fi

PYTHON_VERSION="$(python3 - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
echo "检测到 Python $PYTHON_VERSION"

if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "首次启动：创建独立 Python 环境..."
    python3 -m venv "$VENV_DIR"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "安装/更新基础依赖..."
"$PY" -m pip install --upgrade pip
"$PIP" install -r "$APP_DIR/requirements.txt"

echo "安装/更新 macOS OCR 依赖（PaddleOCR 首次可能较慢）..."
if ! "$PIP" install -r "$APP_DIR/requirements-macos.txt"; then
    echo ""
    echo "OCR 高精度依赖安装失败，应用仍可启动，但截图 OCR 可能不可用。"
    echo "你可以稍后在网络稳定时重新打开应用重试。"
fi

cd "$APP_DIR"
echo ""
echo "启动 Dazzle Secretary..."
echo "浏览器地址：http://localhost:$PORT"
(sleep 4; open "http://localhost:$PORT") >/dev/null 2>&1 &
exec "$PY" -m streamlit run secretary.py --server.port "$PORT" --server.headless true --browser.gatherUsageStats false
RUNNER

chmod +x "$MACOS/dazzle-secretary" "$RESOURCES/run-dazzle.command"

if command -v codesign >/dev/null 2>&1; then
    codesign --force --deep --sign - "$APP_BUNDLE" >/dev/null 2>&1 || true
fi

ditto -c -k --keepParent "$APP_BUNDLE" "$DIST_DIR/Dazzle-Secretary-macOS.zip"

echo "已生成："
echo "$APP_BUNDLE"
echo "$DIST_DIR/Dazzle-Secretary-macOS.zip"
