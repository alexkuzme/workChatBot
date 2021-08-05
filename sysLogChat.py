#!/usr/bin/python3
# -*- coding: utf-8 -*-

########################################################################
#    author: Alexey.Kuzmenko                                           #
#    file  : sysLogChat.py (v1)                                        #
########################################################################

# List of SysLog chats
class SysLogChats:
    def __init__(self, chatConfPath='./'):
        self.chatsList = {'NSK': -1001254784660, 'MSK': -1001155063130,
                          'RND': -1001420718299, 'EKB': -1001324363136,
                          'NIN': -1001324760238}
        self.chatObjects = {}
        self.humanState = lambda state: 'Активен' if state else 'Неактивен'
        self.chatConfPath = chatConfPath
        self._createChats()
        self._exportConfig(chatConfPath)

    # Create list of chats object
    def _createChats(self):
        for chatName, ChatId in self.chatsList.items():
            self.chatObjects[chatName] = SysLogChat(chatName, ChatId)

    # Export config
    def _exportConfig(self, chatConfPath):
        with open(chatConfPath + 'chatConfig.txt', 'w') as confFile:
            for chatName in self.chatsList:
                confFile.write(chatName + '\t' + str(self.chatObjects[chatName].chatState) + '\n')

    # Set Chat state
    def setChatState(self, chatName, state, pwName):
        self.chatObjects[chatName].setChatState(state, pwName)
        self._exportConfig(self.chatConfPath)

    # Obtain chat states printout for telegram
    def getChatsStatesPrintout(self):
        chatsStates = []
        for chatName in self.chatsList.keys():
            chatState = self.chatObjects[chatName].chatState
            chatActivePW = ','.join(list(self.chatObjects[chatName].activePW))
            chatsStates.append('%s Alert Channel состояние - "%s" (%s)'
                               % (chatName, self.humanState(chatState), chatActivePW))
        return chatsStates

    # Get chats ID
    def getChatsIDPrintout(self):
        chatsId = []
        for chatName in self.chatsList.keys():
            chatId = str(self.chatObjects[chatName].chatId)
            chatsId.append('%s Alert Channel chatId  "%s"' % (chatName, chatId))
        return chatsId


# Class SysLog chat for
class SysLogChat:
    def __init__(self, chatName, chatId):
        self.chatName = chatName
        self.chatId = chatId
        self.chatState = True
        self.activePW = set()

    # Set notification state
    def setChatState(self, state, pwName):
        if state:
            if not self.chatState:
                self.activePW.remove(pwName)
                if not self.activePW:
                    self.chatState = state
        else:
            self.chatState = state
            self.activePW.add(pwName)
