'''
Author: Kexin Shang (Jasmine) - RA
This File help to generate the series which originally from Old FAO Balance Sheets(1961-2013) and New Balance Sheets (2014-2017).
There are four functions which help you generate total 156 series from the Balance Sheets.
Before you run the functions, make sure you have these files below in your current folder:
    Aggregation for crop type.csv
    CountryConcordFAO.csv
    FAOBS.xlsx
    FAOBSCodeBook.xlsx
    FoodBalanceSheets_E_All_Data_(Normalized).csv -- Old Balance Sheet
    FoodBalanceSheets_E_All_Data_New.csv -- New Balance Sheet 
AND create a new folder in your current folder called: output -- this folder will save the series you generated.

To call the Functions 
import FAOBS
FAOBS.BSCode()
FAOBS.AGCrop()
FAOBS.AGMeat()
FAOBS.FruVeg()

'''

#Ag Series with Code in Source
def BSCode():
    import pandas as pd
    Country_Concord = pd.read_csv('CountryConcordFAO.csv')
    dt = pd.read_excel('FAOBS.xlsx',sheet_name = 'Code')
    #New
    df = pd.read_csv('FoodBalanceSheets_E_All_Data_New.csv',encoding="ISO-8859-1")
    #Old
    dd = pd.read_csv('FoodBalanceSheets_E_All_Data_(Normalized).csv',encoding="ISO-8859-1")
    Element = list(dt.Element.values)
    Item = list(dt.Item.values)
    Name = list(dt.Variable.values)
    y = list(dd.Year.unique())
    y.sort()
    for row in range(len(dt)):
        #New
        series = df.loc[(df['Element Code'] == Element[row]) & (df['Item Code'] == Item[row])]
        dropcol = ['Area Code', 'Item Code', 'Item', 'Element Code', 'Element', 'Unit','Y2014F','Y2015F','Y2016F','Y2017F']
        series = series.drop(columns = dropcol)
        series = series.merge(Country_Concord, left_on = 'Area', right_on = 'Area Name',how = 'right')
        series = series.drop(columns = ['Area Name','Area'])
        if dt.Formula[row] == '/1000':
            series['2014'] = series['Y2014']/1000
            series['2015'] = series['Y2015']/1000
            series['2016'] = series['Y2016']/1000
            series['2017'] = series['Y2017']/1000
        elif dt.Formula[row] == '*1000':
            series['2014'] = series['Y2014']*1000
            series['2015'] = series['Y2015']*1000
            series['2016'] = series['Y2016']*1000
            series['2017'] = series['Y2017']*1000
        else:
            series['2014'] = series['Y2014']
            series['2015'] = series['Y2015']
            series['2016'] = series['Y2016']
            series['2017'] = series['Y2017']
        series = series[['Country in Ifs','2014','2015','2016','2017']]

        #Old
        data = dd.loc[(dd['Element Code'] == Element[row]) & (dd['Item Code'] == Item[row])]
        dropcol = ['Area Code', 'Item Code', 'Item', 'Element Code', 'Element','Year Code', 'Unit','Flag']
        data = data.drop(columns = dropcol)
        if dt.Formula[row] == '/1000':
            data['FValue'] = data.Value/1000
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year')
        elif dt.Formula[row] == '*1000':
            data['FValue'] = data.Value*1000
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year')
        else:
            data = pd.pivot_table(data,values = 'Value', index = 'Area', columns = 'Year')
        data['Country'] = data.index
        data = data.reset_index()
        data = data.merge(Country_Concord, left_on = 'Country', right_on = 'Area Name',how = 'right')

        #Merge
        series = data.merge(series,left_on = 'Country in Ifs',right_on = 'Country in Ifs', how = 'outer')
        col = ['Country in Ifs'] + y + ['2014','2015','2016','2017']
        series[col].to_csv(f'output/{Name[row]}.csv')

        
