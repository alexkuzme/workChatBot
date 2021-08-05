#!/usr/bin/python3
# -*- coding: utf-8 -*-

########################################################################
#    author: Alexey.Kuzmenko                                           #
#    file  : teleBot.py (v3)                                           #
########################################################################
# NEW in 3 ver:
# - new methods: setMyCommand, getMyCommand
# - in getMessageData added userId
########################################################################
import requests


# Telegram Bot
class TeleBot:
    def __init__(self, token, proxy):
        self.token = token
        self.URL = "https://api.telegram.org/bot%s/" % token
        self.proxy = proxy
        self.updateId = {}
        self.httpResponseJson = {}
        self.sendMessageId = 0
        self.pinnedMessages = {}

    # Http get method
    def _getHttpRequest(self, method, **args):
        self.httpResponseJson = requests.get(self.URL + method, proxies=self.proxy, params=args).json()

    # Http post method
    def _postHttpRequest(self, method, **args):
        self.httpResponseJson = requests.post(self.URL + method, proxies=self.proxy, data=args).json()

    # Obtain new messages from all chats
    def getUpdates(self):
        self._getHttpRequest('getUpdates', offset=str(self.updateId))
        self._getLastUpdateId()

    # Send message to chat
    def sendMessage(self, chatId, text, notify=False):
        self._postHttpRequest('sendMessage', chat_id=chatId, text=text, disable_notification=notify)
        self._getSendMessageId()

    # Reply to message
    def replyToMessage(self, chatId, messageId, text, notify=False):
        self._postHttpRequest('sendMessage', chat_id=chatId, text=text, reply_to_message_id=messageId,
                              disable_notification=notify)
        self._getSendMessageId()

    # Pin message
    def pinChatMessage(self, chatId, messageId):
        self._postHttpRequest('pinChatMessage', chat_id=chatId, message_id=messageId)
        self.pinnedMessages[chatId] = messageId

    # Unpin chat messages
    def unpinChatMessage(self, chatId, messageId):
        self._postHttpRequest('unpinChatMessage', chat_id=chatId, message_id=messageId)
        del self.pinnedMessages[chatId]

    def setMyCommands(self, commands):
        self._postHttpRequest('setMyCommands', commands=commands)

    def getMyCommands(self):
        self._getHttpRequest('getMyCommands')

    # Unpin all messages
    def unpinAllChatMessages(self, chatId):
        self._postHttpRequest('unpinAllChatMessages', chat_id=chatId)
        self.pinnedMessages.pop(chatId, None)

    # Obtain last update id
    def _getLastUpdateId(self):
        result = self.httpResponseJson['result']
        if result:
            self.updateId = result[-1]['update_id'] + 1

    # Get attachment type
    def _getMessageAttachType(self, messageData):
        attachType = 'Unknown'
        types = ('text', 'animation', 'sticker', 'photo', 'document')
        for type in types:
            if type in messageData:
                attachType = type
                break
        return attachType

    # Get message ID that was sent
    def _getSendMessageId(self):
        if 'result' in self.httpResponseJson:
            self.sendMessageId = self.httpResponseJson['result']['message_id']

    # Obtain message data from update
    def getMessageData(self, update):
        chatType, messageType = self._getMessageTypes(update)
        text = ''
        try:
            userId = update[chatType]['from']['id']
        except KeyError as error:
            userId = 'unknown'
        chatId = update[chatType]['chat']['id']
        messageId = update[chatType]['message_id']
        attachType = self._getMessageAttachType(update[chatType])
        # Only text messages
        if attachType == 'text':
            text = update[chatType]['text']
        return chatId, messageId, chatType, messageType, text, userId

    # Obtain message and channel types
    def _getMessageTypes(self, update):
        if 'channel_post' in update:
            messageType = 'channel_post'
        elif 'message' in update:
            messageType = 'message'
        elif 'reply_to_message' in update:
            messageType = 'reply_to_message'
        chatType = update[messageType]['chat']['type']
        return messageType, chatType
