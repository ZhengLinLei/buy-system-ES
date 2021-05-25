import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

from datetime import datetime

import sqlite3, json, os

# pyinstaller --icon=./data/ico.ico --noconsole --add-data './readme.txt;.' --add-data './data/delete.log;data' --add-data './data/ico.ico;data' index.py

db_pathName = './data/database.db'
#SQLITE SQL REQUEST
def run_sqlite_query(query, parameters = ()):
    global db_pathName

    with sqlite3.connect(db_pathName) as conection:
        place = conection.cursor()
        response = place.execute(query, parameters)
        conection.commit()

    if "SELECT " in query and query[0] == 'S':
        return response.fetchall()

    return True
def prepare_database():
    querys = [''' CREATE TABLE 'Product_data' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `code` INTEGER NOT NULL,
                        `name` TEXT NOT NULL,
                        `price` REAL NOT NULL
                    );''',
                ''' CREATE TABLE 'Product_register_pay' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `date_time` DATETIME NOT NULL,
                        `data` TEXT NOT NULL,
                        `total_price` REAL NOT NULL,
                        `number_product` INTEGER NOT NULL,
                        `method_pay` TEXT NOT NULL
                    );''',
                '''CREATE TABLE 'Product_deletedRegister_pay' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `date_time` DATETIME NOT NULL,
                        `data` TEXT NOT NULL,
                        `total_price` REAL NOT NULL,
                        `number_product` INTEGER NOT NULL,
                        `method_pay` TEXT NOT NULL
                    );''']
        
    for query in querys:
        run_sqlite_query(query)

def isFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