#13 AGCrop        
def AGCrop():
    import pandas as pd
    import numpy as np
    Country_Concord = pd.read_csv('CountryConcordFAO.csv')
    dt = pd.read_excel('FAOBS.xlsx',sheet_name = 'Agg')
    dt = dt[dt['Crop Type'] == 'Crop']
    dt = dt.reset_index()
    Element = list(dt.Element.values)
    Name = list(dt.Variable.values)

    Agg4Type = pd.read_csv('Aggregation for crop type.csv')
    Crop = Agg4Type[Agg4Type['Code Name']=='Crops']
    CropNo = list(Crop['Code no'].unique())
    BSCode = pd.read_excel('FAOBSCodeBook.xlsx', sheet_name = 'Item Code')
    BSItemCode = list(BSCode['Item Code'].values)
    InBS = []
    for code in CropNo:
        if code in BSItemCode:
            InBS.append(code)

    #old
    dd = pd.read_csv('FoodBalanceSheets_E_All_Data_(Normalized).csv',encoding="ISO-8859-1")
    y = list(dd.Year.unique())
    y.sort() 
    oldlist = []
    for i,code in enumerate(InBS):
        old = dd.loc[dd['Item Code'] == code]
        oldlist.append(old)
    old = pd.concat(oldlist)

    #new
    df = pd.read_csv('FoodBalanceSheets_E_All_Data_New.csv',encoding="ISO-8859-1")
    df = df[['Area','Item Code','Element Code', 'Y2014', 'Y2015', 'Y2016', 'Y2017']]
    newlist = []
    for code in InBS:
        new = df.loc[df['Item Code'] == code]
        newlist.append(new)
    new = pd.concat(newlist)
    new = new.drop(['Item Code'], axis = 1)
    new = new.groupby(['Area', 'Element Code']).sum(min_count = 1)
    new = new.reset_index()

    for row in range(len(dt)):
        #Old
        data = old.loc[old['Element Code'] == Element[row]]
        data = data.drop(['Area Code','Item','Item Code','Element','Element Code','Year','Unit','Flag'], axis =1)
        #data = old
        if dt.Formula[row] == '*1000':
            data['FValue'] = data['Value']*1000
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])
        elif dt.Formula[row] == '*1000/365':
            data['FValue'] = data['Value']*1000/365
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])
        else:
            data = pd.pivot_table(data,values = 'Value', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])

        data['Country'] = data.index
        data = data.reset_index()
        data = data.merge(Country_Concord, left_on = 'Country', right_on = 'Area Name',how = 'right')
        data = data[['Country in Ifs',('sum', 1961), ('sum', 1962), ('sum', 1963),
           ('sum', 1964), ('sum', 1965), ('sum', 1966), ('sum', 1967),
           ('sum', 1968), ('sum', 1969), ('sum', 1970), ('sum', 1971),
           ('sum', 1972), ('sum', 1973), ('sum', 1974), ('sum', 1975),
           ('sum', 1976), ('sum', 1977), ('sum', 1978), ('sum', 1979),
           ('sum', 1980), ('sum', 1981), ('sum', 1982), ('sum', 1983),
           ('sum', 1984), ('sum', 1985), ('sum', 1986), ('sum', 1987),
           ('sum', 1988), ('sum', 1989), ('sum', 1990), ('sum', 1991),
           ('sum', 1992), ('sum', 1993), ('sum', 1994), ('sum', 1995),
           ('sum', 1996), ('sum', 1997), ('sum', 1998), ('sum', 1999),
           ('sum', 2000), ('sum', 2001), ('sum', 2002), ('sum', 2003),
           ('sum', 2004), ('sum', 2005), ('sum', 2006), ('sum', 2007),
           ('sum', 2008), ('sum', 2009), ('sum', 2010), ('sum', 2011),
           ('sum', 2012), ('sum', 2013)]]
        data.columns = ['Country in Ifs'] + y
        #New
        series = new.loc[new['Element Code'] == Element[row]]
        if dt.Formula[row] == '*1000/365':
            series['2014'] = series['Y2014']*1000/365
            series['2015'] = series['Y2015']*1000/365
            series['2016'] = series['Y2016']*1000/365
            series['2017'] = series['Y2017']*1000/365
        elif dt.Formula[row] == '*1000':
            series['2014'] = series['Y2014']*1000
            series['2015'] = series['Y2015']*1000
            series['2016'] = series['Y2016']*1000
            series['2017'] = series['Y2017']*1000
        else:
            series['2014'] = series['Y2014']
            series['2015'] = series['Y2015']
            series['2016'] = series['Y2016']
            series['2017'] = series['Y2017']
        series = series.merge(Country_Concord,left_on = 'Area', right_on = 'Area Name',how = 'right')
        #Merge
        series = data.merge(series,left_on = 'Country in Ifs',right_on = 'Country in Ifs', how = 'outer')
        col = ['Country in Ifs'] + y + ['2014','2015','2016','2017']
        series = series.sort_values(by ='Country in Ifs')
        series[col].to_csv(f'output/{Name[row]}.csv')

        
