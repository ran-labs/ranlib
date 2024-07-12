import os


def find_all_python_files(directory: str):
    """
    Recursively finds all Python files in the given directory and its subdirectories.

    :param directory: Path to the directory to start searching from.
    :return: List of paths to all Python files found.
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def replace_imports(directory: str) -> None:
    allFiles = find_all_python_files(directory)

    for fileName in allFiles:
        f = open(fileName, "r")
        newf = open(fileName + ".temp", "w")
        lines = f.readlines()
        for l in lines:
            words = l.split(" ")

            if (
                words[0] == "from"
                and words[2] == "import"
                and not words[1].startswith(".")
            ):  # non library import
                try:
                    testf = open("/".join(words[1].split(".")) + ".py", "r")
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
                    newLine = "from " + newPath + " import " + words[3]
                    newf.write(newLine)
                except:
                    newf.write(l)
            elif words[0] == "import" and not words[1].startswith("."):
                try:
                    newString = "/".join(words[1].split("."))[:-1] + ".py"
                    print(newString)
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
                    newf.write(l)

            else:
                newf.write(l)
        newf.close()
        f.close()
        f = open(fileName, "w")
        newf = open(fileName + ".temp", "r")
        for l in newf.readlines():
            f.write(l)
        os.remove(fileName + ".temp")
