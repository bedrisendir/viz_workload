#!/usr/bin/python
import sys
import glob
import re
import csv

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
            tput[skey][opkey] += (opval/interval)
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


def main(fn):
    timelinefiles = glob.glob(fn+'*err.txt')
    summaryfiles = glob.glob(fn+'*out.txt')
    out_tput_fn = fn.replace('data/raw', 'data/final') + '.optput.csv'
    out_lat_fn = fn.replace('data/raw', 'data/final') + '.oplatency.csv'
    instances = len(summaryfiles)
    try:
        tokenValue = re.search('status.interval=(.*)',open(timelinefiles[0], 'r').readline())
        interval = int(tokenValue.group(1).split()[0])
    except:
        interval = 2
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

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_ycsb.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])