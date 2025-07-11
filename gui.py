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
    green_circle_icon,
    red_circle_icon,
    num_1_icon,
    num_2_icon,
    info_icon,
    remove_icon,
    uae_icon,
    fr_icon,
    ca_icon,
    tr_icon,
)

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.update_idletasks()
root.geometry("700x500")
root.resizable(False, False)
root.iconbitmap("./config/icon.ico")
root.title("All in One DNS")

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
    fg_color="#122759",
    text_color="#fff",
    height=40,
)
home_btn.pack(pady=(10, 5), padx=10, fill="x")
add_btn = ctk.CTkButton(
    sidebar,
    text="Add Service",
    image=add_icon,
    command=lambda: show_page(add_page),
    compound="left",
    anchor="w",
    fg_color="#122759",
    text_color="#fff",
    height=40,
)
add_btn.pack(pady=5, padx=10, fill="x")
delete_btn = ctk.CTkButton(
    sidebar,
    text="Delete Service",
    image=delete_icon,
    command=lambda: show_page(delete_page),
    compound="left",
    anchor="w",
    fg_color="#122759",
    text_color="#fff",
    height=40,
)
delete_btn.pack(pady=5, padx=10, fill="x")

show_page(home_page)

dns = DNS()
dns_servers = dns.get_servers()
dns_server_names = list(dns_servers.keys())
connected = False

# home page
combobox_label = ctk.CTkLabel(
    home_page, text="Choose your service :", text_color="#78acd6"
)
combobox_label.place(relx=0.5, rely=0.08, anchor="center")
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
combobox.place(relx=0.5, rely=0.16, anchor="center")

info_frame = ctk.CTkFrame(home_page, fg_color="#122759", width=700, height=120)
info_frame.place(rely=0.4)

primary_dns_label = ctk.CTkLabel(
    info_frame,
    text="   Primary DNS : ",
    font=("Arial", 14),
    compound="left",
    image=num_1_icon,
)
primary_dns_label.place(relx=0.03, rely=0.1)

secondary_dns_label = ctk.CTkLabel(
    info_frame,
    text="   Secondary DNS : ",
    font=("Arial", 14),
    compound="left",
    image=num_2_icon,
)
secondary_dns_label.place(relx=0.03, rely=0.6)

dns_connected_name_label = ctk.CTkLabel(
    info_frame,
    text="   DNS Name : ",
    font=("Arial", 14),
    compound="left",
    image=info_icon,
)
dns_connected_name_label.place(relx=0.4, rely=0.1)

dns_status_label = ctk.CTkLabel(
    info_frame, text="DNS Status : ", font=("Arial", 14), compound="left"
)
dns_status_label.place(relx=0.398, rely=0.6)

dns_info_labels = {
    "Primary DNS": primary_dns_label,
    "Secondary DNS": secondary_dns_label,
    "DNS Status": dns_status_label,
    "DNS Name": dns_connected_name_label,
}


def show_dns_info(active_dns, dns_servers=dns_servers):
    for key, value in dns_servers.items():
        if key == active_dns:
            dns_pair = str(value).split(" ")
            primary_dns_label.configure(text=f"  Primary DNS : {dns_pair[0]}")
            secondary_dns_label.configure(text=f"  Secondary DNS : {dns_pair[1]}")
            dns_status_label.configure(
                text="  DNS Status : Connect", image=green_circle_icon
            )

            dns_connected_name_label.configure(text=f"  DNS Name : {key}")


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

        for name, label in dns_info_labels.items():
            if name == "DNS Status":
                label.configure(text=f"  {name} : Disconnect", image=red_circle_icon)
            else:
                label.configure(text=f"  {name} : Disconnect")

        connected = False

    else:
        dns.connect_dns(combobox.get())
        show_dns_info(combobox.get())
        combobox.configure(state="disabled")
        button.configure(image=red_icon)
        delete_btn.configure(state="disabled")
        connected = True


loading_animation_running = False


def update_pings_async():
    global loading_animation_running

    results = []

    for (
        _,
        _,
        ip,
    ) in ping_labels:
        results.append(dns.get_ping(ip))

    for (
        label,
        icon,
        _,
    ), ping in zip(ping_labels, results):
        root.after(
            0,
            lambda lbl=label, icn=icon, p=ping: lbl.configure(text=f" {p} ", image=icn),
        )

    loading_animation_running = False


def update_pings():
    global loading_animation_running
    loading_animation_running = True
    animate_loading()
    threading.Thread(target=update_pings_async, daemon=True).start()


