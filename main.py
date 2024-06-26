"""Download music app"""

import asyncio

from utils.app import App


async def main():
    """Main def"""

    app = App()

    await app.run()

    print("DONE!")


if __name__ == "__main__":
    asyncio.run(main())
