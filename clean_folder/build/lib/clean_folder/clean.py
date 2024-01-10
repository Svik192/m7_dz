import re
import sys
from pathlib import Path

import shutil
from pathlib import Path

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

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():       
            if item.name not in ('Image', 'Video_files', 'Documents', 'Music', 'Archives', 'Other'):
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

    with open(Path(sys.argv[1])+"\list.txt", 'w') as fh:
        fh.write(f"Image: {print_list(Image)}\n")
        fh.write(f"Video_files: {print_list(Video_files)}\n")
        fh.write(f"Documents: {print_list(Documents)}\n")
        fh.write(f"Music: {print_list(Music)}\n")
        fh.write(f"Archives: {print_list(Archives)}\n")
        fh.write(f"Other: {print_list(Unknown_extensions)}\n")

        #fh.write(f"Folder: {folders}\n")

        fh.write(f"All extensions: {print_list(extensions)}\n")
        fh.write(f"Unknown extensions: {print_list(unknown)}\n")


def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)

    # print(f"Image: {Image}")
    # print(f"Video_files: {Video_files}")
    # print(f"Documents: {Documents}")
    # print(f"Music: {Music}")
    # print(f"Archives: {Archives}")
    # print(f"Unknown_extensions: {Unknown_extensions}")

    for file in Image:
        handle_file(file, folder_path, "Image")

    for file in Video_files:
        handle_file(file, folder_path, "Video_files")

    for file in Documents:
        handle_file(file, folder_path, "Documents")

    for file in Music:
        handle_file(file, folder_path, "Music")

    for file in Unknown_extensions:
        handle_file(file, folder_path, "Unknown_extensions")

    for file in Archives:
        handle_archive(file, folder_path, "Unpack_Archive")

    remove_empty_folders(folder_path)

    write_to_file()


if __name__ == '__main__':
    main()
