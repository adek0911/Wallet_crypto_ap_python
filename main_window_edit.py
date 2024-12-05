import requests
import tkinter.messagebox as msgbox
from tkinter.simpledialog import askstring
from Classes import TopFrame
from ttkbootstrap import Treeview, Frame
from details_wallet import button_clear_entrys
from New_account import add_value_to_treeview


# TEST
def refresh_aplication(
    func,
):
    def wrapper(*args, **kwargs):

        func(*args, **kwargs)

    return wrapper


def edit_wallet_window_ingredients(
    root_sc_width: float,
    root_sc_height: float,
    wallet_name: str,
    wallet_values: list,
    session_user: dict,
    json_values: dict,
) -> None:
    """Create window with possibilities of change name of wallet or values in it"""

    edit_window = TopFrame()
    edit_window.frame.title("Edit Wallet")
    edit_window.frame.grab_set()

    edit_window.text_display(
        "Możesz zmienić nazwę oraz wartości w portfelu", row=0, column=0, columnspan=5
    )
    edit_window.text_display(
        "Nazwa portfela:", row=1, column=1, columnspan=2, sticky="E"
    )
    edit_window.entry_display(row=1, column=3, columnspan=2, sticky="W")
    edit_window.objList[2].insert(0, wallet_name)

    headings_list_wallet = ["Nazwa waluty", "Cena zakupu zł", "Cena zakupu $", "Ilość"]
    edit_window.treeview_display(
        columns=tuple(headings_list_wallet),
        headings_text=headings_list_wallet,
        row=2,
        column=0,
        columnspan=5,
    )
    edit_window.frame.style.configure("Treeview.Heading", font=("Helvetica", 11))
    edit_window.add_data_in_treeview(edit_window.objList[3], wallet_values)

    edit_window.combobox_display(
        values=json_values.file_dict["variable_json"]["available_charts_data"],
        width=5,
        name="edit_wallet_list",
        row=3,
        rowspan=2,
        column=0,
    )
    edit_window.text_display("Nazwa waluty", row=3, column=1)
    edit_window.entry_display(row=4, column=1)  # 5
    edit_window.text_display("Cena zakupu zł", row=3, column=2)
    edit_window.entry_display(row=4, column=2)  # 7
    edit_window.text_display("Cena zakupu $", row=3, column=3)
    edit_window.entry_display(row=4, column=3)  # 9
    edit_window.text_display("Ilość", row=3, column=4)
    edit_window.entry_display(row=4, column=4)  # 11

    edit_window.text_display("Opcje modyfikacji konta:", row=5, column=0)
    edit_window.button_display(
        "Dodaj",
        row=5,
        column=1,
        pady=5,
        columnspan=2,
        command=lambda: add_value_to_treeview(
            treeview_obj=edit_window.objList[3],
            list_entrys=[edit_window.objList[i] for i in range(5, 12, 2)],
            currency_names=json_values.file_dict["variable_json"][
                "available_charts_data"
            ],
            dollar_price=session_user["dollar_price"],
        ),
    )
    edit_window.button_display(
        "Usuń",
        row=5,
        column=3,
        columnspan=2,
        command=lambda: edit_window.objList[3].delete(
            edit_window.objList[3].selection()
        ),
    )

    # DONT WORK YET
    edit_window.combobox_display(
        ["Wybierz", "Usuń konto", "Zmień hasło", "Zmień nazwę konta"],
        width=15,
        row=6,
        column=0,
        name="Edit_account",
    )

    edit_window.dict_combo["Edit_account"].bind(
        "<<ComboboxSelected>>",
        lambda _: change_account_data(
            changed=edit_window.dict_combo["Edit_account"].get(),
            url=json_values.file_dict["variable_json"]["URL_Credentials"],
            session_user=session_user,
            window=edit_window.frame,
        ),
    )

    # WORK BUT NEED REFRESH on main window
    edit_window.button_display(
        "Usuń porftel",
        width=10,
        row=6,
        column=1,
        padx=5,
        command=lambda: delete_wallet(
            new_wallet_name=edit_window.objList[2].get(),
            session_user=session_user,
            url=json_values.file_dict["variable_json"]["URL_Credentials"],
            window=edit_window.frame,
        ),
    )
    edit_window.objList[15].configure(style="Invest.TButton")
    edit_window.button_display(
        "Anuluj", row=6, column=2, command=edit_window.frame.destroy
    )
    edit_window.button_display(
        "Zamień",
        row=6,
        column=3,
        command=lambda: apply_changes(
            new_wallet_name=edit_window.objList[2].get(),
            new_wallet_values=[
                edit_window.objList[3].item(values)["values"]
                for values in edit_window.objList[3].get_children()
            ],
        ),
        padx=5,
        pady=10,
    )
    edit_window.button_display(
        "Stwórz",
        row=6,
        column=4,
        padx=5,
        command=lambda: create_wallet(
            new_wallet_name=edit_window.objList[2].get(),
            wallet_values=[
                edit_window.objList[3].item(values)["values"]
                for values in edit_window.objList[3].get_children()
            ],
            session_user=session_user,
            url=json_values.file_dict["variable_json"]["URL_Credentials"],
            window=edit_window.frame,
        ),
    )
    edit_window.frame.update_idletasks()
    # set popup on screen center
    x = (root_sc_width // 2) - (edit_window.frame.winfo_width() // 2)
    y = (root_sc_height // 2) - (edit_window.frame.winfo_height() // 2)
    edit_window.frame.geometry(f"+{x}+{y}")


def apply_changes(new_wallet_name: str, new_wallet_values: list) -> None:
    """Apply changes in to database"""

    # Take new wallet name

    if len(new_wallet_name) < 1:
        return msgbox.showinfo("Warning", "Nowa nazwa jest za krótka")


# TODO Create delete account
def delete_account(session_user: dict) -> None:
    """Deleted account from aplication"""

    """First wallets values then wallets and at the end delete account"""
    pass


def delete_wallet(
    new_wallet_name: str, session_user: dict, url: str, window: Frame
) -> None:
    """Delete edited wallet from database"""

    if not new_wallet_name in session_user["wallet_names"]:
        msgbox.showwarning(
            "Brak portfela w bazie", "Nie ma portfela o tej nazwie w baze"
        )
        return 0

    headers = {"Authorization": session_user["account_token"]}
    # Get all wallet for this account
    get_id_of_wallet: dict = requests.get(
        url + f"wallets/{session_user['Account_ID']}", headers=headers
    ).json()

    print(session_user["wallet_names"])
    # Search id for wallet in responce
    wallet_id: int = [
        val["Id"] for val in get_id_of_wallet if val["Name"] == new_wallet_name
    ][0]

    # Delete values for this wallet
    delete_detail_wallet = requests.delete(
        f"{url}wallet_detail/{wallet_id}", headers=headers
    )

    # Delete wallet name from database
    delete_wallet_name = requests.delete(
        f"{url}wallets/{session_user['Account_ID']}",
        json={"wallet_name": new_wallet_name},
        headers=headers,
    )
    window.destroy()
    msgbox.showinfo(
        "Status Usunięcia",
        f"Status usunięcia szczegółów {delete_detail_wallet.status_code}\n Status usunięcia portfela {delete_wallet_name.status_code}",
    )


# TODO Create refresh method of list in top area and wallet values in middle area
def create_wallet(
    new_wallet_name: str,
    wallet_values: list,
    session_user: dict,
    url: str,
    window: Frame,
) -> None:
    """Create new wallet on this account"""
    if new_wallet_name in session_user["wallet_names"]:
        msgbox.showwarning(
            "Warning", "Niestety istnieje już porftel o tej nazwie dla tego użytkownika"
        )
        return 0

    # Add wallet name to database
    data_to_send = {"wallet_name": new_wallet_name}
    headers = {"Authorization": session_user["account_token"]}
    add_wallet = requests.post(
        f"{url}wallets/{session_user['Account_ID']}", json=data_to_send, headers=headers
    )
    if add_wallet.status_code != 201:
        msgbox.showerror("ERROR", "Niestety coś poszło nie tak")
        return 0

    # Add wallet values to database
    new_wallet_id: int = add_wallet.json()["wallet_id"]

    data_to_send = {"wallet_values": wallet_values}
    add_value_wallet = requests.post(
        f"{url}wallet_detail/{new_wallet_id}", json=data_to_send, headers=headers
    )
    window.destroy()
    status: str = add_value_wallet.json()["Status"]
    msgbox.showinfo("Sukces", message=status)


def change_account_data(changed: str) -> None:
    """Set new password or account name"""

    # TODO this func need window to distroy if delete acount, if change password and account log out, need urls so json_file

    if changed == "Usuń konto":
        if msgbox.askokcancel("Warning", "Czy na pewno chcesz usunąć konto?"):
            print("poszło")

    if changed == "Zmień hasło":
        new_password = askstring("Nowe hasło", "Podaj nowe hasło")
        if msgbox.askokcancel(
            "Warning", f"Czy chcesz potwierdzić zmianę hasła na {new_password}?"
        ):
            print("poszło")

    if changed == "Zmień nazwę konta":
        new_account = askstring("Nowa nazwa", "Podaj nową nazwę konta")
        if msgbox.askokcancel(
            "Warning", f"Czy chcesz potwierdzić zmianę nazwy konta na {new_account}?"
        ):
            print("poszło")
