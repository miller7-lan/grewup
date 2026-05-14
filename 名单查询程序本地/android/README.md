# Dazzle Secretary Android

0 成本原生 Android 首版。使用 Java + Android Views，不接 AI、不联网、不内置个人名单。图片文字识别使用免费的 Google ML Kit 端侧 OCR。

## 功能

- 班团支书：维护本班底册，粘贴文本核查。
- 年团支书：维护多个分组底册，支持全年级或单个分组核查。
- 核查范围：支持全体、仅党员、仅团员、仅群众。
- 图片 OCR：选择截图或图片，识别文字后自动填入核查文本框。
- 底册分类：党员、团员、群众三个分类分别编辑。
- 手机复制：每个分类名单都可以一键复制。
- 结果页：展示完成率、已完成、未完成、未知姓名。
- 年级汇总：按分组展示应核查、已完成、未完成、完成率。
- 记录页：保存最近核查摘要。

## 默认数据

安装后的默认底册为空，用户在手机端自行录入或粘贴。不会携带桌面版里的个人名单。

## 构建 APK

本机已有 Android Studio 和 Android SDK 时，推荐使用 Gradle 构建新版 APK：

```bash
./gradlew assembleDebug
```

输出：

```text
app/build/outputs/apk/debug/app-debug.apk
```

这个 APK 使用本地 debug key 签名，适合真机测试或发给少量同学试用。正式放网站下载时，可以后续再做 release 签名。

`build_apk.sh` 是早期无依赖版本的快速打包脚本；加入 ML Kit OCR 后，以 Gradle 输出为准。

## Android Studio

直接用 Android Studio 打开 `android/` 目录即可查看源码。

如果打开后提示 Gradle/JDK 相关错误：

1. 进入 `Settings / Preferences`。
2. 找到 `Build, Execution, Deployment > Build Tools > Gradle`。
3. 将 `Gradle JDK` 设为 Android Studio 自带的 `jbr-21` 或 `Embedded JDK`。
4. 重新 Sync Project。

项目内已经提供 `gradlew` 和 `gradle.properties`，会优先使用 Android Studio 自带 JBR。首次构建 OCR 版本时，Gradle 会下载免费的 ML Kit 依赖。
