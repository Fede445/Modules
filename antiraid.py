from .. import loader, utils
from telethon.tl.types import ChatBannedRights as cb
from telethon.tl.functions.channels import EditBannedRequest as eb


@loader.tds
class AntiRaidMod(loader.Module):
    strings = {'name': 'AntiRaid'}

    async def client_ready(self, client, db):
        self.db = db

    async def antiraidcmd(self, message):
        """Enable/disable the AntiRaid mode.\nUsage: .antiraid <clearall* (optional)>. * - turns off mode in all chats!"""
        ar = self.db.get("AntiRaid", "ar", [])
        sets = self.db.get("AntiRaid", "sets", {})
        args = utils.get_args_raw(message)

        if args == "clearall":
            self.db.set("AntiRaid", "ar", {})
            self.db.set("AntiRaid", "action", {})
            return await message.edit("<b>[AntiRaid]</b> Mode is off in all group chats.")

        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>I'm not an administrator here.</b>")
            else:
                if chat.admin_rights.ban_users == False:
                    return await message.edit("<b>I don't have the necessary rights.</b>")

            chatid = str(message.chat_id)
            if chatid not in ar:
                ar.append(chatid)
                sets.setdefault(chatid, {})
                sets[chatid].setdefault("stats", 0)
                sets[chatid].setdefault("action", "kick")
                self.db.set("AntiRaid", "ar", ar)
                self.db.set("AntiRaid", "sets", sets)
                return await message.edit("<b>[AntiRaid]</b> Activated in this chat.")

            else:
                ar.remove(chatid)
                sets.pop(chatid)
                self.db.set("AntiRaid", "ar", ar)
                self.db.set("AntiRaid", "sets", sets)
                return await message.edit("<b>[AntiRaid]</b> Deactivated in this chat.")

        else:
            return await message.edit("<b>[AntiRaid]</b> This is not a chat room.")

    async def swatscmd(self, message):
        """The AntiRaid module settings.\nUsage: .swats <kick/ban/mute/clear>."""
        if not message.is_private:
            ar = self.db.get("AntiRaid", "ar", [])
            sets = self.db.get("AntiRaid", "sets", {})
            chatid = str(message.chat_id)
            args = utils.get_args_raw(message)
            if chatid in ar:
                if args:
                    if args == "kick":
                        sets[chatid].update({"action": "kick"})
                    elif args == "ban":
                        sets[chatid].update({"action": "ban"})
                    elif args == "mute":
                        sets[chatid].update({"action": "mute"})
                    elif args == "clear":
                        sets[chatid].pop("stats")
                        self.db.set("AntiRaid", "sets", sets)
                        return await message.edit(f"<b>[AntiRaid - Settings]</b> Chat statistics reset.")
                    else:
                        return await message.edit("<b>[AntiRaid - Settings]</b> This mode is not on the list.\nAvailable modes: kick/ban/mute.")

                    self.db.set("AntiMention", "sets", sets)
                    return await message.edit(f"<b>[AntiRaid - Settings]</b> Now when participants enter, the following action will be performed: {sets[chatid]['action']}.")
                else:
                    return await message.edit(f"<b>[AntiRaid - Settings]</b> Chat settings:\n\n"
                                              f"<b>Mode status:</b> True\n"
                                              f"<b>When participants enter, an action will be performed:</b> {sets[chatid]['action']}\n"
                                              f"<b>Total users:</b> {sets[chatid]['stats']}")
            else:
                return await message.edit("<b>[AntiRaid - Settings]</b> In this chat mode is deactivated.")
        else:
            return await message.edit("<b>[AntiRaid]</b> This is not a chat room..!")

    async def watcher(self, message):
        """aahahahahaa fuck"""
        try:
            ar = self.db.get("AntiRaid", "ar", [])
            sets = self.db.get("AntiRaid", "sets", {})
            chatid = str(message.chat_id)
            if chatid not in ar:
                return

            if message.user_joined or message.user_added:
                user = await message.get_user()
                if sets[chatid]["action"] == "kick":
                    await message.client.kick_participant(int(chatid), user.id)
                elif sets[chatid]["action"] == "ban":
                    await message.client(eb(int(chatid), user.id, cb(until_date=None, view_messages=True)))
                elif sets[chatid]["action"] == "mute":
                    await message.client(eb(int(chatid), user.id, cb(until_date=True, send_messages=True)))
                sets[chatid].update({"stats": sets[chatid]["stats"] + 1})
                return self.db.set("AntiRaid", "sets", sets)
        except:
            pass
