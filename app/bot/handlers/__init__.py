from app.bot.handlers.start import router as start_router
from app.bot.handlers.orders import router as orders_router


routers = [
    start_router,
    orders_router
]
