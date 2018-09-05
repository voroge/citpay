# -*- coding: utf-8 -*-

monthes = {1:  'январь',
           2:  'февраль',
           3:  'март',
           4:  'апрель',
           5:  'май',
           6:  'июнь',
           7:  'июль',
           8:  'август',
           9:  'сентябрь',
           10: 'октябрь',
           11: 'ноябрь',
           12: 'декабрь'
           }

gconnstr='analytics/analytics@fst_rac'

gscsql = 'select * from eas.data_scenarios where ROWNUM=1 AND name=:param'

# переменные в которых будут храниться основные параметры для главного запроса и выходной формы
# генерятся в основном коде в зависимости от месяца и года

gpgscenario = ''
gpkuscenario = ''
gpgtemplate = ''
grepdate = ''
gdeldate = ''
gyear = ''
gmonth = ''

gmainsql = """
        /*
          В мониторинге JKH12.PREDEL_KU_2014_LIST_MO содержатся предельные индексы изменения платы граждан, а также 
          информация по наличию в конкретном МО населения
          например для межселенных территорий плата граждан не устанавливается 
          l_existance принимает значения: 
              да
              исключить, отчётность предоставляется по муниципальному району, в состав которого входит муниципальное образование
              исключить, индекс не установлен
              исключить, отчётность предоставляется по муниципальным образованиям, входящим в муниципальный район
              исключить, на территории населению услуги не оказываются
          связь вышеуказанной таблицы с таблицами реестра не возможна напрямую через поле MO_ID, хотя оно там есть, 
          надо связывать через промежуточную таблицу eas.dictionary_values и поле dictionary_values_guid,
          аналогично делаем и для таблицы по плате граждан JKH12.NTKU12_M_LIST_MO
        */ 
        with
        consts as
          (select to_date(:srd,'dd.mm.yyyy') as report_date, to_date(:sdd, 'dd.mm.yyyy') as del_date, 
                  :spgt as pg_templ, :spgs as pg_scenario, 
                  :spkus as pku_scenario
           from dual),
        reg as
        ( 
          select b.code, b.region_id, b.region_name, c.oktmo_name as mr_oktmo, c.rst_mr_id, c.mr_name, 
                 a.oktmo_name as mo_oktmo, a.rst_mo_id, a.mo_id, a.mo_name,a.date_begin, a.date_end, d.l_existence, 
                 pg.mo_name as pg_mo, pc.total_ppl_count
          from 
            REESTR.RST_MO a
            cross join consts
            inner join REESTR.RST_REGION_FULL b on (a.region_id=b.region_id)
            inner join REESTR.RST_MR c on (a.rst_mr_id=c.rst_mr_id)
            inner join eas.dictionary_values vs on (a.dictionary_values_guid = vs.guid and vs.dictionaryid in (658, 680))-- 658-МО, 680-МР
            left join (select a.* from JKH12.PREDEL_KU_2014_LIST_MO a cross join consts b where a.scenario_id = b.pku_scenario) d on (vs.code = d.entity_code) --собирается 2 раза в год есть за 01 и 07 меcяца 2017
            inner join eas.dictionary_values vspg on (a.dictionary_values_guid = vspg.guid and vspg.dictionaryid in (658, 680))-- 658-МО, 680-МР
            left join (select a.* from JKH12.NTKU12_M_LIST_MO a cross join consts b where a.scenario_id = b.pg_scenario) pg on (vspg.code = pg.entity_code)
            left join WS_XLS_SOBR_KITCHEN.TBL_FSGS_POPULATION_2018 pc on (a.oktmo_name=pc.oktmo_name)
          where a.status<>'DELD' and b.status<>'DELD' and c.status<>'DELD' --статусы DELD ставятся только для ошибочных записей
                -- прекратившие деятельность МО надо отсекать по полю a.date_end
                and (a.date_end is null or a.date_end > consts.del_date) and (a.date_begin is null or a.date_begin < consts.del_date) 
                --and d.id is null --
                --выкидываем Крым наш и Байконур
                and a.region_id not in (2585, 2586, 2672)
                and ((not d.l_existence like 'исключить,%') or d.l_existence is null)  
          order by b.region_name, c.mr_name, a.mo_name
        ),
        ot as
        (
          select
              f.region,
              f.id as part_id,
              a.instant_date as instant_date,
              max(f.name) as part_name,
              min(b.adate) as adate, --это дата первого присланного шаблона, если нужна дата последнего присланного, то меняем функцию на max
              max(g.periodic_type) as periodic_type,
              max(g.id) as templ_id
          from
              eas.data_contexts a
          inner join
              eas.files b
          on
              a.source_file_id=b.id
          inner join
              eas.files c
          on
              b.parent_guid=c.guid
          inner join
              eas.users e
          on
              c.author=e.code
          inner join
              eas.participants f
          on
              e.participantid=f.id
          inner join
              eas.templates g
          on
              c.template=g.code
          where
              c.template in (select pg_templ from consts)
          group by
              f.region,
              a.instant_date,
              f.id
          order by
              a.instant_date,
              max(f.name)
        ),
        
        reg_sum as
        (
          select 
            reg.code, reg.region_name, sum(decode(reg.pg_mo,NULL,1,0)) as cnt_loss_mo, sum(decode(reg.pg_mo,NULL,reg.total_ppl_count,0)) as cnt_pop_loss_mo,
            count(reg.rst_mo_id) as cnt_mo, sum(reg.total_ppl_count) as cnt_pop_mo   
          from reg 
          group by reg.code, reg.region_name
        ),  
        reg_ot as
          (
          select reg_sum.code, reg_sum.region_name, reg_sum.cnt_loss_mo, reg_sum.cnt_pop_loss_mo, reg_sum.cnt_mo, reg_sum.cnt_pop_mo, ot.adate, 
                 consts.report_date-nvl(ot.adate,sysdate) as deltaabs, reg_sum.cnt_pop_loss_mo/reg_sum.cnt_pop_mo as part_loss_pop,
                 decode(sign(consts.report_date-nvl(ot.adate,sysdate)),-1,'Просрочен на ','Раньше срока на ')||trunc(ABS(consts.report_date-nvl(ot.adate,sysdate)))||' д. ' ||to_char(trunc(sysdate) + ABS(consts.report_date-nvl(ot.adate,sysdate)),'fmhh24" ч. "mi" мин. "ss" с."') delta, 
                 case 
                   when reg_sum.cnt_pop_loss_mo/reg_sum.cnt_pop_mo < 0.1 then reg_sum.cnt_pop_loss_mo/reg_sum.cnt_pop_mo*0.2
                   when reg_sum.cnt_pop_loss_mo/reg_sum.cnt_pop_mo >= 0.1 then reg_sum.cnt_pop_loss_mo/reg_sum.cnt_pop_mo*0.6
                 end as rate_pop,
                 case
                   when
                     consts.report_date-nvl(ot.adate,sysdate)>=0 then 0
                   when 
                     consts.report_date-nvl(ot.adate,sysdate)>-2 then (consts.report_date-nvl(ot.adate,sysdate))/(consts.report_date-sysdate)*0.1  
                   else
                     (consts.report_date-nvl(ot.adate,sysdate))/(consts.report_date-sysdate)*0.4      
                   end  as rate_expired 
          from
            reg_sum cross join consts left outer join ot on (reg_sum.code=ot.region)
          order by 
            ot.adate, reg_sum.region_name
          )
        select /*reg_ot.code,*/ reg_ot.region_name, reg_ot.cnt_loss_mo, reg_ot.part_loss_pop*100 as prc_loss_pop, /*reg_ot.cnt_pop_loss_mo, reg_ot.cnt_mo, reg_ot.cnt_pop_mo,*/ reg_ot.adate, 
               /*reg_ot.deltaabs,*/ reg_ot.delta, /*reg_ot.rate_pop, reg_ot.rate_expired,*/ trunc((1-reg_ot.rate_pop-reg_ot.rate_expired)*100) as rating
        from reg_ot
        order by 1-reg_ot.rate_pop-reg_ot.rate_expired desc, reg_ot.deltaabs desc """

