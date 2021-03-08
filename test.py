from PIL import Image, ImageDraw, ImageFont

img=Image.new('RGB', (10*16+24, 10*16+16), 0xC0C0C0)
for row in range(24, 10*16+24, 16):
    for column in range(16, 10*16+16, 16):
        img.paste(Image.open("sprites/hidden.png"), (row, column))
d=ImageDraw.Draw(img)
fnt = ImageFont.truetype('fonts/mine-sweeper.ttf', 10)
d.text((27, 0), " ".join([chr(i+97) for i in range(10)]), font=fnt, fill=0x0)
for i in range(16, 10*16+16, 16):
    d.text((2, i+2), str(int((i-16)/16)+1),font=fnt, fill=0x0)

img.save("image.png")
