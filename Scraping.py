import pdfplumber
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd


nombre_archivo= "Kardex_21378146_C.pdf"
uc_totales = 0
cont = 0
texto=''
ano = []
graduado = False
semestres = []
lista = []
materias = []
ano_1985 = False
ano_2004 = False
regex_semestres = r"^(?:\d+|-) (?:I|U|\d{2})-\d{4}[a-zA-ZÀ-ÿ\u00f1\u00d1\d ().,:/ \n-]+(?:___|NOTA:)"
regex_periodo = r'(?:\d{2}|I|U)-\d{4}'
regex_ano = r'\d{4}'
regex_grupo = r"(\d{4}|\d{2}[A-Z]\d) [A-Z0-9]+ [a-zA-ZÀ-ÿ\u00f1\u00d1\d() -:]+ (OBLIGATORIA|SEMINARIO|TRABAJO ESPECIAL DE|ELECTIVA|COMPLEMENTARIA|LABORATORIO|SERVICIO COMUNITARIO|PASANTIA) (\d+) (1[0-9]|20|A|EQ)"

#Extraer PDF a Texto
with pdfplumber.open(nombre_archivo) as pdf:
        paginas=len(pdf.pages)
        for i in range(paginas):
                texto += pdf.pages[i].extract_text()

#Separar los semestres
matches = re.finditer(regex_semestres, texto, re.MULTILINE)
for matchNum, match in enumerate(matches, start=1):
    semestres.append(match.group())


#Separar cada semestres por sus materias en una lista de 5 campos : [Periodo, Codigo, Tipo, UC , Nota]
for i in range(len(semestres)): #Periodos del Semestre

        paux= ''
        periodo = ''

        paux= re.findall(regex_periodo,semestres[i], re.MULTILINE) #Guardar el Periodo del Semestres
        ano= re.findall(regex_ano,paux[0], re.MULTILINE)
        periodo = ano[0]
        if(int(periodo) >= 1985 and int(periodo) < 2000 ):
                ano_1985 = True
        if(int(periodo) >= 2004 ):
                ano_2004 = True

        result = re.sub(regex_periodo, '',semestres[i], 1, re.MULTILINE) #Eliminamos El Periodo en cada Semestres
        semestres[i] = result

        matches = re.finditer(regex_grupo,semestres[i], re.MULTILINE) #Separamos cada materia con sus campos de cada semestre
        for matchNum, match in enumerate(matches, start=1):
                cont +=1
                Codigo = ''
                Tipo = ''
                UC = ''
                Nota = ''

                Codigo = match.group(1)
                Tipo = match.group(2)
                UC = int(match.group(3))
                Nota =match.group(4)

                lista = [periodo,Codigo,Tipo,UC,Nota]
                materias.append(lista)
                if (Tipo == "TRABAJO ESPECIAL DE"):
                        graduado = True
                uc_totales += UC

if(graduado == False):
        obligatoria = 0
        electiva = 0
        complementaria = 0
        laboratorio = 0
        servicio_comunitario = 0
        pasantia = 0
        seminario = 0
        optativas = 0

        for i in range(len(materias)):
                if(materias[i][2] == "OBLIGATORIA"):
                        obligatoria += 1
                if(materias[i][2] == "ELECTIVA"):
                        electiva += 1
                if(materias[i][2] == "COMPLEMENTARIA"):
                        complementaria += 1
                if(materias[i][2] == "LABORATORIO"):
                        laboratorio += 1
                if(materias[i][2] == "PASANTIA"):
                        pasantia += 1
                if(materias[i][2] == "SEMINARIO"):
                        seminario += 1
                if(materias[i][2] == "SERVICIO COMUNITARIO"):
                        servicio_comunitario += 1
                if(materias[i][1] == ("2011") or materias[i][1] == ("6311") or materias[i][1] == ("6211") or materias[i][1] == ("6221")):
                        optativas += 1

        if ((obligatoria == 21) and (electiva >= 10) and (complementaria == 3) and (laboratorio >= 1) and (pasantia == 1) and (seminario == 1) and (servicio_comunitario == 2) and (optativas >= 2)):
                print("El alumno puede graduarse")
                print("Tiene: ",uc_totales," UC Aprobados")
                
        else:
                lista_obligatorias = [["8206" , False] , ["6201" , False] , ["6301" , False] , ["6106" , False] , ["8207" , False] , ["6202" , False] ,
                ["6107" , False] , ["6001" , False] , ["8208" , False] , ["6002" , False] , ["6108" , False] , ["6203" , False] , ["6104" , False] , 
                ["6204" , False] , ["6303" , False] , ["6004" , False] , ["0030" , False] , ["6204" , False] , ["6302" , False] , ["6109" , False] , 
                ["0031" , False] ] # OBLIGATORIAS

                for i in range(len(materias)):
                        for j in range(len(lista_obligatorias)):
                                if(materias[i][1] == lista_obligatorias[j][0]):
                                        lista_obligatorias[j][1] = True

                print("Al estudiante le faltan estas materias para Graduarse: ")

                if(obligatoria < 21 ):
                        print(21 - obligatoria," Obligatoria(s):")
                        for j in range(len(lista_obligatorias)):
                                if(lista_obligatorias[j][1] == False):
                                        print(lista_obligatorias[j][0])


                if(electiva < 10):
                        if(optativas < 2):
                                print(10 - electiva,": Electiva(s), de las cuales faltarian: ", 2-optativas," Optativa(s) Obligatorias")
                        elif(optativas >= 2):
                                print(10 - electiva,": Electiva(s)")
                if(complementaria < 3):
                        print(3 - complementaria,": Complementaria(s)")
                if(laboratorio == 0):
                        print("Laboratorio")
                if(seminario == 0):
                        print("Seminario")
                if(servicio_comunitario < 2):
                        print("Servicio Comunitario")
                if(pasantia == 0):
                        print("Pasantias")
                print("Trabajo Especial de Grado")
                print("Tiene: ",uc_totales," UC Aprobados")
