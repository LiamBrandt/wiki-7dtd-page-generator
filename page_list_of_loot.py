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

# WORK IN PROGRESS

from xml.etree import ElementTree

from wiki import get_path_settings

class ItemRef(object):
    def __init__(self, name, count, prob):
        self.name = name
        self.count = count
        self.prob = prob

class LootGroupRef(object):
    def __init__(self, name, count, prob):
        self.name = name
        self.count = count
        self.prob = prob

class LootGroup(object):
    def __init__(self, name):
        self.name = name

        self.groups = []
        self.items = []

class LootContainer(object):
    def __init__(self, id_number, count):
        self.id_number = id_number
        self.count = count

        self.groups = []
        self.items = []

def parse_loot_item(loot_item):
    name = loot_item.attrib["name"]
    count = "1"
    prob = 1
    if "count" in loot_item.attrib:
        count = loot_item.attrib["count"]
    if "prob" in loot_item.attrib:
        prob = float(loot_item.attrib["prob"])
    return ItemRef(name, count, prob)

def parse_loot_group_ref(loot_group):
    name = loot_group.attrib["group"]
    count = "1"
    prob = 1
    if "count" in loot_group.attrib:
        count = loot_group.attrib["count"]
    if "prob" in loot_group.attrib:
        prob = float(loot_group.attrib["prob"])
    return LootGroupRef(name, count, prob)

def create_table_loot(path_settings):
    root = ElementTree.parse(path_settings["xml_loot"]).getroot()

    for loot_container in root:
        if loot_container.tag == "lootgroup":
            new_loot_group = LootGroup(loot_container.attrib["name"])
            for loot in loot_container:
                if "name" in loot.attrib:
                    new_item_ref = parse_loot_item(loot)
                    new_loot_group.items.append(new_item_ref)
                elif "group" in loot.attrib:
                    new_loot_group_ref = parse_loot_group_ref(loot)
                    new_loot_group.groups.append(new_loot_group_ref)
        elif loot_container.tag == "lootcontainer":
            new_loot_container = LootContainer()




    """#go through each recipe
    for recipe in root:
        recipe_name = recipe.attrib["name"]
        table[recipe_name] = OrderedDict([
            ("Recipe", WikiString(recipe_name, "items", is_link=True)),
            ("Count", WikiString("", None)),
            ("Craft Area", WikiString("", "crafting_area")),
            ("Ingredients", WikiList()),
        ])
        if "count" in recipe.attrib:
            table[recipe_name]["Count"].text = recipe.attrib["count"]
        if "craft_area" in recipe.attrib:
            table[recipe_name]["Craft Area"] = WikiString(recipe.attrib["craft_area"], "crafting_area", is_link=True)

        #go through each ingredient
        for subitem in recipe:
            if subitem.tag == "ingredient":
                prefix = subitem.attrib["count"] + " x "
                postfix = ""
                if int(subitem.attrib["count"]) == 0:
                    prefix = "1 x "
                    postfix = " (Optional)"
                table[recipe_name]["Ingredients"].add_string(WikiString(subitem.attrib["name"], "items", prefix=prefix, postfix=postfix, is_link=True))

    return table"""

def main():
    path_settings = get_path_settings()

    create_table_loot(path_settings)

main()
