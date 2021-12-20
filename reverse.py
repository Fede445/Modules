from .. import loader, utils


@loader.tds
class ReverseMod(loader.Module):
    """Reverse text."""
    strings = {'name': 'Reverse'}

    async def revcmd(self, message):
        """Use .rev <text or replay>."""
        if message.text:
            text = utils.get_args_raw(message)
            reply = await message.get_reply_message()

            if not text and not reply:
                return await message.edit("No text or replay.")

            return await message.edit((text or reply.raw_text)[::-1])
        else:
            return await message.edit("It's not text..")