else:
        if(ano_2004 == True):
                url_2004 = 'http://www.ciens.ucv.ve/jefedeptoec/pensum_2004.html'
                page_2004 = requests.get(url_2004)
                soup_2004 = BeautifulSoup(page_2004.content,'html.parser')

                a = list(soup_2004.find_all("tr", {"bgcolor" : "white"}))
                a += list(soup_2004.find_all("tr", {"bgcolor" : "lightblue"}))

                materias_2004 = []
                mats_2004 = []
                cods_2004 = []
                links_2004 = []

                for i in a:
                        materias_2004= str(i)
                        mat = materias_2004.find("<td>")+3
                        materias_2004 = materias_2004[mat:]
                        mat = materias_2004.find("<td>")+3
                        materias_2004 = materias_2004[mat:]
                        p = materias_2004.find("</td>")
                        numero = materias_2004[1:p]
                        mat = p
                        materias_2004 = materias_2004[mat:]
                        mat= materias_2004.find("<td")+3
                        materias_2004 = materias_2004[mat:]
                        p = materias_2004.find("</td>")
                        asignatura=materias_2004[1:p]
                        mat = p 
                        mat = printmat = materias_2004.find ("href=\"")
                        if(mat >= 0):
                                mat += 6
                                materias_2004 = materias_2004[mat:]
                                p=materias_2004.find("\"")
                                link=materias_2004[:p]
                                link = "http://www.ciens.ucv.ve/jefedeptoec/" + link
                        else:
                                link="Error"
                        mats_2004.append(asignatura)
                        cods_2004.append(numero)
                        links_2004.append(link)


        if(ano_1985 == True):
                url_1985 = 'http://www.ciens.ucv.ve/jefedeptoec/pensum_1985.html'
                page_1985 = requests.get(url_1985)
                soup_1985 = BeautifulSoup(page_1985.content,'html.parser')

                #materias_1985
                a_1985 = list(soup_1985.find_all ("tr", {"bgcolor" : "white"}))
                a_1985 += list(soup_1985.find_all ("tr", {"bgcolor" : "lightblue"}))
                materias_1985 = []
                mats_1985 = []
                cods_1985 = []
                urls_1985 = []
                for i in a_1985:
                        materias_1985 = str(i)
                        mat = materias_1985.find ("<td>")+3
                        materias_1985 = materias_1985[mat:]
                        mat = materias_1985.find ("<td>")+3
                        materias_1985 = materias_1985[mat:]
                        p = materias_1985.find("</td>")
                        numero = materias_1985[1:p]
                        mat = p
                        materias_1985 = materias_1985[mat:]
                        mat = materias_1985.find ("<td>")+3
                        materias_1985 = materias_1985[mat:]
                        p = materias_1985.find("</td>")
                        asignatura = materias_1985[1:p]
                        mat = p
                        mat = materias_1985.find ("href=\"")
                        if(mat >= 0):
                                mat += 6
                                materias_1985 = materias_1985[mat:]
                                p = materias_1985.find("\"")
                                link = materias_1985[:p]
                                if(link != "#"):
                                        link = "http://www.ciens.ucv.ve/jefedeptoec/" + link
                        else:
                                link = '#'
                        mats_1985.append(asignatura)
                        cods_1985.append(numero)
                        urls_1985.append(link)
        
        
                url_2000 = 'http://computacion.ciens.ucv.ve/escueladecomputacion/pensumdeestudiosdepregrado'
                page_2000 = requests.get(url_2000)
                soup_2000 = BeautifulSoup(page_2000.content,'html.parser')



                materias_2000 = soup_2000.find_all ('h3')
                mat_2000 = list()
                for i in materias_2000:
                        mat_2000.append(i.text) #
                mat_2000.remove(mat_2000[174])

                #Codigos del 1968-2000
                codigos_2000 = soup_2000.find_all ('p')
                cod_2000 = list()
                for i in codigos_2000:
                        cod_2000.append(i.text) 
                lcod_2000 = (re.findall("(\d{2}(?:[A-Z]\d|\d{2}b|\d{2}))",str(cod_2000))) #
                lcod_2000.remove(lcod_2000[174])

                #Links del 1968-2000
                enl_2000 = []
                for el in soup_2000.find_all('a',class_ = "btn btn-primary"):
                        enlace_2000 = (el.get('href'))
                        if(enlace_2000 != "#"):
                                enlace_2000 = "http://computacion.ciens.ucv.ve/escueladecomputacion/" + enlace_2000
                        enl_2000.append(enlace_2000) #
                enl_2000.remove(enl_2000[0])

                m2000 = []
                l2000 = []
                c2000 = []

                m1985 = []
                l1985 = []
                c1985 = []

                m1974 = []
                l1974 = []
                c1974 = []

                m1968 = []
                l1968 = []
                c1968 = []

                m2000 = mat_2000[0:91]
                c2000 = lcod_2000[0:91]
                l2000 = enl_2000[0:91]

                m1985 = mat_2000[91:129]
                c1985 = lcod_2000[91:129]
                l1985 = enl_2000[91:129]

                m1974 = mat_2000[129:149]
                c1974 = lcod_2000[129:149]
                l1974 = enl_2000[129:149]

                m1968 = mat_2000[149:174]
                c1968 = lcod_2000[149:174]
                l1968 = enl_2000[149:174]

        #Impresion Estudiantes                
        for i in range(len(materias)):
                error = False

                if (int(materias[i][0]) >= 2004): #2004
                        for k in range(len(cods_2004)):
                                if(materias[i][1] == cods_2004[k]):
                                        print(materias[i][0],"\t",cods_2004[k],"\t",mats_2004[k],"\t",links_2004[k])
                                        error = True

                elif(int(materias[i][0]) < 2004 and int(materias[i][0]) >= 2000 ): #2000
                        for k in range(len(c2000)):
                                if(materias[i][1] == c2000[k]):
                                        error = True
                                        if(l2000[k] == "#"):
                                                print(materias[i][0],"\t",c2000[k],"\t",m2000[k],"\t","Error")
                                                
                                        else:
                                                print(materias[i][0],"\t",c2000[k],"\t",m2000[k],"\t",e2000[k])

                elif(int(materias[i][0]) < 2000 and int(materias[i][0]) >= 1985 ): #1985
                        existe = False
                        numeral = False
                        encontrar = False
                        val = 0
                        vol = 0
                        for k in range(len(c1985)):
                                if(materias[i][1] == c1985[k]):
                                        error = True
                                        if(l1985[k] == "#"):
                                                numeral = True
                                                val= k
                                        else:
                                                
                                                existe = True
                                                print(materias[i][0],"\t",c1985[k],"\t",m1985[k],"\t",l1985[k])
                        if (existe == False):
                                for j in range(len(cods_1985)):
                                        if(materias[i][1] == cods_1985[j]):
                                                error = True
                                                if(urls_1985[j] == "#"):
                                                        encontrar = True
                                                        vol = j
                                                else:
                                                        print(materias[i][0],"\t",cods_1985[j],"\t",mats_1985[j],"\t",urls_1985[j])

                        if(numeral == True):
                                print(materias[i][0],"\t",c1985[val],"\t",m1985[val],"\t","Error")
                        if((encontrar == True) and (numeral != True)):
                                print(materias[i][0],"\t",cods_1985[vol],"\t",mats_1985[vol],"\t","Error")

                elif(int(materias[i][0]) < 1985 and int(materias[i][0]) >= 1974 ): #1974
                        for k in range(len(c1974)):
                                if(materias[i][1] == c1974[k]):
                                        error = True
                                        if(l1974[k] == "#"):
                                                print(materias[i][0],"\t",c1974[k],"\t",m1974[k],"\t","Error")
                                                
                                        else:
                                                print(materias[i][0],"\t",c1974[k],"\t",m1974[k],"\t",l1974[k])

                elif(int(materias[i][0]) < 1974 and int(materias[i][0]) >= 1968 ): #1968
                        for k in range(len(c1968)):
                                if(materias[i][1] == c1968[k]):
                                        error = True
                                if(l1968[k] == "#"):
                                        print(materias[i][0],"\t",c1968[k],"\t",m1968[k],"\t","Error")    
                                else:
                                        print(materias[i][0],"\t",c1968[k],"\t",m1968[k],"\t",l1968[k])
                if(error == False):
                        print(materias[i][0],"\t",materias[i][1],"\t\t","Error")
        print("Tiene: ",uc_totales * 15, " horas vistas a lo largo de la carrera")