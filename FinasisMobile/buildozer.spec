[app]
title = FinAsis
package.name = finasis
package.domain = org.finasis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,kivy==2.2.1,kivymd==1.1.1,kivy-garden.graph==0.4.0,requests==2.31.0,python-dotenv==1.0.0,plyer==2.1.0

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# (str) Android NDK version to use
android.ndk_api = 21

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1 