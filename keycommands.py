from crypto_utils import generate_key,load_key,encrypt_file,decrypt_file
#generate_key()
key = load_key()
encrypt_file("passwords.csv", key)
#decrypt_file("passwords.csv", key)
"""l=[]
for x in range(401):
    if x<10:
        l.append(f"ID00{x}:pass")
    elif x<100:
        l.append(f"ID0{x}:pass")
    elif x>=100:
        l.append(f"ID{x}:pass")

l=str(l)
l=l.replace("'","")
l=l.replace("[","")
l=l.replace("]","")
l=l.replace(" ","")
print(l)
with open('passwords.csv','w') as file:
    file.write(l)
"""