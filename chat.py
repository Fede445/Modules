# Chat Module for Friendly-Telegram UserBot.
# Copyright (C) 2020 @Fl1yd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ======================================================================

from .. import loader, utils
from os import remove
from telethon.tl.functions.channels import LeaveChannelRequest, InviteToChannelRequest
from telethon.errors import UserIdInvalidError, UserNotMutualContactError, UserPrivacyRestrictedError, BotGroupsBlockedError, ChannelPrivateError, YouBlockedUserError,  MessageTooLongError, \
    UserBlockedError, ChatAdminRequiredError, UserKickedError, InputUserDeactivatedError, ChatWriteForbiddenError, UserAlreadyParticipantError
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantsAdmins, PeerChat, ChannelParticipantsBots
from telethon.tl.functions.messages import AddChatUserRequest


@loader.tds
class ChatMod(loader.Module):
    """Chat module"""
    strings = {'name': 'ChatModule'}

    async def useridcmd(self, message):
        """The command .userid <@ or reply> shows the ID of the selected user."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        try:
            if args:
                user = await message.client.get_entity(args if not args.isdigit() else int(args))
            else:
                user = await message.client.get_entity(reply.sender_id)
        except ValueError:
            user = await message.client.get_entity(message.sender_id)

        await message.edit(f"<b>Name:</b> <code>{user.first_name}</code>\n"
                           f"<b>ID:</b> <code>{user.id}</code>")

    async def chatidcmd(self, message):
        """ The command .chatid shows the chat ID."""
        if not message.is_private:
            args = utils.get_args_raw(message)
            to_chat = None

            try:
                if args:
                    to_chat = args if not args.isdigit() else int(args)
                else:
                    to_chat = message.chat_id

            except ValueError:
                to_chat = message.chat_id

            chat = await message.client.get_entity(to_chat)

            await message.edit(f"<b>Title:</b> <code>{chat.title}</code>\n"
                               f"<b>ID</b>: <code>{chat.id}</code>")
        else:
            return await message.edit("<b>This is not a chat.!</b>")

    async def invitecmd(self, message):
        """Use .invite <@ or reply> to add a user to the chat."""
        if message.is_private:
            return await message.edit("<b>This is not a chat room..!</b>")

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not args and not reply:
            return await message.edit("<b>No argument or reply.</b>")

        try:
            if args:
                user = args if not args.isdigit() else int(args)
            else:
                user = reply.sender_id

            user = await message.client.get_entity(user)

            if not message.is_channel and message.is_group:
                await message.client(AddChatUserRequest(chat_id=message.chat_id,
                                                        user_id=user.id,
                                                        fwd_limit=1000000))
            else:
                await message.client(InviteToChannelRequest(channel=message.chat_id,
                                                            users=[user.id]))
            return await message.edit("<b>User is invited successfully!</b>")

        except ValueError:
            m = "<b>Incorrect @ or ID.</b>"
        except UserIdInvalidError:
            m = "<b>Incorrect @ or ID.</b>"
        except UserPrivacyRestrictedError:
            m = "<b>The user's privacy settings do not allow you to invite him.</b>"
        except UserNotMutualContactError:
            m = "<b>The user's privacy settings do not allow you to invite him.</b>"
        except ChatAdminRequiredError:
            m = "<b>I have no rights.</b>"
        except ChatWriteForbiddenError:
            m = "<b>I have no rights.</b>"
        except ChannelPrivateError:
            m = "<b>I have no rights.</b>"
        except UserKickedError:
            m = "<b>User is kicked out of the chat, contact the administrators.</b>"
        except BotGroupsBlockedError:
            m = "<b>Bot blocked in chat, contact administrators.</b>"
        except UserBlockedError:
            m = "<b>User is blocked in chat, contact administrators.</b>"
        except InputUserDeactivatedError:
            m = "<b>User account deleted.</b>"
        except UserAlreadyParticipantError:
            m = "<b>The user is already in the group.</b>"
        except YouBlockedUserError:
            m = "<b>You have blocked this user.</b>"
        return await message.reply(m)

    async def kickmecmd(self, message):
        """Use the .kickme command to kick yourself from chat."""
        args = utils.get_args_raw(message)
        if not message.is_private:
            if args:
                await message.edit(f"<b>Goodbye.\nПричина: {args}</b>")
            else:
                await message.edit("<b>Goodbye.</b>")
            await message.client(LeaveChannelRequest(message.chat_id))
        else:
            return await message.edit("<b>This is not a chat room.!</b>")

    async def userscmd(self, message):
        """The command .users <name>; nothing lists all users in the chat room."""
        if not message.is_private:
            await message.edit("<b>Counting...</b>")
            args = utils.get_args_raw(message)
            info = await message.client.get_entity(message.chat_id)
            title = info.title or "this chat"

            if not args:
                users = await message.client.get_participants(message.chat_id)
                mentions = f"<b>Users in \"{title}\": {len(users)}</b> \n"
            else:
                users = await message.client.get_participants(message.chat_id, search=f"{args}")
                mentions = f'<b>In "{title}" were found {len(users)} users with the name {args}:</b> \n'

            for user in users:
                if not user.deleted:
                    mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> | <code>{user.id}</code>"
                else:
                    mentions += f"\n• Account deleted <b>|</b> <code>{user.id}</code>"

            try:
                await message.edit(mentions)
            except MessageTooLongError:
                await message.edit("<b>Damn, the chat room is too big. Uploading a list of users to a file...</b>")
                file = open("userslist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "userslist.md",
                                               caption="<b>Users in {}:</b>".format(
                                                   title),
                                               reply_to=message.id)
                remove("userslist.md")
                await message.delete()
        else:
            return await message.edit("<b>This is not a chat room.!</b>")

    async def adminscmd(self, message):
        """The .admins command shows a list of all admins in the chat room."""
        if not message.is_private:
            await message.edit("<b>Counting...</b>")
            info = await message.client.get_entity(message.chat_id)
            title = info.title or "this chat"

            admins = await message.client.get_participants(message.chat_id, filter=ChannelParticipantsAdmins)
            mentions = f"<b>Admins in \"{title}\": {len(admins)}</b>\n"

            for user in admins:
                admin = admins[admins.index((await message.client.get_entity(user.id)))].participant
                if not admin:
                    if type(admin) == ChannelParticipantCreator:
                        rank = "creator"
                    else:
                        rank = "admin"
                else:
                    rank = admin.rank or "admin"

                if not user.deleted:
                    mentions += f"\n• <a href=\"tg://user?id={user.id}\">{user.first_name}</a> | {rank} | <code>{user.id}</code>"
                else:
                    mentions += f"\n• Account deleted <b>|</b> <code>{user.id}</code>"

            try:
                await message.edit(mentions)
            except MessageTooLongError:
                await message.edit("Damn, too many admins here. Uploading a list of admins to the file...")
                file = open("adminlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "adminlist.md",
                                               caption="<b>Admins in \"{}\":<b>".format(
                                                   title),
                                               reply_to=message.id)
                remove("adminlist.md")
                await message.delete()
        else:
            return await message.edit("<b>This is not a chat room.!</b>")

    async def botscmd(self, message):
        """The .bots command shows a list of all bots in the chat room."""
        if not message.is_private:
            await message.edit("<b>Counting...</b>")

            info = await message.client.get_entity(message.chat_id)
            title = info.title if info.title else "this chat"

            bots = await message.client.get_participants(message.to_id, filter=ChannelParticipantsBots)
            mentions = f"<b>Bot in \"{title}\": {len(bots)}</b>\n"

            for user in bots:
                if not user.deleted:
                    mentions += f"\n• <a href=\"tg://user?id={user.id}\">{user.first_name}</a> | <code>{user.id}</code>"
                else:
                    mentions += f"\n• Bot deleted <b>|</b> <code>{user.id}</code>"

            try:
                await message.edit(mentions, parse_mode="html")
            except MessageTooLongError:
                await message.edit("Damn, too many bots here. Uploading a list of bots to the file...")
                file = open("botlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "botlist.md",
                                               caption="<b>Bot in \"{}\":</b>".format(
                                                   title),
                                               reply_to=message.id)
                remove("botlist.md")
                await message.delete()
        else:
            return await message.edit("<b>This is not a chat room.!</b>")
