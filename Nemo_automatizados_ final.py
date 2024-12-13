import customtkinter as ctk
import paho.mqtt.client as mqtt
import requests
import random
from PIL import Image
from io import BytesIO

#funções auxiliares
get_char_id = lambda a,b: random.randint(a, b)

##requests (aquisições)
def request_api(url):
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
def get_quote():
    data = request_api(f'https://philosophyapi.pythonanywhere.com/api/philosophers/')
    while True:
        n = random.randint(0,8)
        m = random.randint(0, len(data['results'][n]['ideas'])-1)
        author = data['results'][n]['name'] 
        daily_quote = data['results'][n]['ideas'][m]
        if len(daily_quote) < 200: #Não quero lidar com frases grandes 
            break

    if len(daily_quote) > 60:
        corte = round(len(daily_quote)/2) #adequando a frase à label
        while daily_quote[corte] != " ":
            corte += 1
        daily_quote = daily_quote[:corte] + "\n" + daily_quote[corte:]
    return daily_quote, author

def request_pkemon():
    char_id = get_char_id(1,1015)
    pk_url = f"https://pokeapi.co/api/v2/pokemon/{char_id}"
    pk_data = request_api(pk_url)
    pk_name = pk_data["name"]
    pk_img_url = pk_data["sprites"]["front_default"]
    pk_resp = requests.get(pk_img_url)
    pk_img = Image.open(BytesIO(pk_resp.content)) 
    return pk_name, pk_img

def request_dragonball():
    char_id = get_char_id(1,35)
    db_url = f"https://dragonball-api.com/api/characters/{char_id}"
    db_data = request_api(db_url)
    db_name = db_data["name"]
    db_img_url = db_data["image"]
    response = requests.get(db_img_url)
    db_img = Image.open(BytesIO(response.content))
    return db_name, db_img
    
valor_recebido = None    # Sim, uma variável global! As vezes, elas são úteis

def on_message(client, userdata, mensagem):
    global valor_recebido
    valor_recebido = mensagem.payload.decode()

cliente = mqtt.Client()
cliente.on_message = on_message
cliente.connect("test.mosquitto.org")
cliente.subscribe("UFSC/DAS/NEMO")
cliente.loop_start() 
    
def atualizar_contador():
    global contador
    contador += 1
    if valor_recebido is not None:
        dados = valor_recebido.split(",") #fazer fç set_texto
        texto_cpu.set(f"CPU%: {dados[0].replace("[","")}")  # Atualiza a variável
        texto_ram.set(f"RAM%: {dados[1]}") 
        texto_perc_bateria.set(f"BATERIA%: {dados[2]}")  #notebook #apenas teste, utíl para um aquisição de dados em campo (conferir bateria)
        texto_carregando_bateria.set(f"CARREGANDO: {dados[3]}") 
        texto_freq_atual.set(f"FREQ ATUAL: {dados[4]} MHz") 
        texto_freq_max.set(f"FREQ BASE: {dados[5]} MHz") #É pra ser constante, apenas teste
        disco_usado.set(f"DISCO USADO: {dados[7]}b")
        disco_livre.set(f"DISCO LIVRE: {dados[8]}b")
    janela.after(1000, atualizar_contador) 

#GRÁFICO


#fazer função



#configuração da janela
janela = ctk.CTk()
janela.title("Teste_interface")
janela.iconbitmap("icon.ico")
janela.geometry("720x480")
janela.minsize(width= 640, height=420)
#janela.configure()
janela._set_appearance_mode("system")  #modo claro ou escuro de acordo com o sistema
#janela.iconify() #fecha a janela
#janela.withdraw()
#janela.update() #chamar antes de deiconify
#janela.deiconify() #abre a janela


#label (frase do dia)
ctk.CTkLabel(janela, text=get_quote()[0], font=("Times", 20,"bold"),anchor="center").pack(pady=2)
ctk.CTkLabel(janela, text=get_quote()[1], font=("Times", 11),text_color="gray").pack()

#variáveis de texto para os dados do mosquitto
texto_cpu, texto_ram, texto_perc_bateria, texto_carregando_bateria\
, texto_freq_atual, texto_freq_max = ctk.StringVar(), ctk.StringVar(),\
      ctk.StringVar(), ctk.StringVar(), ctk.StringVar(), ctk.StringVar()  #horrível kkkkkkk
texto_ram.set("RAM%:  ")
texto_perc_bateria.set("Bateria%:  ")
texto_carregando_bateria.set("Carregando:  ")
texto_cpu.set("CPU%:")
texto_freq_atual.set("Freq atual:")
texto_freq_max.set("Freq max:")
disco_usado, disco_livre = ctk.StringVar(), ctk.StringVar()
disco_livre.set(0)
disco_usado.set(0)

##frame(esquerda)
frame2 = ctk.CTkFrame(janela)#janela.winfo_width()-
frame2.place( relx=0.02, rely=0.6, anchor="w",relheight=0.8,relwidth=0.3)
ctk.CTkLabel(frame2, textvariable=texto_ram, font=("courier", 14)).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, text="BATERIA", font=("arial", 18),text_color="cyan").pack(anchor="center",pady=5)
ctk.CTkLabel(frame2, textvariable=texto_perc_bateria, font=("courier", 14),).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, textvariable=texto_carregando_bateria, font=("courier", 14),).pack(anchor="w",pady=2)
ctk.CTkLabel(frame2, text="CPU", font=("Arial", 18),text_color="cyan").pack(anchor="center",pady=5)
ctk.CTkLabel(frame2, textvariable=texto_cpu, font=("courier", 14)).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, textvariable=texto_freq_atual, font=("courier", 14),).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, textvariable=texto_freq_max, font=("courier", 14),).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, textvariable=disco_usado, font=("courier", 14),).pack(anchor="w",pady=4)
ctk.CTkLabel(frame2, textvariable=disco_livre, font=("courier", 14),).pack(anchor="w",pady=4)

##tab view (à direita)
tabview = ctk.CTkTabview(janela, width=220, height=700)
tabview.pack(expand = True, anchor="e",padx=10,pady=10)
tabview.add("Pókemon")
tabview.add("Dragon Ball")
tabview.tab("Pókemon").grid_columnconfigure(0, weight=1)
tabview.tab("Dragon Ball").grid_columnconfigure(0, weight=1)    

#arquivando texto e imagem
pk_hd_text,pk_hd_img = request_pkemon() 
poke_img = ctk.CTkImage(dark_image=pk_hd_img, size=(190, 200))
db_hd_text,db_hd_img = request_dragonball() 
db_img = ctk.CTkImage(dark_image=db_hd_img, size=(170, 240))

#ajustando a tabela
tb_lb_1 = ctk.CTkLabel(tabview.tab("Pókemon"),image= poke_img,text="")  #width=50
tb_lb_1_text = ctk.CTkLabel(tabview.tab("Pókemon"),text = pk_hd_text, font=("impact", 24))
tb_lb_2 = ctk.CTkLabel(tabview.tab("Dragon Ball"),image= db_img,text="").pack(pady=20)
tb_lb_2_text = ctk.CTkLabel(tabview.tab("Dragon Ball"),text = db_hd_text, font=("impact", 24)).pack()
tb_lb_1.pack(pady=20)
tb_lb_1_text.pack()

contador = 0 #usado para atualizar o contador
#loop
atualizar_contador()
janela.mainloop()


  