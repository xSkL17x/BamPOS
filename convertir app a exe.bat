@echo off
pyinstaller --name="BamPos" --onedir --add-data "assets/:assets/" --add-data "administrar/administrar.kv:." --add-data "pos/pos.kv:." --icon="icono.ico" --noconsole main.py




pause
