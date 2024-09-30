from modules import scripts
import gradio as gr
import json
import os


STYLE_FILE = os.path.join(scripts.basedir(), "styles.json")
EMPTY_STYLE = {"styles": {}, "deleted": {}}


class StyleManager:

    def __init__(self):
        self.STYLE_SHEET: dict = None

    def load_styles(self):
        if os.path.isfile(STYLE_FILE):
            with open(STYLE_FILE, "r", encoding="utf-8") as json_file:
                self.STYLE_SHEET = json.load(json_file)
                print("[Flux. CC] Style Sheet Loaded...")

        else:
            with open(STYLE_FILE, "w+", encoding="utf-8") as json_file:
                self.STYLE_SHEET = EMPTY_STYLE
                json.dump(self.STYLE_SHEET, json_file)
                print("[Flux. CC] Creating Empty Style Sheet...")

        return self.list_style()

    def list_style(self) -> list[str]:
        return list(self.STYLE_SHEET["styles"].keys())

    def get_style(self, style_name: str) -> tuple[bool | str | float]:
        style: list = self.STYLE_SHEET["styles"].get(style_name, None)

        if not style:
            print(f'\n[Error] No Style of name "{style_name}" was found!\n')
            return [gr.update()] * 11

        return [gr.update(value=s) for s in style]

    def save_style(self, style_name: str, *args):
        if style_name in self.STYLE_SHEET["styles"]:
            print(f'\n[Error] Duplicated Style Name: "{style_name}" Detected!')
            print("Values were not saved!\n")
            return self.list_style()

        new_style = [*args]
        self.STYLE_SHEET["styles"].update({style_name: new_style})

        with open(STYLE_FILE, "w+") as json_file:
            json.dump(self.STYLE_SHEET, json_file)

        print(f'\nStyle of Name "{style_name}" Saved!\n')
        return self.list_style()

    def delete_style(self, style_name: str):
        if style_name not in self.STYLE_SHEET["styles"]:
            print(f'\n[Error] No Style of name "{style_name}" was found!\n')
            return self.list_style()

        style: dict = self.STYLE_SHEET["styles"].get(style_name)
        self.STYLE_SHEET["deleted"].update({style_name: style})
        del self.STYLE_SHEET["styles"][style_name]

        with open(STYLE_FILE, "w+") as json_file:
            json.dump(self.STYLE_SHEET, json_file)

        print(f'\nStyle of name "{style_name}" was deleted!\n')
        return self.list_style()
