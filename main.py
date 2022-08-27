import discord
import json
import requests

TOKEN = os.getenv("DISCORD_TOKEN", "NO_TOKEN")
WA_API_SERVER = os.getenv("WA_API_SERVER", "localhost:8080")

client = discord.Client()
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    
    messageList = sendWaMessage(message.content, "Discord Channel", "Discord User")

    if messageList[0]:
        await message.channel.send(messageList[1])
    else:
        for messageItem in messageList[1]:
            await message.channel.send(messageItem)

def sendWaMessage(messageContent, messageChannel, messageAuthor):
    requestData = dict([("msg", messageContent), ("room", messageChannel), ("sender", messageAuthor)])
    resultData = requests.post(f"${WA_API_SERVER}/getMessage", json=requestData).json()

    resultMessage = resultData["DATA"]["msg"]

    if resultData["RESULT"]["RESULT_CODE"] == 0:
        if resultMessage.find("\\m") > 0:
            resultMessageList = resultMessage.split("\\m")
            return [0, resultMessageList]                
        else:
            resultMessage = resultMessage.replace("\\n", "\n")
            return [1, resultMessage]

client.run(TOKEN)