<!--lint disable list-item-indent-->

# usbstick_masscopy
Linux python tool to mass copy data to USB sticks in an mostly automated way

## Installation / Setup
<!-- - install additional packages  
`$ sudo apt install pmount` -->
- clone or download this repository  
`$ git clone https://github.com/s-light/usbstick_masscopy.git`
- navigate to newly created directory  
`$ cd usbstick_masscopy`
- setup an virtual environment  
`$ python3 -m venv env`
- activate virtual environment  
`$ source env/bin/activate`
- setup python packages  
`(masscopy-env) $ pip3 install -r pip_requirements.txt`

## Usage
- start main script with the source folder  
`sudo ./ustick_copy.py --interactive --source="~/mysource/folder"`
- now there is a interactive menu shown (every command is done on 'enter'-key)
- first you can start the mapping process with 'map'
- now use on usb-stick to put in every usb-port you want to use later - do this in the order you want them to be assigned. its best to first use some tape and write the numbers on the ports - and than do the mapping
- to stop the mapping process use the 'done' command
- there is an table shown with all mappings.
- now you can start the copy process with 'start'
- if you now insert an USB stick in on of the mapped ports
  the tool will
  - rename the stick to the label defined in the 'config.json' file
  - mount the stick
  - copy all files from the source folder onto the stick
  - unmount the stick
- if done it will show up as 'done' in the port-status row
- to exit the programm just use 'q' (and as with every command run it with 'enter'-key)
