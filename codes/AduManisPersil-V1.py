# Import libraries
import shapefile as sf
import numpy as np
import pandas as pd


numPersilControl = int(input('Jumlah persil sebagai kontrol:'))
nibcontrol =[]
for i in range(numPersilControl):
    nibcontrol.append(input('Nomor Induk Bidang :'))

print(nibcontrol)   
tolerance = float(input('Nilai Toleransi Residu Titik Batas:'))

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
Xcen = 0
Ycen = 0
numObs = 0
numControl = 0
for i in range(numParcels):
    PointID = 0
    NIB = Attributes[i][NIBindex]
    isControl = False
    if NIB in nibcontrol:
        isControl = True
    for n in range(len(Features[i].points)-1):
        PointID += 1
        Point = [NIB, PointID, Features[i].points[n][0], Features[i].points[n][1], isControl]
        Points.append(Point)
        Xcen = Xcen + Features[i].points[n][0]
        Ycen = Ycen + Features[i].points[n][1]
        if not isControl:
            numObs = numObs + 1
        else:
            numControl = numControl + 1
    Xcen = Xcen/len(Features[i].points)
    Ycen = Ycen/len(Features[i].points)
        
for Point in Points:
    Point[2] = Point[2]-Xcen
    Point[3] = Point[3]-Ycen
    Point.append(Point[0]+'-'+str(Point[1]))


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

def block_adjustment_sparsity(nParcels, nPoints, nObs, tiePoints, Controls):
    # m adalah jumlah pengamatan
    m = nObs
    # n adalah jumlah parameter, yaitu jumlah foto di luar kontrol dengan masing2x vertex nya
    nControls = len(Controls)
    n = ((nParcels-nControls) * 4) + (nPoints * 2)
    A = np.zeros((m, n))
    F = np.zeros((m,1))
    NIBarray = []
    PointParamIdx = []
    ControlCoords = []
    #cek dulu baris mana saja yang merefer ke titik kontrol
    for (i, Points) in enumerate(tiePoints):
        for (j, Obs) in enumerate(Points[1]):
            NIB = Obs[0][:5]
            isKontrol = False
            if NIB in Controls:
                isKontrol = True
                PointParamIdx.append(i)
            if NIB not in NIBarray and NIB not in Controls:
                NIBarray.append(NIB)
            if (isKontrol == True):
                Xcontrol = Obs[1][0]
                Ycontrol = Obs[1][1]
                ControlCoords.append(Obs[1])
                
    #print(PointParamIdx)
    row = 0
    col = -1
    for (i, Points) in enumerate(tiePoints):
        #print(i, sub[1])
        if i not in PointParamIdx:
            col = col + 1
        for (j, Obs) in enumerate(Points[1]):
            NIB = Obs[0][:5]
            isKontrol = False
            if NIB in Controls:
                isKontrol = True

            if (isKontrol == False):
                idx = NIBarray.index(NIB)
                A[2 * row, (2 * nPoints) + (4 * idx)] = Obs[1][0]
                A[2 * row, (2 * nPoints) + (4 * idx) + 1] = -Obs[1][1]
                A[2 * row, (2 * nPoints) + (4 * idx) + 2] = 1
                A[2 * row, (2 * nPoints) + (4 * idx) + 3] = 0

                A[2 * row + 1, (2 * nPoints) + (4 * idx)] = Obs[1][1]
                A[2 * row + 1, (2 * nPoints) + (4 * idx) + 1] = Obs[1][0]
                A[2 * row + 1, (2 * nPoints) + (4 * idx) + 2] = 0
                A[2 * row + 1, (2 * nPoints) + (4 * idx) + 3] = 1

                if i not in PointParamIdx:
                    A[2 * row, 2 * col] = -1
                    A[2 * row + 1, 2 * col + 1] = -1
                if i in PointParamIdx:
                    F[2 * row,0] = ControlCoords[PointParamIdx.index(i)][0]
                    F[2 * row + 1,0] = ControlCoords[PointParamIdx.index(i)][1] 
                row = row + 1           
            
            #print(Obs, idx)
            

    #print(NIBarray)

            
    return A, F, ControlCoords, PointParamIdx


    
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
                if Euclidean(PointA, PointB) <= tolerance and Points[i][-1] not in TSSearched:
                    TS.append([Points[i][-1],Points[i][2:4]])
                    TSSearched.append(Points[i][-1])
                elif Euclidean(PointA, PointB) <= tolerance and Points[i][-1] in TSSearched:
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
numPoints = len(TitikSekawan) - numControl

#print(numObs*2)
#print(((numParcels-len(nibcontrol)) * 4) + (numPoints * 2))

numObs = numObs * 2
numControl = numControl * 2
numParams = ((numParcels-len(nibcontrol)) * 4) + (numPoints * 2)
print("Jumlah Pengamatan = ",numObs)
print("Jumlah Parameter = ", numParams)

if numParams > numObs:
    print("Jumlah Parameter lebih banyak dari jumlah pengamatan, pengolahan dihentikan!")
    exit;


MatriksA, MatriksF, CoordinatControl, IndexControl = block_adjustment_sparsity(numParcels, numPoints, numObs, TitikSekawan, nibcontrol)

#print(CoordinatControl)
#print(IndexControl)


#da = pd.DataFrame(MatriksA)
#da.to_excel(excel_writer = "D:/Eksperimen/AduManis/mata.xlsx")
#df = pd.DataFrame(MatriksF)
#df.to_excel(excel_writer = "D:/Eksperimen/AduManis/matf.xlsx")

#print("shape = ",np.shape(MatriksF))

MatriksAt = np.transpose(MatriksA)
MatriksAtA = np.mat(MatriksAt) * np.mat(MatriksA)
MatriksAtF = np.mat(MatriksAt) * np.mat(MatriksF)
X = np.linalg.solve(MatriksAtA, MatriksAtF)

                
# Merata-ratakan titik sekawan
TitikAvgTS = []
counter = 0
tiecoun = 0
for TS in TitikSekawan:
    if counter in IndexControl:
        Titik = CoordinatControl[IndexControl.index(counter)]       
        Xavg = Titik[0] + Xcen
        Yavg = Titik[1] + Ycen
    else:
        Xavg = X[tiecoun*2] + Xcen
        Yavg = X[tiecoun*2+1] + Ycen
        tiecoun = tiecoun+1
        
    for Titik in TS[1]:
        TitikAvgTS.append([Titik[0], Xavg, Yavg])
    counter = counter + 1

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
w = sf.Writer('D:\Eksperimen\AduManis\Data Dummy Pengukuran Persil Tanah\Data Dummy Pengukuran Persil Tanah Cleaned7', ShapeType = 5)
w.field('NIB', 'N')
for NIBPersil, coordinates in TitikAvg.items():
    w.record(NIB = NIBPersil)
    w.poly([coordinates])
w.close()
