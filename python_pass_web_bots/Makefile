
run:
	 cd nohide_space && python3 ./main.py --check --postit --download && cd ..
run_check:
	 cd nohide_space && python3 ./main.py --check && cd ..
run_download:
	 cd nohide_space && python3 ./main.py --download && cd ..
testq:
	 cd tests && pytest -rAq --tb=no ./unit_test.py && cd ..
nospace-download:
	 cd nohide_space && python3 ./main.py --download && cd ..

test: FORCE
	cd tests && pytest -rAq ./unit_test.py && cd ..
clean:
	cd nohide_space && rm options.json posts.txt links.txt combo_links.txt && cd ..
pack:
	zip *
FORCE: ;

install:
	pip3 install requirements.txt