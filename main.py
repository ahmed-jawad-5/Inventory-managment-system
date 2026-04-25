import os
import json
import time
from blessed import Terminal

term = Terminal()

# ── persistence ─────────────────────────────────────────────────────────────


def load_inventory():
    if os.path.exists("test4.json"):
        with open("test4.json") as f:
            return json.load(f)
    return {}


def load_employ():
    if os.path.exists("testemploy.json"):
        with open("testemploy.json") as f:
            return json.load(f)
    return {}


def save_inventory(inv):
    with open("test4.json", "w") as f:
        json.dump(inv, f, indent=4)


def save_employ(emp):
    with open("testemploy.json", "w") as f:
        json.dump(emp, f, indent=4)

# ── drawing helpers ──────────────────────────────────────────────────────────


BOX = dict(
    tl="╔", tr="╗", bl="╚", br="╝",
    h="═", v="║",
    ml="╠", mr="╣", mt="╦", mb="╩", cross="╬",
)


def box(x, y, w, h, color=None):
    c = color or term.blue
    lines = []
    lines.append(term.move(y, x) + c +
                 BOX["tl"] + BOX["h"] * (w - 2) + BOX["tr"])
    for row in range(1, h - 1):
        lines.append(term.move(y + row, x) + c +
                     BOX["v"] + " " * (w - 2) + BOX["v"])
    lines.append(term.move(y + h - 1, x) + c +
                 BOX["bl"] + BOX["h"] * (w - 2) + BOX["br"])
    print("".join(lines), end="", flush=True)


def center_text(text, x, y, w, color=None):
    c = color or term.white
    pad = (w - 2 - len(text)) // 2
    print(term.move(y, x + 1) + " " * (w - 2), end="", flush=True)
    print(term.move(y, x + 1 + pad) + c +
          text + term.normal, end="", flush=True)


def write_at(x, y, text, color=None):
    c = color or term.normal
    print(term.move(y, x) + c + text + term.normal, end="", flush=True)


def clear_screen():
    print(term.clear, end="", flush=True)


def status_bar(msg, color=None):
    c = color or term.green
    h = term.height
    print(term.move(h - 2, 0) + term.clear_eol, end="", flush=True)
    print(term.move(h - 2, 2) + c + msg + term.normal, end="", flush=True)


def input_at(prompt_x, prompt_y, label, secret=False, color=None):
    c = color or term.yellow
    write_at(prompt_x, prompt_y, c + label + term.normal)
    inp_x = prompt_x + len(label)
    print(term.move(prompt_y, inp_x), end="", flush=True)
    buf = []
    with term.cbreak():
        while True:
            ch = term.inkey(timeout=None)
            if ch.name == "KEY_ENTER" or ch == "\n":
                break
            elif ch.name == "KEY_BACKSPACE" or ch == "\x7f":
                if buf:
                    buf.pop()
                    print(term.move(prompt_y, inp_x) + " " *
                          (term.width - inp_x - 1), end="", flush=True)
                    print(term.move(prompt_y, inp_x) + ("*" * len(buf)
                          if secret else "".join(buf)), end="", flush=True)
            elif not ch.is_sequence and len(ch) == 1:
                buf.append(ch)
                display_ch = "*" if secret else ch
                print(term.move(prompt_y, inp_x + len(buf) - 1) +
                      display_ch, end="", flush=True)
    return "".join(buf)

# ── splash screen ────────────────────────────────────────────────────────────


ASCII_LOGO = [
    r"  :::   :::   ::.        --:                             .::          ",
    r"  :++. .+++:  =+.        =+-                             -+=          ",
    r"   =+- -+-+= :+- ==-=+=. =+- ==-==+=-==+=  :=--==: -+-==:-++==       ",
    r"   :+= == ==.=+.  ::-=+- =+- =+:  ++-  =+:  .::=+= -+=.  -+=         ",
    r"    =+-+: -+-+= :==:.-+= =+- =+:  =+:  =+:.=+-.:++ -+=   -+=         ",
    r"    :=+=  .=++. :+=:-=== =+- =+:  =+:  =+:.=+-:==+ -+=   :++-:       ",
]


