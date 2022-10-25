from flask import Flask,redirect,render_template
import ibm_boto3
from ibm_botocore.client import Config,ClientError

COS_ENDPOINT="https://s3.eu-gb.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID= "YErxSSK7V2al0Bz-Ehf6dUC8b_FefnV6RszRT1kXuwr1"
COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/bea0b29e7c0b4eba90c8ee4ffd7d383a:2f4410a0-5ef4-4881-b2f6-7114492e0193::"


cos=ibm_boto3.resource("s3",
ibm_api_key_id=COS_API_KEY_ID,
ibm_service_instance_id=COS_INSTANCE_CRN,
config=Config(signature_version="oauth"),
endpoint_url=COS_ENDPOINT

)
print(cos)
app=Flask(__name__)
def get_bucket_content(bucket_name):
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names=[]
        for file in files:
            files_names.append(file.key)
        return files_names
    except ClientError as ce:
        print("client error:{0}".format(ce))
    except Exception as e:
        print("unable to retrieve bucket content: {0}".format(e))


@app.route("/")
def index():
    files=get_bucket_content("bucket-img")
    return render_template("index.html",file=files)


if __name__=='__main__':
    app.run(debug=True,port=7000)
