import requests
import io
from .. import loader, utils


@loader.tds
class HiddenUrlMod(loader.Module):
    """Hides the link under the invisible text."""
    strings = {'name': 'HiddenUrl'}

    async def hidecmd(self, message):
        """Use .hide <url> <text or reply on media."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args or reply:
            if reply:
                if reply.media:
                    file = io.BytesIO(await message.client.download_file(reply.media))
                    file.name = reply.file.name if reply.file.name else reply.file.id + reply.file.ext
                    try:
                        x0at = requests.post(
                            'https://x0.at', files={'file': file})
                    except ConnectionError as e:
                        return await message.edit(str(e))
                    await message.client.send_message(message.to_id, f'{args} <a href="{x0at.text}">\u2060</a>')
                else:
                    return await message.edit("This is not a media.")
            else:
                try:
                    await message.client.send_message(message.to_id, f"{args.split(' ', 1)[1]} <a href=\"{args.split()[0]}\">\u2060</a>")
                except:
                    await message.client.send_message(message.to_id, f'<a href="{args}">\u2060</a>')
            await message.delete()
        else:
            return await message.edit("No argument or reply on the media.")
