[app]

# App info
title = Yatoshi
package.name = yatoshi
package.domain = org.yatoshi

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

# Version
version = 1.0

# Requirements — python3 + kivy + useful packages
requirements = python3,kivy,plyer,android,pyjnius,requests,pillow,numpy

# Orientation
orientation = portrait

# Android
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# Intent filter — open .py files with Yatoshi
android.manifest.intent_filters = intent_filters.xml

# Icon (optional, will use default if missing)
# icon.filename = %(source.dir)s/icon.png

# Fullscreen
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0
