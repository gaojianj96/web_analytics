import csv
import ast
import dateutil.parser
import datetime
import math

from collections import OrderedDict

def mean_times(timeList):
    sum = 0
    for time in timeList:
        sum += (time - datetime.datetime(1970, 1, 1)).total_seconds()
    med = sum // len(timeList)
    return datetime.datetime.fromtimestamp(med).strftime('%Y-%m-%d %H:%M:%S')

def date2float(dateTime):
    return (dateTime-datetime.datetime(1970,1,1)).total_seconds()

class DataFrame(object):

    @classmethod
    def from_csv(cls, file_path, delimiting_character=',', quote_character='"'):
        with open(file_path, 'rU') as infile:
            reader = csv.reader(infile, delimiter=delimiting_character, quotechar=quote_character)
            data = []

            for row in reader:
                data.append(row)

            return cls(list_of_lists=data)

    @staticmethod
    def convert_Value_Type(dataConvert,origin=[]):
        # convert value type
        for j in range(len(dataConvert[0])):
            if origin!=[]:
                type_col=type(origin.data[0][origin.header[j]])
            else:
                type_col = str
                try:
                    type0 = type(ast.literal_eval(dataConvert[0][j]))
                    type1 = type(ast.literal_eval(dataConvert[1][j]))
                    type2 = type(ast.literal_eval(dataConvert[2][j]))
                    if (type0 == type1 or type0 == type2):
                        type_col = type0
                    elif (type1 == type2):
                        type_col = type1
                except:
                    try:
                        dateutil.parser.parse(dataConvert[0][j])
                        dateutil.parser.parse(dataConvert[1][j])
                        dateutil.parser.parse(dataConvert[2][j])
                        type_col = datetime.datetime
                    except:
                        pass

            for i in range(len(dataConvert)):
                try:  # numeric
                    if (type_col == int):
                        dataConvert[i][j] = int(dataConvert[i][j].replace(',', '').replace('"', ''))
                    elif (type_col == float):
                        dataConvert[i][j] = float(dataConvert[i][j].replace(',', '').replace('"', ''))
                    elif (type_col == datetime.datetime):
                        dataConvert[i][j] = dateutil.parser.parse(dataConvert[i][j])
                except:
                    pass
        return dataConvert

    def __init__(self, list_of_lists, header=True):

        # no duplicate column
        header_tmp = []
        for header_ele in list_of_lists[0]:
            if header_ele not in header_tmp:
                header_tmp.append(header_ele)
            else:
                raise Exception("No duplicates of header are allowed")

        #stripe blank
        for i in range(len(list_of_lists)):
            for j in range(len(list_of_lists[i])):
                list_of_lists[i][j]=list_of_lists[i][j].strip()


        if header:
            self.header = list_of_lists[0]
            self.data = list_of_lists[1:]
        else:
            self.header = ['column' + str(index + 1) for index, column in enumerate(list_of_lists[0])]
            self.data = list_of_lists

        self.data=self.convert_Value_Type(self.data)

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            return [row[item] for row in self.data]

        # this is for rows and columns
        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):

                if isinstance(item[0], list):
                    rowz = [row for index, row in enumerate(self.data) if index in item[0]]
                else:
                    rowz = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return [[column_value for index, column_value in enumerate([value for value in row.itervalues()]) if index in item[1]] for row in rowz]
                    elif all([isinstance(thing, (str, unicode)) for thing in item[1]]):
                        return [[row[column_name] for column_name in item[1]] for row in rowz]
                    else:
                        raise TypeError('What the hell is this?')

                else:
                    return [[value for value in row.itervalues()][item[1]] for row in rowz]
            else:
                if isinstance(item[1], (int, slice)):
                    return [[value for value in row.itervalues()][item[1]] for row in self.data[item[0]]]
                elif isinstance(item[1], (str, unicode)):
                    return [row[item[1]] for row in self.data[item[0]]]
                else:
                    raise TypeError('I don\'t know how to handle this...')

        # only for lists of column names
        elif isinstance(item, list):
            return [[row[column_name] for column_name in item] for row in self.data]

    def get_rows_where_column_has_value(self, column_name, value, index_only=False):
        if index_only:
            return [index for index, row_value in enumerate(self[column_name]) if row_value==value]
        else:
            return [row for row in self.data if row[column_name]==value]

    def min(self, column_name):
        list_tmp = self[column_name]
        if isinstance(list_tmp[0], (int,float,datetime.datetime)):
            return min(list_tmp)
        else:
            raise TypeError("The column contains other types! Cannot calculate its min")

    def max(self, column_name):
        list_tmp = self[column_name]
        print self.data
        if isinstance(list_tmp[0], (int, float, datetime.datetime)):
            return max(list_tmp)
        else:
            raise TypeError("The column contains other types! Cannot calculate its max")

    def median(self, column_name):
        list_tmp = sorted(self[column_name])
        if isinstance(list_tmp[0], (int, float)):
            if len(list_tmp) % 2 == 1:
                return list_tmp[len(list_tmp) // 2]
            else:
                return (list_tmp[len(list_tmp) // 2 - 1] + list_tmp[len(list_tmp )// 2])/ 2.0
        elif isinstance(list_tmp[0], datetime.datetime):
            if len(list_tmp) % 2 == 1:
                return list_tmp[len(list_tmp) // 2]
            else:
                time1=(list_tmp[len(list_tmp) // 2 - 1]-datetime.datetime(1970,1,1)).total_seconds()
                time2=(list_tmp[len(list_tmp) // 2]-datetime.datetime(1970,1,1)).total_seconds()
                med=(time1+time2)//2
                return datetime.datetime.fromtimestamp(med).strftime('%Y-%m-%d %H:%M:%S')
        else:
            raise TypeError("The column contains other types! Cannot calculate its median")

    def mean(self, column_name):
        list_tmp = self[column_name]
        if isinstance(list_tmp[0], (int, float)):
            for i in range(len(list_tmp)):
                if not isinstance(list_tmp[i],(int,float)):
                    print i,list_tmp[i]
            sum_ls=float(sum(list_tmp))
            len_ls=len(list_tmp)
            return sum_ls//len_ls
        elif isinstance(list_tmp[0],datetime.datetime):
           return mean_times(list_tmp)
        else:
            raise TypeError("The column contains other types! Cannot calculate its mean")

    def std(self, column_name):
            list_tmp = self[column_name]
            if isinstance(list_tmp[0], (int, float)):
                mean=self.mean(column_name)
                variance = map(lambda t: (t - mean) ** 2, list_tmp)
                sum=0
                for i in variance:
                    sum+=i
                return math.sqrt(sum//len(variance))
            elif isinstance(list_tmp[0], datetime.datetime):
                mean = dateutil.parser.parse(mean_times(list_tmp))
                variance = map(lambda t: (date2float(t) -date2float(mean)) ** 2, list_tmp)#more modify
                sum = 0
                for i in variance:
                    sum += i
                return math.sqrt(sum // len(variance))
            else:
                raise TypeError("The column contains other types! Cannot calculate its std")

    def add_rows(self,rows):
        #check len
        for row in rows:
            if(len(row)!=len(self.header)):
                raise Exception("Length of added rows does not match with Dataframe")
        # stripe blank
        for i in range(len(rows)):
            for j in range(len(rows[i])):
                rows[i][j] = rows[i][j].strip()

        rows = DataFrame.convert_Value_Type(rows,self)
        rows = [OrderedDict(zip(self.header, row)) for row in rows]
        for row in rows:
            self.data.append(rows)

    def add_column(self, list_of_values, column_name):
        if len(list_of_values)!=len((self.data)):
            raise ValueError("The length of new column is not match with the Dataframe")

        # stripe blank
        column_name=column_name.strip()
        for i in range(len(list_of_values)):
            list_of_values[i] = list_of_values[i].strip()

        type_col = str
        try:
            type0 = type(ast.literal_eval(list_of_values[0]))
            type1 = type(ast.literal_eval(list_of_values[1]))
            type2 = type(ast.literal_eval(list_of_values[2]))
            if (type0 == type1 or type0 == type2):
                type_col = type0
            elif (type1 == type2):
                type_col = type1
        except:
            try:
                dateutil.parser.parse(list_of_values[0])
                dateutil.parser.parse(list_of_values[1])
                dateutil.parser.parse(list_of_values[2])
                type_col = datetime.datetime
            except:
                pass

        for i in range(len(list_of_values)):
            try:  # numeric
                if (type_col == int):
                    list_of_values[i] = int(list_of_values[i].replace(',', '').replace('"', ''))
                elif (type_col == float):
                    list_of_values[i] = float(list_of_values[i].replace(',', '').replace('"', ''))
                elif (type_col == datetime.datetime):
                    list_of_values[i] = dateutil.parser.parse(list_of_values[i])
            except:
                pass

        ordered_dict_data = []
        for row in list_of_values:
            ordered_dict_row = OrderedDict([(column_name, row)])
            ordered_dict_data.append(ordered_dict_row)

        self.header.append(column_name)
        # list_of_values = [OrderedDict(column_name, values) for values in list_of_values]
        # print  list_of_values
        self.header.append(column_name)
        for i in range(len(ordered_dict_data)):
            self.data[i].update((ordered_dict_data[i]))


"""Test code"""
infile = open('SalesJan2009.csv')
lines = infile.readlines()
lines = lines[0].split('\r')
data = [l.split(',') for l in lines]
things = lines[559].split('"')
data[559] = things[0].split(',')[:-1] + [things[1]] + things[-1].split(',')[1:]

data[0][0]="      "+data[0][0]+"   "

df = DataFrame(list_of_lists=data)
# get the 5th row
fifth = df[4]
sliced = df[4:10]
# get item definition for df [row, column]

col=[]
for i in range(len(df.data)):
    col.append("  "+str(i)+"   ")
print len(df.data[0])
df.add_column(col,"NUMBER")
print df.data[0]