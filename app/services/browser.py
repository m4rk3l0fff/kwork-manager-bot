from playwright.async_api import async_playwright, ViewportSize
from playwright_stealth import Stealth


class Browser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled'
            ]
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
            viewport=ViewportSize(width=1280, height=800),
            locale='ru-RU'
        )

        await Stealth().apply_stealth_async(self.context)

        self.page = await self.context.new_page()

    async def stop(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
