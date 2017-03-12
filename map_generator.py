import pygame
import struct
from xml.etree import ElementTree

from wiki import get_path_settings, get_variant

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

def main():
    path_settings = get_path_settings()

    source_size = (4096, 4096)
    target_size = (1024, 1024)
    source_target_ratio = (source_size[0]/target_size[0], source_size[1]/target_size[1])
    marker_size = (80, 80)
    target_marker_ratio = (target_size[0]/marker_size[0], target_size[1]/marker_size[1])

    out_image = pygame.surface.Surface(target_size)
    map_image = pygame.transform.smoothscale(pygame.image.load("map.png"), target_size)
    circle_image = pygame.transform.smoothscale(pygame.image.load("circle.png"), (int(target_size[0]/target_marker_ratio[0]), int(target_size[1]/target_marker_ratio[1])))

    combined_lines = [line.rstrip("\n") for line in open("combined_prefabs.txt")]
    root = ElementTree.parse(path_settings["xml_navezgane_prefabs"]).getroot()
    prefab_positions = {}
    for decoration in root:
        prefab_name = get_variant(decoration.attrib["name"])[0]
        prefab_position = decoration.attrib["position"]
        for combined_line in combined_lines:
            param_list = combined_line.split("/")
            if prefab_name in param_list:
                prefab_name = param_list[0]

        #check if we already have another location stored
        if prefab_name not in prefab_positions:
            prefab_positions[prefab_name] = [prefab_position]
        else:
            prefab_positions[prefab_name].append(prefab_position)

    for prefab_name, position_list in prefab_positions.items():
        out_image.blit(map_image, (0, 0))

        """#get the size of the prefab to put marker at the center
        tts_file = open(path_settings["folder_prefabs"] + prefab_name + ".tts", "rb")
        tts_file.read(4)
        size_x = unpack(tts_file, "I")
        tts_file.read(4)
        size_y = unpack(tts_file, "I")
        tts_file.close()"""

        for position_string in position_list:
            position = position_string.split(", ")
            x = int(position[0])
            y = int(position[2])

            scaled_x = (target_size[0]/2)+(x/source_target_ratio[0])-(target_size[0]/target_marker_ratio[0]/2)
            scaled_y = (target_size[1]/2)+(-y/source_target_ratio[1])-(target_size[1]/target_marker_ratio[1]/2)

            out_image.blit(circle_image, (int(scaled_x), int(scaled_y)))
        pygame.image.save(out_image, path_settings["folder_map_images"] + "map_" + prefab_name + ".jpg")

main()
