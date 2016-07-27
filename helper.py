import os
import re


def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def fetch_id(text, command):
    regex = "^/{0} *(\d+)$".format(command)
    print("... regex is %s" % regex)
    pattern = re.compile(regex)
    matches = re.findall(pattern, text)
    print(matches)

    if len(matches) == 0:
        return None
    else:
        return matches[0]
