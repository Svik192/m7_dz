import re
import sys
from pathlib import Path

import shutil
from pathlib import Path

# Image('JPEG', 'PNG', 'JPG', 'SVG');
# Video_files ('AVI', 'MP4', 'MOV', 'MKV');
# Documents ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX');
# Music ('MP3', 'OGG', 'WAV', 'AMR');
# Archives ('ZIP', 'GZ', 'TAR');
# Other (Unknown_extensions)

Image = list()
Video_files = list()
Documents = list()
Music = list()
Archives = list()
Unknown_extensions = list()

folders = list()

unknown = set()
extensions = set()

FLAG_FILE = 1
FLAG_ARCHIVES  = 2

list_folders = [
        [Image, 'Image',FLAG_FILE], 
        [Video_files, 'Video_files',FLAG_FILE], 
        [Documents, 'Documents',FLAG_FILE], 
        [Music, 'Music',FLAG_FILE], 
        [Archives,'Archives',FLAG_ARCHIVES],
        [Unknown_extensions, 'Other',FLAG_FILE],
    ]

registered_extensions = {
    'JPEG': Image,
    'PNG': Image,
    'JPG': Image,
    'SVG': Image,    

    'AVI': Video_files,
    'MP4': Video_files,
    'MOV': Video_files,
    'MKV': Video_files,  

    'DOC': Documents,
    'DOCX': Documents,
    'TXT': Documents,
    'PDF': Documents, 
    'XLSX': Documents,
    'PPTX': Documents,   

    'MP3': Music,
    'OGG': Music,
    'WAV': Music,
    'AMR': Music,   

    'ZIP': Archives,
    'GZ': Archives,
    'TAR': Archives
}

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    folders = list()
    for params in list_folders:
        folders.append(params[1])

    for item in folder.iterdir():
        if item.is_dir():       
            # if item.name not in ('Image', 'Video_files', 'Documents', 'Music', 'Archives', 'Other'):
            if item.name not in folders:
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            Unknown_extensions.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                Unknown_extensions.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name.replace(".zip", ''))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def print_list(list):
    res_str = "\n"
    for el in list:
        res_str += f"\t{el}\n"

    return res_str
        
def write_to_file():

    with open(str(Path(sys.argv[1]))+"\\list.txt", 'w') as fh:

        for params in list_folders:
            fh.write(f"{params[1]}: {print_list(params[0])}\n")

        #fh.write(f"Folder: {folders}\n")

        fh.write(f"All extensions: {print_list(extensions)}\n")
        fh.write(f"Unknown extensions: {print_list(unknown)}\n")


def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)

    for params in list_folders:
        print(f"{params[1]}: {print_list(params[0])}")

        for file in params[0]:
            if params[2] == FLAG_FILE:
                handle_file(file, folder_path, params[1])
            elif params[2] == FLAG_ARCHIVES:
                handle_archive(file, folder_path, params[1])
        
    remove_empty_folders(folder_path)

    write_to_file()

    print(f"Done")

if __name__ == '__main__':
    main()


    # for file in Image:
    #     handle_file(file, folder_path, "Image")

    # for file in Video_files:
    #     handle_file(file, folder_path, "Video_files")

    # for file in Documents:
    #     handle_file(file, folder_path, "Documents")

    # for file in Music:
    #     handle_file(file, folder_path, "Music")

    # for file in Unknown_extensions:
    #     handle_file(file, folder_path, "Unknown_extensions")

    # for file in Archives:
    #     handle_archive(file, folder_path, "Unpack_Archive")


