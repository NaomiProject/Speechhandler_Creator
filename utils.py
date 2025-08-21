def load_template(path):
    with open(path, "r") as f:
        return f.read()

def save_file(path, content):
    with open(path, "w") as f:
        f.write(content)
