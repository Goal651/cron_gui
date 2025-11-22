# Release Guide

This document outlines the process for creating a new release of **Cron GUI**.

## 1. Update Version Numbers

Before creating a release, ensure the version number is updated in the following files:

* `cron_gui/__init__.py`: `__version__ = "X.Y.Z"`
* `setup.py`: `version="X.Y.Z"`
* `build_deb.sh`: `VERSION="X.Y.Z"`

## 2. Build Artifacts

Run the build scripts to generate the release files:

```bash
# 1. Build Python Package (Wheel & Source)
python3 setup.py sdist bdist_wheel

# 2. Build Debian Package (.deb)
./build_deb.sh
```

This will create the following files in `dist/`:

* `cron_gui-X.Y.Z-py3-none-any.whl`
* `cron_gui-X.Y.Z.tar.gz`
* `cron-gui_X.Y.Z_all.deb`

## 3. Create Git Tag

Tag the specific commit you want to release:

```bash
git add .
git commit -m "Bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main --tags
```

## 4. Create GitHub Release

1. Go to the **Releases** section of your GitHub repository.
2. Click **Draft a new release**.
3. Choose the tag you just pushed (`vX.Y.Z`).
4. Title the release `vX.Y.Z`.
5. Add a description of the changes (changelog).
6. **Upload the artifacts** from the `dist/` folder (the `.whl`, `.tar.gz`, and `.deb` files).
7. Click **Publish release**.

## Automating with GitHub Actions (Optional)

You can automate this process using GitHub Actions. Create a file at `.github/workflows/release.yml` to automatically build and upload assets when you push a tag.
