from dependency.elastic import make_index, add_data, retrieve, delete_index
if __name__ == '__main__':
    print(make_index('my_index2'))
    print(add_data('my_index2', [
        {
            "filename": '윤하 - 라이브리뷰',
            "page": 1,
            "content" : '다만 한 순간이라도 당신을 위해 살아. 누구도 그 이유이지 않은 오로지 그대로만.'
        },
        {
            "filename": '윤하 - 라이브리뷰',
            "page": 2,
            "content" : '슬픔 고난이 차오른 그림자. 한 번이라도 함께하게 해줘.'
        },
        {
            "filename": '윤하 - 라이브리뷰',
            "page": 3,
            "content" : '기쁨 환희에 차오른 눈동자. 등대가 되어 반짝일 때 그대를 바라보고 싶어.'
        },
        ]))
    print(retrieve('my_index2', '그게 누구 때문이 아니라 자신을 위해 살아요.', 0, 1).json())
    print(delete_index('my_index2'))