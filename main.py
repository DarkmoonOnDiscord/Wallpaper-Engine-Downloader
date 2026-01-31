import os
import sys
import threading
import subprocess
import base64
import re
import time
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    from winotify import Notification, audio
    HAS_NOTIF = True
except:
    HAS_NOTIF = False

CHROME_PATH = os.path.join("chromium", "chrome.exe")
CHROMEDRIVER_PATH = os.path.join("chromium", "chromedriver.exe")
DEPOT_EXE_PATH = os.path.join("DepotdownloaderMod", "DepotDownloadermod.exe")
WORKSHOP_URL = "https://steamcommunity.com/workshop/browse/?appid=431960&browsesort=trend&actualsort=trend&p=1&days=-1"
CONFIG_FILE = "lastsavelocation.cfg"

ACCOUNTS = {
    'ruiiixx': 'UzY3R0JUQjgzRDNZ',
    'premexilmenledgconis': 'M3BYYkhaSmxEYg==',
    'vAbuDy': 'Qm9vbHE4dmlw',
    'adgjl1182': 'UUVUVU85OTk5OQ==',
    'gobjj16182': 'enVvYmlhbzgyMjI=',
    '787109690': 'SHVjVXhZTVFpZzE1'
}

active_downloads = set()
download_queue = queue.Queue()
current_account_index = 0
save_location = None


def load_save_location():
    global save_location
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                path = f.read().strip()
                if path and os.path.isdir(path):
                    target = os.path.join(path, 'projects', 'myprojects')
                    if os.path.isdir(target):
                        save_location = path
                        return True
    except:
        pass
    return False


def save_save_location(path):
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(path)
    except:
        pass


def select_save_location():
    global save_location
    
    root = tk.Tk()
    root.withdraw()
    
    messagebox.showinfo(
        "Select Wallpaper Engine Folder",
        "Please select your Wallpaper Engine installation folder.\n\n"
        "Example: C:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine"
    )
    
    while True:
        selected = filedialog.askdirectory(title="Select Wallpaper Engine Folder")
        
        if not selected:
            if messagebox.askyesno("No Folder Selected", "You must select a folder. Try again?"):
                continue
            else:
                root.destroy()
                return False
        
        target = os.path.join(selected, 'projects', 'myprojects')
        
        if os.path.isdir(target):
            save_location = selected
            save_save_location(selected)
            print(f"  [OK] Save location: {selected}")
            root.destroy()
            return True
        else:
            if messagebox.askyesno(
                "Invalid Folder",
                f"This folder doesn't contain 'projects\\myprojects'.\n\n"
                f"Selected: {selected}\n\n"
                "Make sure you select the wallpaper_engine folder.\n\n"
                "Try again?"
            ):
                continue
            else:
                root.destroy()
                return False


def get_account(index):
    accounts_list = list(ACCOUNTS.items())
    if index >= len(accounts_list):
        return None, None
    username, encoded_pwd = accounts_list[index]
    try:
        password = base64.b64decode(encoded_pwd).decode('utf-8')
        return username, password
    except:
        return None, None


def send_notification(title, message):
    if not HAS_NOTIF:
        return
    try:
        toast = Notification(app_id="Workshop Downloader", title=title, msg=message, duration="short")
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except:
        pass


