from textnode import TextNode
import os
import shutil


def main():
    copies_directory_to_public("static", "public")

def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def copies_directory_to_public(source, dest):     
    clear_directory(dest)       
    
    if not os.path.exists(dest):
        os.makedirs(dest)

    directory_list = os.listdir(source)

    for item in directory_list:

        source_item = os.path.join(source, item)
        dest_item = os.path.join(dest, item)

        if os.path.isfile(source_item):
            print(f"Copying file {source_item} to {dest_item}")
            shutil.copy(source_item, dest_item)

        elif os.path.isdir(source_item):
            print(f"Entering directory {source_item}")
            copies_directory_to_public(source_item, dest_item)




main()