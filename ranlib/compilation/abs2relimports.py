import os
from typing import Optional

from ranlib.constants import DOTRAN_FOLDER_NAME


def find_all_python_files(directory: str) -> list[str]:
    """
    Recursively finds all Python files in the given directory and its subdirectories.

    :param directory: Path to the directory to start searching from.
    :return: List of paths to all Python files found.
    """
    python_files = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def replace_imports(directory: str) -> None:
    allFiles: list[str] = find_all_python_files(directory)
    repository_files = set()
    for fileName in allFiles:
        file_to_add = fileName.split("/")[-1]
        repository_files.add(file_to_add)
    print(repository_files)
    # TODO: why cannot these files be found?
    print("Files:", allFiles)
    for fileName in allFiles:
        print(fileName)
        f = open(fileName, "r")
        newf = open(fileName + ".temp", "w")
        lines = f.readlines()
        for line in lines:
            # TODO: The strip is problematic because spaces are removed from the line
            # Ex: outputs jso.py instead of json.py however, works for repo files as expected
            words = line.strip().split(" ")
            # if len(words) > 2:
            #     print("test",words[1] in repository_files,words[1])
            if (
                len(words) > 2
                and words[0] == "from"
                and words[2] == "import"
                and not words[1].startswith(".")
                and (words[1] + ".py") in repository_files
            ):  # non library import
                print("Words", words, words[1])
                try:
                    # TODO: consider navigating to the file we want creating and leaving
                    # TODO: Why do we want to do this?
                    # TODO: What is the purpose of this code?
                    file_path_test: str = directory + "/" + words[1] + ".py"
                    file_path_test_list: list[str] = file_path_test.split("/")
                    ran_path_index: int = file_path_test_list.index(DOTRAN_FOLDER_NAME)
                    ran_path = "/".join(file_path_test_list[ran_path_index:])
                    # new_file: str = "/".join(words[1].split(".")) + ".py"  # assigned but never used
                    testf = open(ran_path, "r")
                    testf.close()
                    currentPath = words[1].split(".")
                    myPath = fileName.split("/")[1:]
                    print(f"Observing Path Traversal of {words[1]}")
                    print(currentPath, myPath)
                    index = 0
                    while currentPath[index] == myPath[index]:
                        index += 1
                    if index == len(myPath) - 1 and index == len(currentPath) - 1:
                        newPath = "." + currentPath[-1]
                    else:
                        numParents = len(myPath) - index
                        newPath = ""
                        # for i in range(1):
                        #     newPath += "."
                        # newPath += ".".join(currentPath[index:])

                        newPath += (index + 1) * "."
                        # for _ in range(index + 1):
                        #     newPath += "."
                        newPath += ".".join(currentPath[index:])
                    newLine = "from " + newPath + " import " + words[3]
                    print(directory)
                    print(newLine)
                    newf.write(newLine)
                except:
                    # print("Exception (File Unable to be read):",e)
                    # print(l.strip())
                    newf.write(line.strip())
                    print("File Does Not Exist Writing File:", line.strip())
            elif words[0] == "import" and not words[1].startswith("."):
                try:
                    newString = "/".join(words[1].split(".")) + ".py"
                    print("Import", newString)
                    testf = open(newString, "r")
                    testf.close()
                    currentPath = words[1].split(".")
                    myPath = fileName.split("/")[1:]
                    index = 0
                    while currentPath[index] == myPath[index]:
                        index += 1
                    if index == len(myPath) - 1 and index == len(currentPath) - 1:
                        newPath = "." + currentPath[-1]
                    else:
                        numParents = len(myPath) - index
                        newPath = ""
                        for i in range(numParents):
                            newPath += "."
                        newPath += ".".join(currentPath[index:])
                    newLine = "import " + newPath
                    newf.write(newLine)
                except:
                    # print("Exception:",e)
                    newf.write(line)
            else:
                newf.write(line)
        newf.close()
        f.close()
        f = open(fileName, "w")
        newf = open(fileName + ".temp", "r")
        for newf_line in newf.readlines():
            f.write(newf_line)
        os.remove(fileName + ".temp")
