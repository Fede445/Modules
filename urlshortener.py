import os
from .. import loader, utils


def register(cb):
    cb(URLShortenerMod())


class URLShortenerMod(loader.Module):
    """Link Cutter"""
    strings = {'name': 'URLShortener'}

    async def lgtcmd(self, message):
        """Reduce the link with the verylegit.link service"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("No argument..")
        link = os.popen(
            f"curl verylegit.link/sketchify -d long_url={args}").read()
        await message.edit(f"Link:\n> {link}")
