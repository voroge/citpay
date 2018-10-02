# -*- coding: utf-8 -*-

import cx_Oracle
import pandas as pd
import datetime
import time
import reposit as rp
import string
import os

class Event:
    def __init__(self):
    # Конструктор.
    # Методы конструктора
        self.handlers = set()

    def handle(self, handler):
        """
            Реализация подписки.
        """
        # Добавление функций оповещения.
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        """
            Удаление функции оповещения
        """
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        """
            - Выполнение оповещения клиентов, исполнение функций
                прикреплённых к событию.
        """
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        """
            Возращает количество функций оповещения.
        """
        return len(self.handlers)

            # Переопределяем системные функции,
            # которые помогают нам переопределить логику
            # работы с операторами и другими стандартными функциями
        #Добавление
    __iadd__ = handle
        #Отнимание
    __isub__ = unhandle
        #Вызов
    __call__ = fire
        #Использование функции len.
    __len__  = getHandlerCount


class Tcitpay(object):

    def __init__(self):
        self.gdebug = False
        self.logcount = 0
        self.step = 10
        self.onlog = Event()

    def log(self, amessage):
        if self.gdebug:
            print(amessage + ": " + time.asctime(time.localtime(time.time())))
        else:
            try:
                f = open('citpay.log', 'a')
                f.write(amessage + ": " + time.asctime(time.localtime(time.time())) + '\n')
            finally:
                f.close()
        self.logcount += self.step
        self.onlog(self.logcount)

    def dprint(self, aobject):
        if self.gdebug:
            print(aobject)

    def load_data_from_oracle(self, asql, aconnstr, **parameters):
        conn = cx_Oracle.connect(aconnstr)
        cursor = conn.cursor()
        try:
            try:
                cursor.prepare(asql)
            except cx_Oracle.DatabaseError as exception:
                self.log('Failed to prepare cursor')
                self.log(exception)
                exit(1)
            try:
                self.log('Start query')
                cursor.execute(cursor.statement, parameters)
                self.log('End query')
                ltable = cursor.fetchall()
            except cx_Oracle.DatabaseError as exception:
                self.log('Failed to select records')
                self.log(exception)
                self.log(cursor.statement)
                # return False #Если произошла ошибка (нужно для отката транзакции)
                exit(1)
            # Создаем DataFrame на основе загруженных из Oracle данных
            # получаем название полей запроса
            lcols = [col_desc[0] for col_desc in cursor.description]
            ldf = pd.DataFrame(ltable, columns=lcols)
            # переименование столбцов в соответствие с последовательностью после удаления
            # df.columns=range(len(df.columns))
            # df.drop(0, axis=1, inplace=True)
            # df.columns = acols
            # заполняем пустые значения
            # df.fillna('', inplace=True)
            return ldf
        finally:
            cursor.close()
            conn.close()

    def getnextmonth(self, amonth, ayear):
        lmonth = int(amonth)+1
        if lmonth < 10:
            return '0' + str(lmonth) + '.' + ayear
        elif lmonth < 13:
            return str(lmonth) + '.' + ayear
        else:
            return '01.' + str(int(ayear)+1)

    def getmonthlypg(self, amonth, ayear):
        rp.gpgscenario = 'sce:OREP.KU.'+ayear+'.MONTHLY.'+amonth
        if 1 <= int(amonth) < 7:
            nmonth = '01'
        else:
            nmonth = '07'
        rp.gpkuscenario = 'sce:PREDEL.KU.'+ayear+'.'+nmonth
        rp.gpgtemplate = 'OREP.KU.'+ayear+'.MONTHLY.'+amonth
        rp.grepdate = '06.'+self.getnextmonth(amonth, ayear)
        rp.gdeldate = '01.01.'+ayear
        self.log(rp.gpgscenario + ', ' + rp.gpkuscenario + ', ' + rp.gpgtemplate + ', ' + rp.grepdate + ', ' + rp.gdeldate)

        lpar = {"param": rp.gpgscenario}
        ldf = self.load_data_from_oracle(rp.gscsql, rp.gconnstr, **lpar)
        pgid = int(ldf.iloc[0, 0])

        lpar = {"param": rp.gpkuscenario}
        ldf = self.load_data_from_oracle(rp.gscsql, rp.gconnstr, **lpar)
        pkuid = int(ldf.iloc[0, 0])

        self.log('pgid, pkuid :' + str(pgid) + ', ' + str(pkuid))

        lpar = {"srd": rp.grepdate, "sdd": rp.gdeldate, "spgt": rp.gpgtemplate, "spgs": pgid, "spkus": pkuid}
        ldf = self.load_data_from_oracle(rp.gmainsql, rp.gconnstr, **lpar)

        with pd.option_context('display.max_rows', None, 'display.max_columns', 7):
            self.dprint(ldf.to_string(index=True))

        return ldf

    def getmonthrange(self, amonth):
        # Работающий кусок кода, для формирования рейтинга по полугодиям
        # if amonth <7:
        #     startmonth = 1
        # else:
        #     startmonth = 7
        startmonth = 1
        llist = []
        for x in range(startmonth, amonth + 1):
            if x<10:
                llist.append('0'+str(x))
            else:
                llist.append(str(x))
        return llist

    def getregpg(self, amonth, ayear):
        mlist = self.getmonthrange(amonth)
        pdf = pd.DataFrame()
        for m in mlist:
            ldf = self.getmonthlypg(m, '2018')
            if len(pdf.columns) == 0:
                pdf['REGION_NAME']=ldf['REGION_NAME']
                pdf['RATING'] = ldf['RATING']
            else:
                pdf = pd.merge(pdf, ldf[['REGION_NAME', 'RATING']], left_on=['REGION_NAME'],
                                   right_on=['REGION_NAME'], suffixes=('', m), how='outer')
                # pdf.drop(['REGION_NAME_r'], axis=1, inplace=True)
        pdf['TOTAL_RATING'] = pdf.mean(axis=1).astype(int)
        ldf = pd.merge(ldf, pdf[['REGION_NAME', 'TOTAL_RATING']], left_on=['REGION_NAME'],
                       right_on=['REGION_NAME'], suffixes=('', mlist[0]), how='outer')
        ldf['PRC_LOSS_POP'] = round(ldf['PRC_LOSS_POP']).astype(int)
        ldf = ldf.sort_values(['TOTAL_RATING','RATING'],ascending=[False, False])
        ldf.insert(loc=0, column='N', value=range(1,len(ldf.index)+1))
        with pd.option_context('display.max_rows', None, 'display.max_columns', 7):
            self.dprint(ldf.to_string(index=True))
        return ldf

    def getfmt(self, awbook, afmt):
        try:
            return awbook.add_format(rp.dictfmt[afmt])
        except KeyError as e:
            # можно также присвоить значение по умолчанию вместо бросания исключения
            raise ValueError('Undefined value: {}'.format(e.args[0]))

    def col2num(self, col):
        num = 0
        for c in col:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num

    def num2col(self, n):
        """Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA."""
        name = ''
        while n > 0:
            n, r = divmod (n - 1, 26)
            name = chr(r + ord('A')) + name
        return name

    def to_excel(self, adf, acolprop, amonth, ayear, anow, afile):
        self.log(afile)
        self.log('Start')
        writer = pd.ExcelWriter(afile, engine='xlsxwriter',
                            datetime_format='dd.mm.yyyy hh:mm:ss',
                            date_format='dd.mm.yyyy')
        workbook=writer.book
        self.log('Create Excel Writer')
        #df=df.applymap(lambda s: s.decode('utf8') if isinstance(s, str) else s)
        nrows = len(adf.index)
        #Если данных нет (кол-во записей в DF =0), то файл не создаем
        if nrows!=0:
            #выгружаем основные данные в Excel
            adf.to_excel(writer, sheet_name='Дисциплина', header=False, index=False,
                            startrow=11, startcol=0, encoding='utf-8')
        worksheet = writer.sheets['Дисциплина']
        worksheet.hide_gridlines(2)
        worksheet.set_zoom(65)
        worksheet.set_column('A:' + self.num2col(len(adf.columns)+1), None, self.getfmt(workbook, 'data'))
        worksheet.merge_range('B2:G2', u'Рейтинг субъектов Российской Федерации по дисциплине предоставления отчетности'
                                       u' в рамках мониторинга "Информация об изменении размера платы граждан за '
                                       u'коммунальные услуги, связанная с установленными тарифами для населения и '
                                       u'нормативами потребления коммунальных услуг в разрезе организаций коммунального '
                                       u'комплекса и муниципальных образований субъектов РФ в ' + ayear + ' году" за '
                                       + rp.monthes[amonth] + ' ' + ayear + ' года',
                              self.getfmt(workbook, 'head1'))
        worksheet.set_row(1, 61.5)
        worksheet.merge_range('B3:G3',
                              u'Код шаблона: '+rp.gpgtemplate,
                              self.getfmt(workbook, 'head3'))
        worksheet.set_row(2, 27)
        worksheet.merge_range('B4:G4',
                              u'Дата окончания мониторинга: 05.'+rp.grepdate[3:],
                              self.getfmt(workbook, 'head3'))
        worksheet.write('H6', u'Подготовлено Информационно-техническим центром ФАС России c применением ФГИС ЕИАС',
                        self.getfmt(workbook, 'head2'))
        worksheet.write('H7', 'Отчет подготовлен по состоянию на %s  %s ч. %s мин. %s с.'
                        % (anow.strftime('%d.%m.%Y'), anow.strftime('%H'), anow.strftime('%M'), anow.strftime('%S')),
                        self.getfmt(workbook, 'head2'))

        worksheet.write('B5', u'Легенда:', self.getfmt(workbook, 'data'))
        worksheet.merge_range('B6:C6',u'Регионы, приславшие отчет без нарушений',
                              self.getfmt(workbook, 'legend'))
        worksheet.conditional_format('B6:C6', {'type': 'no_blanks', 'format': self.getfmt(workbook, 'cf_green')})
        worksheet.merge_range('B7:C7', u'Регионы, приславшие отчет с нарушениями',
                              self.getfmt(workbook, 'legend'))
        worksheet.conditional_format('B7:C7', {'type': 'no_blanks', 'format': self.getfmt(workbook, 'cf_orange')})
        worksheet.merge_range('B8:C8', u'Регионы, не приславшие отчет',
                              self.getfmt(workbook, 'legend'))
        worksheet.conditional_format('B8:C8', {'type': 'no_blanks', 'format': self.getfmt(workbook, 'cf_red')})
        worksheet.insert_image('H2', 'gerb_ch_b.png', {'x_scale': 0.05, 'y_scale': 0.05})

        adf.ADATE = adf.ADATE.astype(str)
        adf.columns = acolprop['names']
        for col_num, value in enumerate(adf.columns.values):
            worksheet.set_column(self.num2col(col_num + 1) + ':' + self.num2col(col_num + 1),
                                 acolprop['widthes'][col_num],
                                 self.getfmt(workbook, acolprop['col_format'][col_num]))
            worksheet.write(10, col_num, value, self.getfmt(workbook, 'header'))
        worksheet.conditional_format('A12:H' + str(len(adf.index)+11),
                                     {'type': 'formula',
                                      'criteria': '=$H12=100',
                                      'format': self.getfmt(workbook, 'cf_green')})
        worksheet.conditional_format('A12:H' + str(len(adf.index) + 11),
                                     {'type': 'formula',
                                      'criteria': '=AND($H12<100,$H12>0,$G12>0)',
                                      'format': self.getfmt(workbook, 'cf_orange')})
        worksheet.conditional_format('A12:H' + str(len(adf.index) + 11),
                                     {'type': 'formula',
                                      'criteria': '=$G12=0',
                                      'format': self.getfmt(workbook, 'cf_red')})

        worksheet.merge_range('B' + str(len(adf.index)+14) + ':F' + str(len(adf.index)+14),
                              u'В рейтинге не участвуют: Республика Крым, г. Севастополь и г. Байконур',
                              self.getfmt(workbook, 'data'))
        self.dprint(adf.dtypes)
        worksheet.merge_range('B' + str(len(adf.index) + 16) + ':G' + str(len(adf.index) + 16),
                              u'Количество регионов, получивших запрос регулятора: %d. Количество регионов приславших отчет без нарушений: %d (%d%%).'
                              % (len(adf.index), len(adf[adf.iloc[:, -1] == 100].index),
                                 round(len(adf[adf.iloc[:, -1] == 100].index)/len(adf.index)*100)),
                              self.getfmt(workbook, 'data'))

        writer.save()
        os.startfile(afile)

    def pgmain(self, amonth, ayear):
        self.logcount = 0
        self.step = 100/(2 + len(self.getmonthrange(amonth))*8)
        lnow = datetime.datetime.now()
        ldf = self.getregpg(amonth, ayear)
        self.to_excel(ldf, rp.colprop, amonth, ayear, lnow, '%s\\Дисциплина по мониторингу %s %s %s.xlsx'
               % (os.path.expanduser('~\\documents'), rp.gpgtemplate.replace('.','_'), lnow.strftime('%Y%m%d'), lnow.strftime('%H%M%S')))
        return ldf
