import json
import pandas as pd
import tabula
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
from pdf2image import convert_from_path
import numpy as np
import re
import pdfplumber
import camelot



def pdftoimageee(pdf_path):
    # images = convert_from_path(pdf_path,last_page=1,poppler_path=r'C:\Users\rimpal\Downloads\poppler-0.67.0\bin')
    images = convert_from_path(pdf_path,last_page=1)
    return images[0]


def get_first_page(pdf_path):
    imagee = pdftoimageee(pdf_path)
    ll=['2 CONTRACINO','3 SOLICITATIONNO','2. CONTRA CT NO.',' 5 DAIE ISSUED','2. CONTRACT NUMBER','3. SOLICITATION NUMBER','5. DATE ISSUED','2. CONTRACT NO.','3. SOLICITATION NO.','5.DATE ISSUED','RATING','6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.','A. NAME'
        ,'C. E-MAIL ADDRESS','AREA CODE','AMENDMENT NO.','AMENDMENT NO','INUMBER','EXTENSION','DATE','20. AMOUNT','28. AWARD DATE','4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|','20 AMOUNT',
        '28 AWARDDAIE','28 AWARDDATE','18. OFFERDATE','18 OFFERDATE','18. OFFER DATE']
    pix = np.array(imagee)
    result = ocr.ocr(pix, cls=True)
    result=result[0]
    ammends=[]
    boxes = []
    datess=[]

    for line in result:
        if str(line[1][0]) in ll:
            line[0][2][1] = line[0][2][1] + 5
            line[0][3][1] = line[0][3][1] + 50
            boxes.append([line[0],line[1][0]])

    my_dict={'Contract Number':'','Solicitation Number':'','Solicitation Type':'','Date Issued':'',
             'REQUISITION/PURCHASE NUMBER':'','Email':'','RATING':'','Area Code':'','EXTENSION':'','Number':'',
             'AMENDMENT NO.':[],'Date':[],'Award Date':'','Award Amount':'','Offer Date':''}

    for r in result:

        for i in boxes:
            amend_list = ['AMENDMENT NO.','AMENDMENT NO']
            datelist = ['DATE']
            if i[1] in amend_list:
                if r[1][0] not in ll and (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(i[0][0][0]-r[0][0][0])<80:
                    ammends.append(r[1][0])
                    my_dict['AMENDMENT NO.']=ammends
            if i[1] in datelist:
                if r[1][0] not in ll and (0 <= (r[0][0][1] - i[0][0][1]) < 80) and 0 <= (i[0][0][0] - r[0][0][0]) < 80:
                    datess.append(r[1][0])
                    my_dict['Date'] = datess

            if (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(r[0][0][0]-i[0][0][0])<80 and r[1][0] not in ll :
                contract_listt=['2 CONTRACINO','2. CONTRACT NO.','2. CONTRACT NUMBER','2. CONTRA CT NO.']
                SOLICITATION_listt=['3 SOLICITATIONNO','3. SOLICITATION NUMBER','3. SOLICITATION NO.']
                Date_listt=['5.DATE ISSUED','5. DATE ISSUED',' 5 DAIE ISSUED']
                Purchase_list=['6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.']
                name_list=['A. NAME']
                emaill_list=['C. E-MAIL ADDRESS']
                area_list=['AREA CODE']
                number_list=['INUMBER']
                extension_list=['EXTENSION']
                datelist=['DATE']
                Soliciation_typeee = ['4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|']
                awardlist=['20. AMOUNT','20 AMOUNT']
                awarddatee=['28. AWARD DATE','28 AWARDDAIE','28 AWARDDATE']
                offerdatee=['18. OFFERDATE','18. OFFER DATE']


                # fulll_list=[contract_listt,SOLICITATION_listt,Date_listt,Purchase_list]
                # namess=['Contract Number','Solicitation Number']
                # for i in fulll_list:
                answer=r[1][0]
                if str(i[1]) in contract_listt:
                    name='Contract Number'
                elif str(i[1]) in SOLICITATION_listt:
                    name='Solicitation Number'
                elif str(i[1]) in Date_listt:
                    name='Date Issued'
                elif str(i[1]) in Purchase_list:
                    name='REQUISITION/PURCHASE NUMBER'
                elif  str(i[1]) in name_list:
                    name='Name'
                elif str(i[1]) in emaill_list:
                    name='Email'
                elif str(i[1]) in area_list:
                    name='Area Code'
                elif str(i[1]) in extension_list:
                    name='EXTENSION'
                elif str(i[1]) in number_list:
                    name='Number'
                elif str(i[1]) in Soliciation_typeee:
                    name = 'Solicitation Type'
                    # r[1][0]=list(r[1])
                    answer = (str(r[1][0]).split(' ', 1))[1]
                elif str(i[1]) in awardlist:
                    name='Award Amount'
                elif str(i[1]) in datelist:
                    datess.append(r[1][0])
                elif str(i[1]) in awarddatee:
                    # datess.append(r[1][0])
                    name='Award Date'
                elif str(i[1]) in offerdatee:
                    name='Offer Date'
                else:
                    name=str(i[1])
                if name=='AMENDMENT NO.':
                    my_dict[name] = ammends
                elif name=='Date':
                    my_dict[name]=datess
                else:
                    my_dict[name]=answer

                break

    return my_dict,result



def get_tabless_pages(pdf_path):
    method = ''
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        # Get number of pages
        # Enter code here
        String = "ITEM NO"
        String2="QUANTITY UNIT"
        String3="Item"
        String4="Unit Price"
        String5="Supplies/Service"
        string6="MAX UNIT"
        # Extract text and do the search
        table_pagess=[]
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search(String,Text):
                if re.search(string6,Text):
                    method='third'
                    table_pagess.append(i)
            if re.search(String,Text):
                if re.search(String2,Text):
                    method='first'
                    table_pagess.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5,Text):
                method='second'
                table_pagess.append(i)


    return table_pagess,method


def first_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,
            flavor='stream', edge_tol=500, pages=pagesss)

        tableess = []
        seconddd=False
        for table in tables:
            try:
                index_change=False
                df = table.df
                try:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
                except:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'AMOUNT']
                    seconddd=True
                tableess.append(table.df)
                indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index
                if len(indexxx) == 0:
                    indexxx = df.loc[df['ITEM NO'] == 'ITEM NO \nSUPPLIES/SERVICES'].index
                    index_change = True
                count = 0
                for i in indexxx:
                    dff = df.iloc[i + 1]
                    if seconddd==True:
                        sss = dff['UNIT'].split('\n')
                        if len(sss) > 1:
                            dff['UNIT PRICE'] = sss[1]
                        else:
                            dff['UNIT PRICE'] = ''
                    if index_change == True:
                        data_change = [dff['SUPPLIES/SERVICES'], dff['QUANTITY'], dff['UNIT']]
                        dff['QUANTITY'] = data_change[0]
                        dff['UNIT'] = data_change[1]
                        dff['UNIT PRICE'] = data_change[2]
                    json1 = dff.to_json()
                    aDict = json.loads(json1)
                    if indexxx[-1] == i:
                        full_text = []
                        ccc = df.iloc[(i + 2):]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])
                        str1 = ''.join(full_text)
                        aDict['SUPPLIES/SERVICES'] = str1
                        itemss.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])

                        str1 = ''.join(full_text)
                        count += 1
                        aDict['SUPPLIES/SERVICES'] = str1
                        itemss.append(aDict)
            except:
                pass
    except:
        pass
    return itemss


