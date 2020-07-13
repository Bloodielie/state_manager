def get_requires():
    with open("requirements.txt", encoding="utf-8") as f:
        return f.readlines()

print(get_requires())
