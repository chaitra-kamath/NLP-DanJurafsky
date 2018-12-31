import sys
import os
import re
import pprint

enc = 'iso-8859-15'
my_first_pat = '(\w+)@(\w+).edu'

"""
TODO
This function takes in a filename along with the file object (actually
a StringIO object at submission time) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***, as it will be called directly by
the submit script

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO at submission time. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    # email_pat = '(\w+)@(\w+)'
    email_pat = '(\w+)@((?:\w+.?)+)\.[eE][Dd][Uu]'
    phone_pat = '(\d{3})-(\d{3})-(\d{4})'
    res = []
    # sys.stderr.write('current file name: %s' % name)
    for line in f:
        #replace blank spaces between username and domain
        line = re.sub('(\w+)\s@\s((?:\w+.?)+)', r'\1@\2', line)
        #replace 'dot'
        line = re.sub('[\s\(](dot|dt)[\s\)]', r'.', line)
        #special cases
        if '@-' in line:
            line = re.sub('(\w)-', r'\1', line)
            line = re.sub('-', '', line)
        if 'DOM' in line:
            line = re.sub('(\w+)(\sWHERE\s)(\w+)(\s)(DOM)(\s)(\w+)', r'\1@\3.\7', line)
        if ';edu' in line:
            line = re.sub(';', r'.', line)
        #replace (at) / at with @
        line = re.sub('[\s\(]at[\s\)]((?:\w+\.+)+)', r'@\1', line)
        #emails hidden within html metacharacters
        line = re.sub("obfuscate\('((?:\w+\.?)+)','(\w+)'\)", r'\2@\1', line)
        #more special cases
        #sometimes, @ comes in as a set of special metacharacters
        line = re.sub(r'&#x40;', r'@', line)
        #obfuscated emails found in ouster.txt
        if '(followed by' in line.lower():
            line = re.sub('(.*>)((?:\w+\.?)+)(.*)(@(?:\w+\.?)+)(.*)', r'\2@\4', line)
        #look for 'email:' in line and replace form an email
        if 'email:' in line:
            line = re.sub('(email:\s?)(\w+)\s(at)\s(\w+)\s(\w+)\s(\w+)', r'\2@\4.\5.\6', line)
        #avoid catastrophic backtracking in case where there is no real email
        email_matches = re.findall(email_pat,line)
        #phone
        line = re.sub('\+1\s?\(?(\d{3})\s?\)?-?\s?(\d{3})[-\s]?(\d{4})', r'\1-\2-\3', line)
        line = re.sub('\((\d{3})\)(\s*)(\d{3})', r'\1-\3', line)
        phone_matches = re.findall(phone_pat, line)
        for m in email_matches:
            email = '%s@%s.edu' % m
            res.append((name,'e',email))
        for m in phone_matches:
            phone = '%s-%s-%s' % m
            res.append((name, 'p', phone))
    return res

"""
You should not need to edit this function, nor should you alter
its interface as it will be called directly by the submit script
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r', encoding=enc)
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print ('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print ('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print ('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print ('Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn)))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) == 1):
        main('../data/dev', '../data/devGOLD')
    elif (len(sys.argv) == 3):
        main(sys.argv[1],sys.argv[2])
    else:
        print ('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
