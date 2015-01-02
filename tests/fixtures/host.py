result_of_execute_srvr_ok = 'ZOOKEEPER: 123\nzxID:33\nmode:follower\nSome data: 55:AA\n   trailing:space'
result_of_execute_srvr_err = 'OKEEPER: 123\nmode:leAder\nSome data: 55:AA\n   trailing:space'


parse_info_data = {
    'ok': [
        {
            'in': result_of_execute_srvr_ok.split('\n'),
            'out': {'zookeeper': '123', 'zxid': '33', 'some': '55:AA', 'trailing': 'space'},
            'health': 'HOST_HEALTHY',
            'mode': 'FOLLOWER'
        },
        {
            'in': result_of_execute_srvr_ok.upper().split('\n'),
            'out': {'zookeeper': '123', 'zxid': '33', 'some': '55:AA', 'trailing': 'SPACE'},
            'health': 'HOST_HEALTHY',
            'mode': 'FOLLOWER'
        },
        {
            'in': result_of_execute_srvr_ok.lower().split('\n'),
            'out': {'zookeeper': '123', 'zxid': '33',  'some': '55:aa', 'trailing': 'space'},
            'health': 'HOST_HEALTHY',
            'mode': 'FOLLOWER'
        },
    ],
    'raise_on_parse': [
        {
            'in': 'Zookeeper: 123\nSome data: 55:AA\n   trailing:space'.split('\n'),
            'out': {'zookeeper': '123', 'some': '55:AA', 'trailing': 'space'},
            'health': 'HOST_ERROR',
            'mode': 'UNKNOWN',
        },
    ],
    'raise_on_validate': [
        {
            'in': result_of_execute_srvr_err.split('\n'),
            'out': {'okeeper': '123', 'some': '55:AA', 'trailing': 'space'},
            'health': 'HOST_ERROR',
            'mode': 'UNKNOWN',
        },
        {
            'in': 'Zookeeper: 123\nempty_value:\nmode: creepy_one\n   trailing:space'.split('\n'),
            'out': {'zookeeper': '123', 'trailing': 'space'},
            'health': 'HOST_ERROR',
            'mode': 'UNKNOWN',
        },
        {
            'in': 'Zookeeper: 123\n:empty_key\nmode: creepy_one\n   trailing:space'.split('\n'),
            'out': {'zookeeper': '123', 'trailing': 'space'},
            'health': 'HOST_ERROR',
            'mode': 'UNKNOWN',
        },
    ]
}


parse_stat_data = {
    'ok': {
        'in': 'Zookeeper version: 3.4.6-1569965, built on 02/20/2014 09:09 GMT\n'
              'Clients:\n/1.1.5.38:60841[1](queued=0,recved=45,sent=45)\n'
              '/1.1.5.14:57782[1](queued=0,recved=905,sent=905)\n'
              '/1.1.5.23:36027[1](queued=0,recved=1093,sent=1093)\n'
              '/1.1.5.137:39362[1](queued=0,recved=101,sent=101)'.split('\n'),
        'parsed': {
            'head': 'Zookeeper version: 3.4.6-1569965, built on 02/20/2014 09:09 GMT',
            'clients': [
                {'recved': '45', 'port': '60841', 'host': '1.1.5.38', 'n': '1', 'queued': '0', 'sent': '45'},
                {'recved': '905', 'port': '57782', 'host': '1.1.5.14', 'n': '1', 'queued': '0', 'sent': '905'},
                {'recved': '1093', 'port': '36027', 'host': '1.1.5.23', 'n': '1', 'queued': '0', 'sent': '1093'},
                {'recved': '101', 'port': '39362', 'host': '1.1.5.137', 'n': '1', 'queued': '0', 'sent': '101'}]
        },
        'not_parsed': ['Clients:']
    },
    'no_clients': {
        'in': 'ZooWithout proper head\n'
              'Clients:\n/1.1.5.38:60841[1](queued=0,recved=45)\n'
              '/aa.1.5.14:57782[1](queued=0,recved=905,sent=905)\n'
              '/1.1.5.23:36027[1](queued=dddd,recved=1093,sent=1093)\n'
              '/1.1.5.137[1](queued=0,recved=101,sent=101)'.split('\n'),
        'parsed': {
            'head': '',
            'clients': []
        },
        'not_parsed': [
            'ZooWithout proper head',
            'Clients:',
            '/1.1.5.38:60841[1](queued=0,recved=45)',
            '/aa.1.5.14:57782[1](queued=0,recved=905,sent=905)',
            '/1.1.5.23:36027[1](queued=dddd,recved=1093,sent=1093)',
            '/1.1.5.137[1](queued=0,recved=101,sent=101)'
        ]
    },
}
