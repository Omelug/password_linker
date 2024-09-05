CZ
________________________________________________________________________________
linker_test.py spustí všechny testy pro všechny scripty

Založení nového testu:
1. Vytvořit nový soubor v test/scripts/<jméno_scriptu>(nebo cokoliv)/test<číslo_testu>_<název_testu>
2. OPTIONAL - create result.json file in the same directory, it update default config:
    RESULT_JSON = {
        "output":"output.txt",
        "command":"command.txt",
        "result":"result.txt",
        "data":"data",
        "cmd_prefix":"find"
    }
3. Změnit toto:
    data - složka s daty pro test (find je pošle na stdin)
    output - referenční výstup
    command - příkaz, který se spustí
    cmd_prefix - typ vstupů pro stdin
        find -> vstup je seznam souborů v data

    result - výstup testu

Spuštění:
    make run_test v ./test