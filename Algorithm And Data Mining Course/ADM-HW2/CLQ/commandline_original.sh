
declare -A myDict
counter=0
file_to_read="series.json"
sortedArray=""
while IFS= read -r line; do
	start_index_id=$(echo "$line" | grep -b -o '"id": "' | cut -d: -f1 | head -n 1)
	end_index_id=$(echo "$line" | grep -b -o '", "title": "' | cut -d: -f1 | head -n 1)
	substring_id=$(echo "$line" | cut -c $((start_index_id+8))-$((end_index_id)))
	start_index_title=$(echo "$line" | grep -b -o '"title": "' | cut -d: -f1 | head -n 1)
	end_index_title=$(echo "$line" | grep -b -o '", "description"' | cut -d: -f1 | head -n 1)
	title_name=$(echo "$line" | cut -c $((start_index_title+11))-$((end_index_title)))
	start_index=$(echo "$line" | grep -b -o '"books_count": "' | cut -d: -f1) #    "works": \[
	if [ -n "$start_index" ]; then
	    	IFS=$'\n' read -d '' -ra start_index <<< "$start_index"
		end_index=$(echo "$line" | grep -b -o '"}' | cut -d: -f1)
		if [ -n "$end_index" ]; then
			IFS=$'\n' read -d '' -ra end_index <<< "$end_index"
			arrayLength=${#start_index[@]}
			tbc=0
			for ((index = 0; index < arrayLength; index++))
			do
			    start_i="${start_index[index]}"
			    end_i="${end_index[index]}"
			    substring=$(echo "$line" | cut -c $((start_i + 17))-$((end_i)))
			    substring=$((substring))
			    tbc=$((tbc+substring))
			   
			done
			myDict[$title_name]=$tbc
			sortedArray+="$substring_id "$title_name" $tbc\n"
		fi
	fi
	((counter += 1))
	if [ $((counter % 100)) -eq 0 ]; then
    		echo "$counter"
    	fi    
done < $file_to_read

sortedArray=$(echo -e $sortedArray)
sortedArray=$(awk '{print $NF, $0}' <<< $sortedArray | sort -rn | cut -d' ' -f2-| head -n 5)
IFS='?'

echo "id title total_books_count"
echo "$sortedArray"



