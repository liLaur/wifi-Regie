from tkinter import *
import os, time, subprocess, socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import Checkbutton
import wmi

steps = [
    'Configurator de WiFi.\n\nCa acest program să funcționeze înainte de a apăsa Start deconecteaza-te de la orice rețea! Și introdu parola de admin a router-ului.',
    '1. Conecteaza-ti laptopul la reteaua de internet din perete prin switch cu un cablu Ethernet.\n\nAșteaptă sa se conecteze laptopul la internet și apasa NEXT.',
    '2. Deconectează cablul de internet din switch și conectează-l într-un port LAN (de obicei portocaliu) și asteaptă câteva secunde.\n\nCand apesi NEXT o sa se deschida un browser si o sa se completeze campurile router-ului.',
    '3. Conectează cablul de internet din laptop in swith și mută cablul in router din LAN în WAN.\n\nAr trebui ca led-ul de la internet sa se aprinda pentru o secunda portocaliu apoi verde (sau direct verde).'
]

step = 0
data = None
browser = None
admin_password = None

dhcp_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]/span[2]/input'
statip_xpath = '/html/body/div[3]/div/div[3]/div/div/ul/li[2]/label'

ip_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div[1]/div[2]/div[1]/span[2]/input'
mask_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div[2]/div[2]/div[1]/span[2]/input'
gateway_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div[3]/div[2]/div[1]/span[2]/input'
dns_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div[4]/div[2]/div[1]/span[2]/input'
dns2_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[4]/div/div/div[5]/div[2]/div[1]/span[2]/input'
saveBtn_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/div[3]/div[2]/div[1]/a'
mac_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[3]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/span[2]/input'
macclone_xpath = '/html/body/div[3]/div/div[3]/div/div/ul/li[2]/label'

password_xpath = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div[3]/div[3]/div/div/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/span[2]/input[1]'
loginBtn_xpath = '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div[3]/div[3]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/a'

def find_true_ethernet():
    c = wmi.WMI()
    for adapter in c.Win32_NetworkAdapter():
        if adapter.AdapterType == "Ethernet 802.3" and "Wireless" not in adapter.Name:
            return adapter.Description
        
