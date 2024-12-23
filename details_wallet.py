import tkinter.messagebox as msgbox
from datetime import datetime
from Classes import AreaFrame, TopFrame
import ttkbootstrap as ttk
import requests
import tkinter.messagebox as msgbox
from convert_prices import convert_price


class ZeroDataFromDB(Exception):
    pass


def button_change_state(button: ttk.Button, window: ttk.Toplevel):
    button.configure(state="normal")
    window.destroy()


def create_widgets(
    frame: AreaFrame, data: list, changed_rows: list[dict], dollar_price: float
):

    frame.text_display(text="Data", row=0, column=0, columnspan=2)
    frame.text_display(text="Nazwa", row=0, column=2, columnspan=2)
    frame.text_display(text="Sprzedaż/Kupno", row=0, column=4, columnspan=2)

    """Data_filtr"""
    frame.combobox_display(
        values=update_filtr("Data_filtr", data),
        width=10,
        row=1,
        column=0,
        columnspan=2,
        name="Data_filtr",
    )
    """Name_filtr"""
    frame.combobox_display(
        values=update_filtr("Name_filtr", data),
        width=10,
        row=1,
        column=2,
        columnspan=2,
        name="Name_filtr",
    )
    """Status_filtr"""
    frame.combobox_display(
        values=update_filtr("Status_filtr", data),
        width=10,
        row=1,
        column=4,
        columnspan=2,
        name="Status_filtr",
    )

    tree_view_headers = [
        "Data",
        "Nazwa",
        "Sprzedaż/ Kupno",
        "Cena zł",
        "Cena $",
        "Ilość",
    ]
    frame.treeview_display(
        columns=tuple(tree_view_headers),
        headings_text=tree_view_headers,
        row=2,
        column=0,
        columnspan=6,
    )
    for i in range(6):  # obj_4-8
        if i != 2:
            frame.entry_display(row=3, column=i)
        else:
            """on index 2 is combobox"""
            frame.combobox_display(
                values=("BUY", "SALE"),
                row=3,
                column=i,
                width=10,
                name="combo_status_transaction",
            )

    button_names = (
        "Wyczyść",
        "Wybierz",
        "Zamień",
        "Dodaj",
        "Usuń",
        "Aktualizuj",
    )
    """Button Clear"""
    frame.button_display(
        text=button_names[0],
        row=4,
        column=0,
        command=lambda: button_clear_entrys(entres=frame.objList[4:9]),
    )

    """Button Select"""
    frame.button_display(
        text=button_names[1],
        row=4,
        column=1,
        command=lambda: button_selected(
            entres=frame.objList[4:9],
            combo_entry=frame.dict_combo["combo_status_transaction"],
            treeview=frame.objList[3],
        ),
    )
    """Button Change"""
    frame.button_display(
        text=button_names[2],
        row=4,
        column=2,
        command=lambda: button_change(
            entres=frame.objList[4:9],
            combo_entry=frame.dict_combo["combo_status_transaction"],
            treeview=frame.objList[3],
            changed_values=changed_rows,
        ),
    )
    """Button Add"""
    frame.button_display(
        text=button_names[3],
        row=4,
        column=3,
        command=lambda: button_add(
            entres=frame.objList[4:9],
            combo_entry=frame.dict_combo["combo_status_transaction"],
            treeview=frame.objList[3],
            changed_values=changed_rows,
            dollar_price=dollar_price,
        ),
    )
    """Button Delete"""
    frame.button_display(
        text=button_names[4],
        row=4,
        column=4,
        command=lambda: button_delete(
            treeview=frame.objList[3],
            frame=frame.frame,
            changed_values=changed_rows,
        ),
    )
    """Button Update wallet"""
    frame.button_display(
        text=button_names[5],
        row=4,
        column=5,
    )

    unit_price_column = ["Nazwa", "Cena jedn. zł", "Cena jedn. $", "Ilość"]
    frame.treeview_display(
        columns=tuple(unit_price_column),
        headings_text=unit_price_column,
        row=5,
        column=0,
        columnspan=6,
    )


def update_filtr(filtr_name: str, data_list: list):
    result = []
    for val in data_list:
        if filtr_name == "Data_filtr":
            result.append(val[0][6:])
        if filtr_name == "Name_filtr":
            result.append(val[1])
        if filtr_name == "Status_filtr":
            result.append(val[2])
    result = list(set(result))
    result.sort()
    result.insert(0, "Wszystko")
    return result


