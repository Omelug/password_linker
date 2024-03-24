import sqlite3
import argparse
import yaml
import os
import csv
import shutil
import coloredlogs
import logging

valid_formats = [".sql", ".txt", ".csv"]
def valid_format(format, print_error=False):
    if format in valid_formats:
        return True
    if print_error:
        print(f"Error: Invalid output format '{format}'. Valid formats are: {', '.join(valid_formats)}")
        exit(1)
    return False

def valid_file(file_path, print_error=False):
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        base_name, file_format = os.path.splitext(file_name)

        if file_format in valid_formats:
            return base_name, file_format
        if print_error:
            print(f"Error: Unsupported format '{file_format}' for input file '{file_path}'. Valid formats are: {', '.join(valid_formats)}")
            exit(1)
    else:
        if print_error:
            print(f"Error: Input file '{file_path}' does not exist.")
            exit(1)
    return None, None


def convert_txt_csv_to_txt_csv(input_file, output_file, input_separator, output_separator):
    with open(input_file, 'r') as file1, open(output_file, 'w', newline='') as file2:
        file_reader = csv.reader(file1, delimiter=input_separator)
        file_writer = csv.writer(file2, delimiter=output_separator)
        for row in file_reader:
            file_writer.writerow(row)


def convert_txt_csv_to_sql(input_file, output_file, input_separator):
    db = sqlite3.connect(output_file)
    cursor = db.cursor()

    base_name = os.path.basename(input_file)
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=input_separator)

        header = next(csv_reader)
        create_table_query = f'CREATE TABLE IF NOT EXISTS {base_name} (\n'
        for column_name in header:
            create_table_query += f'    {column_name} TEXT,\n'
        create_table_query = create_table_query.rstrip(',\n')  # Remove the trailing comma and newline
        create_table_query += '\n)'
        cursor.execute(create_table_query)

        for row in csv_reader:
            insert_query = f"INSERT INTO {base_name} VALUES (?, ?, ...)"
            cursor.execute(insert_query, row)
    db.commit()
    db.close()


def resource_name_correction(resource):
    base_name = os.path.basename(resource)
    #TODO change czech weird chars, empty chars etc.
    new_name = os.path.basename(resource)
    return base_name, new_name
logger = logging.getLogger('my_logger')
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="HELP!")
    a = parser.add_argument("-s", "--start", action="store_true", help="Run script defined in the file")
    parser.add_argument("-r", "--run", action="store_true", help="Run script defined in the file")
    parser.add_argument("-rt_pwd", "--reset_pwd_db", action="store_true", help="Database creation/reset")
    parser.add_argument("-rt_out", "--reset_output", action="store_true", help="Reset output")
    parser.add_argument("-rt_in", "--reset_input", action="store_true", help="Reset input")
    parser.add_argument("-c", "--convert", nargs="+", help="Convert resource file to different format")
    parser.add_argument("-add_r", "--add_resource", nargs=1, help="Add resource to program")

    #import data from deferrent location of this program
    parser.add_argument("-im_in", "--import_input", action="store_true", help="Import input folder")
    parser.add_argument("-im_out", "--import_output", action="store_true", help="Import output folder")
    parser.add_argument("-im_pwd", "--import_pwd_db", action="store_true", help="Import password database")

    args = parser.parse_args()

    with open("config.yaml", 'r+') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("Error loading config", file.name)
            print(exc)
    psw_db_name = config['name_config']['password_database']

    if args.reset_pwd_db:
        db = sqlite3.connect(psw_db_name)
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS password(plain)")
        db.commit()
        db.close()

    if args.convert:
        if len(args.options) >= 2:
            input_file, out_format, separator1, separator2 = args.convert
            in_name, in_format = valid_file(input_file, True)
            if valid_format(out_format, True) and in_format is not None:
                logger.info(f"Converting  {input_file} to {config['name_config']['input_folder']}/{in_name+out_format}")

                output_file = config['name_config']['input_folder'] + "/"+in_name+out_format

                if (in_format == ".txt" or in_format == ".csv") and (out_format == ".txt" or out_format == ".csv"):
                    convert_txt_csv_to_txt_csv(input_file, output_file,separator1, separator2)
                if (in_format == ".txt" or in_format == ".csv") and out_format == ".sql":
                    if(len(args.options) >= 3):
                        logger.error('''f"For txt or csv convert is there too many arguments'\n"
                            Use --convert <input_file> .sql <input_separator> 
                            ''')
                        exit(1)
                    convert_txt_csv_to_sql(input_file, output_file, separator1)
        else:
            logger.error("Error: At least 2 options are required.")
            exit(1)

    if args.add_resource:
        resource = args.add_resource[0]
        if os.path.exists(resource):
            old_name, rsc_name = resource_name_correction(resource)
            if old_name != rsc_name:
                logger.info(f"Resource named {old_name} will be saved like {rsc_name}")
            no_extension = os.path.splitext(rsc_name)[0]
            rsc_folder = f"{config['name_config']['input_folder']}/rsc/{no_extension}/original"

            if not os.path.exists(rsc_folder):
                os.makedirs(rsc_folder)
            shutil.move(resource, rsc_folder)
            os.chmod(rsc_folder + "/" + rsc_name, 0o666)
        else:
            logger.error(f"The file {resource} does not exist.")
'''
        ##cur.execute("CREATE TABLE IF NOT EXISTS person(uzivatel,emails,phone_numbers,json_info,description)")
        ##cur.execute("CREATE TABLE IF NOT EXISTS resource(date, name, link,used_tool, hash_algorithms, database_type, json_info, description)")
        #cur.execute("CREATE TABLE IF NOT EXISTS password(plain)")
        ##cur.execute("CREATE TABLE IF NOT EXISTS account(nickname_id, link, json_info, description)")

    with open('import/import_csv/import_csv.yaml', 'r') as file:
        prime_service = yaml.safe_load(file)
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        #cur.execute(" IF NOT EXISTS person(uzivatel,emails,phone_numbers,json_info,description)")

    with open('../res/for_database/uzivatele.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))
    with open('uzivatele.txt', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        uzivatel = [row['heslo'] for row in csv_reader]

    with open('uzivatel.txt', mode='w') as txt_file:
        for name in uzivatel:
            txt_file.write(name.replace('(', ':').replace(')', '').replace(" ", "") + '\n')
'''