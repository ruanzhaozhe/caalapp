CONFIG+= release shared rtti no_plugin_manifest directwrite qpa
host_build {
    QT_ARCH = i386
    QT_TARGET_ARCH = i386
} else {
    QT_ARCH = i386
}
QT_CONFIG += minimal-config small-config medium-config large-config full-config release shared zlib icu dynamicgl png freetype harfbuzz accessibility opengl openssl-linked dbus audio-backend directwrite native-gestures qpa concurrent
#versioning 
QT_VERSION = 5.6.0
QT_MAJOR_VERSION = 5
QT_MINOR_VERSION = 6
QT_PATCH_VERSION = 0

QT_EDITION = OpenSource