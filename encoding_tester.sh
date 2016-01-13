#!/bin/bash
#TESTS THE ENCODING FUNCTION

if [ "$#" -ne 2 ]; then #checks parameters
    echo "Illegal number of parameters. Expected 2 parameters (PATH_TO_PYTHON_CODE/ and PATH_TO_TESTS/tests/)"
	exit
fi

ln -s $1/mtfcoding.py mtfencode.py  &>/dev/null 

#array holding the possible numbers for the tests
declare -a numbers=("00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19")

# loop to use each element in array
for i in "${numbers[@]}"
do
	cat $2/test$i.txt > t$i.txt #create a new .txt file with the contents of the actual test txt file

if [ $? -eq 0 ]; then
	output=$($1/mtfencode.py t$i.txt) #runs the program
	if [ $? -eq 0 ]; then #notifies the user of what happened
    	echo Program ran with no problems.
		output=$(diff t$i.mtf $2/test$i.mtf) #diffs the expected test result and the current test result and gathers output 
		if [ $? -eq 0 ]; then #indicates status of test cases
			echo Test Case $i PASSED 
		else
			echo Test Case $i FAILED
			echo $output
		fi  
	else #indicates errors
    	echo Program error.
		echo output
	fi
	#removes files that were created
	if [ -f t$i.txt ]; then
    	rm t$i.txt
	fi

	if [ -f t$i.mtf ]; then
    	rm t$i.mtf
	fi
else
echo The test file for Test Case $i could not be found. 
fi
done




