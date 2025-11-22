#!/bin/bash

# Exit on error
set -e

APP_NAME="cron-gui"
VERSION="0.1.0"
ARCH="all"
DEB_NAME="${APP_NAME}_${VERSION}_${ARCH}"
BUILD_DIR="build_deb"
DEB_DIR="$BUILD_DIR/$DEB_NAME"

echo "📦 Building Debian package for $APP_NAME v$VERSION..."

# 1. Clean previous builds
rm -rf "$BUILD_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/lib/python3/dist-packages"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/scalable/apps"
python3 setup.py sdist bdist_wheel

# 2. Create Control File
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.8), python3-gi, python3-gi-cairo, gir1.2-gtk-4.0, gir1.2-adw-1, python3-crontab, python3-croniter
Maintainer: Cron GUI Team <maintainer@example.com>
Description: Modern Cron GUI Manager
 A modern, beautiful Linux desktop application for managing cron jobs 
 with a graphical interface. Built with Python and GTK4.
EOF

# 3. Create Post-Install Script (to update icon cache)
cat > "$DEB_DIR/DEBIAN/postinst" << EOF
#!/bin/sh
set -e
if [ "\$1" = "configure" ]; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
EOF
chmod 755 "$DEB_DIR/DEBIAN/postinst"

# 4. Install Python package into the deb structure
# We use pip to install into the target directory
pip install . --target "$DEB_DIR/usr/lib/python3/dist-packages" --no-deps --upgrade

# 5. Clean up dist-info/egg-info to keep it clean (optional, but good for system packages)
# rm -rf "$DEB_DIR/usr/lib/python3/dist-packages/"*.dist-info
# rm -rf "$DEB_DIR/usr/lib/python3/dist-packages/"*.egg-info

# 6. Install executable script
cat > "$DEB_DIR/usr/bin/$APP_NAME" << EOF
#!/bin/sh
export PYTHONPATH=/usr/lib/python3/dist-packages
exec python3 -m cron_gui.main "\$@"
EOF
chmod 755 "$DEB_DIR/usr/bin/$APP_NAME"

# Need to ensure main.py is importable as a module or adjust entry point
# Let's move main.py to cron_gui/__main__.py for better module execution
cp main.py "$DEB_DIR/usr/lib/python3/dist-packages/cron_gui/main.py"

# 7. Install Desktop File
cp cron-gui.desktop "$DEB_DIR/usr/share/applications/"
# Update Exec path in desktop file for installed version
sed -i "s|Exec=.*|Exec=$APP_NAME|" "$DEB_DIR/usr/share/applications/cron-gui.desktop"
# Update Icon path to use system icon
sed -i "s|Icon=.*|Icon=$APP_NAME|" "$DEB_DIR/usr/share/applications/cron-gui.desktop"

# 8. Install Icon
cp assets/icon.svg "$DEB_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"

# 9. Build the .deb package
dpkg-deb --build "$DEB_DIR"

# 10. Move artifact and clean up
mkdir -p dist
mv "$BUILD_DIR/$DEB_NAME.deb" dist/
echo "🧹 Cleaning up build directory..."
rm -rf "$BUILD_DIR"

echo "✅ Package created successfully: dist/$DEB_NAME.deb"
