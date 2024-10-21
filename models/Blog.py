from odoo import models, fields, api
import logging
from odoo.exceptions import UserError
import requests

_logger = logging.getLogger(__name__)

class Blog(models.Model):
    _name = 'blog'
    _description = 'Blog'

    blog_post_id = fields.Many2one('blog.post', string="Blog Post", required=True) 
    server_id = fields.Many2many('server', string="Server") 
    tags = fields.Char(string="Tag Mapping")  
    server_tag = fields.Many2many('mapping_tag', string="Server Tag")  
    local_tag = fields.Many2many('blog.tag', string="Local Tag")  

    @api.onchange('blog_post_id')
    def _onchange_blog_post_id(self):
        if self.blog_post_id:  
            local_tags = self.env['blog.tag'].search([('post_ids', 'in', self.blog_post_id.id)])
            self.local_tag = [(6, 0, local_tags.ids)]  
            self.server_tag = [(5,)]

    @api.onchange('server_id')
    def _onchange_server_id(self):
        if self.blog_post_id and self.server_id:  
            local_tags = self.env['blog.tag'].search([('post_ids', 'in', self.blog_post_id.id)])
            server_tags = self.env['tag_server'].search([
                ('local_tag', 'in', local_tags.ids),
                ('server_id', 'in', self.server_id.ids)
            ])
            self.local_tag = [(6, 0, local_tags.ids)]
            self.server_tag = [(6, 0, server_tags.mapped('server_tag.id'))]  

