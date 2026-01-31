# 📥 Wallpaper Engine Workshop Downloader

A powerful, automated tool to download Steam Workshop wallpapers directly into Wallpaper Engine without needing the Steam client running. Features a custom browser integration with a "One-Click" download system.

![Project Banner or Main Screensh<img width="1280" height="714" alt="Gemini_Generated_Image_iwz70uiwz70uiwz7-Photoroom" src="https://github.com/user-attachments/assets/4d328a9a-4df0-495c-bcf1-b213e2c3dd96" />
ot]

## ⚡ Features

* **One-Click Download:** Injects a seamless "Download" button directly into the Workshop page.
* **Queue System:** Browse and click multiple wallpapers; they will download in the background automatically.
* **No Steam Client Required:** Uses `DepotDownloader` to fetch files directly from Steam servers.
* **Auto-Install:** Places files in the correct directory so Wallpaper Engine detects them instantly without a restart.

---

## 🚀 How to Install & Use

### 1. Download
Go to the **Releases** page and download the latest `.zip` file.

[**🔗 CLICK HERE TO DOWNLOAD LATEST RELEASE**](PLACE_LINK_TO_GITHUB_RELEASES_PAGE_HERE)

![Screenshot of the Release Page download button](PLACE_IMAGE_LINK_HERE)

### 2. Extract
Unzip the downloaded file into a folder of your choice.

> **Note:** Do not run the files directly from the zip archive. Extract them first!

### 3. Run
Double-click **`Launch.bat`** to start the application.
*(Alternatively, if you are running from source, open a terminal and run `python start.py`)*

### 4. Select Wallpaper Engine Folder
On the first launch, a popup will ask for your Wallpaper Engine installation path.
Navigate to your folder, usually located here:
`C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine`

![Screenshot of the Folder Selection Dialog](PLACE_IMAGE_LINK_HERE)

### 5. Browse & Download
A customized browser window will open. Browse the Workshop as you normally would. When you see a wallpaper you like, click the **Download** button (this replaces the standard Subscribe button).

![Screenshot of the Browser Window with items](PLACE_IMAGE_LINK_HERE)

![Screenshot of the Download Button being clicked](PLACE_IMAGE_LINK_HERE)

### 6. Done!
The download usually takes **15-20 seconds**.
Once the notification appears, the wallpaper is ready! It will appear in Wallpaper Engine immediately—**no restart required** if your folder path was set correctly.

---

## ❓ F.A.Q.

### Q: Why is the download size so large (heavy)?
**A:** The release package includes a standalone version of **Chromium** (a web browser) and the necessary drivers. We bundle this so you don't need to install or configure Chrome manually on your PC. It ensures the tool is "plug-and-play" and works correctly regardless of your default browser settings.

### Q: The console window closes immediately when I open it.
**A:** This usually happens if the folder structure is incomplete. Ensure you extracted **all** files from the .zip, including the `chromium` and `DepotdownloaderMod` folders. Do not move the `.exe` or `.py` files out of the main folder.

### Q: Does this work with Steam Guard / 2FA enabled accounts?
**A:** The tool uses shared accounts configured in the script. If you modify the script to use your own account, note that `DepotDownloader` may struggle with 2FA prompts during automation. It is best to use the provided accounts or a secondary account without 2FA.

### Q: My download is stuck in the "Queue".
**A:** The queue processes one file at a time. If the first download is taking a long time (e.g., a very large video wallpaper), the others will wait. Check the black console window to see the progress log.

### Q: Can I change the download location later?
**A:** Yes. In the black console window that runs in the background, type `path` and press **Enter**. It will prompt you to select a new folder.

---

## ⚠️ Disclaimer
This tool is for educational purposes and simplifies the use of `DepotDownloader`. The creators are not responsible for any misuse of Steam services. Please support creators by subscribing to items on Steam when possible.
