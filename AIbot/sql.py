import os

text = input("Enter a data: ")
hex_data = text.encode().hex()
filename = "hex_output.txt"
with open(filename, "w") as file:
    file.write(hex_data)
file_size = os.path.getsize(filename)

print("\nData has been saved in hex format.")
print(f"File name   : {filename}")
print(f"File size   : {file_size} bytes")

