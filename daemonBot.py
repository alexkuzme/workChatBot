#!/usr/bin/python3
# -*- coding: utf-8 -*-

########################################################################
#    author: Alexey.Kuzmenko                                           #
#    file  : daemonBot.py (v2)                                         #
########################################################################
import workChatBot, sysLogChat
import time


# Handle all updates
def handleUpdate(allUpdates, workChatBot1, alowedChatId):
    for oneUpdate in allUpdates:
        # handling message data from update
        chatId, messageId, chatType, messageType, text, userId = workChatBot1.getMessageData(oneUpdate)
        if chatId == alowedChatId or messageType == 'private':
            print(oneUpdate.__str__())
            pin, unpin = workChatBot1.handleMessage(chatId, messageId, messageType, text, userId)
            # pin message
            if pin:
                response = workChatBot1.httpResponseJson
                if 'result' in response:
                    if chatId in workChatBot1.pinnedMessages:
                        workChatBot1.unpinChatMessage(chatId, workChatBot1.pinnedMessages[chatId])
                    workChatBot1.pinChatMessage(chatId, workChatBot1.sendMessageId)
            # unpin message
            elif not pin and unpin:
                if chatId in workChatBot1.pinnedMessages:
                    workChatBot1.unpinChatMessage(chatId, workChatBot1.pinnedMessages[chatId])


# Main function
def main():
    # Token for @t2_cloud_bot
    botToken = "1537398066:AAHPMB955DX6HcdWcUj4wWaDr24zagyE1wU"
    # T2 Proxy Rostov
    # t2Proxy = {'http': 'http://10.78.10.28:8888',
    #            'https': 'https://10.78.10.28:8888'}
    # t2Proxy = {'http': 'http://10.77.212.44:6539',
    #           'https': 'https://10.77.212.44:6539'}
    # PW chat id now its test
    sourcePWChatId = -1001420624130
    # Period
    period = 2
    sysLogChats1 = sysLogChat.SysLogChats()
    workChatBot1 = workChatBot.workChatBot(botToken, sysLogChats1)
    # if need proxy
    # workChatBot1 = workChatBot.workChatBot(botToken, sysLogChats1, t2Proxy)
    # Unpin all previous messages
    workChatBot1.unpinAllChatMessages(sourcePWChatId)
    while True:
        # Get all available updates
        workChatBot1.getUpdates()
        allUpdates = workChatBot1.httpResponseJson['result']
        print(allUpdates)
        handleUpdate(allUpdates, workChatBot1, sourcePWChatId)
        time.sleep(period)


if __name__ == '__main__':
    main()
