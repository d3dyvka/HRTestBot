import asyncio
from create_bot import bot, dp
from handlers.handlers import router

async def main():
    try:
        dp.include_router(router)
        await dp.start_polling(bot)
    finally:
        dp.stop_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
