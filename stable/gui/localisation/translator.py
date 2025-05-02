##################################################################
##
## file: translator.py
##
## description: provides functionality for localisation
##
## (c) 2024 Jochen Rust
##     DSI aerospace technology
##
##################################################################
import tkinter as tk

from stable.gui.localisation import english


# returns the necessary language module/ dictionary
def get_dict(language):
    match language.lower():
        case 'en' | 'english':
            return english.translations
        # case ...
        case _:
            return {}


# class, that manages labels. consult documentation on how to use
class Translator:
    def __init__(self, root, lang='en'):
        self.root = root
        self.lang_dict = get_dict(lang)

        # default label, when no translation is defined
        self.default = tk.StringVar(root, "???")
        self.dictionary = {}
        self.spec_keys = {}
        self.initialize()

    # loads the initial language
    def initialize(self):
        correct_dict = self.lang_dict
        for key, translation in correct_dict.items():
            if isinstance(translation, dict):
                spec_key = next(iter(translation))
                translation = translation[spec_key]
                self.spec_keys[key] = spec_key

            self.dictionary[key] = tk.StringVar(self.root, translation)

    # returns the StringVar Object which corresponds to 'key'
    def get(self, key):
        return self.dictionary.get(key, self.default)

    # if multiple meanings are defined: switch to specific meaning
    def set_to(self, key, accurate_key):
        correct_dict = self.lang_dict
        value = correct_dict[key]
        if isinstance(value, dict):
            self.dictionary[key].set(value.get(accurate_key))
            self.spec_keys[key] = accurate_key


    # changes the value of each StringVar to the meaning of the new language
    def translate(self, lang):
        correct_dict = get_dict(lang)
        self.lang_dict = correct_dict
        for key, string_var in self.dictionary.items():
            new_translation = correct_dict.get(key, self.default.get())
            if isinstance(new_translation, dict):
                new_translation = new_translation.get(self.spec_keys[key])
            string_var.set(new_translation)


