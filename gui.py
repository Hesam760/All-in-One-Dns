import customtkinter as ctk
from app import DNS
import threading
from utils import (
    add_icon,
    delete_icon,
    home_icon,
    refresh_icon,
    eu_icon,
    us_icon,
    sg_icon,
    ir_icon,
    red_icon,
    green_icon,
)

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.update_idletasks()
root.geometry("700x500")
root.resizable(False, False)
root.iconbitmap("./config/icon.ico")

overlay_frame = ctk.CTkFrame(root, fg_color="transparent")
overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# Sidebar
sidebar = ctk.CTkFrame(overlay_frame, width=160)
sidebar.pack(side="left", fill="y")

content_frame = ctk.CTkFrame(overlay_frame, fg_color="transparent")
content_frame.pack(side="left", expand=True, fill="both")

home_page = ctk.CTkFrame(content_frame, fg_color="#0a1a3f")
add_page = ctk.CTkFrame(content_frame, fg_color="#0a1a3f")
delete_page = ctk.CTkFrame(content_frame, fg_color="#0a1a3f")


def show_page(page):
    global add_page_state_label
    global delete_page_state_label

    for frame in [home_page, add_page, delete_page]:
        frame.pack_forget()
    if page == delete_page:
        render_delete_page()
    page.pack(expand=True, fill="both")
    try:
        add_page_state_label.configure(text="")
        delete_page_state_label.configure(text="")
    except NameError:
        pass


home_btn = ctk.CTkButton(
    sidebar,
    text="Home",
    image=home_icon,
    command=lambda: show_page(home_page),
    compound="left",
    anchor="w",
    fg_color="#78acd6",
    text_color="#000",
    height=40,
)
home_btn.pack(pady=(20, 10), padx=10, fill="x")
add_btn = ctk.CTkButton(
    sidebar,
    text="Add Service",
    image=add_icon,
    command=lambda: show_page(add_page),
    compound="left",
    anchor="w",
    fg_color="#78acd6",
    text_color="#000",
    height=40,
)
add_btn.pack(pady=10, padx=10, fill="x")
delete_btn = ctk.CTkButton(
    sidebar,
    text="Delete Service",
    image=delete_icon,
    command=lambda: show_page(delete_page),
    compound="left",
    anchor="w",
    fg_color="#78acd6",
    text_color="#000",
    height=40,
)
delete_btn.pack(pady=10, padx=10, fill="x")

show_page(home_page)

root.title("All in One DNS")
title_label = ctk.CTkLabel(
    home_page,
    text="All in One DNS",
    bg_color="#78acd6",
    text_color="#000",
    font=ctk.CTkFont(size=30, weight="bold"),
    width=800,
)
title_label.place(relx=0.5, rely=0.04, anchor="center")

dns = DNS()
dns_servers = dns.get_servers()
dns_server_names = list(dns_servers.keys())
connected = False

# home page
combobox_label = ctk.CTkLabel(
    home_page, text="Choose your service :", text_color="#78acd6"
)
combobox_label.place(relx=0.5, rely=0.18, anchor="center")
combobox = ctk.CTkOptionMenu(
    home_page,
    values=dns_server_names,
    bg_color="#061F62",
    fg_color="#6380A2",
    text_color="black",
    button_color="#CEC6C4",
    width=200,
    height=30,
    anchor="center",
)
combobox.place(relx=0.5, rely=0.25, anchor="center")


def button_event() -> None:
    global connected
    global button
    global delete_btn
    global combobox
    dns_server_names = list(dns_servers.keys())

    if connected:
        dns.disconnect_dns()
        button.configure(image=green_icon)
        combobox.configure(state="normal")
        delete_btn.configure(state="normal")
        combobox.set(dns_server_names[0])
        connected = False

    else:
        dns.connect_dns(combobox.get())
        combobox.configure(state="disabled")
        button.configure(image=red_icon)
        delete_btn.configure(state="disabled")
        connected = True


def update_pings_async():
    eu_ping = dns.get_ping("4.2.2.4")
    us_ping = dns.get_ping("204.106.240.53")
    asia_ping = dns.get_ping("203.126.118.38")
    ir_ping = dns.get_ping("85.15.1.14")

    root.after(
        0,
        lambda: ping_eu_label.configure(text=f"  EU Ping :   {eu_ping}", image=eu_icon),
    )
    root.after(
        0,
        lambda: ping_us_label.configure(text=f"  US Ping :   {us_ping}", image=us_icon),
    )
    root.after(
        0,
        lambda: ping_asia_label.configure(
            text=f"  Asia Ping :   {asia_ping}", image=sg_icon
        ),
    )
    root.after(
        0,
        lambda: ping_ir_label.configure(text=f"  IR Ping :   {ir_ping}", image=ir_icon),
    )


def update_pings():
    threading.Thread(target=update_pings_async, daemon=True).start()


