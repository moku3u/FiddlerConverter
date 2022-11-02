from kivy.config import Config
Config.set("graphics", "resizable", False)
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import japanize_kivy

from PIL import Image
from PIL import ImageDraw
import os
import json
import shutil
import urllib.parse


GUI = """
<menu>:
    FloatLayout:
        size_hint: 1, 1
        ScrollView:
            id: TextInputScrollBar
            size_hint: None, None
            size: 580, 480
            pos: 10, 10
            TextInput:
                id: FiddlerSessionInput
                multiline: False
                line_height: 26
                size_hint: None, None
                hint_text: "Fill in your fiddler raw here"
                foreground_color: (1, 1, 1, 0.6)
                background_color: (64/255, 68/255, 75/255, 1)
                height: max(self.minimum_height, TextInputScrollBar.height)
                width: TextInputScrollBar.width
        Button:
            id: ConvertButton
            pos: 700-75, 30
            size_hint: None, None
            size: 150, 50
            text: "Convert"
            background_normal: root.ConvertButtonImage_Normal
            background_down: root.ConvertButtonImage_Down
            on_press: root.ConvertFiddlerSession()
        Label:
            id: LanguageText
            text: "Language"
            pos: 650, 420
        ToggleButton:
            id: LanguageGroup_EN
            group: "LanguageGroup"
            text: "EN"
            size_hint: None, None
            size: 51, 51
            background_normal: root.LanguageButtonImage_right_Normal
            background_down: root.LanguageButtonImage_right_Down
            pos: 700, 400
            state: "down"
            on_release: root.LanguageStateChanged("EN")
        ToggleButton:
            id: LanguageGroup_JA
            group: "LanguageGroup"
            text: "JA"
            size_hint: None, None
            size: 51, 51
            background_normal: root.LanguageButtonImage_left_Normal
            background_down: root.LanguageButtonImage_left_Down
            pos: 650, 400
            on_release: root.LanguageStateChanged("JA")
        Label:
            id: FormatText
            text: "Format"
            pos: 650, 330
        Button:
            id: FormatChanger
            pos: 625, 300
            size_hint: None, None
            size: 150, 50
            text: "py-requests"
            background_normal: ""
            background_color: (55/255, 118/255, 170/255, 1)
            on_press: root.ChangeLanguageFormat()
"""

Builder.load_string(GUI)


