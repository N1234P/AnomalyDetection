import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import random
import pandas as pd

import os

# Methods for generating martingale results - martingale algorithm implemented in python
# martingaleTest() is the generic martingale algorithm method for dynamic data

# arrays to store final data - total anomalies detected, average delay time, % of anomalies detected correctly,
# % of false positives, and % of missed detections
tdarr, adtarr, dcarr, fparr, mdarr = [], [], [], [], []


# [[[graph 1 centrality nodes], [graph 2 centrality nodes], ... [graph nth timestep centrality nodes]],[[  ],[  ]..., [ ]]]

def getFormattedString(list):
    string = ''
    for i in range(len(list)):
        if i % 8 == 0:
            string = string + '\n'
        if i == len(list) - 1:
            string = string + str(list[i])
        else:
            string = string + str(list[i]) + ', '
    return string


def getStrangeness(data):
    kmeans = KMeans(n_clusters=1, random_state=0).fit(data)
    strangeness = kmeans.fit_transform(data)
    return strangeness


def getPValue(strangeness, i):
    rand_term = random.uniform(0, 1)
    term1 = []
    term2 = []
    for i in range(len(strangeness)):
        if strangeness[i] > strangeness[-1]:
            term1.append(i)
        elif strangeness[i] == strangeness[-1]:
            term2.append(i)

    pvalue = (len(term1) + (rand_term * len(term2))) / (i + 1)

    return pvalue


def martingaleTest(data, offset, threshold=100, epsilon=0.92, window=300):
    pvalues = []
    change_detected = []
    martingale = [1]
    saved_martingales = [1]
    T = []
    saved_strangeness = []
    for i in range(len(data)):
        print(i)
        if len(T) == 0:
            strangeness = [0]
        else:
            strangeness = getStrangeness(T + [data[i]])
        saved_strangeness.append(strangeness[-1])

        pvalues.append(getPValue(strangeness, i))

        martingale.append(martingale[-1] * epsilon * (pvalues[-1] ** (epsilon - 1)))
        saved_martingales.append(martingale[-1])

        if martingale[-1] > threshold and i > offset:
            print('CHANGE DETECTED')
            T = []
            change_detected.append(i)
            martingale[-1] = 1
        else:
            T.append(data[i])
            if len(T) > window:
                T.pop(0)

    print('Changes detected at timestep: ' + str(change_detected))
    return change_detected, pvalues, saved_strangeness, saved_martingales


def multiMartingaleTest(datas, threshold, epsilon=0.92, offset=50):
    pValueLists = []
    change_detected = []
    martingales = []
    saved_martingales = []
    tempLists = []
    strangenesses = []
    changeIsDetected = []
    detectionCounters = []

    for i in range(len(datas)):
        pValueLists.append([])
        martingales.append([1])
        saved_martingales.append([1])
        tempLists.append([])
        strangenesses.append([])
        detectionCounters.append(-1)
        changeIsDetected.append(False)

    for i in range(len(datas[0])):

        print(i)
        if len(tempLists[0]) == 0:
            for j in range(len(strangenesses)):
                strangenesses[j] = [0]
        else:
            for j in range(len(datas)):
                strangenesses[j] = getStrangeness(tempLists[j] + [datas[j][i]])

        for j in range(len(datas)):
            pValueLists[j].append(getPValue(strangenesses[j], i))
            martingales[j].append(martingales[j][-1] * epsilon * (pValueLists[j][-1] ** (epsilon - 1)))
            saved_martingales[j].append(martingales[j][-1])
            changeIsDetected[j] = False

        for j in range(len(datas)):
            # print(martingales[j][-1])
            if martingales[j][-1] > threshold and i > offset:
                changeIsDetected[j] = True
                if detectionCounters[j] == -1:
                    detectionCounters[j] = 25
                elif detectionCounters[j] > 0:
                    detectionCounters[j] -= 1
                elif detectionCounters[j] == 0:
                    detectionCounters[j] = -1
                    tempLists[j] = []
                    martingales[j][-1] = 1
                    changeIsDetected[j] = False
                print("Change suggested by Representation " + str(j))
        count = 0.0
        for j in range(len(datas)):
            if changeIsDetected[j]:
                count += 1
        if count >= (len(datas) / 2):
            print("CHANGE DETECTED")
            change_detected.append(i)

            for j in range(len(datas)):
                tempLists[j] = []
                martingales[j][-1] = 1
                detectionCounters[j] = -1
        else:
            for j in range(len(datas)):
                tempLists[j].append(datas[j][i])
        # print(saved_martingales)

    return change_detected, pValueLists, [], saved_martingales


def calculateAndSaveMartingales(titles, datas, data, offset, filename, threshold=100, epsilon=0.92, anomalies=[],
                                title='Martingale'):
    change_detected, pvalues, strangeness, test_martingale = martingaleTest(data, offset, threshold, epsilon)
    outputAndSummarizeMartingaleData(titles, datas, data, offset, threshold, epsilon, change_detected, pvalues,
                                     strangeness,
                                     test_martingale, filename, anomalies, title=title)


