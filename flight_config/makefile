# Detect operating system
ifeq ($(OS),Windows_NT)
	WINDOWS = 1
endif

MCU = 64m1
DEVICE = m$(MCU)
PGMR = stk500
CONF = avrdude.conf
EEPROM = eeprom.bin

ifeq ($(WINDOWS),1)
	PYTHON = python
else
	PYTHON = python3
endif


.PHONY: help eeprom harness hash ports read_fuses write_debug_fuses write_flight_fuses write_fuses write_optical_fuses

help:
	@echo "usage: make [help | eeprom | harness | hash | ports | read_fuses | upload | upload_bin | write_debug_fuses | write_flight_fuses | write_fuses | write_optical_fuses]"

eeprom:
	@echo "Reading EEPROM to binary file eeprom.bin..."
	avrdude -p $(DEVICE) -c $(PGMR) -P $(PORT) -U eeprom:r:$(EEPROM):r -C ./$(CONF)
	@echo "Displaying eeprom.bin in hex..."
	hexdump eeprom.bin

hash:
ifeq ($(WINDOWS),1)
	@for file in ./* ; do \
		powershell Get-FileHash -Path ./$$file -Algorithm SHA256 ; \
	done
else
	@for file in ./* ; do \
		shasum -a 256 $$file ; \
	done
endif

ports:
	@echo "Programming port(s):"
	pavr2cmd --prog-port
	@echo "UART port(s):"
	pavr2cmd --ttl-port

read_fuses:
	avrdude -P $(PORT) -c $(PGMR) -p $(DEVICE) -v -C ./$(CONF)

write_fuses:
	avrdude -U efuse:w:$(EFUSE):m -U hfuse:w:$(HFUSE):m -U lfuse:w:$(LFUSE):m -c $(PGMR) -p $(DEVICE) -P $(PORT) -C ./$(CONF)

write_debug_fuses:
	make write_fuses EFUSE=0xf9 HFUSE=0xd7 LFUSE=0xff

write_flight_fuses:
	make write_fuses EFUSE=0xf9 HFUSE=0xdf LFUSE=0xff

write_optical_fuses:
	make write_fuses EFUSE=0xf8 HFUSE=0xd7 LFUSE=0xff

harness:
	@echo "Computing hash on file..."
ifeq ($(WINDOWS),1)
	powershell Get-FileHash -Path ./$(PROG) -Algorithm SHA256
else
	shasum -a 256 $(PROG)
endif
	@read -p "Press enter to continue: "
	$(PYTHON) ./harness.py -p $(PORT) -u $(UART) -d ./ -b $(PROG) -v

upload:
	@echo "Computing hash on file..."
ifeq ($(WINDOWS),1)
	powershell Get-FileHash -Path ./$(PROG) -Algorithm SHA256
else
	shasum -a 256 $(PROG)
endif
	@read -p "Press enter to continue: "
	avrdude -c $(PGMR) -C ./$(CONF) -p $(DEVICE) -P $(PORT) -U flash:w:./$(PROG)

# This is just for the test harness because harness.py calls the command
# "make upload_bin" when supplied with a pre-compiled binary
upload_bin: upload