def animate_loading(count=0):
    global loading_animation_running

    if not loading_animation_running:
        return

    dots = "." * (count % 4)
    text = f" Loading{dots}"

    for (
        label,
        icon,
        _,
    ) in ping_labels:
        label.configure(text=text, image=icon)

    root.after(300, animate_loading, count + 1)


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
    data = {}
    dns_service = None
    for key, value in dns_list:
        if current_dns == str(value).split(" ")[0]:
            dns_service = key
            dns_pair = str(value).split(" ")
            data = {
                "Primary DNS": f"  Primary DNS : {dns_pair[0]}",
                "Secondary DNS": f"  Secondary DNS : {dns_pair[1]}",
                "DNS Status": "  DNS Status : Connect",
                "DNS Name": f"  DNS Name : {key}",
            }
            break

    for key, value in data.items():
        if key == "DNS Status":
            dns_info_labels[key].configure(text=f" {value}", image=green_circle_icon)
        else:
            dns_info_labels[key].configure(text=f" {value}")

    combobox.set(dns_service)
    delete_btn.configure(state="disabled")

else:
    for name, label in dns_info_labels.items():
        if name == "DNS Status":
            label.configure(text=f"  {name} : Disconnect", image=red_circle_icon)
        else:
            label.configure(text=f"  {name} : Disconnect")

button.place(relx=0.5, rely=0.3, anchor="center")

ping_header = ctk.CTkLabel(home_page, text="Live Pings :", font=("Arial", 16))
ping_header.place(relx=0.04, rely=0.7, anchor="w")
ping_refresh_btn = ctk.CTkButton(
    home_page,
    text="",
    image=refresh_icon,
    width=16,
    height=16,
    command=update_pings,
    fg_color="transparent",
)
ping_refresh_btn.place(relx=0.8, rely=0.7, anchor="w")

ping_targets_info = [
    ("EU", eu_icon, "4.2.2.4", 0.1, 0.8),
    ("US", us_icon, "204.106.240.53", 0.3, 0.8),
    ("Asia", sg_icon, "203.126.118.38", 0.5, 0.8),
    ("IR", ir_icon, "85.15.1.14", 0.7, 0.8),
    ("CA", ca_icon, "99.240.73.140", 0.1, 0.9),
    ("FR", fr_icon, "87.231.109.145", 0.3, 0.9),
    ("TR", tr_icon, "212.154.19.244", 0.5, 0.9),
    ("UAE", uae_icon, "94.206.42.74", 0.7, 0.9),
]

ping_labels = []
for name, icon, ip, relx, rely in ping_targets_info:
    label = ctk.CTkLabel(home_page, text="", font=("Arial", 16), compound="left")
    label.place(relx=relx, rely=rely, anchor="w")
    ping_labels.append((label, icon, ip))

# add page
entry_widgets = {}


def save_dns() -> None:
    global combobox

    service_name = entry_widgets["service_entry"].get()
    primary_dns = entry_widgets["primary_entry"].get()
    secondary_dns = entry_widgets["secondary_entry"].get()
    new_service = {f"{service_name}": "{} {}".format(primary_dns, secondary_dns)}
    message, state = dns.add_dns(new_service)
    if not state:
        add_page_state_label.configure(text=message, text_color="red")
    else:
        add_page_state_label.configure(text=message, text_color="green")

        for entry in entry_widgets.values():
            entry.delete(0, "end")

        combobox.configure(values=dns.get_servers())


add_fields = [
    ("Service Name:", "service_entry"),
    ("Primary DNS:", "primary_entry"),
    ("Secondary DNS:", "secondary_entry"),
]

for label_text, var_name in add_fields:
    label = ctk.CTkLabel(add_page, text=label_text)
    label.pack(pady=5)

    entry = ctk.CTkEntry(add_page, width=200)
    entry.pack(pady=5)

    entry_widgets[var_name] = entry

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
        delete_page,
        text="",
        fg_color="transparent",
        hover_color="#ed6d6d",
        image=remove_icon,
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
        y = 0.1 + index * 0.09
        create_delete_widgets(item, y)


delete_page_state_label = ctk.CTkLabel(delete_page, text="", text_color="red")
delete_page_state_label.pack(pady=2)

version_lebel = ctk.CTkLabel(sidebar, text="Version 1.0.4")
version_lebel.place(relx=0.5, rely=1, anchor="s")

root.mainloop()
