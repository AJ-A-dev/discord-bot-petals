
from ollama import Client
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# markdown_path = "create_context_for_ollama/examproject.md"
markdown_path = "create_context_for_ollama/examproject-2.md"
loader = UnstructuredMarkdownLoader(markdown_path)

data = loader.load()

client = Client(host='https://canvas.xini.no')

def read_and_add(f):
    global modelfile_70B, modelfile_7B
    text = f.read()
    modelfile_7B += text
    modelfile_70B += text

# they have different header
with open("create_context_for_ollama/start_7B_modelfile", "r") as f:
    modelfile_7B = f.read()
with open("create_context_for_ollama/start_70B_modelfile", "r") as f: 
    modelfile_70B = f.read()

# aditional info given before markdown file
# with open("create_context_for_ollama/base_system_conf", "r") as f:
#     read_and_add(f)

#markdown file
# with open("create_context_for_ollama/examproject-2.md", "r") as f:
#     read_and_add(f)
modelfile_7B += data[0].page_content
modelfile_70B += data[0].page_content

# end part of file
with open("create_context_for_ollama/base_end", "r") as f:
    read_and_add(f)

print(modelfile_7B)
print(modelfile_70B)

response = client.create(model='llama7B_with_context', modelfile=modelfile_7B)
response = client.create(model='llama70B_with_context', modelfile=modelfile_70B)

print(response)
