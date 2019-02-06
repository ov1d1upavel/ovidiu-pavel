import numpy as np
import matplotlib.pyplot as plt



def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def readDataFromFile(filename):
    try:
        file = open(filename, "r")
    except IOError:
        print("Could not open file!")

    isCol = None
    tableHeaders = []
    dataMap = {}

    xAxis = None
    yAxis = None

    for line in file:

        if "x axis: " in line:
            xAxis = line[len("x axis: "):].rstrip("\r").rstrip("\n")
            continue

        if "y axis: " in line:
            yAxis = line[len("y axis: "):].rstrip("\r").rstrip("\n")
            continue

        if line.rstrip("\r").rstrip("\n") == '':
            continue

        inputLineList = []

        # Read all line elements

        for elem in line.rstrip("\r").rstrip("\n").split(' '):
            if "\n" in elem or " " in elem or elem == '':
                continue
            inputLineList.append(elem)

        # Handle the headers
        if isCol is None:
            if isInt(inputLineList[1]):
                isCol = False
            else:
                isCol = True
                for header in inputLineList:
                    tableHeaders.append(header.lower())
                    dataMap[header.lower()] = []
                continue

        if not isCol:
            RowsCurrentHeader = inputLineList[0].lower()
            tableHeaders.append(RowsCurrentHeader)
            del(inputLineList[0])

        # Handle the numbers

        if isCol:
            if len(inputLineList) != len(tableHeaders):
                print("Input file error: Data lists are not the same length")
                return None, None, None, None
            for i in range(len(tableHeaders)):
                dataMap[tableHeaders[i]].append(float(inputLineList[i]))
        else:
            dataMap[RowsCurrentHeader] = [float(i) for i in inputLineList]

    # Handle errors

    for header in tableHeaders:
        if len(dataMap[header]) != len(dataMap[tableHeaders[0]]):
            print("Input file error: Data lists are not the same length")
            return None, None, None, None

    for header in ['dx', 'dy']:
        for elem in dataMap[header]:
            if float(elem) < 0:
                print("Input file error: Not all uncertainties are positive.")
                return None, None, None, None



    return tableHeaders, xAxis, yAxis, dataMap

def fit_linear(filename):
    tableHeaders, xAxis, yAxis, dataMap = readDataFromFile(filename)

    # If Error

    if tableHeaders is None:
        return

    # Calculate parameters a, b:

    N = len(dataMap['x'])

    x_mean = np.mean(dataMap['x'])
    y_mean = np.mean(dataMap['y'])




    xy = [dataMap['x'][i] * dataMap['y'][i] for i in range(N)]
    xy_mean = np.mean(xy)



    x_squared = [dataMap['x'][i] * dataMap['x'][i] for i in range(N)]
    x_squared_mean = np.mean(x_squared)

    dy_squared = [dataMap['dy'][i] * dataMap['dy'][i] for i in range(N)]
    dy_squared_mean = np.mean(dy_squared)

    

    a = (xy_mean - x_mean * y_mean) / (x_squared_mean - x_mean * x_mean)
    b = y_mean - a * x_mean



    da = np.sqrt(dy_squared_mean / (N * (x_squared_mean - x_mean * x_mean)))
    db = da * np.sqrt(x_squared_mean)

    chi2 = np.sum(
        [
            np.square((dataMap['y'][i] - (a * dataMap['x'][i] + b))/dataMap['dy'][i])
            for i in range(N)
        ]
    )

    chi2_reduced = chi2 / (N-2)

    # Print results:

    print("\n")
    print("a = " + str(a) + " +- " + str(da))
    print("b = " + str(b) + " +- " + str(db))
    print("chi2 = " + str(chi2))
    print("chi2_reduced = " + str(chi2_reduced))

    #Plot linear regression graph:

    x = np.array(dataMap['x'])
    y = np.array(dataMap['y'])

    xerr = np.array(dataMap['dx'])
    yerr = np.array(dataMap['dy'])

    plt.scatter(x, y, marker='o')



    plt.errorbar(x, y, yerr, xerr, fmt='b, ')

    plt.xlabel(xAxis)
    plt.ylabel(yAxis)

    plt.plot(x, (a * x + b), c='r')


    plt.title('Linear Regression Plot')



    plt.savefig('linear_fit.svg', format='svg')

    plt.show()




fit_linear("/Users/uzieven/Desktop/project2/files/inputcols.txt")