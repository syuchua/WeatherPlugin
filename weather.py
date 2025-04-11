import aiohttp, os
from typing import Optional
from rapidfuzz import process, fuzz
from app.plugin.plugin_base import PluginBase
from app.logger import logger
from .city_codes import get_city_code, get_city_name, CITY_CODES

@PluginBase.register("weather")
class WeatherPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "Weather Plugin"
        self.register_name = "weather"
        self.version = "1.0.0"
        self.description = "提供天气查询功能"
        self.WEATHER_KEYWORDS = ['天气', '气温', '温度', '下雨', '阴天', '晴天', '多云', '预报']

    async def on_load(self):
        """当插件被加载时调用"""
        #logger.info(f"正在加载 {self.name}")
        self.load_config()
        #logger.info(f"{self.name} 加载完成")

    async def on_unload(self):
        """当插件被卸载时调用"""
        logger.info(f"{self.name} 已卸载")

    async def on_enable(self):
        """当插件被启用时调用"""
        await super().on_enable()
        #logger.info(f"{self.name} 已启用")

    async def on_disable(self):
        """当插件被禁用时调用"""
        await super().on_disable()
        logger.info(f"{self.name} 已禁用")

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.WEATHER_BASE_URL = config.get('WEATHER_BASE_URL', '')
        self.AMAP_API_KEY = config.get('AMAP_API_KEY', '')

    def extract_city(self, text: str) -> Optional[str]:
        logger.debug(f"Extracting city from: {text}")
        
        # 去除常见的无关词
        for keyword in self.WEATHER_KEYWORDS:
            text = text.replace(keyword, '')
        
        logger.debug(f"Text after removing keywords: {text}")
        
        try:
            # 使用模糊匹配找到最可能的城市名
            result = process.extractOne(text, CITY_CODES.keys(), scorer=fuzz.partial_ratio)
            
            logger.debug(f"Fuzzy matching result: {result}")
            
            if result and len(result) >= 2:
                city, score = result[0], result[1]
                logger.debug(f"Extracted city: {city}, match score: {score}")
                
                # 如果匹配度低于某个阈值，认为没有找到有效的城市名
                if score < 60:
                    logger.info(f"No valid city name found. Best match was '{city}' with score {score}")
                    return None
                
                return city
            else:
                logger.info("No city match found")
                return None
        except Exception as e:
            logger.error(f"Error in extract_city: {e}", exc_info=True)
            return None

    async def on_message(self, message):
        content = message.get('content', '')
        if isinstance(content, str):
            if any(keyword in content for keyword in self.WEATHER_KEYWORDS):
                city = self.extract_city(content)
                if city:
                    if '预报' in content:
                        return await self.get_forecast(city)
                    else:
                        return await self.get_weather(city)
                else:
                    return "抱歉，我无法识别您提到的城市。请确保您的消息中包含有效的城市名称。"
        return None

    async def get_weather(self, city):
        city_code = get_city_code(city)
        if not city_code:
            logger.warning(f"City code not found for: {city}")
            return f"抱歉，未找到 {city} 的城市编码。请检查城市名称是否正确。"

        params = {
            "key": self.AMAP_API_KEY,
            "city": city_code,
            "extensions": "base",
            "output": "JSON"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.WEATHER_BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "1":  # API 调用成功
                            weather = data["lives"][0]
                            return f"{city}天气：{weather['weather']}，温度：{weather['temperature']}°C，湿度：{weather['humidity']}%，风向：{weather['winddirection']}，风力：{weather['windpower']}级"
                        else:
                            logger.error(f"Weather API error: {data['info']}")
                            return f"获取{city}天气信息失败：{data['info']}"
                    else:
                        logger.error(f"Weather API request failed with status code: {response.status}")
                        return f"天气信息获取失败（状态码：{response.status}），请稍后再试"
        except Exception as e:
            logger.error(f"Error in get_weather: {e}")
            return f"获取天气信息时发生错误：{str(e)}"

    async def get_forecast(self, city):
        city_code = get_city_code(city)
        if not city_code:
            logger.warning(f"City code not found for: {city}")
            return f"抱歉，未找到 {city} 的城市编码。请检查城市名称是否正确。"

        params = {
            "key": self.AMAP_API_KEY,
            "city": city_code,
            "extensions": "all",
            "output": "JSON"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.WEATHER_BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "1":  # API 调用成功
                            forecasts = data["forecasts"][0]["casts"]
                            result = f"{city}未来3天天气预报：\n"
                            for forecast in forecasts[:3]:  # 只取未来3天的预报
                                result += f"{forecast['date']}：白天{forecast['dayweather']}，夜间{forecast['nightweather']}，温度：{forecast['nighttemp']}°C - {forecast['daytemp']}°C\n"
                            return result.strip()
                        else:
                            logger.error(f"Weather forecast API error: {data['info']}")
                            return f"获取{city}天气预报失败：{data['info']}"
                    else:
                        logger.error(f"Weather forecast API request failed with status code: {response.status}")
                        return f"天气预报获取失败（状态码：{response.status}），请稍后再试"
        except Exception as e:
            logger.error(f"Error in get_forecast: {e}")
            return f"获取天气预报时发生错误：{str(e)}"

    def get_commands(self):
        return [
            {"name": "天气", "description": "查询指定城市的当前天气，用法：天气 城市名"},
            {"name": "天气预报", "description": "查询指定城市的未来3天天气预报，用法：天气预报 城市名"}
        ]

    async def handle_command(self, command, args):
        if command == "天气":
            return await self.get_weather(args)
        elif command == "天气预报":
            return await self.get_forecast(args)
        return await super().handle_command(command, args)
