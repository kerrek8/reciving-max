import asyncio
import logging

from app.bot import bot
from app.config import CHAT_ID
from app.utils import parse_message

queue: asyncio.Queue = asyncio.Queue()

async def send_with_retry(text, retries: int = 3):
    for attempt in range(retries):
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"{text}",
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logging.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)

    return False


async def worker():
    while True:
        payload = await queue.get()

        try:
            msg = parse_message(payload)

            if msg["type"] == "text":
                await send_with_retry(msg["text"])

            elif msg["type"] == "photo":
                await bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=msg["url"],
                    caption=msg["text"],
                    parse_mode="HTML"
                )

            elif msg["type"] == "video":
                await bot.send_video(
                    chat_id=CHAT_ID,
                    video=msg["url"],
                    caption=msg["text"],
                    parse_mode="HTML"
                )

            else:
                await send_with_retry(msg["text"])

        except Exception as e:
            logging.exception(f"Worker error: {e}")

        finally:
            queue.task_done()
