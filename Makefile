#TODO zakladni linkovani listu



install:
	apt install python3
	apt install python3-pip
	pip3 install -r requirements.txt #TODO pridat python knihovny potřebne pro telegram bota
	#TODO zkontrolovat, ze se vytvori output slozky
venv: #FIXME zkontrolovat venv na stáhnutí vsech zacislosti
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