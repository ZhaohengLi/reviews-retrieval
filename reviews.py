import pymysql


def get_review_text(shop_id, reviews_num=0, db_host='localhost', db_user='root', db_password='password', db_schema='JDReviews'):
    """
    Open MySQL database and fetch data.
    :param shop_id: (int) This's also the table's name.
    :param reviews_num: (int,optional) The number of needed reviews, fetch all by default.
    :param db_host: (str,optional)
    :param db_user: (str,optional)
    :param db_password: (str,optional)
    :param db_schema: (str,optional)
    :return: (list) A list of review text like "['It is a good day.','The weather is great!','I love it!']".
    """
    review_text_list = []
    database = pymysql.connect(db_host, db_user, db_password, db_schema)
    cursor = database.cursor()
    if reviews_num > 0:
        command = 'SELECT `review_text` FROM `{}` WHERE `primary_id` < {}'.format(shop_id, reviews_num)
    else:
        command = 'SELECT `review_text` FROM `{}`'.format(shop_id)
    try:
        cursor.execute(command)
        rows = cursor.fetchall()
        for row in rows:
            review_text_list.append(row[0])
    except:
        print("Failed to fetch data from database!")
    database.close()
    return review_text_list


