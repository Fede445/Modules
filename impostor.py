import io
import requests
from .. import loader, utils
from random import choice, randint
from PIL import Image, ImageDraw, ImageFont


@loader.tds
class ImpMod(loader.Module):
    """Among Us"""
    strings = {'name': 'Impostor?'}

    async def impcmd(self, message):
        """Use: .imp <@ or text or reply."""
        await self.procces_img(message, "en")

    async def procces_img(self, message, way):
        remain = randint(1, 2)
        imps = ['wasn`t the impostor', 'was the impostor']
        text2 = f"\n{remain} impostor(s) remain."

        background = requests.get(
            f"https://fl1yd.ml/modules/stuff/impostor{randint(1,22)}.png").content
        font = requests.get("https://fl1yd.su/modules/stuff/font2.ttf").content

        await message.edit("Just a minute...")
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        try:
            if not args and not reply:
                user = await message.client.get_me()
            else:
                user = await message.client.get_entity(args or reply.sender_id)
            text = f"{user.first_name} {choice(imps)}."
            text += text2
        except:
            text = args

        font = io.BytesIO(font)
        font = ImageFont.truetype(font, 30)
        image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        w, h = draw.multiline_textsize(text=text, font=font)
        image = Image.open(io.BytesIO(background))
        x, y = image.size
        draw = ImageDraw.Draw(image)
        draw.multiline_text(((x - w) // 2, (y - h) // 2),
                            text=text, font=font, fill="white", align="center")
        output = io.BytesIO()
        output.name = "impostor.png"
        image.save(output, "png")
        output.seek(0)
        await message.client.send_file(message.to_id, output, reply_to=reply)
        await message.delete()
