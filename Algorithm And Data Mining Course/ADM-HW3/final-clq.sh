#!/bin/bash
grep -i 'part-time' merged_courses.tsv |  wc -l > part_time_colleges_count.txt
echo " Print the number of part time education "
cat part_time_colleges_count.txt
#----------------------
total_courses=$(wc -l < merged_courses.tsv)
engineering_courses=$(grep -i 'Engineer' merged_courses.tsv | wc -l)
echo "Total Courses: $total_courses"
echo "Engineering Courses: $engineering_courses"
percentage=$(echo "scale=2; ($engineering_courses / $total_courses) * 100" | bc)
echo "Percentage: $percentage"
echo $percentage > engineering_percentage.txt
#-----------------------------------------------------
# Load the CSV data into a temporary table
sqlite3 tmp.db <<EOF
.mode csv
.import file.csv courses
EOF
# Get country and city count for MS degrees
RESULTS=$(sqlite3 tmp.db "
SELECT administration, city, COUNT(*) AS num_ms
FROM courses
WHERE modality LIKE '%MSc%'
GROUP BY administration, city
ORDER BY num_ms DESC
LIMIT 1;
")
# Print out the top country, city for MS degrees
echo "Country and city with the most MS degrees:"
echo "$RESULTS"
# Clean up temporary database
rm tmp.db
chmod +x analysis.sh