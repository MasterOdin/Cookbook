from __future__ import print_function
from colorama import init, Fore
import markdown2 as markdown
import os
import shutil
import subprocess


init()

URL = "http://masterodin.github.io/Cookbook"

def setup_directory():
    #print("Setting up the directories...", end="")
    dir_files = os.listdir(".")
    no_remove = ['.git', 'generate.py', '.gitignore']
    for dir_file in dir_files:
        if dir_file in no_remove:
            continue
        elif os.path.isfile(dir_file):
            os.remove(dir_file)
        else:
            shutil.rmtree(dir_file)
    os.makedirs("processed")
    p = subprocess.Popen(["git", "clone",
            "https://github.com/MasterOdin/Cookbook"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    #print(Fore.GREEN + "DONE" + Fore.RESET)


def process_files(categories, recipes, get_dir="Cookbook"):
    #if get_dir == "Cookbook":
    #    print("Processing all the files...", end="")
    dir_files = os.listdir(get_dir)
    #print(get_dir)
    #print(dir_files)
    no_process = ['.git', 'raw_doc_files','.gitignore','README.md']
    for dir_file in dir_files:
        full_file = os.path.join(get_dir, dir_file)
        if dir_file in no_process:
            continue
        elif os.path.isdir(full_file):
            process_files(categories, recipes, full_file)
        else:
            file_name, file_extension = os.path.splitext(dir_file)
            if file_extension == ".md":
                with open(full_file) as read:
                    file_contents = read.read()
                title = get_title(file_contents)
                recipes[file_name] = title
                keywords = get_keywords(file_contents)
                for keyword in keywords:
                    if keyword not in categories:
                        categories[keyword] = set([file_name])
                    else:
                        categories[keyword].add(file_name)
                html = markdown.markdown(file_contents)
                write_file = os.path.join("processed",file_name+".html")
                with open(write_file, "w") as w:
                    w.write(html)
    #if get_dir == "Cookbook":
    #    print(Fore.GREEN + "DONE" + Fore.RESET)


def get_keywords(contents):
    i = contents.find("__Keywords__:")
    contents = contents[i:]
    i = contents.find("\n")
    keywords = contents[13:i].strip().lower()
    return keywords.split(",")


def get_title(contents):
    i = contents.find("\n")
    return contents[2:i]


def get_all_categories(categories):
    return
    i = 0
    keys = categories.keys()
    while i < len(keys):
        for j in range(i+1, len(keys)):
            new_keyword = compound_keywords(keys[i], keys[j])
            categories[new_keyword] = categories[keys[i]] & categories[keys[j]]
        keys = categories.keys()
        i += 1


def compound_keywords(keyword1, keyword2):
    keyword1 = keyword1.split("/")
    keyword2 = keyword2.split("/")
    keyword = keyword1 + keyword2
    keyword.sort()
    return "/".join(keyword)


def generate_cookbook(categories, recipes):
    main_index = open("index.html", "w")
    main_index.write("<h1>Cookbook</h1><br /><br />")
    for key in categories.keys():
        path = os.path.join(URL,key)
        main_index.write("<a href='%s'>%s</a><br />\n" % (path, path))
        if not os.path.exists(key):
            os.makedirs(key)
        index_file = open(os.path.join(key, "index.html"), "w")
        for recipe in categories[key]:
            file_url = os.path.join(URL,key,recipe+".html")
            index_file.write("<a href='%s'>%s</a><br />\n" % (file_url, recipes[recipe]))
            shutil.copyfile(os.path.join("processed", recipe+".html"),
                            os.path.join(key, recipe+".html"))


def generate():
    setup_directory()
    recipe_categories = dict()
    all_recipes = dict()
    process_files(recipe_categories, all_recipes)
    get_all_categories(recipe_categories)
    generate_cookbook(recipe_categories, all_recipes)
    shutil.rmtree("Cookbook")
    shutil.rmtree("processed")


if __name__ == "__main__":
    generate()
