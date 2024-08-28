# 适用于MY_QBOT项目的天气插件

这个插件使用高德开放平台的 API 来提供实时天气信息和天气预报功能。

## 功能

- 查询指定城市的实时天气信息
- 获取指定城市的未来天气预报
- 支持自然语言处理，可以从用户输入中提取城市名称

## 安装

1. 克隆此仓库到你的插件目录：

   ```
   git clone https://github.com/your-username/weather-plugin.git
   ```

2. 安装依赖：

   ```
   pip install -r requirements.txt
   ```

3. 在高德开放平台注册并获取 API 密钥。

4. 在 `config.json` 文件中配置你的 API 密钥和其他设置。

## 配置

在 `config.json` 文件中设置以下参数：
```
{
"WEATHER_BASE_URL": "https://restapi.amap.com/v3/weather/weatherInfo",
"AMAP_API_KEY": "你的高德API密钥"
}
```


## 使用

插件支持以下命令：

- `/天气 [城市名]`: 查询指定城市的当前天气
- `/天气预报 [城市名]`: 查询指定城市的未来天气预报

例如：

/天气 北京
/天气预报 上海


插件也支持自然语言查询，例如：

今天北京天气怎么样？
明天上海会下雨吗？


## 依赖

- aiohttp
- rapidfuzz

## 注意事项

- 确保你有足够的 API 调用额度
- 遵守高德开放平台的使用条款和政策
- 插件使用模糊匹配来识别城市名，可能会有误判，请在必要时明确指定城市名

## 贡献

欢迎提交 issues 和 pull requests 来帮助改进这个插件。

## 许可证

[MIT License](LICENSE)