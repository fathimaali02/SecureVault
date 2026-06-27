from main import SecureFileVault
import os

vault = SecureFileVault()
file_id = '1ded6d0835b6270e'
password = 'testpassword123'  # not used in our test if file decrypts

# Test 1: provide directory
out_dir = os.path.join(os.getcwd(), 'test_out')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
print('Test 1: output directory:', out_dir)
success, msg = vault.retrieve_file(file_id, password, out_dir)
print('Result:', success, msg)

# Test 2: provide filename without extension
out_file_noext = os.path.join(os.getcwd(), 'test_out', 'retrieved_noext')
print('\nTest 2: filename without extension:', out_file_noext)
success, msg = vault.retrieve_file(file_id, password, out_file_noext)
print('Result:', success, msg)

# Test 3: provide filename with .txt extension
out_file_txt = os.path.join(os.getcwd(), 'test_out', 'retrieved.txt')
print('\nTest 3: filename with extension:', out_file_txt)
success, msg = vault.retrieve_file(file_id, password, out_file_txt)
print('Result:', success, msg)

# List output dir
print('\nContents of test_out:')
for f in os.listdir(out_dir):
    print(' -', f)
