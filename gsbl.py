import io
import os
from .. import loader
from PIL import Image
from gsbl.stick_bug import StickBug


def register(cb):
    cb(GSBLMod())


class GSBLMod(loader.Module):
    """Fan, meme module."""
    strings = {'name': 'Get-Stick-Bugged-Lol'}

    async def gsblcmd(self, event):
        """Use .gsbl <replug to picture/sticker>."""
        try:
            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("No reply on the picture/sticker.")
            await event.edit("Just a minute...")
            im = io.BytesIO()
            await event.edit("Скачиваю...")
            await event.client.download_file(reply, im)
            await event.edit("Downloading...")
            im = Image.open(im)
            sb = StickBug(im)
            sb.save_video("get_stick_bugged_lol.mp4")
            await event.edit("Sending...")
            await event.client.send_file(event.to_id, open("get_stick_bugged_lol.mp4", "rb"), reply_to=reply)
            os.remove("get_stick_bugged_lol.mp4")
            await event.delete()
        except:
            return await event.edit("This is not a picture/sticker.")
