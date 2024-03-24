#!/bin/bash

sqlite3 ../../rsc/hashpass.db "select password from pass_hash" > "pass_from_DB.txt"

