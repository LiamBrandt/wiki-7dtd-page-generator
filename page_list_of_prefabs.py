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

import os
import math
from xml.etree import ElementTree
from collections import OrderedDict

from wiki import WikiString, WikiList, WikiTable, get_path_settings, get_variant
from page_random_world_generation import get_prefab_rules, get_possible_prefabs

def get_sign(num):
    return 1 ^ ((num >> 31) & 0x1)

class PrefabWikiTable(WikiTable):
    def write_entry(self, key, value, table_file):
        #entry in the prefab table
        if not value.is_empty():
            wiki_text = value.get_wiki_text()
            if key == "Locations":
                if value.get_length() > 3:
                    table_file.write("<div class='mw-collapsible mw-collapsed'><small>" + wiki_text + "</small></div>")
                else:
                    table_file.write("<small>" + wiki_text + "</small>")
            else:
                table_file.write(wiki_text)

    def write_header_entry(self, key, table_file):
        if key == "Locations":
            table_file.write(key + " in [[Navezgane]]")
            return
        elif key == "Random World Generation":
            table_file.write("[[" + key + "|RWG]]")
            return
        table_file.write(key)

def create_table_prefabs(path_settings):
    unused_keys = []

    prefab_rules = get_prefab_rules(path_settings)
    possible_prefabs = get_possible_prefabs(prefab_rules)

    #create List of Prefabs table
    table = OrderedDict()
    #go through each prefab
    for filename in os.listdir(path_settings["folder_prefabs"]):
        if filename.endswith(".xml") and path_settings["filter"] in filename:
            #determine the name of the prefab
            prefab_name, variant = get_variant(filename[:-4])

            #just a variant on another prefab, dont add a new row
            if prefab_name in table:
                if variant != "":
                    table[prefab_name]["Variants"].add_string(WikiString(variant, None, no_format=True))
                continue
            #create a new row and add this variant
            else:
                table[prefab_name] = OrderedDict([
                    ("Prefab", WikiString(prefab_name, "prefabs", no_format=True)),
                    ("Variants", WikiList()),
                    ("Biome", WikiList(default="Any")),
                    ("Zoning", WikiString("", "zones")),
                    ("Townships", WikiList()),
                    ("Locations", WikiList()),
                    ("Random World Generation", WikiString("No", None, no_format=True)),
                ])
                if prefab_name+variant in possible_prefabs:
                    table[prefab_name]["Random World Generation"] = WikiString("Yes", None, no_format=True)
                if variant != "":
                    table[prefab_name]["Variants"].add_string(WikiString(variant, None, no_format=True))

            #go through each property of the prefab
            root = ElementTree.parse(path_settings["folder_prefabs"] + filename).getroot()
            for prop in root:
                attribute = prop.attrib
                #Biome
                if attribute["name"] == "AllowedBiomes":
                    for biome in attribute["value"].split(","):
                        if biome == "snow":
                            biome = "Snowy Forest"
                        table[prefab_name]["Biome"].add_string(WikiString(biome, "biomes"))
                elif attribute["name"] == "DisallowedBiomes":
                    for biome in attribute["value"].split(","):
                        print(biome + " -> " + prefab_name)
                #Zoning
                elif attribute["name"] == "Zoning":
                    table[prefab_name]["Zoning"] = WikiString(attribute["value"], "zones")
                #Townships
                elif attribute["name"] == "AllowedTownships":
                    for township in attribute["value"].split(","):
                        table[prefab_name]["Townships"].add_string(WikiString(township, "townships"))
                else:
                    if attribute["name"] not in unused_keys:
                        unused_keys.append(attribute["name"])
    print("Unused Prefab Keys: " + str(unused_keys))

    for prefab_name, prefab in table.items():
        root = ElementTree.parse(path_settings["xml_navezgane_prefabs"]).getroot()
        for decoration in root:
            attribute_name, variant = get_variant(decoration.attrib["name"])
            if attribute_name == prefab_name:
                coords = decoration.attrib["position"].split(",")
                x = int(coords[0])
                z = int(coords[2])
                location = str(int(math.fabs(z)))
                if get_sign(z):
                    location += " N, "
                else:
                    location += " S, "
                location += str(int(math.fabs(x)))
                if get_sign(x):
                    location += " E"
                else:
                    location += " W"
                table[prefab_name]["Locations"].add_string(WikiString(location, "locations", no_format=True))

    for prefab_name, prefab in table.items():
        #if there was only one variant on this prefab, get rid of the variants and put it back into the prefab name
        if prefab["Variants"].get_length() == 1:
            prefab["Prefab"].text = prefab["Prefab"].text + prefab["Variants"].get_string(0).text
            prefab["Variants"] = WikiList()

    return table

def main():
    path_settings = get_path_settings()

    table = create_table_prefabs(path_settings)
    prefab_wiki_table = PrefabWikiTable(table)
    prefab_wiki_table.write_table(path_settings["folder_wiki_pages"] + "page_list_of_prefabs.txt")

main()
