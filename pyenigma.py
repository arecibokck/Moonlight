import sys
from enigma.machine import EnigmaMachine

# setup machine according to specs from a daily key sheet:

machine = EnigmaMachine.from_key_sheet(rotors='II IV V', reflector='B',
                                       ring_settings=[1, 20, 11],
                                       plugboard_settings='AV BS CG DL FU HZ IN\
                                       KM OW RX')

# ENCRYPTION

# set machine initial starting position
machine.set_display('WXC')

# encrypt the message key
enc_key = machine.process_text('KCH')

# set machine starting position as given by the chosen key
machine.set_display('KCH')

# encrypt the message with chosen key
ciphertext = machine.process_text(sys.argv[1], replace_char='X')
print (ciphertext)

# DECRYPTION

# set machine initial starting position
machine.set_display('WXC')

# decrypt the message key
msg_key = machine.process_text(enc_key)

# set machine starting position as given by the sent (decrypted) key
machine.set_display(msg_key)

# decrypt the message with sent (decrypted) key
plaintext = machine.process_text(ciphertext)

print(plaintext)