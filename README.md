<!--lint disable list-item-indent-->

# usbstick_masscopy
Linux python tool to mass copy data to USB sticks in an mostly automated way

## Installation / Setup
- install additional packages  
`$ sudo apt install pmount`
- clone or download this repository  
`$ git clone https://github.com/s-light/usbstick_masscopy.git`
- navigate to newly created directory  
`$ cd usbstick_masscopy`
- setup an virtual environment  
`$ python3 -m venv masscopy-env`
- activate virtual environment  
`$ source masscopy-env/bin/activate`
- setup python packages  
`(masscopy-env) $ pip3 install -r pip_requirements.txt`

## Usage
- start main script with the source folder  
`sudo python ./ustick_copy.py --source="~/mysource/folder"`
- now there should open up your default browser with an information page  
- on this page you can check/setup your USB-port mapping
- now you can switch to copy mode
- if you now insert an USB stick in on of the mapped ports
  the tool will copy all data from the source folder onto the stick
- if done it will show up as finished in the web-page
