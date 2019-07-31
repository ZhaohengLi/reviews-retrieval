import csv
import pymysql

database = pymysql.connect('localhost', 'root', 'password', 'JDReviews')
cursor = database.cursor()

name_list = ['QUILT']
for name in name_list:
    path = '/Users/lizhaoheng/Dropbox/Work/SRT/ReviewsData/' + name + '.csv'

    command = """CREATE TABLE `JDReviews`.`{}` (
  `primary_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(45) NOT NULL,
  `review_text` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`primary_id`),
  UNIQUE INDEX `primary_id_UNIQUE` (`primary_id` ASC) VISIBLE);""".format(name)
    cursor.execute(command)
    database.commit()

    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            review_text = row[3]
            user_name = row[0]
            if review_text == '评价内容':
                continue
            command = """INSERT INTO `{}`
                    (user_name, review_text) 
                    VALUES 
                    ('{}', '{}')""".format(name, user_name, review_text)
            try:
                cursor.execute(command)
                database.commit()
            except:
                database.rollback()
                print('Error!')
        database.close()
