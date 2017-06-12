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

from xml.etree import ElementTree

from wiki import name_to_wiki_name, convert_to_link, get_path_settings

class PrefabRule(object):
    def __init__(self, name):
        self.name = name

        self.prefabs = []

    #calculate probability for each prefab and set it as the prob attrib as a float
    def calculate_and_set_probs(self):
        total_prob = 0.0
        for prefab in self.prefabs:
            if "prob" in prefab.attrib:
                total_prob += float(prefab.attrib["prob"])
            else:
                total_prob += 1.0

        for prefab in self.prefabs:
            if "prob" in prefab.attrib:
                prefab.attrib["prob"] = float(prefab.attrib["prob"]) / total_prob
            else:
                prefab.attrib["prob"] = 1.0 / total_prob

    def grab_nested_prefabs(self, top_level_prefab_rules):
        grabbed = []
        for prefab in self.prefabs:
            if "rule" in prefab.attrib:
                #go through top level prefabs to find one that matches this rule
                for top_level_prefab_rule in top_level_prefab_rules:
                    if prefab.attrib["rule"] == top_level_prefab_rule.name:
                        grabbed += top_level_prefab_rule.grab_nested_prefabs(top_level_prefab_rules)
                        break
            elif "name" in prefab.attrib:
                grabbed.append(prefab.attrib["name"])

        #return grabbed with no duplicate names
        return sorted(set(grabbed))

    def write(self, write_file):
        write_file.write("*'''Prefab Rule - " + name_to_wiki_name(self.name) + "'''\n")
        for prefab in self.prefabs:
            prefab.write(write_file)

class Prefab(object):
    def __init__(self):
        self.attrib = {}

    def write(self, write_file):
        write_file.write("**")
        if "name" in self.attrib:
            write_file.write("Prefab - " + convert_to_link(self.attrib["name"], "prefabs", use_get_variant=True) + " - ")
        elif "rule" in self.attrib:
            write_file.write("Prefab Rule - " + name_to_wiki_name(self.attrib["rule"]) + " - ")
        else:
            write_file.write("ERROR - ")

        write_file.write(str(('%.2f' % (self.attrib["prob"]*100.0)).rstrip('0').rstrip('.')) + "% chance")
        write_file.write("\n")

def get_prefab_rules(path_settings):
    prefab_rules = []

    root = ElementTree.parse(path_settings["xml_rwgmixer"]).getroot()
    for item in root:
        print(item.tag)
        if item.tag == "prefab_rules":
            #go through each prefab rule
            for prefab_rule in item:
                if prefab_rule.attrib["name"] != "none":
                    new_rule_object = PrefabRule(prefab_rule.attrib["name"])

                    #go through each prefab in the prefab rule
                    for prefab in prefab_rule:
                        if prefab.tag == "prefab":
                            new_prefab_object = Prefab()
                            new_prefab_object.attrib = prefab.attrib
                            new_rule_object.prefabs.append(new_prefab_object)

                    new_rule_object.calculate_and_set_probs()
                    prefab_rules.append(new_rule_object)

    return prefab_rules

def get_possible_prefabs(prefab_rules):
    top_level_rules = ["default", "wildernessGroup"]
    possible_prefabs = []
    for prefab_rule in prefab_rules:
        if prefab_rule.name in top_level_rules:
            possible_prefabs += prefab_rule.grab_nested_prefabs(prefab_rules)

    return possible_prefabs

def main():
    path_settings = get_path_settings()

    prefab_rules = get_prefab_rules(path_settings)

    #write the random_world_generation.txt
    write_file = open(path_settings["folder_wiki_pages"] + "page_random_world_generation.txt", "w")
    write_file.truncate()
    for prefab_rule in prefab_rules:
        prefab_rule.write(write_file)
    write_file.close()

    possible_prefabs = get_possible_prefabs(prefab_rules)

    all_prefabs = []
    for prefab_rule in prefab_rules:
        all_prefabs += prefab_rule.grab_nested_prefabs(prefab_rules)

    impossible_prefabs = list(set(all_prefabs)-set(possible_prefabs))
    for prefab_name in impossible_prefabs:
        print("impossible prefab: " + prefab_name)

main()
