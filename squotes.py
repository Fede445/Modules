# API/Module authors: @Fl1yd, @spypm
# Thank for.... - no1!!, no1 helped us, we did everything ourselves
# But we took one method of get messages from the Mishase's and Droox's modules

# ладно


import io
import json
import base64
import requests
import telethon

from telethon.tl import types
from telethon.tl.patched import Message

from typing import List
from time import gmtime

from .. import loader, utils


def get_message_media(message: Message):
    data = None
    if message and message.media:
        data = message.photo or message.sticker or message.video or message.video_note or message.gif or message.web_preview
    return data


def get_entities(entities: types.TypeMessageEntity):
    # coded by @droox
    r = []
    if entities:
        for entity in entities:
            entity = entity.to_dict()
            entity["type"] = entity.pop("_").replace(
                "MessageEntity", "").lower()
            r.append(entity)
    return r


def get_message_text(message: Message, reply: bool = False):
    return (
        "📷 Photo"
        if message.photo and reply
        else message.file.emoji + " Sticker"
        if message.sticker and reply
        else "📹 Video message"
        if message.video_note and reply
        else "📹 Video"
        if message.video and reply
        else "🖼 GIF"
        if message.gif and reply
        else "📊 Poll"
        if message.poll
        else "📍 Location"
        if message.geo
        else "👤 Contact"
        if message.contact
        else f"🎵 Voice message: {strftime(message.voice.attributes[0].duration)}"
        if message.voice
        else f"🎧 Music: {strftime(message.audio.attributes[0].duration)} | {message.audio.attributes[0].performer} - {message.audio.attributes[0].title}"
        if message.audio
        else f"💾 File: {message.file.name}"
        if type(message.media) == types.MessageMediaDocument and not get_message_media(message)
        else f"{message.media.emoticon} Dice: {message.media.value}"
        if type(message.media) == types.MessageMediaDice
        else f"Service message: {message.action.to_dict()['_']}"
        if type(message) == types.MessageService
        else ""
    )


def strftime(time: int):
    t = gmtime(time)
    return (
        (
            f"{t.tm_hour:02d}:"
            if t.tm_hour > 0
            else ""
        ) + f"{t.tm_min:02d}:{t.tm_sec:02d}"
    )


