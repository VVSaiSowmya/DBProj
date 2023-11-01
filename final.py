import re
from datetime import datetime

def is_integer(attr):
    try:
        int(attr)
        return True
    except ValueError:
        return False

def is_alphanumeric(attr):
    return bool(re.match("^[a-zA-Z0-9]*$", attr))

def is_date(attr):
    date_formats = [
        r'\d{4}-\d{2}-\d{2}',           # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}'            # MM/DD/YYYY
    ]
    for date_format in date_formats:
        if re.match(date_format, attr):
            try:
                datetime.strptime(attr, "%Y-%m-%d")
                return True
            except ValueError:
                return False

    return False

def is_email(attr):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
    return re.match(email_pattern, attr)

def check_datatypes(csv_filePath):
    import csv
    with open(f'{csv_filePath}', mode ='r')as file:
        csvFile = csv.reader(file)
        header = next(csvFile)
        row1 = next(csvFile)
        data_types = {}
        for i,j in zip(header, row1):
            if(is_integer(j)):
                data_types[i] = "INT"
            elif(is_alphanumeric(j)):
                data_types[i] = "VARCHAR(100)"
            elif(is_date(j)):
                data_types[i] = "DATE"
            elif(is_email(j)):
                data_types[i] = "VARCHAR(50)"
    return data_types

def check_1NF(csv_filePath):
    import csv
    with open(f'{csv_filePath}', mode ='r')as file:
        csvFile = csv.reader(file)
        res=[]
        for row in csvFile:
            for i in row:
                res.append(i.split(","))
        for i in res:
            x = str(i)
            if("," in x[2:-2]):
                return False
    return True

def convert_1NF(csv_filePath):  
    import csv
    with open(f'{csv_filePath}', mode ='r')as file:
        csvFile = csv.reader(file)
        res = []
        res.append(next(csvFile))
        c = 0
        for row in csvFile:
            x = row
            each_index = [item.split(',') for item in x]
            num_elements = [len(sublist) for sublist in each_index]
            total_combinations = 1
            for num in num_elements:
                total_combinations *= num
            for i in range(total_combinations):
                new_item = []
                for j in range(len(each_index)):
                    element_index = i % num_elements[j]
                    new_item.append(each_index[j][element_index])
                    i //= num_elements[j]
                res.append(new_item)
        return res

def check_2NF(FD,Key):
    if(check_1NF(csv_filePath)):
        for i in FD:
            F = i.split("->")
            if(F[0] not in Key):
                continue
            if("," in F[0]):
                inter = F[0].split(",")
                if(sorted(inter) != sorted(Key)):
                    return False
            else:
                if(sorted(F[0]) != sorted(Key)):
                    return False
        return True

def convert_to_2NF(FD, Key):
    tables = {}
    res_table = {}

    for fd in FD:
        lhs, rhs = fd.split('->')
        lhs = lhs.strip().split(',')
        rhs = rhs.strip().split(',')

        if(sorted(lhs)==sorted(Key)):
            if(tables.get('Candidate')==None):
                tables["Candidate"] = lhs
                tables["Candidate"].extend(rhs)
            else:
                tables["Candidate"].extend(rhs)
        
        if(set(sorted(lhs)).issubset(set(sorted(Key)))):
            if(len(lhs)==1):
                x = str(lhs[0])
                if(tables.get(x)==None):
                    tables[x] = lhs
                    tables[x].extend(rhs)
                else:
                    tables[x].extend(rhs)
        else:
            if(tables.get('Candidate')==None):
                tables["Candidate"] = lhs
                tables["Candidate"].extend(rhs)
            else:
                tables["Candidate"].extend(rhs)
    
    check_key = 0
    for table, attributes in tables.items():
        if(set(sorted(Key)).issubset(set(sorted(attributes)))):
            check_key = 1
    if(check_key == 0):
        tables["C"] = Key     
    return tables

def check_3nf(FD, Key):
    c_key = ""
    for i in Key:
        c_key += i
    for i in FD:
        FD_l, FD_r = i.split("->")
        if("," in FD_l):
            FD_l_other = FD_l.split(",")
            if(set(sorted(FD_l_other)).issubset(set(sorted(Key)))):
                continue
        elif(set(sorted(FD_l)).issubset(set(sorted(Key)))):
            continue
        elif("," in FD_r):
            FD_r_other = FD_r.split(",")
            if(set(sorted(FD_r_other)).issubset(set(sorted(Key)))):
                continue
        elif(set(sorted(FD_r)).issubset(set(sorted(Key)))):
            continue
        else:
            for x in FD:
                FD_ll, FD_rr = x.split("->")
                if(FD_l in FD_rr) and (FD_ll in c_key):
                    return False
    return True  

def generate_sql_queries(FD, Key, tables, data_types):
    sql_statements = []
    fd_lhs = []
    fd_rhs = []

    for fd in FD:
        lhs, rhs = fd.split('->')
        x = lhs.strip().split(',')
        for i in x:
            if(i not in fd_lhs):
                fd_lhs.append(i)
        y = rhs.strip().split(',')
        for i in y:
            if(i not in fd_rhs):
                fd_rhs.append(y)

    for table_name, columns in tables.items():
        foreign_query = ""
        query = f'CREATE TABLE {table_name} ('
    
        count_of_keys = 0
        for x in columns:
            if x in fd_lhs:
                count_of_keys += 1

        for i in range(len(columns)):
            attr = columns[i]
            query += f'{attr} {data_types.get(attr)}'
            if(count_of_keys==1) and (attr in fd_lhs):
                query += " PRIMARY KEY"
            elif(attr == table_name):
                query += " PRIMARY KEY"
            elif(attr in fd_lhs):
                foreign_query += f', FOREIGN KEY {attr} REFERENCES {attr}({attr})'
            if(i != (len(columns)-1)):
                query += ", "
        
        query += foreign_query
        query += ");"
    
        sql_statements.append(query)
    
    return sql_statements

print("Enter the csv file path:")
csv_filePath = input()
data_types = check_datatypes("Datasets\Sample.csv")
print(data_types)
if check_1NF(csv_filePath):
    print("In 1NF")
else:
    print("Not in 1NF")
res_1NF = convert_1NF(csv_filePath)
for i in res_1NF:
    print(i)
FD = []
print("Enter Functional Dependencies:   Eg(A->B, A,B->C, A->B,C)")
print("Enter 'Done' if completed")
i = 1
while(i):
    x = str(input())
    if(x=="DONE" or x=="done" or x == "Done"):
        i=0
    else:
        FD.append(x)
print("Enter Key:")
Key = input().split(",")
print(f'Given Functional Dependencies: \n{FD}')
print(f'Given Key: \n{Key}')
if(check_2NF(FD, Key)):
    print("In 2NF")
else:
    print("Not in 2NF")
