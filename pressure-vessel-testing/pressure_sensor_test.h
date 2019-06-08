#ifndef SENSORS_H
#define SENSORS_H

#ifndef F_CPU
#define F_CPU 8000000UL
#endif

#include <SPI.h>
#include <stdint.h>

#define PRES_RESET_SPI  0x1E
#define PRES_D1_4096    0x48
#define PRES_D2_4096    0x58
#define PRES_ADC_READ   0x00
#define PRES_PROM_BASE  0xA0


// Pressure sensor
#define PRES_CS_PIN 52

// pressure
void pres_reset(void);
uint16_t pres_read_prom(uint8_t address);
uint32_t pres_read_raw_uncompensated_data(uint8_t cmd);
uint32_t pres_read_raw_uncompensated_pressure(void);
uint32_t pres_read_raw_uncompensated_temperature(void);
uint32_t pres_convert_raw_uncompensated_data_to_raw_pressure(uint32_t D1, uint32_t D2, uint32_t *raw_temperature);
uint32_t pres_read_raw_pressure(void);
float pres_convert_raw_temperature_to_temperature(uint32_t raw_temperature);

#endif
