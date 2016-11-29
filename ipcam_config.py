import ConfigParser

def save_config(resolution, annotate):
    config = ConfigParser.RawConfigParser()
    config.add_section('Camera')
    config.set('Camera', 'resolution', resolution)
    config.set('Camera', 'annotate', annotate)
    with open('ipcam.cfg', 'wb') as configfile:
        config.write(configfile)


def load_config():
    cfg_dict = {}

    config = ConfigParser.ConfigParser()
    config.read('ipcam.cfg')
    cfg_dict['resolution'] = config.get('Camera', 'resolution', '640x480')
    cfg_dict['annotate'] = config.get('Camera', 'annotate', '')

    return cfg_dict
