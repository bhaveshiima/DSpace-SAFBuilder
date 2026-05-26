# DSpace-SAFBuilder
DSpace SAFBuilder - Bulk Import data from CSV
<br>
I have taken the reference of the https://github.com/lib-uoguelph-ca/dspace-csv-archive and modified based on my understanding to make more simplified version.

## Overview
This code takes a simple CSV spreadsheet (UTF-8), and a bunch of files and it will turns them into the DSpace Simple Archive format. This tool supports unicode characters in metadata. It will automatically strip unicode characters out of filenames. 

## Requirements
Requires [Python](https://www.python.org/) version 3.8 or greater

## Check the python version
	# python3 --version

It will show the python version installed in your system, if not showing or some error shows then you need to install Python on your system by using the following commands

#### update the list of available packages
	# sudo apt update

#### Installs Python 3 and pip (Python package manager)
	# sudo apt install -y python3 python3-pip

## After installation just check the Python version
	# python3 --version

## Some simple rules for the CSV spreadsheet
* The first row should be your header, which defines the values you're going to provide. 
* Only one column is mandatory: 'files'. Files can be organized in any way you want, just provide the proper path relative to the CSV file's location.
* Add one column for each metadata element (eg: dc.title)
* Only dublin core metadata elements are supported (for now).
* Use the fully qualified dublin core name for each element (eg dc.contributor.author).
* Languages can be specified by leaving a space after the element name and then listing the language. (eg: dc.title en)
* Separate multiple values for an element by double-pipes (||).
* If your metadata value has a comma in it, put some quotes around it. Eg: "Roses are red, violets are blue".
* The order of the columns does not matter.

## Example CSV structure 
<table>
	<tr>
		<th>files</th>
		<th>dc.title en</th>
		<th>dc.contributor.author en</th>
		<th>dc.subject</th>
		<th>dc.type</th>
	</tr>
	<tr>
		<td>file1.pdf||file2.pdf</td>
		<td>title 1</td>
		<td>author 1</td>
		<td>subject 1 || subject 3</td>
		<td>Report</td>
	</tr>
	<tr>
		<td>file3.pdf</td>
		<td>"title 2, with comma"</td>
		<td>author 2a||author 2b</td>
		<td>subject 2</td>
		<td>Article</td>
	</tr>
</table>


## cd means "change directory" — navigate to the /dspace folder
	# cd /dspace

## git clone downloads the tool from GitHub to your server
	# git clone https://github.com/bhaveshiima/DSpace-SAFBuilder.git

## Now enter to that folder
	# cd DSpace-SAFBuilder

## Create Folder (eg. bhavesh_bulkimport inside DSpace_SAFBuilder folder) 
Go to 
	# /dspace/DSpace_SAFBuilder/
Then create a folder name 'bhavesh_bulkimport' (this is the folder where you keeping your CSV + files)
	# mkdir bhavesh_bulkimport

## Copy CSV file and pdf (or other) files to 'bhavesh_bulkimport' folder
After copy execute the following command
	# cd /dspace/DSpace_SAFBuilder/bhavesh_bulkimport/
List all the files and folders
	# ls

## Usage  (go to 'bhavesh_bulkimport' folder)
now you should be 'bhavesh_bulkimport' folder in order to run the script. Make sure that data.csv file will be the CSV file so check the filename before execute the following command
	# python3 /dspace/DSPACE_SAFBuilder/dspace-csv-archive.py data.csv

After successful execution, the script will processed files and generate the Dublin Code into a directory called `SimpleArchiveFormat` inside the 'bhavesh_bulkimport' directory.




