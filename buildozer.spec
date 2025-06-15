###########################################
# buildozer.spec – SSHServer (Android APK)
###########################################

[app]
title = SSHServer
package.name = sshserver
package.domain = org.abd.ssh
version = 1.0.0

source.dir = .
source.include_exts = py,pem
requirements = python3,paramiko

android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE

android.services = sshservice: ssh_server.py
android.foreground_service = True

android.api = 30
android.minapi = 21
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a
android.private_storage = True
android.allow_backup = False

android.accept_sdk_license = True
android.release_artifact = apk
android.debug_artifact = apk
android.logcat_filters = *:S python:D
android.ant_path = /usr/bin/ant

[buildozer]
log_level = 2
warn_on_root = 1
