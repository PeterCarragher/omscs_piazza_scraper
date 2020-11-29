import csv
import numpy as np

def parseCSV(file_name, first_idx, last_idx):
    results = np.empty([1, 7]) 
    with open(file_name) as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            results = np.vstack([results, row[first_idx:last_idx]])
    return results

results1 = parseCSV('survey_1.csv', 3, 10)
results2 = parseCSV('survey_0.csv', 15, 22)

results = np.concatenate((results1, results2))

print((results))
print(np.mean(results.astype(np.float), axis=0))
print(np.mean(np.mean(results.astype(np.float), axis=0)))
print(np.mean(results.astype(np.float)))
