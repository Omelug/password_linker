import argparse
import enum
from chardet.universaldetector import UniversalDetector
import sys
import codecs


__author__ = 'Omelug'
__date__ = '2024'
__description__ = ""
__external_tools__ = []

__inpired_author__ = 'Matt Weir'
__inpired_src__ = "https://github.com/lakiw/Password_Research_Tools"


class CrackingSession:
    def __init__(self):
        self.passwords = {}
        self.num_passwords = 0
        self.num_cracked = 0
        self.num_guesses = 0

def get_args(args):
 
    parser = argparse.ArgumentParser(description='Used to test the effectiveness of a password cracking session against a known set of plaintext passwords')

    #TODO kvuli detekci to asi nemuze byt ted stdin, dodelat
    parser.add_argument('--in_file','-if', help='The set of passwords to use as a target',metavar='TARGET_SET',required=True)
    parser.add_argument('--guess_file',required=True, default=None)
    parser.add_argument('--out_file',"-o", help='Filename to save the results to. Default is to output to stdout',metavar='OUTPUTFILE_NAME',required=False,default=None)

    parser.add_argument('--max_guesses','-m', help='If specified, limits the number of guesses to what is specified',metavar='MAX_GUESSES',type=int,required=False,default=None)
    parser.add_argument('--start_count','-s', help='Used to continue a previous cracking session. Aka just starts with *count* number of guesses already',metavar='NUM_GUESSS',type=int,required=False,default=0)
    parser.add_argument('--start_cracked','-c', help='Used to continue a previous cracking session. Aka just starts with *cracked* number of passwords already',metavar='NUM_CRACKED',type=int,required=False,default=0)
    parser.add_argument('--uncracked_file','-u', help='Save all uncracked passwords at the end of the session to file',metavar='SAVEFILE',required=False,default=None)
    parser.add_argument('--encoding','-e', help='Encoding format of th training file', metavar='ENCODING', required=False, default=None)
    parser.add_argument('--verbose','-v', help='Prints debugging messages', required=False, action="store_true")

    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args



# pip install chardet
# You can also get it from https://github.com/chardet/chardet
def detect_file_encoding(training_file, file_encoding, max_passwords=10000):
    detector = UniversalDetector()
    try:
        with open(training_file, 'rb') as file:
            for cur_count, line in enumerate(file, 1):
                detector.feed(line)
                if detector.done or cur_count >= max_passwords:
                    break
            detector.close()
    except IOError as error:
        print(f"Error opening file {training_file}\nError is {error}", file=sys.stderr)
        return RetType.FILE_IO_ERROR

    try:
        file_encoding.append(detector.result['encoding'])
        print(f"Input encoding Detected: {detector.result['encoding']}\n"
              f"Confidence: {detector.result['confidence']}", file=sys.stderr)
    except KeyError as error:
        print(f"Error encountered with file encoding autodetection\n"
              f"Error: {error}", file=sys.stderr)
        return RetType.ENCODING_ERROR

    return RetType.STATUS_OK


# Reads in all of the passwords and returns the raw passwords, (minus any POT formatting to master_password_list
# Format of the raw passwords is (password,"DATA" or "COMMENT")
def read_input_passwords(training_file, cs, file_encoding='utf-8'):
    ret_value = RetType.STATUS_OK
    try:
        with codecs.open(training_file, 'r', encoding=file_encoding, errors='surrogateescape') as file:
            num_encoding_errors = 0

            for password in file:
                try:
                    password.encode(file_encoding)
                except UnicodeEncodeError as e:
                    if e.reason == 'surrogates not allowed':
                        num_encoding_errors = num_encoding_errors + 1
                    else:
                        print(f"Hmm, there was a weird problem reading line  {password} from the training file",
                              file=sys.stderr)
                    continue

                # save the password
                cs.num_passwords = cs.num_passwords + 1
                clean_password = password.rstrip()
                # If the password has already been read in, (aka multiple people used the same password), increment the count
                if clean_password in cs.passwords:
                    cs.passwords[clean_password][0] = cs.passwords[clean_password][0] + 1
                ## Otherwise insert the password into the list if it is the first time it has been seen
                else:
                    ## The values of cs.passwords are (Password_String: [Number_of_Passwords, isCracked, Number_Of_Guesses_To_Crack])
                    cs.passwords[clean_password] = [1, False, -1]

            if num_encoding_errors != 0:
                print(f"WARNING: {num_encoding_errors} passwords in the training set did not decode properly",
                      file=sys.stderr)
                print("Ignoring passwords that contained encoding errors so it does not skew the results",
                      file=sys.stderr)
                print(
                    "If you see a lot of these errors then you may want to re-run the training with a different file encoding",
                    file=sys.stderr)

    except IOError as error:
        print(error, file=sys.stderr)
        print(f"Error opening file {training_file}", file=sys.stderr)
        return RetType.FILE_IO_ERROR

    return ret_value


