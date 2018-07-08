import time
from asterisk.ami import AMIClient, EventListener, SimpleAction, AutoReconnect


def event_notification(source, event):
    print('notify-send "%s" "%s"' % (event.name, str(event)))


def main():
    conf_connection = dict(address='42.116.18.41', port=5038)
    conf_account = dict(username='callservice', secret='505e3ea75c1e21f4f288a83Dz2V9K')

    ami = AMIClient(**conf_connection)
    future = ami.login(**conf_account)
    if future.response.is_error():
        raise Exception(str(future.response))
    AutoReconnect(ami)
    ami.add_event_listener(EventListener(on_event=event_notification, white_list='Cdr'))
    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        ami.logoff()


if __name__ == '__main__':
    main()
