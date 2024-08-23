#TODO zakladni linkovani listu



install:
	pip3 install git+https://github.com/Omelug/python_mini_modules.git#egg=input_parser
	apt install python3
	apt install python3-pip
	pip3 install -r requirements.txt
	#TODO zkontrolovat, ze se vytvori output slozky

venv: #FIXME zkontrolovat venv na stáhnutí vsech zavislosti
	python -m venv venv
	#source ./venv/bin/activate
	which python

passlist_test:
	python -m doctest -v passlist.py

save_requirements: #tun WITOUT SUDO !!!! (jiank se to spusti v globalnim pythonu)
	pip3 install --upgrade pip
	pip3 freeze > requirements.txt

clean_venv:
	#deactivate
	rm -rf ./venv

test_all:
	pytest -s ./lib/test/

USERNAME = root
SERVER = 45.134.226.157
DEST_DIR = /root/passwordList/TelegramChecker
FILES = ./TelegramChecker/breachdetector ./TelegramChecker/user_config.py


breachdetector_pull:
	echo "Copying files to server..."
	scp -r $(FILES) $(USERNAME)@$(SERVER):$(DEST_DIR)
	echo "Files copied successfully to $(USERNAME)@$(SERVER):$(DEST_DIR)"


DEST_DIR = /root/passwordList
FILES = ./lib
lib_pull:
	echo "Copying files to server..."
	scp -r $(FILES) $(USERNAME)@$(SERVER):$(DEST_DIR)
	echo "Files copied successfully to $(USERNAME)@$(SERVER):$(DEST_DIR)"