os.makedirs(f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP", exist_ok=True)

ConvertButtonImage_Normal = Image.new("RGBA", (150, 50), (0, 0, 0, 0))
draw = ImageDraw.Draw(ConvertButtonImage_Normal)
draw.rounded_rectangle((0, 0, 149, 50), 25, "#8758FF")
ConvertButtonImage_Normal.save(f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\ConvertButtonImage_Normal.png")

ConvertButtonImage_Down = Image.new("RGBA", (150, 50), (0, 0, 0, 0))
draw = ImageDraw.Draw(ConvertButtonImage_Down)
draw.rounded_rectangle((0, 0, 149, 50), 25, "#6a49be")
ConvertButtonImage_Down.save(f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\ConvertButtonImage_Down.png")

def Draw_LanguageButton_left(color, file):
    Baseimage = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(Baseimage)
    draw.rectangle((25, 0, 50, 50), color)
    draw.ellipse((0, 0, 50, 50), color)
    Baseimage.save(file)

def Draw_LanguageButton_right(color, file):
    Baseimage = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(Baseimage)
    draw.rectangle((0, 0, 25, 50), color)
    draw.ellipse((0, 0, 50, 50), color)
    Baseimage.save(file)

Draw_LanguageButton_left("#207428", f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_left_Normal.png")
Draw_LanguageButton_left("#29AA36", f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_left_Down.png")

Draw_LanguageButton_right("#207428", f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_right_Normal.png")
Draw_LanguageButton_right("#29AA36", f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_right_Down.png")

class menu(Widget):
    ConvertButtonImage_Normal = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\ConvertButtonImage_Normal.png"
    ConvertButtonImage_Down = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\ConvertButtonImage_Down.png"
    LanguageButtonImage_left_Normal = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_left_Normal.png"
    LanguageButtonImage_left_Down = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_left_Down.png"
    LanguageButtonImage_right_Normal = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_right_Normal.png"
    LanguageButtonImage_right_Down = f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP\LanguageButtonImage_right_Down.png"

    def ConvertFiddlerSession(self, *args):
        if self.ids.FiddlerSessionInput.text.isspace() or self.ids.FiddlerSessionInput.text == "":
            popup = Popup(title="Error", content=Label(text="No content entered"), size_hint=(None, None), size=(300, 200))
            popup.open()
            return
        parser = FiddlerParser(self.ids.FiddlerSessionInput.text)
        status = parser.Setup()
        if status == "Error": return
        if self.ids.FormatChanger.text == "py-requests":
            code = parser.Parse_Data_request()
        else:
            code = parser.Parse_Data_curl()
        code_preview = ScrollView(size = (670, 390), size_hint=(None, None), )
        text_preview = TextInput(
            foreground_color = (1, 1, 1, 0.6),
            line_height = 20,
            background_color = (47/255, 49/255, 54/255, 1),
            multiline=False,
            size_hint = (None, None),
            readonly=True, text=code,
            width=code_preview.width,
            font_size=10)
        text_preview.height = max(text_preview.minimum_height, code_preview.height)

        code_preview.add_widget(text_preview)

        popup = Popup(title="Result", content=code_preview, size_hint=(None, None), size=(700, 450))
        popup.open()

    
    def LanguageStateChanged(self, selectedlanguage, *args):
        if self.ids.LanguageGroup_JA.state == "normal" and self.ids.LanguageGroup_EN.state == "normal":
            exec(f"self.ids.LanguageGroup_{selectedlanguage}.state = 'down'")
            return
        if selectedlanguage == "JA":
            self.ids.ConvertButton.text = "変換"
            self.ids.FiddlerSessionInput.hint_text = "ここにフィドラーのrawを入力してください"
            self.ids.LanguageText.text = "言語"
        else:
            self.ids.ConvertButton.text = "Convert"
            self.ids.FiddlerSessionInput.hint_text = "Fill in your fiddler raw here"
            self.ids.LanguageText.text = "Language"

    def ChangeLanguageFormat(self, *args):
        if self.ids.FormatChanger.text == "py-requests":
            animation = Animation(background_color = (1/255, 50/255, 80/255, 1), duration = 0.5)
            animation.start(self.ids.FormatChanger)
            self.ids.FormatChanger.text = "curl"
        else:
            animation = Animation(background_color = (55/255, 118/255, 170/255, 1), duration = 0.5)
            animation.start(self.ids.FormatChanger)
            self.ids.FormatChanger.text = "py-requests"

class FiddlerParser():
    def __init__(self, raw):
        self.raw = raw

        self.spaces = 0
        is_exist_payload = False
        for line in reversed(self.raw.splitlines()):
            self.spaces += 1
            try:
                if not line.isspace() or not line == "":
                    json.loads(line)
                    is_exist_payload = True
                    break
            except: None

        if self.spaces >= len(self.raw.splitlines()):
            is_exist_payload = False
            self.spaces = self.spaces - len(self.raw.splitlines())

        self.is_exist = {
            "payload": is_exist_payload,
            "headers": True if len(self.raw.split("\n\n")[0].splitlines()) > 3 else False,
            "params": True if "?" in self.raw.splitlines()[0].split(" ")[1] else False,
            "cookies": False
        }

        if self.is_exist["headers"]:
            if "\nCookie: " in self.raw:
                self.is_exist["cookies"] = True

    def Setup(self):
        self.headers = {}
        self.payload = {}
        self.cookies = {}
        self.params = {}

        self.method = self.raw.splitlines()[0].split(" ")[0]
        self.url = self.raw.splitlines()[0].split(" ")[1]

        if self.method not in ["GET", "POST", "PUT", "DELETE", "OPTIONS"]:
            popup = Popup(title="Error", content=Label(text="unsupported method"), size_hint=(None, None), size=(300, 200))
            popup.open()
            return "Error"

        if self.is_exist["params"]:
            for line in self.raw.splitlines()[0].split(" ")[1].split("?")[-1].split("&"):
                self.params[line.split("=")[0]] = line.split("=")[1]

        self.payload_type = "data"

        if self.is_exist["headers"]:
            try:
                for line in self.raw.splitlines()[1:len(self.raw.splitlines())-self.spaces]:
                    if line.isspace() or line == "": continue
                    if line.split(": ")[0].lower() == "cookie":
                        for key_value in line.split(": ")[1].split("; "):
                            self.cookies[key_value.split("=")[0]] = key_value.split("=")[1]
                    elif line.split(": ")[0].lower() == "content-type":
                        if "application/json" in line.split(": ")[1]:
                            self.payload_type = "json"
                    self.headers[line.split(": ")[0]] = line.split(": ")[1]
            except IndexError:
                popup = Popup(title="Error", content=Label(text="unparseable syntax"), size_hint=(None, None), size=(300, 200))
                popup.open()
                return "Error"

        if self.is_exist["payload"]:
            for line in reversed(self.raw.splitlines()):
                self.spaces += 1
                try:
                    if not line.isspace() or not line == "":
                        self.payload = json.loads(line)
                        break
                except: None

    def Parse_Data_request(self):
        self.headers = json.dumps(self.headers, indent=4, ensure_ascii=False).replace(" false,", " False,").replace(" true,", " True,")
        self.cookies = json.dumps(self.cookies, indent=4, ensure_ascii=False).replace(" false,", " False,").replace(" true,", " True,")
        self.payload = json.dumps(self.payload, indent=4, ensure_ascii=False).replace(" false,", " False,").replace(" true,", " True,")

        config = ""

        if self.is_exist["params"]: config += f"params = {self.params}\n\n"

        if self.is_exist["headers"]: config += f"headers = {self.headers}\n\n"

        if self.is_exist["payload"]: config += f"{'json_data' if self.payload_type == 'json' else 'data'} = {self.payload}\n\n"

        if self.is_exist["cookies"]: config += f"cookies = {self.cookies}\n\n"

        arugment = ""

        if self.is_exist["params"]: arugment += ", params=params"

        if self.is_exist["headers"]: arugment += ", headers=headers"

        if self.is_exist["payload"]: arugment += f", {'json' if self.payload_type == 'json' else 'data'}={'json_data' if self.payload_type == 'json' else 'data'}"

        if self.is_exist["cookies"]: arugment += ", cookies=cookies"

        self.code =f"""import requests\n\n{config}\n\nrequests.{self.method.lower()}("{self.url}"{arugment})"""


        return self.code

    def Parse_Data_curl(self):
        print(self.payload)
        if self.is_exist["payload"]:
            for line in reversed(self.raw.splitlines()):
                self.spaces += 1
                try:
                    if not line.isspace() or not line == "":
                        self.payload = json.loads(line)
                        break
                except: None
        self.payload = urllib.parse.urlencode(self.payload)

        arugment = ""
        if self.is_exist["headers"]:
            for item in self.headers.items():
                arugment += f"\t-H '{item[0]}: {item[1]}' \\\n"

        if self.is_exist["payload"]: arugment += f"\t--data-raw '{self.payload}' \\\n"

        self.code =f"""curl -X {self.method} \\\n{arugment}\t"{self.url}"\n\t--compressed"""

        return self.code

class APP(App):
    def build(self):
        Window.size = (800, 500)
        self.title = "Fiddler converter"
        Window.clearcolor = (33/255, 36/255, 37/255, 1)
        Window.background_color = (23, 23, 23, 1)
        return menu()

if __name__ == "__main__":
    APP().run()
    shutil.rmtree(f"{os.getenv('LOCALAPPDATA')}\Temp\FiddlerMAPP")


