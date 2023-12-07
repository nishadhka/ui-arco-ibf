import panel as pn

import geoviews as gv #version 1.8.1

import datetime
from utils_page3 import make_plot
from utils_page3 import make_kc_zarr_df

import boto3


# date='20231016'
# run='18'



gv.extension('bokeh')

# read in the refET dataset
#dsRefET = xr.open_dataset("http://basin.ceoe.udel.edu/thredds/dodsC/DEOSRefET.nc")

# declare dataset list
datasets = ['tp']

# generate panel widgets
dataset = pn.widgets.Select(name='Dataset', options=datasets, value=datasets[0])
#dateVal = pn.widgets.DatePicker(name='Start Date', value=(date.today() + timedelta(days=-1)))
memVal=pn.widgets.Select(name='Ensemble Member', options={'Member1': 1, 'Member2': 2, 'Member3': 3, 'Member4': 4, 
                                                          'Member5': 5, 'Member6': 6, 'Member7': 7, 'Member8': 8, 
                                                          'Member9': 9, 'Member10': 10, 'Member11': 11, 'Member12': 12,
                                                          'Member13': 13, 'Member14': 14, 'Member15': 15, 'Member16': 16, 
                                                          'Member17': 17, 'Member18': 18, 'Member19': 19, 'Member20': 20, 
                                                          'Member21': 21, 'Member22': 22, 'Member23': 23, 'Member24': 24, 
                                                          'Member25': 25, 'Member26': 26, 'Member27': 27, 'Member28': 28,
                                                          'Member29': 29, 'Member30': 30})


timeVal=pn.widgets.Select(name='Forecast Timestep', options={'Hour0': 0, 'Hour1': 1, 'Hour2': 2, 'Hour3': 3, 'Hour4': 4, 'Hour5': 5, 'Hour6': 6,
 'Hour7': 7, 'Hour8': 8, 'Hour9': 9, 'Hour10': 10, 'Hour11': 11, 'Hour12': 12, 'Hour13': 13,
 'Hour14': 14, 'Hour15': 15, 'Hour16': 16, 'Hour17': 17, 'Hour18': 18, 'Hour19': 19, 'Hour20': 20,
 'Hour21': 21, 'Hour22': 22, 'Hour23': 23, 'Hour24': 24, 'Hour25': 25, 'Hour26': 26, 'Hour27': 27, 'Hour28': 28, 
 'Hour29': 29, 'Hour30': 30, 'Hour31': 31, 'Hour32': 32, 'Hour33': 33, 'Hour34': 34, 'Hour35': 35, 'Hour36': 36, 
 'Hour37': 37, 'Hour38': 38, 'Hour39': 39, 'Hour40': 40})

run_options = ['00','06','12', '18']




class S3ImageSlider:
    def __init__(self):
        # Initialize the S3 client
        self.s3 = boto3.client('s3')
        
        self.bucket_name = "S3 Bucket name"
        self.initial_date = datetime.date(2023, 10, 16)
        self.prefix = self.update_prefix_from_date_and_run(self.initial_date, '12')
        self.image_keys = self.list_image_keys(self.bucket_name, self.prefix)

        # Initialize widgets
        self.date_picker = pn.widgets.DatePicker(name='Date', value=self.initial_date)
        self.run_dropdown = pn.widgets.Select(name='Run Time', options=['00','06','12','18'], value='12')
        self.current_filename = pn.widgets.StaticText(name='Current Filename', value='')
        
        self.date_picker.param.watch(self.on_date_change, 'value')
        self.run_dropdown.param.watch(self.on_run_change, 'value')

        self.player = pn.widgets.Player(start=0, end=len(self.image_keys)-1, value=0, loop_policy='loop')
        self.player.param.watch(self.on_player_change, 'value')

        self.image_pane = pn.pane.JPG(self.get_image_bytes_from_s3(self.bucket_name, self.image_keys[0]), width=500)
        
        self.is_image_retrieval_ongoing = False
        
        self.layout = pn.Column(self.date_picker, self.run_dropdown, self.player, self.current_filename, self.image_pane)

    def list_image_keys(self, bucket_name, prefix):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return [item['Key'] for item in response.get('Contents', [])]

    def get_image_bytes_from_s3(self, bucket_name, file_key):
        response = self.s3.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read()

    def update_prefix_from_date_and_run(self, date, run):
        return f"fcst/gefs_ens/{date.year}/{date.month:02}/{date.strftime('%Y%m%d')}/{run}/plot_stitch/"

    def show_image(self, index):
        self.is_image_retrieval_ongoing = True
        self.image_pane.object = self.get_image_bytes_from_s3(self.bucket_name, self.image_keys[index])
        self.current_filename.value = self.image_keys[index]
        self.is_image_retrieval_ongoing = False

    def update_image_keys(self):
        new_prefix = self.update_prefix_from_date_and_run(self.date_picker.value, self.run_dropdown.value)
        self.image_keys = self.list_image_keys(self.bucket_name, new_prefix)
        self.player.value = 0

    def on_date_change(self, event):
        self.update_image_keys()
    
    def on_run_change(self, event):
        self.update_image_keys()

    def on_player_change(self, event):
        if not self.is_image_retrieval_ongoing:
            if self.player.value < len(self.image_keys):
                self.show_image(self.player.value)
                
    def view(self):
        return pn.Column(self.date_picker, self.run_dropdown, self.player, self.current_filename, self.image_pane)

class Page3:
    def __init__(self):
        self.content = pn.Column("Current Forecast & Observations")

        # Convert string to datetime.date object
        initial_date = datetime.date(2023, 10, 16)
        
        # Replace date dropdown with DatePicker using the datetime.date object
        self.date_widget = pn.widgets.DatePicker(name='Date', value=initial_date)
        
        self.run_widget = pn.widgets.Select(name='Run', options=run_options, value=run_options[0])

        self.load_dataset()

        generate_button = pn.widgets.Button(name='Plot', button_type='primary')
        generate_button.on_click(self.update)
        self.dashboard = pn.Row(pn.Column(dataset, self.date_widget, self.run_widget, memVal, timeVal, generate_button),
                                make_plot(self.cropped_ds, dataset.value, memVal.value, timeVal.value),
                                )

    def load_dataset(self):
        # When fetching the date from the DatePicker widget, you can format it to match the expected string format
        min_lon = 21
        min_lat = -12
        max_lon = 53
        max_lat = 24 
        date=self.date_widget.value.strftime('%Y%m%d')
        run=self.run_widget.value
        print(date,run)
        ds = make_kc_zarr_df(date,run)
        self.cropped_ds = ds.sel(latitude=slice(max_lat, min_lat), longitude=slice(min_lon, max_lon))

    def update(self, event):
        self.load_dataset()  # Reload dataset if date or run changes
        self.dashboard[1].object = make_plot(self.cropped_ds, dataset.value, memVal.value, timeVal.value)

    def view(self):
        s3_slider = S3ImageSlider()
        return pn.Column(s3_slider.view(), self.dashboard)

    def servable(self):
        return self.view()


page = Page3()
page.servable()
 
