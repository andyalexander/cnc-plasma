freq_zero = 100.4
freq_full = 904.9
volt_full = 5  # or 5 or 10
freq_div = 32  # or 32 or 64 or 128, 32 recommended in QTPlasmac docs
plasma_divider_ratio = 50  # default is 50:1; better is 20:1
encoder_max_freq = 3e6  # 3 MHz
encoder_implied_scale = 1 / encoder_max_freq

max_torch_voltage = 200

# freq_zero = 122.9
# freq_full = 925.7
# volt_full = 10 # or 5 or 10
# freq_div = 32 # or 32 or 64 or 128
# plasma_divider_ratio = 50  # default is 50:1; better is 20:1
# encoder_max_freq = 3e6 # 3 MHz
# encoder_implied_scale = 1/encoder_max_freq
# max_torch_voltage = 200


scale = volt_full * freq_div * plasma_divider_ratio / (1000 * (freq_full - freq_zero))
offset = 1000 * freq_zero / freq_div

print(f"Scale: {scale:.8f}, Offset: {offset:.8f}")

print(f"Freq at max voltage: {(max_torch_voltage * (1 / scale) + offset) / 1e6:.2f} MHz")

print(f"At max voltage we use: {max_torch_voltage / (volt_full * plasma_divider_ratio) * 100:.0f}% of the total")

# * scale = thcad_model_voltage * frequency_divider * plasma_divider_ratio / (max_voltage_frequency - zero_voltage_frequency)
# * offset = zero_voltage_frequency / frequency_divider
