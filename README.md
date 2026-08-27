# Driver's License Generator（演示项目）

这是一个用于开发测试的美国驾照号码与 PDF417 条码演示项目。生成的内容是随机的合成数据，不是真实证件，也不能用于身份验证、制证或冒充他人。

## 最快启动方式

项目提供了一个零依赖的 Python 开发服务器，同时服务网页和 API。macOS/Linux 终端执行：

```bash
cd /Users/x/code/driver-license-generator
python3 backend/server.py
```

浏览器打开 <http://127.0.0.1:8080>。页面中选择州、填写名字和姓氏，点击 **Generate License**；随后会显示合成号码和 PDF417 条码，点击 **Download Barcode** 可下载 SVG。**Toggle Theme** 可切换深色模式。

按 `Ctrl-C` 停止服务器。

## API

生成：

```bash
curl -X POST http://127.0.0.1:8080/generate \
  -H 'Content-Type: application/json' \
  -d '{"state":"CA","firstName":"John","lastName":"Doe"}'
```

校验本项目生成的合成格式：

```bash
curl -X POST http://127.0.0.1:8080/validate \
  -H 'Content-Type: application/json' \
  -d '{"state":"CA","licenseNumber":"CA-JD-123456"}'
```

后端也保留了 `backend/src` 下的 Ktor 原型，但它不是当前默认启动路径；默认 Python 服务便于无需下载 Gradle/Kotlin 工具链的本地体验。

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
