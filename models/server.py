from odoo import models, fields, api, _  # Nhập các mô-đun cần thiết từ Odoo
from odoo.exceptions import UserError  # Nhập ngoại lệ UserError để xử lý lỗi
import requests  # Nhập thư viện requests để thực hiện các yêu cầu HTTP
import logging  # Nhập thư viện logging để ghi lại thông tin và lỗi

_logger = logging.getLogger(__name__)  # Tạo logger để ghi lại thông tin

# Định nghĩa model database_list
class database_list(models.Model):
    _name = 'database_list'  # Định nghĩa tên model là 'database_list'
    name = fields.Char(string="Tên Database")  # Trường lưu tên database
    domain = fields.Char(string="Domain")  # Trường lưu URL API

# Định nghĩa class cho Server
class Server(models.Model):
    _name = 'server'  # Định nghĩa tên model là 'server'
    _description = 'server'  # Mô tả ngắn về model
   

 
    db_domain = fields.Char(string="Domain", required=True) 
    database_list = fields.Many2one("database_list", string="Danh sách Database")  # Liên kết đến một bản ghi trong bảng database_list
    name_database = fields.Char(string="Tên Database", required=False, compute="compute_database_list")
    name = fields.Char(string="Tên gợi nhớ")  
    image = fields.Binary() 
    password = fields.Char(string="Mật Khẩu", required=False)  
    user = fields.Char(string="Tên người dùng", required=False)  
    mapping_tag = fields.One2many("tag_server", "server_id", string="Mapping Tag")      
    server_tag = fields.One2many("mapping_tag","server_id", string="Server Tags")   
    is_connected = fields.Boolean()  

    
    session_id = fields.Char(string="Session ID")

    # Hiển thị tên name_database
    @api.depends("database_list")  # Tính toán lại khi danh sách database thay đổi
    def compute_database_list(self):
        for record in self:
            if record.database_list:  # Nếu database_list có giá trị
                record.name_database = record.database_list.name  # Gán tên database từ database_list
            else:
                record.name_database = False  # Đặt lại thành False nếu không có database_list
            
    # Phương thức để tải danh sách database từ server
    def action_load_databases(self):       
        if not self.db_domain:  # Kiểm tra nếu không có domain
            raise UserError(_("Vui lòng cung cấp Domain hợp lệ."))  # Hiện thông báo lỗi
        url = f"{self.db_domain}/web/database/list"  # Xây dựng Doamain để lấy danh sách database
        try:
            response = requests.post(url, json={ "jsonrpc": "2.0", "method": "call","params": {}})# Gửi yêu cầu POST tới server
            if response.status_code == 200:  # Kiểm tra nếu phản hồi thành công
                result = response.json().get('result', [])  # Lấy kết quả từ phản hồi
            
                if result:  # Nếu có kết quả
                    for r in result:  # Lặp qua từng database trong kết quả
                        db = self.env["database_list"].search([("name", "=", r), ("domain", "=", self.db_domain)])  # Tìm database trong database_list 
                        if not db:
                            self.env["database_list"].create({"name": r, "domain": self.db_domain})  # Tạo mới nếu chưa tồn tại
                            
                    # Lưu danh sách database
                    _logger.info(f"Cơ sở dữ liệu được tải thành công: {self.database_list}")  # Ghi lại thông tin
                else:
                    raise UserError(_("Không tìm thấy cơ sở dữ liệu hoặc phản hồi không hợp lệ."))  # Hiện thông báo lỗi nếu không có kết quả
            else:
                raise UserError(_("Không thể tải cơ sở dữ liệu. Vui lòng kiểm tra URL máy chủ."))  # Hiện thông báo lỗi nếu phản hồi không thành công
        except Exception as e:  # Bắt ngoại lệ
            raise UserError(_("Đã xảy ra lỗi khi tải cơ sở dữ liệu: %s" % str(e)))  # Hiện thông báo lỗi

    # Kiểm tra đăng nhập
    def action_test_login(self): 
        session_data = self.action_login()  # Gọi phương thức đăng nhập
        auth_response_data = session_data.json()  # Lấy dữ liệu phản hồi từ đăng nhập
        if auth_response_data.get("result") and auth_response_data["result"]["uid"]:  # Nếu xác thực thành công
            self.is_connected = True  # Đánh dấu là đã kết nối
            self.action_load_tag()  # Gọi danh sách tag từ test login
        else:
            self.is_connected = False  # Đánh dấu là chưa kết nối
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Xác thực không thành công !'),
                    'message': _('Thông tin xác thực không hợp lệ. Vui lòng kiểm tra tên người dùng và mật khẩu của bạn.'),
                    'sticky': False,
                    'type': 'danger',
                },
            }

    # Phương thức để thực hiện đăng nhập 
    def action_login(self):
        url = f"{self.db_domain}/web/session/authenticate"  # Xây dựng URL để đăng nhập
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.name_database,  # Tên database
                "login": self.user,  # Tên người dùng
                "password": self.password  # Mật khẩu
            },
            "id": 1
        }
        # Gửi yêu cầu đăng nhập
        session_data = requests.post(url, json=data)  # Gửi yêu cầu POST
        session_data.json()  # Lấy dữ liệu phản hồi

        return session_data  # Trả về dữ liệu phiên làm việc


    # Load tag
    def action_load_tag(self):
        """ Phương thức để tải và mapping các tag """
        tags_local = self.env["blog.tag"].search([])  # Lấy tất cả các tag trong bảng 'blog.tag'
        _logger.info(self.id)  # Ghi lại ID của server hiện tại

        # Xóa các tag đã có liên kết với server hiện tại để tránh lặp lại
        tag_search = self.env['tag_server'].search([("server_id", "=", self.id)])  # Tìm các tag đã liên kết với server
        tag_search.unlink()  # Xóa các tag này

        # Thiết lập URL để đăng nhập vào server
        session_data = self.action_login()  # Gọi phương thức đăng nhập
        auth_response_data = session_data.json()  # Lấy dữ liệu phản hồi từ đăng nhập
        if auth_response_data.get("result") and auth_response_data["result"]["uid"]:  # Nếu xác thực thành công
            uid = auth_response_data["result"]["uid"]  # Lấy UID
            session_id = session_data.cookies['session_id']  # Lấy session ID
            print(f"Đã xác thực! UID: {uid}, Session ID: {session_id}")  # In ra thông tin xác thực
        else:
            print("Xác thực không thành công")  # Nếu xác thực không thành công
            

        # Gửi yêu cầu để lấy tag từ server khác
        headers = {  # Thiết lập headers cho yêu cầu
            'Content-Type': 'application/json',
            'Cookie': f'session_id={session_id}'  # Thêm session ID vào cookie
        }
        data = {  # Dữ liệu gửi đi
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "blog.tag",  # Mô hình cần lấy
                "method": "search_read",  # Phương thức để tìm và đọc
                "args": [[]],  # Tham số
                "kwargs": {
                    "fields": ["name"],  # Các trường cần lấy
                }
            },
            "id": 2
        }

        # Gửi yêu cầu lấy tag từ server
        response = requests.post(f"{self.db_domain}/web/dataset/call_kw", headers=headers, json=data)  # Gửi yêu cầu POST
        tag = response.json()  # Lấy dữ liệu phản hồi
        _logger.info(tag)

        # Tạo tag từ server nếu chúng chưa tồn tại
        for tag_server in tag.get('result', []):  # Lặp qua từng tag trong kết quả từ server
            # Kiểm tra nếu tag đã tồn tại cho server này
            server_tag = self.env['mapping_tag'].search([
                ("name", "=", tag_server.get("name")),  # Tìm tag với tên tương ứng
                ("server_id", "=", self.id)  # Phải thuộc về server hiện tại
            ], limit=1)  # Chỉ lấy một kết quả

            # Chỉ tạo mới tag nếu chưa tồn tại
            if not server_tag:  # Nếu tag chưa tồn tại
                server_tag = self.env['mapping_tag'].create({  # Tạo mới tag trong bảng 'mapping_tag'
                    "id_tag": tag_server.get("id"),  # Gán ID tag từ server
                    "name": tag_server.get("name"),  # Gán tên tag từ server
                    "server_id": self.id  # Gán ID của server hiện tại
                })

        # Tạo liên kết giữa server và tag, chỉ load client tag
        for local_tag in tags_local:  # Lặp qua danh sách client tag và hiển thị chúng
            self.env['tag_server'].create({  # Tạo bản ghi mới trong bảng 'tag_server'
                'server_id': self.id,  # Gán ID của server
                'server_tag': [(6, 0, [])],  # Không load server tag, để trống cho đến khi được chọn (thêm server_tag_id)
                'local_tag': local_tag.id  # Hiển thị danh sách client tag
            }) 
                
        _logger.info("Client tag đã được load, server tag sẽ không hiển thị cho đến khi bấm chọn") 

