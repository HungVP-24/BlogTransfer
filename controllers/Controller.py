from odoo import http
from odoo.http import request

class BlogAPIController(http.Controller):
    # @http.route('/api/blog/transfer', type='json', auth='public', methods=['POST'])
    # def transfer_blog(self, **kwargs):
    #     content = kwargs.get('content')
    #     if not content:
    #         return {'status': 'error', 'message': 'No content provided'}

    #     # Thực hiện xử lý dữ liệu ở đây
    #     # Ví dụ: Tạo một blog mới trong cơ sở dữ liệu hiện tại
    #     blog_model = request.env['blog.post'].create({'name': content, 'content': content})  # Update model as needed

    #     return {'status': 'success', 'message': 'Blog transferred successfully'}

    @http.route('/api/blog/test_transfer', type='json', auth='public', methods=['GET'])
    def test_transfer_blog(self,  **kwargs):
        # test_content = "Test Blog Post Title"
        # test_content_body = "This is the body of the test blog post."

        # # Simulate a blog transfer
        # response = self.transfer_blog(content=test_content_body)

        #        # Thêm nhiều xác nhận nếu cần
        return {
            'status': 'success',
            'message': 'Test transfer executed',
            # 'response': response
        }
    

    


