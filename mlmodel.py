import pickle
import os

path = r"G:\My Drive\TradePilot_Final\models_gld.pkl"

print("PATH:", path)
print("EXISTS:", os.path.exists(path))
print("SIZE:", os.path.getsize(path))

with open(path, "rb") as file:
    first = file.read(20)
    print("HEADER:", first)

with open(path, "rb") as file:
    data = pickle.load(file)

print(type(data))