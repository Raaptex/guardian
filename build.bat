@echo off
echo current.json
pause
pyinstaller --noconfirm --onefile --windowed --icon "logo.ico" --name "Guardian" --add-data "interface;interface/" "main.py"
cd dist
move Guardian.exe ../installer/
cd ../agent
pyinstaller --noconfirm --onefile --windowed --icon "logo.ico" --add-data "logo.ico;." "agent.py"
cd dist
move agent.exe ../../installer/
cd ..
pyinstaller --noconfirm --onefile --windowed --icon "NONE" --name discord-agent "discord-agent.py"
cd dist
move discord-agent.exe ../../installer/
cd ../../uninstall
pyinstaller --noconfirm --onefile --console --icon "NONE" --name guardian-uninstall "uninstall.py"
cd dist
move guardian-uninstall.exe ../../installer/
pause
cd ../../installer/
pyinstaller --noconfirm --onefile --console --icon "../logo.ico" --name "guardian-setup-v1-" --add-data "guardian-uninstall.exe;." --add-data "agent.exe;." --add-data "current.json;." --add-data "discord-agent.exe;." --add-data "Guardian.exe;." "install.py"
pause