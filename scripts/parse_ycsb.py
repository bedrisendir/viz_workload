#!/usr/bin/python
import sys
import glob
import re
import csv
import os

tput = {}
latency = {}
def parseInstance(dataset,instances,interval):
    dataset = [x for x in open(dataset, 'r').readlines() if 'sec' and 'operations' in x]
    for line in dataset:
        skey = int(line.split()[2])
        if skey is 0:
            continue;
        if skey not in tput:
            tput[skey] = {}
        if skey not in latency:
            latency[skey] = {}

        if "TOTAL" not in tput[skey]:
            tput[skey]["TOTAL"] = int(0)

        tput[skey]["TOTAL"] += int(round(float(line.split()[6])))

        ops = re.findall(r"\[(.*?)\]", line)
        flag = False
        for op in ops:
            if flag:
                continue
            opkey = op.split(":")[0]
            opval = int(op.split()[1].split("=")[1].rstrip(","))
            if opkey in "CLEANUP" and opval < 2:
                flag = True
                continue
            try:
                latval = float(op.split()[4].split("=")[1].rstrip(","))
            except:
                latval = 0
            if opkey not in tput[skey]:
                tput[skey][opkey] = int(0)
            tput[skey][opkey] += int(round(float((opval/interval))))
            if opkey not in latency[skey]:
                latency[skey][opkey] = float(0)
            latency[skey][opkey] += (latval)

def TPUTtoCsv(fn,instances,interval):
    file = open(fn,'wb')
    writer = csv.writer(file)
    #identify all possible op types so that we can fill missing values
    headerkeys = set()
    for time,row in sorted(tput.iteritems()):
        for key,value in sorted(row.iteritems()):
            headerkeys.add(key)
    #omit cleanup
    if "CLEANUP" in headerkeys:
        headerkeys.remove("CLEANUP")

    #write time field
    writer.writerow(["time"] + list(headerkeys))
    for time,row in sorted(tput.iteritems()):
        csvrow=[]
        csvrow.append(time)
        if not row:
            continue
        for opkey in headerkeys:
            if opkey not in row:
                csvrow.append(0)
                continue
            try:
               csvrow.append(row[opkey])
            except:
               print row
        writer.writerow(csvrow)

def LATtoCsv(fn,instances,interval):
    file = open(fn,'wb')
    writer = csv.writer(file)
    #identify all possible op types so that we can fill missing values
    headerkeys = set()
    for time,row in sorted(latency.iteritems()):
        for key,value in sorted(row.iteritems()):
            headerkeys.add(key)
    #omit cleanup
    if "CLEANUP" in headerkeys:
        headerkeys.remove("CLEANUP")

    #write time field
    writer.writerow(["time"] + list(headerkeys))
    for time,row in sorted(latency.iteritems()):
        csvrow=[]
        csvrow.append(time)
        if not row:
            continue
        for opkey in headerkeys:
            if opkey not in row:
                csvrow.append(0)
                continue
            try:
                csvrow.append(row[opkey]/instances)
            except:
               print row
        writer.writerow(csvrow)

def generateSummary(summaryfiles,summary_fn,runid,instances):
    hasSummary = os.path.isfile(summary_fn)

    #read the data from the files
    avgtput = float(0)
    for summaryfile in summaryfiles:
       data = [x.split()[2] for x in open(summaryfile, 'r').readlines() if 'OVERALL' and 'Throughput' in x]
       avgtput+=float(data[0])

    #parse iteration and runid
    itertokens = [strr for strr in runid.split("_") if "ITER" in strr]
    iter_count = 1
    if itertokens and itertokens[0].split("=")[1].isalnum():
        runid = runid.split("_")[0]
        iter_count = itertokens[0].split("=")[1]

    #we now have data as avgtput , runid, and itercount

    dataset={}
    indexmap={}
    if hasSummary:
        reader = csv.reader(open(summary_fn));
        headerRow = next(reader)
        index = 0
        for item in headerRow[1:]:
            dataset[item]={}
            indexmap[index]=item
            index+=1
        for row in reader:
            iter_num = int(row[0])
            iter_index = 0
            for tput in row[1:]:
                dataset[indexmap[iter_index]][int(iter_num)] = tput
                iter_index+=1
        print dataset
        print indexmap

    if runid not in dataset:
        dataset[runid] = {}
        indexmap[len(indexmap)] = runid

    dataset[runid][int(iter_count)] = avgtput
    print ""
    print dataset
    print indexmap
    writer = csv.writer(open(summary_fn,'w+'));
    #construct header
    header = []
    header.append("runid")
    maxVal = 0
    for key,value in sorted(indexmap.iteritems()):
        header.append(value)
        if len(dataset[value]) > maxVal:
            maxVal = len(dataset[value])

    writer.writerow(header);
    for i in range(1,1+maxVal):
        row = []
        row = row + [0]*(len(indexmap))
        for key,value in sorted(indexmap.iteritems()):
            print "--1-"
            print key
            print value
            print row
            print "--2-"
            if i in dataset[value]:
              row[key] = dataset[value][i]
        writer.writerow([str(i)]+row)



def main(fn):
    fn = fn.replace('data/raw', 'data/raw/ycsb')
    timelinefiles = glob.glob(fn+'*err.txt')
    summaryfiles = glob.glob(fn+'*out.txt')
    out_tput_fn = fn.replace('data/raw/ycsb', 'data/final') + '.optput.csv'
    out_lat_fn = fn.replace('data/raw/ycsb', 'data/final') + '.oplatency.csv'
    finalpath, runid = os.path.split(os.path.abspath(fn.replace('data/raw/ycsb', 'data/final')))
    print fn
    print finalpath
    print runid
    summary_fn = finalpath  + '/ycsbsummary.csv'
    runid = runid.split('.')[0]
    instances = len(summaryfiles)
    try:
        tokenValue = re.search('status.interval=(.*)',open(timelinefiles[0], 'r').readline())
        interval = int(tokenValue.group(1).split()[0])
    except:
        interval = 10
    print "YCSB Instances:" + str(instances)
    print "YCSB Interval:"+ str(interval)
    print "YCSB Throughput File:"+ out_tput_fn
    print "YCSB Latency File:"+ out_lat_fn
    if (len(timelinefiles)!=len(summaryfiles)):
        sys.stderr.write("incorrect number of ycsb input files\n")
        sys.exit(1)
    instances = len(timelinefiles)
    dataset = []
    for instanceData in timelinefiles:
        dataset.append(parseInstance(instanceData,instances,interval))
    TPUTtoCsv(out_tput_fn,instances,interval)
    LATtoCsv(out_lat_fn,instances,interval)
    generateSummary(summaryfiles,summary_fn,runid,instances);

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_ycsb.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])