import sys
import asyncio
import logging
import telegram

async def main():
    loop = asyncio.create_task(telegram.main_loop())

    await asyncio.gather(loop)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)


    asyncio.run(main())
    print('hola ... ')
