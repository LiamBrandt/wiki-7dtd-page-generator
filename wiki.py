"""
Part of the 7 Days to Die Wiki Content Generator
Copyright (C) 2017 Liam Brandt <brandt.liam@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import csv
import os
import struct
from re import finditer
from xml.etree import ElementTree
from collections import OrderedDict

def unpack(bin_file, data_type, length_arg=0):
    #integer or unsigned integer
    if data_type == "i" or data_type == "I":
        return int(struct.unpack(data_type, bin_file.read(4))[0])
    #short or unsigned short
    elif data_type == "h" or data_type == "H":
        return int(struct.unpack(data_type, bin_file.read(2))[0])
    #string
    elif data_type == "s":
        return struct.unpack(str(length_arg) + data_type, bin_file.read(length_arg))[0]
    #char
    elif data_type == "c":
        return struct.unpack(data_type, bin_file.read(1))[0]
    #byte or unsigned byte
    elif data_type == "b" or data_type == "B":
        return int(struct.unpack(data_type, bin_file.read(1))[0])

class WikiString(object):
    def __init__(self, original, link_type, no_format=False, prefix="", postfix="", is_link=False):
        self.original = original
        if no_format:
            self.text = original
        else:
            self.text = name_to_wiki_name(original)

        self.prefix = prefix
        self.postfix = postfix

        self.link = None

        #if this is a block with a variant, make link point to the block not the variant
        if link_type == "blocks":
            block_variants = ["Half", "Quarter", "ThreeQuarters", "Eighth", "ArrowSlitHalf",
                "CNRRound", "CNRRoundTop", "CNRFull", "CNRInside", "CNRWedgedFiller",
                "Pillar100", "Pillar50", "Plate", "CTRPlate", "Pole", "Pyramid",
                "Ramp", "CNRRamp", "Stairs25", "Stairs50", "Support", "Wedge",
                "WedgeTip"]

            num_block_variants = 0
            found_working_localization = False
            working_localized_name = ""
            failed_localized_name = ""
            for block_variant in block_variants:
                if original.endswith(block_variant):
                    #this is a variant, first check if the block without the variant plus block is in localization
                    original_without_variant = original.split(block_variant)[0].strip()
                    localized_name = get_localized_name(original_without_variant+"Block")
                    if localized_name == None:
                        #failed, now try without block at the end
                        localized_name = get_localized_name(original_without_variant)
                        if localized_name == None:
                            #try again next loop with the next block variant
                            num_block_variants += 1
                            failed_localized_name = original_without_variant
                            continue
                        else:
                            found_working_localization = True
                            working_localized_name = localized_name
                            break
                    else:
                        found_working_localization = True
                        working_localized_name = localized_name
                        break

            #if we found a better localization for this block
            if found_working_localization:
                self.link = working_localized_name
            else:
                #confirm that this block checked for block variants
                #this will keep blocks without any variants from throwing an error
                if num_block_variants > 0:
                    print("ERROR: Could not find localization for: " + original)
                    self.link = name_to_wiki_name(failed_localized_name)


        #use localization to get a better name for the wiki
        if link_type == "items" or link_type == "blocks":
            localized_name = get_localized_name(original)
            if localized_name != None:
                self.text = localized_name

        #automatically make this a link so long as link hasnt already been set
        if is_link and self.link == None:
            self.link = self.text

        self.check_for_link(link_type)

    def check_for_link(self, link_type):
        if link_type == None:
            return

        link_file = open("./links/links_" + link_type + ".txt", "r")
        for line in link_file.readlines():
            #list of items on the line
            line_list = line.replace("\n", "").split("/")
            if self.original in line_list:
                #create a link
                self.link = line_list[0]

        link_file.close()

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
    full_name = " ".join(word_list)
    for i in range(len(full_name)):
        if full_name[i] == "/":
            if i+1 < len(full_name):
                full_name = full_name[:i+1] + full_name[i+1:].title()

    return full_name

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

def get_localized_name(name):
    with open(get_path_settings()["txt_localization"], newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if row[0] == name:
                return row[4]
    return None

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
    return text+variant

def discover_flags(path_settings):
    found_block_ids = []
    flags = {}
    for filename in os.listdir(path_settings["folder_prefabs"]):
        if filename.endswith(".tts") and path_settings["filter"] in filename:
            bin_file = open(path_settings["folder_prefabs"] + filename, "rb")
            tts_prefab = {}
            tts_prefab["header"] = unpack(bin_file, "s", 4)
            tts_prefab["version"] = unpack(bin_file, "I")
            tts_prefab["x"] = unpack(bin_file, "H")
            tts_prefab["y"] = unpack(bin_file, "H")
            tts_prefab["z"] = unpack(bin_file, "H")

            for i in range(tts_prefab["x"]*tts_prefab["y"]*tts_prefab["z"]):
                block_data = unpack(bin_file, "I")
                found_block_id = str(block_data & 2047)
                if found_block_id not in found_block_ids:
                    found_block_ids.append(found_block_id)
                    block_name = get_block_name(path_settings, found_block_id)

                    bin_string = "{0:b}".format(block_data).zfill(32)[:-11]
                    #print(bin_string + " -> " + block_name)
                    for index, bit in enumerate(bin_string):
                        if bit == "1":
                            if index not in flags:
                                flags[index] = []
                            if block_name not in flags[index]:
                                flags[index].append(block_name)
            print(flags)
    print("\n\n\nFINAL\n\n\n")
    print(flags)

def get_block_name(path_settings, block_id):
    root = ElementTree.parse(path_settings["xml_blocks"]).getroot()
    for block in root:
        if int(block.attrib["id"]) == int(block_id):
            return block.attrib["name"]

def get_prefab_with_most_block(path_settings, block_id):
    #find loot containers
    prefab_loot_blocks = {}
    for filename in os.listdir(path_settings["folder_prefabs"]):
        if filename.endswith(".tts") and path_settings["filter"] in filename:
            prefab_name, variant = get_variant(filename[:-4])
            if prefab_name not in prefab_loot_blocks:
                prefab_loot_blocks[prefab_name] = OrderedDict([("variants", [variant])])
            else:
                prefab_loot_blocks[prefab_name]["variants"].append(variant)

            if block_id not in prefab_loot_blocks[prefab_name]:
                prefab_loot_blocks[prefab_name][block_id] = {}
            prefab_loot_blocks[prefab_name][block_id][variant] = 0

            bin_file = open(path_settings["folder_prefabs"] + filename, "rb")
            tts_prefab = {}
            tts_prefab["header"] = unpack(bin_file, "s", 4)
            tts_prefab["version"] = unpack(bin_file, "I")
            tts_prefab["x"] = unpack(bin_file, "H")
            tts_prefab["y"] = unpack(bin_file, "H")
            tts_prefab["z"] = unpack(bin_file, "H")

            for i in range(tts_prefab["x"]*tts_prefab["y"]*tts_prefab["z"]):
                block_data = unpack(bin_file, "I")
                found_block_id = str(block_data & 2047)

                if found_block_id == str(block_id):
                    prefab_loot_blocks[prefab_name][block_id][variant] += 1

    #report
    prefab_list = {}
    for prefab_name, prefab in prefab_loot_blocks.items():
        for tag, data in prefab.items():
            if tag == block_id:
                for variant_name, count in data.items():
                    if count > 0:
                        if prefab_name not in prefab_list:
                            #determine whether prefab should be considered for max
                            if "[[" in WikiString(prefab_name, "prefabs").get_wiki_text():
                                prefab_list[prefab_name] = count
                        else:
                            if count > prefab_list[prefab_name]:
                                prefab_list[prefab_name] = count
                        #print(prefab_name + variant_name + " -> " + str(count))
    if len(prefab_list) > 0:
        return max(prefab_list, key=lambda key: prefab_list[key])
    return ""

def get_path_settings():
    with open("./settings.txt", "r") as settings_file:
        path_settings = eval(settings_file.read())

    path_settings["folder_data"] = path_settings["folder_7dtd"] + "Data/"
    path_settings["folder_wiki_pages"] = "./output/" + path_settings["version"] + "/wiki_pages/"
    path_settings["folder_map_images"] = "./output/" + path_settings["version"] + "/map_images/"
    path_settings["folder_prefabs"] = path_settings["folder_data"] + "Prefabs/"
    path_settings["folder_config"] = path_settings["folder_data"] + "Config/"

    path_settings["xml_recipes"] = path_settings["folder_config"] + "recipes.xml"
    path_settings["xml_rwgmixer"] = path_settings["folder_config"] + "rwgmixer.xml"
    path_settings["xml_blocks"] = path_settings["folder_config"] + "blocks.xml"
    path_settings["xml_loot"] = path_settings["folder_config"] + "loot.xml"
    path_settings["xml_entity_classes"] = path_settings["folder_config"] + "entityclasses.xml"
    path_settings["xml_navezgane_prefabs"] = path_settings["folder_data"] + "Worlds/Navezgane/prefabs.xml"

    path_settings["txt_localization"] = path_settings["folder_config"] + "Localization.txt"


    #make folders
    folders_to_create = ["folder_wiki_pages", "folder_map_images"]
    for new_folder_name in folders_to_create:
        if not os.path.exists(path_settings[new_folder_name]):
            os.makedirs(path_settings[new_folder_name])

    return path_settings
