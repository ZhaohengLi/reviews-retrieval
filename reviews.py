import pymysql
import sys


def get_review(item_id, category='', db_host='localhost', db_user='root', db_password='password', db_schema='FinalTestReviews'):
    """
    Open MySQL database and fetch data.
    :param item_id: (int) This's also the table's name.
    :param reviews_num: (int,optional) The number of needed reviews, fetch all by default.
    :param db_host: (str,optional)
    :param db_user: (str,optional)
    :param db_password: (str,optional)
    :param db_schema: (str,optional)
    :return: (list) A list of review text like "['It is a good day.','The weather is great!','I love it!']".
    """
    review_list = []
    database = pymysql.connect(db_host, db_user, db_password, db_schema)
    cursor = database.cursor()
    if not category == '':
        command = "SELECT * FROM `{}` WHERE `category` = '{}'".format(item_id, category)
    else:
        command = 'SELECT * FROM `{}`'.format(item_id)
    try:
        cursor.execute(command)
        rows = cursor.fetchall()
        for row in rows:
            single_review = []
            single_review.append(int(row[3][4]))  # star
            single_review.append(str(row[4])+str(row[9]))  # text
            single_review.append(str(row[10]))  # category
            review_list.append(single_review)
    except:
        print("Failed to fetch data from database!")
        print(sys.exc_info())
    database.close()
    return review_list