def calculateAndSaveMultiMartingales(datas, offset, filename, threshold=10, epsilon=0.92, anomalies=[],
                                     title='Ensemble-Martingale'):
    change_detected, pvalues, strangeness, test_martingale = multiMartingaleTest(datas=datas, threshold=threshold,
                                                                                 epsilon=0.92, offset=offset)
    outputMultiMartingaleData(datas[0], offset, threshold, epsilon, change_detected, pvalues, strangeness,
                              test_martingale,
                              filename, anomalies, title=title)


def outputMultiMartingaleData(data, offset, threshold, epsilon, change_detected, pvalues, strangeness, test_martingale,
                              filename, anomalies, title='Martingale'):
    fig = plt.figure(figsize=(15, 15))

    ax1 = fig.add_subplot(221)
    ax1.plot(pvalues)
    ax1.set_title("P - Values for Dataset ")
    ax1.set_xlabel('Time', fontsize=18)
    ax1.set_ylabel('P-Value', fontsize=16)

    ax2 = fig.add_subplot(222)
    plot_martingale = []
    for i in range(len(test_martingale[0])):
        for j in range(len(test_martingale)):
            plot_martingale.append(test_martingale[j][i])
        ax2.plot(plot_martingale)
        plot_martingale = []

    # ax2 = fig.add_subplot(222)
    # ax2.plot(test_martingale)
    ax2.set_title("test_martingale for Dataset ")
    ax2.set_xlabel('Time', fontsize=18)
    ax2.set_ylabel('test_martingale', fontsize=16)

    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    ax3.axis('off')
    ax4.axis('off')

    string1 = ''
    if len(change_detected) > 0:
        string1 = getFormattedString(change_detected)

    message = 'Timesteps: ' + str(len(data)) + '\n\nNumber of Nodes: ' + str(
        len(data[0])) + '\n\nWeighted: Yes' + '\n\nDirected: No'
    message = message + '\n\nEpsilon: ' + str(epsilon) + '\n\nThreshold: ' + str(threshold) + '\n\nOffset: ' + str(
        offset)
    message1 = 'Anomalies Detected At: ' + string1 + '\n\n# of Total Detections: ' + str(len(change_detected))

    if len(anomalies) > 0:
        length = len(anomalies)
        anomalies2 = anomalies.copy()
        totalDetected = 0
        delays = []
        missed_anomalies = []
        for num in change_detected:
            for num2 in anomalies2:
                if num - num2 >= 0 and num - num2 <= 50:
                    totalDetected += 1
                    delays.append(num - num2)
                    anomalies2.remove(num2)
                    break
        for anomaly in anomalies:
            if all((abs(anomaly - detection)) > 50 for detection in change_detected):
                missed_anomalies.append(str(anomaly))

        percentMissedDet = str(round((len(missed_anomalies) / length) * 100)) + "%"

        percent = 0
        percentFalsePos = 0
        avgDelay = 0
        if len(change_detected) > 0:
            percent = int(round((float(totalDetected / len(anomalies))), 2) * 100)
            percentFalsePos = int(round((len(change_detected) - totalDetected) / len(change_detected), 2) * 100)
            if (len(delays) == 0):
                avgDelay = 0
            else:
                avgDelay = int(sum(delays) / len(delays))
        string = ''
        if len(anomalies) > 0:
            string = getFormattedString(anomalies)
        message = message + '\n\nAnomalies Induced At: ' + string
        message1 = message1 + '\n\nAverage Delay Time: ' + str(
            avgDelay) + ' Timesteps' + '\n\n# of Anomalies Detected Correctly: ' + str(
            totalDetected) + '\n\n% of Anomalies Correctly Detected: ' + str(
            percent) + '%' + '\n\n% of False-Positive Detections: ' + str(percentFalsePos) + '%' + \
                   "\n\nMissed Detections:\n" + ", ".join(missed_anomalies) + "\n\n% of Missed Detections: " + str(
            percentMissedDet)

    ax3.text(0.7, 0.5, message, bbox=dict(facecolor='blue', alpha=0.5), horizontalalignment='center',
             verticalalignment='center', fontsize=11)
    ax4.text(0.3, 0.5, message1, bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='center',
             verticalalignment='center', fontsize=11)
    fig.suptitle(title + '\n' + filename, fontsize=22)

    plt.savefig(filename, bbox_inches='tight')
    plt.close()


