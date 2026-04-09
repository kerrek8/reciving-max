import asyncio
import logging

from app.bot import bot
from app.config import CHAT_ID
from app.utils import format_payload

queue: asyncio.Queue = asyncio.Queue()
    

async def send_with_retry(text: str, retries: int = 3):
    for attempt in range(retries):
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"<pre>{text}</pre>",
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logging.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(2)

    return False


async def worker():
    while True:
        payload = await queue.get()

        try:
            chunks = format_payload(payload)

            for chunk in chunks:
                success = await send_with_retry(chunk)

                if not success:
                    logging.error("Message dropped after retries")

        except Exception as e:
            logging.exception(f"Worker error: {e}")

        finally:
            queue.task_done()