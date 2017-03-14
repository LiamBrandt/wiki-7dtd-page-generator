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

    root = ElementTree.parse(path_settings["xml_blocks"]).getroot()

    list_of_property_names = ["Extends", "Group", "Material", "Shape", "Weight", "FuelValue"]
    unrecorded_property_names = ["IsDeveloper"]
    print(list_of_property_names)

    developer_block_names = []

    for block in root:
        block_name = block.attrib["name"]
        table[block_name] = OrderedDict([
            ("Block", WikiString(block_name, "blocks", is_link=True)),
            ("Id", WikiString(block.attrib["id"], None)),
        ])
        for property_name in list_of_property_names:
            if property_name == "Group":
                table[block_name]["Group"] = WikiList()
            else:
                table[block_name][property_name] = WikiString("", None)

        for subitem in block:
            if subitem.tag == "property":
                if "name" in subitem.attrib:
                    if subitem.attrib["name"] in list_of_property_names or subitem.attrib["name"] in unrecorded_property_names:
                        if subitem.attrib["name"] == "Extends":
                            table[block_name]["Extends"] = WikiString(subitem.attrib["value"], "blocks", is_link=True)
                        elif subitem.attrib["name"] == "Group":
                            for each_group in subitem.attrib["value"].split(","):
                                table[block_name]["Group"].add_string(WikiString(each_group, None, is_link=True))
                        elif subitem.attrib["name"] == "IsDeveloper":
                            if subitem.attrib["value"] == "true":
                                print("Dev block: " + block_name)
                                developer_block_names.append(block_name)
                        else:
                            table[block_name][subitem.attrib["name"]] = WikiString(subitem.attrib["value"], None)

    #go back and apply extended properties
    for block_name, block in table.items():
        #if this block extends another block
        if "Extends" in block:
            if not block["Extends"].is_empty():
                #make sure no extends links to a developer block
                if block["Extends"].original in developer_block_names:
                    block["Extends"] = WikiString(block["Extends"].original, "blocks")

                parent_name = block["Extends"].original
                parent_block = table[parent_name]
                for key, value in parent_block.items():
                    #if the value we are copying into is empty and the value we are copying is not empty
                    if block[key].is_empty() and not value.is_empty():
                        block[key] = value

    #delete all developer blocks that may have already been extended for use in other blocks
    for dev_block_name in developer_block_names:
        del table[dev_block_name]

    return table

def main():
    path_settings = get_path_settings()

    table = create_table_blocks(path_settings)
    blocks_wiki_table = BlockWikiTable(table)
    blocks_wiki_table.write_table(path_settings["folder_wiki_pages"] + "page_list_of_blocks.txt")

main()
