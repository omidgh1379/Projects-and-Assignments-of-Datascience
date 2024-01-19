cat vodclickstream_uk_movies_03.csv | cut -d',' -f4 | sort | uniq -c | sort -nr > title_counts.txt
#Display the most-watched title
most_watched_title=$(head -n 1 title_counts.txt)
echo "The most-watched Netflix title is: $most_watched_title"
#Provide the ID of the user that has spent the most time on Netflix
awk -F',' '{sum[$2] += $1} END {for (user in sum) print user, sum[user]}' new_vodclickstream_uk_movies_03.csv | sort  -k2,2nr | awk '{print $1 }' | head -n 1
#3
#Report the average time between subsequent clicks on Netflix.com
awk -F',' '
  NR > 1 {
    gsub("\"", "", $3)
    if ($3 + 0 == $3) {
      sum += $3
      count++
    }
  }
  END {
    if (count > 0) {
      print "Average of time_difference:", sum/count, "seconds"
    } else {
      print "No valid data for calculation."
    }
  }
' data3.csv