#start root window
class AppOpen:
    second_windowOpen = root_window_fullScreen = False
    totalPrice_arr_toPay = {}

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('Pestaña de pago')
        # self.root_window.iconphoto(True, tk.PhotoImage(file='ico.jpg'))

        self.root_window.bind("<F11>", lambda event: self.toggle_fullScreen())
        self.root_window.bind("<f>", lambda event: self.toggle_fullScreen())
        self.root_window.bind("<Control-e>", lambda event: self.root_window.destroy())

        self.root_window.iconbitmap(default = './data/ico.ico')
        self.root_window.focus_force()
        #More option Buttons
        addProduct_open_window = tk.Button(self.root_window, text = 'Añadir', padx = 25, cursor = 'hand2', command = lambda : self.open_newWindowConfig('add'))
        addProduct_open_window.grid(row = 0, column = 0) #Add products
        #FastKey
        self.root_window.bind("<Control-t>", lambda event: self.open_newWindowConfig('add'))
        CreateToolTip(addProduct_open_window, text = 'Abrir pestaña de añaduir productos。usa Ctrl+t para abrir')

        changeProduct_open_window = tk.Button(self.root_window, text = 'Modificar', padx = 25, cursor = 'hand2', command = lambda : self.open_newWindowConfig('change'))
        changeProduct_open_window.grid(row = 0, column = 1) #Modify and delete product
        #FastKey
        self.root_window.bind("<Control-k>", lambda event: self.open_newWindowConfig('change'))
        CreateToolTip(changeProduct_open_window, text = 'Modifica y elimina productos。usa Ctrl+k para abrir')

        self.root_window_fullScreenButton = tk.Button(self.root_window, text= 'FullScreen',padx = 25, cursor = 'hand2', command = self.toggle_fullScreen)
        self.root_window_fullScreenButton.grid(row = 0, column = 2, padx = (20, 0)) #Full Screen

        helpProduct_open_window = tk.Button(self.root_window, text = 'Ayuda', padx = 25, cursor = 'hand2', command = lambda : self.open_newWindowConfig('help'))
        helpProduct_open_window.grid(row = 0, column = 3, padx = (0, 20)) #Help 
        #FastKey
        self.root_window.bind("<Control-h>", lambda event: self.open_newWindowConfig('help'))
        CreateToolTip(helpProduct_open_window, text = 'Pestaña de ayuda。usa Ctrl+h para abrir')

        autoRepair_button = tk.Button(self.root_window, text = 'AutoRepair', padx = 25, cursor = 'hand2', command = self.auto_repair)
        autoRepair_button.grid(row = 0, column = 4, padx = 35) #Auto repair

        history_button = tk.Button(self.root_window, text = 'Historial ventas', padx = 25, cursor = 'hand2', command = lambda : self.open_newWindowConfig('history'))
        history_button.grid(row = 0, column = 5, padx = 35) #Sended history
        #FastKey
        self.root_window.bind("<Control-j>", lambda event: self.open_newWindowConfig('history'))
        CreateToolTip(history_button, text = 'En esta pestaña puede hacer una breve vista de sus ventas, usa Ctrl+j para abrir')

        #FullScreen Button ToolTips
        CreateToolTip(self.root_window_fullScreenButton, text = 'F11 o F para fullscreen')
        #Autorepair Button ToolTips
        #FastKey
        self.root_window.bind("<F8>", lambda event: print(event))
        CreateToolTip(autoRepair_button, text = 'Si hay errores de sistema, pulse aqui, si persiste abre "Ayuda", F8 para reparacion rapida')

        #LabelFrame to write code and click button
        self.root_window_firstLabelFrame = tk.LabelFrame(self.root_window, text = 'Codigo barra', padx = 20, pady = 20)
        self.root_window_firstLabelFrame.grid(row = 2, column = 0, pady = 30, columnspan = 4)

        #LabelFrame > input
        self.root_window_firstLabelFrame_code = tk.Entry(self.root_window_firstLabelFrame, width = 30)
        self.root_window_firstLabelFrame_code.grid(row = 0, column = 0)
        self.root_window_firstLabelFrame_code.focus()

        #LabelFrame > button
        add_productsFase1Button = tk.Button(self.root_window_firstLabelFrame, text = 'Añadir', command = lambda : self.open_newWindowConfig('amount_product'))
        add_productsFase1Button.grid(row = 1, column = 0, sticky = tk.W + tk.E, pady = (10, 0))

        self.root_window.bind("<Return>", lambda event: self.open_newWindowConfig('amount_product'))
        CreateToolTip(add_productsFase1Button, text = 'Una vez escaneado entra al carrito con Enter')

        #Table Div Frame
        root_window_tableProductsFrame = tk.Frame(self.root_window)
        root_window_tableProductsFrame.grid(row = 3, column = 0, columnspan = 150, sticky = tk.W+tk.E)
        #Table 
        self.root_window_tableProducts = ttk.Treeview(root_window_tableProductsFrame, columns = ("name", "price", "amount", "total"), selectmode = tk.EXTENDED, height = 23)

        self.root_window_tableProducts.heading('#0', text = 'Codigo', anchor = tk.CENTER)
        self.root_window_tableProducts.column("#0", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('name', text = 'Producto', anchor = tk.CENTER)
        self.root_window_tableProducts.column("name", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('price', text = 'Precio', anchor = tk.CENTER)
        self.root_window_tableProducts.column("price", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('amount', text = 'Cant.', anchor = tk.CENTER)
        self.root_window_tableProducts.column("amount", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('total', text = 'Total', anchor = tk.CENTER)
        self.root_window_tableProducts.column("total", width = int(self.root_window.winfo_screenwidth()/5)-25, stretch = False)

        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        self.root_window_tableProducts.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)

        #SCROLL
        root_window_tableProductsScroll = tk.Scrollbar(root_window_tableProductsFrame, orient = tk.VERTICAL, command = self.root_window_tableProducts.yview)
        root_window_tableProductsScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.root_window_tableProducts.configure(yscrollcommand = root_window_tableProductsScroll.set)

        #NEW window DELETE AND CHANGE AMOUNT BUTTONS
        newWindow_to_open = tk.Button(self.root_window, text = 'Nueva pestaña', cursor = 'hand2', command = lambda : os.startfile('{}\index.py'.format(os.getcwd())))
        newWindow_to_open.grid(row = 4, column = 0, pady = (10, 0), sticky = tk.W + tk.E)
        #FastKey
        self.root_window.bind("<Control-n>", lambda event: os.startfile('{}\index.py'.format(os.getcwd())))
        CreateToolTip(newWindow_to_open, text = 'Abre nueva pestaña de compra o usa Ctrl+n.')

        root_window_tableProductsDelete = tk.Button(self.root_window, text = 'Eliminar', padx = 40, cursor = 'hand2', command = self.removeProduct_addToPay)
        root_window_tableProductsDelete.grid(row = 4, column = 46, pady = (10, 0))
        #FastKey
        self.root_window.bind("<Delete>", lambda event: self.removeProduct_addToPay())
        CreateToolTip(root_window_tableProductsDelete, text = 'Se puede usar tecla Delete')
        
        root_window_tableProductsChange = tk.Button(self.root_window, text = 'Modificar', padx = 40, cursor = 'hand2', command = lambda : self.to_open_amountTable_number())
        root_window_tableProductsChange.grid(row = 4, column = 45, pady = (10, 0))
        #FastKey
        self.root_window.bind("<F10>", lambda event: self.to_open_amountTable_number())
        CreateToolTip(root_window_tableProductsChange, text = 'Para modificar lo añadido, F10')

        #Total Price
        root_window_priceFrame = tk.Frame(self.root_window, bg = "#fff", borderwidth = 3, relief= tk.RAISED)
        root_window_priceFrame.grid(row = 2, column = 45, sticky = tk.W + tk.E, pady = 20)

        tk.Label(root_window_priceFrame, text ="Total: ", bg = '#fff', anchor = tk.W, font = ("", 20, "bold")).grid(row = 0, column = 0, sticky = tk.N + tk.S, padx = 15, pady = 20)
        self.root_window_totalPrice = tk.Label(root_window_priceFrame, text ="0.00", bg = '#fff', anchor = tk.E, font = ("", 20))
        self.root_window_totalPrice.grid(row = 0, column = 1, sticky = tk.N + tk.S, padx = 15, pady = 20)
        #Pay
        root_window_payButton = tk.Button(root_window_priceFrame, text = 'Pagar', padx = 30, cursor = 'hand2', font = ("", 14), command = self.allProduct_payAllPrice)
        root_window_payButton.grid(row = 0, column = 4, sticky = tk.W + tk.E + tk.N + tk.S, pady = (0, 1))
        #FastKey
        self.root_window.bind("<F12>", lambda event: self.allProduct_payAllPrice())
        CreateToolTip(root_window_payButton, text = 'Puede usar F12')

    def open_newWindowConfig(self, type, amounttype = False):
        open_trueWindowAcceptParameter = ('add', 'change', 'help', 'history')
        if type in open_trueWindowAcceptParameter:

            if type == 'add':
                addRoot = tk.Tk()
                applicationAdd = AppAdd(addRoot)

                addRoot.mainloop()
            elif type == 'change':
                changeRoot = tk.Tk()
                applicationChange = AppChange(changeRoot)

                changeRoot.mainloop()
            elif type == 'history':
                historyRoot = tk.Tk()
                applicationHistory = AppHistory(historyRoot)

                historyRoot.mainloop()
            elif type == 'help':
                self.second_window = tk.Toplevel(self.root_window)
                self.second_window.title('Ayuda')

                tk.Label(self.second_window, text = 'Ayuda', font = ('times', 18, 'bold')).grid(row = 0, column = 0, sticky = tk.W + tk.E, padx = 10, pady = (3, 0))
                
                #How to Use Frame
                div_howToUse = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_howToUse.grid(row = 1, column = 0, padx = 10, pady = 10)

                tk.Label(div_howToUse, text = 'Como usar: ', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '1. Antes de usar añada los productos necesarios。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '2. Si hay errores se puede modificar', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '3. Haga pruebas con un escane。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '4. Acerque el escaner al codigo y se introducira, si no existe el codigo devolvera un error', wrap = 800,  anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '5. Si necesita hacer cambios de la compra, abajo puede solicitarlas', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '6. Si hay un nuevo cliente, puede abrir nueva pestaña', anchor = tk.W).pack(fill = tk.BOTH)

                #How to Use Frame
                div_erro = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_erro.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = tk.W + tk.E)

                tk.Label(div_erro, text = 'Arregla problemas: ', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = 'Si en el uso del sistema hay errores puede usar "AutoRepair" y se autoreparara. Puede que tarde el proceso, por favor no cierre el programa', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = 'Si persiste los problemas puede arreglarlo manualmente', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = '1. En la ruta '+os.getcwd()+' encuentra la carpeta "data" y despues localiza "database.db"', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '2. Copie el archivo de datos, recuerde que el nombre debe de ser identico', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '3. Vuelva a descargar el sistema', anchor = tk.W, wrap = 780).pack(fill = tk.BOTH, padx = (20, 0))
                tk.Label(div_erro, text = '4. Una vez descargado mueva el archivo copiado "database.db" a la carpeta de data en la ruta '+os.getcwd(), anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '4. Una vez hecho todo, puede abrir de nuevo el sistema', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '5. Si hay problemas, comuniquenos', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))

                #How to Use Frame
                div_creator = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_creator.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = tk.W + tk.E)

                tk.Label(div_creator, text = 'Autor: 郑林磊 [Zheng Lin Lei]', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_creator, text = 'Correo: zheng9112003@gmail.com', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_creator, text = 'v1.0 2020', anchor = tk.W).pack(fill = tk.BOTH)
        else:
            if type == 'amount_product':
                if self.root_window_firstLabelFrame_code.get() != "" and self.root_window_firstLabelFrame_code.get().isnumeric():
                    self.open_amountTable_number(False)
                    
                        
    def auto_repair(self):
        if os.path.isfile('./data/database.db'):
            if os.path.isdir('./data'):
                messagebox.showwarning('No hay errores', 'No se localizo errores del sistema. Continue y le guiaremos a repararlo')
            else:
                messagebox.showwarning('Error detectado', 'Un archivo falta o esta en ruta equivocada. Continue y le guiaremos a repararlo')


            messagebox.showinfo('Reparacin manual', 'Encuentre en {}\\data\\ encuentre "database.db"， haga una copia y guardelo。 \n \n Vuelva a descargar el sistema. \n \n Mueva el archivo copiado a la ruta {}\\data\\'.format(os.getcwdb(), os.getcwdb()))


        else:
            messagebox.showwarning('Error detectado', 'Falta componentes o archivos， quizas se pierdan los datos')

            if os.path.isfile('./database.db'):
                os.replace("./database.db", "./data/database.db")

                messagebox.showinfo('Reparacion terminada', 'Se termino la reparación, quizas algunos datos se pierdan')
            else:
                messagebox.showwarning('Error detectado', 'Lo sentimos， no hemos encontrado los componentes faltantes. El archivo que falta es la base de datos y perdera todo los datos \n\n\n o puede usted buscar el archivo "database.db" quizas este en la papelera. De momento se le creara de nuevo un archivo database.db. Si finalmente lo encuentra, puede moverlo hacia la ruta {}'. format(os.getcwd()))
                prepare_database()

    def open_amountTable_number(self, type):
        if not self.second_windowOpen:
            #Only can open one
            #Check if it's openned
            self.second_windowOpen = True

            self.second_window = tk.Toplevel()
            self.second_window.title('Cantidad')
            def closeSecond_window():
                self.second_windowOpen = False
                self.root_window_firstLabelFrame_code.focus()
                self.second_window.destroy()
                            
            self.second_window.protocol("WM_DELETE_WINDOW", closeSecond_window)

            inputNumber_frame = tk.Frame(self.second_window, padx = 40, pady = 15)
            inputNumber_frame.grid(row = 0, column = 0, sticky = tk.W + tk.E)

            add_productAmountInput = tk.Spinbox(inputNumber_frame, from_ = 1, to = 9999, wrap = True)
            add_productAmountInput.pack(fill = tk.BOTH, padx = 5, ipadx = 2, ipady = 10)
            add_productAmountInput.focus()

            buttonNumber_frame = tk.Frame(self.second_window, padx = 25, pady = 25)
            buttonNumber_frame.grid(row = 1, column = 0)

            def amountInputButton(number):
                if number == 'del':
                    add_productAmountInput.delete(len(add_productAmountInput.get())-1)
                else:
                    add_productAmountInput.insert(tk.END, number) 

            tk.Button(buttonNumber_frame, text = 7, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 8, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 9, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 4, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 5, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 6, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 1, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 2, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 3, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 0, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = tk.W + tk.E)
            tk.Button(buttonNumber_frame, text = 'Del', cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 14, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5, sticky = tk.N + tk.S)

            self.second_window.focus_force()

            if type:
                add_productsFase2Button = tk.Button(buttonNumber_frame, text = 'Cambiar', cursor = 'hand2', bd = 3, font = ('times', 16), command = lambda : self.editProduct_addToPay(add_productAmountInput.get()))
                self.second_window.bind("<Return>", lambda event: self.editProduct_addToPay(add_productAmountInput.get()))
            else:
                add_productsFase2Button = tk.Button(buttonNumber_frame, text = 'Continuar', cursor = 'hand2', bd = 3, font = ('times', 16), command = lambda : self.secondWindow_addToPay(self.root_window_firstLabelFrame_code.get(), add_productAmountInput.get()))
                self.second_window.bind("<Return>", lambda event: self.secondWindow_addToPay(self.root_window_firstLabelFrame_code.get(), add_productAmountInput.get()))

                            
            add_productsFase2Button.grid(row = 4, column = 0, columnspan = 3, sticky = tk.W + tk.E, pady = (15, 0))

            CreateToolTip(add_productsFase2Button, text = 'Una vez elegido la cantidad, pulse Enter')         
        else:
            self.second_window.focus_force()
        

    def toggle_fullScreen(self):
        self.root_window_fullScreen = not self.root_window_fullScreen

        if self.root_window_fullScreen:
            self.root_window_fullScreenButton['text'] = 'SmallScreen'
        else:
            self.root_window_fullScreenButton['text'] = 'FullScreen'

        self.root_window.attributes("-fullscreen", self.root_window_fullScreen)

    #Show all total Price    
    def calc_totalPrice(self):
        if len(self.totalPrice_arr_toPay) == 0:
            totalPrice = 0.00
        else:
            totalPrice = 0

            prices = self.totalPrice_arr_toPay.values()
            for price in prices:
                totalPrice += float(price)

        return "{:.2f}".format(totalPrice)

    def secondWindow_addToPay(self, code, amount):
        if (code != "" and amount != "") and (code.isnumeric() and amount.isnumeric()):
            query = 'SELECT `code`, `name`, `price` FROM `Product_data` WHERE `code` = ?'
            parameters = (code, )
            responseData = run_sqlite_query(query, parameters = parameters)

            if len(responseData) == 0:
                messagebox.showwarning("Error", "Este codigo no esta añadido en la base de datos, añadala.")
            else:
                return_ifAdded = self.checkProduct_added_before(code)

                if return_ifAdded:
                    child_toDelete = self.root_window_tableProducts.item(return_ifAdded)
                    #----------
                    amount_number = int(child_toDelete['values'][2]) + int(amount)
                    #------------------------
                    self.root_window_tableProducts.delete(return_ifAdded)

                else:
                    amount_number = amount

                totalPrice_product = float("{:.2f}".format((float(responseData[0][2]))*(float(amount_number))))

                self.root_window_tableProducts.insert('', tk.END, text = responseData[0][0], values = (responseData[0][1], responseData[0][2], int(amount_number), totalPrice_product))
                self.totalPrice_arr_toPay[code] = "{:.2f}".format(totalPrice_product)

                self.root_window_totalPrice['text'] = self.calc_totalPrice()

            self.root_window_firstLabelFrame_code.delete(0, tk.END)
            self.root_window_firstLabelFrame_code.focus()
            self.second_window.destroy()
            self.second_windowOpen = False

    def checkProduct_added_before(self, code):
        allChilds = self.root_window_tableProducts.get_children()

        for child in allChilds:
            if str(self.root_window_tableProducts.item(child)['text']) == code:
                return child


        return False

    #EDIT AND DELETE
    def checkProduct_is_selected(self):
        if len(str(self.root_window_tableProducts.item(self.root_window_tableProducts.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("Error", "Ningun producto seleccionado， seleccionalo")
            self.root_window_firstLabelFrame_code.focus()
            return False


    def removeProduct_addToPay(self):
        if(self.checkProduct_is_selected()):
            code = str(self.root_window_tableProducts.item(self.root_window_tableProducts.selection())['text'])
            
            del self.totalPrice_arr_toPay[code]
            self.root_window_tableProducts.delete(self.root_window_tableProducts.selection())

            self.root_window_totalPrice['text'] = self.calc_totalPrice()

            self.root_window_firstLabelFrame_code.focus()
    def to_open_amountTable_number(self):
        if(self.checkProduct_is_selected()):
            self.open_amountTable_number(True)

    def editProduct_addToPay(self, amount):
        item_selectedId = self.root_window_tableProducts.selection()
        item_selectedValues = self.root_window_tableProducts.item(item_selectedId)

        totalPrice_product = float("{:.2f}".format((float(item_selectedValues['values'][1]))*(int(amount))))

        self.root_window_tableProducts.insert('', tk.END, text = item_selectedValues['text'], values = (item_selectedValues['values'][0], item_selectedValues['values'][1], int(amount), totalPrice_product))
        self.totalPrice_arr_toPay[str(item_selectedValues['text'])] = totalPrice_product

        self.root_window_tableProducts.delete(item_selectedId)
            
        self.root_window_totalPrice['text'] = self.calc_totalPrice()

        self.root_window_firstLabelFrame_code.focus()
        self.second_window.destroy()
        self.second_windowOpen = False

    
    #Pay the price
    def allProduct_payAllPrice(self):
        if len(self.totalPrice_arr_toPay) == 0:
            messagebox.showerror("Producto", "El carro esta vacio, no se puede hacer el total")
            self.root_window_firstLabelFrame_code.focus()
        else:
            self.chooseType_forPay()

    def chooseType_forPay(self):
        if not self.second_windowOpen:
            #Only can open one
            #Check if it's openned
            self.second_windowOpen = True
            self.second_window = tk.Toplevel(self.root_window)
            self.second_window.focus_force()
            self.second_window.title('Pagar')

            def closeSecond_window():
                self.second_windowOpen = False
                self.root_window_firstLabelFrame_code.focus()
                self.second_window.destroy()
                                
            self.second_window.protocol("WM_DELETE_WINDOW", closeSecond_window)

            tk.Label(self.second_window, text = 'Metodo de pago', anchor = tk.CENTER, font = ('', 18, 'bold')).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E, pady = (10, 0))
            moneyMethod_pay = tk.Button(self.second_window, text = 'Efectivo', padx = 15, pady = 15, font = ('times', 18, 'bold'), command = lambda : self.payAll_priceToFinish('money'))
            moneyMethod_pay.grid(row = 1, column = 0, padx = 20, pady = (60, 90))
            #FastKey
            self.second_window.bind("<F1>", lambda event: self.payAll_priceToFinish('money'))
            CreateToolTip(moneyMethod_pay, text = 'Tecla rapida: F1')

            creditCardMethod_pay = tk.Button(self.second_window, text = 'Tarjeta Credito', padx = 15, pady = 15, font = ('times', 18, 'bold'), command = lambda : self.payAll_priceToFinish('card'))
            creditCardMethod_pay.grid(row = 1, column = 1, padx = 20, pady = (60, 90))
            #FastKey
            self.second_window.bind("<F2>", lambda event: self.payAll_priceToFinish('card'))
            CreateToolTip(creditCardMethod_pay, text = 'Tecla rapida: F2')
        else:
            messagebox.showwarning("No se puede continuar", "Hay otro programa corriendo, cierrela para continuar")
            self.second_window.focus_force()

    def payAll_priceToFinish(self, typeOf):
        #Create a datetime 
        datetimeVar = datetime.now()
        #-------------
        methodPay = typeOf
        date = datetimeVar.strftime('%Y-%m-%d')
        time = datetimeVar.strftime("%H:%M:%S")

        totalPrice = self.calc_totalPrice()
        numberProduct = len(self.totalPrice_arr_toPay)

        dataProduct = {'data': []}

        for product in self.root_window_tableProducts.get_children():
            data_of_product = self.root_window_tableProducts.item(product)

            jsonToStr = {
                    'code': data_of_product['text'], 
                    'name': data_of_product['values'][0], 
                    'price': data_of_product['values'][1], 
                    'amount': data_of_product['values'][2], 
                    'total_price': data_of_product['values'][3]
                    }

            dataProduct['data'].append(jsonToStr)

        dataProduct_str = json.dumps(dataProduct)

        query = 'INSERT INTO `Product_register_pay` (`date_time`,`data`, `total_price`, `number_product`, `method_pay`) VALUES (?, ?, ?, ?, ?)'
        parameters = ('{} {}'.format(date, time), dataProduct_str, totalPrice, numberProduct, methodPay)

        if run_sqlite_query(query, parameters = parameters):
            self.second_window.destroy()
            self.second_windowOpen = False
            #Reset system----------
            self.reset_allSystem_toNew()


    def reset_allSystem_toNew(self):
        self.second_window.destroy()
        
        self.totalPrice_arr_toPay.clear()
        self.root_window_totalPrice['text'] = self.calc_totalPrice()

        for element in self.root_window_tableProducts.get_children():
            self.root_window_tableProducts.delete(element)

        self.root_window_firstLabelFrame_code.focus()
class AppAdd():
    addProduct_status_level = 0

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('Añadir producto')

        self.root_window.bind('<Return>', lambda event : self.check_status_level())
        self.root_window.focus_force()

        #Title
        tk.Label(self.root_window, text = 'Añadir producto', font = ('times', 18), anchor = tk.CENTER).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        #---------------------------------
        self.root_window_firstLabelFrame = tk.LabelFrame(self.root_window, text = 'Codigo de barra', padx = 20, pady = 20)
        self.root_window_firstLabelFrame.grid(row = 1, column = 0, pady = 30, columnspan = 2, sticky = tk.W + tk.E, padx = 20)

        #code
        tk.Label(self.root_window_firstLabelFrame, text = 'Codigo: ', font = ('', 14, 'bold')).grid(row = 0, column = 0, padx = (0, 15))
        self.root_window_firstLabelFrame_code = tk.Entry(self.root_window_firstLabelFrame, width = 50)
        self.root_window_firstLabelFrame_code.grid(row = 0, column = 1, padx = 5)

        #focus
        self.root_window_firstLabelFrame_code.focus_force()

        #name
        tk.Label(self.root_window_firstLabelFrame, text = 'Nombre: ', font = ('', 14, 'bold')).grid(row = 1, column = 0, padx = (0, 15))
        self.root_window_firstLabelFrame_name = tk.Entry(self.root_window_firstLabelFrame, width = 50)
        self.root_window_firstLabelFrame_name.grid(row = 1, column = 1, padx = 5)
        #----------------------------------
        self.root_window_secondLabelFrame = tk.LabelFrame(self.root_window, text = 'Precio', padx = 20, pady = 20)
        self.root_window_secondLabelFrame.grid(row = 2, column = 0, pady = 30, sticky = tk.W + tk.E, padx = 20)

        self.root_window_secondLabelFrame_price = tk.Entry(self.root_window_secondLabelFrame,)
        self.root_window_secondLabelFrame_price.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.number_button_frame = tk.Frame(self.root_window_secondLabelFrame)
        self.number_button_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

        def amountInputButton(number):
            if number == 'del':
                self.root_window_secondLabelFrame_price.delete(len(self.root_window_secondLabelFrame_price.get())-1)
            else:
                self.root_window_secondLabelFrame_price.insert(tk.END, number) 

        tk.Button(self.number_button_frame, text = 7, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 8, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 9, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 4, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 5, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 6, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 1, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 2, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 3, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 0, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '.', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('.')).grid(row = 3, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 'Del', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5)
        #------------------------
        self.number_continue_frame = tk.Frame(self.root_window)
        self.number_continue_frame.grid(row = 2, column = 1, padx = 5, pady = 30, sticky = tk.W + tk.E + tk.N + tk.S)

        checkExist = tk.Button(self.number_continue_frame, text = 'Buscar', cursor = 'hand2', font = ('', 10, 'bold'), width = 10, command = self.checkProduct_inDB)
        checkExist.pack(pady = 30)
        self.root_window.bind('<F1>', lambda event : self.checkProduct_inDB())
        CreateToolTip(checkExist, text = 'Para saber si existe dicho producto usa F1 para abrir mas rapido')

        addProduct = tk.Button(self.number_continue_frame, text = 'Añadir', cursor = 'hand2', font = ('', 10, 'bold'), width = 10, command = self.addProduct_toDB)
        addProduct.pack(pady = 30)

        CreateToolTip(addProduct, text = 'El sistema comprobara si existe ya el producto, si existe no se añadira Enter para usar (回车键)，Se podra usar despues de su mensaje')
    
        self.root_window_statusText = tk.Label(self.root_window, text = '', padx = 20, pady = 20, fg = 'green')
        self.root_window_statusText.grid(row = 3, column = 0, columnspan = 2, sticky = tk.W + tk.E)

    def check_status_level(self):
        if self.addProduct_status_level == 0:
            self.root_window_statusText["text"] = ''
            self.root_window_firstLabelFrame_name.focus()
        elif self.addProduct_status_level == 1:
            self.root_window_secondLabelFrame_price.focus()
        elif self.addProduct_status_level == 2:
            self.addProduct_toDB()

        self.addProduct_status_level += 1

    def checkProduct_inDB(self, code = False):
        self.root_window_statusText["text"] = ''
        if not code:
            code = self.root_window_firstLabelFrame_code.get()

        query = 'SELECT `name`, `price` FROM `Product_data` WHERE `code` = ?'
        parameters = (code, )

        returnResponse_query = run_sqlite_query(query, parameters = parameters)

        if len(returnResponse_query) == 0:
            self.root_window_statusText['fg'] = 'green'
            self.root_window_statusText["text"] = 'Este producto no se añadio, puede añadirla'
            return True
        else:
            self.root_window_statusText['fg'] = 'red'
            self.root_window_statusText['text'] = 'Usted ya añadio un producto Nombre: {}, Precio: {}'.format(returnResponse_query[0][0], returnResponse_query[0][1])
            return False


    def addProduct_toDB(self):
        self.root_window_statusText["text"] = ''
        code = self.root_window_firstLabelFrame_code.get()
        if code.isnumeric() and len(code) != 0:

            ifExist = self.checkProduct_inDB(code)

            if ifExist:
                self.root_window_statusText["text"] = ''
                name = self.root_window_firstLabelFrame_name.get()
                price = self.root_window_secondLabelFrame_price.get()

                if name != 0 and isFloat(price):
                    query = 'INSERT INTO `Product_data` (`code`, `name`, `price`) VALUES (?, ?, ?)'
                    parameters = (code, name, price)

                    if run_sqlite_query(query, parameters = parameters):
                        self.root_window_statusText["fg"] = 'green'
                        self.root_window_statusText["text"] = 'Producto añadido: {} | {} | {}'.format(code, name, price)

                        self.root_window_firstLabelFrame_code.delete(0, tk.END)
                        self.root_window_firstLabelFrame_name.delete(0, tk.END)

                        self.root_window_secondLabelFrame_price.delete(0, tk.END)

                        self.addProduct_status_level = 0
                        self.root_window_firstLabelFrame_code.focus_force()
                else:
                    self.root_window_statusText["fg"] = 'red'
                    self.root_window_statusText["text"] = 'Comprueba si el nombre o precio es correcto'
        else:
            self.root_window_statusText["fg"] = 'red'
            self.root_window_statusText["text"] = 'Introduce codigo'


class AppChange():

    addProduct_status_level = code_condition = 0

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('Modificar')

        self.root_window.focus_force()

        tk.Label(self.root_window, text = 'Introduce el codigo del producto', pady = 10, font = ('', 12, 'bold')).grid(row = 0, column = 0, sticky = tk.N + tk.S)
        #First div
        first_frame = tk.Frame(self.root_window, pady = 10, padx = 10)
        first_frame.grid(row = 1, column = 0, sticky = tk.N + tk.S)

        self.search_value_input = tk.Entry(first_frame, width = 80)
        self.search_value_input.grid(row = 0, column = 0)
        
        self.search_value_input.focus_force()

        self.choose_type_search = ttk.Combobox(first_frame, values = ('Codigo', 'Nombre', 'Precio'), state = 'readonly')
        self.choose_type_search.grid(row = 0, column = 1, padx = (0, 5))

        self.choose_type_search.set('Nombre')

        button_toSearch = tk.Button(first_frame, text = 'Buscar', padx = 10, command = self.search_data_fromValue)
        button_toSearch.grid(row = 0, column = 2, padx = (5, 0))
        #----------------------------
        self.root_window.bind("<Return>", lambda event: self.search_data_fromValue())
        CreateToolTip(button_toSearch, text = 'Tecla rapida: Enter <回车>')

        #-----------------------------------------
        #Second div
        second_frame = tk.Frame(self.root_window)
        second_frame.grid(row = 2, column = 0)

        self.showProduct_table = ttk.Treeview(second_frame, columns = ("name", "price"), selectmode = tk.EXTENDED, height = 28)
        #Prepare
        self.showProduct_table.heading('#0', text = 'Codigo', anchor = tk.CENTER)
        self.showProduct_table.column("#0", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)
        self.showProduct_table.heading('name', text = 'Nombre', anchor = tk.CENTER)
        self.showProduct_table.column("name", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)
        self.showProduct_table.heading('price', text = 'Precio', anchor = tk.CENTER)
        self.showProduct_table.column("price", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)

        self.showProduct_table.grid(row = 0, column = 0)
        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        #SCROLL
        showProductScroll = tk.Scrollbar(second_frame, orient = tk.VERTICAL, command = self.showProduct_table.yview)
        showProductScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.showProduct_table.configure(yscrollcommand = showProductScroll.set)

        #Third div
        third_frame = tk.Frame(self.root_window)
        third_frame.grid(row = 3, column = 0, sticky = tk.W + tk.E)

        changeButton = tk.Button(third_frame, text = 'Modificar', padx = 25, cursor = 'hand2', command = self.change_product_fromDB)
        changeButton.grid(row = 0, column = 0, padx = 10, pady = (10, 20))
        #FastKey
        self.root_window.bind("<F10>", lambda event: self.change_product_fromDB())
        CreateToolTip(changeButton, text = 'Tecla rapida: F10')

        deleteButton = tk.Button(third_frame, text = 'Del', padx = 25, cursor = 'hand2', command = self.delete_product_fromDB)
        deleteButton.grid(row = 0, column = 1, padx = 10, pady = (10, 20))
        #FastKey
        self.root_window.bind("<Delete>", lambda event: self.delete_product_fromDB())
        CreateToolTip(deleteButton, text = 'Tecla rapida: Delete')

    def search_data_fromValue(self):

        if len(self.search_value_input.get()) != 0:
            type = ['code', 'name', 'price']

            query = 'SELECT `code`, `name`, `price` FROM `Product_data` WHERE `{}` LIKE ?'.format(type[self.choose_type_search.current()])

            parameters = (self.search_value_input.get()+'%',)

            responseData = run_sqlite_query(query, parameters = parameters)

            for element in self.showProduct_table.get_children():
                self.showProduct_table.delete(element)

            if responseData:
                self.show_data_in_table(responseData)
            else:
                self.showProduct_table.insert('', tk.END, text = 'Vacio', values = ('No hay nada', 'Nada de nada'))
        
    def show_data_in_table(self, data):
        for element in data:
            self.showProduct_table.insert('', tk.END, text = element[0], values = (element[1], element[2]))
    def change_product_fromDB(self):
        if self.checkRegister_is_selected():
            item_to_change = self.showProduct_table.item(self.showProduct_table.selection())
            if item_to_change['text'] != 'Vacio':
                self.open_second_window_toChange(item_to_change)

                self.code_condition = item_to_change['text']

    def open_second_window_toChange(self, element):
        self.second_window = tk.Toplevel()

        self.second_window.title('Cambiar datos')
        self.second_window.focus_force()

        self.second_window.bind('<Return>', lambda event : self.check_status_level())
        #Title
        tk.Label(self.second_window, text = 'Cambiar producto', font = ('times', 18), anchor = tk.CENTER).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        #---------------------------------
        self.second_window_firstLabelFrame = tk.LabelFrame(self.second_window, text = 'Codigo o nombre que desea borrar', padx = 20, pady = 20)
        self.second_window_firstLabelFrame.grid(row = 1, column = 0, pady = 30, columnspan = 2, sticky = tk.W + tk.E, padx = 20)

        #code
        tk.Label(self.second_window_firstLabelFrame, text = 'Codigo: ', font = ('', 14, 'bold')).grid(row = 0, column = 0, padx = (0, 15))
        self.second_window_firstLabelFrame_code = tk.Entry(self.second_window_firstLabelFrame, width = 50)
        self.second_window_firstLabelFrame_code.insert(0, element['text'])

        self.second_window_firstLabelFrame_code.grid(row = 0, column = 1, padx = 5)


        #focus
        self.second_window_firstLabelFrame_code.focus_force()

        #name
        tk.Label(self.second_window_firstLabelFrame, text = 'Nombre: ', font = ('', 14, 'bold')).grid(row = 1, column = 0, padx = (0, 15))
        self.second_window_firstLabelFrame_name = tk.Entry(self.second_window_firstLabelFrame, width = 50)
        self.second_window_firstLabelFrame_name.grid(row = 1, column = 1, padx = 5)
        
        self.second_window_firstLabelFrame_name.insert(0, element['values'][0])
        #----------------------------------
        self.second_window_secondLabelFrame = tk.LabelFrame(self.second_window, text = 'Precio nuevo', padx = 20, pady = 20)
        self.second_window_secondLabelFrame.grid(row = 2, column = 0, pady = 30, sticky = tk.W + tk.E, padx = 20)

        self.second_window_secondLabelFrame_price = tk.Entry(self.second_window_secondLabelFrame,)
        self.second_window_secondLabelFrame_price.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.second_window_secondLabelFrame_price.insert(0, element['values'][1])

        self.number_button_frame = tk.Frame(self.second_window_secondLabelFrame)
        self.number_button_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

        def amountInputButton(number):
            if number == 'del':
                self.second_window_secondLabelFrame_price.delete(len(self.second_window_secondLabelFrame_price.get())-1)
            else:
                self.second_window_secondLabelFrame_price.insert(tk.END, number) 

        tk.Button(self.number_button_frame, text = 7, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 8, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 9, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 4, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 5, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 6, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 1, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 2, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 3, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 0, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '.', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('.')).grid(row = 3, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 'Del', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5)
        #------------------------
        self.number_continue_frame = tk.Frame(self.second_window)
        self.number_continue_frame.grid(row = 2, column = 1, padx = 5, pady = 30, sticky = tk.W + tk.E + tk.N + tk.S)

        checkExist = tk.Button(self.number_continue_frame, text = 'Buscar', cursor = 'hand2', font = ('', 10, 'bold'), width = 30, command = self.checkProduct_inDB)
        checkExist.pack(pady = 30)

        self.second_window.bind('<F1>', lambda event : self.checkProduct_inDB())
        CreateToolTip(checkExist, text = 'Comprueba si ya existe o parecidos, tecla rapida F1')

        addProduct = tk.Button(self.number_continue_frame, text = 'Modificar', cursor = 'hand2', font = ('', 10, 'bold'), width = 30, command = lambda : self.addProduct_toDB())
        addProduct.pack(pady = 30)

        CreateToolTip(addProduct, text = 'Antes de añadir el sistema comprobara si ya existe el producto, Enter (回车键)')
    
        self.second_window_statusText = tk.Label(self.second_window, text = '', padx = 20, pady = 20, fg = 'green')
        self.second_window_statusText.grid(row = 3, column = 0, columnspan = 2, sticky = tk.W + tk.E)
    
    
    def check_status_level(self):
        if self.addProduct_status_level == 0:
            self.second_window_statusText["text"] = ''
            self.second_window_firstLabelFrame_name.focus()
        elif self.addProduct_status_level == 1:
            self.second_window_secondLabelFrame_price.focus()
        elif self.addProduct_status_level == 2:
            self.addProduct_toDB()

        self.addProduct_status_level += 1
    def addProduct_toDB(self):
        self.second_window_statusText["text"] = ''
        code = self.second_window_firstLabelFrame_code.get()
        if code.isnumeric() and len(code) != 0:

            ifExist = self.checkProduct_inDB(code)

            if ifExist:
                self.second_window_statusText["text"] = ''
                name = self.second_window_firstLabelFrame_name.get()
                price = self.second_window_secondLabelFrame_price.get()

                if name != 0 and isFloat(price):
                    query = 'UPDATE `Product_data` SET `code` = ?, `name` = ?, `price` = ? WHERE `code` = ?'
                    parameters = (code, name, price, self.code_condition)

                    if run_sqlite_query(query, parameters = parameters):
                        self.second_window_statusText["fg"] = 'green'
                        self.second_window_statusText["text"] = 'Producto modificado: {} | {} | {}'.format(code, name, price)

                        self.second_window_firstLabelFrame_code.delete(0, tk.END)
                        self.second_window_firstLabelFrame_name.delete(0, tk.END)

                        self.second_window_secondLabelFrame_price.delete(0, tk.END)

                        self.addProduct_status_level = self.code_condition = 0

                        self.search_data_fromValue()
                        
                        self.second_window.destroy()

                        self.second_window_firstLabelFrame_code.focus_force()
                else:
                    self.second_window_statusText["fg"] = 'red'
                    self.second_window_statusText["text"] = 'Compruba si el nombre o precio esta bien'
        else:
            self.second_window_statusText["fg"] = 'red'
            self.second_window_statusText["text"] = 'Introduce codigo'

    def checkProduct_inDB(self, code = False):
        self.second_window_statusText["text"] = ''
        if not code:
            code = self.second_window_firstLabelFrame_code.get()

        if str(self.code_condition) != code:
            query = 'SELECT `name`, `price` FROM `Product_data` WHERE `code` = ?'
            parameters = (code, )

            returnResponse_query = run_sqlite_query(query, parameters = parameters)

            if len(returnResponse_query) == 0:
                self.second_window_statusText['fg'] = 'green'
                self.second_window_statusText["text"] = 'Este producto no se añadio'
                return True
            else:
                self.second_window_statusText['fg'] = 'red'
                self.second_window_statusText['text'] = 'Usted ya añadio este producto Nombre: {}, Precio: {}'.format(returnResponse_query[0][0], returnResponse_query[0][1])
                return False
        else:
            self.second_window_statusText['fg'] = 'black'
            self.second_window_statusText["text"] = 'No modificastes el codigo'
            return True

    def delete_product_fromDB(self):
        if self.checkRegister_is_selected():
            item_to_delete = self.showProduct_table.item(self.showProduct_table.selection())
            if item_to_delete['text'] != 'Vacio':
                msgReturn = messagebox.askokcancel('Confirmar', '¿Seguro que deseas eliminarlo? Una vez borrado no se recupera')

                if msgReturn:
                    query = 'DELETE FROM `Product_data` WHERE `code` = ? AND `name` = ? AND `price` = ?'
                    parameters = (item_to_delete['text'], item_to_delete['values'][0], item_to_delete['values'][1])

                    if run_sqlite_query(query, parameters = parameters):
                        messagebox.showinfo('Del', 'Producto eliminado')
                        self.search_data_fromValue()

                        self.root_window.focus_force()

                        self.search_value_input.focus()
                else:
                    self.root_window.focus_force()


    def checkRegister_is_selected(self):
        if len(str(self.showProduct_table.item(self.showProduct_table.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("Error", "No hay prducto seleccionado, seleccionala")
            self.root_window.focus_force()
            return False

class AppHistory():
    def __init__(self, window):
        self.root_window = window
        self.root_window.title('Buscar historial')

        self.root_window.focus_force()
        #First div
        first_frame = tk.Frame(self.root_window)
        first_frame.grid(row = 0, column = 0, sticky = tk.N + tk.S)

        tk.Label(first_frame, text = 'Buscar historial de ventas', anchor = tk.CENTER).grid(row = 0, column = 0, sticky = tk.W + tk.E, pady = (10, 5))

        self.root_window_firstLabelFrame = tk.LabelFrame(first_frame, text = ' Por fecha ', padx = 10, pady = 10)
        self.root_window_firstLabelFrame.grid(row = 2, column = 0, padx = 5, pady = 5)

        tk.Label(self.root_window_firstLabelFrame, text = 'Fecha', anchor = tk.W).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        self.startDate = DateEntry(self.root_window_firstLabelFrame, width = 15)
        self.startDate.grid(row = 1, column = 0, padx = 10, pady = (5, 15))

        self.endDate = DateEntry(self.root_window_firstLabelFrame, width = 15)
        self.endDate.grid(row = 1, column = 1, padx = 10, pady = (5, 15))

        tk.Label(self.root_window_firstLabelFrame, text = 'Tiempo (hh:mm:ss) Default 24h', anchor = tk.W).grid(row = 2, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        self.startTime = tk.Entry(self.root_window_firstLabelFrame, width = 18, bd = 1, relief = tk.RAISED)
        self.startTime.insert(0, '00:00:00')
        self.startTime.grid(row = 3, column = 0, padx = 10, pady = (5, 15))

        self.endTime = tk.Entry(self.root_window_firstLabelFrame, width = 18, bd = 1, relief = tk.RAISED)
        self.endTime.insert(0, '23:59:59')
        self.endTime.grid(row = 3, column = 1, padx = 10, pady = (5, 15))

        searchHistory_register = tk.Button(self.root_window_firstLabelFrame, cursor = 'hand2', text = 'Buscar', pady = 5, command = self.searchData_inDB)
        searchHistory_register.grid(row = 4, column = 0, columnspan = 2, sticky = tk.W + tk.E, pady = (10, 5))
        #FastKey
        self.root_window.bind("<Return>", lambda event: self.searchData_inDB())
        CreateToolTip(searchHistory_register, text = 'Una vez introducido puede usar Enter <回车键> 快速查找')

        #---------------
        checkHistory_element = tk.Button(first_frame, text = 'Buscar historial', pady = 5, cursor = 'hand2', command = self.check_register)
        checkHistory_element.grid(row = 3, column = 0, pady = (80, 5), sticky = tk.W + tk.E, padx = 10)
        #FastKey
        self.root_window.bind("<F1>", lambda event: self.check_register())
        CreateToolTip(checkHistory_element, text = 'Tecla rapida F1')

        deleteHistory_element = tk.Button(first_frame, text = 'Borrar historial', pady = 5, cursor = 'hand2', command = self.delete_register)
        deleteHistory_element.grid(row = 4, column = 0, pady = 5, sticky = tk.W + tk.E, padx = 10)
        #FastKey
        self.root_window.bind("<F2>", lambda event: self.delete_register())
        CreateToolTip(deleteHistory_element, text = 'Tecla rapida F2')

        #-----------------------------------------
        #Second div
        second_frame = tk.Frame(self.root_window)
        second_frame.grid(row = 0, column = 1)

        self.showHistory_searched = ttk.Treeview(second_frame, columns = ("date_time", "total_price", "number_product", "method_pay"), selectmode = tk.EXTENDED, height = 28)
        #Prepare
        self.showHistory_searched.heading('#0', text = 'id', anchor = tk.CENTER)
        self.showHistory_searched.column("#0", width = 230, stretch = False)
        self.showHistory_searched.heading('date_time', text = 'FechaTiempo', anchor = tk.CENTER)
        self.showHistory_searched.column("date_time", width = 200, stretch = False)
        self.showHistory_searched.heading('total_price', text = 'Total', anchor = tk.CENTER)
        self.showHistory_searched.column("total_price", width = 120, stretch = False)
        self.showHistory_searched.heading('number_product', text = 'Cant', anchor = tk.CENTER)
        self.showHistory_searched.column("number_product", width = 110, stretch = False)
        self.showHistory_searched.heading('method_pay', text = 'Pago', anchor = tk.CENTER)
        self.showHistory_searched.column("method_pay", width = 140, stretch = False)

        self.showHistory_searched.grid(row = 0, column = 0)
        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        #SCROLL
        showHistoryScroll = tk.Scrollbar(second_frame, orient = tk.VERTICAL, command = self.showHistory_searched.yview)
        showHistoryScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.showHistory_searched.configure(yscrollcommand = showHistoryScroll.set)

    def searchData_inDB(self):
        start_date = self.startDate.get_date().strftime("%Y-%m-%d")
        end_date = self.endDate.get_date().strftime("%Y-%m-%d")

        start_time = self.startTime.get()
        end_time = self.endTime.get()

        if (self.checkIf_is_a_timeDate(start_time, 'time') and self.checkIf_is_a_timeDate(end_time, 'time')) and (self.checkIf_is_a_timeDate(start_date, 'date') and self.checkIf_is_a_timeDate(end_date, 'date')):
            query = 'SELECT `id`, `date_time`, `total_price`, `number_product`, `method_pay` FROM `Product_register_pay` WHERE `date_time` BETWEEN ? AND ?'
            parameters = ('{} {}'.format(start_date, start_time), '{} {}'.format(end_date, end_time))
            
            returnResponse = run_sqlite_query(query, parameters = parameters)

            for element in self.showHistory_searched.get_children():
                self.showHistory_searched.delete(element)
            if returnResponse:
                self.show_register_in_table(returnResponse)
            else:
                self.showHistory_searched.insert('', tk.END, text = 'Vacio', values = ('No hay registros', 'en este', 'tiempo', 'fecha'))
        else:
            messagebox.showerror('Error de formato', "Error formato de tiempo, use hh:mm:ss")
            self.root_window.focus_force()

    def show_register_in_table(self, response):
        for element in response:
            self.showHistory_searched.insert('', tk.END, text = element[0], values = (element[1], element[2], element[3], element[4]))
    
    def check_register(self):
        if self.checkRegister_is_selected():
            item_to_check = self.showHistory_searched.item(self.showHistory_searched.selection())
            if item_to_check['text'] != 'Vacio':

                values = (item_to_check['text'], item_to_check['values'][0], item_to_check['values'][1], item_to_check['values'][2], item_to_check['values'][3])
                
                self.open_to_showDataRegister(values)

    def open_to_showDataRegister(self, parameters):
        self.second_window = tk.Toplevel()

        self.second_window.title('Datos')
        self.second_window.focus()

        first_frame = tk.Frame(self.second_window)
        first_frame.grid(row = 0, column = 0)

        show_data_table = ttk.Treeview(first_frame, columns = ("name", "price", "amount", "total"), selectmode = tk.EXTENDED, height = 23)

        show_data_table.heading('#0', text = 'Codigo', anchor = tk.CENTER)
        show_data_table.column("#0", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('name', text = 'Producto', anchor = tk.CENTER)
        show_data_table.column("name", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('price', text = 'Price', anchor = tk.CENTER)
        show_data_table.column("price", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('amount', text = 'Cant.', anchor = tk.CENTER)
        show_data_table.column("amount", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('total', text = 'Total', anchor = tk.CENTER)
        show_data_table.column("total", width = int(self.second_window.winfo_screenwidth()/5)-25, stretch = False)

        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        show_data_table.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)

        #SCROLL
        show_data_tableScroll = tk.Scrollbar(first_frame, orient = tk.VERTICAL, command = show_data_table.yview)
        show_data_tableScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        show_data_table.configure(yscrollcommand = show_data_tableScroll.set)

        #----------------------------
        second_frame = tk.Frame(self.second_window)
        second_frame.grid(row = 1, column = 0, sticky = tk.W + tk.E)

        tk.Label(second_frame, text = 'ID : {}'.format(parameters[0]), font = ('', 10, 'bold')).grid(row = 0, column = 0, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = 'Tiempo : {}'.format(parameters[1]), font = ('', 10, 'bold')).grid(row = 0, column = 1, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = 'Total : {}'.format(parameters[2]), font = ('', 10, 'bold')).grid(row = 0, column = 2, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = 'Cant. : {}'.format(parameters[3]), font = ('', 10, 'bold')).grid(row = 0, column = 3, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = 'Pago : {}'.format("Efectivo" if parameters[4] == 'money' else "Tarjeta credito"), font = ('', 10, 'bold')).grid(row = 0, column = 4, padx = 40, pady = (50, 100))

        query = 'SELECT `data` FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ? AND `method_pay` = ?'

        responseData = run_sqlite_query(query, parameters = parameters)

        if responseData:
            self.json_to_table_register(json.loads(responseData[0][0]), show_data_table)

    def json_to_table_register(self, jsonArr, table):
        for jsonElement in jsonArr['data']:
            table.insert('', tk.END, text = jsonElement['code'], values = (jsonElement['name'], jsonElement['price'], jsonElement['amount'], jsonElement['total_price']))


    def delete_register(self):
        if self.checkRegister_is_selected():
            item_to_delete = self.showHistory_searched.item(self.showHistory_searched.selection())
            if item_to_delete['text'] != 'Vacio':
                msgReturn = messagebox.askokcancel('Confirmar', '¿Seguro que desea borrarlo? Una vez borrado no se recupera')

                if msgReturn:

                    #--------------
                    parameters = (item_to_delete['text'], item_to_delete['values'][0], item_to_delete['values'][1], item_to_delete['values'][2])
                    #--------------
                    query_add = 'INSERT INTO `Product_deletedRegister_pay` SELECT * FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ?'
                    if run_sqlite_query(query_add, parameters = parameters):
                        query_delete = 'DELETE FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ?'
                        if run_sqlite_query(query_delete, parameters = parameters):
                            messagebox.showinfo('Eliminar', 'Registro eliminado')
                            self.root_window.focus_force()

                            self.searchData_inDB()
                            return True

                    messagebox.showerror('Eliminar', 'Hubo un error en el proceso, repita la acción')
                else:
                    self.root_window.focus_force()

    def checkIf_is_a_timeDate(self, timeDate_str, typeOf):
        if typeOf == 'time':
            checkArr = timeDate_str.split(':')
        else:
            checkArr = timeDate_str.split('-')

        if len(checkArr) == 3:
            
            isNumber = 0

            for num in checkArr:
                if num.isnumeric():
                    isNumber += 1

            if isNumber == 3:
                return True

        return False

    def checkRegister_is_selected(self):
        if len(str(self.showHistory_searched.item(self.showHistory_searched.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("Error", "No hay ningun registro seleccionado, seleccionalo")
            self.root_window.focus_force()
            return False

#Create ToolTips
class CreateToolTip(object):
    '''
        Create a tooltip
    '''
    def __init__ (self, element, text = 'text'):
        self.toolTip_element = element
        self.toolTip_text = text
        self.toolTip_element.bind("<Enter>", self.enter_toolTip)
        self.toolTip_element.bind("<Leave>", self.close_toolTip)

    def enter_toolTip(self, event = None):
        x = y = 0
        x, y, cx, cy = self.toolTip_element.bbox("insert")

        x += self.toolTip_element.winfo_rootx() + 45
        y += self.toolTip_element.winfo_rooty() + 20

        # Create a toplevel window z-index
        self.toolTip_element_topLevel = tk.Toplevel(self.toolTip_element)
        
        self.toolTip_element_topLevel.wm_overrideredirect(True)
        self.toolTip_element_topLevel.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.toolTip_element_topLevel, text = self.toolTip_text, wraplength = 200, justify = 'left', background='#d8ffa1', relief='solid', borderwidth=1, font=("times", "8", "normal"), padx = 3, pady = 3)
        
        label.pack(ipadx = 1)

    def close_toolTip(self, event = None):
        if self.toolTip_element_topLevel:
            self.toolTip_element_topLevel.destroy()

#Check if it is the main py
if __name__ == '__main__':
    if not os.path.isfile('./data/database.db') and os.path.isfile('./data/delete.log'):
        os.startfile(os.getcwd()+'/readme.txt')
        prepare_database()
        os.remove('./data/delete.log')

        messagebox.showinfo('Datos', 'Su sistema se instalo correctamente, vuelva a abrir el programa')



    else:
        root = tk.Tk()
        application = AppOpen(root)
        
        root.mainloop()