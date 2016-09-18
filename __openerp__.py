{
    'name': 'Ceph RADOS attachment storage',
    'version': '8.0.0.2',
    'category': '',
    'description': """Attachment storage support for Ceph (RADOS) clusters.

To configure the module after installation, add a new system parameter: 

Key: ir_attachment.location

Value: rados:pool=<yourpoolname>&keyring=<path to keyring file>&name=client.<clientname>

    """,
    'author': 'Teemu Haapoja',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [],
    'test': [],
    'demo_xml': [],
    'js': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
