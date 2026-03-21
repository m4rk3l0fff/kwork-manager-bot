import asyncio
from playwright.async_api import async_playwright


async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://kwork.ru/login")

        print("👉 ВОЙДИ В АККАУНТ ВРУЧНУЮ")
        print("👉 Потом нажми ENTER в терминале")
        input()

        await context.storage_state(path="data/session.json")

        print("✅ Сессия сохранена")

        await browser.close()


asyncio.run(login())