def splash():
    clear_screen()
    w, h = term.width, term.height
    logo_y = h // 2 - 5
    box_w = min(w - 4, 76)
    box_x = (w - box_w) // 2
    box(box_x, logo_y - 1, box_w, len(ASCII_LOGO) + 4, term.cyan)
    for i, line in enumerate(ASCII_LOGO):
        write_at(box_x + 2, logo_y + i + 1, term.cyan +
                 line[:box_w - 4] + term.normal)
    subtitle = "  Inventory Management System  "
    write_at((w - len(subtitle)) // 2, logo_y + len(ASCII_LOGO) +
             1, term.bright_white + subtitle + term.normal)
    time.sleep(0.8)

# ── auth screen ──────────────────────────────────────────────────────────────


def draw_auth_frame():
    clear_screen()
    w, h = term.width, term.height
    bw, bh = 50, 14
    bx, by = (w - bw) // 2, (h - bh) // 2
    box(bx, by, bw, bh, term.blue)
    center_text("── INVENTORY SYSTEM ──", bx, by, bw, term.cyan + term.bold)
    return bx, by, bw, bh


def auth_screen(employ):
    while True:
        bx, by, bw, _ = draw_auth_frame()
        center_text("[ S ] Sign Up     [ L ] Log In",
                    bx, by + 2, bw, term.yellow)
        center_text("[ Q ] Quit", bx, by + 3, bw, term.yellow)
        write_at(bx + 2, by + 5, term.white + "Choice: " + term.normal)
        print(term.move(by + 5, bx + 10), end="", flush=True)

        with term.cbreak():
            key = term.inkey(timeout=None)

        if key.lower() == "s":
            result = signup_screen(employ)
            if result:
                status_bar("Account created! Please log in.", term.green)
        elif key.lower() == "l":
            user = login_screen(employ)
            if user:
                return user
        elif key.lower() == "q":
            clear_screen()
            print(term.cyan + "\n  Goodbye!\n" + term.normal)
            raise SystemExit


def login_screen(employ):
    bx, by, bw, bh = draw_auth_frame()
    center_text("── LOG IN ──", bx, by, bw, term.cyan + term.bold)
    uname = input_at(bx + 4, by + 4, "Username : ", color=term.yellow)
    passw = input_at(bx + 4, by + 6, "Password : ",
                     secret=True, color=term.yellow)
    if uname in employ and employ[uname] == passw:
        status_bar(f"  Welcome back, {uname}!", term.green)
        time.sleep(0.8)
        return uname
    else:
        status_bar("  Invalid credentials. Try again.", term.red)
        time.sleep(1.2)
        return None


def signup_screen(employ):
    bx, by, bw, bh = draw_auth_frame()
    center_text("── SIGN UP ──", bx, by, bw, term.cyan + term.bold)
    uname = input_at(bx + 4, by + 4, "New Username : ", color=term.yellow)
    passw = input_at(bx + 4, by + 6, "New Password : ",
                     secret=True, color=term.yellow)
    if not uname:
        status_bar("  Username cannot be empty.", term.red)
        time.sleep(1)
        return False
    employ[uname] = passw
    save_employ(employ)
    return True

# ── main menu ────────────────────────────────────────────────────────────────


MENU_ITEMS = [
    ("A", "Add Items",        term.green),
    ("B", "Billing",          term.yellow),
    ("C", "Edit Inventory",   term.cyan),
    ("D", "Display All",      term.magenta),
    ("E", "Logout",           term.red),
]


def draw_main_menu(username):
    clear_screen()
    w, h = term.width, term.height
    bw, bh = 44, 16
    bx, by = (w - bw) // 2, (h - bh) // 2
    box(bx, by, bw, bh, term.blue)
    center_text("INVENTORY MANAGER", bx, by, bw, term.cyan + term.bold)
    write_at(bx + 2, by + 1, term.white + f" User: " +
             term.green + username + term.normal)
    for i, (key, label, color) in enumerate(MENU_ITEMS):
        row = by + 3 + i * 2
        write_at(bx + 6, row, term.blue +
                 "[ " + color + key + term.blue + " ]  " + term.white + label + term.normal)
    status_bar("  Use key shortcuts to navigate", term.white)