@loader.tds
class ShitQuotesMod(loader.Module):
    """
    Quotes by @sh1tchannel
    """

    strings = {
        "name": "SQuotes",
        "no_reply": "<b>[SQuotes]</b> No Replay",
        "processing": "<b>[SQuotes]</b> Processing...",
        "api_processing": "<b>[SQuotes]</b> Waiting API...",
        "api_error": "<b>[SQuotes]</b> Error API",
        "loading_media": "<b>[SQuotes]</b> Sending...",
        "no_args_or_reply": "<b>[SQuotes]</b> No argument or replay",
        "args_error": "<b>[SQuotes]</b> An error occurred while processing the arguments. The query was: <code>{}</code>",
        "too_many_messages": "<b>[SQuotes]</b> Too many messages. Maximum: <code>{}</code>"
    }

    async def client_ready(self, client: telethon.TelegramClient, db: dict):
        self.client = client
        self.db = db
        self.api_endpoint = "https://quotes.fl1yd.su/generate"
        self.settings = self.get_settings()

    async def qcmd(self, message: types.Message):
        """
        Abbreviation of the .sq command
        """

        return await self.sqcmd(message)

    async def sqcmd(self, message: Message):
        """
        Использование:

        • .sq <number of messages> + <reply> + <!file - drop a file (optional)> + <color (optional))>
        >>> .sq
        >>> .sq 2 #2d2d2d
        >>> .sq red
        >>> .sq !file
        """

        args: List[str] = utils.get_args(message)
        if not await message.get_reply_message():
            return await utils.answer(
                message, self.strings["no_reply"])

        m = await utils.answer(
            message, self.strings["processing"])

        isFile = "!file" in args
        [count] = [int(arg)
                   for arg in args if arg.isdigit() and int(arg) > 0] or [1]
        [bg_color] = [arg for arg in args if arg != "!file" and not arg.isdigit()] or [
            self.settings["bg_color"]]

        if count > self.settings["max_messages"]:
            return await utils.answer(
                m, self.strings["too_many_messages"].format(
                    self.settings["max_messages"])
            )

        payload = {
            "messages": await self.quote_parse_messages(message, count),
            "quote_color": bg_color,
            "text_color": self.settings["text_color"]
        }

        if self.settings["debug"]:
            file = open("SQuotesDebug.json", "w")
            json.dump(
                payload, file, indent=4,
                ensure_ascii=False,
            )
            await message.respond(
                file=file.name)

        await utils.answer(
            m, self.strings["api_processing"])

        r = await self._api_request(payload)
        if r.status_code != 200:
            return await utils.answer(
                m, self.strings["api_error"])

        quote = io.BytesIO(r.content)
        quote.name = "SQuote" + (".png" if isFile else ".webp")
        await utils.answer(
            m, quote, force_document=isFile)
        return await m[-1].delete()

    async def quote_parse_messages(self, message: Message, count: int):
        payloads = []
        messages = [
            msg async for msg in self.client.iter_messages(
                message.chat_id, count, reverse=True, add_offset=1,
                offset_id=(await message.get_reply_message()).id,
            )
        ]

        for message in messages:
            avatar = rank = reply_id = reply_name = reply_text = None
            entities = get_entities(message.entities)

            if message.fwd_from:
                if message.fwd_from.from_id:
                    if type(message.fwd_from.from_id) == types.PeerChannel:
                        user_id = message.fwd_from.from_id.channel_id
                    else:
                        user_id = message.fwd_from.from_id.user_id
                    try:
                        user = await self.client.get_entity(user_id)
                    except Exception:
                        name, avatar = await self.get_profile_data(message.sender)
                        return (
                            "Oh shit, there was an error. Maybe you were banned from this channel and you can't get information.",
                            None, message.sender.id, name, avatar, "error :(", None, None, None, None
                        )
                    name, avatar = await self.get_profile_data(user)
                    user_id = user.id

                elif name := message.fwd_from.from_name:
                    user_id = message.chat_id
            else:
                if reply := await message.get_reply_message():
                    reply_id = reply.sender.id
                    reply_name = telethon.utils.get_display_name(reply.sender)
                    reply_text = get_message_text(reply, True) + (
                        ". " + reply.raw_text
                        if reply.raw_text and get_message_text(reply, True)
                        else reply.raw_text or ""
                    )

                user = await self.client.get_entity(message.sender)
                name, avatar = await self.get_profile_data(user)
                user_id = user.id

                if message.is_group and message.is_channel:
                    admins = await self.client.get_participants(message.chat_id, filter=types.ChannelParticipantsAdmins)
                    if user in admins:
                        admin = admins[admins.index(user)].participant
                        rank = admin.rank or ("creator" if type(
                            admin) == types.ChannelParticipantCreator else "admin")

            media = await self.client.download_media(get_message_media(message), bytes, thumb=-1)
            media = base64.b64encode(media).decode() if media else None

            via_bot = message.via_bot.username if message.via_bot else None
            text = (
                (message.raw_text or "") + (
                    (
                        "\n\n" + get_message_text(message)
                        if message.raw_text
                        else get_message_text(message)
                    )
                    if get_message_text(message)
                    else ""
                )
            )

            payloads.append(
                {
                    "text": text,
                    "media": media,
                    "entities": entities,
                    "author": {
                        "id": user_id,
                        "name": name,
                        "avatar": avatar,
                        "rank": rank or "",
                        "via_bot": via_bot
                    },
                    "reply": {
                        "id": reply_id,
                        "name": reply_name,
                        "text": reply_text
                    }
                }
            )

        return payloads

    async def fsqcmd(self, message: Message):
        """
        Using:

        • .fsq <@ or ID> + <text> - quota from user with @ or ID + specified text
        >>> .fsq @onetimeusername You're fucked.

        • .fsq <Replay> + <text> - quota from user with replay + specified text
        >>> .fsq I'm a sucker.

        • .fsq <@ or ID> + <text> + -r + <@ or ID> + <text> - quota with fake Replay
        >>> .fsq @Fl1yd Thanks -r @onetimeusername You're cool.

        • .fsq <@ or ID> + <text> + -r + <@ or ID> + <text>; <arguments> - quota with fake multi messages
        >>> .fsq @onetimeusername The guys from @sh1tchannel, Wait for the award for the fucking botnet; @elonmuskplssuckmybigdick What; @Fl1yd OUR BOTNET IS THE BEST -r @elonmuskplssuckmybigdick What
        """

        args: str = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not (args or reply):
            return await utils.answer(
                message, self.strings["no_args_or_reply"])

        m = await utils.answer(
            message, self.strings["processing"])
        try:
            payload = await self.fakequote_parse_messages(args, reply)
        except (IndexError, ValueError):
            return await utils.answer(
                m, self.strings["args_error"].format(
                    message.text)
            )

        if len(payload) > self.settings["max_messages"]:
            return await utils.answer(
                m, self.strings["too_many_messages"].format(
                    self.settings["max_messages"])
            )

        payload = {
            "messages": payload,
            "quote_color": self.settings["bg_color"],
            "text_color": self.settings["text_color"]
        }

        if self.settings["debug"]:
            file = open("SQuotesDebug.json", "w")
            json.dump(
                payload, file, indent=4,
                ensure_ascii=False,
            )
            await message.respond(
                file=file.name)

        await utils.answer(
            m, self.strings["api_processing"])

        r = await self._api_request(payload)
        if r.status_code != 200:
            return await utils.answer(
                m, self.strings["api_error"])

        quote = io.BytesIO(r.content)
        quote.name = "SQuote.webp"
        await utils.answer(
            m, quote)
        return await m[-1].delete()

    async def fakequote_parse_messages(self, args: str, reply: Message):
        async def get_user(args: str):
            args_, text = args.split(), ""
            user = await self.client.get_entity(
                int(args_[0]) if args_[0].isdigit() else args_[0])

            if len(args_) < 2:
                user = await self.client.get_entity(
                    int(args) if args.isdigit() else args)
            else:
                text = args.split(maxsplit=1)[1]
            return user, text

        if reply or reply and args:
            user = reply.sender
            name, avatar = await self.get_profile_data(user)
            text = args or ""

        else:
            messages = []
            for part in args.split("; "):
                user, text = await get_user(part)
                name, avatar = await self.get_profile_data(user)
                reply_id = reply_name = reply_text = None

                if " -r " in part:
                    user, text = await get_user(''.join(part.split(" -r ")[0]))
                    user2, text2 = await get_user(''.join(part.split(" -r ")[1]))

                    name, avatar = await self.get_profile_data(user)
                    name2, _ = await self.get_profile_data(user2)

                    reply_id = user2.id
                    reply_name = name2
                    reply_text = text2

                messages.append(
                    {
                        "text": text,
                        "media": None,
                        "entities": None,
                        "author": {
                            "id": user.id,
                            "name": name,
                            "avatar": avatar,
                            "rank": ""
                        },
                        "reply": {
                            "id": reply_id,
                            "name": reply_name,
                            "text": reply_text
                        }
                    }
                )
            return messages

        return [
            {
                "text": text,
                "media": None,
                "entities": None,
                "author": {
                    "id": user.id,
                    "name": name,
                    "avatar": avatar,
                    "rank": ""
                },
                "reply": {
                    "id": None,
                    "name": None,
                    "text": None
                }
            }
        ]

    async def get_profile_data(self, user: types.User):
        avatar = await self.client.download_profile_photo(user.id, bytes)
        return telethon.utils.get_display_name(user), \
            base64.b64encode(avatar).decode() if avatar else None

    async def sqsetcmd(self, message: Message):
        """
        Using:

        • .sqset <bg_color/text_color/debug> (<цвет для bg_color/text_color> <True/False for debug>)
        >>> .sqset bg_color #2d2d2d
        >>> .sqset debug true
        """

        args: List[str] = utils.get_args_raw(message).split(maxsplit=1)
        if not args:
            return await utils.answer(
                message,
                f"<b>[SQuotes]</b> Settings:\n\n"
                f"Maximum messages (<code>max_messages</code>): {self.settings['max_messages']}\n"
                f"The color of the quota (<code>bg_color</code>): {self.settings['bg_color']}\n"
                f"Text color (<code>text_color</code>): {self.settings['text_color']}\n"
                f"Debug (<code>debug</code>): {self.settings['debug']}\n\n"
                f"You can set it up with the help of <code>.sqset</code> <parameter> <value> или <code>reset</code>"
            )

        if args[0] == "reset":
            self.get_settings(True)
            return await utils.answer(
                message, "<b>[SQuotes - Settings]</b> The infusions of quotas have been reset")

        if len(args) < 2:
            return await utils.answer(
                message, "<b>[SQuotes - Settings]</b> Not enough arguments")

        mods = ["max_messages", "bg_color", "text_color", "debug"]
        if args[0] not in mods:
            return await utils.answer(
                message, f"<b>[SQuotes - Settings]</b> There is no such parameter, there is {', '.join(mods)}")

        elif args[0] == "debug":
            if args[1].lower() not in ["true", "false"]:
                return await utils.answer(
                    message, "<b>[SQuotes - Settings]</b> There is no such parameter value, there is true/false")
            self.settings[args[0]] = args[1].lower() == "true"

        elif args[0] == "max_messages":
            if not args[1].isdigit():
                return await utils.answer(
                    message, "<b>[SQuotes - Settings]</b> It's not a number.")
            self.settings[args[0]] = int(args[1])

        else:
            self.settings[args[0]] = args[1]

        self.db.set("SQuotes", "settings", self.settings)
        return await utils.answer(
            message, f"<b>[SQuotes - Settings]</b> Parameter value {args[0]} has been exposed to {args[1]}")

    def get_settings(self, force: bool = False):
        settings: dict = self.db.get(
            "SQuotes", "settings", {}
        )
        if not settings or force:
            settings.update(
                {
                    "max_messages": 15,
                    "bg_color": "#162330",
                    "text_color": "#fff",
                    "debug": False
                }
            )
            self.db.set("SQuotes", "settings", settings)

        return settings

    async def _api_request(self, data: dict):
        return await utils.run_sync(
            requests.post, self.api_endpoint, json=data)
