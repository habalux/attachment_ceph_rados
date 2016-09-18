# -*- coding: utf-8 -*-

import base64
import logging
from openerp.osv import osv

logger = logging.getLogger(__name__)

import rados

# /opt/odoo/server/openerp/addons/base/ir/ir_attachment.py

class RadosStore(osv.Model):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    __STORE_PREFIX = "rados:"
    __WRITE_CHUNK_SIZE = 1024*1024*10 # write large files 10Mb at a time

    def __connect_ceph(self, name, keyring, pool, conffile='/etc/ceph/ceph.conf'):
        conf = {
                'keyring':keyring
        }
        cluster = rados.Rados(conffile=conffile, name=name, conf=conf)
        cluster.connect()
        ctx = cluster.open_ioctx(pool)
        return cluster, ctx

    def __parse_location(self, location):
        conf = {
            'conffile':'/etc/ceph/ceph.conf',
        }

        location = location.replace(self.__STORE_PREFIX,'')
        # Parse conf string
        loc_dict = dict( [v.split('=') for v in location.split('&')] )
        if 'name' not in loc_dict.keys():
            raise ValueError("missing parameter: name")
        if 'keyring' not in loc_dict.keys():
            raise ValueError("missing parameter: keyring")
        if 'pool' not in loc_dict.keys():
            raise ValueError("missing parameter: pool")

        conf.update(loc_dict)
        return conf

    def _file_write(self, cr, uid, value):
        location = self._storage(cr, uid)
        if not location.startswith(self.__STORE_PREFIX):
            return super(RadosStore, self)._file_write(cr, uid, value)
        
        # Does the file data always come in as base64? Why?
        value = value.decode('base64')
        location_params = self.__parse_location(location)

        data_len = len(value)
        logger.info("DATA LENGTH: %d"%(data_len))

        filename, full_path = self._get_path(cr, uid, value)

        cluster,ctx = self.__connect_ceph(**location_params)
        try:
            data_pos = 0
            write_done = False
            while not write_done:
                write_start = data_pos
                write_end = data_pos + self.__WRITE_CHUNK_SIZE
                if write_end >= data_len:
                    write_end = data_len
                    write_done = True

                logger.info("RADOS write: %d to %d (total %d)"%(data_pos, write_end, data_len))
                chunk = value[data_pos:write_end]
                ctx.write(filename, chunk, data_pos)
                data_pos = write_end
                del chunk

            return filename
        except Exception,e:
            logger.info("RADOS error during write: %s"%(str(e)) )
            raise
        finally:
            ctx.close()
            cluster.shutdown()
            logger.info("RADOS wrote %s bytes to file %s"%(data_len, filename) )
        

    def _file_delete(self, cr, uid, fname):
        location = self._storage(cr, uid)
        if not location.startswith(self.__STORE_PREFIX):
            return super(RadosStore, self)._file_delete(cr, uid, fname)

        location_params = self.__parse_location(location)
        cluster,ctx = self.__connect_ceph(**location_params)

        try:
            ctx.remove_object(fname)
            logger.info("RADOS (delete): object '%s'"%(fname) )
        except rados.ObjectNotFound:
            logger.info("RADOS error (delete): object '%s' not found"%(fname) )
            return None
        except Exception,e:
            logger.info("RADOS error during delete: %s"%(str(e)) )
            raise
        finally:
            ctx.close()
            cluster.shutdown()

    def _file_read(self, cr, uid, fname, bin_size=False):
        location = self._storage(cr, uid)
        if not location.startswith(self.__STORE_PREFIX):
            return super(RadosStore, self)._file_read(cr, uid, fname, bin_size=bin_size)

        location_params = self.__parse_location(location)
        cluster,ctx = self.__connect_ceph(**location_params)
        
        try:
            stat = ctx.stat(fname)
            if bin_size:
                return stat[0]
            else:
                #while not read_done:
                data = ctx.read(fname, length=stat[0])
                logger.info("RADOS READ %d bytes of object '%s'"%(stat[0],fname))
        except rados.ObjectNotFound:
            logger.info("RADOS (read): object '%s' not found"%(fname) )
            return None
        except Exception,e:
            logger.info("RADOS error during read: %s"%(str(e)) )
            raise
        finally:
            ctx.close()
            cluster.shutdown()
        ret = data.encode('base64')
        del data
        return ret
