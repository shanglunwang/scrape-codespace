print ("Input Start Index")

startIndex = input()

print ("Input Last Index")
lastIndex = input()

datas = ['start_url']

for i in range(int(startIndex), int(lastIndex) + 1):
    datas.append(f"https://stackoverflow.com/users/{i}")
    # datas.append("https://meta.stackexchange.com/users/" + str(i) )

with open("StartupUrl.csv", 'w') as file:
    file.writelines("%s\n" % data for data in datas)