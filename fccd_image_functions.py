from collections import namedtuple

def get_fccd_roi(header, roi_number):
    config = header.descriptors[0]['configuration']['fccd']['data']
    if config  == {}:                    #prior to mid 2017
        x_start, x_size, y_start, y_size = None
    elif config['fccd_stats1_compute_statistics'] == 'Yes' and type(roi_number) is str:
        x_start = config[f'fccd_roi{roi_number}_min_xyz_min_x']
        x_size  = config[f'fccd_roi{roi_number}_size_x']
        y_start = config[f'fccd_roi{roi_number}_min_xyz_min_y']
        y_size  = config[f'fccd_roi{roi_number}_size_y']
        name    = config[f'fccd_roi{roi_number}_name_']
        
    FCCDroi = namedtuple('FCCDroi', 'start_x, size_x, start_y, size_y, name')
    return FCCDroi(x_start, x_size, y_start, y_size, name)

def get_fccd_exp(header):
    config = header.descriptors[0]['configuration']['fccd']['data']
    if config  == {}:                    #prior to mid 2017
        exp_t = header.table().get('fccd_acquire_time')[1]
        exp_p = header.table().get('fccd_acquire_period')[1]
    else:
        exp_t = config['fccd_cam_acquire_time']
        exp_p = config['fccd_cam_acquire_period']
    
    FCCDexp = namedtuple('FCCDconfig', 'time period')
    return FCCDexp(exp_t, exp_p)

def get_final_images_for_scan(header, bgnd8, bgnd2 = None, bgnd1 = None, flatfield=None):
    print(f'Processing {header["start"]["scan_id"]}' , end='.')
    images = get_fastccd_images(header, (bgnd8, bgnd2, bgnd1), flat=None)
    stack = get_images_to_4D(images)
    images =stack
    #print(images.shape)

    if images.shape[-1] > 1001:    
        images = np.concatenate((images[:,:,:,486:966],images[:,:,:,1034:1514]),axis=3)
    elif images.shape[-1] == 1000:
        images = np.concatenate((images[:,:,:,7:486],images[:,:,:,515:996]),axis=3)
    else:
        print('Unexpected array shape', images[0].shape)
        pass
    return images
          
def browse_images(res,title='Frame'):
    N = len(res)
    def view_image(i=0):
        im.set_data(res[i])
        ax.set_title(f'{title} {i}')
        fig.canvas.draw_idle()
    interact(view_image, i=(0, N-1))
    
def area_images(fullFOVimages,areas):
    for k in areas.keys():
        temp = np.array(fullFOVimages[:, areas[k]['loc'][0] : areas[k]['loc'][1], areas[k]['loc'][2] : areas[k]['loc'][3]])
        areas[k].update({'data' : temp})