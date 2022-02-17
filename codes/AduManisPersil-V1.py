# Import libraries
import shapefile as sf
import numpy as np
import pandas as pd

# Membaca shapefile input, directory disesuaikan dengan kebutuhan
ShapefileDir = "D:\Eksperimen\AduManis\Data Dummy Pengukuran Persil Tanah\Data Dummy Pengukuran Persil Tanah"
SFReader = sf.Reader(ShapefileDir)
Attributes = SFReader.records()
Features = SFReader.shapes()
Fields = SFReader.fields

# Menentukan atribut NIB
NIBindex = 0
for i in range(len(Fields)):
    if Fields[i][0] == 'NIB':
        NIBindex = i - 1

# Ekstraksi koordinat persil
Points = []
numParcels = len(Features)
for i in range(numParcels):
    PointID = 0
    NIB = Attributes[i][NIBindex]
    for n in range(len(Features[i].points)-1):
        PointID += 1
        Point = [NIB, PointID, Features[i].points[n][0]-304425, Features[i].points[n][1]-733018]
        Points.append(Point)
        
for Point in Points:
    Point.append(Point[0]+'-'+str(Point[1]))

numObs = len(Points)

# Mendefinisikan fungsi pencarian jarak terdekat (Euclidean Distance)
def Euclidean(a, b):
    Distance = np.linalg.norm(np.array(a) - np.array(b))
    return Distance

def deep_index1(lst, w):
    for (i, sub) in enumerate(lst):
        #print(i, sub[1])
        for (j, subsub) in enumerate(sub[1]):
            #print(j, subsub)
            if w==subsub[0]:
                return(sub[1])
            
def deep_index2(lst, w):
    for (i, sub) in enumerate(lst):
        #print(i, sub[1])
        if w==sub[0]:
            return(sub[0])

def block_adjustment_sparsity(nParcels, nPoints, nObs, tiePoints):
    m = nObs * 2
    n = nParcels * 4 + nPoints * 2
    A = np.zeros((m, n))
    F = np.zeros((m,1))
    row = 0
    NIBarray = []
    for (i, Points) in enumerate(tiePoints):
        #print(i, sub[1])
        isKontrol = False
        if i < 4:
            isKontrol = True
        for (j, Obs) in enumerate(Points[1]):
            if (isKontrol == True) and  (j==0):
                Xcontrol = Obs[1][0]
                Ycontrol = Obs[1][1]
            
            NIB = Obs[0][:5]
            if NIB not in NIBarray:
                NIBarray.append(NIB)
            idx = NIBarray.index(NIB)
    
            
            A[2 * row, (2 * nPoints) + (4 * idx)] = Obs[1][0]
            A[2 * row, (2 * nPoints) + (4 * idx) + 1] = -Obs[1][1]
            A[2 * row, (2 * nPoints) + (4 * idx) + 2] = 1
            A[2 * row, (2 * nPoints) + (4 * idx) + 3] = 0

            A[2 * row + 1, (2 * nPoints) + (4 * idx)] = Obs[1][1]
            A[2 * row + 1, (2 * nPoints) + (4 * idx) + 1] = Obs[1][0]
            A[2 * row + 1, (2 * nPoints) + (4 * idx) + 2] = 0
            A[2 * row + 1, (2 * nPoints) + (4 * idx) + 3] = 1

            if isKontrol == False:
                A[2 * row, 2 * i] = -1
                A[2 * row + 1, 2 * i + 1] = -1

            if isKontrol == True:
                F[2 * row,0] = Xcontrol
                F[2 * row + 1,0] = Ycontrol    
            
            print(Obs, idx)
            row = row + 1

    #print(NIBarray)

            
    return A, F


    
