import folium
import json

def crearMapa(ordenes):
    stageFile = open("./Ordenes.json")
    stageData = json.load(stageFile)

    rowP = stageData[ordenes[0]]
    lat = rowP['Latitude']
    long2 = rowP['Longitude']
    m = folium.Map(location=[lat, long2], zoom_start=12)

    colors=["black","red","yellow","purple","green","black"]
    
    centinela=True
    cont=0
    c=0
    col=-1
    points=[]
    print(ordenes)
    while (cont)<len(ordenes):
        row = stageData[ordenes[cont]]
        lat1 = row['Latitude']
        long1 = row['Longitude']
        points.append(tuple([lat1,long1]))
        folium.Marker(tuple([lat1,long1]), popup="Orden "+str(ordenes[cont])).add_to(m)
        if(ordenes[cont]==0):
            c+=1
            if(c==1):
                col+=1
                c=-1
        if (cont !=0 and (cont%2-1)==0):

            folium.PolyLine(points,color=colors[col], weight=4, opacity=1).add_to(m)
            points=[]

        
        
        
        cont+=1
    m.save("prueba5.html")

