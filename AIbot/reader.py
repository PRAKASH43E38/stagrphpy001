import os
import pyttsx3

filename = input("Enter the file name: ")
engine = pyttsx3.init()
with open(filename, "r") as file:
    hex_data = file.read().strip()

try:
    text = bytes.fromhex(hex_data).decode("utf-8")
    engine.say("Decoded text is " + text)
    engine.say("Result Accepted")
    engine.runAndWait()
    print("Result             : Accepted")
except Exception as e:
    print("Conversion failed! Not valid hex.")
    print("Error:", e)

    engine.say("Conversion failed. Hex is not valid.")
    engine.runAndWait()
