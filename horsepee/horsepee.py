import json
import pystache

def decode(filename):
  with open(filename) as f:
    parsed = {}
    inContent = False
    decoder = json.JSONDecoder()
    content = ""
    for line in f:
      if("===" in line):
        #print(parsed)
        #print("end keys, content now")
        inContent = True
        continue
      if(not(inContent)):
        key = decoder.decode(line)
        #print(key)
        parsed.update(key)
      else:
        #print(line)
        content = content + line

    parsed["content"] = content
    return parsed

def fill(template, data):
  with open(template) as f:
    templateContent = f.read()
    return pystache.render(templateContent, data)


print(fill("template.mustache", decode("test.tex")))
