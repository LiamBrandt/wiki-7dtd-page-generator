import csv
import os
from re import finditer

class WikiString(object):
    def __init__(self, original, link_type, no_format=False, prefix="", postfix="", is_link=False):
        if no_format:
            self.text = original
        else:
            self.text = name_to_wiki_name(original)

        #use localization to get a better name for the wiki
        if link_type == "items":
            with open(get_path_settings()["txt_localization"], newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for row in reader:
                    if row[0] == original:
                        self.text = row[4]

        self.prefix = prefix
        self.postfix = postfix

        self.link = None
        #automatically make this a link
        if is_link:
            self.link = self.text

        self.check_for_link(link_type)

    def check_for_link(self, link_type):
        if link_type == None:
            return

        link_file = open("./links/links_" + link_type + ".txt", "r")
        for line in link_file.readlines():
            #list of items on the line
            line_list = line.replace("\n", "").split("/")
            if self.text in line_list:
                #create a link
                self.link = line_list[0]

        link_file.close()
        return None

    def get_wiki_text(self):
        if self.link != None and self.text != None:
            if self.link != self.text:
                return self.prefix + "[[" + self.link + "|" + self.text + "]]" + self.postfix
            else:
                return self.prefix + "[[" + self.link + "]]" + self.postfix
        else:
            return self.prefix + self.text + self.postfix

    def is_empty(self):
        if self.get_wiki_text() == "":
            return True
        return False

class WikiList(object):
    def __init__(self, default=""):
        self.wiki_strings = []
        self.default = default

    def add_string(self, wiki_string):
        self.wiki_strings.append(wiki_string)

    def get_string(self, index):
        return self.wiki_strings[index]

    def get_length(self):
        return len(self.wiki_strings)

    def get_wiki_text(self):
        if self.get_length() == 0:
            return self.default

        wiki_text = ""
        for wiki_string in self.wiki_strings:
            wiki_text += wiki_string.get_wiki_text() + "<br>"
        return wiki_text

    def is_empty(self):
        if self.get_wiki_text() == "":
            return True
        return False

class WikiTable(object):
    def __init__(self, table):
        #an OrderedDict of OrderedDicts for table information
        self.table = table

    def write_table(self, table_file_name):
        #write table
        table_file = open(table_file_name, "w")
        table_file.truncate()

        #write top row in table
        table_file.write("{| class='wikitable sortable'\n|-\n! ")
        for prefab_name, prefab in self.table.items():
            j = 0
            for key, value in prefab.items():
                if j != 0:
                    table_file.write(" !! ")
                j += 1
                self.write_header_entry(key, table_file)
            break
        table_file.write("\n")

        for prefab_name, prefab in self.table.items():
            #write row in table
            table_file.write("|-\n| ")
            i = 0
            for key, value in prefab.items():
                #write entry in table
                if i != 0:
                    table_file.write(" || ")
                i += 1

                self.write_entry(key, value, table_file)
            table_file.write("\n")

        table_file.write("|}")
        table_file.close()

    def write_entry(self, key, value, table_file):
        if not value.is_empty():
            wiki_text = value.get_wiki_text()
            table_file.write(wiki_text)

    def write_header_entry(self, key, table_file):
        table_file.write(key)

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

#should be same as title() except it doesnt capitalize the 'm' in 762mmBullet
def title_custom(name):
    word_list = " ".join(name.split("_")).split()
    for i in range(len(word_list)):
        word_list[i] = word_list[i].capitalize()
    return " ".join(word_list)

def name_to_wiki_name(name):
    return title_custom(" ".join(camel_case_split(name))).replace("_", " ")

def get_variant(name):
    variant_char_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_"]
    variant = ""
    shortening = True
    while(shortening):
        if name[-1] in variant_char_list:
            variant = name[-1] + variant
            name = name[:-1]
        else:
            shortening = False
    return name, variant

def convert_to_link(text, link_type, use_get_variant=False):
    variant = ""
    if use_get_variant:
        text, variant = get_variant(text)

    link_file = open("./links/links_" + link_type + ".txt", "r")
    for line in link_file.readlines():
        #list of items on the line
        line_list = line.replace("\n", "").split("/")
        if text in line_list:
            #create a link
            link = line_list[0]
            if link != text:
                return "[[" + link + "|" + text + variant + "]]"
            else:
                return "[[" + link + "]]"

    link_file.close()
    return text

def get_path_settings():
    with open("./settings.txt", "r") as settings_file:
        path_settings = eval(settings_file.read())

    path_settings["folder_data"] = path_settings["folder_7dtd"] + "Data/"
    path_settings["folder_wiki_pages"] = "./wiki_pages/" + path_settings["version"] + "/"
    path_settings["folder_prefabs"] = path_settings["folder_data"] + "Prefabs/"
    path_settings["folder_config"] = path_settings["folder_data"] + "Config/"

    path_settings["xml_recipes"] = path_settings["folder_config"] + "recipes.xml"
    path_settings["xml_rwgmixer"] = path_settings["folder_config"] + "rwgmixer.xml"
    path_settings["xml_navezgane_prefabs"] = path_settings["folder_data"] + "Worlds/Navezgane/prefabs.xml"

    path_settings["txt_localization"] = path_settings["folder_config"] + "Localization.txt"


    #make folders
    if not os.path.exists(path_settings["folder_wiki_pages"]):
        os.makedirs(path_settings["folder_wiki_pages"])

    return path_settings
