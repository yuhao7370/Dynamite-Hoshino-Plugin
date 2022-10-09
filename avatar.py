import requests
from requests_toolbelt import MultipartEncoder
import PIL, json
from PIL import Image
from io import BytesIO

def downloadimg(url):
    r = requests.get(url, stream=True)
    img = Image.open(BytesIO(r.content))
    img = img.resize((256,256))
    return img

def Send_To_Server(bytesio, uid):
    url = "http://124.223.85.207:5244/api/public/upload"
    m = MultipartEncoder(
        fields={
            'files': (uid, bytesio, 'image/jpeg'),
            'path': "/download/avatar/256x256_jpg"
        }
    )
    print(m.content_type)
    headers = {'Content-Type': m.content_type,
               'authorization': "ed62d3fa9e04392f306d680ab1d0912c"}
    response = requests.post(url, headers=headers, data=m, timeout=10)
    return json.loads(response.text)

def upload_avatar(qqid, uid):
    url = f"https://q.qlogo.cn/headimg_dl?dst_uin={qqid}&spec=640&img_type=jpg"
    img = downloadimg(url)
    bytesio = BytesIO()
    img.save(bytesio, 'JPEG')
    response = Send_To_Server(bytesio, uid)
    if(response["code"] == 200):
        return True
    return False

# if __name__ == '__main__':
#     qqid = 2737723325
#     url = f"https://q.qlogo.cn/headimg_dl?dst_uin={qqid}&spec=640&img_type=jpg"
#     # filename = "dbef7e85-0d5b-416a-82d0-fbffb420588e.jpg"
#     img = downloadimg(url)
#     bytesio = BytesIO()
#     img.save(bytesio, 'JPEG')
#     response = Send_To_Server(bytesio, "dbef7e85-0d5b-416a-82d0-fbffb420588e")
#     if(response["code"] == 200):
#         print("上传成功")


# https://q.qlogo.cn/headimg_dl?dst_uin=2737723325&spec=640&img_type=jpg
