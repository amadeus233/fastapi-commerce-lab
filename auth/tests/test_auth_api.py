# 这个文件预留给 auth 模块的接口测试。
#
# pytest 会自动发现 test_*.py 文件中的测试函数。
# 例如以后可以写：
#
# def test_auth_ok(client):
#     response = client.get("/api/v1/auth/ok")
#     assert response.status_code == 200
#
# 当前模板还没有提供测试 client fixture，所以这里暂时只保留学习说明。