def outputAndSummarizeMartingaleData(titles, datas, data, offset, threshold, epsilon, change_detected, pvalues,
                                     strangeness,
                                     test_martingale, filename, anomalies, title='Martingale'):
    global tdarr, adtarr, dcarr, fparr, mdarr

    tdarr.append(len(change_detected))

    fig = plt.figure(figsize=(15, 15))

    ax1 = fig.add_subplot(221)

    ax1.plot(pvalues)
    ax1.set_title("P - Values for Dataset ")
    ax1.set_xlabel('Time', fontsize=18)
    ax1.set_ylabel('P-Value', fontsize=16)

    ax2 = fig.add_subplot(222)
    ax2.plot(test_martingale)
    ax2.set_title("test_martingale for Dataset ")
    ax2.set_xlabel('Time', fontsize=18)
    ax2.set_ylabel('test_martingale', fontsize=16)

    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    ax3.axis('off')
    ax4.axis('off')

    string1 = ''
    if len(change_detected) > 0:
        string1 = getFormattedString(change_detected)

    message = 'Timesteps: ' + str(len(data)) + '\n\nNumber of Nodes: ' + str(
        len(data[0])) + '\n\nWeighted: Yes' + '\n\nDirected: No'
    message = message + '\n\nEpsilon: ' + str(epsilon) + '\n\nThreshold: ' + str(threshold) + '\n\nOffset: ' + str(
        offset)
    message1 = 'Anomalies Detected At: ' + string1 + '\n\n# of Total Detections: ' + str(len(change_detected))

    if len(anomalies) > 0:
        length = len(anomalies)
        anomalies2 = anomalies.copy()
        totalDetected = 0
        delays = []
        missed_anomalies = []

        for num in change_detected:
            for num2 in anomalies2:
                if num - num2 >= 0 and num - num2 <= 50:
                    totalDetected += 1
                    delays.append(num - num2)
                    anomalies2.remove(num2)
                    break

        for anomaly in anomalies:
            if all((abs(anomaly - detection)) > 50 for detection in change_detected):
                missed_anomalies.append(str(anomaly))

        percentMissedDet = str(round((len(missed_anomalies) / length) * 100)) + "%"
        percent = 0
        percentFalsePos = 0
        avgDelay = 0
        if len(change_detected) > 0:
            percent = int(round((float(totalDetected / len(anomalies))), 2) * 100)
            percentFalsePos = int(round((len(change_detected) - totalDetected) / len(change_detected), 2) * 100)
            if (len(delays) == 0):
                avgDelay = 0
            else:
                avgDelay = int(sum(delays) / len(delays))
        string = ''
        if len(anomalies) > 0:
            string = getFormattedString(anomalies)
        message = message + '\n\nAnomalies Induced At: ' + string
        message1 = message1 + '\n\nAverage Delay Time: ' + str(
            avgDelay) + ' Timesteps' + '\n\n# of Anomalies Detected Correctly: ' + str(
            totalDetected) + '\n\n% of Anomalies Correctly Detected: ' + str(
            percent) + '%' + '\n\n% of False-Positive Detections: ' + str(percentFalsePos) + '%' + \
                   "\n\nMissed Detections:\n" + ", ".join(missed_anomalies) + "\n\n% of Missed Detections: " + str(
            percentMissedDet)

        adtarr.append(avgDelay)
        dcarr.append(percent)
        fparr.append(percentFalsePos)
        mdarr.append(percentMissedDet)
    ax3.text(0.7, 0.5, message, bbox=dict(facecolor='blue', alpha=0.5), horizontalalignment='center',
             verticalalignment='center', fontsize=11)
    ax4.text(0.3, 0.5, message1, bbox=dict(facecolor='red', alpha=0.5), horizontalalignment='center',
             verticalalignment='center', fontsize=11)
    fig.suptitle(title + '\n' + filename, fontsize=22)

    plt.savefig(filename, bbox_inches='tight')

    if title == titles[len(titles) - 1]:
        # define figure and axes

        fig, ax = plt.subplots()

        # hide the axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        rows = []
        for i in range(len(datas)):
            if len(adtarr) > 0:
                rows.append([titles[i], tdarr[i], adtarr[i], dcarr[i], fparr[i], mdarr[i]])
            else:
                rows.append([titles[i], tdarr[i]])
        if len(adtarr) > 0:
            df = pd.DataFrame(rows, columns=["CENTRALITY MEASURE", "TOTAL DETECTED", "AVERAGE DELAY TIME",
                                             "% OF ANOMALIES CORRECTLY DETECTED", "% OF FALSE POSITIVE DETECTIONS",
                                             "% OF MISSED DETECTIONS"])
        else:
            df = pd.DataFrame(rows, columns=["CENTRALITY MEASURE", "TOTAL DETECTED"])

        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(15)
        table.scale(5, 5)
        plt.savefig("final_results", bbox_inches='tight')

    plt.close()


def calculateAndSaveManyMartingales(datas, offset, anomalies=[], dirName="Graphs_Martingale_Data", titles=[]):
    while len(titles) > len(datas):
        titles.append('Martingale')
    os.mkdir(dirName)
    os.chdir(dirName)
    for i in range(len(datas)):
        calculateAndSaveMartingales(titles, datas, datas[i], offset, filename=str(i), anomalies=anomalies,
                                    title=titles[i])

    os.chdir('..')
    os.chdir('..')