# Penentuan titik sekawan
TitikSekawan = []
TSSearched = []
Counter = 0
for n in range(len(Points)):
    TSCheck = Points[n][-1]
    if TSCheck not in TSSearched:

        #TitikSekawan.append([Counter])
        TS = []
        TS.append([Points[n][-1],Points[n][2:4]])
        PointA = Points[n][2:4]
        flag = False
        for i in range(len(Points)):
            if i != n:
                PointB = Points[i][2:4]
                if Euclidean(PointA, PointB) <= 2.5 and Points[i][-1] not in TSSearched:
                    TS.append([Points[i][-1],Points[i][2:4]])
                    TSSearched.append(Points[i][-1])
                elif Euclidean(PointA, PointB) <= 2.5 and Points[i][-1] in TSSearched:
                    TSw = (deep_index1(TitikSekawan, Points[i][-1]))
                    #print(TSw)
                    if deep_index2(TSw,Points[n][-1]) is None:
                        TSw.append([Points[n][-1],Points[n][2:4]])
                    flag = True

        if flag == False:
            Counter += 1
            TitikSekawan.append([Counter])            
            TitikSekawan[Counter-1].append(TS)

#print(TitikSekawan)

#Block Adjusment, dimulai dengan menyusun matriks persamaan pengamatan
numPoints = len(TitikSekawan)

print(numObs)
print(numPoints)
print(numParcels)
MatriksA, MatriksF = block_adjustment_sparsity(numParcels, numPoints, numObs, TitikSekawan)

#SEmentara
MatriksA = np.delete(MatriksA,slice(8), 1)
MatriksA = np.delete(MatriksA, slice(28,32), 1)
MatriksA = np.delete(MatriksA, [0,1,4,5,12,13,20,21], 0)
MatriksF = np.delete(MatriksF, [0,1,4,5,12,13,20,21], 0)



da = pd.DataFrame(MatriksA)
da.to_excel(excel_writer = "D:/Eksperimen/AduManis/mata.xlsx")
df = pd.DataFrame(MatriksF)
df.to_excel(excel_writer = "D:/Eksperimen/AduManis/matf.xlsx")



#print("shape = ",np.shape(MatriksF))

MatriksAt = np.transpose(MatriksA)
MatriksAtA = np.mat(MatriksAt) * np.mat(MatriksA)
MatriksAtF = np.mat(MatriksAt) * np.mat(MatriksF)

dg = pd.DataFrame(MatriksAtA)
dg.to_excel(excel_writer = "D:/Eksperimen/AduManis/matata.xlsx")
dh = pd.DataFrame(MatriksAtF)
dh.to_excel(excel_writer = "D:/Eksperimen/AduManis/matatf.xlsx")


X = np.linalg.solve(MatriksAtA, MatriksAtF)

print(X)


# Merata-ratakan titik sekawan
TitikAvgTS = []
for TS in TitikSekawan:
    X = []
    Y = []
    for Titik in TS[1]:
        X.append(Titik[1][0])
        Y.append(Titik[1][1])
    Xavg = sum(X)/len(X)
    Yavg = sum(Y)/len(Y)
    for Titik in TS[1]:
        TitikAvgTS.append([Titik[0], Xavg, Yavg])

TitikAvgTS.sort()

TitikAvg = {}
for Titik in TitikAvgTS:
    NIB = Titik[0][:5]
    #print(NIB)
    if int(NIB) not in list(TitikAvg.keys()):
        TitikAvg[int(NIB)] = [(Titik[1],Titik[2])]
    elif int(NIB) in list(TitikAvg.keys()):
        TitikAvg[int(NIB)].append((Titik[1],Titik[2]))

for NIB in list(TitikAvg.keys()):
    Koordinat = TitikAvg[NIB]
    Koordinat.append(Koordinat[0])

# Definisikan dengan directory di mana shapefile persil bersih akan disimpan
#os.chdir('D:\Eksperimen\AduManis\Data Dummy Pengukuran Persil Tanah\')
# Penulisan shapefile, dapat diganti nama file sesuai kebutuhan
w = sf.Writer('D:\Eksperimen\AduManis\Data Dummy Pengukuran Persil Tanah\Data Dummy Pengukuran Persil Tanah Cleaned5', ShapeType = 5)
w.field('NIB', 'N')
for NIBPersil, coordinates in TitikAvg.items():
    w.record(NIB = NIBPersil)
    w.poly([coordinates])
w.close()
