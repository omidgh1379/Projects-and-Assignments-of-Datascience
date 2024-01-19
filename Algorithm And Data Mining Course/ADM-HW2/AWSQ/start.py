import json
import time
import pandas as pd
start_time = time.time()
counter=0
file_path="list.json"
main_dictionary=dict()

with open(file_path, "r") as file:
    for line in file:
        data = json.loads(line)
        if "tags" in data:
            for element in data["tags"]:
                if element not in main_dictionary:
                    main_dictionary[element]=1
                else:
                    main_dictionary[element]+=1




sorted_keys = sorted(main_dictionary, key=lambda k: main_dictionary[k], reverse=True)[:5]
arraynames=[]
arraynum=[]
for data in sorted_keys:
    arraynames.append(data)
    arraynum.append(main_dictionary[data])
data = {"tag": arraynames,
        "#usage": arraynum}
df = pd.DataFrame(data)
print(df)
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print(elapsed_time)