def run_download(pubfileid):
    global current_account_index, save_location
    
    print(f"\n{'='*50}")
    print(f"DOWNLOADING: {pubfileid}")
    print(f"{'='*50}")
    
    if not save_location:
        print("[ERROR] Save location not set!")
        send_notification("Download Failed", "Save location not set")
        active_downloads.discard(pubfileid)
        return
    
    target_dir = os.path.join(save_location, 'projects', 'myprojects', pubfileid)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"[PATH] {target_dir}")
    
    exe = DEPOT_EXE_PATH if os.path.exists(DEPOT_EXE_PATH) else "DepotDownloadermod.exe"
    
    if not os.path.exists(exe):
        print(f"[ERROR] Exe not found")
        send_notification("Download Failed", "DepotDownloader not found")
        active_downloads.discard(pubfileid)
        return
    
    start_index = current_account_index
    tried_accounts = 0
    total_accounts = len(ACCOUNTS)
    
    while tried_accounts < total_accounts:
        account_index = (start_index + tried_accounts) % total_accounts
        username, password = get_account(account_index)
        
        if not username or not password:
            tried_accounts += 1
            continue
        
        print(f"[ACCOUNT] Trying: {username} ({account_index + 1}/{total_accounts})")
        
        cmd = [
            exe,
            '-app', '431960',
            '-pubfile', pubfileid,
            '-verify-all',
            '-username', username,
            '-password', password,
            '-dir', target_dir
        ]
        
        print("-" * 50)
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, startupinfo=startupinfo,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            
            output_lines = []
            
            for line in proc.stdout:
                line = line.strip()
                if line:
                    print(line)
                    output_lines.append(line.lower())
            
            proc.wait()
            
            full_output = ' '.join(output_lines)
            login_failed = any(x in full_output for x in [
                'login failed', 'invalid password', 'invalid credentials',
                'access denied', 'rate limit', 'too many', 'captcha',
                'steam guard', 'two factor', '2fa', 'authentication',
                'login key', 'expired', 'denied'
            ])
            
            print("-" * 50)
            
            if proc.returncode == 0 and not login_failed:
                print(f"SUCCESS (using {username})")
                current_account_index = account_index
                send_notification("Download Complete", f"Item {pubfileid}")
                active_downloads.discard(pubfileid)
                print(f"{'='*50}\n")
                return
            
            if login_failed:
                print(f"[FAILED] Account {username} didn't work, trying next...")
                tried_accounts += 1
                continue
            else:
                print(f"FAILED (code {proc.returncode})")
                send_notification("Download Failed", f"Item {pubfileid}")
                active_downloads.discard(pubfileid)
                print(f"{'='*50}\n")
                return
                
        except Exception as e:
            print(f"ERROR: {e}")
            tried_accounts += 1
            continue
    
    print(f"[ERROR] All {total_accounts} accounts failed!")
    send_notification("Download Failed", "All accounts failed")
    active_downloads.discard(pubfileid)
    print(f"{'='*50}\n")


def worker_loop():
    while True:
        item_id = download_queue.get()
        if item_id:
            run_download(item_id)
        download_queue.task_done()


INJECT_JS = """
(function() {
    if (window.__dlReady) return;
    window.__dlReady = true;

    var style = document.createElement('style');
    style.textContent = '#dlBtn{display:inline-flex;align-items:center;padding:10px 24px;background:#1a9fff;border-radius:3px;cursor:pointer;margin:8px 0}#dlBtn:hover{background:#00bbff}#dlBtn span{color:#fff;font-size:14px;font-weight:500}#dlBtn.clicked{background:#444;pointer-events:none}';
    document.head.appendChild(style);

    function inject() {
        if (document.getElementById('dlBtn')) return;
        
        var params = new URLSearchParams(window.location.search);
        var id = params.get('id');
        if (!id) return;

        var selectors = ['#SubscribeItemBtn', '#SubscribeItemOptionAdd', '.subscribeOption'];
        var target = null;
        
        for (var i = 0; i < selectors.length; i++) {
            target = document.querySelector(selectors[i]);
            if (target) break;
        }

        if (target) {
            target.style.display = 'none';
            
            var btn = document.createElement('div');
            btn.id = 'dlBtn';
            btn.innerHTML = '<span>Download</span>';
            btn.onclick = function() {
                window.__downloadRequested = id;
                btn.className = 'clicked';
                btn.innerHTML = '<span>Added to Queue</span>';
                setTimeout(function() {
                    btn.className = '';
                    btn.innerHTML = '<span>Download</span>';
                }, 1500);
            };
            target.parentNode.insertBefore(btn, target);
        }
    }

    inject();
    new MutationObserver(inject).observe(document.body, {childList: true, subtree: true});
})();
"""


