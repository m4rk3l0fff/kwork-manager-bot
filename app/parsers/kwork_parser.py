from urllib.parse import urljoin
from re import sub

from playwright.async_api import Page
from app.models.order import Order
from app.utils.human import human_delay


class KworkParser:
    def __init__(self, page: Page):
        self.page = page


    async def get_orders(self, url: str = 'https://kwork.ru/projects', stop_at: str | None = None):
        await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )
        await human_delay()

        await self.page.wait_for_selector('.want-card')

        cards, orders = await self.page.query_selector_all('.want-card'), []
        for card in cards:
            try:
                title_tag = await card.query_selector('a')

                order_url = urljoin(url, await title_tag.get_attribute('href'))
                if stop_at and order_url == stop_at:
                    break

                show_more_button = await card.query_selector("text=Показать полностью")
                if show_more_button:
                    await show_more_button.click()

                    # await self.page.wait_for_function(
                    #     """el => !el.innerText.includes('...')""",
                    #     arg=await card.query_selector('[class*="description-text"]')
                    # )

                title = await title_tag.inner_text()
                description = (
                    await (await card.query_selector('[class*="description"]')).inner_text()
                ).replace('Скрыть', '').strip()
                prices = tuple([
                    int(sub(r'\D+', '', await price_tag.inner_text()))
                    for price_tag in await card.query_selector_all('.wants-card__right > div')
                ])
                informers = await card.query_selector_all('.want-card__informers-row span')
                responses = int((await informers[1].inner_text()).split()[1])

                orders.append(Order(
                    title=title,
                    description=description,
                    prices=prices,
                    responses=responses,
                    url=order_url
                ))

            except Exception as ex:
                print(f'Ошибка: {ex}')

        return orders
