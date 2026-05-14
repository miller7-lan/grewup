# Dazzle Secretary Android

0 成本原生 Android 首版。使用 Java + Android Views，不接 AI/OCR，不联网，不内置个人名单。

## 功能

- 班团支书：维护本班底册，粘贴文本核查。
- 年团支书：维护多个分组底册，支持全年级或单个分组核查。
- 底册分类：党员、团员、群众三个分类分别编辑。
- 手机复制：每个分类名单都可以一键复制。
- 结果页：展示完成率、已完成、未完成、未知姓名。
- 年级汇总：按分组展示应核查、已完成、未完成、完成率。
- 记录页：保存最近核查摘要。

## 默认数据

安装后的默认底册为空，用户在手机端自行录入或粘贴。不会携带桌面版里的个人名单。

## 构建 APK

本机已有 Android Studio 和 Android SDK 时，可直接运行：

```bash
./build_apk.sh
```

输出：

```text
out/DazzleSecretary-debug.apk
```

这个 APK 使用本地 debug key 签名，适合真机测试或发给少量同学试用。正式放网站下载时，可以后续再做 release 签名。

## Android Studio

直接用 Android Studio 打开 `android/` 目录即可查看源码。当前项目也提供 Gradle 配置，但 `build_apk.sh` 不依赖 Gradle 下载，适合先快速出包。
