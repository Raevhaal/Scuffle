# SCUFFLE
Soul Calibur 6 Live Frame Data Reader -- based on the useful parts of the popular Tekken Bot Prime, it shows you frame data while you're playing the game so you don't have to alt-tab to a wiki or a google doc or a paste bin or yell at your twitch chat or <character> discord. Some of the frame data is even correct.

![image](https://user-images.githubusercontent.com/44570288/47742019-b740ca00-dc49-11e8-8f68-938c418bbaa3.png)

# Usage

Download the latest release from https://github.com/rougelite/SCUFFLE/releases. Run the .exe at the same as Soul Calibur 6 (PC version only) and it will read the memory to display internal frame data. The frame data overlay should display at the top of the screen, works only in windowed or windowed borderless mode (NO FULLSCREEN).

# Technical

SCUFFLE uses python 3.5 and strives to use only Standard Library modules so it should run with any 64-bit python 3.5. 32-bit Python (the default if you use the installer) probably won't work.

To build the project, make sure you have python 3.5 and pyinstaller and run the the project_build.bat file.

# I want to know more!

Check out https://www.youtube.com/watch?v=GjB-MRonAFc or read [How the Movelist is Parsed](__HowTheMovelistBytesWork.md)