current_dns, status = dns.check_dns_status()
connected = status
button = ctk.CTkButton(
    home_page,
    image=red_icon if status else green_icon,
    text=None,
    width=64,
    height=64,
    command=button_event,
    fg_color="transparent",
    text_color="white",
    corner_radius=5,
)
if status:
    combobox.configure(state="disabled")
    dns_list = dns_servers.items()
    dns_service = ""
    for key, value in dns_list:
        if current_dns == str(value).split(" ")[0]:
            dns_service = key
            break
    combobox.set(dns_service)
    delete_btn.configure(state="disabled")

button.place(relx=0.5, rely=0.40, anchor="center")

ping_header = ctk.CTkLabel(home_page, text="Current Pings :", font=("Arial", 16))
ping_header.place(relx=0.04, rely=0.63, anchor="w")
ping_refresh_btn = ctk.CTkButton(
    home_page,
    text="",
    image=refresh_icon,
    width=16,
    height=16,
    command=update_pings,
    fg_color="transparent",
)
ping_refresh_btn.place(relx=0.8, rely=0.63, anchor="w")

ping_eu_label = ctk.CTkLabel(home_page, text="", font=("Arial", 16), compound="left")
ping_eu_label.place(relx=0.1, rely=0.70, anchor="w")
ping_us_label = ctk.CTkLabel(home_page, text="", font=("Arial", 16), compound="left")
ping_us_label.place(relx=0.1, rely=0.77, anchor="w")
ping_asia_label = ctk.CTkLabel(home_page, text="", font=("Arial", 16), compound="left")
ping_asia_label.place(relx=0.1, rely=0.84, anchor="w")
ping_ir_label = ctk.CTkLabel(home_page, text="", font=("Arial", 16), compound="left")
ping_ir_label.place(relx=0.1, rely=0.91, anchor="w")


# add page
def save_dns() -> None:
    global combobox

    service_name = service_entry.get()
    primary_dns = primary_entry.get()
    secondary_dns = secondary_entry.get()
    new_service = {f"{service_name}": "{} {}".format(primary_dns, secondary_dns)}
    message, state = dns.add_dns(new_service)
    if not state:
        add_page_state_label.configure(text=message, text_color="red")
    else:
        add_page_state_label.configure(text=message, text_color="green")
        service_entry.delete(0, "end")
        primary_entry.delete(0, "end")
        secondary_entry.delete(0, "end")
        combobox.configure(values=dns.get_servers())


service_label = ctk.CTkLabel(add_page, text="Service Name:")
service_label.pack(pady=5)
service_entry = ctk.CTkEntry(add_page, width=200)
service_entry.pack(pady=5)

primary_label = ctk.CTkLabel(add_page, text="Primary DNS:")
primary_label.pack(pady=5)
primary_entry = ctk.CTkEntry(add_page, width=200)
primary_entry.pack(pady=5)

secondary_label = ctk.CTkLabel(add_page, text="Secondary DNS:")
secondary_label.pack(pady=5)
secondary_entry = ctk.CTkEntry(add_page, width=200)
secondary_entry.pack(pady=5)

save_button = ctk.CTkButton(
    add_page,
    text="Save",
    command=save_dns,
    fg_color="yellow",
    hover_color="#e4e697",
    text_color="black",
    corner_radius=5,
    width=200,
)
save_button.pack(pady=20)

add_page_state_label = ctk.CTkLabel(add_page, text="", text_color="red")
add_page_state_label.pack(pady=5)


# delete page
def delete_service(item, service_label, service_button) -> None:
    global combobox
    message, state = dns.delete_dns(item)
    if state:
        service_label.destroy()
        service_button.destroy()
        combobox.configure(values=dns.get_servers())
        combobox.set("")
        render_delete_page()
        delete_page_state_label.configure(text=message, text_color="green")
    else:
        delete_page_state_label.configure(text=message, text_color="red")


def create_delete_widgets(item, y):
    server_name_label = ctk.CTkLabel(delete_page, text=f"{item}")
    server_name_label.place(relx=0.2, rely=y, anchor="center")

    server_delete_button = ctk.CTkButton(
        delete_page, text="Delete", fg_color="red", hover_color="#ed6d6d"
    )
    server_delete_button.place(relx=0.7, rely=y, anchor="center")

    server_delete_button.configure(
        command=lambda: delete_service(item, server_name_label, server_delete_button)
    )


def render_delete_page():
    for widget in delete_page.winfo_children():
        if widget != delete_page_state_label:
            widget.destroy()

    dns_server_names = dns.get_servers()
    for index, item in enumerate(dns_server_names):
        y = 0.1 + index * 0.08
        create_delete_widgets(item, y)


delete_page_state_label = ctk.CTkLabel(delete_page, text="", text_color="red")
delete_page_state_label.pack(pady=2)

version_lebel = ctk.CTkLabel(sidebar, text="Version 1.0.4")
version_lebel.place(relx=0.5, rely=1, anchor="s")

root.mainloop()
