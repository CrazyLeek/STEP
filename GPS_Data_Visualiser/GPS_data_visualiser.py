"""
This script allows to visualise in a map the GPS data collected during a trip.
   
The script reads a .csv file and looks at the two columns corresponding to the 
longitude and the latitude coordinates.
"""

# Longitude and latitude columns' name
# It is possible to change the names to adapt the columns' name in the files 
# provided
LON_COL_NAME = "longitude"
LAT_COL_NAME = "latitude"

import sys
import tkinter
import dateutil.parser

import tkintermapview
import pandas
import haversine
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DUBLIN_CENTER_COORDS = (53.34845697085062, -6.2705164019067325)



class App():
    """Main class of the program"""

    def __init__(self):
        
        self.create_widgets()
        self.place_widgets()

        self.load_gps_data()
        self.draw_markers()
        self.draw_speed_infos()

        self.root.mainloop()


    def create_widgets(self):
        """Create all the widgets of the window"""

        # The window itself
        self.root = tkinter.Tk()
        self.root.geometry("1400x800")
        self.root.title("GPS data viewer")

        # The interactive map which will display the positions
        self.map_widget = tkintermapview.TkinterMapView(self.root)
        self.map_widget.set_zoom(14)

        # The figure showing the speed profile
        fig_speed_profile = Figure(figsize=(4, 4), dpi=100)
        self.ax_speed_profile = fig_speed_profile.add_subplot()
        self.ax_speed_profile.set_title("Speed profile")

        self.tk_speed_profile = \
        FigureCanvasTkAgg(fig_speed_profile, master=self.root)
        
        
        # The figure showing the speed distribution
        fig_hist_speed = Figure(figsize=(4, 4), dpi=100)
        self.ax_hist_speed = fig_hist_speed.add_subplot()
        self.ax_hist_speed.set_title("Distribution of speeds")

        self.tk_hist_speed = \
            FigureCanvasTkAgg(fig_hist_speed, master=self.root)
        


    def place_widgets(self):
        """Define how the widgets are displayed in the window"""

        self.root.rowconfigure([0, 1], weight=1)
        self.root.columnconfigure((0), weight=1)

        self.map_widget \
            .grid(row=0, column=0, rowspan=2, sticky="nswe")
        
        self.tk_speed_profile \
            .get_tk_widget() \
            .grid(row=0, column=1)
        
        self.tk_hist_speed \
            .get_tk_widget() \
            .grid(row=1, column=1)


    def load_gps_data(self):
        """Load gps data in the given .csv file"""

        if len(sys.argv) > 1:
            self.gps_data = pandas.read_csv(sys.argv[1])
        else:
            print("Provide a path to a file in the arguments")
            exit()


    def draw_markers(self):
        """Draw the markers on the map"""

        # Center the map around the first point
        self.map_widget.set_position(
            self.gps_data[LAT_COL_NAME][0], 
            self.gps_data[LON_COL_NAME][0])

        # Display of GPS positions in the map
        for i, rows in self.gps_data.iterrows():
        
            # We can choose to display the position's index or not
            if i % 1 == 0:
                text_marker = str(i)
            else:
                text_marker = None # No text

            # Call of the map's function to display the position
            self.map_widget.set_marker(
                rows[LAT_COL_NAME], rows[LON_COL_NAME], 
                text=text_marker)#, icon=image)
            

    def draw_speed_infos(self):
        """Draw the speed profile and the speed distribution"""

        # Speed calculation
        old_lat, old_lon, old_date = None, None, None
        speeds = []
        for i, rows in self.gps_data.iterrows():

            lat, lon = rows[LAT_COL_NAME], rows[LON_COL_NAME]
            date = dateutil.parser.parse(rows["created"])

            if old_lat != None:
                distance = haversine.haversine(
                    (old_lat, old_lon), (lat, lon), 
                    unit=haversine.Unit.METERS)
                
                delta_time = date - old_date

                speeds.append(distance / delta_time.seconds)

            old_lat, old_lon, old_date = lat, lon, date


        # Display speed values
        self.ax_speed_profile.plot(speeds)
        self.tk_speed_profile.draw()

        # Display speed distribution
        self.ax_hist_speed.hist(speeds, bins=int(len(speeds)**.5))
        self.tk_hist_speed.draw()

#image = tkinter.PhotoImage(file="plus2.png")

if __name__ == '__main__':  
    App()