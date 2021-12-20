import os
from .. import loader, utils
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest


@loader.tds
class WhoIsMod(loader.Module):
    """Gets information about the user."""
    strings = {'name': 'WhoIs'}

    async def whoiscmd(self, message):
        """Use .whois <@ or replay>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        await message.edit("<b>Getting information about the user...</b>")

        try:
            if args:
                user = await message.client.get_entity(args if not args.isgidit() else int(args))
            else:
                user = await message.client.get_entity(reply.sender_id)
        except:
            user = await message.client.get_me()

        user = await message.client(GetFullUserRequest(user.id))
        photo, caption = await get_info(user, message)

        await message.client.send_file(message.chat_id, photo, caption=caption,
                                       link_preview=False, reply_to=reply.id if reply else None)
        os.remove(photo)
        await message.delete()


async def get_info(user, message):
    """Detailed information about the user."""
    uuser = user.user

    user_photos = await message.client(GetUserPhotosRequest(user_id=uuser.id,
                                                            offset=42, max_id=0, limit=100))
    user_photos_count = "User does not have an avatar."
    try:
        user_photos_count = user_photos.count
    except:
        pass

    user_id = uuser.id
    first_name = uuser.first_name or "User did not enter a name."
    last_name = uuser.last_name or "The user did not provide a last name."
    username = "@" + uuser.username or "User has no username."
    user_bio = user.about or "The user has no information about himself."
    common_chat = user.common_chats_count
    is_bot = "Yes" if uuser.bot else "No"
    restricted = "Yes" if uuser.restricted else "No"
    verified = "Yes" if uuser.verified else "No"

    photo = await message.client.download_profile_photo(user_id, str(user_id) + ".jpg", download_big=True)

    caption = (f"<b>USER INFORMATION:</b>\n\n"
               f"<b>Name:</b> {first_name}\n"
               f"<b>Last name:</b> {last_name}\n"
               f"<b>Username:</b> {username}\n"
               f"<b>ID:</b> <code>{user_id}</code>\n"
               f"<b>Bot:</b> {is_bot}\n"
               f"<b>Limited:</b> {restricted}\n"
               f"<b>Verified:</b> {verified}\n\n"
               f"<b>Bio:</b> \n<code>{user_bio}</code>\n\n"
               f"<b>Number of avatars in profile:</b> {user_photos_count}\n"
               f"<b>Common chats:</b> {common_chat}\n"
               f"<b>Permalink:</b> <a href=\"tg://user?id={user_id}\">click</a>")

    return photo, caption
