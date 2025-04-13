[app]
title = FinAsis
package.name = finasis
package.domain = org.finasis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.2.1,kivymd==1.1.1,kivy-garden.graph==0.4.0,requests==2.31.0,python-dotenv==1.0.0

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1 