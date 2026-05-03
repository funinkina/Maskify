import fontforge

base = fontforge.open(
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_2.ttf"
)

for f in [
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_3.ttf",
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_4.ttf",
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_5.ttf",
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_6.ttf",
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_7.ttf",
    "/home/funinkina/Downloads/fonts_69f79fb426cf9/fonts/UntitledTTF_8.ttf",
]:
    base.mergeFonts(f)

base.generate("merged.ttf")