class Browser:
    def __init__(self):
        self.driver = None
        self.tabs = {}
        self.known_handles = []

    def start(self):
        options = Options()
        options.binary_location = CHROME_PATH
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        profile = os.path.join(os.getcwd(), 'chrome_data')
        options.add_argument(f'--user-data-dir={profile}')
        
        service = Service(CHROMEDRIVER_PATH)
        service.creation_flags = subprocess.CREATE_NO_WINDOW
        
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get(WORKSHOP_URL)
            return True
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def is_item_page(self, url):
        return 'filedetails' in url and 'id=' in url

    def check_download_request(self):
        try:
            result = self.driver.execute_script("var r = window.__downloadRequested; window.__downloadRequested = null; return r;")
            return result
        except:
            return None

    def monitor(self):
        try:
            self.known_handles = self.driver.window_handles
        except:
            pass

        while True:
            try:
                current_handles = self.driver.window_handles
                
                # Switch to new tab if detected
                if set(current_handles) != set(self.known_handles):
                    if current_handles:
                        try:
                            self.driver.switch_to.window(current_handles[-1])
                        except:
                            pass
                    self.known_handles = current_handles

                try:
                    url = self.driver.current_url
                except:
                    time.sleep(0.5)
                    continue

                if url in ['about:blank', 'chrome://newtab/', ''] or 'new-tab' in url.lower():
                    self.driver.get(WORKSHOP_URL)

                if self.is_item_page(url):
                    self.driver.execute_script(INJECT_JS)
                    
                    req = self.check_download_request()
                    if req and req not in active_downloads:
                        active_downloads.add(req)
                        print(f"[QUEUE] Added to queue: {req}")
                        download_queue.put(req)
                
                time.sleep(0.2)
                
            except Exception as e:
                err = str(e).lower()
                if 'no such window' in err or 'target window already closed' in err:
                    time.sleep(0.5)
                elif 'window' in err or 'disconnect' in err or 'target' in err:
                    print("\nBrowser closed.")
                    subprocess.Popen('taskkill /f /im DepotDownloadermod.exe', 
                                   creationflags=subprocess.CREATE_NO_WINDOW,
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)
                    os._exit(0)
                time.sleep(0.5)


def change_save_location():
    global save_location
    
    root = tk.Tk()
    root.withdraw()
    
    selected = filedialog.askdirectory(title="Select Wallpaper Engine Folder")
    
    if selected:
        target = os.path.join(selected, 'projects', 'myprojects')
        if os.path.isdir(target):
            save_location = selected
            save_save_location(selected)
            print(f"\n[OK] Save location changed to: {selected}\n")
        else:
            messagebox.showerror("Invalid Folder", "This folder doesn't contain 'projects\\myprojects'")
    
    root.destroy()


def main():
    global save_location
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║   WALLPAPER ENGINE WORKSHOP DOWNLOADER    ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()
    
    if not os.path.exists(CHROME_PATH):
        print(f"  [ERROR] Chrome not found: {CHROME_PATH}")
        input("\n  Press Enter to exit...")
        return
    
    if not os.path.exists(CHROMEDRIVER_PATH):
        print(f"  [ERROR] ChromeDriver not found: {CHROMEDRIVER_PATH}")
        input("\n  Press Enter to exit...")
        return
    
    exe = DEPOT_EXE_PATH if os.path.exists(DEPOT_EXE_PATH) else "DepotDownloadermod.exe"
    if not os.path.exists(exe):
        print(f"  [ERROR] DepotDownloader not found")
        input("\n  Press Enter to exit...")
        return
    
    print(f"  [OK] Chrome")
    print(f"  [OK] ChromeDriver")
    print(f"  [OK] DepotDownloader")
    print(f"  [OK] {len(ACCOUNTS)} accounts loaded")
    
    if not load_save_location():
        print()
        print("  [!] No save location configured.")
        print("  [!] Please select your Wallpaper Engine folder...")
        print()
        
        if not select_save_location():
            print("\n  [ERROR] Save location is required!")
            input("\n  Press Enter to exit...")
            return
    
    print(f"  [OK] Save location: {save_location}")
    print()
    
    browser = Browser()
    if not browser.start():
        input("\n  Press Enter to exit...")
        return
    
    print("  ─────────────────────────────────────────────")
    print("  Ready! Click 'Download' on Workshop items.")
    print("  Type 'path' + Enter to change save location.")
    print("  ─────────────────────────────────────────────")
    print()
    
    # Start the worker thread for the queue
    threading.Thread(target=worker_loop, daemon=True).start()
    
    def input_listener():
        while True:
            try:
                cmd = input().strip().lower()
                if cmd == 'path':
                    change_save_location()
            except:
                break
    
    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()
    
    try:
        browser.monitor()
    except KeyboardInterrupt:
        pass
    finally:
        subprocess.Popen('taskkill /f /im DepotDownloadermod.exe',
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stderr=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL)
        try:
            browser.driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()