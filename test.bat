@echo off
cls

rem python Mausembler.py test.dasm test.out
python Mausembler.py ilog.dasm ilog.bin
rem python Mausembler.py src\0x42c.dasm16 0x42c.bin