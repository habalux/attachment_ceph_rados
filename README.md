RADOS attachment support for Odoo 8
===================================

This module allows Odoo to store attachments in a Ceph cluster.

Disclaimer
==========

This module has never seen production usage, as it was intended as a proof-of-concept and also as a practice for me for creating Odoo modules.

Installation
============

System requirements:
- A fully functional Odoo 8 installation
- A fully functional Ceph cluster
- Python rados library

1. Install the module in your Odoo addons path and reload the module list
2. Install the module using Odoo admin interface
3. To configure the module after installation, add a new system parameter: 
   - Key: ```ir_attachment.location```
   - Value: ```rados:pool=<yourpoolname>&keyring=<path to keyring file>&name=client.<clientname>```
4. No migration for existing attachments is provided, you must figure that out on your own. However the old attachments should keep working from their old location.

