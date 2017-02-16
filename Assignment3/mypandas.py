import csv
import ast
import dateutil.parser
import datetime
import math
from itertools import repeat

from collections import OrderedDict

def avg(list_of_values):
    return sum(list_of_values) / float(len(list_of_values))

def date2float(dateTime):
    return (dateTime-datetime.datetime(1970,1,1)).total_seconds()

def avg(list_of_values):
    return sum(list_of_values)/float(len(list_of_values))

class Series(list):
    def check_type(self,other):
        if (not isinstance(other,(int,float))) or (not isinstance(self[0],(int,float))):
            if not isinstance(self[0],type(other)):
                raise TypeError("The types do not match")

    def __eq__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item == other)

        return ret_list

    def __gt__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item >other)

        return ret_list

    def __lt__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item < other)

        return ret_list

    def __ge__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item >= other)

        return ret_list

    def __le__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item <= other)

        return ret_list

    def __ne__(self, other):
        self.check_type(other)
        ret_list = []

        for item in self:
            ret_list.append(item != other)

        return ret_list

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
                if isinstance(list_of_lists[i][j],(str,unicode)):
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
            return Series(self.data[item])

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            ret=[row[item] for row in self.data]
            return Series(ret)

        # this is for rows and columns
        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):

                if isinstance(item[0], list):
                    rowz = [row for index, row in enumerate(self.data) if index in item[0]]
                else:
                    rowz = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return Series([[column_value for index, column_value in enumerate([value for value in row.itervalues()]) if index in item[1]] for row in rowz])
                    elif all([isinstance(thing, (str, unicode)) for thing in item[1]]):
                        return Series([[row[column_name] for column_name in item[1]] for row in rowz])
                    else:
                        raise TypeError('What the hell is this?')

                else:
                    return Series([[value for value in row.itervalues()][item[1]] for row in rowz])
            else:
                if isinstance(item[1], (int, slice)):
                    return Series([[value for value in row.itervalues()][item[1]] for row in self.data[item[0]]])
                elif isinstance(item[1], (str, unicode)):
                    return Series([row[item[1]] for row in self.data[item[0]]])
                else:
                    raise TypeError('I don\'t know how to handle this...')

        # only for lists of column names
        elif isinstance(item, list):
            if isinstance(item[0],bool):
                return Series([self.data[index] for index, val in enumerate(item) if val==True])
            return Series([[row[column_name] for column_name in item] for row in self.data])

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

    def sum(self,column_name):
        sum_ls=0
        list_tmp = self[column_name]
        if isinstance(list_tmp[0], (int, float)):
            sum_ls = sum(list_tmp)
        elif isinstance(list_tmp[0], datetime.datetime):
            for time in list_tmp:
                sum_ls += (time - datetime.datetime(1970, 1, 1)).total_seconds()
        return float(sum_ls)

    def mean(self, column_name):
        if not isinstance(self[column_name][0], (int, float,datetime.datetime)):
            raise TypeError("The column contains other types! Cannot calculate its mean")
        sum_ls=self.sum(column_name)
        len_ls=float(len(self[column_name]))
        med=float(sum_ls/len_ls)
        if isinstance(self[column_name][0],(int,float)):
            return med
        elif isinstance(self[column_name][0],datetime.datetime):
           return datetime.datetime.fromtimestamp(med)

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
                mean = self.mean(column_name)
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
        for i in range(len(ordered_dict_data)):
            self.data[i].update((ordered_dict_data[i]))

    def sort_by(self, column_name, reverse=False):
        dict = self.data
        if isinstance(column_name,(str,unicode)) and isinstance(reverse,bool):
            dict = sorted(dict, key=lambda d: d[column_name], reverse=reverse)
        elif isinstance(column_name, list):
            keys=[]
            if isinstance(reverse, bool):
                for i in range(len(column_name)-1, -1, -1):
                    dict = sorted(dict, key=lambda d: d[column_name[i]], reverse=reverse)
            elif isinstance(reverse,list):
                if len(column_name)==len(reverse):
                    for i in range(len(column_name)-1,-1,-1):
                        dict = sorted(dict, key=lambda d: d[column_name[i]], reverse=reverse[i])
        if dict==self.data:
            raise ValueError("The arguments of sort_by are not valid")
        list_of_lists=[self.header]
        for d in dict:
            list_of_lists.append(d.values())
        return DataFrame(list_of_lists=list_of_lists,header=True)

    def __eq__(self, other):
        if len(self.header)!=len(other.header) or len(self)!=len(other):
            return False
        for col in range(len(self.header)):
            if self.header[col]!=other.header[col]:
                return False
            for row in range(len(self.data)):
                if self.data[row][col]!=self.data[row][col]:
                    return False

    @staticmethod
    def find_same(list_value):
        for index, value in enumerate(list_value):
            if value != list_value[0]:
                return index
        return len(list_value)

    def group_by(self,column_name,value_column,method):
        group_df=self.sort_by(column_name)
        group_N_end=True
        list_of_lists=[]
        header=[]
        group_by_value=[]
        group_by_column=[]
        start=[]
        end=[]
        column_index=0 #current level of group
        if isinstance(column_name, list):
            header = list(column_name)
            start = list(repeat(0, len(column_name)))
            end=list(repeat(len(self.data), len(column_name)))
        else:
            header.append(column_name)
            start = [0]
            end = [len(self.data)]
            column_name=[column_name]
        header.append(value_column)
        list_of_lists.append(header)
        while group_N_end:
            sub_N_end=True
            if start[column_index]==end[column_index]:
                if column_index==0:
                    if end[column_index]==len(self.data):
                        break
                else:
                    start[column_index-1]=end[column_index]
                    column_index-=1
                    continue
            while column_index<len(column_name):
                if column_index==0:
                    end_col=len(group_df.data)
                else:
                    end_col=end[column_index-1]
                end[column_index]=start[column_index]+DataFrame.find_same(group_df[column_name[column_index]][start[column_index]:end_col])
                column_index+=1

            # if(end[len]<start):
            #     end=len(group_df[column_name])
            #     group_N_end=False
            group_by_value.append(method(group_df[value_column][start[len(column_name)-1]:end[len(column_name)-1]]))
            group_by_column.append(group_df[column_name][start[len(column_name)-1]])
            start[len(column_name) - 1]=end[len(column_name) - 1]
            end[len(column_name) - 1]=end[len(column_name) - 2]
            column_index-=1 #column_index==len(column_name)
        for index in range(len(group_by_column)):
            row=[]
            for i in range(len(column_name)):
                row.append(group_by_column[index][i])
            row.append(group_by_value[index])
            list_of_lists.append(row)
        return DataFrame(list_of_lists)

"""Test code"""
infile = open('SalesJan2009.csv')
lines = infile.readlines()
lines = lines[0].split('\r')
data = [l.split(',') for l in lines]
things = lines[559].split('"')
data[559] = things[0].split(',')[:-1] + [things[1]] + things[-1].split(',')[1:]

df = DataFrame(list_of_lists=data)

gp1=df.group_by(['City', 'Payment_Type'], 'Price', avg)
gp2=df.group_by('Payment_Type', 'Price', avg)
# w = csv.writer(open("output.csv", "wb"),delimiter=",")
# w.writerow(gp.header)
# for d in gp.data:
#     w.writerow(d.values())
