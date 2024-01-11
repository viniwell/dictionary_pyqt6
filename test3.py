import json
file=open('test.json', 'w')
json.dump(['\n', ['Theme', 'Українська', 'English'], ['Theme', 'Українська', 'English'], 'Unrecorded', 0], file)
file.close()
with open('test.json', 'r') as file:
    data=json.load(file)
    print(data[0])