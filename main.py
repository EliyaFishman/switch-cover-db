import json
import os
import string
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.request import urlopen

import requests
from PIL import Image


def main():
    json_handler = JsonHandler()
    download_cover_db()
    download_db()
    list_of_ids = read_xml()
    for (game_id, name) in list_of_ids:
        if os.path.exists("switch/coverM/US/" + game_id + ".jpg"):
            real_id = json_handler.find_in_dict(name)
            print("game id " + game_id)
            print("name " + name)
            if real_id is None:
                print("Couldn't find a title id for " + name)
                continue
            print("real id " + real_id)
            if name[0] in string.digits:
                directory = "Vertical/0-9/"
            else:
                directory = "Vertical/" + name[0].upper() + "/"
            Path(directory).mkdir(parents=True, exist_ok=True)
            image_name = directory + replace_space_with_dashes(string_to_ascii(name)) + "-cover1-[" + real_id + "].jpg"
            # resize the image to the right dimensions
            img = Image.open("switch/coverM/US/" + game_id + ".jpg")
            img = img.resize((256, 256), Image.ANTIALIAS)
            img.save(image_name)
            check_for_extra_images("https://art.gametdb.com/switch/coverM2/US/" + game_id + ".jpg",
                                   directory + replace_space_with_dashes(
                                       string_to_ascii(name)) + "-cover2-[" + real_id + "].jpg")
            result = check_for_extra_images("https://art.gametdb.com/switch/coverMB/US/" + game_id + ".jpg",
                                            directory + replace_space_with_dashes(
                                                string_to_ascii(name)) + "-cover-b-[" + real_id + "].jpg")
            if result:
                check_for_extra_images("https://art.gametdb.com/switch/coverMB2/US/" + game_id + ".jpg",
                                       directory + replace_space_with_dashes(
                                           string_to_ascii(name)) + "-cover-b2-[" + real_id + "].jpg")


class JsonHandler:
    def __init__(self):
        response = urlopen("https://raw.githubusercontent.com/blawar/titledb/master/titles.US.en.json")
        html = response.read()

        self.dictionary = json.loads(html)

    def find_in_dict(self, name):
        a = [x for x in self.dictionary.values() if "name" in x and compare_names(name, x['name'])]
        if len(a) > 0:
            return a[0]["id"]


def string_to_ascii(s):
    printable = set(string.digits + string.ascii_letters + string.whitespace)
    return ''.join(filter(lambda x: x in printable, s)).lower()


def replace_space_with_dashes(s):
    return s.replace(" ", "-")


def compare_names(name1, name2):
    return all(word in string_to_ascii(name2) for word in string_to_ascii(name1))


def download_cover_db():
    url = "https://www.gametdb.com/download.php?FTP=GameTDB-switch_coverM-US-2021-03-31.zip"
    response = urlopen(url)
    file = open("database.zip", "wb")
    file.write(response.read())
    file.close()
    with zipfile.ZipFile("database.zip", 'r') as zip_ref:
        zip_ref.extractall(".")


def download_db():
    url = "https://www.gametdb.com/switchtdb.zip?LANG=EN"
    response = urlopen(url)
    file = open("switchtdb.zip", "wb")
    file.write(response.read())
    file.close()
    with zipfile.ZipFile("switchtdb.zip", 'r') as zip_ref:
        zip_ref.extractall(".")


def read_xml():
    tree = ET.parse('switchtdb.xml')
    root = tree.getroot()
    list_of_id = list()
    for child in root:
        game_id = child.find("id")
        locale = child.find("locale")
        region = child.find("region")
        if game_id is not None and region is not None and (
                region.text is None or region.text == "ALL" or "USA" in region.text):
            if locale is not None:
                list_of_id.append((game_id.text, locale.find("title").text))
    # print(list_of_id)
    return list_of_id


def check_for_extra_images(url, name):
    r = requests.get(url, allow_redirects=True)
    if r.status_code == 200:
        file = open(name, "wb")
        file.write(r.content)
        file.close()
        img = Image.open(name)
        img = img.resize((256, 256), Image.ANTIALIAS)
        img.save(name)
        return True
    return False


if __name__ == '__main__':
    # print(compare_names("LEGO City Undercover", "LEGO CITY Undercover"))
    # download_cover_db()
    # read_xml()
    main()
