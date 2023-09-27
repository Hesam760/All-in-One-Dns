import customtkinter as ctk
from PIL import Image, ImageTk
from app import connect_dns, disconnect_dns, add_dns, get_servers, delete_dns

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.geometry("400x400")
root.resizable(False,False)

image_path = "config/bg.jpg" 
image = Image.open(image_path)

background_image = ctk.CTkImage(light_image=image, dark_image=image, size=(400,400))
background_frame = ctk.CTkFrame(root, width=root.winfo_width(), height=root.winfo_height())
background_frame.pack(expand=True, fill="both")
background_label = ctk.CTkLabel(background_frame, image=background_image, text="")
background_label.place(x=0, y=0, relwidth=1, relheight=1)

root.title("All in One DNS")
title_label = ctk.CTkLabel(background_frame, text="All in One DNS", bg_color="#040F49" ,font=ctk.CTkFont(size=30, weight="bold"),width=400)
title_label.place(relx=0.5, rely=0.1, anchor="center")

dns_servers = get_servers()
dns_server_names = list(dns_servers.keys())
combobox = ctk.CTkOptionMenu(root, values=dns_server_names, bg_color="#061F62", fg_color="#6380A2", text_color="black", button_color="#CEC6C4")
combobox.place(relx=0.5, rely=0.3, anchor="center")

connected = False

def button_event():
    global connected
    global button
    global delete_server_button
    
    if connected:
        disconnect_dns()
        button.configure(text="Connect", fg_color="green", hover_color="#98e3c6")
        combobox.configure(state="normal")
        delete_server_button.configure(state="normal")
        connected = False
            
    else:
        connect_dns(combobox.get())
        combobox.configure(state="disabled") 
        button.configure(text="Disconnect", fg_color="red", hover_color="#ff9999")
        delete_server_button.configure(state="disabled")
        connected = True

button = ctk.CTkButton(root, text="Connect", command=button_event, fg_color="#2FA572", hover_color="#98e3c6", text_color="black", corner_radius=5)
button.place(relx=0.5, rely=0.45, anchor="center")

def add_server():
    
    def save_dns():
        service_name = service_entry.get()
        primary_dns = primary_entry.get()
        secondary_dns = secondary_entry.get()
        new_service = {f"{service_name}" :"{} {}".format(primary_dns, secondary_dns)}
        output = add_dns(new_service)
        if output != True :
            errors_label.configure(text=f"{output}")
        else :
            add_server_window.destroy()
            combobox.configure(values=get_servers())
     
    root_x, root_y = root.winfo_x(), root.winfo_y()

    offset_x, offset_y = 50, 50
    new_window_x = root_x + offset_x
    new_window_y = root_y + offset_y    
    add_server_window = ctk.CTkToplevel(root)
    add_server_window.title("Add DNS Server")
    add_server_window.geometry(f"300x400+{new_window_x}+{new_window_y}")
    add_server_window.resizable(False,False)
    add_server_window.attributes('-toolwindow', True)
    add_server_window.grab_set()
    add_server_window.focus_set()

    errors_label = ctk.CTkLabel(add_server_window, text="", text_color="red")
    errors_label.pack(pady=1)

    service_label = ctk.CTkLabel(add_server_window, text="Service Name:")
    service_label.pack(pady=5)
    service_entry = ctk.CTkEntry(add_server_window)
    service_entry.pack(pady=5)
    
    primary_label = ctk.CTkLabel(add_server_window, text="Primary DNS:")
    primary_label.pack(pady=5)
    primary_entry = ctk.CTkEntry(add_server_window)
    primary_entry.pack(pady=5)

    secondary_label = ctk.CTkLabel(add_server_window, text="Secondary DNS:")
    secondary_label.pack(pady=5)
    secondary_entry = ctk.CTkEntry(add_server_window)
    secondary_entry.pack(pady=5)

    save_button = ctk.CTkButton(add_server_window, text="Save", command=save_dns, fg_color="yellow", hover_color="#e4e697", text_color="black", corner_radius=5)
    save_button.pack(pady=15)
   
add_server_button = ctk.CTkButton(root, text="Add New Service", command=add_server, fg_color="#0A6DD3", hover_color="#78acd6", text_color="white", corner_radius=5)
add_server_button.place(relx=0.3, rely=0.68, anchor="center")

        
def delete_server_event():
    
    def delete_service(item, service_label, service_button):
        if delete_dns(item):
            service_label.destroy()
            service_button.destroy()
            combobox.configure(values=get_servers())
            combobox.set('')
        else :
            errors_label.configure(text="Cant delete service")
    
    root_x, root_y = root.winfo_x(), root.winfo_y()

    offset_x, offset_y = 50, 50
    new_window_x = root_x + offset_x
    new_window_y = root_y + offset_y
    
    delete_server_window = ctk.CTkToplevel(root)
    delete_server_window.title("Delete DNS Server")
    delete_server_window.geometry(f"300x400+{new_window_x}+{new_window_y}")
    delete_server_window.resizable(False,False)
    delete_server_window.attributes('-toolwindow', True)
    delete_server_window.grab_set()
    delete_server_window.focus_set()
     
    errors_label = ctk.CTkLabel(delete_server_window, text="", text_color="red")
    errors_label.pack(pady=1)
    
    dns_server_names = get_servers()
    for index, item in enumerate(dns_server_names):
        server_name_label = ctk.CTkLabel(delete_server_window, text=f"{item}")
        server_name_label.place(relx=0.2, rely=float(f"0.{index + 1}"), anchor="center")
        
        server_delete_button = ctk.CTkButton(delete_server_window, text="Delete", command=lambda name=item: delete_service(name, server_name_label, server_delete_button), fg_color="red", hover_color="#ed6d6d")
        server_delete_button.place(relx=0.7, rely=float(f"0.{index + 1}"), anchor="center")
          
delete_server_button = ctk.CTkButton(root, text="Delete Service", command=delete_server_event, fg_color="red", text_color="white", corner_radius=5, hover_color="#ed6d6d")
delete_server_button.place(relx=0.7, rely=0.68, anchor="center")

root.mainloop()
