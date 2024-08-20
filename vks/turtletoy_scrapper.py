import os
import shutil
import re
import requests
from bs4 import BeautifulSoup
import html
import jsbeautifier


def camel_case(s):
    return "".join(word.title() for word in s.split("_"))


import re
import html
import jsbeautifier
import requests
from bs4 import BeautifulSoup


urls = [
    r"https://turtletoy.net/turtle/ca6b971c6f",
    r"https://turtletoy.net/turtle/12f1da9318",
    r"https://turtletoy.net/turtle/8a68f77d34",
    r"https://turtletoy.net/turtle/2696d19370",
    r"https://turtletoy.net/turtle/b2e21ea799",
    r"https://turtletoy.net/turtle/2a47f9244f",
    r"https://turtletoy.net/turtle/101d362439",
    r"https://turtletoy.net/turtle/8e3dcf67c9",
    r"https://turtletoy.net/turtle/9e49109bc0",
    r"https://turtletoy.net/turtle/7fcc815177",
    r"https://turtletoy.net/turtle/716fcbfa5b",
    r"https://turtletoy.net/turtle/fa14c628d4",
    r"https://turtletoy.net/turtle/4f0f7579c8",
    r"https://turtletoy.net/turtle/e5df5b10e0",
    r"https://turtletoy.net/turtle/a4242cdb2b",
    r"https://turtletoy.net/turtle/789cce3829",
    r"https://turtletoy.net/turtle/65cb465053",
    r"https://turtletoy.net/turtle/ee757a914f",
    r"https://turtletoy.net/turtle/92ebe08d89",
    r"https://turtletoy.net/turtle/11075dfee0",
    r"https://turtletoy.net/turtle/c31e5055d1",
    r"https://turtletoy.net/turtle/740f09b88c",
    r"https://turtletoy.net/turtle/deca53a32d",
    r"https://turtletoy.net/turtle/2d8b61851f",
    r"https://turtletoy.net/turtle/182d91df0d",
    r"https://turtletoy.net/turtle/4b8ea1c123",
    r"https://turtletoy.net/turtle/f9915c1d89",
    r"https://turtletoy.net/turtle/db5745b137",
    r"https://turtletoy.net/turtle/e6727b8fd6",
    r"https://turtletoy.net/turtle/34d41bac2b",
    r"https://turtletoy.net/turtle/c1486ea2b0",
    r"https://turtletoy.net/turtle/1eeb777471",
    r"https://turtletoy.net/turtle/30f29b215b",
    r"https://turtletoy.net/turtle/ab7954417c",
    r"https://turtletoy.net/turtle/39291a37f5",
    r"https://turtletoy.net/turtle/1774c93bd1",
    r"https://turtletoy.net/turtle/3b1cb6beea",
    r"https://turtletoy.net/turtle/9a79d5c213",
    r"https://turtletoy.net/turtle/browse/lov",
    r"https://turtletoy.net/turtle/21307683d5",
    r"https://turtletoy.net/turtle/676604a95f",
    r"https://turtletoy.net/turtle/1b67144c76",
    r"https://turtletoy.net/turtle/1e87098a8c",
    r"https://turtletoy.net/turtle/00598fd5c7",
    r"https://turtletoy.net/turtle/86fba4692b",
    r"https://turtletoy.net/turtle/c82f5e2af3",
    r"https://turtletoy.net/turtle/914281c07f",
    r"https://turtletoy.net/turtle/7ea8091a5c",
    r"https://turtletoy.net/turtle/8c5bc4d2b9",
    r"https://turtletoy.net/turtle/bebb916342",
    r"https://turtletoy.net/turtle/6000294180",
    r"https://turtletoy.net/turtle/6ad35dce15",
    r"https://turtletoy.net/turtle/26334527b8",
    r"https://turtletoy.net/turtle/f9ae1f8605",
    r"https://turtletoy.net/turtle/80f5254064",
    r"https://turtletoy.net/turtle/cd5d29d769",
    r"https://turtletoy.net/turtle/8fd587d673",
    r"https://turtletoy.net/turtle/2675421072",
    r"https://turtletoy.net/turtle/52d84c54cc",
    r"https://turtletoy.net/turtle/cf30458f23",
    r"https://turtletoy.net/turtle/c355e9f385",
    r"https://turtletoy.net/turtle/dfacc24904",
    r"https://turtletoy.net/turtle/dd4c8beb92",
    r"https://turtletoy.net/turtle/cec3b339df",
    r"https://turtletoy.net/turtle/d30c466e56",
    r"https://turtletoy.net/turtle/c0af204ebf",
    r"https://turtletoy.net/turtle/8ebadc44b9",
    r"https://turtletoy.net/turtle/5d4f95a589",
    r"https://turtletoy.net/turtle/150402a6fb",
    r"https://turtletoy.net/turtle/8d3cf5a5c2",
    r"https://turtletoy.net/turtle/a521066015",
    r"https://turtletoy.net/turtle/0479c0d1c9",
]

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    h3_tags = soup.find_all("h3")

    for tag in h3_tags:
        print(tag.text)
        tag_text = tag.text
        sanitized_tag = re.sub(
            "[^0-9a-zA-Z]+", "_", tag_text
        )  # Replace non-alphanumeric characters with underscore
        sanitized_tag = sanitized_tag.strip("_")  # Remove trailing underscores
        sanitized_tag = sanitized_tag.lower()  # Convert to lowercase
        # Create a new directory with the sanitized tag name
        new_dir = os.path.join(os.getcwd(), sanitized_tag)
        if  os.path.exists(new_dir):
            print(f"Directory {new_dir} already exists.")
            continue
        shutil.copytree("template", new_dir)

        # Create a README.md file in the new directory
        with open(os.path.join(new_dir, "README.md"), "w") as f:
            f.write(f"# {tag_text}\n\n")
            f.write(f"[turtle toy]({url})\n")
            f.write(f" - [ ] done")

        # Replace 'TmpSketch' with the CamelCase version of the sanitized tag in the file
        with open(os.path.join(new_dir, "sketch_template.py"), "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("TmpSketch", camel_case(sanitized_tag))

        # Write the file out again
        with open(os.path.join(new_dir, f"sketch_{sanitized_tag}.py"), "w") as file:
            file.write(filedata)

        # Delete the original file
        os.remove(os.path.join(new_dir, "sketch_template.py"))

    code = soup.find("pre")

    if code:
        code_text = html.unescape(code.text)
        formatted_code = jsbeautifier.beautify(code_text)  # Format the JavaScript code
        # Write the formatted code to original_code.js in the new directory
        with open(os.path.join(new_dir, "original_code.js"), "w") as f:
            f.write(formatted_code)

    else:
        print("No <pre> tag found in the HTML.")
    pass