def cal_unit_prices(history_trans_data: list, new_wallet_count: bool = False) -> list:
    # TODO If value is empty one of price, convert the second one to price
    status = ("BUY", "SALE")
    result = []
    # list of all crypto
    unique_names = []
    for val in history_trans_data:
        if val[1] not in unique_names:
            unique_names.append(val[1])
            result.append([val[1], 0, 0, 0])

        if val[2] == status[0]:
            index = unique_names.index(val[1])
            for i in range(1, 4):
                result[index][i] = round(float(result[index][i]) + float(val[i + 2]), 6)

        if val[2] == status[1]:
            index = unique_names.index(val[1])
            for i in range(1, 4):
                result[index][i] = round(float(result[index][i]) - float(val[i + 2]), 6)
            # TRY IF DONT WANT REFRESH AFTER SALE TO 0
            # if round(result[index][3], 3) == 0:
            #     result[index][1], result[index][2], result[index][3] = 0, 0, 0

    if new_wallet_count != True:
        remove_list = []
        for i in result:
            i[3] = i[3].__round__(4)
            if i[3] != 0:
                i[1] = round(i[1] / i[3], 4)
                i[2] = round(i[2] / i[3], 4)
                i[3] = round(i[3], 4)
            else:
                remove_list.append(i[0])

        result = [val for val in result if val[0] not in remove_list]
        return result
    else:
        for i in result:
            if round(i[3], 4) == 0 and i[1] != 0:
                i[3] = 0
            if i[1] == 0 and i[2] == 0:
                result.pop(result.index(i))
        return result


def treeview_values(treeview_obj: ttk.Treeview) -> list[str]:
    return [
        treeview_obj.item(values)["values"] for values in treeview_obj.get_children()
    ]


def sort_treeview(
    combobox_obj_dict: dict[ttk.Combobox],
    treeview_obj: ttk.Treeview,
    db_data: list,
    frame: AreaFrame,
) -> None:

    data: str = combobox_obj_dict["Data_filtr"].get()
    name: str = combobox_obj_dict["Name_filtr"].get()
    status: str = combobox_obj_dict["Status_filtr"].get()

    frame.add_data_in_treeview(treeview_obj, db_data)

    if data != combobox_obj_dict["Data_filtr"]["values"][0]:
        result = [val for val in treeview_values(treeview_obj) if val[0][6:] == data]
        frame.add_data_in_treeview(treeview_obj, result)

    if name != combobox_obj_dict["Name_filtr"]["values"][0]:
        result = [val for val in treeview_values(treeview_obj) if val[1] == name]
        frame.add_data_in_treeview(treeview_obj, result)

    if status != combobox_obj_dict["Status_filtr"]["values"][0]:
        result = [val for val in treeview_values(treeview_obj) if val[2] == status]
        frame.add_data_in_treeview(treeview_obj, result)


def prep_data_from_db(url: str, session_user: dict):

    responce = requests.get(
        f"{url}trans_curr/{session_user['selected_wallet_id']}",
        headers={"Authorization": session_user["account_token"]},
    )
    data_db = responce.json()
    result = []
    for val in data_db:
        temp = []
        temp.append(
            datetime.strptime(val["date_purchase"], "%Y-%m-%d").strftime("%d.%m.%Y")
        )
        temp.append(val["name_currency"])

        replace_taple = ("}", "{", "'")
        for i in replace_taple:
            val["status_of_purchase"] = val["status_of_purchase"].replace(i, "")

        temp.append(val["status_of_purchase"])
        temp.append(f"{val['price_PLN']}")
        temp.append(f"{val['price_dollar']}")
        temp.append(f"{val['quantity']}")
        temp.append({"Id": val["Id"]})
        result.append(temp)

    return result


def save_in_file(path: str, detail_wallet: list):
    """TEMP"""
    prep_data = []
    for i, val in enumerate(detail_wallet):
        if i == len(detail_wallet) - 1:
            prep_data.append(",".join(val))
        else:
            prep_data.append(",".join(val) + "\n")
    with open(path, "w", encoding="UTF-8") as file:
        file.writelines(prep_data)