def main_menu(username, inventory, employ):
    while True:
        draw_main_menu(username)
        with term.cbreak():
            key = term.inkey(timeout=None)
        if key.lower() == "a":
            adding_items_screen(inventory)
        elif key.lower() == "b":
            billing_screen(inventory)
        elif key.lower() == "c":
            edit_inventory_screen(inventory)
        elif key.lower() == "d":
            display_all_screen(inventory)
        elif key.lower() == "e":
            break

# ── adding items ─────────────────────────────────────────────────────────────


def adding_items_screen(inventory):
    while True:
        clear_screen()
        w, h = term.width, term.height
        bw, bh = 54, 18
        bx, by = (w - bw) // 2, (h - bh) // 2
        box(bx, by, bw, bh, term.green)
        center_text("── ADD INVENTORY ITEM ──", bx,
                    by, bw, term.green + term.bold)

        bar = input_at(
            bx + 3, by + 2, "Barcode (0 to finish)  : ", color=term.yellow)
        if bar == "0":
            break
        if bar in inventory:
            status_bar("  Barcode already exists!", term.red)
            time.sleep(1)
            continue

        item = input_at(
            bx + 3, by + 4, "Item name              : ", color=term.yellow)
        # duplicate name check
        duplicate = any(
            item.upper() in inventory[k][0].upper() for k in inventory)
        if duplicate:
            status_bar("  Warning: similar item name found.", term.yellow)
            time.sleep(0.8)

        qty_str = input_at(
            bx + 3, by + 6, "Quantity               : ", color=term.yellow)
        price_str = input_at(
            bx + 3, by + 8, "Price                  : ", color=term.yellow)
        try:
            qty = int(qty_str)
            price = float(price_str)
        except ValueError:
            status_bar("  Invalid quantity or price.", term.red)
            time.sleep(1)
            continue

        inventory[bar] = [item, qty, price]
        save_inventory(inventory)
        status_bar(f"  '{item}' added successfully!", term.green)
        time.sleep(0.9)

# ── billing ──────────────────────────────────────────────────────────────────


