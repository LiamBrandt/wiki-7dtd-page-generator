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

    allowed_property_names = ["Extends", "Group", "Material", "Shape", "Weight", "FuelValue"]
    #create a list of all of the names of properties for the blocks
    """list_of_property_names = []
    for block in root:
        for subitem in block:
            if subitem.tag == "property":
                if "name" in subitem.attrib:
                    if subitem.attrib["name"] not in list_of_property_names and subitem.attrib["name"] in allowed_property_names:
                        list_of_property_names.append(subitem.attrib["name"])"""
    list_of_property_names = allowed_property_names

    print(list_of_property_names)

    for block in root:
        block_name = block.attrib["name"]
        table[block_name] = OrderedDict([
            ("Block", WikiString(block_name, "items", is_link=True)),
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
                    if subitem.attrib["name"] in list_of_property_names:
                        if subitem.attrib["name"] == "Extends":
                            table[block_name]["Extends"] = WikiString(subitem.attrib["value"], "items", is_link=True)
                        elif subitem.attrib["name"] == "Group":
                            for each_group in subitem.attrib["value"].split(","):
                                table[block_name]["Group"].add_string(WikiString(each_group, None, is_link=True))
                        else:
                            table[block_name][subitem.attrib["name"]] = WikiString(subitem.attrib["value"], None)

    #go back and apply extended properties
    for block_name, block in table.items():
        #if this block extends another block
        if "Extends" in block:
            if not block["Extends"].is_empty():
                parent_name = block["Extends"].original
                parent_block = table[parent_name]
                for key, value in parent_block.items():
                    if block[key].is_empty() and not value.is_empty():
                        block[key] = value

    return table

def main():
    path_settings = get_path_settings()

    table = create_table_blocks(path_settings)
    blocks_wiki_table = BlockWikiTable(table)
    blocks_wiki_table.write_table(path_settings["folder_wiki_pages"] + "page_list_of_blocks.txt")

main()
