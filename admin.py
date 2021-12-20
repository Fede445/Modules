# Admin Tools for Friendly-Telegram UserBot.
# Copyright (C) 2020 @Fl1yd, @AtiksX.
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

import io
import time
from .. import loader, utils, security
from PIL import Image
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError, PhotoCropSizeSmallError
from telethon.tl.types import ChatAdminRights, ChatBannedRights
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditPhotoRequest, DeleteUserHistoryRequest
from telethon.tl.functions.messages import EditChatAdminRequest

# ================== КОНСТАНТЫ ========================

DEMOTE_RIGHTS = ChatAdminRights(post_messages=None,
                                add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None,
                                edit_messages=None)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=None,
                                 send_messages=False,
                                 send_media=False,
                                 send_stickers=False,
                                 send_gifs=False,
                                 send_games=False,
                                 send_inline=False,
                                 embed_links=False)

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

UNBAN_RIGHTS = ChatBannedRights(until_date=None,
                                view_messages=None,
                                send_messages=None,
                                send_media=None,
                                send_stickers=None,
                                send_gifs=None,
                                send_games=None,
                                send_inline=None,
                                embed_links=None)

# =====================================================


@loader.tds
class AdminToolsMod(loader.Module):
    strings = {'name': 'AdminTools',
               'no_reply': '<b>No reply on the picture/sticker.</b>',
               'not_pic': '<b>This is not a picture/sticker</b>',
               'wait': '<b>Just a minute...</b>',
               'pic_so_small': '<b>The picture is too small, try another one.</b>',
               'pic_changed': '<b>The chat picture has been changed.</b>',
               'promote_none': "<b> There's no one to promote. < /b >",
               'who': '<b>Who is this?</b>',
               'not_admin': "<b>I'm not an administrator here.</b>",
               'promoted': '<b>{} promote to administrator.\nRank: {}</b>',
               'wtf_is_it': '<b>What is it?</b>',
               'this_isn`t_a_chat': '<b>This is not a chat.!</b>',
               'demote_none': "<b>There's no one to demote.</b>",
               'demoted': '<b>{} demoted.</b>',
               'pinning': '<b>Pin...</b>',
               'pin_none': '<b>Reply to the message to pin it.</b>',
               'unpinning': '<b>Unpin...</b>',
               'unpin_none': "<b>There's nothing to unpin.</b>",
               'no_rights': '<b>I have no rights.</b>',
               'pinned': '<b>Pinned successfully!</b>',
               'unpinned': '<b>Unpinned successfully!</b>',
               'can`t_kick': "<b>Can't kick a user. < /b >",
               'kicking': '<b>Kicking...</b>',
               'kick_none': "<b>There's no one to kick.. < /b >",
               'kicked': '<b>{} kicked out of the chat.</b>',
               'kicked_for_reason': '<b>{} kicked out of the chat.\nReason: {}.</b>',
               'banning': '<b>Banning...</b>',
               'banned': '<b>{} banned from the chat.</b>',
               'banned_for_reason': '<b>{} banned from the chat.\nReason: {}</b>',
               'ban_none': '<b>No one to ban.</b>',
               'unban_none': "<b>There's no one to unban..</b>",
               'unbanned': '<b>{} unbanned in chat.</b>',
               'mute_none': "<b>There's no one to mute. < /b >",
               'muted': '<b>{} muted </b>',
               'no_args': '<b>Incorrect arguments.</b>',
               'unmute_none': "<b>There's no one to unmute.</b>",
               'unmuted': '<b>{} unmuted.</b>',
               'no_reply': '<b>No reply.</b>',
               'deleting': '<b>Deleting...</b>',
               'no_args_or_reply': '<b>No argument or reply.</b>',
               'deleted': '<b>All messages from {} deleted.</b>',
               'del_u_search': '<b>Search for deleted accounts...</b>',
               'del_u_kicking': '<b>Kick of deleted accounts...\nOh~, can I do that?!</b>'}

    async def ecpcmd(self, message):
        if message.chat:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    pic = await check_media(message, reply)
                    if not pic:
                        return await utils.answer(message, self.strings('not_pic', message))
                else:
                    return await utils.answer(message, self.strings('no_reply', message))

                await utils.answer(message, self.strings('wait', message))

                what = resizepic(pic)
                if what:
                    try:
                        await message.client(EditPhotoRequest(message.chat_id, await message.client.upload_file(what)))
                    except PhotoCropSizeSmallError:
                        return await utils.answer(message, self.strings('pic_so_small', message))
                await utils.answer(message, self.strings('pic_changed', message))
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def promotecmd(self, message):
        """The .promote command promotes the user to administrator.\nUse: .promote <@ or reply> <rank>."""
        if message.chat:
            try:
                args = utils.get_args_raw(message).split(' ')
                reply = await message.get_reply_message()
                rank = 'одмэн'

                chat = await message.get_chat()
                adm_rights = chat.admin_rights
                if not adm_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    args = utils.get_args_raw(message)
                    if args:
                        rank = args
                    else:
                        rank = rank
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if len(args) == 1:
                        rank = rank
                    elif len(args) >= 2:
                        rank = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await message.client(EditAdminRequest(message.chat_id, user.id, ChatAdminRights(add_admins=False, invite_users=adm_rights.invite_users,
                                                                                                    change_info=False, ban_users=adm_rights.ban_users,
                                                                                                    delete_messages=adm_rights.delete_messages, pin_messages=adm_rights.pin_messages), rank))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('promoted', message).format(user.first_name, rank))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def demotecmd(self, message):
        """The .demote command demotes the user to administrator rights.\nUse: .demote <@ or reply>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('demote_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))

                try:
                    if message.is_channel:
                        await message.client(EditAdminRequest(message.chat_id, user.id, DEMOTE_RIGHTS, ""))
                    else:
                        await message.client(EditChatAdminRequest(message.chat_id, user.id, False))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('demoted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args'))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def pincmd(self, message):
        """The .pin command pin the message in the chat.\nUse: .pin <repay>."""
        if not message.is_private:
            reply = await message.get_reply_message()
            if not reply:
                return await utils.answer(message, self.strings('pin_none', message))

            await utils.answer(message, self.strings('pinning', message))
            try:
                await message.client.pin_message(message.chat, message=reply.id, notify=False)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('pinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unpincmd(self, message):
        """The .unpin command unpin a pinned message.\nUse: .unpin."""
        if not message.is_private:
            await utils.answer(message, self.strings('unpinning', message))

            try:
                await message.client.pin_message(message.chat, message=None, notify=None)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('unpinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def kickcmd(self, message):
        """The .kick command kicks the user.\nUse: .kick <@ or reply>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(
                                message).split(' ', 1)[1]

                await utils.answer(message, self.strings('kicking', message))
                try:
                    await message.client.kick_participant(message.chat_id, user.id)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
                if reason:
                    return await utils.answer(message, self.strings('kicked_for_reason', message).format(user.first_name, reason))

                return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def bancmd(self, message):
        """The .ban command ban the user.\nUse: .ban <@ or reply>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(
                                message).split(' ', 1)[1]
                try:
                    await utils.answer(message, self.strings('banning', message))
                    await message.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('banned', message).format(user.first_name))
                if reason:
                    return await utils.answer(message, self.strings('banned_for_reason', message).format(user.first_name, reason))
                return await utils.answer(message, self.strings('banned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unbancmd(self, message):
        """The .unban command unban a user.\nUse: .unban <@ or reply>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unban_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))

                return await utils.answer(message, self.strings('unbanned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def mutecmd(self, message):
        """The .mute command mute a user.\nUse: .mute <@ or reply> <time (1m, 1h, 1d)>."""
        if not message.is_private:
            args = utils.get_args_raw(message).split()
            reply = await message.get_reply_message()
            timee = False

            try:
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        timee = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            timee = False
                        elif len(args) >= 2:
                            timee = utils.get_args_raw(
                                message).split(' ', 1)[1]
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))

            if timee:
                n = ''
                t = ''

                for _ in timee:
                    if _.isdigit():
                        n += _
                    else:
                        t += _

                text = f"<b>{n}"

                if t == "m":
                    n = int(n) * 60
                    text += " мин.</b>"

                elif t == "h":
                    n = int(n) * 3600
                    text += " час.</b>"

                elif t == "d":
                    n = int(n) * 86400
                    text += " дн.</b>"

                else:
                    return await utils.answer(message, self.strings('no_args', message))

                try:
                    tm = ChatBannedRights(
                        until_date=time.time() + int(n), send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await utils.answer(message, self.strings('muted', message).format(user.first_name) + text)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
            else:
                try:
                    tm = ChatBannedRights(until_date=True, send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await message.edit('<b>{} теперь в муте.</b>'.format(user.first_name))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unmutecmd(self, message):
        """The .unmute command unmute a user.\nUse: .unmute <@ or reply>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unmute_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, UNMUTE_RIGHTS))

                return await utils.answer(message, self.strings('unmuted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def delallmsgscmd(self, message):
        """The command .delallmsgs deletes all messages from the user.\nUse: .delallmsgs <@ or reply>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await utils.answer(message, self.strings('no_args_or_reply', message))

        await utils.answer(message, self.strings('deleting', message))

        if args:
            user = await message.client.get_entity(args)
        if reply:
            user = await message.client.get_entity(reply.sender_id)

        await message.client(DeleteUserHistoryRequest(message.to_id, user.id))
        await message.client.send_message(message.to_id, self.strings('deleted', message).format(user.first_name))
        await message.delete()

    async def deluserscmd(self, message):
        """The command .delusers shows a list of all deleted accounts in chat."""
        if message.is_private:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

        con = utils.get_args_raw(message)
        del_u = 0
        del_status = '<b>There are no deleted accounts, the chat has been cleared.</b>'

        if con != "clean":
            await utils.answer(message, self.strings('del_u_search', message))
            async for user in message.client.iter_participants(message.chat_id):
                if user.deleted:
                    del_u += 1
            if del_u == 1:
                del_status = f"<b>Found {del_u} deleted account, clear them with the </b><code>.delusers clean</code><b>.</b>"
            if del_u > 0:
                del_status = f"<b>Found {del_u} deleted accounts, clear them using the </b><code>.delusers clean</code><b>.</b>"
            return await message.edit(del_status)

        chat = await message.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings('not_admin', message))
        else:
            if chat.admin_rights.ban_users == False:
                return await utils.answer(message, self.strings('no_rights', message))

        await utils.answer(message, self.strings('del_u_kicking', message))
        del_u = 0
        del_a = 0
        async for user in message.client.iter_participants(message.chat_id):
            if user.deleted:
                try:
                    await message.client(EditBannedRequest(message.chat_id, user.id, BANNED_RIGHTS))
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await message.client(EditBannedRequest(message.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1
        if del_u == 1:
            del_status = f"<b>Kicked {del_u} deleted account.</b>"
        if del_u > 0:
            del_status = f"<b>Kicked {del_u} deleted accounts.</b>"

        if del_a == 1:
            del_status = f"<b>Kicked {del_u} deleted account.\n" \
                f"{del_a} the deleted admin account is not kicked.</b>"
        if del_a > 0:
            del_status = f"<b>Kicked {del_u} deleted accounts.\n" \
                f"{del_a} deleted admin accounts are not kicked.</b>"
        await message.edit(del_status)


def resizepic(reply):
    im = Image.open(io.BytesIO(reply))
    w, h = im.size
    x = min(w, h)
    x_ = (w-x)//2
    y_ = (h-x)//2
    _x = x_ + x
    _y = y_ + x
    im = im.crop((x_, y_, _x, _y))
    out = io.BytesIO()
    out.name = "outsuder.png"
    im.save(out)
    return out.getvalue()


async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.video:
            data = reply.video
        elif reply.document:
            if reply.gif or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
