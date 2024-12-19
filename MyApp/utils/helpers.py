import json

def get_index(lista,palabra):#el indice se puede obtener con el nombre porque es unico, pero no se puede obtener con este metodo el indice con el significado                           
    aux_count = 0            #porque este no es necesariamente unico
    for item in  lista:
        if item["word"] == palabra:
            return aux_count
        aux_count+=1
    return aux_count

def orden_H_L_index(lista):
    n = len(lista)
    aux = [(item["points"],item["translation"][0]) for item in lista]
    data = [item for item in range(n)]
    for i in range(n-1):       
        for j in range(n-1-i):
            if aux[j][0] > aux[j+1][0]:
                aux[j], aux[j+1] = aux[j+1], aux[j]
                data[j], data[j+1] = data[j+1], data[j]
    return aux,data

def filter_by_letter(lista, letra):
    filtrado =  [item for item in lista if item["word"].startswith(letra.lower())]
    return filtrado, len(filtrado)

def save_data(items, filename):
    with open(filename, 'w',encoding='utf-8') as file:
        json.dump(items, file,ensure_ascii=False, indent=4)

def get_color(puntos):
    if puntos>10:
        return "green"
    elif puntos >6:
        return "orange"
    else:
        return "red"

def load_data(filename):
    try:
        with open(filename, 'r',encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError as error_f:
        data = []
        # print(f"An exception occurred: {error_f}")
        # sys.exit(1)  # Exit the program with a status code of 1 indicating an error
    return data