def billing_screen(inventory):
    clear_screen()
    w, h = term.width, term.height
    bw = min(w - 4, 70)
    bx = (w - bw) // 2
    by = 1
    box(bx, by, bw, h - 3, term.yellow)
    center_text("── BILLING ──", bx, by, bw, term.yellow + term.bold)

    name = input_at(bx + 3, by + 2, "Customer name : ", color=term.cyan)
    date = input_at(bx + 3, by + 3, "Date (dd/mm/yyyy) : ", color=term.cyan)

    items, qtys, prices = [], [], []
    total = 0
    row = by + 5

    while True:
        if row >= h - 5:
            status_bar("  Receipt full. Press any key.", term.yellow)
            with term.cbreak():
                term.inkey()
            break
        bar = input_at(bx + 3, row, "Barcode (0 to finish) : ",
                       color=term.yellow)
        if bar == "0":
            break
        if bar not in inventory:
            status_bar("  Barcode not found.", term.red)
            time.sleep(0.8)
            write_at(bx + 3, row, " " * (bw - 6))
            continue
        item_data = inventory[bar]
        qty_str = input_at(
            bx + 3, row + 1, f"  Qty for '{item_data[0]}' : ", color=term.cyan)
        try:
            qty = int(qty_str)
        except ValueError:
            status_bar("  Invalid quantity.", term.red)
            time.sleep(0.8)
            write_at(bx + 3, row, " " * (bw - 6))
            write_at(bx + 3, row + 1, " " * (bw - 6))
            continue
        if qty > item_data[1]:
            status_bar(f"  Only {item_data[1]} in stock!", term.red)
            time.sleep(0.8)
            write_at(bx + 3, row, " " * (bw - 6))
            write_at(bx + 3, row + 1, " " * (bw - 6))
            continue

        t_price = item_data[2] * qty
        total += t_price
        items.append(item_data[0])
        qtys.append(qty)
        prices.append(item_data[2])
        item_data[1] -= qty
        inventory[bar] = item_data

        line = f"  {item_data[0][:20]:<22} x{
            qty:<4} @ {item_data[2]:.2f}$  = {t_price:.2f}$"
        write_at(bx + 3, row, term.white + line[:bw - 6] + term.normal)
        write_at(bx + 3, row + 1, " " * (bw - 6))
        row += 1

    save_inventory(inventory)

    # ── receipt ──
    clear_screen()
    rw = min(w - 4, 52)
    rx = (w - rw) // 2
    ry = 1
    rh = len(items) + 12
    box(rx, ry, rw, rh, term.green)
    center_text("  RECEIPT  ", rx, ry, rw, term.green + term.bold)
    write_at(rx + 3, ry + 1, term.cyan +
             f"Customer : {name.capitalize()}" + term.normal)
    write_at(rx + 3, ry + 2, term.cyan + f"Date     : {date}" + term.normal)
    # divider
    write_at(rx + 1, ry + 3, term.green + "╠" +
             "═" * (rw - 2) + "╣" + term.normal)
    header = f"{'Item':<22} {'Qty':>4}  {'Price':>8}  {'Total':>8}"
    write_at(rx + 3, ry + 4, term.yellow + header + term.normal)
    write_at(rx + 1, ry + 5, term.green + "╠" +
             "═" * (rw - 2) + "╣" + term.normal)
    for i in range(len(items)):
        line = f"{items[i][:21]:<22} {qtys[i]:>4}  {
            prices[i]:>7.2f}$  {qtys[i]*prices[i]:>7.2f}$"
        write_at(rx + 3, ry + 6 + i, term.white + line[:rw - 6] + term.normal)
    sep_row = ry + 6 + len(items)
    write_at(rx + 1, sep_row, term.green + "╠" +
             "═" * (rw - 2) + "╣" + term.normal)
    write_at(rx + 3, sep_row + 1, term.bright_white +
             f"{'TOTAL':<30} {total:>10.2f}$" + term.normal)
    write_at(rx + 1, sep_row + 2, term.green + "╚" +
             "═" * (rw - 2) + "╝" + term.normal)
    status_bar("  Press any key to return to menu…", term.white)
    with term.cbreak():
        term.inkey()

# ── edit inventory ───────────────────────────────────────────────────────────


