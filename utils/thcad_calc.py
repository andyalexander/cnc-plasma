boards = [{'freq_zero': 100.4, 'freq_full': 904.9, 'volt_full':5 ,'freq_div':32, 'plasma_divider_ratio':40},
          {'freq_zero': 101.2, 'freq_full': 904.4, 'volt_full':5,'freq_div':32,'plasma_divider_ratio':1},
          ]

# VOLT RANGE: 5 (W1=down) or 10 (W1=up)
# freq_div = 32 or 64 or 128, 32 recommended in QTPlasmac docs

#plasma_divider_ratio: default is 50:1; better is 20:1, if using 50:1 use a 5v scale, if 20:1 use 10v
encoder_max_freq = 3e6  # 3 MHz
encoder_implied_scale = 1 / encoder_max_freq

max_torch_voltage = 200

for i, board in enumerate(boards):
    print(f"Board {i + 1}: F0={board['freq_zero']} MHz, FFS={board['freq_full']} MHz")
    scale = board['volt_full'] * board['freq_div'] * board['plasma_divider_ratio'] / (1000 * (board['freq_full'] - board['freq_zero']))
    offset = 1000 * board['freq_zero'] / board['freq_div']

    print(f"Scale: {scale:.6f}, Offset: {offset:.3f}")

    print(f"Freq at max voltage: {(max_torch_voltage * (1 / scale) + offset) / 1e6:.2f} MHz")

    print(f"At max voltage we use: {max_torch_voltage / (board['volt_full'] * board['plasma_divider_ratio']) * 100:.0f}% of the total")
    print(f"Input voltage will be {board['volt_full']}v to give max torch voltage of {board['volt_full']*board['plasma_divider_ratio']:.0f}v")

    print('-' * 40 + '\n')
