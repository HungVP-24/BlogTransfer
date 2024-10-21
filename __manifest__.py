{
    'name': ' Blog_transfer ',  # Tên module
    'version': '1.1',  # Phiên bản mới
    'category': 'Website',  # Danh mục module
    'summary': 'Chuyển giao blog từ một cơ sở dữ liệu đến nhiều cơ sở dữ liệu.',  # Tóm tắt về chức năng của module
    'description': 'Module cho phép nhập thông tin API và chuyển giao blog thông qua giao diện người dùng.',  # Mô tả chi tiết
    'depends': ['base', 'web', 'website_blog'],  # Các module mà module này phụ thuộc vào
    'data': [
        'views/Blog.xml',
        'views/server_view.xml',
        'views/menu.xml'
    ],
    'installable': True,  # Cho phép cài đặt module
}