def edit_inventory_screen(inventory):
    if not inventory:
        status_bar("  No items in inventory.", term.red)
        time.sleep(1)
        return

    items = list(inventory.keys())
    cursor = 0

    while True:
        clear_screen()
        w, h = term.width, term.height
        bw = min(w - 4, 70)
        bx = (w - bw) // 2
        by = 1
        visible = h - 8
        box(bx, by, bw, h - 3, term.cyan)
        center_text("── EDIT INVENTORY ── (↑↓ navigate, E edit, Q back)",
                    bx, by, bw, term.cyan + term.bold)

        start = max(0, cursor - visible // 2)
        end = min(len(items), start + visible)
        for idx, key in enumerate(items[start:end]):
            row = by + 2 + idx
            d = inventory[key]
            line = f"  {key:<12} {d[0]:<20} Qty:{d[1]:<6} ${d[2]:.2f}"
            color = term.reverse if (start + idx) == cursor else term.normal
            write_at(bx + 1, row, color + line[:bw - 2] + term.normal)

        status_bar("  ↑↓ Move   E Edit   Q Back", term.white)

        with term.cbreak():
            key_pressed = term.inkey(timeout=None)

        if key_pressed.name == "KEY_UP":
            cursor = max(0, cursor - 1)
        elif key_pressed.name == "KEY_DOWN":
            cursor = min(len(items) - 1, cursor + 1)
        elif key_pressed.lower() == "e":
            _edit_item(bx, by, bw, items[cursor], inventory)
        elif key_pressed.lower() == "q":
            break


def _edit_item(bx, by, bw, barcode, inventory):
    d = inventory[barcode]
    clear_screen()
    w, h = term.width, term.height
    ebw, ebh = 50, 14
    ebx, eby = (w - ebw) // 2, (h - ebh) // 2
    box(ebx, eby, ebw, ebh, term.cyan)
    center_text(f"  Editing: {d[0]}  ", ebx, eby, ebw, term.cyan + term.bold)
    write_at(ebx + 3, eby + 2, term.yellow +
             f"Barcode  : {barcode}" + term.normal)
    write_at(ebx + 3, eby + 3, term.yellow +
             f"Quantity : {d[1]}" + term.normal)
    write_at(ebx + 3, eby + 4, term.yellow +
             f"Price    : {d[2]:.2f}$" + term.normal)
    write_at(ebx + 3, eby + 6, term.white +
             "[ Q ] Quantity   [ P ] Price   [ B ] Back" + term.normal)

    with term.cbreak():
        sel = term.inkey(timeout=None)

    if sel.lower() == "q":
        val = input_at(ebx + 3, eby + 8, "New quantity : ", color=term.green)
        try:
            d[1] = int(val)
            inventory[barcode] = d
            save_inventory(inventory)
            status_bar("  Quantity updated!", term.green)
        except ValueError:
            status_bar("  Invalid value.", term.red)
        time.sleep(0.8)
    elif sel.lower() == "p":
        val = input_at(ebx + 3, eby + 8, "New price : ", color=term.green)
        try:
            d[2] = float(val)
            inventory[barcode] = d
            save_inventory(inventory)
            status_bar("  Price updated!", term.green)
        except ValueError:
            status_bar("  Invalid value.", term.red)
        time.sleep(0.8)

# ── display all ──────────────────────────────────────────────────────────────


def display_all_screen(inventory):
    if not inventory:
        status_bar("  Inventory is empty.", term.red)
        time.sleep(1)
        return

    items = list(inventory.keys())
    cursor = 0

    while True:
        clear_screen()
        w, h = term.width, term.height
        bw = min(w - 4, 74)
        bx = (w - bw) // 2
        by = 1
        visible = h - 7
        box(bx, by, bw, h - 3, term.magenta)
        center_text("── ALL INVENTORY ITEMS ── (↑↓ scroll, Q back)",
                    bx, by, bw, term.magenta + term.bold)
        # header
        header = f"  {'Barcode':<14} {'Name':<22} {'Qty':>6}  {'Price':>8}"
        write_at(bx + 1, by + 1, term.yellow + header[:bw - 2] + term.normal)
        write_at(bx + 1, by + 2, term.magenta + "╠" +
                 "═" * (bw - 2) + "╣" + term.normal)

        start = max(0, cursor - visible // 2)
        end = min(len(items), start + visible)
        for idx, key in enumerate(items[start:end]):
            row = by + 3 + idx
            d = inventory[key]
            line = f"  {key:<14} {d[0]:<22} {d[1]:>6}  {d[2]:>7.2f}$"
            color = term.reverse if (start + idx) == cursor else term.normal
            write_at(bx + 1, row, color + line[:bw - 2] + term.normal)

        write_at(bx + 2, h - 4, term.white +
                 f"  {len(items)} items total" + term.normal)
        status_bar("  ↑↓ Scroll   Q Back", term.white)

        with term.cbreak():
            key_pressed = term.inkey(timeout=None)

        if key_pressed.name == "KEY_UP":
            cursor = max(0, cursor - 1)
        elif key_pressed.name == "KEY_DOWN":
            cursor = min(len(items) - 1, cursor + 1)
        elif key_pressed.lower() == "q":
            break

# ── entry point ──────────────────────────────────────────────────────────────


def main():
    employ = load_employ()
    inventory = load_inventory()

    with term.fullscreen(), term.hidden_cursor():
        splash()
        while True:
            username = auth_screen(employ)
            if username:
                main_menu(username, inventory, employ)


if __name__ == "__main__":
    main()
