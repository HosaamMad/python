###########################################
# buildozer.spec – SSHServer (Android APK)
###########################################

[app]
# معلومات أساسية
title           = SSHServer
package.name    = sshserver
package.domain  = org.abd.ssh

# رقم الإصدار (مطلوب من Buildozer)
version         = 1.0.0

# مسار الشيفرة وامتدادات الملفات التي تُضمَّن في الـAPK
source.dir          = .
source.include_exts = py,pem

# المكتبات التي يحتاجها بايثون داخل التطبيق
requirements = python3,paramiko

# الأذونات التي يتطلبها خادم SSH
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE

# تشغيل سكربتك كخدمة في الخلفية
android.services = sshservice: ssh_server.py
android.foreground_service = True

# إعدادات منصة أندرويد
android.api            = 30
android.minapi         = 21
android.sdk            = 30
android.ndk            = 23b
android.archs          = arm64-v8a, armeabi-v7a
android.private_storage = True
android.allow_backup    = False

# نوع المخرجات التي تريدها
android.release_artifact = apk
android.debug_artifact   = apk

# تحسين عرض سجلّ الأخطاء
android.logcat_filters = *:S python:D


################################################
# إعدادات Buildozer نفسها
################################################
[buildozer]
log_level   = 2      # 0=خطأ فقط، 1=معلومات، 2=تصحيح مفصَّل
warn_on_root = 1
