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

def create_table_recipes(path_settings):
    table = OrderedDict()
    root = ElementTree.parse(path_settings["xml_recipes"]).getroot()
    #go through each recipe
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

    return table

def main():
    path_settings = get_path_settings()

    table = create_table_recipes(path_settings)
    recipe_wiki_table = WikiTable(table)
    recipe_wiki_table.write_table(path_settings["folder_wiki_pages"] + "page_list_of_recipes.txt")

main()
