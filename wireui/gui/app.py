from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
from wireui.library.typedefs.exceptions import DataIntegrityError

from .strings import strings

from ..library import convert_list_to_str
from ..library import convert_str_to_list
from ..library import Site
from ..library import SiteDoesNotExistError
from ..library import WireUI


class App(Frame):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.row = 0

    #########
    # Select a site
    #########
    label = Label(self, text=strings["sites"]["select_site"] + ": ")
    label.grid(row=self.row, column=0, sticky=E)

    sites = WireUI.get_instance().get_sites()
    # sites.append(strings["sites"]["create_new_site"])  # TODO: uncomment

    self.__selected_site = StringVar()

    combo = ttk.Combobox(self,
                         values=sites,
                         state="readonly",
                         textvariable=self.__selected_site,
                         width=28)
    combo.set(strings["sites"]["select_site_cb"])
    combo.grid(row=self.row, column=1)
    combo.bind("<<ComboboxSelected>>", self.__site_selected)

    self.row += 1

    self.pack(side=TOP, anchor=NW, fill="both", expand=True)

  def __site_selected(self, event):
    if App.__site_selected.first_run:
      App.__site_selected.first_run = False
      self.__site_selected_extend()
    self.__site_selected_cleanup()
    if self.__selected_site.get() == strings["sites"]["create_new_site"]:
      self.__site_selected_new()
    else:
      self.__site_selected_refresh_existing()

  def __site_selected_extend(self):
    site = self.__selected_site.get()

    #########
    # Site functions (create_wg_config, save, delete)
    #########
    self.buttonFrame = Frame(self)
    self.buttonFrame.grid(row=self.row, columnspan=2)
    self.create_wg_config_b = Button(self.buttonFrame,
                                     text=strings["sites"]["create_wg_config"],
                                     command=exit)
    self.create_wg_config_b.grid(row=0, column=0)
    self.save_site_b = Button(self.buttonFrame,
                              text=strings["sites"]["save_site"],
                              command=self.__save_site)
    self.save_site_b.grid(row=0, column=1)
    self.delete_site_b = Button(self.buttonFrame,
                                text=strings["sites"]["delete_site"],
                                command=exit)
    self.delete_site_b.grid(row=0, column=2)

    self.row += 1

    #########
    # Site name
    #########
    self.site_name_l = Label(self, text=strings["sites"]["site_name"] + ": ")
    self.site_name_l.grid(row=self.row, column=0, sticky="e")
    self.site_name_e = Entry(self, width=30)
    self.site_name_e.grid(row=self.row, column=1)

    self.row += 1

    #########
    # IP networks
    #########
    self.ip_networks_l = Label(self,
                               text=strings["sites"]["ip_networks"] + ": ")
    self.ip_networks_l.grid(row=self.row, column=0, sticky="e")
    self.ip_networks_e = Entry(self, width=30)
    self.ip_networks_e.grid(row=self.row, column=1)

    self.row += 1

    #########
    # DNS
    #########
    self.dns_l = Label(self, text=strings["sites"]["dns"] + ": ")
    self.dns_l.grid(row=self.row, column=0, sticky="e")
    self.dns_e = Entry(self, width=30)
    self.dns_e.grid(row=self.row, column=1)

    self.row += 1

    #########
    # Peers
    #########
    try:
      peers = WireUI.get_instance().get_peer_names(site)
    except SiteDoesNotExistError:
      peers = []
    peers.append(strings["sites"]["create_new_peer"])
    self.__selected_peer = StringVar()

    self.peers_l = Label(self, text=strings["sites"]["select_peer"] + ": ")
    self.peers_l.grid(row=self.row, column=0, sticky="e")
    self.peers_e = ttk.Combobox(self,
                                values=peers,
                                state="readonly",
                                textvariable=self.__selected_peer,
                                width=28)
    self.peers_e.set(strings["sites"]["select_peer_cb"])
    self.peers_e.grid(row=self.row, column=1)
    self.peers_b = Button(self,
                          text=strings["sites"]["edit_peer"],
                          command=exit)
    self.peers_b.grid(row=self.row, column=2)

    self.row += 1

  def __site_selected_refresh_existing(self):
    site = WireUI.get_instance().get_site(self.__selected_site.get())

    self.site_name_e.insert(0, site.name)
    self.ip_networks_e.insert(0, convert_list_to_str(site.ip_networks))
    self.dns_e.insert(0, convert_list_to_str(site.dns))

  __site_selected.first_run = True

  def __site_selected_new(self):
    # Set and ensure correct button states
    self.create_wg_config_b["command"] = self.__create_wg_config_save_first
    self.delete_site_b["state"] = DISABLED

  def __save_site(self):
    # TODO: new site
    # TODO: integrate peers
    site_old = WireUI.get_instance().get_site(
      self.__selected_site.get())  # TODO: Remove when peers are integrated

    name = self.site_name_e.get()

    dns = convert_str_to_list(self.dns_e.get())
    ip_networks = convert_str_to_list(self.ip_networks_e.get())

    try:
      WireUI.get_instance().set_site(
        Site(
          name=name,
          ip_networks=ip_networks,
          dns=dns,
          peers=site_old.peers,
        ))
    except DataIntegrityError as e:
      showerror(title="Cannot save", message=str(e))

  def __site_selected_cleanup(self):
    # Reset entry fields
    self.site_name_e.delete(0, len(self.site_name_e.get()))
    self.ip_networks_e.delete(0, len(self.ip_networks_e.get()))
    self.dns_e.delete(0, len(self.dns_e.get()))

    # Set and ensure correct button states
    self.create_wg_config_b["command"] = exit
    self.delete_site_b["state"] = NORMAL
    self.peers_b["state"] = DISABLED  # TODO: remove if integrated
    self.delete_site_b["state"] = DISABLED  # TODO: remove if integrated
    self.create_wg_config_b["state"] = DISABLED  # TODO: remove if integrated

  def __create_wg_config_save_first(self):
    showerror(
      title=strings["sites"]["create_wg_config_save_first_error_title"],
      message=strings["sites"]["create_wg_config_save_first_error"])
