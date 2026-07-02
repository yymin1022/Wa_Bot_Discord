import base64
import discord
import os
import requests

TOKEN = os.getenv("DISCORD_TOKEN", "NO_TOKEN")
WA_API_SERVER = os.getenv("WA_API_SERVER", "localhost:8080")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    
    image_base64 = None
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.content_type and attachment.content_type.startswith("image/"):
            image_bytes = await attachment.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    messageList = sendWaMessage(message.content, str(message.channel.id), str(message.author.id), image_base64)

    if len(messageList) > 0:
        if messageList[0]:
            await message.channel.send(messageList[1])
        else:
            for messageItem in messageList[1]:
                await message.channel.send(messageItem)


def sendWaMessage(messageContent, messageChannel, messageAuthor, imageBase64=None):
    requestData = dict([("msg", messageContent), ("room", messageChannel), ("sender", messageAuthor)])
    if imageBase64:
        requestData["image"] = imageBase64
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