dictfmt = {
        'data': {'font_name': 'Verdana',
                 'font_size': 12
                 },

        'legend': {'font_name': 'Verdana',
                   'font_size': 12,
                   'align': 'center',
                   'text_wrap': True
                   },

        'head1': {'font_name': 'Verdana',
                  'font_size': 12,
                  'align': 'center',
                  'bold': True,
                  'text_wrap': True
                  },

        'head2': {'font_name': 'Verdana',
                  'font_size': 12,
                  'align': 'right',
                  'italic': True
                  },

        'head3': {'font_name': 'Verdana',
                  'font_size': 12,
                  'align': 'center'
                  },

        'header': {'font_name': 'Verdana',
                   'font_size': 12,
                   'bold': True,
                   'text_wrap': True,
                   'valign': 'top',
                   'align': 'center',
                   'top': 1,
                   'left': 1,
                   'bottom': 2,
                   'right': 1
                   },

        'header1': {'font_name': 'Verdana',
                    'font_size': 10,
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'align': 'center',
                    'fg_color': '#C4D79B',
                    'top': 2,
                    'left': 1,
                    'bottom': 1,
                    'right': 2
                    },

        'num': {'font_name': 'Verdana',
                'font_size': 12,
                'text_wrap': True,
                'num_format': '#,##0'
                },

        'prc': {'font_name': 'Verdana',
                'font_size': 12,
                'text_wrap': True,
                'num_format': '0'
                },

        'date': {
                'font_name': 'Verdana',
                'font_size': 12,
                },

        'top': {'top': 2,
                'left': 1,
                'bottom': 1,
                'right': 1
                },

        'tcorner': {'top': 2,
                    'left': 1,
                    'bottom': 1,
                    'right': 2
                    },

        'bottom': {'top': 1,
                   'left': 1,
                   'bottom': 2,
                   'right': 1
                   },

        'right': {'top': 1,
                  'left': 1,
                  'bottom': 1,
                  'right': 2
                  },

        'bcorner': {'top': 1,
                    'left': 1,
                    'bottom': 2,
                    'right': 2
                    },

        'cf_red': {'bg_color': '#ffc7ce',
                   'font_color': '#9c0006',
                   'border': 1
                   },

        'cf_blue': {'bg_color': '#C5D9F1',
                    'border': 1
                    },

        'cf_yellow': {'bg_color': '#FFFF99',
                      'border': 1
                      },

        'cf_orange': {'bg_color': '#fde9d9',
                    'border': 1
                    },

        'cf_green': {'bg_color': '#EBF1DE',
                     'border': 1
                     }
    }


colprop = dict()
colprop['names'] = [
              u'№ п/п',
              u'Регион',
              u'Количество муниципальных образований (районов) по которым отчет не предоставлен',
              u'Процент численности населения в муниципальных образованиях (районах) по которым отчет не предоставлен',
              u'Дата получения отчета',
              u'Период просрочки/досрочного предоставления отчета',
              u'Интегральная оценка (рейтинг) по месяцу',
              u'Интегральная оценка (рейтинг) по периоду регулирования'
              ]
colprop['widthes'] = [8.33, 55.33, 28.22, 28.33, 30.22, 36.67+21.67, 22.67, 22.67]
colprop['col_format'] = ['num','data','num','prc','date','legend','prc','prc']