def write_uncracked_to_disk(cs, uncracked_file, file_encoding="UTF-8"):
    try:
        with codecs.open(uncracked_file, 'w', encoding=file_encoding) as file:
            for password, result in cs.passwords.items():
                if not result[1]:
                    file.write((password + "\n") * result[0])
    except Exception as error:
        print(f'Error opening the uncracked file. Error: {error}', file=sys.stderr)

@enum.unique
class RetType(enum.IntEnum):
    STATUS_OK = 0  # Everything worked as expected
    COMMAND_LINE_ERROR = 1  # Error parsing the command line
    FILE_IO_ERROR = 2  # Error reading or writeing a file
    NOT_ENOUGH_TRAINING_PASSWORDS = 5  # Not enough passwords in the training file
    BAD_INPUT = 6  # Bad input to the program
    ENCODING_ERROR = 7  # File encoding error
    DEBUG = 8  # Debug results
    GENERIC_ERROR = 98  # Generic error
    QUIT = 99  # Program should shut down
    ERROR_QUIT = 100  # Program should shut down due to error



def test_cracking_session(cs, encoding = "UTF-8",
                          start_count = 0, start_cracked = 0, max_guesses = None,
                          guess_file = None,out_file = None, verbose = False):

    ##--Initialize the session--##
    cs.num_guesses = start_count
    cs.num_cracked = start_cracked
    cs.num_passwords = cs.num_passwords + start_cracked

    output_file = open(out_file, 'w') if out_file else sys.stdout

    ## I only want to print out 1000 items + the last count to make graphing easier
    step_size = int(cs.num_passwords * 0.001)
    if step_size == 0:
        step_size = 1

    cur_step_limit = step_size

    num_input_errors = 0
    print(f'{cs.num_guesses}\t{cs.num_cracked}', file=output_file)

    with open(guess_file, 'rb') as file:
        try:
            for i, guess in enumerate(file.readlines()):

                cs.num_guesses = cs.num_guesses + 1

                try:
                    guess = guess.decode(encoding).rstrip()
                ##--Handle errors parsing input guesses
                except:
                    num_input_errors = num_input_errors + 1
                    if verbose:
                        print(f"error decoding input guess. Total number of errors = {num_input_errors}", file=sys.stderr)
                    else:
                        if num_input_errors == 10000:
                            print("***Warning***", file=sys.stderr)
                            print("10,000 errors have occured while processing the input", file=sys.stderr)
                            print("Your results may be unreliable", file=sys.stderr)
                    continue

                ## If it is a match
                if guess in cs.passwords and cs.passwords[guess][1] == False:
                    cs.passwords[guess][1] = True
                    cs.passwords[guess][2] = cs.num_guesses
                    cs.num_cracked = cs.num_cracked + cs.passwords[guess][0]
                    if cs.num_cracked >= cur_step_limit:
                        print(f"{cs.num_guesses}\t{cs.num_cracked}\t", file=output_file)
                        cur_step_limit = step_size + cur_step_limit

                    #If all passwords have been cracked, exit
                    if cs.num_cracked >= cs.num_passwords:
                        break

                ##--If we have made all the maximum number of guesses
                if max_guesses is not None and (cs.num_guesses >= max_guesses):
                    break
                # guess = sys.stdin.buffer.readline()
        except Exception as error:
            print(f"halting due to :{error}", file=sys.stderr)
    ##--Do final cleanup and printout for this cracking session
    print(f"{cs.num_guesses}\t{cs.num_cracked}", file=output_file)

    return RetType.STATUS_OK

def run(args, config=None):
    cs = CrackingSession()
    args = get_args(args)

    #inpyut encoding detection
    if args.encoding is None:
        possible_encodings = []
        if detect_file_encoding(args.in_file, possible_encodings) != RetType.STATUS_OK:
            print("Error detecting file encoding ", file=sys.stderr)
            return
    else:
        possible_encodings = [args.encoding]
    encoding=possible_encodings[0]

    # parse in_file
    if read_input_passwords(args.in_file, cs, file_encoding=encoding) != RetType.STATUS_OK:
        print('Error reading in target file. Exiting', file=sys.stderr)
        return

    print(f"Done parsing input, {cs.num_passwords} passwords to crack", file=sys.stderr)
    test_cracking_session(cs,
                          encoding=encoding,
                          start_count=args.start_count,
                          start_cracked=args.start_cracked,
                          max_guesses=args.max_guesses,
                          out_file=args.out_file,
                          guess_file=args.guess_file,
                          verbose = args.verbose)

    if args.uncracked_file is not None:
        write_uncracked_to_disk(cs, args.uncracked_file, file_encoding=encoding)