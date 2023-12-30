import base64
import pickle
import json
import os
from flask import *
_A = 'utf-8'


def decrypt(encoded_text): encoded_bytes = encoded_text.encode(
    _A); decoded_bytes = base64.b64decode(encoded_bytes); return decoded_bytes.decode(_A)


def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)


def create_root(root):
    folders = root.split('/')
    orig_dir = os.getcwd()
    for x in range(len(folders)):
        try:
            create_folder(folders[x])
            os.chdir(folders[x])
        except:
            pass
    os.chdir(orig_dir)

def get_input(_input): return request.form[_input]

def space():
    print("-------------\n")

def get_element_by_index(lst, index, default=None):
    return lst[index] if 0 <= index < len(lst) else default

def trier_2_listes(liste_dominante, liste_associée1):
    return zip(*sorted(zip(liste_dominante, liste_associée1), key=lambda x: x[0]))


class ErrorDB(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def format_liste_with_limit(liste,begin,limit):
    return [x for x in [get_element_by_index(liste, x , default=None) for x in range(begin,limit)] if x]