def get_full_adapter_section():
    ethernet_description = find_true_ethernet()

    p = subprocess.Popen(['ipconfig', '/all'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    adapters = str(out).split("Ethernet adapter Ethernet")
    for adapter in adapters:
        if ethernet_description in adapter:
            return adapter

def checkInternetConnection():
    os.system('ping -n 1 172.217.20.14 > .out')
    out = open(".out", "r").read()
    os.remove(".out")
    if "Destination host unreachable" in str(out) or "100% loss" in str(out):
        return False
    else:
        return True
    
def getCabledNetworkData():
    # Resetare IP
    os.system('ipconfig -release')
    os.system('ipconfig -renew')
    
    # Obtinere date retea
    ethernet = get_full_adapter_section()

    if "media disconnected" in ethernet.lower():
        info_text.config(text= steps[step] + "\n\nConecteaza cablul de Ethernet!!! Nu WIFI!!!")
        return
    else:
        ip = ethernet.split("IPv4 Address")[1].split('\\r')[0].split(': ')[1].split('(')[0]
        gateway = ethernet.split("Default Gateway")[1].split('\\r')[0].split(': ')[1]
        mac = ethernet.split("Physical Address")[1].split('\\r')[0].split(': ')[1]
        mask = ethernet.split("Subnet Mask")[1].split('\\r')[0].split(': ')[1]

        data = {"ip": ip,
            "mask": mask,
            "gateway": gateway,
            "mac": mac,
            "dns": "94.140.14.14" if ad_block.get() else "1.1.1.1",
            "sdns": "94.140.15.15" if ad_block.get() else "1.0.0.1"}
        return data

root = Tk()
root.title("Wi-Fi Config")

windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()

positionRight = int(root.winfo_screenwidth()/2 - 1000/2)
positionDown = int(root.winfo_screenheight()/2 - 500/2)

root.geometry(f"1000x500+{positionRight}+{positionDown}")
root.resizable(False, False)

ad_block = BooleanVar()

def next_step():
    global step, data, admin_password
    
    if step == 0 and (password_text.get() == "" or "Introdu parola!!!" in password_text.get()):
        password_text.delete(0, END)
        password_text.insert(0, "Introdu parola!!!")
        return

    if admin_password is None:
        admin_password = password_text.get()
    
    password_label.destroy()
    password_text.destroy()
    ad_block_box.destroy()

    info_text.config(text="...")
    match step:
        case 1:
            if checkInternetConnection():
                data = getCabledNetworkData()
                if data != None:
                    net_data = Label(main, text=str(data), bg="#282828", fg="white", font=('Arial', 12))
                    net_data.place(relx=0.5, rely=0.9, anchor=CENTER)
                    step += 1
                    info_text.config(text=steps[step])
                    action_button.config(text="Next")
            else:
                info_text.config(text= steps[step] + "\n\nLaptopul nu este conectat la internet!!!!!!")
        case 2:
            opt = webdriver.ChromeOptions()
            opt.add_argument("--log-level=OFF")

            global browser
            browser = webdriver.Chrome(options=opt)
            browser.get("http://192.168.0.1")
            browser.maximize_window()

            def goToNet():
                global step
                browser.get("http://192.168.0.1/#wanSettings")
                time.sleep(1)

                # Setare conexiune DHCP
                browser.find_element(By.XPATH, dhcp_xpath).click()
                time.sleep(.5)
                browser.find_element(By.XPATH, statip_xpath).click()
                print("dchp")
                time.sleep(.5)

                # Inlocuire IP
                browser.find_element(By.XPATH, ip_xpath).clear()
                browser.find_element(By.XPATH, ip_xpath).send_keys(data["ip"])
                print("ip")
                time.sleep(.5)

                # Inlocuire masca
                browser.find_element(By.XPATH, mask_xpath).clear()
                browser.find_element(By.XPATH, mask_xpath).send_keys(data["mask"])
                print("mask")
                time.sleep(.5)

                # Inlocuire gateway
                browser.find_element(By.XPATH, gateway_xpath).clear()
                browser.find_element(By.XPATH, gateway_xpath).send_keys(data["gateway"])
                print("gateway")
                time.sleep(.5)

                # Inlocuire Primary DNS
                browser.find_element(By.XPATH, dns_xpath).clear()
                browser.find_element(By.XPATH, dns_xpath).send_keys(data["dns"])
                print("dns")
                time.sleep(.5)

                # Inlocuire Secondary DND
                browser.find_element(By.XPATH, dns2_xpath).clear()
                browser.find_element(By.XPATH, dns2_xpath).send_keys(data["sdns"])
                print("dns2")
                time.sleep(.5)

                el = browser.find_element(By.XPATH, mac_xpath)
                js_code = "arguments[0].scrollIntoView();"
                browser.execute_script(js_code, el)
                time.sleep(.5)

                # Setare MAC ca "Clone MAC"
                browser.find_element(By.XPATH, mac_xpath).click()
                time.sleep(.5)
                browser.find_element(By.XPATH, macclone_xpath).click()
                print("mac")
                time.sleep(.5)

                # Salveaza setarile
                browser.find_element(By.XPATH, saveBtn_xpath).click()
                time.sleep(2)

                browser.quit()

                step += 1
                info_text.config(text=steps[step])
                action_button.config(text="Quit")
            
            def login():
                try: 
                    browser.find_element(By.XPATH, password_xpath).send_keys(admin_password)
                    browser.find_element(By.XPATH, loginBtn_xpath).click()
                    time.sleep(2)
                    goToNet()
                except:
                    time.sleep(1)
                    login()

            login()
        case 0:
            step += 1
            info_text.config(text=steps[step])
            action_button.config(text="Next")
        case 3:
            info_text.config(text="Good bye!")
            time.sleep(.5)
            exit()


main = Frame(root, bg="#282828")
main.place(relheight=1, relwidth=1)

info_text = Label(main, text=steps[step], bg="#282828", fg="white", font=('Arial', 20), wraplength=800)
info_text.place(relx=0.5, rely=0.2, anchor=CENTER)

password_label = Label(main, text="Parola admin router (nu parola WiFi)", bg="#282828", fg="white", font=('Arial', 15))
password_label.place(relx=0.5, rely=0.42, anchor=CENTER)
password_text = Entry(main, font=('Arial', 20), width=30)
password_text.place(relx=0.5, rely=0.5, anchor=CENTER)
password_text.focus()
ad_block_box = Checkbutton(main, text="Blocare anunturi in retea?", bg="#282828", activebackground="#282828", fg="white", selectcolor="black", font=('Arial', 15), variable=ad_block)
ad_block_box.place(relx=0.5, rely=0.6, anchor=CENTER)
ad_block.set(True)


action_button = Button(main, text="Start!", bg="white", fg="black", font=('Arial', 20), padx=20, command=next_step)
action_button.place(relx=0.5, rely=0.75, anchor=CENTER)
root.mainloop()