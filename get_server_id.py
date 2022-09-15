from API import get_server_id

def get_server_id_from_name():
    print('Please enter the name of the server and press enter:')
    server_name = input()
    id = get_server_id(str(server_name))
    print(f'Server ID: {id}')


if __name__ == '__main__':
    get_server_id_from_name()