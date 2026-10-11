import base64
import io
import os

import discord
from PIL import Image, ImageOps
import requests

TOKEN = os.getenv("DISCORD_TOKEN", "NO_TOKEN")
WA_API_SERVER = os.getenv("WA_API_SERVER", "localhost:8080")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def process_image_to_base64(image_bytes: bytes) -> str:
    with Image.open(io.BytesIO(image_bytes)) as img:
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        if max(img.width, img.height) > 1280:
            img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)

        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG", optimize=True)
        return base64.b64encode(output_buffer.getvalue()).decode("utf-8")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    
    images = []
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                try:
                    image_bytes = await attachment.read()
                    images.append(process_image_to_base64(image_bytes))
                except Exception as e:
                    print(f"[Error] Failed to process attachment image: {e}")
    
    reply_message = None
    if message.reference and message.reference.resolved:
        resolved = message.reference.resolved
        if isinstance(resolved, discord.Message):
            reply_images = []
            if resolved.attachments:
                for orig_attach in resolved.attachments:
                    if orig_attach.content_type and orig_attach.content_type.startswith("image/"):
                        try:
                            image_bytes = await orig_attach.read()
                            reply_images.append(process_image_to_base64(image_bytes))
                        except Exception as e:
                            print(f"[Error] Failed to process reply original image: {e}")
            
            orig_content = resolved.content
            if not orig_content and resolved.attachments:
                if reply_images:
                    orig_content = "📎 [사진 첨부됨]"
                else:
                    orig_content = "📎 [첨부파일]"
                    
            reply_message = {
                "msg": orig_content,
                "sender": resolved.author.name,
                "images": reply_images
            }
            
    messageList = sendWaMessage(message.content, str(message.channel.id), str(message.author.id), images, reply_message)

    if len(messageList) > 0:
        if messageList[0]:
            await message.reply(messageList[1], mention_author=True)
        else:
            for messageItem in messageList[1]:
                await message.reply(messageItem, mention_author=True)


def sendWaMessage(messageContent, messageChannel, messageAuthor, images=None, replyMessage=None):
    requestData = {
        "msg": messageContent,
        "room": messageChannel,
        "sender": messageAuthor,
        "images": images or []
    }
    if replyMessage:
        requestData["replyMessage"] = replyMessage
    resultData = requests.post(f"{WA_API_SERVER}/getMessage", json=requestData).json()

    resultMessage = resultData["DATA"]["msg"]

    if resultData["RESULT"]["RESULT_CODE"] == 0:
        if resultMessage.find("\\m") > 0:
            resultMessageList = resultMessage.split("\\m")
            return [0, resultMessageList]                
        else:
            resultMessage = resultMessage.replace("\\n", "\n")
            return [1, resultMessage]
    return []


def main():
    client.run(TOKEN)


if __name__ == "__main__":
    main()
