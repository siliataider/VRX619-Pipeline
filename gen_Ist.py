# --- Compatible: Python2,Python3 ---
from __future__ import print_function

#----------------
#Import of modules
#----------------
import argparse
import sys,os, re

#----------------
#Global Variables
#----------------
version = "V1.3 on 08-09-2009"

def doProcessing(InputFile, OutputFile):

    # Open the input file
    fidIn = open(InputFile, "r")
    if not fidIn:
        print("Could not open the input file %s" % (InputFile))
        return 1

    print(" [INFO]: Processing Input File \"%s\".....\n" % (InputFile))

    flag = 0
    flg = 0
    cnt = 0
    labels = {}
    lineCount = 0
    for line in fidIn:
        lineCount += 1
        #line = line.strip()

        reRegexp = re.compile(r"^\s*(=)+\s*$")
        res = reRegexp.match(line)
        if res:
            flag = 0
            continue

        reRegexp = re.compile(r"^\s*Name\s*:\s*\.((code)|(abscode))\s*$")
        res = reRegexp.match(line)
        if res:
            flg = 1
            continue

        reRegexp = re.compile(r"^\s*Name\s*:\s*\.symtab\s*$")
        res = reRegexp.match(line)
        if flg == 1 and res:
            flag = 1
            cnt = cnt + 1
            key = "BLK_%d" % (cnt)
            labels[key] = []
            flg = 0
            continue

        if flag == 1:
            reRegexp = re.compile(r"^\s*0x([0-9A-Fa-f]+)\s+(\w)\s+(\w)\s+(code)\s+(\d)\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s+$")
            res = reRegexp.match(line)
            if res:
                if res.group(6) != "__":
                    v = (int(res.group(1), 16) , res.group(6))
                    labels[key].append(v)
    fidIn.close()
    #print labels

    print(" [INFO]: Creating Output File \"%s\"....." % (OutputFile))
    fidIn = open(InputFile, "r")
    if not fidIn:
        print("Could not open the input file %s" % (InputFile))
        return 1
    fidOut = open(OutputFile, "w")
    if not fidOut:
        print("Could not open the output file %s" % (OutputFile))
        return 2

    print(" [INFO]: Writing to Output File \"%s\"....." % (OutputFile))

    flag = 0
    cnt = 0
    lineCount = 0
    stateSecondLine = False
    savedfirstLine = None
    for line in fidIn:
        lineCount += 1
        line = line.rstrip('\n')
        #line = line.strip()

        #print "DbgPrintLine %d: '%s'" % (lineCount, line)

        if not stateSecondLine:
            reRegexp  = re.compile(r"^\s*(\=)+\s*$")
            res = reRegexp.match(line)
            if res:
                flag = 0
                print("%s" % (line), file=fidOut)
                continue

            reRegexp   = re.compile(r"^\s*Name\s*:\s*\.((code)|(abscode))\s*$")
            res = reRegexp.match(line)
            if res:
                flag = 1
                cnt = cnt + 1
                key = "BLK_%d" % (cnt)
                print("%s" % (line), file=fidOut)
                continue

            reRegexp = re.compile(r"^\s*Addr\s*:\s*0x([A-Fa-f0-9]+)\s*$")
            res = reRegexp.match(line)
            if (flag == 1) and res:
                addr = int(res.group(1),16)
                print("%s" % (line), file=fidOut)
                continue

            reRegexp   = re.compile(r"^(\s*File\s*:\s*)\"([^\"]+)\"\s*Name\s*:\s*\d+\s*$")
            res = reRegexp.match(line)
            if (flag == 1) and res:
                #print "Dbg1 %d" % (lineCount), res.groups()
                tmp = res.group(1)
                fn = res.group(2)
                if (fn == "anonymous"):
                    continue

                reRegexp  = re.compile(r"^\s*([A-Za-z]?:?[/\\\]\\\?([A-Za-z_0-9\.\~]+[/\\\]\\\?)+)([A-Za-z_0-9\.\~]+\.([A-Za-z_0-9]+))\s*$")
                res = reRegexp.match(fn)
                if res:
                    #print "Dbg2 %d" % (lineCount), res.groups()
                    if (res.group(4) == "inc"):
                        print("%s" % (line), file=fidOut)
                    else:
                        asm_fn = res.group(3)
                        savedfirstLine = line
                        stateSecondLine = True
                        continue
                else:
                    print("[FAIL]: Unable to extract ASM Path[%s]\n" % (fn))
                    return False
                continue

            reRegexp = re.compile(r"^\s*0x([A-Fa-f0-9]+)(\:.+)")
            res = reRegexp.match(line)
            if (flag == 1) and res:
                tmp = addr + int(res.group(1), 16)
                for i in labels[key]:
                    j = 0
                    if (tmp == i[0]):
                        if (j == 0 and tmp != addr):
                            print("", file=fidOut)
                        j = j + 1
                        print("                                    %s:" % (i[1]), file=fidOut)
                tmp = "0x%08X" % (tmp)
                print("\t%s%s" % (tmp, res.group(2)), file=fidOut)
                continue

            # If nothing matched
            print("%s" % (line), file=fidOut)


        else:
            #print "Dbg3 %d: \First: '%s'\nSecond:'%s'" % (lineCount, savedfirstLine, line)
            stateSecondLine = False
            reRegexp  = re.compile(r"^\s*File\s*:\s*\"([^\"]+)\"\s*Name\s*:\s*\d+\s*$")
            res = reRegexp.match(line)
            if res:
                #print "Dbg4 %d" % (lineCount), res.groups()
                fn = res.group(1)
                reRegexp  = re.compile(r"^\s*([A-Za-z]?:?[/\\\]\\\?([A-Za-z_0-9\.\~]+[/\\\]\\\?)+)([A-Za-z_0-9\.\~]+\.([A-Za-z_0-9]+))\s*$")
                res = reRegexp.match(fn)
                if res:
                    ext = res.group(4)
                    if ext in ('c', 'cpp'):
                        pass
                        #[UNUSED]c_path = res.group(1)
                        #[UNUSED]c_fn = res.group(3)
                    else:
                        print("[FAIL]: Expecting a C or CPP file!!")
                        print(r"[FAIL]: Found a file with \.%s extension!!\n" % (ext))
                        return False
                else:
                    print("[FAIL]: Unable to extract C Path!!\n")
                    return False
                asm_path = os.getcwd()
                fn = os.path.join(asm_path,asm_fn)
                print("%s\"%s\" Name: 0" % (tmp,fn), file=fidOut)
                print("%s" % (line), file=fidOut)
            else:
                print("%s" % (savedfirstLine), file=fidOut)
                print("%s" % (line), file=fidOut)


    fidIn.close()
    fidOut.close()
    return True


if __name__ == "__main__":        
    print ("\n Start of Script: %s" % (sys.argv[0]))
    print ("\n <<-------------------------------------------------------------------------->>")
    parser = argparse.ArgumentParser(description='Generate PP32 list file (%s).' % (version))
    parser.add_argument("InputFile", help='Input file name')
    parser.add_argument("OutputFile", help='Output file name')

    args = parser.parse_args()
    GenOutputFile = args.OutputFile

    resu = doProcessing(args.InputFile, args.OutputFile)
    resu = 0
    if resu != 0:
        # In case of errors we delete the output file
        if os.path.exists(GenOutputFile):
            os.remove(GenOutputFile)

    print ("\n <<-------------------------------------------------------------------------->>")

    # Return result
    sys.exit(resu)


