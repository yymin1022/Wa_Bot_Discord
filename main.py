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
    
    messageList = sendWaMessage(message.content, message.channel.name, message.author.name)

    if messageList[0]:
        await message.channel.send(messageList[1])
    else:
        for messageItem in messageList[1]:
            await message.channel.send(messageItem)

def sendWaMessage(messageContent, messageChannel, messageAuthor):
    requestData = dict([("msg", messageContent), ("room", messageChannel), ("sender", messageAuthor)])
    resultData = requests.post("https://wa-api.defcon.or.kr/getMessage", json=requestData).json()

    resultMessage = resultData["DATA"]["msg"]

    if resultData["RESULT"]["RESULT_CODE"] == 0:
        if resultMessage.find("\\m") > 0:
            return [0, resultMessage]                
        else:
            resultMessage = resultMessage.replace("\\n", "\n")
            return [1, resultMessage]

client.run(TOKEN)