import html


def safe(text: str) -> str:
    return html.escape(text or "")


def parse_message(payload: dict):
    sender = payload.get("senderData", {})
    message = payload.get("messageData", {})

    sender_name = html.escape(sender.get("senderName", "Unknown"))
    chat_name = html.escape(sender.get("chatName", "Unknown"))

    msg_type = message.get("typeMessage")

    # === TEXT ===
    if msg_type == "textMessage":
        text = message.get("textMessageData", {}).get("textMessage", "")
        text = html.escape(text)

        return {
            "type": "text",
            "text": (
                f"👤 <b>{sender_name}</b>\n"
                f"💬 <i>{chat_name}</i>\n\n"
                f"📩 <pre>{text}</pre>"
            )
        }

    # === IMAGE ===
    if msg_type == "imageMessage":
        file_data = message.get("fileMessageData", {})

        caption = html.escape(file_data.get("caption", ""))
        url = file_data.get("downloadUrl")

        text = (
            f"👤 <b>{sender_name}</b>\n"
            f"💬 <i>{chat_name}</i>\n\n"
            f"🖼 Фото\n"
        )

        if caption:
            text += f"\n💬 <i>{caption}</i>"

        return {
            "type": "photo",
            "text": text,
            "url": url
        }

    # === VIDEO ===
    if msg_type == "videoMessage":
        file_data = message.get("fileMessageData", {})

        caption = html.escape(file_data.get("caption", ""))
        url = file_data.get("downloadUrl")

        text = (
            f"👤 <b>{sender_name}</b>\n"
            f"💬 <i>{chat_name}</i>\n\n"
            f"🎥 Видео\n"
        )

        if caption:
            text += f"\n💬 <i>{caption}</i>"

        return {
            "type": "video",
            "text": text,
            "url": url
        }

    # === UNKNOWN ===
    return {
        "type": "unknown",
        "text": f"⚠️ Unknown message type: {msg_type}"
    }