def update_window(
    button_status: ttk.Button,
    changed_rows: list,
    root_x_y: list,
    treeview: ttk.Treeview,
    session_user: dict,
    url: str,
):

    button_status.configure(state="disable")
    update_window = TopFrame()
    upgrade_area = AreaFrame(onFrame=update_window.frame)
    row_number = len(changed_rows)

    upgrade_area.text_display(
        text=f"Znaleziono {row_number} zmian(y)", row=0, column=0, columnspan=2
    )

    added, changed, deleted = 0, 0, 0
    for val in changed_rows:
        if tuple(val.keys())[0] == "CHANGED":
            changed += 1
        if tuple(val.keys())[0] == "ADD":
            added += 1
        if tuple(val.keys())[0] == "DELETED":
            deleted += 1

    upgrade_area.text_display(text=f"Dodano: {added}", row=1, column=0, columnspan=2)

    upgrade_area.text_display(
        text=f"Usunięto: {changed}", row=2, column=0, columnspan=2
    )

    upgrade_area.text_display(
        text=f"Zmieniono: {deleted}", row=3, column=0, columnspan=2
    )

    upgrade_area.button_display(
        text="Potwierdź", command=lambda: submit(), row=4, column=0, padx=10, pady=10
    )

    upgrade_area.button_display(
        text="Anuluj", command=lambda: cancel(), row=4, column=1, padx=10
    )

    update_window.frame.update_idletasks()
    x = (root_x_y[0] // 2) - (upgrade_area.frame.winfo_width() // 2)
    y = (root_x_y[1] // 2) - (upgrade_area.frame.winfo_height() // 2)
    update_window.frame.geometry(f"+{x}+{y}")

    def submit():
        upgrade_area.frame.focus()
        button_status.configure(state="active")

        upgrade_area.objList[1].destroy()
        upgrade_area.objList[2].destroy()
        upgrade_area.objList[3].destroy()

        upgrade_area.statusbar_display(
            row=1, column=0, columnspan=2, maximum=row_number
        )

        # Zrobić całą opcję logiki dodawania zmian do bazy

        if msgbox.showinfo("Informacja", "Udało się przesłać dane do bazy"):
            update_window.frame.destroy()

    def cancel():
        button_status.configure(state="active")
        update_window.frame.destroy()


# region buttons methods
def button_update_wallet(
    changed_data: list,
    db_data: list,
    url: str,
    frame: ttk.Frame,
    # selected_wallet_id: int,
    session_user: dict,
    treeview: ttk.Treeview,
    header: str,
):

    def add_db(val: list, directory: str):
        wallet_id = "1"
        if directory == "trans_curr":
            prep_data = {
                "date_purchase": datetime.strptime(val[0], "%d.%m.%Y").strftime(
                    "%Y-%m-%d"
                ),
                "name_currency": val[1],
                "status_of_purchase": val[2],
                "price_PLN": val[3],
                "price_dollar": val[4],
                "quantity": val[5],
            }
            # responce = requests.put(
            #     f"{url}{directory}/{wallet_id}", json=prep_data, headers=headers
            # )

        if directory == "wallet_detail":
            prep_data = {
                "Name": val[0],
                "Price_PLN": val[1],
                "Price_USD": val[2],
                "Quantity": val[3],
            }
            # responce = requests.put(
            #     f"{url}{directory}/{wallet_id}", json=prep_data, headers=headers
            # )

    def update_db(val: list, id: int, directory: str):
        if directory == "trans_curr":
            prep_data = {
                "date_purchase": datetime.strptime(val[0], "%d.%m.%Y").strftime(
                    "%Y-%m-%d"
                ),
                "name_currency": val[1],
                "status_of_purchase": val[2],
                "price_PLN": val[3],
                "price_dollar": val[4],
                "quantity": val[5],
            }
            # responce = requests.patch(
            #     f"{url}{directory}/{id}", json=prep_data, headers=headers
            # )
            print("update")
        if directory == "wallet_detail":
            prep_data = {
                "Name": val[0],
                "Price_PLN": val[1],
                "Price_USD": val[2],
                "Quantity": val[3],
            }
            # responce = requests.patch(
            #     f"{url}{directory}/{id}", json=prep_data, headers=headers
            # )
            print("update")

    def delete_db(id: int):
        # responce = requests.delete(f"{url}trans_curr/{id}", headers=headers)
        print("delete")

    def wallet_values() -> list[str]:
        # TODO static value
        wallet_id = "1"
        responce = requests.get(f"{url}/wallet_detail/{wallet_id}", headers=headers)
        # print(responce.json())
        if responce.status_code == 200:
            result = [
                [val["Name"], val["Price_PLN"], val["Price_USD"], val["Quantity"]]
                for val in responce.json()
            ]
            return result
        # ERROR 500

        raise ConnectionError

    if msgbox.askokcancel("Warning", "Czy na pewno chcesz przesłać zmiany do bazy?"):
        frame.focus()
        headers = {"Authorization": header}
        if len(changed_data) > 0:
            status = False
            for val in changed_data:

                """ADD"""
                if val["old"] == "":
                    add_db(val["new"], directory="trans_curr")
                    status = True

                """DELETE"""
                if val["new"] == "":
                    id = [value[6] for value in db_data if value[:6] == val["old"]]
                    delete_db(id=id[0]["Id"])

            """If update new added row"""
            if status:
                db_data = prep_data_from_db(url, session_user)

            for val in changed_data:

                """Update"""
                if val["old"] != "" and val["new"] != "":
                    id = [value[6] for value in db_data if value[:6] == val["old"]]
                    print(id)
                    update_db(val["new"], id=id[0]["Id"], directory="trans_curr")
        changed_data = []

        """Recount wallet"""
        new_wallet_data = cal_unit_prices(
            history_trans_data=treeview_values(treeview_obj=treeview),
            new_wallet_count=True,
        )
        old_wallet_data = wallet_values()

        changed_wallet_data = [
            val for val in new_wallet_data if val not in old_wallet_data
        ]

        """Apply change in db wallet details"""
        # create dict with id and name currency
        wallet_id = "1"
        responce = requests.get(
            f"{url}wallet_detail/{wallet_id}", headers=headers
        ).json()
        currency_id: dict = {val["Name"]: val["Id"] for val in responce}
        for val in changed_wallet_data:
            """New line"""
            if val[0] not in [val[0] for val in old_wallet_data]:
                """Req to db for add new value"""
                add_db(val=val, directory="wallet_detail")
            else:
                """Req to db for update value"""
                update_db(val=val, id=currency_id[val[0]], directory="wallet_detail")
                pass
            """changed line"""
    frame.focus()


def button_clear_entrys(entres: list[ttk.Entry]):
    for i in entres:
        i.delete(0, "end")


def button_change(
    entres: list[ttk.Entry],
    combo_entry: ttk.Combobox,
    treeview: ttk.Treeview,
    changed_values: list,
):
    change_data = [val.get() for val in entres if val.get() != ""]
    if len(change_data) < 5:
        msgbox.showinfo("Brak danych", "Nie zostały wprowadzone wszystkie informacje")
    else:
        change_data.insert(2, combo_entry.get())
        changed_values.append(
            {"CHANGED": (treeview.item(treeview.selection())["values"], change_data)}
        )
        treeview.item(treeview.selection(), values=change_data)
        """Clear entry"""
        button_clear_entrys(entres)


def button_add(
    entres: list[ttk.Entry],
    combo_entry: ttk.Combobox,
    treeview: ttk.Treeview,
    changed_values: list[dict],
    dollar_price: float,
):
    add_data = [val.get() for val in entres]
    add_data.insert(2, combo_entry.get())

    exeptions = ("0", 0, "")
    if (
        any(char.isalpha() for char in add_data[3])
        or any(char.isalpha() for char in add_data[4])
        or any(char.isalpha() for char in add_data[5])
        or add_data[5] in exeptions
    ):
        msgbox.showerror(
            "Błędne dane", "Podane dane są błędne popraw wartości i ponów próbę"
        )
        return

    if add_data[3] in exeptions:  # PLN price
        add_data[3] = str(convert_price(add_data[3], add_data[4], dollar_price)["PLN"])
    if add_data[4] in exeptions:  # USD price
        add_data[4] = str(convert_price(add_data[3], add_data[4], dollar_price)["USD"])

    changed_values.append({"ADD": add_data})
    treeview.insert("", "end", values=add_data)

    """Clear entry"""
    button_clear_entrys(entres)


def button_delete(treeview: ttk.Treeview, frame: ttk.Frame, changed_values: list[dict]):
    if msgbox.askokcancel("Warning", "Czy na pewno chcesz usunąć zaznaczony wiersz?"):
        frame.focus()
        changed_values.append(
            {"DELETED": treeview.item(treeview.selection())["values"]}
        )
        treeview.delete(treeview.selection())
    frame.focus()


def button_selected(
    entres: list[ttk.Entry], combo_entry: ttk.Combobox, treeview: ttk.Treeview
):
    button_clear_entrys(entres)
    selected: list = treeview.item(treeview.selection())["values"]
    status = selected.pop(2)

    """insert data to entry"""
    for i, val in enumerate(entres):
        val.insert(0, str(selected[i]))
    combo_entry.set(status)


# endregion


def purchers_area_ingredients(
    button_obj: ttk.Button,
    url: str,
    session_user: dict,
    header: str,
    root_x_y: list[float],
) -> None:

    try:
        """Database data"""
        purchase_details_from_db_core = prep_data_from_db(
            url=url, session_user=session_user
        )
        purchase_details_from_db = [val[:6] for val in purchase_details_from_db_core]
    except ConnectionError:
        msgbox.showinfo("Informacja", "Niestety nie udało się połączyć z serwerem.")
    else:
        purchase_details_window = TopFrame()
        button_obj.configure(state="disable")
        purchase_details_window.frame.protocol(
            "WM_DELETE_WINDOW",
            lambda: button_change_state(button_obj, purchase_details_window.frame),
        )
        """Need for 2 row heading in topframe treeview"""
        purchase_details_window.frame.style.configure(
            "Treeview.Heading", font=("Helvetica", 11)
        )

        changed_rows = []

        purchase_details_area = AreaFrame(onFrame=purchase_details_window.frame)
        create_widgets(
            frame=purchase_details_area,
            data=purchase_details_from_db,
            changed_rows=changed_rows,
            dollar_price=session_user["dollar_price"],
        )

        """Filter bind methods"""
        purchase_details_area.dict_combo["Data_filtr"].bind(
            "<<ComboboxSelected>>",
            lambda _: sort_treeview(
                combobox_obj_dict=purchase_details_area.dict_combo,
                treeview_obj=purchase_details_area.objList[3],
                db_data=purchase_details_from_db,
                frame=purchase_details_area,
            ),
        )
        purchase_details_area.dict_combo["Name_filtr"].bind(
            "<<ComboboxSelected>>",
            lambda _: sort_treeview(
                combobox_obj_dict=purchase_details_area.dict_combo,
                treeview_obj=purchase_details_area.objList[3],
                db_data=purchase_details_from_db,
                frame=purchase_details_area,
            ),
        )
        purchase_details_area.dict_combo["Status_filtr"].bind(
            "<<ComboboxSelected>>",
            lambda _: sort_treeview(
                combobox_obj_dict=purchase_details_area.dict_combo,
                treeview_obj=purchase_details_area.objList[3],
                db_data=purchase_details_from_db,
                frame=purchase_details_area,
            ),
        )

        """Button update wallet method"""
        # purchase_details_area.objList[14].configure(
        #     command=lambda: button_update_wallet(
        #         changed_data=changed_rows,
        #         db_data=purchase_details_from_db_core,
        #         url=url,
        #         frame=purchase_details_window.frame,
        #         # selected_wallet_id=session_user["selected_wallet_id"],  #
        #         session_user=session_user,
        #         treeview=purchase_details_area.objList[3],
        #         header=header,
        #     )
        # )
        purchase_details_area.objList[14].configure(
            command=lambda: update_window(
                button_status=purchase_details_area.objList[14],
                changed_rows=changed_rows,
                root_x_y=root_x_y,
            )
        )

        """First add value in treeviews"""
        purchase_details_area.add_data_in_treeview(
            purchase_details_area.objList[3], purchase_details_from_db, "txt", 10
        )

        purchase_details_area.add_data_in_treeview(
            purchase_details_area.objList[15],
            cal_unit_prices(purchase_details_from_db),
        )
        purchase_details_window.frame.update_idletasks()
        x = (root_x_y[0] // 2) - (purchase_details_area.frame.winfo_width() // 2)
        y = (root_x_y[1] // 2) - (purchase_details_area.frame.winfo_height() // 2)
        purchase_details_window.frame.geometry(f"+{x}+{y}")
