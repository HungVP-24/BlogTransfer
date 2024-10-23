from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import base64
import logging

_logger = logging.getLogger(__name__)

class TagMapping(models.Model):
    _name = "mapping_tag"
    _description = 'Mapping Tag'
    
    server_id = fields.Many2one("server", string="Server")
    id_tag = fields.Integer(string="Tag ID")
    name = fields.Char(string="Name")



class TagServer(models.Model):
    _name = 'tag_server'
    _description = 'Tag Server'

    server_id = fields.Many2one("server", string="Server")
    server_tag = fields.Many2many("mapping_tag", string="Server Tag")
    local_tag = fields.Many2one("blog.tag", string="Local Tag")

