MCU = 64m1
DEVICE = m$(MCU)
PGMR = stk500
CONF = avrdude.conf
EEPROM = eeprom.bin

PYTHON = python3

.PHONY: help eeprom harness hash ports read_fuses write_debug_fuses write_flight_fuses write_fuses write_optical_fuses

help:
	@echo "usage: make [help | eeprom | harness | hash | ports | read_fuses | write_debug_fuses | write_flight_fuses | write_fuses | write_optical_fuses]"

eeprom:
	@echo "Reading EEPROM to binary file eeprom.bin..."
	avrdude -p $(DEVICE) -c $(PGMR) -P $(PORT) -U eeprom:r:$(EEPROM):r
	@echo "Displaying eeprom.bin in hex..."
	hexdump eeprom.bin

hash:
	@for file in ./* ; do \
		shasum -a 256 $$file ; \
	done

# TODO - test on macOS, Windows, Linux
ports:
	@echo "Programming port(s):"
	pavr2cmd --prog-port
	@echo "UART port(s):"
	pavr2cmd --ttl-port

read_fuses:
	avrdude -P $(PORT) -c $(PGMR) -p $(DEVICE) -v

write_fuses:
	avrdude -U efuse:w:$(EFUSE):m -U hfuse:w:$(HFUSE):m -U lfuse:w:$(LFUSE):m -c $(PGMR) -p $(DEVICE) -P $(PORT)

write_debug_fuses:
	make write_fuses EFUSE=0xf9 HFUSE=0xd7 LFUSE=0xff

write_flight_fuses:
	make write_fuses EFUSE=0xf9 HFUSE=0xdf LFUSE=0xff

write_optical_fuses:
	make write_fuses EFUSE=0xf8 HFUSE=0xd7 LFUSE=0xff

harness:
	@echo "Computing hash on file..."
	shasum -a 256 $(PROG)
	@read -p "Press enter to continue: "
	$(PYTHON) ./harness.py -p $(PORT) -u $(UART) -d ./ -b $(PROG) -v

upload:
	@echo "Computing hash on file..."
	shasum -a 256 $(PROG)
	@read -p "Press enter to continue: "
	avrdude -c $(PGMR) -C ./$(CONF) -p $(DEVICE) -P $(PORT) -U flash:w:./$(PROG)
