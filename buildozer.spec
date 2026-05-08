[app]

title = Master Torque
package.name = mastertorque
package.domain = org.mastertorque

source.dir = .
source.include_exts = py,png,json

version = 1.0

requirements = python3,kivy,reportlab

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

presplash.color = #0F172A

[buildozer]
log_level = 2
warn_on_root = 1
