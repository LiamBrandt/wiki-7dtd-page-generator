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

from wiki import get_localized_name, get_path_settings, WikiTable, WikiString, get_prefab_with_most_block

from xml.etree import ElementTree
from collections import OrderedDict

def create_table_drops(path_settings, item_name):
    tools = {
        "Disassemble": "Wrench",
    }

    table = OrderedDict()

    root = ElementTree.parse(path_settings["xml_blocks"]).getroot()

    block_id_list = []
    for block in root:
        block_id = block.attrib["id"]
        block_name = block.attrib["name"]

        for value in block:
            if value.tag == "drop":
                #found a valid drop
                if "name" in value.attrib and "event" in value.attrib:
                    #this drop has the name of the item
                    if value.attrib["name"] == item_name:
                        counts = value.attrib["count"].split(",")
                        minimum = int(counts[0])
                        maximum = int(counts[-1])
                        if minimum > 0:
                            block_id_list.append(block_id)
                            table[block_id] = OrderedDict([
                                ("Block", WikiString(block_name, "blocks", is_link=True)),
                                #("Action", WikiString("", None)),
                                ("Tool", WikiString("", None)),
                                ("Common Location", WikiString(get_prefab_with_most_block(path_settings, int(block_id)), "prefabs")),
                            ])

                            if table[block_id]["Common Location"].link != None:
                                table[block_id]["Common Location"].text = table[block_id]["Common Location"].link

                            #table[block_id]["Action"] = WikiString(value.attrib["event"], None)
                            if "tool_category" in value.attrib:
                                tool_name = value.attrib["tool_category"]
                                if tool_name in tools:
                                    tool_name = tools[tool_name]
                                table[block_id]["Tool"] = WikiString(tool_name, None, is_link=True)
                            else:
                                table[block_id]["Tool"] = WikiString("Any", None)


    #for block_id in block_id_list:
    #    table[block_id]["Common Location"] = Wiki

    return table

def main():
    item_name = "spring"

    path_settings = get_path_settings()

    table = create_table_drops(path_settings, item_name)
    drops_wiki_table = WikiTable(table)

    drop_list_path = path_settings["folder_wiki_pages"] + "drops/"
    if not os.path.exists(drop_list_path):
        os.makedirs(drop_list_path)

    drops_wiki_table.write_table(drop_list_path + item_name + ".txt")

main()
