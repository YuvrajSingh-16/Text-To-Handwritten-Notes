from PIL import Image
from fpdf import FPDF
import sys
import argparse
import cv2
import os
import time

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--font", required=True, help="font")
args = vars(ap.parse_args())

os.makedirs("../Output", exist_ok=True)
os.makedirs("../PDF_Outputs", exist_ok=True)

background = Image.open("../Fonts/myfont/a4.jpg")
SheetWidth = background.width
margin = 115
lineMargin = 115
allowedCharacters = '''ABCDEFGHIJKLMNOPQRSTUVWXYZ 
                        abcdefghijklmnopqrstuvwxyz 
                        #:,.?-!()[]'<>=%^$@_;1234567890 "'''

wordsPerLine = 80
maxLenPerPage = 3349
pageNum = 1

filePath = "../input.txt"
lineGap = 120
writing = args["font"]
FontType = "../Fonts/{}_font/".format(writing)

print("Starting.")

x, y = margin + 20, margin + lineGap

scale_percent = int(
    input("What percent of quality (between 40 to 100) you want in output file? ")
)

if scale_percent < 0 or scale_percent > 100 or scale_percent < 40:
    print("Please enter the quality btw given range!")
    time.sleep(5)
    sys.exit()


def space():
    global x, y

    space = Image.open("../Fonts/myfont/space.png")
    width = space.width
    x += width
    background.paste(space, (x, y))
    del space


def newLine():
    global x, y

    x = margin + 20
    y += margin


def writeAlphabet(path):
    global x, y

    letter = Image.open(path)
    background.paste(letter, (x, y))
    x += letter.width


def check_pageExceed():
    global writing, pageNum, background, x, y, margin, lineGap

    if y >= 3100:
        background.save("../Output/{}_output_{}.png".format(writing, pageNum))
        print("Saved Page: ", pageNum)
        bg = Image.open("../Fonts/myfont/a4.jpg")
        background = bg
        x, y = margin, margin + lineGap
        pageNum += 1


wasDQ = False


def ProcessNwrite(word):
    global x, y, background, pageNum, writing, margin, lineGap, wasDQ

    if x > SheetWidth - wordsPerLine * len(word):
        newLine()

    check_pageExceed()

    path = FontType
    for letter in word:
        if letter in allowedCharacters:
            if letter.isupper():
                path += "upper/{}".format(letter)
            elif letter.islower():
                path += "lower/{}".format(letter)
            elif letter.isnumeric():
                path += "digits/{}".format(letter)
            else:
                path += "symbols/"
                if letter == ",":
                    path += "comma"
                elif letter == ".":
                    path += "fullstop"
                elif letter == "!":
                    path += "exclamation"
                elif letter == "-":
                    path += "hiphen"
                elif letter == "#":
                    path += "hash"
                elif letter == "?":
                    path += "question"
                elif letter == "(":
                    path += "bracketop"
                elif letter == ")":
                    path += "bracketcl"
                elif letter == ":":
                    path += "colon"
                elif letter == ";":
                    path += "semicolon"
                elif letter == "{":
                    path += "Cbracketop"
                elif letter == "}":
                    path += "Cbracketcl"
                elif letter == "[":
                    path += "osb"
                elif letter == "]":
                    path += "csb"
                elif letter == "<":
                    path += "oab"
                elif letter == ">":
                    path += "cab"
                elif letter == "=":
                    path += "equals"
                elif letter == "'":
                    path += "osq"
                elif letter == "%":
                    path += "percent"
                elif letter == "&":
                    path += "empersand"
                elif letter == "$":
                    path += "dollar"
                elif letter == "@":
                    path += "at"
                elif letter == "*":
                    path += "asterisk"
                elif letter == "_":
                    path += "underscore"
                elif letter == "^":
                    path += "cap"
                elif letter == '"' and wasDQ:
                    path += "cdq"
                    wasDQ = False
                elif letter == '"':
                    path += "odq"
                    wasDQ = True
            path += ".png"

            writeAlphabet(path)
            path = FontType
        else:
            writeAlphabet("../Fonts/myfont/space.png")


def writeByLine(data):
    global x, y, background, pageNum, writing

    if data == "":
        newLine
    else:
        data = data.split(" ")
        check_pageExceed()

        for word in data:
            ProcessNwrite(word)
            space()


if __name__ == "__main__":
    try:
        file = open(filePath, "r")
        content = file.read()

        l = len(content)
        content = content.split("\n")

        print("Text Reading Completed.")
        for i in range(len(content)):
            writeByLine(content[i])
            newLine()
        print("Saved Page: ", pageNum)

        background.save("../Output/{}_output_{}.png".format(writing, pageNum))

        ImagesPath = [
            "../Output/{}_output_{}.png".format(writing, page)
            for page in range(1, pageNum + 1)
        ]

        print("Adding lines.")

        for path in ImagesPath:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            x, y = 0, 228

            cv2.line(img, (lineMargin - 20, 0), (lineMargin - 20, 3508), (0, 0, 0), 3)
            cv2.line(img, (x, y), (x + 2480, y), (0, 0, 0), 2)

            while y <= 3349:
                cv2.line(img, (x, y), (x + 2480, y), (0, 0, 0), 2)
                y += lineMargin

            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)

            mimage = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(path, mimage)

        height, width = Image.open(ImagesPath[0]).size
        pdf = FPDF(unit="pt", format=(height, width))

        for i in range(0, pageNum):
            pdf.add_page()
            pdf.image(ImagesPath[i], 0, 0)

        print("Saving the pdf.")
        pdf_name = "../PDF_Outputs/{}_Output.pdf".format(writing)
        pdf.output(pdf_name, "F")

        print("Removing unnecessary files.")
        for path in ImagesPath:
            os.remove(path)

        print("Done.")
        print("Find your output at " + pdf_name + ".")
        time.sleep(5)
    except Exception as E:
        pass
        print(E, "Try again!")