#13 AGMeat
def AGMeat():
    import pandas as pd
    import numpy as np
    Country_Concord = pd.read_csv('CountryConcordFAO.csv')
    dt = pd.read_excel('FAOBS.xlsx',sheet_name = 'Agg')
    dt = dt[dt['Crop Type'] == 'Meat']
    dt = dt.reset_index()
    Element = list(dt.Element.values)
    Name = list(dt.Variable.values)

    Agg4Type = pd.read_csv('Aggregation for crop type.csv')
    Crop = Agg4Type[Agg4Type['Code Name']=='Meat']
    CropNo = list(Crop['Code no'].unique())
    BSCode = pd.read_excel('FAOBSCodeBook.xlsx', sheet_name = 'Item Code')
    BSItemCode = list(BSCode['Item Code'].values)
    InBS = []
    for code in CropNo:
        if code in BSItemCode:
            InBS.append(code)

    #old
    dd = pd.read_csv('FoodBalanceSheets_E_All_Data_(Normalized).csv',encoding="ISO-8859-1")
    y = list(dd.Year.unique())
    y.sort() 
    oldlist = []
    for i,code in enumerate(InBS):
        old = dd.loc[dd['Item Code'] == code]
        oldlist.append(old)
    old = pd.concat(oldlist)

    #new
    df = pd.read_csv('FoodBalanceSheets_E_All_Data_New.csv',encoding="ISO-8859-1")
    df = df[['Area','Item Code','Element Code', 'Y2014', 'Y2015', 'Y2016', 'Y2017']]
    newlist = []
    for code in InBS:
        new = df.loc[df['Item Code'] == code]
        newlist.append(new)
    new = pd.concat(newlist)
    new = new.drop(['Item Code'], axis = 1)
    new = new.groupby(['Area', 'Element Code']).sum(min_count = 1)
    new = new.reset_index()

    for row in range(len(dt)):
        #Old
        data = old.loc[old['Element Code'] == Element[row]]
        data = data.drop(['Area Code','Item','Item Code','Element','Element Code','Year','Unit','Flag'], axis =1)
        #data = old
        if dt.Formula[row] == '*1000':
            data['FValue'] = data['Value']*1000
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])
        elif dt.Formula[row] == '*1000/365':
            data['FValue'] = data['Value']*1000/365
            data = pd.pivot_table(data,values = 'FValue', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])
        else:
            data = pd.pivot_table(data,values = 'Value', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])

        data['Country'] = data.index
        data = data.reset_index()
        data = data.merge(Country_Concord, left_on = 'Country', right_on = 'Area Name',how = 'right')
        data = data[['Country in Ifs',('sum', 1961), ('sum', 1962), ('sum', 1963),
           ('sum', 1964), ('sum', 1965), ('sum', 1966), ('sum', 1967),
           ('sum', 1968), ('sum', 1969), ('sum', 1970), ('sum', 1971),
           ('sum', 1972), ('sum', 1973), ('sum', 1974), ('sum', 1975),
           ('sum', 1976), ('sum', 1977), ('sum', 1978), ('sum', 1979),
           ('sum', 1980), ('sum', 1981), ('sum', 1982), ('sum', 1983),
           ('sum', 1984), ('sum', 1985), ('sum', 1986), ('sum', 1987),
           ('sum', 1988), ('sum', 1989), ('sum', 1990), ('sum', 1991),
           ('sum', 1992), ('sum', 1993), ('sum', 1994), ('sum', 1995),
           ('sum', 1996), ('sum', 1997), ('sum', 1998), ('sum', 1999),
           ('sum', 2000), ('sum', 2001), ('sum', 2002), ('sum', 2003),
           ('sum', 2004), ('sum', 2005), ('sum', 2006), ('sum', 2007),
           ('sum', 2008), ('sum', 2009), ('sum', 2010), ('sum', 2011),
           ('sum', 2012), ('sum', 2013)]]
        data.columns = ['Country in Ifs'] + y
        #New
        series = new.loc[new['Element Code'] == Element[row]]
        if dt.Formula[row] == '*1000/365':
            series['2014'] = series['Y2014']*1000/365
            series['2015'] = series['Y2015']*1000/365
            series['2016'] = series['Y2016']*1000/365
            series['2017'] = series['Y2017']*1000/365
        elif dt.Formula[row] == '*1000':
            series['2014'] = series['Y2014']*1000
            series['2015'] = series['Y2015']*1000
            series['2016'] = series['Y2016']*1000
            series['2017'] = series['Y2017']*1000
        else:
            series['2014'] = series['Y2014']
            series['2015'] = series['Y2015']
            series['2016'] = series['Y2016']
            series['2017'] = series['Y2017']
        series = series.merge(Country_Concord,left_on = 'Area', right_on = 'Area Name',how = 'right')
        #Merge
        series = data.merge(series,left_on = 'Country in Ifs',right_on = 'Country in Ifs', how = 'outer')
        col = ['Country in Ifs'] + y + ['2014','2015','2016','2017']
        series = series.sort_values(by ='Country in Ifs')
        series[col].to_csv(f'output/{Name[row]}.csv')
        
        
