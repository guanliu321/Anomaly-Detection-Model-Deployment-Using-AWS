# Supervised-Anomaly-Detection-Real-Time-Notification-Using-AWS-
Utilized a sample solution deployed by using the AWS CloudFormation template provided by the AWS,We have developed an end-to-end workflow in a dataset with more than 280,000 records for detecting abnormal behaviors of customers' credit cards.Here is the detail of the workflow:

#Using Amazon Sagemaker's algorithm, we built a Logistic model, then used incremental learning to refine and expand the model, and deploy the model to AWS endpoints.

#When the streaming data comes in,SNS client will be invoted and a notification of whether exist abnormal behaviors or not will be sent to the designed endpoint. 

#At the end of each day, a summary dashboard which record the pattern of daily abnormal activities will be automatically generated and sent to key stakeholders.

#Utilized:Python,AWS,Pandas,Numpy,Json,Boto3,Base64,Amazon Sagemaker,ETL,Anomaly Detection,Logistic Model,SQL.
