# -*- coding: utf-8 -*-
#
# File: PlominoReplicationManager.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Xavier PERROT <xavier.perrot@makina-corpus.com>"""
__docformat__ = 'plaintext'

from Persistence import Persistent
from Products.CMFPlomino.config import *

from Products.CMFPlomino.exceptions import PlominoReplicationException
try:
    from Products.ZpCron.crontab import CronTab
    from Products.ZpCron.Product import ZpCron
except:
    pass
import StringIO

class PlominoScheduler(Persistent):
    """Plomino scheduler features
    """
    security = ClassSecurityInfo()


    security.declarePrivate('managePlominoCronTab')
    def managePlominoCronTab(self, onDelete = False):
        """
        delete / set the cron configuration for 
        - agents
        - base replication
        """

        #ZpCron installed
        try:
            cronObj = self.Control_Panel.ZpCron
        except:
            cronObj = None

        if (cronObj):
            #buid hashmap
            tabCron = self.parseCronTab(cronObj)

            #base url
            baseUrl = self.absolute_url(1)

            #del commands for currrent base
            newTabCron = {}
            for cmd in tabCron:
                if not(baseUrl in cmd):
                    newTabCron[cmd] = tabCron[cmd]

            #rebuild base agents commands
            for agent in self.getAgents():
                if (agent.getScheduled()) and not(onDelete and agent.id == self.id):
                    userAgent = self.acl_users.absolute_url(1) + ':' + agent.getAgentUser()
                    if not userAgent.startswith('/'):
                        userAgent = '/' + userAgent
                    newTabCron[agent.absolute_url(1) + '/runAgent'] = {'user':userAgent,'cron':agent.getCron(),}

            #rebuild replication commands
            replications = self.getReplications()
            for replicationId in replications:
                replication = self.getReplication(replicationId)
                if replication['scheduled']:
                    username = self.acl_users.absolute_url(1) + ':' + replication['username']
                    if not username.startswith('/'):
                        username = '/' + username
                    newTabCron[baseUrl + '/replicate?replicationId='+replicationId] = {'user':username,'cron':replication['cron'],}

            #write file
            fileContent = ''
            for cmd in newTabCron:
                if cmd.startswith('/'):
                    command = cmd
                else:
                    command = '/' + cmd
                fileContent = fileContent + 'USER='+newTabCron[cmd]['user'] + '\n'
                fileContent = fileContent + newTabCron[cmd]['cron'] + ' ' + command + '\n'

            #save file
            self.Control_Panel.ZpCron.crontab = fileContent
            self.Control_Panel.ZpCron.update()

    security.declarePrivate('parseCronTab')
    def parseCronTab(self,cronObj):
        """
        buid a hashmap representing file
        key : action url (command)
        value : date, user, cron, params
        """
        #initialization
        res = {}
        currentUser = ''

        #file content
        crontab = cronObj.crontab

        #lines
        for line in crontab.split('\n'):
            #strip spaces
            line = line.strip()
            #no line
            if (not line):
                continue
            #empty line
            elif (line == '') or (len(line) == 0):
                continue
            #comments
            elif (line[0] in ('#', ';')):
                continue
            #@ line -> not managed
            elif (line[0] == '@'):
                continue
            # first caract is letter
            elif line[0].isalpha():
                var, user = line.split('=', 1)
                var = var.strip()
                user = user.strip()
                if user:
                    if user.startswith('"') and user.endswith('"'):
                        user = user[1:-1]
                    currentUser = user
            # first caract is * or num -> cron line
            elif line[0].isdigit() or line[0]=='*':
                line = line.split(None, 5)
                #user
                res[line[5]]={'user':currentUser,
                              'cron':' '.join(line[:5]),}
        return res