#2 FruVeg
def FruVeg():
    import pandas as pd
    import numpy as np
    Country_Concord = pd.read_csv('CountryConcordFAO.csv')
    dt = pd.read_excel('FAOBS.xlsx',sheet_name = 'FruVeg')
    Element = list(dt.Element.values)
    Name = list(dt.Variable.values)

    FruVeg = [2918,2919]

    #old
    dd = pd.read_csv('FoodBalanceSheets_E_All_Data_(Normalized).csv',encoding="ISO-8859-1")
    y = list(dd.Year.unique())
    y.sort() 
    oldlist = []
    for i,code in enumerate(FruVeg):
        old = dd.loc[dd['Item Code'] == code]
        oldlist.append(old)
    old = pd.concat(oldlist)


    #new
    df = pd.read_csv('FoodBalanceSheets_E_All_Data_New.csv',encoding="ISO-8859-1")
    df.columns = ['Area Code', 'Area', 'Item Code', 'Item', 'Element Code', 'Element',
           'Unit', 2014, 'Y2014F', 2015, '2015F', 2016, 'Y2016F',
           2017, 'Y2017F']
    df = df[['Area','Item Code','Element Code', 2014, 2015, 2016, 2017]]
    newlist = []
    for code in FruVeg:
        new = df.loc[df['Item Code'] == code]
        newlist.append(new)
    new = pd.concat(newlist)
    new = new.drop(['Item Code'], axis = 1)
    new = new.groupby(['Area', 'Element Code']).sum(min_count = 1)
    new = new.reset_index()

    for row in range(len(dt)):
        #Old
        data = old.loc[old['Element Code'] == Element[row]]
        data = data.drop(['Area Code','Item','Item Code','Element','Element Code','Year','Unit','Flag'], axis =1)
        data = pd.pivot_table(data,values = 'Value', index = 'Area', columns = 'Year Code',aggfunc=[np.sum])
        data['Country'] = data.index
        data = data.reset_index()
        data = data.merge(Country_Concord, left_on = 'Country', right_on = 'Area Name',how = 'right')
        data = data[['Country in Ifs',('sum', 1961), ('sum', 1962), ('sum', 1963),
           ('sum', 1964), ('sum', 1965), ('sum', 1966), ('sum', 1967),
           ('sum', 1968), ('sum', 1969), ('sum', 1970), ('sum', 1971),
           ('sum', 1972), ('sum', 1973), ('sum', 1974), ('sum', 1975),
           ('sum', 1976), ('sum', 1977), ('sum', 1978), ('sum', 1979),
           ('sum', 1980), ('sum', 1981), ('sum', 1982), ('sum', 1983),
           ('sum', 1984), ('sum', 1985), ('sum', 1986), ('sum', 1987),
           ('sum', 1988), ('sum', 1989), ('sum', 1990), ('sum', 1991),
           ('sum', 1992), ('sum', 1993), ('sum', 1994), ('sum', 1995),
           ('sum', 1996), ('sum', 1997), ('sum', 1998), ('sum', 1999),
           ('sum', 2000), ('sum', 2001), ('sum', 2002), ('sum', 2003),
           ('sum', 2004), ('sum', 2005), ('sum', 2006), ('sum', 2007),
           ('sum', 2008), ('sum', 2009), ('sum', 2010), ('sum', 2011),
           ('sum', 2012), ('sum', 2013)]]
        data.columns = ['Country in Ifs'] + y
        #New
        series = new.loc[new['Element Code'] == Element[row]]
        series = series.merge(Country_Concord,left_on = 'Area', right_on = 'Area Name',how = 'right')
        #Merge
        series = data.merge(series,left_on = 'Country in Ifs',right_on = 'Country in Ifs', how = 'outer')
        col = ['Country in Ifs'] + y + [2014,2015,2016,2017]
        series = series.sort_values(by ='Country in Ifs')
        series[col].to_csv(f'output/{Name[row]}.csv')