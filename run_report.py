

import pandas as pd
import numpy as np
from IPython.display import display
pd.options.display.max_rows = None 

def print_scans(hhs, start_fields=None, baseline_fields=None, skip_reasons=None, use_default_fields = True, debug_mode=False):
    '''Print a custom summary of a set of data based on search critera.
    
    note: 
    The ``since`` and ``until`` parameters accepts the following
    representations of time:
    
    * timestamps like ``time.time()`` and ``datetime.datetime.now()``
    * ``'2015'``
    * ``'2015-01'``
    * ``'2015-01-30'``
    * ``'2015-03-30 03:00:00'``
    '''
    default_baseline = ['pgm_energy_setpoint','stemp_temp_B_T']
    titles_middle = ['energy[eV]','Tsample[K]',]
    baseline_names = default_baseline  
                                
    table_titles = ['scan_id','plan_name','motors','detectors']
    titles_end = ['fccd_aquire_time', 'fccd_num_images','fccd_image_type','fccd_ct_time', 'scan_time[min]', 'sample_type','sample_comp','purpose','notes']
    
    if baseline_fields is not None and type(baseline_fields) is list: 
        baseline_names.extend(baseline_fields)
        print(list(baseline_names))
        titles_middle.extend([field[:15] for field in baseline_fields])
        print
        
    table_titles.extend(titles_middle)
    table_titles.extend(titles_end)
    
    #main_dict = {}  #TODO test if dict or list is faster
    main_list = []  #TODO test if dict or list is faster
    
    for i, hh in enumerate(hhs):
        try:
            if hh['stop'].get('exit_status',0) == 'success':  
                md = hh['start']
                if skip_reasons is not None:
                    if md.get('purpose') in skip_reasons:
                        pass
                    elif md.get('reason') in skip_reasons:
                        pass
                tb = hh.table(stream_name='baseline', fields = baseline_names) #cannot use .mean() because this isn't ordered (databroker 0.13)
                
                scan_num  = md['scan_id']
                scan_plan = md['plan_name']
                meas_time = np.round((hh['stop']['time'] - md['time'])/60, 1) #minutes
                motors = md.get('motors','NA')
                detectors = md.get('detectors',[])
                sample_type = md['sample'].get('type','unk'  )
                sample_comp = md['sample'].get('composition','unk'  )
                purpose = md.get('reason',md.get('purpose','na'))
                
                start_dict_beg = {'scan_num':     scan_num,
                                  'plan_name':    scan_plan,
                                  'motors':       motors,
                                  'detectors':    detectors,
                                 }
                start_dict_end = {'scan_time':  meas_time,
                                  'sample_type':sample_type,   #custom at CSX
                                  'sample_comp':sample_comp,   #custom at CSX
                                  'purpose':    purpose
                                 }
                
                if 'fccd' in md['detectors']: #custom to fccd camera at CSX, 
                    aquire_time = np.round(hh.config_data('fccd')['primary'][0].get('fccd_cam_acquire_time','unk'),2)
                    aquire_period = np.round(hh.config_data('fccd')['primary'][0].get('fccd_cam_acquire_period','unk'),3)
                    num_images = hh.config_data('fccd')['primary'][0].get('fccd_cam_num_images',0)
                    try:
                        total_ct_time = np.round(aquire_period * num_images * md["num_points"]/60,1) #minutes
                    except TypeError:
                        total_ct_time = '?'
                    gain = hh.config_data('fccd')['primary'][0].get('fccd_cam_fcric_gain','unk')
                    if md.get('fccd','light') != 'light':
                        image_type = md['fccd']['image']+'-'+md['fccd']['gain']
                    else:
                        image_type = 'light'+'-gainbit'+np.str(gain)
                    fccd_params = {'aquire_time':aquire_time, 'num_images':num_images, 'image_type':image_type , 'total_ct_time':total_ct_time}
                else: 
                    fccd_params = {'aquire_time':'-',         'num_images':'-',        'image_type':'-',          'total_ct_time':'-', }


                row = [start_dict_beg[k] for k in start_dict_beg.keys()]
                #row.extend([np.round(tb[k],2) for k in tb.keys()])#TODO-cannot use.mean()             
                row.extend([np.round(tb[k].mean(),2) for k in baseline_names])   
                
                row.extend([fccd_params[k] for k in fccd_params.keys()])
                row.extend([start_dict_end[k] for k in start_dict_end.keys()])
                row.extend(['']) #this is for note during analysis process
                if debug_mode is True:
                    print(row)
                #main_dict.update({i:row})
                main_list.append(row)
                
        except KeyError as ex:

            if debug_mode is True:
                print('\t\t\t KeyError on',ex, 'for scan ', hh['start']['scan_id'])
            pass

    if debug_mode is True:
        print(f'{i} rows checked, {len(row)} items in row, {len(table_titles)} titles in row')
        print(table_titles)
    
    df = pd.DataFrame(main_list, columns=table_titles)
    
    display(df)
    
    return df
