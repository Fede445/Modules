#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
#    by anon97945

from .. import loader, utils
from telethon.tl.types import (InputMessagesFilterPhotos,
                               InputMessagesFilterVideo,
                               InputMessagesFilterGif,
                               InputMessagesFilterDocument,
                               InputMessagesFilterMusic,
                               InputMessagesFilterRoundVideo,
                               InputMessagesFilterVoice)

import logging
import time
import math
import re

logger = logging.getLogger(__name__)


def register(cb):
    cb(fsumMod())


def weird_division(n, d):
    return n / d if d else 0


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {
        0: "",
        1: "Ki",
        2: "Mi",
        3: "Gi",
        4: "Ti"
    }
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@loader.tds
class fsumMod(loader.Module):
    """Getting a summary of files for given Chat"""
    strings = {"name": "File summary",
               "error": ("\n<b>Invalid chat ID to check for. "
                         + "(Are you Member or is it Private?)</b>")}

    def __init__(self):
        self.name = self.strings["name"]
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def fsumcmd(self, event):
        """Available commands:
           .fsum
             - summary in actual chat
           .fsum
             - as reply to summary replied user
           .fsum <id/username>
            - summary of another chat with id/username"""
        starttime = int(time.monotonic())

        ######################################
        # Choosing the Filters to search for
        ######################################
        filters = [
            InputMessagesFilterPhotos,
            InputMessagesFilterVideo,
            InputMessagesFilterGif,
            InputMessagesFilterDocument,
            InputMessagesFilterMusic,
            InputMessagesFilterRoundVideo,
            InputMessagesFilterVoice
        ]
        ######################
        # Var initialization
        ######################
        filetype = []
        z = []
        filesize = {}
        filecount = {}
        totalcount = totalsize = w = 0
        user_msg = utils.get_args_raw(event)
        ################################
        # Checking for command with id / username
        ################################
        if event.fwd_from:
            return
        elif event.is_reply:
            userid = await event.get_reply_message()
            chatid = userid.sender.id
        if not user_msg and not event.is_reply:
            chatid = event.chat_id
        elif not isinstance(user_msg, int) and represents_int(user_msg):
            chatid = int(user_msg)
        elif not event.is_reply:
            chatid = user_msg
        try:
            await event.client.get_input_entity(chatid)
        except ValueError:
            await utils.answer(event, self.strings("error", event))
            return
        except ZeroDivisionError:
            await utils.answer(event, self.strings("error", event))
            return
        ########################################
        # Define some of the Strings for later
        ########################################
        chat_info = await event.client.get_entity(chatid)
        if type(chat_info).__name__ == "Channel":
            name = chat_info.title
            if chat_info.username:
                link = "<a href='t.me/" + chat_info.username + "'>[Link]</a>"
            else:
                link = ""
        else:
            name = chat_info.first_name
            linkid = str(chat_info.id)
            link = "<a href='tg://user?id=" + linkid + "'>[Link]</a>"
        topline = ("<b>" + name + "</b>\n" + link + "\n<code>File Summary: </code>\n")
        summary = ""
        descline = ("<code>Media       | Count  | File Size  </code>\n")
        line = ("<code>----------------------------------</code>\n")
        pipe = "<code>| </code>"
        await event.edit("<code>Counting files and file size of </code><b>"
                         + name + "</b>")
        ############################################################
        # Loop all Filters to take the String for Types.. Lazy.
        ############################################################
        for type_ in filters:
            z = type_.__name__
            patt = re.compile(r"(\s*)InputMessagesFilter(\s*)")
            filetype += [patt.sub("", z)]
        ####################################
        # Loop through the files
        ####################################
        for x in filters:
            filesize[w] = filecount[w] = 0
            async for message in event.client.iter_messages(entity=chatid,
                                                            limit=None,
                                                            filter=x):
                if message and message.file:
                    filesize[w] += message.file.size
                    filecount[w] += 1
            w += 1
        ######################
        # Calculating totals
        ######################
        totalsize = sum(filesize.values())
        totalcount = sum(filecount.values())
        ###########################
        # Creating summary string
        ###########################
        for y in range(len(filters)):
            filecountalign = ""
            docnamealign = ""
            if filecount[y] <= 0:
                digitsfilecount = int(math.log10(filecount[y] + 1)) + 1
            else:
                digitsfilecount = int(math.log10(filecount[y])) + 1
            if digitsfilecount <= 12:
                for z in range(digitsfilecount, 7):
                    filecountalign += " "
            if len(filetype[y]) <= 12:
                for z in range(len(filetype[y]), 12):
                    docnamealign += " "
            docnamealign = "<code>" + docnamealign + "</code>"
            filecountalign = "<code>" + filecountalign + "</code>"
            summary += ("<code>" + filetype[y] + "</code>" + docnamealign + pipe
                        + "<code>" + str(filecount[y]) + "</code>" + filecountalign + pipe
                        + "<code>" + humanbytes(filesize[y]) + "</code>\n")
        ##############################################
        # Getting the runtime and avg. time per file
        ##############################################
        endtime = int(time.monotonic())
        if endtime - starttime >= 120:
            runtime = str(round(((endtime - starttime) / 60), 2)) + " minutes"
        else:
            runtime = str(endtime - starttime) + " seconds"
        avghubytes = humanbytes(weird_division(totalsize, totalcount))
        avgruntime = (str(round((weird_division((endtime - starttime), totalcount))
                      * 1000, 2)) + " ms")
        #######################
        # Creating total string
        #######################
        totalstring = ("<code>Total files:         | " + str(totalcount)
                       + "\nTotal file size:     | "
                       + humanbytes(totalsize)
                       + "\nAvg. file size:      | "
                       + avghubytes
                       + "\n</code>")
        runtimestring = ("<code>Runtime:             | " + runtime
                         + "\nRuntime per file:    | "
                         + avgruntime + "</code>")
        finalstring = (topline + line + descline + line + summary + line + totalstring
                       + line + runtimestring)
        ##########
        # Finish
        ##########
        await event.edit(str(finalstring))

    async def fsumusercmd(self, event):
        """Available commands:
           .fsumuser
             - as reply to summary replied user
           .fsumuser <id/username>
             - summary of user in chat with id/username"""
        starttime = int(time.monotonic())

        ######################################
        # Choosing the Filters to search for
        ######################################
        filters = [
            InputMessagesFilterPhotos,
            InputMessagesFilterVideo,
            InputMessagesFilterGif,
            InputMessagesFilterDocument,
            InputMessagesFilterMusic,
            InputMessagesFilterRoundVideo,
            InputMessagesFilterVoice
        ]
        ######################
        # Var initialization
        ######################
        filetype = []
        z = []
        filesize = {}
        filecount = {}
        totalcount = totalsize = w = 0
        user_msg = utils.get_args_raw(event)
        ################################
        # Checking for command with id / username
        ################################
        if event.fwd_from:
            return
        elif event.is_reply:
            userid = await event.get_reply_message()
            chatid = event.chat_id
            user_id = userid.sender.id
        if not user_msg and not event.is_reply:
            chatid = event.chat_id
            user_id = ""
        elif not isinstance(user_msg, int) and represents_int(user_msg):
            chatid = int(user_msg)
            user_id = int(user_msg)
        elif not event.is_reply:
            await utils.answer(event, self.strings("error", event))
            return
        try:
            await event.client.get_input_entity(chatid)
        except ValueError:
            await utils.answer(event, self.strings("error", event))
            return
        try:
            await event.client.get_input_entity(user_id)
        except ValueError:
            await utils.answer(event, self.strings("error", event))
            return
        ########################################
        # Define some of the Strings for later
        ########################################
        chat_info = await event.client.get_entity(chatid)
        user_info = await event.client.get_entity(user_id)
        if type(chat_info).__name__ == "Channel":
            name = chat_info.title
            userfname = user_info.first_name
        topline = ("<b>" + name + "</b>\n" + "User: " + userfname + "\n<code>File Summary: </code>\n")
        summary = ""
        descline = ("<code>Media       | Count  | File Size  </code>\n")
        line = ("<code>----------------------------------</code>\n")
        pipe = "<code>| </code>"
        await event.edit("<code>Counting files and file size in </code><b>"
                         + name + "</b><code> of User: </code><b>" + userfname + "</b>")
        ############################################################
        # Loop all Filters to take the String for Types.. Lazy.
        ############################################################
        for type_ in filters:
            z = type_.__name__
            patt = re.compile(r"(\s*)InputMessagesFilter(\s*)")
            filetype += [patt.sub("", z)]
        ####################################
        # Loop through the files
        ####################################
        for x in filters:
            filesize[w] = filecount[w] = 0
            async for message in event.client.iter_messages(entity=chatid,
                                                            limit=None, filter=x):
                if message and message.file:
                    if "id=" in str(message.sender):
                        logger.critical(message.sender)
                        if message.sender.id == user_id:
                            filesize[w] += message.file.size
                            filecount[w] += 1
            w += 1
        ######################
        # Calculating totals
        ######################
        totalsize = sum(filesize.values())
        totalcount = sum(filecount.values())
        ###########################
        # Creating summary string
        ###########################
        for y in range(len(filters)):
            filecountalign = ""
            docnamealign = ""
            if filecount[y] <= 0:
                digitsfilecount = int(math.log10(filecount[y] + 1)) + 1
            else:
                digitsfilecount = int(math.log10(filecount[y])) + 1
            if digitsfilecount <= 12:
                for z in range(digitsfilecount, 7):
                    filecountalign += " "
            if len(filetype[y]) <= 12:
                for z in range(len(filetype[y]), 12):
                    docnamealign += " "
            docnamealign = "<code>" + docnamealign + "</code>"
            filecountalign = "<code>" + filecountalign + "</code>"
            summary += ("<code>" + filetype[y] + "</code>" + docnamealign + pipe
                        + "<code>" + str(filecount[y]) + "</code>" + filecountalign + pipe
                        + "<code>" + humanbytes(filesize[y]) + "</code>\n")
        ##############################################
        # Getting the runtime and avg. time per file
        ##############################################
        endtime = int(time.monotonic())
        if endtime - starttime >= 120:
            runtime = str(round(((endtime - starttime) / 60), 2)) + " minutes"
        else:
            runtime = str(endtime - starttime) + " seconds"
        avghubytes = humanbytes(weird_division(totalsize, totalcount))
        avgruntime = (str(round((weird_division((endtime - starttime), totalcount))
                      * 1000, 2)) + " ms")
        #######################
        # Creating total string
        #######################
        totalstring = ("<code>Total files:         | " + str(totalcount)
                       + "\nTotal file size:     | "
                       + humanbytes(totalsize)
                       + "\nAvg. file size:      | "
                       + avghubytes
                       + "\n</code>")
        runtimestring = ("<code>Runtime:             | " + runtime
                         + "\nRuntime per file:    | "
                         + avgruntime + "</code>")
        finalstring = (topline + line + descline + line + summary + line + totalstring
                       + line + runtimestring)
        ##########
        # Finish
        ##########
        await event.edit(str(finalstring))
