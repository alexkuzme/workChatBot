#!/usr/bin/python3
# -*- coding: utf-8 -*-

########################################################################
#    author: Alexey.Kuzmenko                                           #
#    file  : workChatBot.py (v2)                                       #
########################################################################
# NEW in 2 ver:
# - new commands: get_my_userid, get_bot_placement, get_chats_id, help
########################################################################
from teleBot import TeleBot
import help
import json, os, socket


# SysLogSwitcher Bot
class workChatBot(TeleBot):
    def __init__(self, token, SysLogChatsObject, proxy=set()):
        super(workChatBot, self).__init__(token, proxy)
        self.commands = [{'command': 'help', 'description': 'помощь'},
                         {'command': 'get_chats_states', 'description': 'состояния Alert channel-ов'},
                         {'command': 'get_chats_list', 'description': 'список Alert channel-ов'},
                         {'command': 'get_chats_id', 'description': 'список Alert channel-ов с ID'},
                         {'command': 'get_bot_placement', 'description': 'расположение скрипта с ботом'},
                         {'command': 'get_my_userid', 'description': 'узнать свой userId'}]
        self.actionState = {'START': False, 'END': True}
        self.humanState = lambda state: 'Активен' if state else 'Неактивен'
        self.SysLogChats = SysLogChatsObject
        super(workChatBot, self).setMyCommands(json.dumps(self.commands))

    # Handle WA or / messages
    def handleMessage(self, chat_id, message_id, messageType, message, userId):
        pinUnpin = [False, False]
        if message.startswith('/'):
            self.handleCommand(chat_id, message_id, message, userId)
        elif message.startswith('#WA'):
            pinUnpin = self.handleWorkMessage(chat_id, message_id, message)
        return pinUnpin

    # Handle command /
    def handleCommand(self, chat_id, message_id, command, userId):
        if command == '/help' or command == '/help@t2_cloud_bot':
            self.replyToMessage(chat_id, message_id, help.helpMessage)
        elif command == '/get_chats_states' or command == '/get_chats_states@t2_cloud_bot':
            chatsStates = '\n'.join(self.SysLogChats.getChatsStatesPrintout())
            self.replyToMessage(chat_id, message_id, chatsStates)
        elif command == '/get_chats_list' or command == '/get_chats_list@t2_cloud_bot':
            chList = ', '.join(list(self.SysLogChats.chatsList))
            self.replyToMessage(chat_id, message_id, chList)
        elif command == '/get_chats_id' or command == '/get_chats_id@t2_cloud_bot':
            chatsId = '\n'.join(self.SysLogChats.getChatsIDPrintout())
            self.replyToMessage(chat_id, message_id, chatsId)
        elif command == '/get_bot_placement' or command == '/get_bot_placement@t2_cloud_bot':
            scriptPath = 'path : ' + os.getcwd()
            hostName = 'hostname : ' + socket.gethostname()
            self.replyToMessage(chat_id, message_id, hostName + '\n' + scriptPath)
        elif command == '/get_my_userid' or command == '/get_my_userid@t2_cloud_bot':
            self.replyToMessage(chat_id, message_id, 'Ваш userId - "%s"' % userId)
        else:
            self.replyToMessage(chat_id, message_id,
                                'Неподдержваемая комнда. Список доступных комманд можно посмотреть введя "/"')

    # Check PW Header
    def checkPWHeader(self, message):
        errorMessage = ''
        pw = ''; action = ''; region = '';
        try:
            pw, action, region = message.split()[:3]
        except ValueError as error1:
            errorMessage = 'Ошибка заголовка, требуется три параметра с хэштэгом.'
        else:
            pw = pw.upper(); region = region.upper(); action = action.upper();
            if pw[0] != '#' or action[0] != '#' or region[0] != '#':
                errorMessage = 'Ошибка заголовка, необходим хэштэг после каждого параметра.'
            elif len(pw[1:]) != 10 or pw[1:].startswith('PW'):
                errorMessage = 'Ошибка заголовка, недопустимый номер работ "%s".' % pw[1:]
            elif action[1:] not in self.actionState.keys():
                errorMessage = 'Ошибка заголовка, недопустимое действие "%s".' % action[1:]
            elif region[1:] not in self.SysLogChats.chatsList:
                errorMessage = 'Ошибка заголовка, недопустимый регион "%s".' % region[1:]
        return pw, action, region, errorMessage

    # Handle work messages
    def handleWorkMessage(self, chat_id, message_id, message):
        pinUnpin = [False, False]
        pw, action, region, errorMessage = self.checkPWHeader(message)
        if errorMessage != '':
            self.replyToMessage(chat_id, message_id, errorMessage)
        else:
            prevChatState = self.SysLogChats.chatObjects[region[1:]].chatState
            self.SysLogChats.setChatState(region[1:], self.actionState[action[1:]], pw[1:])
            curChatState = self.SysLogChats.chatObjects[region[1:]].chatState
            listPW = ','.join(list(self.SysLogChats.chatObjects[region[1:]].activePW))
            if prevChatState != curChatState:
                self.replyToMessage(chat_id, message_id, '%s Alert Channel состояние "%s" причина "%s"' %
                                    (region[1:], self.humanState(curChatState), listPW))
                if action[1:] == 'START':
                    pinUnpin = [True, False]
                else:
                    pinUnpin = [False, True]
            else:
                if pw[1:] not in listPW:
                    self.SysLogChats.setChatState(region[1:], self.actionState[action[1:]], pw[1:])
                self.replyToMessage(chat_id, message_id, '%s Alert Channel канал уже в состоянии "%s"'
                                    % (region[1:], self.humanState(prevChatState)))
        return pinUnpin
