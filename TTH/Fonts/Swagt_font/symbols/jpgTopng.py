import os

for file in enumerate(os.listdir()):
    base = file[1].split(".")
    if base[-1] == "jpg":
        os.rename(file[1], base[0] + ".png")
    print(base)