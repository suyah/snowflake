#1) Import the argparse library
import argparse

import os,sys

#2） Create the parser
my_parser = argparse.ArgumentParser(description='List the content of a folder')

#3) Add the arguments
my_parser.add_argument('Path', metavar='path', type=str, help='the path to list')

#4) Execute the parse_args() method
args = my_parser.parse_args() # Namespace object

input_path = args.Path

if not os.path.isdir(input_path):
    print('The path specified does not exist')
    sys.exit()

print('\n'.join(os.listdir(input_path)))

## declaring variables
name = "Datacamp"
type_of_company = "Educational"

## enclose your variable within the {} to display it's value in the output
print(f"{name} is an {type_of_company} company.")

print(name +  type_of_company +" company.")