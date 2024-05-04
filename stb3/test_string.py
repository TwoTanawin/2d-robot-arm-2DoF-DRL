model_path = "/home/two-asus/Documents/ait/drl/2d-robot-arm-2DoF-DRL/stb3/report/A2C_MLP_Robot2DoF/model/100000.zip"


text = model_path.split("/")

last_text = text[-1].split(".")

print(text)
print(last_text[0])