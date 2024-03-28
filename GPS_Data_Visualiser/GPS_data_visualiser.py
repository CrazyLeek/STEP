"""
This script allows to visualise in a map the GPS data collected during a trip.
   
The script reads a .csv file and looks at the two columns corresponding to the 
longitude and the latitude coordinates.
"""

# Longitude and latitude columns' name
# It is possible to change the names to adapt the columns' name in the files 
# provided
LON_COL_NAME = "latitude"
LAT_COL_NAME = "longitude"

import tkinter

import tkintermapview
import pandas

DUBLIN_CENTER_COORDS = (53.34845697085062, -6.2705164019067325)

# Creation of the graphical elements
root = tkinter.Tk()
root.geometry("800x500")
root.title("GPS data visualiser")

map_widget = tkintermapview.TkinterMapView(root)
map_widget.pack(expand=True, fill='both')

map_widget.set_position(*DUBLIN_CENTER_COORDS)
map_widget.set_zoom(14)

image = tkinter.PhotoImage(file="plus2.png")



# Loading of the .csv file
gps_data = pandas.read_csv("trajet_eloi_bus.csv")
print(gps_data.head())

# Display of GPS positions in the map
for i, rows in gps_data[[LON_COL_NAME, LAT_COL_NAME]].iterrows():
   
   # We can choose to display the position's index or not
    if i % 1 == 1:
        text_marker = str(i)
    else:
        text_marker = None # No text

    # Call of the map's function to display the position
    map_widget.set_marker(
        rows["latitude"], rows["longitude"], 
        text=text_marker, icon=image)
    


root.mainloop()