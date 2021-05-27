from re import MULTILINE
from typing import List
from kivy.core import text
from kivy.uix.gridlayout import GridLayout
import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from SMS_Fusion_Tree import*


class MainWindow(Screen):
    headings_col = ObjectProperty(None)
    recyc_view = ObjectProperty(None)

    def on_kv_post(self, *args):

        #Initiating the fusion tree
        #       create a fusion tree of degree 3
        self.tree = FusionTree(243)
        f = open("cars.csv", encoding='cp850')
        f.readline()
        self.size_tree = 0
        for i in f:
            i = i.split(",")
            lst = [word.strip() for word in i]
            lst = [int(lst[0])] + lst[1:6] + [int(lst[6])] + lst[7:10] +  [float(lst[10])]
            self.tree.insert(lst)
            self.size_tree += 1
        f.close()
        print("Tree length " + str(self.size_tree))
        self.tree.initiateTree()
        #____________________________________________________

        main_layout = BoxLayout(orientation = "vertical")
        #adding cars
        add_car_lab_box = BoxLayout(orientation = "vertical", size_hint =  (1, 0.01))
        add_car_label = Label(text = "Add a Car", size_hint = (1, 1), color = (123,2,3,1))
        add_car_lab_box.add_widget(add_car_label)
        add_block = BoxLayout(orientation = "horizontal")
        main_layout.add_widget(add_car_lab_box) #first adding Add a Car text on top

        label_manuf_name = Label(text = "Manufacturer")
        self.add_manuf_name = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_model_name = Label(text = "Model")
        self.add_model_name = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_trans = Label(text = "Transmission")
        self.add_trans = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_color = Label(text = "Color")
        self.add_color = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_miles = Label(text = "Miles Driven")
        self.add_miles = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_year = Label(text = "Year Produced")
        self.add_year = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_engine = Label(text = "Engine Type")
        self.add_engine = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_engine_cap = Label(text = "Engine Cap")
        self.add_engine_cap = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_category = Label(text = "Category")
        self.add_category = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        label_price = Label(text = "Price($)", size_hint = (0.2, 1))
        self.add_price = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12, size_hint = (0.3, 1))

        box1 = BoxLayout(orientation = "horizontal", size_hint=(1, 0.01))
        box1.add_widget(label_manuf_name)
        box1.add_widget(self.add_manuf_name)
        box1.add_widget(label_model_name)
        box1.add_widget(self.add_model_name)
        box1.add_widget(label_trans)
        box1.add_widget(self.add_trans)

        box2 = BoxLayout(orientation = "horizontal", size_hint=(1, 0.01))
        box2.add_widget(label_color)
        box2.add_widget(self.add_color)
        box2.add_widget(label_miles)
        box2.add_widget(self.add_miles)
        box2.add_widget(label_year)
        box2.add_widget(self.add_year)

        box3 = BoxLayout(orientation = "horizontal", size_hint=(1, 0.01))
        box3.add_widget(label_engine)
        box3.add_widget(self.add_engine)
        box3.add_widget(label_engine_cap)
        box3.add_widget(self.add_engine_cap)
        box3.add_widget(label_category)
        box3.add_widget(self.add_category)

        box4 = BoxLayout(orientation = "horizontal", size_hint=(1, 0.01))
        box5 = BoxLayout(orientation = "horizontal", padding = [40,0,100,0], size_hint = (0.7, 1))
        box6 = BoxLayout(orientation = "vertical", padding = [400,0,0,0])

        box5.add_widget(label_price)
        box5.add_widget(self.add_price)
        button_add = Button(text = "Add", size_hint = (0.3, 1), background_color = [128, 128, 128, 0.2])
        button_add.bind(on_press = self.add_car)
        box6.add_widget(button_add)
        box4.add_widget(box5)
        box4.add_widget(box6)

        main_layout.add_widget(box1)
        main_layout.add_widget(box2)
        main_layout.add_widget(box3)
        main_layout.add_widget(box4)

        search_label = Label(text = "Search", size_hint= (1, 0.01), color = (123,2,3,1))
        main_layout.add_widget(search_label)

        search_sec = BoxLayout(orientation = "horizontal", size_hint=(1, 0.01))

        se_manuf_label = Label(text = "Manufacturer", size_hint= (1, 1))
        self.se_manuf_name = TextInput(multiline = False, readonly = False, halign = "left", font_size = 12)

        se_year_label = Label(text = "Year", size_hint= (1, 1))
        self.year_spinner = Spinner(text='None', values=('<=1970', '<=2000', '<=2010', '<=2020', '>=1970', '>=2000', '>=2010', '>=2020'), background_color = [0,0,255, 0.5])

        se_price_label = Label(text = "Price", size_hint= (1, 1))
        self.price_spinner = Spinner(text='None', values=('<=5000', '<=10000', '<=20000', '<=30000', '<=40000', '<=50000', '>=5000', '>=10000', '>=20000', '>=30000', '>=40000', '>=50000'), background_color = [0,0,255, 0.5])

        search_btn = Button(text = "Search", background_color = [128, 128, 128, 0.2])
        search_btn.bind(on_press = self.on_press_search)

        search_sec_wid = BoxLayout(orientation = "horizontal", size_hint=(1, 1))

        search_sec.add_widget(se_manuf_label)
        search_sec.add_widget(self.se_manuf_name)
        search_sec.add_widget(se_year_label)
        search_sec.add_widget(self.year_spinner)
        search_sec.add_widget(se_price_label)
        search_sec.add_widget(self.price_spinner)
        search_sec_wid.add_widget(search_btn)
        search_sec.add_widget(search_sec_wid)

        main_layout.add_widget(search_sec)

        
        dataset_label = Label(text = "List of All of the available cars", size_hint= (1, 0.01))
        main_layout.add_widget(dataset_label)

        self.ids.c_layout.add_widget(main_layout)

        self.headings_col.add_widget(Label(text = "Id"))
        self.headings_col.add_widget(Label(text = "Manufacturer"))
        self.headings_col.add_widget(Label(text = "Model"))
        self.headings_col.add_widget(Label(text = "Transmission"))
        self.headings_col.add_widget(Label(text = "Color"))
        self.headings_col.add_widget(Label(text = "Miles Driven"))
        self.headings_col.add_widget(Label(text = "Year Produced"))
        self.headings_col.add_widget(Label(text = "Engine Type"))
        self.headings_col.add_widget(Label(text = "Engine Cap"))
        self.headings_col.add_widget(Label(text = "Category"))
        self.headings_col.add_widget(Label(text = "Price($)"))

    def add_car(self, instance):
        ## added the car into our fusion tree
        data_row = [self.size_tree+1, self.add_manuf_name, self.add_model_name, self.add_trans, self.add_color, self.add_miles, self.add_year, self.add_engine, self.add_engine_cap, self.add_category, self.add_price]
        self.tree.insert(data_row)
        cell_rv = []
        for element in data_row:
            cell_rv.append([element, self.size_tree + 1])
        self.size_tree += 1
        data_set = [{'text': str(x[0]), 'Index': str(x[1]), 'selectable': True} for x in cell_rv]
        for i in data_set:
            self.ids.rv.data.append(i)



        #Creating a confirmation popup that car has been added
        popup_box = GridLayout(cols = 1, padding = 10)
        popup_label = Label(text = "Car and its details added successfully!")
        popup_close_btn = Button(text = "Okay", size_hint = (1, 0.2))
        popup_box.add_widget(popup_label)
        popup_box.add_widget(popup_close_btn)
        conf_msg = Popup(title = "Confirmation Message", content = popup_box, size_hint =(None, None), size =(400, 400))
        conf_msg.open()
        popup_close_btn.bind(on_press = conf_msg.dismiss)

    def on_press_search(self, instance):
        #Searching module
        print("Search Start")
        def less_than_equal(manufacturer, price, year):
            output_lst= []
            for i in range(1, self.size_tree):
                lst = self.tree.predecessor(i)
                if len(output_lst) > 0:
                    if lst != output_lst[-1]:
                        if manufacturer != "":
                            if price != -1:
                                if year != -1:
                                    if lst[1] == manufacturer and lst[10] <= price and lst[6] <= year:
                                        output_lst.append(lst)
                                elif lst[1] == manufacturer and lst[10] <= price:
                                    output_lst.append(lst)
                            elif lst[1] == manufacturer and lst[6] <= year:
                                output_lst.append(lst)
                            elif lst[1] == manufacturer and price == -1 and year == -1:
                                output_lst.append(lst)
                        elif price != -1 :
                            if year != -1:
                                if lst[10] <= price and lst[6] <= year:
                                    output_lst.append(lst)
                            elif lst[10] <= price:
                                output_lst.append(lst)
                        elif year != -1:
                            if lst[6] <= year:
                                output_lst.append(lst)
                else:
                    if manufacturer != "":
                        if price != -1:
                            if year != -1:
                                if lst[1] == manufacturer and lst[10] <= price and lst[6] <= year:
                                    output_lst.append(lst)
                        elif lst[1] == manufacturer and lst[10] <= price:
                            output_lst.append(lst)
                        elif lst[1] == manufacturer and lst[6] <= year:
                            output_lst.append(lst)
                        elif lst[1] == manufacturer and price == -1 and year == -1:
                            output_lst.append(lst)
                    elif price != -1:
                        if year != -1:
                            if lst[6] <= year and lst[10] <= price:
                                output_lst.append(lst)
                        elif lst[10] <= price:
                            output_lst.append(lst)
                    elif year != -1:
                        if lst[6] <= year:
                            output_lst.append(lst)
                # print(9)
            return output_lst

        def greater_than_equal(manufacturer, price, year):
            output_lst = []
            for i in range(1, self.size_tree):
                lst = self.tree.successor(i)
                # print(lst)
                if len(output_lst) > 0:
                    if lst != output_lst[-1]:
                        if manufacturer != "":
                            if price != "":
                                if year != "":
                                    if lst[1] == manufacturer and lst[10] >= price and lst[6] >= year:
                                        output_lst.append(lst)
                                elif lst[1] == manufacturer and lst[10] >= price:
                                    output_lst.append(lst)
                            elif lst[1] == manufacturer and lst[6] >= year:
                                output_lst.append(lst)
                            elif lst[1] == manufacturer and price == -1 and year == -1:
                                output_lst.append(lst)
                        elif price != "" :
                            if year != "":
                                if lst[10] >= price and lst[6] >= year:
                                    output_lst.append(lst)
                            elif lst[10] >= price:
                                output_lst.append(lst)
                        elif year != "":
                            if lst[6] >= year:
                                output_lst.append(lst)
                else:
                    if manufacturer != "":
                        if price != "":
                            if year != "":
                                if lst[1] == manufacturer and lst[10] >= price and lst[6] >= year:
                                    output_lst.append(lst)
                        elif lst[1] == manufacturer and lst[10] >= price:
                            output_lst.append(lst)
                        elif lst[1] == manufacturer and lst[6] >= year:
                            output_lst.append(lst)
                        elif lst[1] == manufacturer and price == -1 and year == -1:
                            output_lst.append(lst)
                    elif price != "":
                        if year != "":
                            if lst[6] >= year and lst[10] >= price:
                                output_lst.append(lst)
                        elif lst[10] >= price:
                            output_lst.append(lst)
                    elif year != "":
                        if lst[6] >= year:
                            output_lst.append(lst)
            return output_lst




        manufacturer = self.se_manuf_name.text
        year_range = self.year_spinner.text
        price_range = self.price_spinner.text
        lst_data = []
        cell_rv = []

        if ((year_range[0:2] == "<=") and (price_range[0:2] == "<=")):
            lst_data = less_than_equal(manufacturer, float(price_range[2:]), int(year_range[2:]))
        elif ((year_range[0:2] == ">=") and (price_range[0:2] == ">=")):
            lst_data = greater_than_equal(manufacturer, float(price_range[2:]), int(year_range[2:]))
        
        for row_num in range(len(lst_data)):
            for element in lst_data[row_num]:
                cell_rv.append([element, row_num + 1])

        data_set = [{'text': str(x[0]), 'Index': str(x[1]), 'selectable': True} for x in cell_rv]
        self.ids.rv.data = data_set
        print("Search Done")
       
    
class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''

class RV(RecycleView):                    #Part of the code "below" has been inspired by    https://stackoverflow.com/questions/49856502/kivy-listview-excel-file
    data_set = ListProperty([])
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.load_dataSet()
        self.data = self.data_set
    def load_dataSet(self):
        df = pd.read_csv('cars.csv')
        data = []
        for e_row in df.itertuples():
            for i in range(1, len(e_row)):
                data.append([e_row[i], e_row[0]])
        
        self.data_set = [{'text': str(x[0]), 'Index': str(x[1]), 'selectable': True} for x in data]


class WindowManager(ScreenManager):
    pass


kivy_file = Builder.load_file("ui_b_end.kv")   #The Kivy design file is being loaded


class ShowroomManagementSys(App):
    def build(self):
        return kivy_file


if __name__ == "__main__":
    app = ShowroomManagementSys()
    app.run()
