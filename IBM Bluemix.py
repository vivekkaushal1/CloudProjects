#Python Appliction to upload a file from local repository to IBM Bluemix.

import os
import json
import keystoneclient.v3 as keystoneclient
import swiftclient.client as swiftclient
import gnupg
try:
  from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
  from SocketServer import TCPServer as Server
except ImportError:
  from http.server import SimpleHTTPRequestHandler as Handler
  from http.server import HTTPServer as Server

PORT = int(os.getenv('VCAP_APP_PORT', 8003))
os.chdir('/your local directory to upload file/')

def mainFunc():
    #Bluemix Credentials
    auth_url = '' + '/v3'
    project_name = ''
    password = ''
    user_domain_name = ''
    project_id = ''
    user_id = ''
    region_name = ''

    # Get a Swift client connection object
    conn = swiftclient.Connection(
            key=password,
            authurl=auth_url,
            auth_version='3',
            os_options={"project_id": project_id,
                        "user_id": user_id,
                        "region_name": region_name})


##    plainDir = r'C:\Users\Vivek\Desktop\cloud\plain'
##    if not os.path.exists(plainDir):
##        os.makedirs(plainDir)
##
##    enDenDir = r'C:\Users\Vivek\Desktop\cloud\encrypted'
##    if not os.path.exists(enDenDir):
##        os.makedirs(enDenDir)

    #enKey = input('Give your passphrase: ')
    #print('Your key is : ', enKey)

    container_name1='plain'
    container_name2='encrypted'

    # File name for testing
    file_name = 'quiz1.txt'

    # Create a new container
    conn.put_container(container_name1)
    print "\nContainer %s created successfully." % container_name1
    conn.put_container(container_name2)
    print "\nContainer %s created successfully." % container_name2

    # List your containers
    print ("\nContainer List:")
    for container in conn.get_account()[1]:
        print container['name']

    selection = raw_input('Do you want to encrypt the file (Y/N): ')
    #print selection

    if selection is 'N':
        with open(file_name, 'w') as quiz1:
            conn.put_object(container_name1,
            file_name,
            contents= "This is sample file for Task 1.",
            content_type='text/plain')

    if selection is 'Y':
        enfile = 'EnFileQuiz1.pgp'
        gpg_home = 'C:\Program Files (x86)\GnuPG'
        gpg = gnupg.GPG(gnupghome=gpg_home)
        #gpgobj = gnupg.GPG(gnupghome='/home/testgpguser/gpghome')
        data = gpg.gen_key_input(key_type="RSA",key_length=1024,passphrase="qwerty")
        key_gen = gpg.gen_key(data)
        #print key_gen
        with open(enfile, 'w') as f:
            encrypting=gpg.encrypt_file(f)
            conn.put_object(container_name2,enfile,contents=str(encrypting),content_type='text/plain')

    print ("\nObject List:")
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            print 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])


    obj = conn.get_object(container_name1, file_name)
    with open(file_name, 'w') as my_example:
           my_example.write(obj[1])
           print "\nObject %s downloaded successfully." % file_name

##    obj = conn.get_object(container_name2, enfile)
##    with open(enfile, 'w') as dec:
##        dec.write(obj[1])
##        decrypted_data=gpg.decrypt(enfile, passphrase="qwerty")
##        print '\nDecrypted File Downloaded.'

    # Delete an object
    conn.delete_object(container_name1, file_name)
    print "\nObject %s deleted successfully." % file_name

    # To delete a container. Note: The container must be empty!
    conn.delete_container(container_name1)
    print "\nContainer %s deleted successfully.\n" % container_name

httpd = Server(("", PORT), Handler)
try:
  print("Start serving at port %i" % PORT)
  mainFunc()
  httpd.serve_forever()
except:
  print ''
httpd.server_close()
