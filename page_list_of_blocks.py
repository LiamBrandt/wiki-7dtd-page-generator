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
from collections import OrderedDict

from wiki import WikiString, WikiList, WikiTable, get_path_settings

class Block(object):
    def __init__(self):
        pass

class BlockWikiTable(WikiTable):
    def write_entry(self, key, value, table_file):
        if not value.is_empty():
            wiki_text = value.get_wiki_text()
            table_file.write(wiki_text)

    def write_header_entry(self, key, table_file):
        table_file.write(key)

def create_table_blocks(path_settings):
    table = OrderedDict()

    recipe_root = ElementTree.parse(path_settings["xml_recipes"]).getroot()
    recipe_names = []
    for recipe in recipe_root:
        recipe_names.append(recipe.attrib["name"])

    root = ElementTree.parse(path_settings["xml_blocks"]).getroot()

    developer_block_names = []

    for block in root:
        block_name = block.attrib["name"]
        table[block_name] = OrderedDict([
            ("Block", WikiString(block_name, "blocks", is_link=True)),
            ("Id", WikiString(block.attrib["id"], None)),
            ("Upgrades To", WikiString("", None)),
            ("Downgrades To", WikiString("", None)),
            ("Extends", WikiString("", None)),
            ("Craftable", WikiString("No", None)),
            ("Group", WikiList()),
            ("Repair Items", WikiList())
        ])

        if block_name in recipe_names:
            table[block_name]["Craftable"] = WikiString("Yes", None)

        for block_property in block:
            if block_property.tag == "property":
                #property has a name
                if "name" in block_property.attrib:
                    property_name = block_property.attrib["name"]
                    property_value = block_property.attrib["value"]
                    if property_name == "Extends":
                        table[block_name]["Extends"] = WikiString(property_value, "blocks", is_link=True)
                    elif property_name == "Group":
                        for each_group in property_value.split(","):
                            table[block_name]["Group"].add_string(WikiString(each_group, None, is_link=True))
                    elif property_name == "IsDeveloper":
                        if property_value == "true":
                            developer_block_names.append(block_name)
                    elif property_name == "DowngradeBlock":
                        table[block_name]["Downgrades To"] = WikiString(property_value, "blocks", is_link=True)
                    elif property_name in table[block_name]:
                        table[block_name][property_name] = WikiString(property_value, None)
                #property has a class with sub properties
                elif "class" in block_property.attrib:
                    if block_property.attrib["class"] == "UpgradeBlock":
                        for upgrade_property in block_property:
                            property_name = upgrade_property.attrib["name"]
                            property_value = upgrade_property.attrib["value"]
                            if property_name == "ToBlock":
                                table[block_name]["Upgrades To"] = WikiString(property_value, "blocks", is_link=True)
                    elif block_property.attrib["class"] == "RepairItems":
                        for repair_property in block_property:
                            table[block_name]["Repair Items"].add_string(WikiString(repair_property.attrib["name"], "items", prefix=repair_property.attrib["value"]+" x ", is_link=True))

    #go back an remove links to dev blocks
    keys_to_remove_dev_links = ["Extends", "Upgrades To", "Downgrades To"]
    for block_name, block in table.items():
        for key in keys_to_remove_dev_links:
            if not block[key].is_empty():
                if block[key].original in developer_block_names:
                    block[key] = WikiString(block[key].original, "blocks")

    #go back and apply extended properties
    for block_name, block in table.items():
        #if this block extends another block
        if not block["Extends"].is_empty():
            parent_name = block["Extends"].original
            parent_block = table[parent_name]
            for key, value in parent_block.items():
                #if the value we are copying into is empty and the value we are copying is not empty
                if block[key].is_empty() and not value.is_empty():
                    block[key] = value

    #delete all developer blocks that may have already been used to extend non developer blocks
    for dev_block_name in developer_block_names:
        del table[dev_block_name]

    return table

def main():
    path_settings = get_path_settings()

    table = create_table_blocks(path_settings)
    blocks_wiki_table = BlockWikiTable(table)
    blocks_wiki_table.write_table(path_settings["folder_wiki_pages"] + "page_list_of_blocks.txt")

main()
