import socket

_config = {
    'mysql' : {
        'user': 'sergej',
        'password': 'password',
        'host': '127.0.0.1',
        'database': 'sergej_lego-priisvrgliich_test',
        'raise_on_warnings': True
    },
    'scanner' : {
        'limit' : 100,
        'wishlist' : {
            'set_number' : ['40407', '75275', '70418', '70419', '70420', '70421', '70422', '70423', '70424', '70425', '70427', '70428', '70429', '70430', '70431', '70432', '10270', '10272', '75098', '21311', '21320', '21319', '21318', '21317', '21316', '21322', '21321', '75179', '75954', '75810', '21321', '75266', '75270', '75271', '75292', '75317', '80104', '80105', '10264', '10267', '21316', '40333', '40362', '70840', '70841', '75225',' 75226', '75228', '75229', '75244', '75252', '75948', '10261', '10263', '75181', '70620', '10228', '75192', '79115', '79116', '79117', '79118', '79119', '79120', '79121', '79122', '79100', '79101', '79102', '79103', '79104', '79105', '75054', '75189', '70751'],
            'theme' : ['Ideas', 'Hidden Side', 'Creator Expert', 'Jurassic World', 'Jurassic Park'],
            'subtheme' : ['Episode IV', 'Episode V', 'Episode VI', 'Ultimate Collector Series', 'The Mandalorian', 'The Clone Wars']
        },
        'blacklist' : ['1974', '1967', '9800', '1985', '2008', '1018', '1983', '2017', '1981', '2018'],
        'title_blacklist' : ['Anleitung', 'Anleitungen', 'Bauplan', 'emploi', 'Verkleidung', 'Sticker', 'Bauanleitung']
    }
}

if 'uberspace.de' in socket.gethostname():
    _config['mysql']['database'] = 'sergej_lego-priisvrgliich'
    _config['scanner']['limit'] = 9999
