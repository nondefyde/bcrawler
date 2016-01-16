import json
from twisted.enterprise import adbapi
import MySQLdb.cursors
import logging


class BirdseyePipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', db='birdseye',
                                            user='root', passwd='', cursorclass=MySQLdb.cursors.DictCursor,
                                            charset='utf8', use_unicode=True)

    def process_item(self, item, spider):
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self, tx, item):

        # all this block run on it's own thread
        tx.execute("select * from product_tb where product_url = %s", (item['product_url'],))
        result = tx.fetchone()
        if result:
            query = "UPDATE product_tb SET "
            query += "product_name=%s, description=%s, manufacturer=%s, oem=%s,"
            query += "price=%s, stock_quantity=%s, vendor=%s WHERE product_url=%s "

            tx.execute(query, (item['product_name'], item['description'], item['manufacturer'],
                               item['oem'], item['price'], item['stock_quantity'], item['vendor'], item['product_url']))
            logging.log(logging.INFO, "Item has  been updated in db: %s" % item)
        else:
            tx.execute(
                "insert into product_tb (product_name, description, manufacturer, oem,"
                " price, stock_quantity, product_url, vendor)"
                "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (item['product_name'], item['description'], item['manufacturer'], item['oem'],
                 item['price'], item['stock_quantity'], item['product_url'], item['vendor'])
            )
            logging.log(logging.INFO, "Item stored in db: %s" % item)

    def handle_error(self, e):
        logging.log(logging.ERROR, e)


class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.json', 'wb')

    def process_item(self, item,spider):
        line = json.dumps(dict(item)) + ",\n"
        self.file.write(line)
        return item


class JsonStartUrlWriterPipeline(object):

    def __init__(self):
        self.file = open('the url.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ",\n"
        self.file.write(line)
        return item
