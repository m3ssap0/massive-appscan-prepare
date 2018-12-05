import sys, getopt
import time, datetime
import os, shutil, subprocess

# Reads and checks input parameters.
def read_input(argv):
   usage = "massive-appscan-prepare.py -i|--input <input_file> [-c|--configuration <configuration_file>]"
   input_file = None
   config_file = None
   
   try:
      opts, args = getopt.getopt(argv,"hi:c:",["input=", "configuration="])
   except getopt.GetoptError:
      print usage
      sys.exit(2)
	  
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print usage
         sys.exit()
      elif opt in ("-i", "--input"):
         input_file = arg
      elif opt in ("-c", "--configuration"):
         config_file = arg

   if input_file is None or len(input_file.strip()) < 1:
      print "[!] The input file can not be empty!"
      sys.exit(2)

   input_file = input_file.strip()
   print "[*] Input file is: '{}'.".format(input_file)
   
   if not os.path.isfile(input_file):
      print "[!] Input file provided is not a file!"
      sys.exit(2)

   if config_file is not None:
      config_file = config_file.strip()
      print "[*] Configuration file is: '{}'.".format(config_file)
      if not os.path.isfile(config_file):
         print "[!] Configuration file provided is not a file!"
         sys.exit(2)

   return input_file, config_file

# Parses file to read project folders that will be analyzed.
def parse_file(input_file):
   print "[*] Reading file '{}'.".format(input_file)
   with open(input_file) as f:
      projects = f.readlines()
   projects = [p.strip() for p in projects]
   print "[*] There are '{}' project folders in the file.".format(len(projects))
   return projects

# Prints a fancy separator with timestamp.
def print_separator():
   print "[*] -------------------------------------------------------------------------"
   print "[*] Timestamp: '{}'.".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
   print "[*] -------------------------------------------------------------------------"

# Gets the right system char to concat shell commands on one line.
def get_sys_cmd_concat_char():
   cmd_concat_char = "&&"
   return cmd_concat_char

# Launches command for each project.
def appscan_prepare(projects, config_file):
   num = 0
   for project in projects:
      print_separator()
      num = num + 1
      print "[*] {}/{}".format(num, len(projects))
      if project.startswith("#"):
         print "[-] Ignoring project '{}'.".format(project)
      else:
         print "[*] Considering project '{}'.".format(project)
         if os.path.isdir(project):
            command = "cd \"{}\" ".format(project)
            command = command + get_sys_cmd_concat_char() + " "
            command = command + "appscan prepare "
            if config_file is not None:
               print "[*] Copying configuration file '{}'.".format(config_file)
               shutil.copy2(config_file, project)
               head, tail = os.path.split(config_file)
               command = command + "-c {} ".format(tail)
            else:
               print "[-] No configuration file to copy."
            command = command + "-v"
            print "[*] Command will be: '{}'.".format(command)
            print "[*] Executing command."
            try:
               command_output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
               print command_output
               print "[*] Command executed."
            except subprocess.CalledProcessError as cpe:
               print "[!] Command failed."
               print "[!]    {}".format(cpe)
               print "[!]    Return code = {}".format(cpe.returncode)
               print "[!]         Output = {}".format(cpe.output.replace("\r", "").replace("\n", ""))
         else:
	        print "[!] This project is not a directory! Jumping it."

# Main execution.
if __name__ == "__main__":
   print "Massive 'appscan prepare' - v1.0 (2018-10-19)"
   input_file, config_file = read_input(sys.argv[1:])
   projects = parse_file(input_file)
   appscan_prepare(projects, config_file)
   print_separator()
   print "Finished."