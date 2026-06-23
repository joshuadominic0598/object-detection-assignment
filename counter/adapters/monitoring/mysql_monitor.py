from datetime import datetime

import mysql.connector


class MysqlMonitor:

    def __init__(self,host,port,user,password,database):
        self.connection = mysql.connector.connect(host=host,port=port,user=user,password=password,database=database)

    def log_request(self,request_id,endpoint,image_name,threshold,response_time_ms,detected_count,detected_classes,status_code,success,error_message=None):

        cursor = self.connection.cursor()
        cursor.execute("""INSERT INTO api_request_log (
                        request_id,
                        request_timestamp,
                        image_name,
                        endpoint,
                        threshold,
                        detected_classes,
                        response_time_ms,
                        detected_count,
                        status_code,
                        success,
                        error_message)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (   request_id,
                        datetime.utcnow(),
                        image_name,
                        endpoint,
                        threshold,
                        detected_classes,
                        response_time_ms,
                        detected_count,
                        status_code,
                        success,
                        error_message
                    )
                )

        self.connection.commit()

    def log_prediction(self,request_id,endpoint,image_name,object_class,confidence):

        cursor = self.connection.cursor()
        cursor.execute("""INSERT INTO prediction_log (
                            request_id,
                            request_timestamp,
                            image_name,
                            endpoint,
                            object_class,
                            confidence)
                        VALUES (%s,%s,%s,%s,%s,%s)""",
                        (   request_id,
                            datetime.utcnow(),
                            image_name,
                            endpoint,
                            object_class,
                            confidence
                        )
                    )

        self.connection.commit()