def third_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,
            flavor='stream', edge_tol=500, pages=pagesss)
        tableess = []

        for table in tables:
            df = table.df
            df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
            tableess.append(table.df)
            indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index

            count = 0
            for i in indexxx:
                dff = df.iloc[i + 2]
                json1 = dff.to_json()
                aDict = json.loads(json1)

                if indexxx[-1] == i:
                    full_text = []
                    ccc = df.iloc[(i + 2):]
                    for index, row in ccc.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])
                    str1 = ''.join(full_text)
                    aDict['SUPPLIES/SERVICES'] = str1
                    itemss.append(aDict)
                    count += 1
                else:
                    full_text = []
                    ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                    for index, row in ccc.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])

                    str1 = ''.join(full_text)
                    count += 1
                    aDict['SUPPLIES/SERVICES'] = str1
                    itemss.append(aDict)

    except:
        pass

    return itemss


def get_clausess(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        String = "ITEM NO"
        clauses_list=[]
        Months_list=['ggg','JAN','FEB','MAR',"APR",'MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        # Extract text and do the search
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()

            phoneNumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = phoneNumRegex.search(Text)
            try:
                if array.group():
                    phoneNumRegex2 = re.compile(r'\d{4}', flags=0)
                    gg = Text.split('\n')
                    for g in gg:

                        ggg = g.split(' ')
                        if phoneNumRegex.search(ggg[0]) and phoneNumRegex2.search(ggg[-1]):
                            if len(g)>20:
                                g=g.replace('(','')
                                g=g.replace(')','')
                                yy=g.split(' ')

                                if yy[-2] in Months_list:
                                    yy[-2]=yy[-1]+'-'+str(Months_list.index(yy[-2]))
                                    yy=yy[:-1]
                                    g=' '.join(yy)
                                if '/' in yy[-1]:
                                    # print('yess')
                                    month=yy[-1].split('/')[1]
                                    year=yy[-1].split('/')[2]
                                    yy[-1]=year+'-'+month
                                    g=' '.join(yy)
                                clauses_list.append(g)

            except:
                pass
    clausess_new_list = []
    for c in clauses_list:
        cc = c.split(' ')
        clausee = cc[0] + ' | ' + ' '.join(cc[1:-1]) + ' | ' + cc[-1]
        clausess_new_list.append(clausee)
    return clausess_new_list


def method2(pdf_path,pages):
    itemss_lsit=[]
    for p in pages:
        pp=p+10
        df = tabula.read_pdf(pdf_path, pages=str(p)+'-'+str(pp),
                             stream=True)
        tables_list = []
        tables = df
        count = 0
        data = []

        for t in tables:
            try:

                if count == 0:
                    value = t.columns
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    count += 1
                    tables_list.append(t)
                else:
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    tables_list.append(t)
            except:
                pass

    d = '.'.join(data)
    new_list = []
    d = d.replace('Firm Fixed Price', 'Firm Fixed Price fffff')
    d = d.replace('Cost No Fee', 'Cost No Fee fffff')
    d = d.split('fffff')
    for f in d:
        new_list.append(f)

    dff = pd.concat(tables_list, axis=0, ignore_index=True)
    vv = dff.loc[pd.isna(dff["Item"]), :].index

    for v in vv:
        if pd.notnull(dff['Unit Price'][v]):
            if pd.notnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v - 1, 3]) + ' ' + str(dff.iloc[v, 3])
            if pd.isnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v, 3])
        if pd.notnull(dff['Amount'][v]):
            if pd.notnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4]) + '\n' + str(dff.iloc[v + 1, 4])
            elif pd.isnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4])

    dff.dropna(thresh=2, axis=0, inplace=True)
    dff['Supplies/Services'] = new_list
    itemsss=dff.to_json(orient="index")
    # dff.to_csv('table3.csv')
    itemsss=json.loads(itemsss)
    for it in itemsss:
        itemss_lsit.append(itemsss[str(it)])
    return itemss_lsit


def main(pdf_path):
    #Getting values from first page
    mydict,result=get_first_page(pdf_path)

    #Getting page numbers which include tables and also a method
    pagess,methodd=get_tabless_pages(pdf_path)

    #functions based on various different methods
    if methodd=='first':
        iteemms=first_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif methodd=='second':
        iteemms=method2(pdf_path,pagess)
        mydict['items'] = iteemms
    elif methodd=='third':
        iteemms=third_method(pdf_path,pagess)
        mydict['items']=iteemms

    #getting clauses from pdf
    clausess=get_clausess(pdf_path)
    mydict['clauses']=clausess

    return mydict

