import json
import requests
from .. import loader, utils


def register(cb):
    cb(DictionaryMod())


class DictionaryMod(loader.Module):
    """Dictionary."""
    strings = {'name': 'Dictionary'}

    async def meancmd(self, message):
        """Usage: .mean <word>."""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit('<b>No argument..</b>')
        await message.edit('<b>Finding out...</b>')
        lang = 'it'
        r = requests.get(
            f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{args}')
        js = json.loads(r.text)
        df = ''
        try:
            for i in js[0]["meanings"][0]["definitions"]:
                try:
                    df += (f'{i["definition"]} ')
                except:
                    return
        except:
            await message.edit(f'◆ <b>{args}</b> - <i>There is no such word in the dictionary.</i>')
            return
        ex = ''
        count = 0
        mess = (f'<b>{js[0]["word"]}</b>, <i>{js[0]["meanings"][0]["partOfSpeech"]}</i>.\n\n'
                f'◆ <b>Meaning:</b> <i>{df}</i>\n')
        try:
            for i in js[0]["meanings"][0]["definitions"]:
                count += 1
                ex += f'\n<b>{count})</b> <i>{i["example"]}</i>'
                alert = ''.join(ex)
        except:
            await message.edit(mess)
            return
        await message.edit(f'{mess}◆ <b>Examples of uses of the word:</b> {alert}')
