from flask import Flask,redirect,render_template
import ibm_boto3
from ibm_botocore.client import Config,ClientError

COS_ENDPOINT="https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID= "1Aoh0NCnLUOCuGnCtjC5y6Mt4Jh0kGyC-UTNgLeW8ESp"
COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/a9549e0a997040b3add4c41636b49810:de1cf225-d159-4ef3-ba74-0a4f03f45d50::"

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
        print(files)
        files_names=[]
        for file in files:
            files_names.append(file.key)
            print(file.key)
        return files_names
    except ClientError as ce:
        print("client error:{0}".format(ce))
    except Exception as e:
        print("unable to retrieve bucket content: {0}".format(e))

@app.route("/")
def index():
    files=get_bucket_content("cloud-object-storage-jm-cos-standard-jrt")
    return render_template("index.html",file=files)


if __name__=='__main__':
    app.run(debug=True,port=7000)