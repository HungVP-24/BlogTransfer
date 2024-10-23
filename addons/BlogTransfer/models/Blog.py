from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Blog(models.Model):
    _name = 'blog'
    _description = 'Blog'

    blog_post_id = fields.Many2one('blog.post', string="Blog Post", required=True) 
    server_id = fields.Many2many('server', string="Server") 
    tags = fields.Char(string="Tag Mapping")  
    server_tag = fields.Many2many('mapping_tag', string="Server Tag")  
    local_tag = fields.Many2many('blog.tag', string="Local Tag")  # Trường này sẽ lưu các tag đã chọn

    # Trường để hiển thị tên local tag và server tag
    local_tag_names = fields.Char(string="Local Tag Names", compute="_compute_local_tag_names", store=True)
    server_tag_names = fields.Char(string="Server Tag Names", compute="_compute_server_tag_names", store=True)
    server_names = fields.Char(string="Server Names", compute="_compute_server_names", store=True)  # Đổi tên trường thành "Server Names"

    @api.onchange('blog_post_id')
    def _onchange_blog_post_id(self):
        if self.blog_post_id:
            # Lấy các local tag tương ứng với blog_post_id
            
            local_tags = self.env['blog.tag'].search([('post_ids', 'in', self.blog_post_id.id)])
            self.local_tag = [(6, 0, local_tags.ids)]  # Cập nhật local_tag với các tag mới

    @api.onchange('server_id')
    def _onchange_server_id(self):
        if self.blog_post_id and self.server_id:
            local_tags = self.env['blog.tag'].search([('post_ids', 'in', self.blog_post_id.id)])
            server_tags = self.env['tag_server'].search([
                ('local_tag', 'in', local_tags.ids),
                ('server_id', 'in', self.server_id.ids)
            ])
            self.server_tag = [(6, 0, server_tags.mapped('server_tag.id'))]  # Gán server tag

    @api.depends('local_tag')
    def _compute_local_tag_names(self):
        for record in self:
            record.local_tag_names = ', '.join(record.local_tag.mapped('name'))

    @api.depends('server_tag')
    def _compute_server_tag_names(self):
        for record in self:
            record.server_tag_names = ', '.join(record.server_tag.mapped('name'))

    @api.depends('server_id')
    def _compute_server_names(self):
        for record in self:
            # Sử dụng hàm mapped để lấy tên từ server_id và nối các tên server bằng dấu phẩy
            record.server_names = ', '.join(record.server_id.mapped('name'))
