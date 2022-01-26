import discord
import json
import requests

tokenFile = open("/home/server/Wa_Bot_Discord/TOKEN_FILE", "r")
TOKEN = tokenFile.read().rstrip("\n")
tokenFile.close()

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
    
    sendWaMessage(message.content, message.channel, message.author)

def sendWaMessage(messageContent, messageChannel, messageAuthor):
    requestData = dict([("msg", messageContent), ("room", messageChannel.name), ("sender", messageAuthor.name)])
    resultData = requests.post("https://wa-api.defcon.or.kr/getMessage", json=requestData).json()

    resultMessage = resultData["DATA"]["msg"]

    if resultData["RESULT"]["RESULT_CODE"] == 0:
        if resultMessage.find("\\m") > 0:
            resultMessageList = resultMessage.split("\\m")

            for resultMessageItem in resultMessageList:
                messageChannel.send(resultMessageItem)
        else:
            resultMessage = resultMessage.replace("\\n", "\n")
            messageChannel.send(resultMessage)

client.run(TOKEN)