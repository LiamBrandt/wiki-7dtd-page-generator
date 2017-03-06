# wiki-7dtd-page-generator
Tool to create tables of information and pages in [wiki markup](https://www.mediawiki.org/wiki/Help:Formatting) for the [7 Days To Die Wiki](https://7daystodie.gamepedia.com/).

Written for [Python 3](https://www.python.org/ftp/python/3.6.0/python-3.6.0.exe).

## Usage
To generate some wiki markup for a page, just run one of the python files that begin with `page_*.py`. The output should be stored in a folder `wiki_pages/version/`.

Not every page python file generates a full page, some just print out information that could be helpful like `page_prefabs.py`.

Don't forget to change `settings.txt` to the path to your 7 Days To Die directory.

### Explanation of each file
- `page_list_of_prefabs.py` - Generates a table of prefabs from the random world generation data from `page_random_world_generation.py`, the Navezgane prefab file `Data/Worlds/Navezgane/prefabs.xml` and the individual prefab XML files in `Data/Prefabs/`.

- `page_list_of_recipes.py` - Generate a list of recipes and ingredients from `Data/Config/recipes.xml`.

- `page_prefabs.py` - Prints out how many prefabs there are in `Data/Prefabs/` and what version each one is.

- `page_random_world_generation.py` - Generates a bullet list of each prefab rule and prefab found in `Data/Config/rwgmixer.xml`.

- `wiki.py` - Shared functions and objects between the python files.

- `settings.txt` - Change the path to your 7 Days To Die directory in here. You can also change the version which affects the name of the output folder, as well as the filter to filter out prefabs with specific names in the `page_list_of_prefabs.py`.

- `links/links_*.txt` - A WikiString will look for links in these files based on the link_type to see if it can link to a page that already exists on the wiki. The items in each file are separated by `/`, the first item being the name of the page on the wiki, and any items after being the names that should link to that page contained in the first item.
