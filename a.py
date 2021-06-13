from kastle import create_app

import asyncio


async def main():
    app = create_app()
    await app.listen()


asyncio.run(main())
