#!/opt/bin/python3

import sys
import binascii
import re

#functions related to the encode functionality

def write_magic_numbers(mtf):
	"""Function used to write the magic numbers to the mtf file """
	xx = bytearray() #byte array used to write the values to the file
	#appends the magic numbers to the array
	xx.append(0xfa)
	xx.append(0xce)
	xx.append(0xfa)
	xx.append(0xdf)
	#writes the magic numbers to the file
	mtf.write(xx)

def verify_argument_is_text_file(file_name):
	"""Function verifies that the input file has the .txt termination """
	matchobj = re.search('.txt$', file_name)
	if not matchobj:
		print("Wrong format of file given. Expected .txt.")
		sys.exit()  

def verify_string_has_new_line(word):
	"""Function returns true if the parameter contains the new line character """
	if "\n" in word:
		return True
	return False

def if_word_is_in_list_move_it_forward(word, list_of_words):
	"""Function checks the index of the occurrence of the word (if it is on the list) and returns the index. also it moves the element to the front """
	index = list_of_words.index(word)
	list_of_words = [list_of_words[index]] + list_of_words[0:index] + list_of_words[(index+1):] #code to move the matching word to the front of the list
	return index, list_of_words

def write_to_mtf_file(mtf, thing_to_write, number_of_words):
	"""Function to write strings or ints to mtf file """
	if isinstance(thing_to_write, int): #if the thing to write is an int
		if(thing_to_write <= 120 and thing_to_write >= 0): #low codes
			mtf.write(chr(thing_to_write+128).encode("latin-1"))
		elif(thing_to_write >= 121 and thing_to_write <= 375): #higher codes
			mtf.write(chr(249).encode("latin-1"))
			mtf.write(chr(thing_to_write - 121).encode("latin-1"))
		elif(thing_to_write >= 376 and thing_to_write <= 65912): #highest codes
			mtf.write(chr(250).encode("latin-1"))
			mtf.write(chr((thing_to_write-376) // 256).encode("latin-1"))
			mtf.write(chr((thing_to_write-376) % 256).encode("latin-1"))
	else:
		mtf.write(bytes(thing_to_write.encode("latin-1"))) #if it is not an int

def encode(names):
	"""Code to encode multiple files """
	if isinstance(names, list):
		for txt_name in names: 
			start_encoding(txt_name)
	else:
		start_encoding(names)

def start_encoding(txt_name):
	"""Program flow for the encode functionality """
	verify_argument_is_text_file(txt_name) #program verifies that the file determined by the user is of the right format
	mtf_name = txt_name.replace("txt", "mtf") #changes .txt for .mtf to get the mtf file name

	try:
		txt_file = open(txt_name, "r") #opens txt file
		mtf_file = open(mtf_name, "wb") #opens mtf file

	except (OSError, IOError) as e:
		print(str(e))
		sys.exit()

	write_magic_numbers(mtf_file) #writes magic numbers to mtf file

	all_words = [] #declares list to hold all the words in the text file
	total_number_of_words = 0 #keeps track of how many words are in the all_words list

	for input_line in txt_file: #loop to read all the lines in the text file
		#initializes the variables for the current iteration
		has_new_line = False
		words_in_line = input_line.split(" ") #gets the individual words from the input line
		words_are_the_same = False
		code = 0 #variable that holds value that will be written to file

		for current_word in words_in_line: #loop that iterates for each one of the words in the input line			
			has_new_line = verify_string_has_new_line(current_word) #check to see if word has new_line
			if has_new_line:
				current_word = current_word.replace("\n", "") #take out the new line from word
						
			try: #block will only finish executing if the word exists in the list
				word_index, all_words = if_word_is_in_list_move_it_forward(current_word, all_words) #checks to see if the current word exists in list of words and if it does it moves it forward
				code = word_index + 1 #value for the file is the index plus 128 (for encoding) + 1 to start count from 1
				words_are_the_same = True #set value of flag
			
			except ValueError:
				words_are_the_same = False

			len_of_current_word = len(current_word)

			if words_are_the_same == False and len_of_current_word > 0: #if the word was not found in the list, add it to the list
				all_words.insert(0, current_word)
				total_number_of_words += 1
				code = total_number_of_words

			if (has_new_line == True and len_of_current_word > 0) or (has_new_line == False): #write the encoded value to the mtf file
				write_to_mtf_file(mtf_file, code, total_number_of_words)

			if words_are_the_same == False: #write the word that was encoded to the mtf  file
				write_to_mtf_file(mtf_file, current_word, total_number_of_words)

			if has_new_line == True: #add the new line character if the word had a new line character
				write_to_mtf_file(mtf_file, "\n", total_number_of_words)
							
	mtf_file.close()
	txt_file.close()

#functions related to the decode functionality
def verify_argument_is_mtf_file(file_name):
	"""Function verifies that the input file has the .mtf termination """
	matchobj = re.search('.mtf$', file_name)
	if not matchobj:
		print("Wrong format of file given. Expected .mtf.")
		sys.exit()

def verify_magic_numbers_exist_in_mtf_file(mtf):
	"""Function to check that the first bytes of the mtf file are the magic numbers"""
	magic_numbers1 = ["0xfa", "0xce", "0xfa"]
	for number in  magic_numbers1:
		byte = mtf.read(1)
		if str(hex(int.from_bytes(byte, "big"))) != number:
			print("Error: Could not find the magic number: "+number+" in the file.")	
			sys.exit()

	byte = mtf.read(1)
	final_byte = str(hex(int.from_bytes(byte, "big")))
	if final_byte != "0xde" and final_byte != "0xdf":
		print("Error: Could not find the final magic number 0xde or 0xdf")    
		sys.exit()


def if_byte_equals_new_line_write_to_file(byte, txt):
	"""This function checks to see if the current byte is a new line. If it is, it writes it to the txt file"""
	if byte.decode("ISO-8859-1") == "\n":
		txt.write("\n")

def handle_repeated_word(int_of_byte, byte, txt, words, mtf):
	"""This function grabs the repeated word, writes it to the file txt, and moves to the next byte in mtf file """
	index = int_of_byte #code has already been figured out
	byte = mtf.read(1) #move to next byte
	word_to_write = words[index] #determine that the word to write is the one at the given index
	
	if byte.decode("ISO-8859-1") != "\n": #if the byte (the one after the current word) is not an end of line, add space
		word_to_write += " "
	txt.write(word_to_write)
	return byte, index

def add_new_word_to_list_and_write_to_file(word, list_of_words, txt):
	"""This function takes care of adding the new words to the list and writing the word to the file. """
	copy_of_new_word = word #creates local copy of the word to be added to the list
	copy_of_word = word.replace("\n", "") #takes out the new line so that the word in the list doesn't have it
	list_of_words.insert(0, copy_of_word) #adds word to the list

	if "\n" not in word: #adds a space if the word doesn't have a new line
		word += " "

	txt.write(word) #writes word to file

def decode(names):
	"""Code to decode multiple files (if given) """
	if isinstance(names, list):
		for mtf_name in names: 
			start_decoding(mtf_name)
	else:
		start_decoding(names)
	
def start_decoding(mtf_name):
	"""Program flow for the decode functionality """
	verify_argument_is_mtf_file(mtf_name) #verifies that the file given by the user has the .mtf extension

	txt_name = mtf_name.replace("mtf","txt") #replaces mtf with txt to get the .txt file name

	try:
		txt_file = open(txt_name, "w") #opens txt file
		mtf_file = open(mtf_name, "rb") #opens mtf file
	
	except (OSError, IOError) as e: #error handling for files
		print(str(e))
		sys.exit()
		 
	verify_magic_numbers_exist_in_mtf_file(mtf_file) #call to method that checks that the magic numbers exist in the mtf file
	
	current_byte = mtf_file.read(1)	#reads the first byte
	all_words = [] #list that will hold the built words
	list_of_ints = [] #list that will hold the found encoding numbers

	while current_byte != b"": #while it isn't the end of the file...
		int_of_current_byte = int.from_bytes(current_byte, "big") #get the integer representation of the file
				
		if int_of_current_byte >= 128 and int_of_current_byte <= 248: #if the byte is a coding number
			int_of_current_byte -= 129
			if int_of_current_byte not in list_of_ints: #the int is seen for the first time

				list_of_ints.append(int_of_current_byte) #save the int value
				wh = Word_Handler(current_byte, int_of_current_byte, all_words, txt_file, mtf_file) #instantiates class to create next word from the input bytes
				current_byte, int_of_current_byte, all_words, txt_file, mtf_file = wh.create_next_word() #updates the variables

			else: #if the coding value is repeated
				current_byte, index = handle_repeated_word(int_of_current_byte, current_byte, txt_file, all_words, mtf_file) #find the word and write it to the file
				all_words = [all_words[index]] + all_words[0:index] + all_words[(index+1):] #move word to front

		elif(int_of_current_byte == 249):
			current_byte = mtf_file.read(1) #read next byte
			int_of_current_byte = int.from_bytes(current_byte, "big") +121 - 1 #get integer representation
			
			if int_of_current_byte not in list_of_ints: #the int is seen for the first time

				list_of_ints.append(int_of_current_byte) #save the int value
				wh = Word_Handler(current_byte, int_of_current_byte, all_words, txt_file, mtf_file)  #instantiates class to create next word from the input bytes
				current_byte, int_of_current_byte, all_words, txt_file, mtf_file = wh.create_next_word() #updates the variables

			else: #if the coding value is repeated
				current_byte, index = handle_repeated_word(int_of_current_byte, current_byte, txt_file, all_words, mtf_file) #find the word and write it to the file
				all_words = [all_words[index]] + all_words[0:index] + all_words[(index+1):] #move word to front	
	

		elif(int_of_current_byte == 250):
			current_byte = mtf_file.read(1) #read next byte
			int_of_current_byte = int.from_bytes(current_byte, "big") #get integer representation
		
			quotient = int_of_current_byte

			current_byte = mtf_file.read(1) #read next byte
			int_of_current_byte = int.from_bytes(current_byte, "big") #get integer representation

			remainder = int_of_current_byte

			int_of_current_byte = 256*quotient + remainder + 376 - 1
		
			if int_of_current_byte not in list_of_ints: #the int is seen for the first time

				list_of_ints.append(int_of_current_byte) #save the int value
				wh = Word_Handler(current_byte, int_of_current_byte, all_words, txt_file, mtf_file)  #instantiates class to create next word from the input bytes
				current_byte, int_of_current_byte, all_words, txt_file, mtf_file = wh.create_next_word() #updates the variables

			else: #if the coding value is repeated
				current_byte, index = handle_repeated_word(int_of_current_byte, current_byte, txt_file, all_words, mtf_file) #find the word and write it to the file
				all_words = [all_words[index]] + all_words[0:index] + all_words[(index+1):] #move word to front
		else:
			if_byte_equals_new_line_write_to_file(current_byte, txt_file) #if a new line is found, write it to the txt file
			current_byte = mtf_file.read(1)
	#close both files
	txt_file.close()
	mtf_file.close()	

class Word_Handler: 
	"""Class that takes care of building words from the bytes from the file stream"""

	def __init__(self, current_byte, int_of_current_byte, all_words, txt_file, mtf_file):
		"""Method that takes care of saving the arguments as variables inside the object"""
		self.byte = current_byte
		self.byte_int = int_of_current_byte
		self.words = all_words
		self.txt = txt_file
		self.mtf = mtf_file
	
	def create_next_word(self):
		"""Method that creates the next word from the file stream"""
		new_word = "" #string used to buid the word from the next bytes             

		while True:
			self.byte = self.mtf.read(1) #read next byte
			self.byte_int = int.from_bytes(self.byte, "big") #get integer representation

			if self.byte_int < 128 and self.byte != b"": #next byte is not a coding number and the byte is not NULL
				new_word += self.byte.decode("ISO-8859-1") #add the next character to the word

			else:
				add_new_word_to_list_and_write_to_file(new_word, self.words, self.txt) #add the finished word to the list of words
				break

		return self.byte, self.byte_int, self.words, self.txt, self.mtf #returns the modified variables
	












