import struct
import os

from wiki import get_path_settings

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

    #print out the count of prefab file version
    versions = {}
    for filename in os.listdir(path_settings["folder_prefabs"]):
        if filename.endswith(".tts") and path_settings["filter"] in filename:
            bin_file = open(path_settings["folder_prefabs"] + filename, "rb")
            bin_file.read(4)
            version = unpack(bin_file, "I")
            if version not in versions:
                versions[version] = 0
            versions[version] += 1

    print("Versions: " + str(versions))

main()
