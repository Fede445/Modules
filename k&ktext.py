from .. import loader, utils
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from asyncio.exceptions import TimeoutError


def register(cb):
    cb(KKTextMod())


class KKTextMod(loader.Module):
    """K&K Text by @ktxtBot"""
    strings = {'name': 'K&K Text'}

    async def kktcmd(self, message):
        """Use .kkt <text or reply>."""
        try:
            text = utils.get_args_raw(message)
            reply = await message.get_reply_message()
            chat = "@ktxtBot"
            if not text and not reply:
                await message.edit("<b>No text or reply.</b>")
                return
            if text:
                await message.edit("<b>Just a minute...</b>")
                async with message.client.conversation(chat) as conv:
                    try:
                        response = conv.wait_event(events.NewMessage(
                            incoming=True, from_users=700914652))
                        await message.client.send_message(chat, text)
                        response = await response
                    except YouBlockedUserError:
                        await message.reply("<b>Unblock bot @ktxtBot.</b>")
                        return
                    if not response.text:
                        await message.edit("<The bot replied in a non-text format, try again.</b>")
                        return
                    await message.delete()
                    await message.client.send_message(message.to_id, response.text)
            if reply:
                await message.edit("<b>Just a minute...</b>")
                async with message.client.conversation(chat) as conv:
                    try:
                        response = conv.wait_event(events.NewMessage(
                            incoming=True, from_users=700914652))
                        await message.client.send_message(chat, reply)
                        response = await response
                    except YouBlockedUserError:
                        await message.reply("<b>Unblock bot @ktxtBot.</b>")
                        return
                    if not response.text:
                        await message.edit("<The bot replied in a non-text format, try again.</b>")
                        return
                    await message.delete()
                    await message.client.send_message(message.to_id, response.text)
        except TimeoutError:
            return await message.edit("<b>The timeout time has expired. Either the bot is dead, or the text is too big, and the bot does not respond.</b>")
